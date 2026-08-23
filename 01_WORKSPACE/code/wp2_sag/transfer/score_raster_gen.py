"""P3.1c growth — Frangi score-raster generator for new NAC DTMs.

Uses the FROZEN Z2 recipe (sigmas = (30, 60, 100, 150, 200, 300) m; PD fill;
neigh=5; seed=42) on the new on-disk DTMs that did not have a cached v0.1
score raster under the N=19 P3.1c re-run.

Memory strategy:
  - Source DTM is opened with rasterio but NOT loaded into a contiguous
    float64 array (sag_search_run.py v0.2 loaded the whole thing as
    float64; that overflowed RAM on 1.44 GiB DTMs).
  - Rebin operations use rasterio's `out_shape=` resampling (writes
    straight into the smaller array; no intermediate float64 of full DTM).
  - Rebinned DTM kept as float32 throughout until Frangi (which requires
    float64 to avoid the v0.1 float32-overflow bug, conventions §8.3).
  - DTMs > 300 MB float32 (TYCHOPK07 ~ 365 MB, FRESHMELT ~ 354 MB) use
    Frangi sub-sampling to <= 5000 px max dim (already in sag_search_run.py).

Output:
  ~/lunarvoid/data/outputs/wp2_sag/score_rasters/<DTM>/score_<rung>m.tif
  ~/lunarvoid/data/outputs/wp2_sag/score_rasters/<DTM>/depth_<rung>m.tif
  ~/lunarvoid/data/outputs/wp2_sag/score_rasters/<DTM>/frangi_<rung>m.tif

Run with the venv python:
  /home/frostflux/lunarvoid/venv/bin/python 01_WORKSPACE/code/wp2_sag/transfer/score_raster_gen.py \
    --dtms FECUNPIT KINGCRATER2 ... \
    --rungs 2 4 5
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

import numpy as np
import rasterio
from rasterio.enums import Resampling
from skimage.filters import frangi

REPO = Path(__file__).resolve().parents[4]
RAW = Path.home() / "lunarvoid" / "data"
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp0_primitive"))


# ---- FROZEN (P3.1b) calibration parameters UNCHANGED --------------------
FROZEN_SIGMAS_M = (30, 60, 100, 150, 200, 300)
FROZEN_FRAC = 0.20
FROZEN_SLOPE = 45.0
FROZEN_NEIGH = 5
FILL = "planchon_darboux (fix_flats=True)"
SEED = 42
OUT_ROOT = RAW / "outputs" / "wp2_sag" / "score_rasters"
FRANGI_MAX_DIM = 5000


def _wbt_with_dir():
    """WhiteboxTools with the venv-local binary path + writable working
    directory. Mirrors sag_search_run.py._wbt_with_dir (conventions §8.2)."""
    import whitebox
    wbt = whitebox.WhiteboxTools()
    wbt_dir = os.path.join(os.path.dirname(whitebox.__file__))
    if os.path.isfile(os.path.join(wbt_dir, "whitebox_tools")):
        wbt.set_whitebox_dir(wbt_dir)
    wbt.set_working_dir(tempfile.gettempdir())
    wbt.verbose = False
    return wbt


def dtm_source(dtm_name: str) -> Path:
    """Source DTM path (krigcorr preferred; raw fallback)."""
    krig = RAW / "outputs" / dtm_name / f"NAC_DTM_{dtm_name}_krigcorr.tif"
    raw = RAW / "dtms" / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
    return krig if krig.exists() else raw


def frangi_vesselness(Z, sigmas_px):
    """Frangi vesselness, float64-masked to avoid the v0.1 float32 overflow
    (conventions §8.3). NaN replaced with mean of finite values."""
    Zf = np.where(np.isfinite(Z), Z,
                  float(np.nanmean(Z[np.isfinite(Z)])) if np.isfinite(Z).any() else 0.0)
    Zf = Zf.astype(np.float64)  # avoid float32 overflow on large sigmas
    V = frangi(Zf, sigmas=sigmas_px, black_ridges=True)
    V = np.where(np.isfinite(V), V, 0).astype(np.float32)
    return V


def run_one_dtm(dtm_name: str, rungs: list, wbt, out_root: Path,
                skip_existing: bool = True) -> dict:
    """Generate score/depth/frangi rasters at the requested rungs.

    FROZEN recipe: sigmas_m = (30, 60, 100, 150, 200, 300); PD fill;
    score = depth * Frangi (vesselness, black_ridges=True). Rasterio
    rebin uses Resampling.average (matches sag_search_run.py semantics).

    Returns a per-DTM dict with one entry per rung produced.
    """
    print(f"\n=== {dtm_name} ===", flush=True)
    dtm_path = dtm_source(dtm_name)
    if not dtm_path.exists():
        print(f"  [skip] no DTM at {dtm_path}", flush=True)
        return {"dtm": dtm_name, "rungs": {}, "error": "no DTM"}
    outdir = out_root / dtm_name
    outdir.mkdir(parents=True, exist_ok=True)
    # Source DTM info — open WITHOUT loading the whole array
    with rasterio.open(dtm_path) as src:
        H_src, W_src = src.height, src.width
        res_full = float(src.res[0])
        transform_full = src.transform
        nodata = src.nodata
        src_crs = src.crs
        src_profile = src.profile.copy()
    print(f"  source: {H_src}x{W_src} @ {res_full:.4f} m/px "
          f"(CRS: {src_crs}) | nodata={nodata}", flush=True)
    if nodata is not None:
        # Sentinel guard: PDS NAC DTMs use ~-3.4e38 nodata; >1e30 is sentinel
        # (NOT the >1000m rule from conventions §8.4 — that's for raw f32
        # point clouds; GeoTIFF DTMs may have intrinsic elevations, e.g.
        # FECNDITATS2 sits at ~-1700 m).
        print(f"  nodata sentinel: {nodata:.3e}", flush=True)

    summary_rungs = {}
    for rung in rungs:
        t0 = time.time()
        # res-compatibility check (sag_search.py 0.6 rule)
        if abs(res_full - rung) / rung > 0.6:
            print(f"  [skip-rung] {rung:g} m: source res {res_full:.3f} m "
                  f"too different (abs diff / rung > 0.6)", flush=True)
            continue
        score_path = outdir / f"score_{rung:g}m.tif"
        depth_path = outdir / f"depth_{rung:g}m.tif"
        frangi_path = outdir / f"frangi_{rung:g}m.tif"
        if skip_existing and score_path.exists():
            print(f"  [skip-rung] {rung:g} m: score raster already at "
                  f"{score_path}", flush=True)
            summary_rungs[rung] = {"status": "exists"}
            continue
        # Rasterio supports fractional output scales.  Do not round the
        # requested posting to an integer factor: for a 2 m source, a 5 m
        # rung is a 2.5x scale factor, not 2x (Python's round(2.5) is 2).
        scale_factor = max(1.0, float(rung) / res_full)
        new_h = max(1, int(np.ceil(H_src / scale_factor)))
        new_w = max(1, int(np.ceil(W_src / scale_factor)))
        # 1. Rebin DTM to rung posting (float32; rasterio out_shape writes
        #    directly into the smaller array, never allocates a full-DTM float64)
        with rasterio.open(dtm_path) as src:
            dtm_r = src.read(
                1,
                out_shape=(new_h, new_w),
                resampling=Resampling.average,
            ).astype(np.float32)
            # Derive the transform from the actual output dimensions so
            # non-integer rungs retain the requested posting.
            transform_r = src.transform * src.transform.scale(
                src.width / new_w, src.height / new_h
            )
        if nodata is not None:
            dtm_r = np.where(dtm_r == nodata, np.nan, dtm_r).astype(np.float32)
            # f32 sentinel guard: where the sentinel got diluted by averaging
            # below exact match, |val| > 1e30 is still sentinel
            dtm_r = np.where(np.abs(dtm_r) > 1e30, np.nan, dtm_r).astype(np.float32)
        # 2. Frangi sub-sample to <= 5000 px max dim (conventions §8.3)
        H_r, W_r = dtm_r.shape
        if max(H_r, W_r) > FRANGI_MAX_DIM:
            frangi_scale = max(H_r, W_r) / float(FRANGI_MAX_DIM)
            new_h = int(round(H_r / frangi_scale))
            new_w = int(round(W_r / frangi_scale))
            with rasterio.open(dtm_path) as src:
                dtm_fr = src.read(
                    1,
                    out_shape=(new_h, new_w),
                    resampling=Resampling.average,
                ).astype(np.float32)
                # transform for the sub-sampled grid
                transform_fr = src.transform * src.transform.scale(
                    src.width / new_w, src.height / new_h
                )
            if nodata is not None:
                dtm_fr = np.where(dtm_fr == nodata, np.nan, dtm_fr).astype(np.float32)
                dtm_fr = np.where(np.abs(dtm_fr) > 1e30, np.nan, dtm_fr).astype(np.float32)
            effective_rung = res_full * (src.width / new_w)
            print(f"  rung {rung:g} m: shape {dtm_r.shape} -> Frangi sub-sample "
                  f"{dtm_fr.shape} @ ~{effective_rung:.2f} m", flush=True)
        else:
            dtm_fr = dtm_r
            transform_fr = transform_r
            effective_rung = rung
            print(f"  rung {rung:g} m: shape {dtm_r.shape} (Frangi same grid "
                  f"@ {effective_rung:.2f} m)", flush=True)
        # 3. Planchon-Darboux fill (conventions §1.1 — NOT Wang & Liu)
        #    Use absolute paths; whitebox needs geokeys (we re-use source CRS)
        tmp = (outdir / f"_tmp_{dtm_name}_{rung:g}m.tif").resolve()
        filled = (outdir / f"_filled_{dtm_name}_{rung:g}m.tif").resolve()
        profile_r = src_profile.copy()
        profile_r.update({
            "dtype": "float32", "nodata": -9999.0,
            "height": dtm_r.shape[0], "width": dtm_r.shape[1],
            "transform": transform_r,
            "compress": "deflate", "BIGTIFF": "IF_SAFER",
        })
        with rasterio.open(tmp, "w", **profile_r) as dst:
            dst.write(np.where(np.isfinite(dtm_r), dtm_r, -9999.0).astype(np.float32), 1)
        t_fill = time.time()
        try:
            wbt.fill_depressions_planchon_and_darboux(
                dem=str(tmp), output=str(filled), fix_flats=True
            )
        except Exception as e:
            print(f"    sink-fill EXC: {e}", flush=True)
            continue
        if not filled.exists():
            print(f"    sink-fill failed silently (kept tmp for inspection)",
                  flush=True)
            continue
        print(f"    sink-fill: {time.time()-t_fill:.1f}s", flush=True)
        with rasterio.open(filled) as fs, rasterio.open(tmp) as ds:
            fill = fs.read(1).astype(np.float32)
            dtm = ds.read(1).astype(np.float32)
        fill = np.where(fill == -9999.0, np.nan, fill)
        dtm = np.where(dtm == -9999.0, np.nan, dtm)
        depth = np.maximum(fill - dtm, 0).astype(np.float32)
        # rebin depth to Frangi grid if they differ
        if depth.shape != dtm_fr.shape:
            from scipy.ndimage import zoom
            depth_fr = zoom(
                depth.astype(np.float64),
                (dtm_fr.shape[0] / depth.shape[0],
                 dtm_fr.shape[1] / depth.shape[1]),
                order=1,
            ).astype(np.float32)
        else:
            depth_fr = depth
        # 4. Frangi (FROZEN sigmas in METRES -> pixels at effective_rung)
        sigmas_px = tuple(max(2.0, s / effective_rung) for s in FROZEN_SIGMAS_M)
        t_fr = time.time()
        F = frangi_vesselness(dtm_fr, sigmas_px)
        print(f"    Frangi({sigmas_px}): {time.time()-t_fr:.1f}s "
              f"-> {F.shape} max={F.max():.3f}", flush=True)
        # 5. score = depth_fr * F (FROZEN recipe)
        score = (np.where(np.isfinite(depth_fr), depth_fr, 0) * F).astype(np.float32)
        # 6. Write output rasters with the source CRS (geokeys preserved)
        profile_fr = profile_r.copy()
        profile_fr.update({"height": F.shape[0], "width": F.shape[1],
                          "transform": transform_fr})
        # Depth is a product at the requested rung grid.  Frangi and score
        # are written separately on the sub-sampled grid, so do not reuse
        # profile_fr for depth.
        with rasterio.open(depth_path, "w", **profile_r) as dst:
            dst.write(np.where(np.isfinite(depth), depth, -9999.0).astype(np.float32), 1)
        with rasterio.open(frangi_path, "w", **profile_fr) as dst:
            dst.write(np.where(np.isfinite(F), F, -9999.0).astype(np.float32), 1)
        with rasterio.open(score_path, "w", **profile_fr) as dst:
            dst.write(np.where(np.isfinite(score), score, -9999.0).astype(np.float32), 1)
        # cleanup tmp + filled
        try: tmp.unlink()
        except FileNotFoundError: pass
        try: filled.unlink()
        except FileNotFoundError: pass
        runtime = round(time.time() - t0, 1)
        print(f"  [done] {dtm_name} rung {rung:g} m -> "
              f"score {score.shape} max={float(score.max()):.3f} "
              f"| {runtime}s", flush=True)
        summary_rungs[rung] = {
            "shape": list(score.shape),
            "eff_m": float(effective_rung),
            "depth_max_m": float(np.nanmax(depth)) if np.isfinite(depth).any() else None,
            "frangi_max": float(F.max()),
            "score_max": float(score.max()),
            "rung_grid_shape": list(dtm_r.shape),
            "frangi_sub_sampled": max(H_r, W_r) > FRANGI_MAX_DIM,
            "runtime_s": runtime,
            "score_path": str(score_path),
            "depth_path": str(depth_path),
            "frangi_path": str(frangi_path),
        }
    return {"dtm": dtm_name, "rungs": summary_rungs}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dtms", nargs="+", required=True,
                    help="DTM names to process (without NAC_DTM_ prefix)")
    ap.add_argument("--rungs", type=float, nargs="+", default=[2.0, 4.0, 5.0],
                    help="rung postings in metres (default: 2 4 5)")
    ap.add_argument("--outdir", type=Path, default=OUT_ROOT)
    ap.add_argument("--no-skip-existing", action="store_true",
                    help="recompute even if score raster exists")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    wbt = _wbt_with_dir()
    print(f"[init] FROZEN sigmas_m={FROZEN_SIGMAS_M}; rungs={args.rungs}; "
          f"outdir={args.outdir}", flush=True)
    all_summaries = {}
    t0 = time.time()
    for d in args.dtms:
        s = run_one_dtm(d, args.rungs, wbt, args.outdir,
                        skip_existing=not args.no_skip_existing)
        all_summaries[d] = s
    elapsed = round(time.time() - t0, 1)
    summary_path = args.outdir / "score_raster_gen_summary.json"
    with open(summary_path, "w") as f:
        json.dump({
            "generated": date.today().isoformat(),
            "frozen_sigmas_m": list(FROZEN_SIGMAS_M),
            "frozen_score_frac": FROZEN_FRAC,
            "frozen_slope_deg": FROZEN_SLOPE,
            "frozen_neigh": FROZEN_NEIGH,
            "fill": FILL,
            "seed": SEED,
            "rungs_requested": args.rungs,
            "frangi_max_dim": FRANGI_MAX_DIM,
            "dtms": args.dtms,
            "summaries": all_summaries,
            "runtime_s": elapsed,
        }, f, indent=2)
    print(f"\n[done] {len(all_summaries)} DTMs processed; "
          f"summary -> {summary_path} | {elapsed}s")


if __name__ == "__main__":
    main()
