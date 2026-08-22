"""Per-DTM sag-band noise floors at Z2 scale (Task 18.3, req: G0' deferral row).

Extends the Task-6 zero-change noise-floor method (wp0_kriging/noise_floor.py)
to EVERY DTM in the Task-18.3 transfer set, computed at the Z2 working
posting (the rung posting the sag search actually runs at), so that each
DTM gets its own local detectability threshold

    A_min = 3 x pooled sag-band RMS      (project convention, labelled as such)

Method (reuses Task-6 functions verbatim — no reimplementation):
  1. Load DTM (krigcorr if present else raw, same rule as sag_search_run).
  2. Rebin to the primary Z2 rung posting (average resampling, same as
     sag_search_run.run_one_dtm) — the floor must match the scale the
     detector competes at.
  3. Panel selection per Task 6 (>=3 flat-mare panels, >=1 km^2, 95% valid,
     excluding catalogued pits / LU5M812TGT craters / Hurwitz rilles) via
     noise_floor.select_panels + build_exclusion.
  4. Per panel: DoG(60-300 m) sag-band RMS (noise_floor.sag_band_dog);
     pooled RMS per DTM; 3-sigma = A_min.
  5. Fallback for highland/rough DTMs where <3 flat panels pass: pooled
     RMS over the whole margin-cropped footprint with exclusions masked
     (method column says so — honest).

Outputs (repo, small files only):
  data/outputs/wp2_sag/transfer/noise_floors.csv        (summary per DTM)
  data/outputs/wp2_sag/transfer/noise_floors_panels.csv (per-panel detail)
  data/outputs/wp2_sag/transfer/noise_floors.json       (machine copy)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from scipy.ndimage import zoom

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp0_kriging"))
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp0_primitive"))

from noise_floor import build_exclusion, sag_band_dog, select_panels, slope_map  # noqa: E402

RAW = Path.home() / "lunarvoid" / "data"
CATALOG = REPO / "01_WORKSPACE/data/outputs/wp0_scope_map/relevant_pits_x_dtms.csv"
CRATER_CSV = RAW / "index_layers" / "craters_lu5m812tgt" / "craters_0p4_5km_pm60.csv.gz"
RILLE_SHP = RAW / "index_layers" / "hurwitz_rilles" / "shapefile" / "SinuousRilles_obs.shp"


class _Args:
    """Attribute bag matching noise_floor.select_panels/build_exclusion
    expectations (defaults = Task-6 release values)."""

    excl_cell = 100.0
    pit_buffer = 3000.0
    crater_buffer = 250.0
    rille_buffer = 1000.0
    slope_max = 2.0
    flat_frac = 0.98
    boxcar_px = 50
    nodata_max_frac = 0.05
    panel_sizes = [2000, 1500, 1200, 1000]
    min_km2 = 1.0
    cand_step = 250.0
    hp_window = 300.0


def load_rung(dtm_name: str, rung: float):
    """DTM at the Z2 rung posting (same rebin rule as sag_search_run)."""
    krig = RAW / "outputs" / dtm_name / f"NAC_DTM_{dtm_name}_krigcorr.tif"
    raw = RAW / "dtms" / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
    path = krig if krig.exists() else raw
    with rasterio.open(path) as src:
        res_full = float(src.res[0])
        factor = max(1, int(round(rung / res_full)))
        if factor == 1:
            z = src.read(1).astype(np.float64)
            transform = src.transform
        else:
            z = src.read(1, out_shape=(src.height // factor, src.width // factor),
                         resampling=Resampling.average).astype(np.float64)
            transform = src.transform * src.transform.scale(factor, factor)
        bounds, crs, nodata = src.bounds, src.crs, src.nodata
    if nodata is not None:
        z = np.where(z == nodata, np.nan, z)
    z = np.where(np.abs(z) > 1000.0, np.nan, z)  # f32 sentinel guard (conventions §8.4)
    return z, float(abs(transform.a)), transform, bounds, crs, path


def pit_list(dtm_name: str):
    cat = pd.read_csv(CATALOG)
    rows = cat[cat["DTM_NAME"] == dtm_name]
    return [(float(r.Longitude) % 360.0, float(r.Latitude)) for r in rows.itertuples()]


def run_dtm_floor(dtm_name: str, rung: float):
    t0 = time.time()
    z, res, transform, bounds, crs, src_path = load_rung(dtm_name, rung)
    valid = np.isfinite(z)
    if valid.sum() < 1000:
        return None
    args = _Args()
    args.pit = pit_list(dtm_name)
    args.crater_csv = str(CRATER_CSV)
    args.rille_shp = str(RILLE_SHP)

    slope = slope_map(np.nan_to_num(z, nan=float(np.nanmean(z))), valid, res, args.boxcar_px)
    flat = slope < args.slope_max
    excl, excl_cell, excl_info = build_exclusion(bounds, res, crs, args)
    panels = select_panels(valid, flat, slope, excl, excl_cell, res, bounds, args)

    panel_rows, dog_chunks = [], []
    for i, p in enumerate(panels):
        r0, c0, side = p["row0"], p["col0"], p["side"]
        win = z[r0:r0 + side, c0:c0 + side]
        mv = valid[r0:r0 + side, c0:c0 + side]
        dog = sag_band_dog(np.nan_to_num(win, nan=float(np.nanmean(win))), mv, res,
                           60.0, 300.0, 300.0)
        dog_v = dog[np.isfinite(dog)]
        if dog_v.size == 0:
            continue
        rms = float(np.sqrt(np.mean(dog_v ** 2)))
        dog_chunks.append(dog_v)
        cx = bounds.left + (c0 + side / 2.0) * res
        cy = bounds.top - (r0 + side / 2.0) * res
        panel_rows.append({
            "dtm": dtm_name, "panel": f"{dtm_name}_P{i + 1}", "zone": p["zone"],
            "center_x_m": cx, "center_y_m": cy, "posting_m": res,
            "size_m": p["size_m"], "area_km2": p["area_km2"],
            "mean_slope_deg": p["mean_slope_deg"], "flat_frac": p["flat_frac"],
            "n_px": int(dog_v.size), "sagband_rms_m": rms,
        })

    method = "panels"
    if len(panel_rows) >= 3:
        pooled = np.concatenate(dog_chunks)
    else:
        # fallback: whole footprint (margin-cropped) with exclusions masked
        method = f"footprint-fallback (only {len(panel_rows)} flat panels passed)"
        zf = np.nan_to_num(z, nan=float(np.nanmean(z)))
        dog = sag_band_dog(zf, valid, res, 60.0, 300.0, 300.0)
        # veto exclusion cells: upsample coarse exclusion grid by block replicate
        ry, rx = dog.shape[0] // excl.shape[0] + 1, dog.shape[1] // excl.shape[1] + 1
        big = np.repeat(np.repeat(excl, ry, 0), rx, 1)[:dog.shape[0], :dog.shape[1]]
        pooled = dog[np.isfinite(dog) & ~big]
        panel_rows = []

    if pooled.size == 0:
        return None
    rms = float(np.sqrt(np.mean(pooled ** 2)))
    prms = [p["sagband_rms_m"] for p in panel_rows] or [np.nan]
    return {
        "dtm": dtm_name, "source": str(src_path), "posting_m": res,
        "n_panels": len(panel_rows), "method": method,
        "pooled_sagband_rms_m": rms, "sigma3_Amin_m": 3.0 * rms,
        "panel_rms_min_m": float(np.min(prms)), "panel_rms_max_m": float(np.max(prms)),
        "n_px_pooled": int(pooled.size), "exclusions": excl_info,
        "runtime_s": round(time.time() - t0, 1), "panels": panel_rows,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dtms", nargs="+", required=True)
    ap.add_argument("--rung", type=float, default=5.0,
                    help="primary Z2 rung posting (default 5 m)")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    summaries, all_panels = [], []
    for d in args.dtms:
        try:
            r = run_dtm_floor(d, args.rung)
        except Exception as e:  # keep batch alive; record failure honestly
            print(f"[floor] {d}: FAILED {type(e).__name__}: {e}", flush=True)
            summaries.append({"dtm": d, "error": f"{type(e).__name__}: {e}"})
            continue
        if r is None:
            print(f"[floor] {d}: no usable data — skipped", flush=True)
            summaries.append({"dtm": d, "error": "no usable data"})
            continue
        summaries.append(r)
        all_panels.extend(r["panels"])
        print(f"[floor] {d}: posting {r['posting_m']:.1f} m, {r['n_panels']} panels, "
              f"pooled sag-band RMS {r['pooled_sagband_rms_m'] * 100:.2f} cm -> "
              f"A_min(3sigma) {r['sigma3_Amin_m']:.2f} m [{r['method']}] "
              f"({r['runtime_s']} s)", flush=True)

    keep = {k: v for s in summaries for k, v in s.items() if k != "panels"}
    df = pd.DataFrame([{k: v for k, v in s.items() if k != "panels"} for s in summaries])
    hdr = [
        "# LUNARVOID Task 18.3 — per-DTM sag-band noise floors at Z2 scale",
        f"# (generated {date.today().isoformat()}; method = Task-6 noise_floor,",
        "#  computed at the Z2 rung posting; A_min = 3x pooled sag-band RMS",
        "#  is a PROJECT CONVENTION detectability threshold, not a physical law.)",
    ]
    csv_path = args.outdir / "noise_floors.csv"
    with open(csv_path, "w") as f:
        f.write("\n".join(hdr) + "\n")
        df.to_csv(f, index=False, float_format="%.6f")
    if all_panels:
        pd.DataFrame(all_panels).to_csv(args.outdir / "noise_floors_panels.csv",
                                        index=False, float_format="%.6f")
    with open(args.outdir / "noise_floors.json", "w") as f:
        json.dump({"generated": str(date.today()), "rung_m": args.rung,
                   "dtms": summaries}, f, indent=2)
    print(f"[out] {csv_path}")


if __name__ == "__main__":
    main()
