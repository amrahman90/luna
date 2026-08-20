"""Z2 sag search — production version (Task 18.1).

Runs the I2 kriging correction (or uses existing), downsamples the
DTM to a manageable posting for Frangi (default 10 m, well below the
60-300 m tube band so the vesselness is preserved), and emits a
per-candidate CSV with depth + Frangi + score peaks.

Output: data/outputs/wp2_sag/<DTM>/sag_candidates.csv +
        data/outputs/wp2_sag/<DTM>/sag_panels_*.png +
        data/outputs/wp2_sag/<DTM>/sag_summary.json

CLI:
  sag_search_run.py --dtms TRANQPIT1 --outdir 01_WORKSPACE/data/outputs/wp2_sag
                     [--rungs 5 10]  # default: 5 m and 10 m
                     [--no-kriging]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import Affine
from scipy.ndimage import maximum_filter
from skimage.filters import frangi

REPO = Path(__file__).resolve().parents[3]
RAW = Path.home() / "lunarvoid" / "data"
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp0_primitive"))
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp0_kriging"))

# ---- helpers (mirror sag_search.py) --------------------------------


def _wbt_with_dir():
    import whitebox
    wbt = whitebox.WhiteboxTools()
    wbt_dir = os.path.join(os.path.dirname(whitebox.__file__))
    if os.path.isfile(os.path.join(wbt_dir, "whitebox_tools")):
        wbt.set_whitebox_dir(wbt_dir)
    wbt.set_working_dir(tempfile.gettempdir())
    wbt.verbose = False
    return wbt


def existing_or_run_kriging(dtm_name, lola_dir):
    raw = RAW / "dtms" / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
    krig = RAW / "outputs" / dtm_name / f"NAC_DTM_{dtm_name}_krigcorr.tif"
    if krig.exists():
        return krig
    # else fall back to raw DTM
    return raw


def frangi_vesselness(Z, sigmas):
    Zf = np.where(np.isfinite(Z), Z, float(np.nanmean(Z[np.isfinite(Z)])) if np.isfinite(Z).any() else 0.0)
    Zf = Zf.astype(np.float64)  # avoid float32 overflow
    V = frangi(Zf, sigmas=sigmas, black_ridges=True)
    V = np.where(np.isfinite(V), V, 0).astype(np.float32)
    return V


def find_peaks(score, threshold_frac=0.10, neigh=5):
    if score.max() <= 0:
        return []
    mf = maximum_filter(score, size=neigh, mode="nearest")
    is_peak = (score == mf) & (score >= threshold_frac * score.max())
    rr, cc = np.where(is_peak)
    out = []
    for r, c in zip(rr, cc):
        out.append({
            "row": int(r), "col": int(c),
            "score": float(score[r, c]),
        })
    out.sort(key=lambda d: -d["score"])
    return out


def run_one_dtm(dtm_name, outdir, args, wbt):
    print(f"\n=== {dtm_name} ===", flush=True)
    dtm_path = existing_or_run_kriging(dtm_name, RAW / "lola_tracks")
    if not dtm_path.exists():
        print(f"  [skip] {dtm_name}: no DTM at {dtm_path}", flush=True)
        return None
    with rasterio.open(dtm_path) as s:
        dtm_full = s.read(1).astype(np.float64)
        res_full = float(s.res[0])
        transform_full = s.transform
        nodata = s.nodata
        src_crs = s.crs
        src_profile = s.profile.copy()
    if nodata is not None:
        dtm_full = np.where(dtm_full == nodata, np.nan, dtm_full)
    print(f"  source DTM: {dtm_full.shape} at {res_full} m/px (CRS {src_crs})", flush=True)

    summary = {"res_m_source": res_full, "rungs": {}}
    all_rows = []
    for rung in args.rungs:
        # skip rungs too far from source res (we resample, not reproject)
        if abs(res_full - rung) / rung > 0.6:
            print(f"  rung {rung} m: skipped (source res too different)", flush=True)
            continue
        factor = max(1, int(round(rung / res_full)))
        if factor == 1:
            dtm_r = dtm_full
            transform_r = transform_full
        else:
            dtm_r = None
            transform_r = None
        if factor > 1:
            with rasterio.open(dtm_path) as s:
                dtm_r = s.read(1, out_shape=(s.height // factor, s.width // factor),
                              resampling=Resampling.average).astype(np.float64)
                transform_r = s.transform * s.transform.scale(factor, factor)
            if nodata is not None:
                dtm_r = np.where(dtm_r == nodata, np.nan, dtm_r)
        # For rungs >= source_res*2 (factor 1), the pixel count can be
        # too large for Frangi; always sub-sample for Frangi speed while
        # keeping the depth/Frangi rasters at the rung posting. Cap the
        # working shape at 5000 px in the larger dimension.
        H, W = dtm_r.shape
        if max(H, W) > 5000:
            frangi_scale = max(H, W) / 5000.0
            new_h = int(round(H / frangi_scale))
            new_w = int(round(W / frangi_scale))
            with rasterio.open(dtm_path) as s:
                dtm_fr = s.read(1, out_shape=(new_h, new_w),
                                resampling=Resampling.average).astype(np.float64)
                transform_fr = s.transform * s.transform.scale(s.width / new_w, s.height / new_h)
            if nodata is not None:
                dtm_fr = np.where(dtm_fr == nodata, np.nan, dtm_fr)
            effective_rung = res_full * (s.width / new_w)
            print(f"  rung {rung} m: shape {dtm_r.shape} (Frangi sub-sampled to {dtm_fr.shape} at ~{effective_rung:.1f} m)",
                  flush=True)
        else:
            dtm_fr = dtm_r
            transform_fr = transform_r
            effective_rung = rung
        # we use `effective_rung` for the Frangi sigmas and write the
        # Frangi + score rasters at THAT posting; the depth raster stays
        # at the requested rung posting.

        # sink-fill (absolute paths required for whitebox; CRS required
        # for whitebox to read geokeys - we re-use the source CRS)
        tmp = (outdir / f"{dtm_name}_{rung:g}m_tmp.tif").resolve()
        out_fill = (outdir / f"{dtm_name}_{rung:g}m_filled.tif").resolve()
        depth_path = (outdir / f"{dtm_name}_{rung:g}m_depth.tif").resolve()
        profile = src_profile.copy()
        profile.update({
            "dtype": "float32", "nodata": -9999.0,
            "height": dtm_r.shape[0], "width": dtm_r.shape[1],
            "transform": transform_r,
            "compress": "deflate", "BIGTIFF": "IF_SAFER",
        })
        with rasterio.open(tmp, "w", **profile) as dst:
            dst.write(np.where(np.isfinite(dtm_r), dtm_r, -9999.0).astype(np.float32), 1)
        t = time.time()
        try:
            wbt.fill_depressions_planchon_and_darboux(dem=str(tmp), output=str(out_fill), fix_flats=True)
        except Exception as e:
            print(f"    sink-fill EXC: {e}", flush=True)
            continue
        if not out_fill.exists():
            print(f"    sink-fill failed silently (kept tmp for inspection)", flush=True)
            continue
        print(f"    sink-fill: {time.time()-t:.1f}s -> {out_fill.name}", flush=True)
        with rasterio.open(out_fill) as fs, rasterio.open(tmp) as ds:
            fill = fs.read(1).astype(np.float64)
            dtm = ds.read(1).astype(np.float64)
        fill = np.where(fill == -9999.0, np.nan, fill)
        dtm = np.where(dtm == -9999.0, np.nan, dtm)
        depth = np.maximum(fill - dtm, 0).astype(np.float32)
        with rasterio.open(depth_path, "w", **profile) as dst:
            dst.write(np.where(np.isfinite(depth), depth, -9999.0), 1)

        # Re-bin depth to the Frangi resolution if it differs
        if depth.shape != dtm_fr.shape:
            depth_fr = np.empty(dtm_fr.shape, dtype=np.float32)
            with rasterio.open(dtm_path) as s:
                depth_fr_full = s.read(1, out_shape=dtm_fr.shape, resampling=Resampling.average).astype(np.float64)
            # depth bin = mean of valid depth values in the cell
            with rasterio.open(depth_path) as s:
                depth_raw = s.read(1)
            # simple nearest-neighbour block average via zoom
            from scipy.ndimage import zoom
            depth_fr = zoom(np.where(depth_raw == -9999.0, np.nan, depth_raw).astype(np.float64),
                            (dtm_fr.shape[0] / depth_raw.shape[0], dtm_fr.shape[1] / depth_raw.shape[1]),
                            order=1).astype(np.float32)
        else:
            depth_fr = depth

        # Frangi at the 60-300 m band (sigmas in metres -> px)
        sigmas_m = (60, 100, 150, 200, 300)
        sigmas_px = tuple(max(2, s / effective_rung) for s in sigmas_m)
        t = time.time()
        F = frangi_vesselness(dtm_fr, sigmas_px)
        print(f"    Frangi: {time.time()-t:.1f}s -> {F.shape} max={F.max():.3f}", flush=True)
        frangi_path = (outdir / f"{dtm_name}_{rung:g}m_frangi.tif").resolve()
        profile_fr = profile.copy()
        profile_fr.update({"height": F.shape[0], "width": F.shape[1],
                          "transform": transform_fr})
        with rasterio.open(frangi_path, "w", **profile_fr) as dst:
            dst.write(np.where(np.isfinite(F), F, -9999.0), 1)
        score = (np.where(np.isfinite(depth_fr), depth_fr, 0) * F).astype(np.float32)
        score_path = (outdir / f"{dtm_name}_{rung:g}m_score.tif").resolve()
        with rasterio.open(score_path, "w", **profile_fr) as dst:
            dst.write(np.where(np.isfinite(score), score, -9999.0), 1)

        # local maxima as candidates
        peaks = find_peaks(score, args.score_frac, args.neigh)
        n = len(peaks)
        print(f"    peaks >= {args.score_frac*100:.0f}% of max: {n}", flush=True)
        for p in peaks[:args.max_candidates]:
            x, y = transform_fr * (p["col"] + 0.5, p["row"] + 0.5)
            all_rows.append({
                "dtm": dtm_name, "res_m": rung, "row": p["row"], "col": p["col"],
                "x_m": float(x), "y_m": float(y),
                "depth_m": float(depth_fr[p["row"], p["col"]])
                              if np.isfinite(depth_fr[p["row"], p["col"]]) else float("nan"),
                "frangi": float(F[p["row"], p["col"]]),
                "score": p["score"],
            })
        summary["rungs"][rung] = {
            "shape": list(dtm_r.shape),
            "frangi_shape": list(dtm_fr.shape),
            "n_peaks": n,
            "depth_max_m": float(np.nanmax(depth)) if np.isfinite(depth).any() else None,
            "frangi_max": float(F.max()),
            "score_max": float(score.max()),
        }

        # figure
        fig, ax = plt.subplots(1, 3, figsize=(15, 5))
        # hillshade
        dz = np.gradient(np.where(np.isfinite(dtm_fr), dtm_fr, np.nanmean(dtm_fr)), effective_rung)
        slope = np.pi / 2.0 - np.arctan(np.hypot(dz[1], dz[0]))
        aspect = np.arctan2(-dz[1], dz[0])
        az, al = np.radians(315.0), np.radians(45.0)
        hs = np.clip(255.0 * (np.sin(al) * np.sin(slope) +
                               np.cos(al) * np.cos(slope) * np.cos(az - aspect)), 0, 255)
        ax[0].imshow(hs, cmap="gray", origin="lower"); ax[0].set_title(f"hillshade {effective_rung:.0f} m")
        im1 = ax[1].imshow(np.where(np.isfinite(depth_fr), depth_fr, np.nan), cmap="magma", origin="lower")
        ax[1].set_title(f"depth (max {np.nanmax(depth_fr):.1f} m)")
        plt.colorbar(im1, ax=ax[1])
        im2 = ax[2].imshow(np.where(np.isfinite(score), score, np.nan), cmap="inferno", origin="lower")
        ax[2].set_title(f"score (peaks n={n})")
        plt.colorbar(im2, ax=ax[2])
        for a in ax: a.set_xticks([]); a.set_yticks([])
        fig.suptitle(f"{dtm_name} @ {rung} m (Frangi@{effective_rung:.0f}m) — Z2 v0.1")
        fig.tight_layout()
        fig_path = outdir / f"sag_panels_{dtm_name}_{rung:g}m.png"
        fig.savefig(fig_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(f"    figure -> {fig_path.name}", flush=True)

        # cleanup tmp + filled to save space
        try: tmp.unlink()
        except FileNotFoundError: pass
        try: out_fill.unlink()
        except FileNotFoundError: pass

    df = pd.DataFrame(all_rows)
    cand_csv = outdir / "sag_candidates.csv"
    df.to_csv(cand_csv, index=False)
    print(f"  [candidates] {len(df)} rows -> {cand_csv.name}", flush=True)
    sum_path = outdir / "sag_search_summary.json"
    with open(sum_path, "w") as f:
        json.dump({
            "generated": str(date.today()),
            "dtm": dtm_name, "rungs": args.rungs,
            "n_candidates": int(len(df)),
            "summary_per_rung": summary,
        }, f, indent=2)
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dtms", nargs="+", required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--rungs", type=float, nargs="+", default=[5, 10])
    ap.add_argument("--score-frac", type=float, default=0.10)
    ap.add_argument("--neigh", type=int, default=5)
    ap.add_argument("--max-candidates", type=int, default=200)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    wbt = _wbt_with_dir()
    summaries = {}
    for d in args.dtms:
        s = run_one_dtm(d, args.outdir, args, wbt)
        if s is not None:
            summaries[d] = s
    with open(args.outdir / "sag_search_summary.json", "w") as f:
        json.dump({"generated": str(date.today()),
                   "dtms": args.dtms, "rungs": args.rungs,
                   "summaries": summaries}, f, indent=2)
    print(f"\n[done] {len(summaries)} DTMs processed; outputs in {args.outdir}")


if __name__ == "__main__":
    main()
