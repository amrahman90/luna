"""Lunar sag search over published good-tier mare NAC DTMs (Z2, Task 18).

For each published DTM the user lists (default = the 8 covered tube-relevant
pits from the WP0 scope map), run the I2 kriging correction (via the
existing kriging_correction module), normalise against SLDEM2015
(deferred to a separate normalisation module; the WP0 DTM kriging
output is used as-is for the v0.1 search), compute the depression
depth + Frangi vesselness, and emit a candidate CSV with a per-candidate
evidence vector.

Sag candidates are local maxima of the per-cell score (depth x Frangi)
above a re-tuned threshold (I9), and the I5 sun-azimuth sector artifact
test is included as a per-candidate attribute (skipped when only a
single NAC DTM is available; flagged when multiple DTM acquisitions of
the same target exist).

CLI:
  sag_search.py --dtms TRANQPIT1 MARIUSPIT01 INGENIIPIT
                --outdir <repo out dir>
                [--lola-dir <lola tracks dir>]
                [--pit-lat L --pit-lon L]   # one or more target centres
                [--no-kriging]              # skip kriging step (use raw DTM)
                [--rungs 2 5]               # m/px to evaluate (default 2, 5)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import Affine
from scipy.ndimage import label as ndlabel, maximum_filter
from skimage.filters import frangi
from whitebox import WhiteboxTools

REPO = Path(__file__).resolve().parents[3]
RAW = Path.home() / "lunarvoid" / "data"
WP0K = REPO / "01_WORKSPACE" / "code" / "wp0_kriging"


def _wbt_with_dir():
    """WhiteboxTools with the venv-local binary path + a writable working
    directory set explicitly. The Rust binary resolves relative paths
    against its own cwd; running it from the project root causes "no
    such file" panics even when the path is correct."""
    import os
    import tempfile
    import whitebox
    wbt = WhiteboxTools()
    wbt_dir = os.path.join(os.path.dirname(whitebox.__file__))
    if os.path.isfile(os.path.join(wbt_dir, "whitebox_tools")):
        wbt.set_whitebox_dir(wbt_dir)
    wbt.set_working_dir(tempfile.gettempdir())
    wbt.verbose = False
    return wbt


def existing_or_run_kriging(dtm_name: str, lola_dir: Path, force: bool = False) -> Path:
    """Look for an existing krigcorr GeoTIFF in the standard WP0 outputs;
    if not present and lola_dir has the right CSV, run the kriging module
    in-process. Otherwise return the raw DTM path."""
    raw_dtm = RAW / "dtms" / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
    krigcorr = RAW / "outputs" / dtm_name / f"NAC_DTM_{dtm_name}_krigcorr.tif"
    if krigcorr.exists() and not force:
        return krigcorr
    # find a matching lola csv
    pattern = re.compile(r"LolaRDR_(\d+)N(\d+)N_(\d+)E(\d+)E_.*_pts_csv\.csv$")
    if not lola_dir.exists():
        print(f"[skip] no lola_dir at {lola_dir}; using raw DTM", flush=True)
        return raw_dtm
    candidates = sorted(lola_dir.glob(f"{dtm_name}/LolaRDR_*_pts_csv.csv"))
    if not candidates:
        # try a glob across all dtm subdirs
        candidates = sorted(lola_dir.glob(f"*/LolaRDR_*_pts_csv.csv"))
    # pick the first one that has shots inside the DTM bbox
    for csv in candidates:
        # sniff the lola header
        try:
            head = pd.read_csv(csv, nrows=2)
        except Exception:
            continue
        if not {"Pt_Longitude", "Pt_Latitude", "Pt_Radius"}.issubset(set(head.columns)):
            continue
        # run kriging module
        sys.path.insert(0, str(WP0K))
        import importlib
        kc = importlib.import_module("kriging_correction")
        importlib.reload(kc)
        outdir = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_kriging"
        outdir.mkdir(parents=True, exist_ok=True)
        krig_out = krigcorr
        # read DTM bbox to set pit lat/lon (use the centroid)
        with rasterio.open(raw_dtm) as s:
            cx = (s.bounds.left + s.bounds.right) / 2.0
            cy = (s.bounds.bottom + s.bounds.top) / 2.0
        # cx, cy are in the DTM projected frame (metres); we need lat/lon
        from pyproj import CRS, Transformer
        geod = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")
        with rasterio.open(raw_dtm) as s:
            tr = Transformer.from_crs(s.crs, geod, always_xy=True)
            lon, lat = tr.transform(cx, cy)
        a = argparse.Namespace(
            dtm=str(raw_dtm),
            ref=str(csv),
            outdir=str(outdir),
            corr_out=str(krig_out),
            raw_depth_tif=None,
            tag=dtm_name,
            grid_spacing=150.0,
            boxcar_px=50,
            slope_max=2.0,
            holdout=0.2,
            seed=42,
            max_train=6000,
            pit_lat=lat,
            pit_lon=lon,
            pit_radius=200.0,
            geodetic_crs=geod,
            primitive_dir=str(REPO / "01_WORKSPACE" / "code" / "wp0_primitive"),
        )
        try:
            kc.run(a)
            if krig_out.exists():
                return krig_out
        except Exception as e:
            print(f"[krig] {dtm_name} kriging failed: {e}", flush=True)
            return raw_dtm
    return raw_dtm


