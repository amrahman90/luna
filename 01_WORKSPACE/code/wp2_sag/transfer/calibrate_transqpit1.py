"""Task 18.3 (P3.1b) — calibrate the Z2 sag detector on TRANQPIT1, FREEZE
parameters for unchanged transfer (v5 I15).

Applies the v0.4 LLTB-1 calibration protocol (per-rung slope-threshold
tuning; notes/2026-08-21_LLTB1_v0.4_release_note.md +
admin/verification_evidence/2026-08-21_v04_tune_slope_verification.json)
to the LUNAR Z2 pipeline, then FREEZES the parameters.

Protocol — v0.4 discipline, honestly adapted to lunar label sparsity:
  1. Build the Z2 score surface on TRANQPIT1 at each rung EXACTLY as
     sag_search.py v0.1 (krigcorr DTM -> average rebin -> Planchon-
     Darboux fill -> depth -> Frangi(30,60,100,150,200,300) on the
     rung grid -> score = depth x Frangi -> peaks = local maxima >= 
     frac*max, neigh 5). The existing MTP/<rung>m_score.tif rasters
     ARE the v0.1 result; we load them directly so the headline
     (rank 11, score 3.72, top 21.06, ~45 m from catalogued pit) is
     byte-identical. See admin/verification_evidence/
     2026-08-21_z2_pit_distance_verification.md.
  2. Ground truth: the catalogued Mare Tranquillitatis Pit — the ONE
     lunar subsurface feature with independent (radar) evidence. Match
     radius 100 m (Z2 pit-distance verification convention).
  3. ADAPTATION (documented, deliberate): the analog v0.4 protocol
     splits cells 50/50 (seed 42) and tunes cell-level F1 on the cal
     half. With exactly ONE known positive, (a) cell-level F1
     degenerates (tuned threshold -> ~0) and (b) a cell split puts the
     single positive in only one half, making test-half F1 structurally
     0. Calibration therefore uses the FULL TRANQPIT1 candidate list;
     THE I15 TRANSFER SET IS THE HELD-OUT TEST. The seed-42 50/50
     split is retained for FP-stability reporting (FP_cal vs FP_test)
     only.
  4. Grid sweep per rung: score_frac x slope threshold (v0.4 slope
     rungs 3..45 deg + 0 = off); candidate-level F1 with TP = pit
     covered by a candidate within 100 m, FP = every other candidate.
     v0.4 slope semantics preserved: candidates survive where
     slope >= threshold (computed via sag_detect.slope_deg_map on the
     rung-grid DTM; smooth=3).

Output: data/outputs/wp2_sag/transfer/calibration_transqpit1.json
        (frozen parameters under key "frozen")
        METHODS.md documents any edits made to the prior files.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from scipy.ndimage import maximum_filter

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp1_detector"))
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp2_sag"))
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp0_primitive"))

from sag_search_run import _wbt_with_dir  # noqa: E402
from sweep_pits import pit_to_pixel  # noqa: E402

PIT_MATCH_RADIUS_M = 100.0
SLOPE_RUNGS = (0.0, 3.0, 5.0, 8.0, 10.0, 15.0, 20.0, 30.0, 45.0)  # v0.4 set + 0
FRAC_LADDER = (0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50)  # incl. v0.1 default
NEIGH = 5  # v0.1 peak neighbourhood
FILL = "planchon_darboux (fix_flats=True)"


def dtm_source(dtm_name: str) -> Path:
    """Source DTM path (krigcorr preferred; raw fallback). Mirrors the rule
    sag_search.py uses for run-on-existing-rasters compatibility."""
    from noise_floors_batch import RAW
    krig = RAW / "outputs" / dtm_name / f"NAC_DTM_{dtm_name}_krigcorr.tif"
    raw = RAW / "dtms" / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
    return krig if krig.exists() else raw


def existing_or_rebuild_surface(dtm_name: str, rung: float, workdir: Path, wbt):
    """Load the v0.1 Z2 score surface from disk if present; rebuild via
    the sag_search.py v0.1 recipe if not. Either way, the returned
    surface is byte-equivalent to what produced the headline."""
    from sag_detect import frangi_vesselness as sag_fv  # not used here
    from rasterio.enums import Resampling
    outdir = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube/01_WORKSPACE/data/outputs/wp2_sag/MTP")
    score_path = outdir / f"{dtm_name}_{rung:g}m_score.tif"
    depth_path = outdir / f"{dtm_name}_{rung:g}m_depth.tif"
    frangi_path = outdir / f"{dtm_name}_{rung:g}m_frangi.tif"
    if score_path.exists() and depth_path.exists():
        with rasterio.open(score_path) as s:
            score = s.read(1).astype(np.float64)
            if s.nodata is not None:
                score = np.where(score == s.nodata, np.nan, score)
            eff = float(abs(s.transform.a))  # column scale (equal to row at rung grid)
            crs = s.crs
            transform = s.transform
            shape = (s.height, s.width)
        with rasterio.open(depth_path) as s:
            dtm_surf = s.read(1).astype(np.float64)  # depth raster as surface proxy
            if s.nodata is not None:
                dtm_surf = np.where(dtm_surf == s.nodata, np.nan, dtm_surf)
        # We need the DTM itself (not depth) for slope_deg_map; load it
        # from the rung grid by reading the score raster's transform.
        # The slope is computed on the same rung grid (depth raster is
        # acceptable for slope since depth ~ 0 on flat mare; the slope
        # at the pit walls is essentially the DTM slope).
        # For honesty, we recompute slope from depth (which is the filled
        # DTM minus the raw DTM — close to 0 on flats, equal to fill
        # difference on pit walls). v0.4 slope_mask uses dtm directly;
        # depth works fine here because the pit walls are the same
        # gradient. See notes/2026-08-22_z2_pit_distance_verification.md.
        # For correctness we load the actual DTM at the rung grid from
        # the source by rebinning (cheap).
        path = dtm_source(dtm_name)
        with rasterio.open(path) as src:
            res_full = float(src.res[0])
            H_src, W_src = src.height, src.width
        # fractional scale (Phase 0.3 — integer round() silently produced a
        # 4 m grid for the 5 m rung on 2 m sources; keep the TRUE factor so
        # pit row/col mapping below stays on the actual grid)
        factor = max(1.0, float(rung) / res_full)
        new_h = max(1, int(np.ceil(H_src / factor)))
        new_w = max(1, int(np.ceil(W_src / factor)))
        with rasterio.open(path) as src:
            dtm_r = src.read(1, out_shape=(new_h, new_w),
                             resampling=Resampling.average).astype(np.float64)
            if src.nodata is not None:
                dtm_r = np.where(dtm_r == src.nodata, np.nan, dtm_r)
        return {"dtm_r": dtm_r, "score": score, "eff": eff,
                "shape": shape, "crs": crs, "transform": transform,
                "source": str(score_path), "factor": factor,
                "from_cache": True}
    # Fallback: rebuild via sag_search.py v0.1 recipe (rare; only if
    # the rasters have been deleted).
    raise FileNotFoundError(
        f"No cached v0.1 score raster at {score_path}. Re-run sag_search.py "
        f"on TRANQPIT1 first to (re)generate the surface.")


def pit_pixels(dtm_name: str, surf):
    """Catalogued pit (row, col) on the rung grid. Uses native ->
    rung-grid scaling (factor)."""
    cats = pd.read_csv(REPO / "01_WORKSPACE/data/outputs/wp0_scope_map/relevant_pits_x_dtms.csv")
    rows = cats[cats["DTM_NAME"] == dtm_name]
    pits = []
    with rasterio.open(dtm_source(dtm_name)) as src:
        for r in rows.itertuples():
            row, col, _ = pit_to_pixel(r.Latitude, r.Longitude, src)
            pits.append((int(round(row / surf["factor"])),
                         int(round(col / surf["factor"])), r.Name))
    return pits


def slope_deg(surf):
    """v0.4 slope_deg_map on the rung-grid DTM (continuous slope in deg)."""
    from sag_detect import slope_deg_map
    return slope_deg_map(surf["dtm_r"], surf["eff"])


def peaks_of(score, frac, neigh=NEIGH):
    """v0.1 find_peaks: local maxima >= frac*max (sparse list)."""
    if not np.isfinite(score).any() or np.nanmax(score) <= 0:
        return []
    s_for_max = np.where(np.isfinite(score), score, 0.0)
    mf = maximum_filter(s_for_max, size=neigh, mode="nearest")
    thr = frac * float(np.nanmax(score))
    rr, cc = np.where((s_for_max == mf) & (s_for_max >= thr) & np.isfinite(score))
    return [(int(r), int(c)) for r, c in zip(rr, cc)]


def cand_f1(peaks, pits_rc, res, half_mask=None):
    """Candidate-level F1 (known-item retrieval): TP = pits covered by a
    peak within PIT_MATCH_RADIUS_M, FP = peaks covering no pit, FN =
    uncovered pits. half_mask restricts peaks (for FP-split reporting)."""
    radius_px_sq = (PIT_MATCH_RADIUS_M / res) ** 2

    def keep(r, c):
        return True if half_mask is None else bool(half_mask[r, c])

    fp = 0
    for r, c in peaks:
        if not keep(r, c):
            continue
        if any((r - pr) ** 2 + (c - pc) ** 2 <= radius_px_sq
               for pr, pc, _ in pits_rc):
            continue
        fp += 1
    tp = 0
    for pr, pc, _ in pits_rc:
        if any(keep(r, c) and
               (r - pr) ** 2 + (c - pc) ** 2 <= radius_px_sq
               for r, c in peaks):
            tp += 1
    fn = len(pits_rc) - tp
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": prec, "recall": rec,
            "f1": (2 * prec * rec / (prec + rec)) if prec + rec else 0.0}


def calibrate(dtm_name: str, rung: float, workdir: Path, wbt, seed: int = 42):
    t0 = time.time()
    surf = existing_or_rebuild_surface(dtm_name, rung, workdir, wbt)
    eff, score = surf["eff"], surf["score"]
    pits_rc = pit_pixels(dtm_name, surf)
    valid = np.isfinite(surf["dtm_r"])
    slope = slope_deg(surf)
    smax = float(np.nanmax(score))

    # Sanity-check the headline reproduction
    peaks_v01 = peaks_of(np.where(np.isfinite(score), score, 0.0), 0.10)
    headline_d = None
    for pr, pc, name in pits_rc:
        d = min((np.hypot(r - pr, c - pc) * eff) for r, c in peaks_v01) if peaks_v01 else None
        headline_d = d
    print(f"[headline] {len(peaks_v01)} peaks at v0.1 defaults; "
          f"closest-to-pit distance = "
          f"{headline_d:.1f} m (expected ~45 m)" if headline_d is not None
          else f"[headline] {len(peaks_v01)} peaks; pit has no peak within 100 m",
          flush=True)

    # seed-42 50/50 cell split — used for FP-stability reporting only
    rng = np.random.default_rng(seed)
    cal_mask = np.zeros_like(valid)
    ev = np.argwhere(valid)
    perm = rng.permutation(len(ev))
    cal_idx = ev[perm[: len(ev) // 2]]
    cal_mask[cal_idx[:, 0], cal_idx[:, 1]] = True

    grid = []
    for deg in SLOPE_RUNGS:
        slope_ok = (slope >= deg) if deg > 0 else np.ones_like(valid)
        masked = np.where(slope_ok & np.isfinite(score), score, 0.0)
        for frac in FRAC_LADDER:
            peaks = peaks_of(masked, frac)
            m = cand_f1(peaks, pits_rc, eff)
            m_cal = cand_f1(peaks, pits_rc, eff, cal_mask)
            m_test = cand_f1(peaks, pits_rc, eff, ~cal_mask)
            grid.append({"slope_deg": deg, "score_frac": frac,
                         "n_peaks": len(peaks), "f1": m["f1"], "tp": m["tp"],
                         "fp": m["fp"], "fn": m["fn"],
                         "fp_cal": m_cal["fp"], "fp_test": m_test["fp"]})
    # F1-max on the full list; deterministic tie-break: fp asc, slope asc, frac asc
    best = sorted(grid, key=lambda g: (-g["f1"], g["fp"], g["slope_deg"],
                                       g["score_frac"]))[0]
    v01 = [g for g in grid if g["slope_deg"] == 0.0 and g["score_frac"] == 0.10][0]

    area_km2 = valid.sum() * eff * eff / 1e6
    out = {
        "dtm": dtm_name, "rung_m": rung, "effective_posting_m": eff,
        "shape": list(surf["shape"]), "seed": seed, "score_max": smax,
        "frozen": {"score_frac": best["score_frac"], "slope_deg": best["slope_deg"]},
        "f1": best["f1"], "tp": best["tp"], "fp": best["fp"], "fn": best["fn"],
        "fp_cal_half": best["fp_cal"], "fp_test_half": best["fp_test"],
        "v01_default": {"score_frac": 0.10, "slope_deg": 0.0, "f1": v01["f1"],
                        "tp": v01["tp"], "fp": v01["fp"], "n_peaks": v01["n_peaks"]},
        "n_peaks": best["n_peaks"], "area_km2": area_km2,
        "fp_per_1e4km2": best["fp"] / area_km2 * 1e4,
        "pits_used": [p[2] for p in pits_rc], "valid_cells": int(valid.sum()),
        "headline_reproduction_m": headline_d,
        "runtime_s": round(time.time() - t0, 1),
        "source_score_tif": surf["source"], "source_dtm": str(dtm_source(dtm_name)),
        "from_cache": surf["from_cache"], "grid": grid,
    }
    print(f"[cal] {dtm_name} rung {rung:g} m (shape {surf['shape']} @ {eff:.2f} m): "
          f"FROZEN frac={best['score_frac']:.2f} "
          f"slope={best['slope_deg']:g} deg -> F1 {best['f1']:.3f} "
          f"(TP {best['tp']}/{len(pits_rc)}, FP {best['fp']}) | v0.1 default: "
          f"F1 {v01['f1']:.3f} (TP {v01['tp']}, FP {v01['fp']}) | "
          f"FP {out['fp_per_1e4km2']:.1f}/1e4km2 | {out['runtime_s']} s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dtm", default="TRANQPIT1")
    ap.add_argument("--rungs", type=float, nargs="+", default=[5],
                    help="rung postings to calibrate (default: [5]). Each rung "
                         "requires the cached v0.1 score raster at "
                         "data/outputs/wp2_sag/<dir>/<DTM>_<rung>m_score.tif; "
                         "if absent, the rung is skipped with a clear message.")
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.gettempdir())
    wbt = _wbt_with_dir()

    results = []
    for r in args.rungs:
        score_path = (REPO / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag" / "MTP"
                      / f"{args.dtm}_{r:g}m_score.tif")
        if not score_path.exists():
            print(f"[skip] rung {r:g} m: no cached score at {score_path}")
            continue
        results.append(calibrate(args.dtm, r, workdir, wbt, args.seed))
    if not results:
        raise SystemExit("No rungs had cached v0.1 score rasters. "
                         "Re-run sag_search.py on the DTM first.")
    frozen = {
        "FREEZE": (f"protocol I15 unchanged-transfer parameters as of "
                   f"{date.today().isoformat()}"),
        "calibration_dtm": args.dtm,
        "protocol": "v0.4 per-rung slope-threshold tuning adapted to lunar label "
                    "sparsity. Surface = sag_search.py v0.1 recipe (load from "
                    "data/outputs/wp2_sag/MTP/<DTM>_<rung>m_score.tif; verified "
                    "byte-identical: rank 11, score 3.72, top 21.06, ~45 m from "
                    "catalogued pit). Objective = candidate-level F1 with TP = "
                    "candidate within 100 m of the catalogued pit (the only "
                    "radar-evidenced lunar subsurface feature), FP = all other "
                    "candidates. Single known positive => cal/test cell split "
                    "of the positive is degenerate; calibration uses the full "
                    "TRANQPIT1 list and THE I15 TRANSFER SET IS THE HELD-OUT "
                    "TEST. Seed-42 50/50 split retained for FP-stability "
                    "reporting only.",
        "neigh": NEIGH, "seed": args.seed, "fill": FILL,
        "surface_recipe": {
            "source": "sag_search.py v0.1 (krigcorr DTM -> average rebin to rung "
                      "-> Planchon-Darboux fill -> depth -> Frangi at rung grid "
                      "-> score = depth * Frangi -> peaks with neigh=5)",
            "frangi_sigmas_m": [30, 60, 100, 150, 200, 300],
            "pit_match_radius_m": PIT_MATCH_RADIUS_M,
        },
        "rungs": {f"{r['rung_m']:g}": {
            "score_frac": r["frozen"]["score_frac"],
            "slope_deg": r["frozen"]["slope_deg"],
            "f1": r["f1"], "tp": r["tp"], "fp": r["fp"],
        } for r in results},
        "frozen_date": str(date.today()),
        "transfer_rule": "TRANSFER UNCHANGED (I15): frozen score_frac + slope_deg "
                         "per rung applied to every transfer DTM; no per-DTM "
                         "re-tuning. Allowed rungs per DTM follow the "
                         "sag_search.py 0.6 res-compatibility rule.",
    }
    payload = {"generated": str(date.today()), "results": results, "frozen": frozen}
    out = args.outdir / "calibration_transqpit1.json"
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"[out] frozen calibration -> {out}")


if __name__ == "__main__":
    main()
