"""LLTB-1 sag detector (Z1, Task 14.2) + per-rung detectability evaluation
(Task 14.3, 14.4, 14.5).

For a raster DTM (one of the ladder rungs), compute:
  - sink-fill (Planchon-Darboux) - DTM = depression depth
  - Frangi vesselness at 60-300 m scales (the realistic tube-width band)
  - local continuity score (length of the connected component)
  - per-cell "sag candidate" score = depth x vesselness
  - per-rung: re-tune the depth threshold (v5 I9) on a calibration split
    (50% of the cloud), apply to the held-out 50%, record both F1 and the
    full stratified detectability curve vs feature size.

For the analog benchmark, "ground truth" is derived from the source
point cloud: a cell is "on a void" if its column contains points from
BELOW the surrounding ground envelope by more than 1 m (this isolates
the cave interior footprint in the cloud). That is a generous
definition; it serves as the LLTB-1 label set for the v0.1 release.

CLI:
  sag_detect.py --npz path/to/analog.npz --outdir <repo out dir>
                [--rungs 0.02 0.5 2 5 60] [--grid-spacing 0.5]
                [--cc-filter off|on|auto]  (C3, default off = v0.5 parity)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import whitebox
from rasterio.transform import Affine, from_bounds
from scipy.ndimage import label as ndlabel
from skimage.filters import frangi
from whitebox import WhiteboxTools

# C3 (LLTB-1 v0.6 candidate): standalone connected-component engine +
# per-rung AREA_MIN table. Dual import style: this file is executed BOTH
# as a bare script (sys.path[0] = wp1_detector/) and as a namespace-
# package module (wp1_detector.sag_detect, code/ on sys.path — e.g.
# hapke_render.py / sensor_degrade.py). Try package style first, fall
# back to the bare-script style.
try:
    from wp1_detector.connected_component_filter import (  # noqa: E402
        AREA_MIN_PER_RUNG,
        area_min_for_rung,
        connected_component_filter,
    )
except ImportError:  # bare-script execution
    from connected_component_filter import (  # noqa: E402
        AREA_MIN_PER_RUNG,
        area_min_for_rung,
        connected_component_filter,
    )


def cloud_ground_truth(x, y, z, pixel: float, threshold_depth: float = 1.0):
    """Boolean raster of cells containing a point >threshold_depth BELOW
    the local surface envelope (= 'this cell is above a void').

    Surface envelope = nan-robust 50th-percentile over a large cell
    neighbourhood (default 21x21 cells, ~5-10x the largest expected
    void cell). The difference (envelope - cell_min_z) > threshold
    marks the cell as over a void. This is robust against flat mare
    panels with a small number of outliers (boulders, narrow rilles)
    AND it localises the void footprint even when the per-cell min
    matches the local 5x5 minimum.
    """
    finite = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[finite], y[finite], z[finite]
    x_min, y_min = x.min(), y.min()
    x_max, y_max = x.max(), y.max()
    nx = max(1, int(np.ceil((x_max - x_min) / pixel)))
    ny = max(1, int(np.ceil((y_max - y_min) / pixel)))
    col = np.clip(((x - x_min) / pixel).astype(int), 0, nx - 1)
    row = np.clip(((y - y_min) / pixel).astype(int), 0, ny - 1)
    flat = row * nx + col
    sums = np.bincount(flat, weights=z, minlength=ny * nx)
    cnts = np.bincount(flat, minlength=ny * nx)
    zmin = np.full(ny * nx, np.inf)
    np.minimum.at(zmin, flat, z)
    zmin = zmin.reshape(ny, nx)
    zmin[cnts.reshape(ny, nx) == 0] = np.nan
    # local surface envelope = nan-robust percentile over a 21x21 window
    # (large enough that any reasonable void footprint is much smaller)
    from scipy.ndimage import generic_filter
    def nan_pct(arr):
        v = arr[np.isfinite(arr)]
        return np.percentile(v, 50) if len(v) else np.nan
    env = generic_filter(np.where(np.isfinite(zmin), zmin, np.nan),
                         nan_pct, size=21, mode="nearest")
    void_above = (env - zmin) > threshold_depth
    void_above &= np.isfinite(zmin) & np.isfinite(env)
    return void_above, (x_min, y_min, nx, ny, pixel)


def frangi_vesselness(Z: np.ndarray, res: float, sigmas=(30, 60, 100, 150, 200, 300)):
    """Frangi vesselness at a list of physical-scale sigmas (m)."""
    # skimage expects sigma in PIXELS, not metres
    sigmas_px = tuple(max(0.5, s / res) for s in sigmas)
    finite = np.isfinite(Z)
    Zf = np.where(finite, Z, float(np.nanmean(Z[finite])) if finite.any() else 0.0)
    Zf = Zf.astype(np.float64)  # float32 overflow on large sigmas (conventions §8.3)
    V = frangi(Zf, sigmas=sigmas_px, black_ridges=True)  # black_ridges: tube = dark = low Z
    # Phase 0.6: zero vesselness at original-NoData cells so the fill
    # cannot fabricate phantom responses inside NoData regions (the
    # score was already 0 there via depth; this makes V itself honest).
    V = np.where(finite, V, 0.0)
    return V.astype(np.float32)


def sink_fill_planchon(wbt: WhiteboxTools, dem_path: Path, out_path: Path) -> Path:
    wbt.verbose = False
    wbt.fill_depressions_planchon_and_darboux(
        dem=str(dem_path), output=str(out_path), fix_flats=True
    )
    return out_path


def write_geotiff(arr: np.ndarray, transform: Affine, path: Path, crs: str = None, nodata=np.nan):
    # C9: default to the shared local-metric CRS (was: hardcoded "EPSG:32631")
    if crs is None:
        from _crs import ANALOG_CRS_WKT
        crs = ANALOG_CRS_WKT
    profile = {
        "driver": "GTiff", "dtype": "float32", "nodata": float(nodata) if np.isfinite(nodata) else -9999.0,
        "width": arr.shape[1], "height": arr.shape[0], "count": 1,
        "transform": transform, "crs": crs, "compress": "deflate", "BIGTIFF": "IF_SAFER",
    }
    with rasterio.open(path, "w", **profile) as dst:
        arr2 = np.where(np.isfinite(arr), arr, profile["nodata"]).astype(np.float32)
        dst.write(arr2, 1)


def f1_at_threshold(scores: np.ndarray, truth: np.ndarray, thr: float):
    pred = scores >= thr
    tp = int((pred & truth).sum())
    fp = int((pred & ~truth).sum())
    fn = int((~pred & truth).sum())
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"thr": float(thr), "tp": tp, "fp": fp, "fn": fn,
            "precision": prec, "recall": rec, "f1": f1}


def _f1_from_pred(pred: np.ndarray, truth: np.ndarray) -> dict:
    """Compute P/R/F1 from a pre-thresholded boolean prediction mask."""
    tp = int((pred & truth).sum())
    fp = int((pred & ~truth).sum())
    fn = int((~pred & truth).sum())
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"thr": 0.0, "tp": tp, "fp": fp, "fn": fn,
            "precision": prec, "recall": rec, "f1": f1}


def filter_small_components(mask: np.ndarray, min_size: int = 1) -> np.ndarray:
    """Return a copy of `mask` with connected components smaller than
    `min_size` removed. Uses 8-connectivity (king moves) so diagonal
    cells in a long thin sink chain are not split.

    This is the v0.2 precision lift named in the G0' report: the
    depth x Frangi score overflags single-cell artifacts; the
    connected-component filter suppresses them.

    NaN cells are not parts of any component (treated as background).
    """
    from scipy.ndimage import label
    if min_size <= 1:
        return mask
    finite_mask = mask & np.isfinite(mask)  # in case caller passes NaN as background
    structure = np.ones((3, 3), dtype=np.int8)  # 8-connectivity
    lab, n_components = label(finite_mask, structure=structure)
    if n_components == 0:
        return mask
    sizes = np.bincount(lab.ravel())
    # sizes[0] is the background; ignore it
    keep_labels = np.zeros_like(lab, dtype=bool)
    for lab_idx in range(1, n_components + 1):
        if sizes[lab_idx] >= min_size:
            keep_labels |= (lab == lab_idx)
    # preserve NaN semantics if any
    return keep_labels & np.isfinite(mask) | (mask & ~np.isfinite(mask))


def _cc_counts(binary: np.ndarray) -> tuple:
    """(n_components, sizes) of an 8-connected binary mask."""
    structure = np.ones((3, 3), dtype=np.int8)
    lab, n = ndlabel(binary & np.isfinite(binary), structure=structure)
    return int(n), np.bincount(lab.ravel(), minlength=n + 1)


def apply_cc_filter(score: np.ndarray, thr: float, mode: str,
                    min_component: int, cc_area_min, rung_m: float):
    """C3: post-threshold connected-component post-processing dispatch.

    Wiring point: called on the binary detection mask AFTER the score
    threshold, BEFORE slope masking / metrics. Modes:

      - ``off``  : the legacy v0.2-v0.5 inline scalar path
        (:func:`filter_small_components` with ``min_component``, default
        5). Byte-identical v0.5 parity arm — the frozen Paper 1/2
        evidence derives from this path.
      - ``on``   : the standalone :func:`connected_component_filter`
        engine with a UNIFORM ``area_min`` (``--cc-area-min``, falls
        back to ``min_component``).
      - ``auto`` : the standalone engine with the per-rung
        ``AREA_MIN_PER_RUNG`` table (V0.2_PLAN.md §4.1; scale-aware
        (GSD ratio)^2 rationale documented in the module).

    Returns ``(pred_mask, audit)`` where audit records the effective
    area_min, component counts, and the components_dropped ratio
    (near-1 = the mask is mostly noise; near-0 = filter is a no-op).
    """
    pred = score >= thr
    if mode == "off":
        filtered = filter_small_components(pred, min_size=min_component)
        n_total, sizes = _cc_counts(pred)
        area_eff = int(min_component)
        n_kept = int((sizes[1:] >= area_eff).sum()) if n_total else 0
    else:
        area_eff = (int(cc_area_min) if cc_area_min is not None
                    else int(min_component)) if mode == "on" \
            else int(area_min_for_rung(rung_m))
        # Engine = the standalone module (C3 wiring). Feed it the 0/1
        # raster at threshold 0.5 so the module's `score > threshold`
        # reproduces the pipeline's `score >= thr` mask exactly (the
        # tuned thr is a score quantile, so `== thr` cells exist).
        binf = pred.astype(np.float64)
        filtered_score, n_kept = connected_component_filter(
            binf, threshold=0.5, area_min=area_eff, connectivity=2)
        filtered = filtered_score > 0.5
        n_total, _ = _cc_counts(pred)
    n_dropped = n_total - n_kept
    audit = {
        "cc_filter": mode,
        "cc_area_min_effective": area_eff,
        "cc_components_total": n_total,
        "cc_components_kept": n_kept,
        "cc_components_dropped": n_dropped,
        "cc_components_dropped_ratio": (n_dropped / n_total) if n_total else 0.0,
        "cc_cells_dropped": int((pred & ~filtered).sum()),
    }
    return filtered, audit


def slope_mask(dtm: np.ndarray, pixel_m: float, min_slope_deg: float,
               smooth: int = 3) -> np.ndarray:
    """Return a boolean mask where True = "local slope is steep enough
    that a roof-sag dimple is geometrically plausible".

    Intuition: a 2 m amplitude dimple on a 60-300 m wavelength tube is
    INVISIBLE on a slope that's already 5 degrees or steeper (the
    dimple is dwarfed by the slope). On a slope gentler than ~3-5
    degrees, the dimple shows up clearly in the depression-depth
    raster as a faint bump; that's the regime our detector is in.

    This is the v0.3 precision lift proposed in the v0.2 release
    note's "what did NOT change" section.

    Algorithm
    ---------
    1. Compute |dz/dx| and |dz/dy| via np.gradient (in metres per cell;
       convert to metres per metre with pixel_m).
    2. Take the max gradient over a `smooth`-cellside neighbourhood
       (median filter; suppresses single-cell noise from the binned
       cloud DTM). This is the local slope (m/m).
    3. Convert to degrees: slope_deg = atan(slope) * 180/pi.
    4. Mask = slope_deg >= min_slope_deg.

    Returns boolean mask of shape dtm.shape. NaN cells (where dtm is
    NaN) are masked out (returned as False) so they don't survive
    downstream.
    """
    if min_slope_deg <= 0:
        return np.isfinite(dtm)
    if not np.isfinite(dtm).any():
        return np.zeros_like(dtm, dtype=bool)
    # dz per cell (metres per cell), then per metre
    dz_y, dz_x = np.gradient(np.where(np.isfinite(dtm), dtm,
                                      float(np.nanmean(dtm[np.isfinite(dtm)])))
                              if np.isfinite(dtm).any() else dtm,
                              pixel_m, pixel_m)
    slope_pm = np.hypot(dz_x, dz_y)  # m/m
    # median smoothing to suppress single-cell noise (binning artifacts)
    if smooth > 1:
        from scipy.ndimage import median_filter
        slope_pm = median_filter(slope_pm, size=smooth, mode="nearest")
    slope_deg = np.degrees(np.arctan(slope_pm))
    return (slope_deg >= min_slope_deg) & np.isfinite(dtm)


def slope_deg_map(dtm: np.ndarray, pixel_m: float, smooth: int = 3) -> np.ndarray:
    """Return the per-cell local slope in DEGREES (the same value
    that `slope_mask()` thresholds). NaN where dtm is NaN.

    Useful for per-rung slope-threshold tuning: you want the
    continuous slope_deg, then sweep thresholds on top of it.
    """
    if not np.isfinite(dtm).any():
        return np.full_like(dtm, np.nan, dtype=np.float64)
    dz_y, dz_x = np.gradient(np.where(np.isfinite(dtm), dtm,
                                      float(np.nanmean(dtm[np.isfinite(dtm)]))),
                              pixel_m, pixel_m)
    slope_pm = np.hypot(dz_x, dz_y)
    if smooth > 1:
        from scipy.ndimage import median_filter
        slope_pm = median_filter(slope_pm, size=smooth, mode="nearest")
    slope_deg = np.degrees(np.arctan(slope_pm))
    slope_deg = np.where(np.isfinite(dtm), slope_deg, np.nan)
    return slope_deg


def tune_slope_threshold(slope_deg: np.ndarray, pred_full: np.ndarray,
                         truth_r: np.ndarray, cal_mask: np.ndarray,
                         rungs_deg: tuple = (3.0, 5.0, 8.0, 10.0, 15.0,
                                            20.0, 30.0, 45.0),
                         ) -> tuple:
    """Pick the slope-threshold maximising F1 on the calibration half.

    `slope_deg` is the per-cell slope in degrees (from `slope_deg_map()`).
    `pred_full` is the post-component-filter boolean prediction mask
    on the FULL surface (test_mask was used to partition elsewhere).
    `truth_r` is the boolean ground-truth on the full surface.
    `cal_mask` is the boolean calibration-half mask (same shape).

    We sweep `min_slope_deg` over `rungs_deg` and pick the slope that
    gives the best F1 on `pred_full & cal_mask` vs `truth_r & cal_mask`.

    Returns (best_slope_deg, best_f1_cal).
    """
    if (pred_full & cal_mask).sum() == 0 or (truth_r & cal_mask).sum() == 0:
        return 0.0, 0.0
    if not np.any(np.isfinite(slope_deg)):
        return 0.0, 0.0
    best = (0.0, 0.0)
    for deg in rungs_deg:
        slope_ok = (slope_deg >= deg) & np.isfinite(slope_deg)
        # use the calibration half only (test half is hidden per v5 I9)
        pred_cal = pred_full & slope_ok & cal_mask
        truth_cal = truth_r & cal_mask
        m = _f1_from_pred(pred_cal, truth_cal)
        if m["f1"] > best[1]:
            best = (float(deg), m["f1"])
    return best


def tune_threshold(scores_cal: np.ndarray, truth_cal: np.ndarray, n_grid: int = 51):
    """Pick the threshold maximising F1 on the calibration half."""
    if not np.isfinite(scores_cal).any() or truth_cal.sum() == 0:
        return 0.0, 0.0
    qs = np.linspace(0.0, 1.0, n_grid)
    grid = np.quantile(scores_cal[np.isfinite(scores_cal)], qs)
    grid = np.unique(grid)
    best = (0.0, 0.0)
    for t in grid:
        m = f1_at_threshold(scores_cal, truth_cal, float(t))
        if m["f1"] > best[1]:
            best = (float(t), m["f1"])
    return best


def build_arg_parser() -> argparse.ArgumentParser:
    """The sag_detect CLI parser (C3: extracted from main() so the
    default surface (--cc-filter off) is unit-testable)."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--rungs", type=float, nargs="+", default=[0.5, 2, 5])
    ap.add_argument("--grid-spacing", type=float, default=0.5)
    ap.add_argument("--frangi-sigmas", type=float, nargs="+",
                    default=[30, 60, 100, 150, 200, 300])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--min-component", type=int, default=5,
                    help="Minimum connected-component size (8-connectivity) in cells; "
                    "components below this are removed before F1 is computed. "
                    "Default 5; set to 1 to disable. Used verbatim when "
                    "--cc-filter off (v0.5 parity) and as the fallback area "
                    "when --cc-filter on is set without --cc-area-min.")
    ap.add_argument("--cc-filter", choices=["off", "on", "auto"], default="off",
                    help="C3 connected-component filter mode. 'off' (default): "
                    "legacy inline scalar --min-component path (v0.5 parity, "
                    "frozen Paper 1/2 evidence). 'on': standalone "
                    "connected_component_filter engine with a uniform "
                    "--cc-area-min. 'auto': the per-rung AREA_MIN table "
                    "(V0.2_PLAN.md sec 4.1; 0.5m->50, 1m->20, 2m->8, 5m->3, "
                    "8/10m->2 cells).")
    ap.add_argument("--cc-area-min", type=int, default=None,
                    help="Uniform minimum component area (cells) for "
                    "--cc-filter on. Ignored in auto (table) and off "
                    "(legacy --min-component) modes.")
    ap.add_argument("--slope-mask-degrees", type=float, default=10.0,
                    help="Mask out predictions on slopes steeper than this many "
                    "degrees (gentle slopes cannot host roof-sag dimples that "
                    "show up in 2-5 m amplitude depression-depth rasters). "
                    "Default 10; set to 0 to disable. With --tune-slope, the "
                    "value here is the *starting point* and the calibration "
                    "half will pick a better value per rung.")
    ap.add_argument("--tune-slope", action="store_true",
                    help="Tune the slope-threshold on the calibration half and "
                    "report the F1-maximising slope per rung. Default off (use the "
                    "fixed --slope-mask-degrees value). Lift on hardest sites: "
                    "typically +5-15 percent on F1.")
    return ap