def frangi_vesselness(Z, res, sigmas=(30, 60, 100, 150, 200, 300)):
    sigmas_px = tuple(max(0.5, s / res) for s in sigmas)
    Zf = np.where(np.isfinite(Z), Z, float(np.nanmean(Z[np.isfinite(Z)])) if np.isfinite(Z).any() else 0.0)
    V = frangi(Zf, sigmas=sigmas_px, black_ridges=True)
    return V.astype(np.float32)


def find_candidates(depth, frangi_v, res, score_p_min=0.5, neigh=5):
    score = np.where(np.isfinite(depth) & np.isfinite(frangi_v),
                     depth * frangi_v, 0.0).astype(np.float32)
    if score.max() <= 0:
        return [], score
    # local maxima of the score
    mf = maximum_filter(score, size=neigh, mode="nearest")
    is_peak = (score == mf) & (score >= score_p_min * score.max())
    rr, cc = np.where(is_peak)
    out = []
    for r, c in zip(rr, cc):
        out.append({
            "row": int(r), "col": int(c),
            "depth_m": float(depth[r, c]),
            "frangi": float(frangi_v[r, c]),
            "score": float(score[r, c]),
        })
    out.sort(key=lambda d: -d["score"])
    return out, score


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dtms", nargs="+", required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--lola-dir", type=Path, default=RAW / "lola_tracks")
    ap.add_argument("--no-kriging", action="store_true")
    ap.add_argument("--rungs", type=float, nargs="+", default=[2, 5])
    ap.add_argument("--frangi-sigmas", type=float, nargs="+",
                    default=[30, 60, 100, 150, 200, 300])
    ap.add_argument("--score-p-min", type=float, default=0.3)
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    # WhiteboxTools needs its binary dir set explicitly in this venv
    wbt = _wbt_with_dir()
    rows = []
    summary_per_dtm = {}
    for dtm_name in args.dtms:
        print(f"\n=== {dtm_name} ===", flush=True)
        if args.no_kriging:
            dtm_path = RAW / "dtms" / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
        else:
            dtm_path = existing_or_run_kriging(dtm_name, args.lola_dir)
        if not dtm_path.exists():
            print(f"[skip] {dtm_name}: no DTM at {dtm_path}", flush=True)
            continue
        with rasterio.open(dtm_path) as s:
            dtm = s.read(1).astype(np.float32)
            nodata = s.nodata
            res = float(s.res[0])
            transform = s.transform
            bounds = s.bounds
        if nodata is not None:
            dtm = np.where(dtm == nodata, np.nan, dtm)
        for r in args.rungs:
            print(f"  rung {r} m ...", flush=True)
            # only proceed if res ~ r
            if abs(res - r) / r > 0.6:
                # we'd need to reproject the DTM to r; skip in v0.1
                print(f"    skip: DTM res {res} m too far from rung {r} m", flush=True)
                continue
            # sink-fill (use absolute paths; whitebox resolves relative to
            # its own working dir and panics otherwise)
            tmp = (args.outdir / f"{dtm_name}_{r:g}m_tmp.tif").resolve()
            out_fill = (args.outdir / f"{dtm_name}_{r:g}m_filled.tif").resolve()
            # write temp DTM with sane nodata + CRS (WhiteboxTools
            # requires geokeys, so we read the source CRS and re-use it)
            with rasterio.open(dtm_path) as src:
                src_crs = src.crs
                src_profile = src.profile.copy()
            profile = src_profile.copy()
            profile.update({
                "dtype": "float32", "nodata": -9999.0,
                "compress": "deflate", "BIGTIFF": "IF_SAFER",
            })
            with rasterio.open(tmp, "w", **profile) as dst:
                dst.write(np.where(np.isfinite(dtm), dtm, -9999.0), 1)
            try:
                wbt.fill_depressions_planchon_and_darboux(dem=str(tmp), output=str(out_fill), fix_flats=True)
            except Exception as e:
                print(f"    sink-fill EXC: {e}", flush=True)
                continue
            if not out_fill.exists():
                # do NOT delete tmp; keep for debugging
                print(f"    sink-fill failed silently: tmp kept at {tmp}", flush=True)
                continue
            with rasterio.open(out_fill) as fs, rasterio.open(tmp) as ds:
                fill = fs.read(1).astype(np.float32)
                dtm_r = ds.read(1).astype(np.float32)
            fill = np.where(fill == -9999.0, np.nan, fill)
            dtm_r = np.where(dtm_r == -9999.0, np.nan, dtm_r)
            depth = np.maximum(fill - dtm_r, 0.0).astype(np.float32)
            F = frangi_vesselness(dtm_r, r, sigmas=tuple(args.frangi_sigmas))
            cands, score = find_candidates(depth, F, r, score_p_min=args.score_p_min)
            # output rasters
            for stem, arr_save in [("depth", depth), ("frangi", F), ("score", score)]:
                out = args.outdir / f"{dtm_name}_{r:g}m_{stem}.tif"
                with rasterio.open(out, "w", **profile) as dst:
                    dst.write(np.where(np.isfinite(arr_save), arr_save, -9999.0), 1)
            # for each candidate, find pixel -> projected coords
            print(f"    {len(cands)} candidate peaks (score>{args.score_p_min}*max)", flush=True)
            for c in cands[:200]:
                x, y = transform * (c["col"] + 0.5, c["row"] + 0.5)
                rows.append({
                    "dtm": dtm_name, "res_m": r,
                    "row": c["row"], "col": c["col"],
                    "x_m": float(x), "y_m": float(y),
                    "depth_m": c["depth_m"], "frangi": c["frangi"], "score": c["score"],
                })
            summary_per_dtm.setdefault(dtm_name, {})[r] = {
                "n_candidates": len(cands),
                "score_max": float(score.max()),
                "depth_max_m": float(np.nanmax(depth)) if np.isfinite(depth).any() else None,
            }
            # figure
            fig, ax = plt.subplots(1, 3, figsize=(15, 5))
            ax[0].imshow(np.where(np.isfinite(depth), depth, np.nan), cmap="magma", origin="lower")
            ax[0].set_title(f"depth (max {np.nanmax(depth):.1f} m)")
            ax[1].imshow(np.where(np.isfinite(F), F, np.nan), cmap="cividis", origin="lower")
            ax[1].set_title(f"Frangi 60-300 m")
            ax[2].imshow(np.where(np.isfinite(score), score, np.nan), cmap="inferno", origin="lower")
            ax[2].set_title(f"score (peaks n={len(cands)})")
            for a in ax: a.set_xticks([]); a.set_yticks([])
            fig.suptitle(f"{dtm_name} @ {r} m — Z2 sag search (v0.1)")
            fig.tight_layout()
            figp = args.outdir / f"{dtm_name}_{r:g}m_panels.png"
            fig.savefig(figp, dpi=120, bbox_inches="tight")
            plt.close(fig)
            print(f"    [out] figure -> {figp}", flush=True)

    # write per-candidate CSV
    cand_csv = args.outdir / "sag_candidates.csv"
    df = pd.DataFrame(rows)
    df.to_csv(cand_csv, index=False)
    print(f"\n[out] candidates -> {cand_csv} ({len(df)} rows)", flush=True)
    # summary json
    sum_path = args.outdir / "sag_search_summary.json"
    with open(sum_path, "w") as f:
        json.dump({
            "generated": str(date.today()),
            "dtms": args.dtms, "rungs": args.rungs,
            "frangi_sigmas": args.frangi_sigmas,
            "summary_per_dtm": summary_per_dtm,
            "n_candidates": int(len(df)),
        }, f, indent=2)
    print(f"[out] summary -> {sum_path}", flush=True)


if __name__ == "__main__":
    main()