def main():
    args = build_arg_parser().parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    data = np.load(args.npz)
    x, y, z = data["x"], data["y"], data["z"]
    print(f"[load] {len(x):,} points from {args.npz.name}", flush=True)

    # ground truth from cloud: cells with a void below
    gt, gt_geo = cloud_ground_truth(x, y, z, args.grid_spacing, threshold_depth=1.0)
    x_min, y_min, nx, ny, px = gt_geo
    transform = Affine(px, 0.0, x_min, 0.0, px, y_min)
    n_void_cells = int(gt.sum())
    print(f"[gt  ] {ny}x{nx} at {px} m, void cells = {n_void_cells} "
          f"({n_void_cells/gt.size:.1%})", flush=True)

    # sink-fill the source cloud at the master res
    # First bin to master grid (median per cell) to make the master DTM,
    # then use the ladder's rungs if --rungs differs.
    # For speed, we only generate rungs <= master; finer rungs are
    # handled by Task 13 (degrade.py) operating on the .npz directly.
    rungs = sorted(set(args.rungs))
    print(f"[rung] running on {rungs} m", flush=True)

    # re-bin cloud to each rung
    def cloud_to_rung(target_res: float):
        # use nanmax/nanmin so NaN sentinel values don't break the bin
        x_finite = x[np.isfinite(x)]
        y_finite = y[np.isfinite(y)]
        x_min, x_max = float(np.nanmin(x_finite)), float(np.nanmax(x_finite))
        y_min, y_max = float(np.nanmin(y_finite)), float(np.nanmax(y_finite))
        nxr = max(1, int(np.ceil((x_max - x_min) / target_res)))
        nyr = max(1, int(np.ceil((y_max - y_min) / target_res)))
        col = np.clip(((x - x_min) / target_res).astype(int), 0, nxr - 1)
        row = np.clip(((y - y_min) / target_res).astype(int), 0, nyr - 1)
        flat = row * nxr + col
        # weight by z finite so sentinel values don't pollute the bin
        z_w = np.where(np.isfinite(z), z, 0.0)
        cnt_w = np.where(np.isfinite(z), 1.0, 0.0)
        Z = np.full(nyr * nxr, np.nan)
        n = np.zeros(nyr * nxr, dtype=np.float64)
        sums = np.zeros(nyr * nxr, dtype=np.float64)
        np.add.at(sums, flat, z_w)
        np.add.at(n, flat, cnt_w)
        ok = n > 0
        Z[ok] = sums[ok] / n[ok]
        Zr = Z.reshape(nyr, nxr)
        tr = Affine(target_res, 0.0, x_min, 0.0, target_res, y_min)
        return Zr, tr, (x_min, y_min, nxr, nyr, target_res)

    wbt = WhiteboxTools()
    rung_rows = []
    for r in rungs:
        print(f"\n--- rung {r} m ---", flush=True)
        Zr, trr, geor = cloud_to_rung(r)
        nxr, nyr = Zr.shape[1], Zr.shape[0]
        valid_r = np.isfinite(Zr)
        if valid_r.sum() < 100:
            print(f"[skip] rung {r} m has <100 valid cells", flush=True)
            continue
        # write DTM
        dtm_tif = args.outdir / f"dtm_{r:g}m.tif"
        write_geotiff(Zr, trr, dtm_tif, nodata=-9999.0)
        # sink-fill
        fill_tif = args.outdir / f"filled_{r:g}m.tif"
        sink_fill_planchon(wbt, dtm_tif, fill_tif)
        with rasterio.open(fill_tif) as fs, rasterio.open(dtm_tif) as ds:
            fill = fs.read(1).astype(np.float32)
            dtm = ds.read(1).astype(np.float32)
            fill_nodata = fs.nodata
        fill_v = np.where(fill == fill_nodata, np.nan, fill)
        dtm_v = np.where(dtm == -9999.0, np.nan, dtm)
        depth = np.maximum(fill_v - dtm_v, 0.0)
        # Frangi vesselness
        V = frangi_vesselness(dtm_v, r, sigmas=tuple(args.frangi_sigmas))
        # per-cell void above (re-grid GT if needed)
        if (nxr, nyr) != (nx, ny):
            from scipy.ndimage import zoom
            truth_r = zoom(gt.astype(np.float32),
                           (nyr / ny, nxr / nx), order=0).astype(bool)
        else:
            truth_r = gt
        # score = depth * vesselness
        score = (np.where(np.isfinite(depth), depth, 0.0) *
                 np.where(np.isfinite(V), V, 0.0)).astype(np.float32)
        # 50/50 split (alternating cells, seed 42)
        rng = np.random.default_rng(args.seed)
        cal_mask = np.zeros_like(score, dtype=bool)
        ev = np.argwhere(np.isfinite(score))
        if len(ev) == 0:
            continue
        perm = rng.permutation(len(ev))
        n_cal = len(ev) // 2
        cal_idx = ev[perm[:n_cal]]
        cal_mask[cal_idx[:, 0], cal_idx[:, 1]] = True
        test_mask = np.isfinite(score) & ~cal_mask
        # tune on calibration (BEFORE component filter; tune is over
        # raw score threshold per v5 I9 protocol)
        thr, f1_cal = tune_threshold(score[cal_mask], truth_r[cal_mask])
        # apply connected-component post-processing on the FULL score
        # surface, then partition into cal/test (otherwise cal/test
        # are not i.i.d. samples of the same post-processing).
        # C3: mode dispatch (off = legacy scalar for v0.5 parity;
        # on/auto = standalone engine, per-rung AREA_MIN table in auto).
        pred_full, cc_audit = apply_cc_filter(
            score, thr, args.cc_filter, args.min_component,
            args.cc_area_min, r)
        # slope-aware mask: predictions on too-gentle slopes cannot
        # host roof-sag dimples that show up in 2-5 m amplitude
        # depression-depth rasters. v0.3 precision lift.
        slope_deg = slope_deg_map(dtm, r)
        if args.tune_slope:
            # pick the F1-maximising slope on the calibration half
            # (v0.4 same-discipline pattern as the v0.2 component
            # filter tuning). Pass full surfaces; the helper does
            # the cal-mask partition.
            best_deg, best_f1_cal = tune_slope_threshold(
                slope_deg, pred_full, truth_r, cal_mask)
        else:
            best_deg = args.slope_mask_degrees
        slope_ok = slope_deg >= best_deg if np.any(np.isfinite(slope_deg)) else np.zeros_like(dtm, dtype=bool)
        pred_full_slope = pred_full & slope_ok
        # partition cal/test as boolean index on the 2D surface
        pred_cal_2d = pred_full & cal_mask
        pred_test_2d = pred_full & test_mask
        pred_test_slope = pred_full_slope & test_mask
        m_cal = f1_at_threshold(score[cal_mask], truth_r[cal_mask], thr)
        # raw F1 (no post-processing) for the comparison print
        m_tst_raw = f1_at_threshold(score[test_mask], truth_r[test_mask], thr)
        # post-component-filter F1: feed the same 1D masks both arrays
        # come from to avoid the dimension-mismatch bug
        m_tst_pred = _f1_from_pred(pred_test_2d[test_mask],
                                   truth_r[test_mask])
        # post-cc-and-slope-mask F1 (v0.3 headline number)
        m_tst_slope = _f1_from_pred(pred_test_slope[test_mask],
                                    truth_r[test_mask])
        # FP per 10^4 km^2 (v5 mandatory reporting): cell area in km^2,
        # evaluated on the COMPONENT-FILTERED predictions (the honest metric)
        cell_area_km2 = (r * r) / 1e6
        n_cells_test = int(test_mask.sum())
        fp_per_1e4km2 = m_tst_pred["fp"] * 1e4 / (n_cells_test * cell_area_km2) if n_cells_test else float("nan")
        # stratified detectability: bucket truth cells by their score on test
        bins = np.array([0.0, 0.25, 0.5, 0.75, 1.0])  # normalised score quartile bins
        norm_score = score / (np.nanpercentile(score, 99) + 1e-9)
        strat = []
        for lo, hi in zip(bins[:-1], bins[1:]):
            band = (norm_score >= lo) & (norm_score < hi) & test_mask
            tp = int((band & truth_r).sum())
            tot = int(truth_r[band].sum() if band.any() else 0)
            strat.append({"score_lo": float(lo), "score_hi": float(hi),
                          "n_truth_in_band": tot,
                          "n_detected_in_band": tp,
                          "detection_rate": (tp / tot) if tot else 0.0})
        print(f"[cal ] thr={thr:.3g}, F1={f1_cal:.3f}, P={m_cal['precision']:.3f}, R={m_cal['recall']:.3f}")
        print(f"[test] thr={thr:.3g}, F1(>thr)={m_tst_pred['f1']:.3f}, "
              f"P={m_tst_pred['precision']:.3f}, R={m_tst_pred['recall']:.3f}, "
              f"FP/10^4 km^2={fp_per_1e4km2:.2f} "
              f"(raw F1={m_tst_raw['f1']:.3f}, +slope F1={m_tst_slope['f1']:.3f})")
        rung_rows.append({
            "res_m": r, "shape": [nyr, nxr], "valid_frac": float(valid_r.sum() / Zr.size),
            "threshold": thr, "f1_cal": m_cal["f1"],
            "f1_test": m_tst_pred["f1"], "f1_test_raw": m_tst_raw["f1"],
            "f1_test_slope": m_tst_slope["f1"],
            "precision_test": m_tst_pred["precision"], "recall_test": m_tst_pred["recall"],
            "fp_per_1e4km2_test": fp_per_1e4km2,
            "n_void_cells": int(truth_r.sum()),
            "n_detected_test": m_tst_pred["tp"],
            "min_component": args.min_component,
            "precision_test_slope": m_tst_slope["precision"],
            "recall_test_slope": m_tst_slope["recall"],
            **cc_audit,
            "slope_mask_degrees": float(best_deg),
            "slope_mask_tuned": bool(args.tune_slope),
            "n_slope_masked_test": int(((pred_full & ~slope_ok) & test_mask).sum()),
            "stratified": strat,
        })
        # save rasters
        for name, arr_save in [("depth", depth), ("frangi", V), ("score", score)]:
            write_geotiff(arr_save, trr, args.outdir / f"{name}_{r:g}m.tif", nodata=-9999.0)
        # save the post-component-filter prediction mask as well, so
        # the geometric post-processing is verifiable
        write_geotiff(pred_full.astype(np.float32), trr,
                      args.outdir / f"pred_{r:g}m.tif", nodata=-9999.0)
        # save the slope mask as well (for v0.3 audit)
        if args.slope_mask_degrees > 0:
            write_geotiff(slope_ok.astype(np.float32), trr,
                          args.outdir / f"slope_ok_{r:g}m.tif", nodata=-9999.0)
        # figure: 4 panels (DTMs hs + depth + frangi + score)
        fig, ax = plt.subplots(1, 4, figsize=(20, 5))
        # hillshade
        dz = np.gradient(np.where(np.isfinite(dtm_v), dtm_v, np.nanmean(dtm_v)), r)
        slope = np.pi / 2.0 - np.arctan(np.hypot(dz[1], dz[0]))
        aspect = np.arctan2(-dz[1], dz[0])
        az, al = np.radians(315.0), np.radians(45.0)
        hs = np.clip(255.0 * (np.sin(al) * np.sin(slope) +
                               np.cos(al) * np.cos(slope) * np.cos(az - aspect)), 0, 255)
        ax[0].imshow(hs, cmap="gray", origin="lower"); ax[0].set_title(f"hillshade {r} m")
        ax[1].imshow(np.where(np.isfinite(depth), depth, np.nan), cmap="magma",
                     origin="lower"); ax[1].set_title("depression depth")
        ax[2].imshow(np.where(np.isfinite(V), V, np.nan), cmap="cividis",
                     origin="lower"); ax[2].set_title("Frangi 60-300 m")
        ax[3].imshow(np.where(np.isfinite(score), score, np.nan), cmap="inferno",
                     origin="lower"); ax[3].set_title(f"score (thr={thr:.3g}, F1={m_tst_pred['f1']:.2f})")
        for a in ax: a.set_xticks([]); a.set_yticks([])
        fig.suptitle(f"LLTB-1 sag detection @ {r} m — {args.npz.name}")
        fig.tight_layout()
        fig_path = args.outdir / f"sag_panels_{r:g}m.png"
        fig.savefig(fig_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(f"[out ] figure -> {fig_path}", flush=True)

    # detectability curve
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    res = [r["res_m"] for r in rung_rows]
    f1 = [r["f1_test"] for r in rung_rows]
    fp = [r["fp_per_1e4km2_test"] for r in rung_rows]
    ax[0].plot(res, f1, "o-", color="#1f78b4", lw=2, ms=8)
    ax[0].set_xscale("log"); ax[0].set_xlabel("GSD (m)"); ax[0].set_ylabel("F1 (test split)")
    ax[0].set_title("Detectability curve (LLTB-1 v0.1)")
    ax[0].grid(True, which="both", alpha=0.3)
    ax[1].plot(res, fp, "s-", color="#c0392b", lw=2, ms=8)
    ax[1].set_xscale("log"); ax[1].set_yscale("log")
    ax[1].set_xlabel("GSD (m)"); ax[1].set_ylabel("FP per $10^4$ km$^2$")
    ax[1].set_title("False-positive rate (v5 mandatory reporting)")
    ax[1].grid(True, which="both", alpha=0.3)
    fig.suptitle(f"LLTB-1 detectability — {args.npz.name}")
    fig.tight_layout()
    curve_path = args.outdir / "detectability_curve.png"
    fig.savefig(curve_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"\n[out ] detectability curve -> {curve_path}", flush=True)

    summary_path = args.outdir / "sag_summary.json"
    with open(summary_path, "w") as f:
        json.dump({
            "source": str(args.npz), "n_points": int(len(x)),
            "gt_void_cells_master": n_void_cells, "rungs": rung_rows,
            "cc_filter": args.cc_filter,
            "cc_area_min_uniform": (args.cc_area_min if args.cc_filter == "on"
                                    else None),
            "area_min_per_rung_table": ({str(k): v for k, v in
                                         sorted(AREA_MIN_PER_RUNG.items())}
                                        if args.cc_filter == "auto" else None),
            "figure_curve": str(curve_path),
        }, f, indent=2)
    print(f"[out ] summary -> {summary_path}", flush=True)
    print(json.dumps({"rungs": rung_rows}, indent=2))


if __name__ == "__main__":
    main()
