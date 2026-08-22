"""Task 13.4 (P1.5) — Sensor-degradation stage on the LLTB-1 ladder +
composed illumination x sensor arms (LLTB-1 v0.5, 2026-08-22).

What this does
--------------
Adds the second degradation axis to the ladder benchmark: a NAC-like
SENSOR stage applied AFTER the Hapke illumination stage (arms compose:
illumination x sensor).  Per rung (0.5/1/2/5 m), on the resampled rung
raster:

  1. PSF blur — nan-aware Gaussian via normalised convolution
     (Z_blur = G*wZ / G*w), effective sigma in CELLS varying by rung:
     0.5 cell @ 0.5 m, 1.0 @ 1 m, 1.5 @ 2 m, 2.0 @ 5 m (an IFOV-
     equivalent blur that grows modestly relative to cell size as the
     product GSD coarsens, as expected from a stereo + resampling
     chain).  NoData cells stay NoData (blur never invents terrain).
  2. Radiometric/sensor height noise — sigma_z = C * res / SNR with
     SNR arms 50 / 100 / 200 and C = 16.5 calibrated so that
     SNR = 100 at the 2 m rung reproduces the Z2 TRANQPIT1 anchor
     (0.33 m NAC-DTM residual RMS): 16.5 * 2 / 100 = 0.33 m.
     Gaussian, zero-mean, seeded per (arm, rung).
  3. Bad-pixel / bad-line dropouts — 0.5 % of finite cells set to
     NoData + 2 full lines (rows) set to NoData, deterministic per
     (arm, rung); models NAC-like detector blemishes / dropped lines.

Arms (all on the SAME frozen protocol as Task 13.3):

  baseline          unperturbed master (re-run for internal consistency)
  noiseonly_i65     Hapke noise-only control (replicates 13.3 exactly)
  sensor_snr{50,100,200}        sensor-only, on baseline rungs
  i{45,65,85}_az{0,90,180,270}  full Hapke (replicates 13.3 exactly)
  hs_i*_az*_snr100              Hapke + sensor(SNR=100), all 12 geoms
  hs_i65az90_snr{50,200}        SNR sensitivity at one geometry

Protocol / honesty (unchanged from 13.3 — that is the point of the
benchmark): ground truth FIXED from the unperturbed cloud; cal/test
split FROZEN from the baseline arm (seed 42); the production
fixed-calibration tuner is left alone — if it collapses to thr=0 on a
degraded arm, that collapse is a finding, NOT tuned away.  Regressions
are reported as-is.  Task-12 entrance-trench+skylight mask is NOT used
as ground truth; these NorthSurface numbers stay separate from the v0.4
Section-8 site table.  Inference-language discipline applies: this is a
benchmark of a detector chain, not a detection claim.

CLI:
  sensor_degrade.py --npz ~/lunarvoid/data/lltb1/IndianTunnel_NorthSurface/lltb1/IndianTunnel_NorthSurface_0.5m.npz \
                    --repo-outdir 01_WORKSPACE/data/outputs/wp1_ladder/sensor \
                    --raster-outdir ~/lunarvoid/data/outputs/wp1_ladder/sensor \
                    [--rungs 0.5 1 2 5] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import sys
import zlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import Affine
from scipy.ndimage import gaussian_filter
from whitebox import WhiteboxTools

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code"))

from wp1_detector.sag_detect import cloud_ground_truth  # noqa: E402
from wp1_ladder.degrade import cloud_to_master_grid, resample  # noqa: E402
from wp1_ladder.hapke_render import (  # noqa: E402
    HAPKE_PARAMS,
    render_geometry,
    run_rung,
)

# effective PSF blur sigma in CELLS per rung (IFOV-equivalent, see docstring)
BLUR_SIGMA_CELLS = {0.5: 0.5, 1.0: 1.0, 2.0: 1.5, 5.0: 2.0}
# radiometric -> height-noise constant; SNR=100 @ 2 m -> 0.33 m (Z2 anchor)
RAD_C = 16.5
SNR_ARMS = (50, 100, 200)
BAD_PIXEL_FRAC = 0.005
BAD_LINES = 2
RELEASE = "LLTB-1 v0.5"


def arm_seed(arm_name: str, res: float) -> tuple:
    """Deterministic integer seed tuple for an (arm, rung) pair."""
    return (zlib.crc32(arm_name.encode()) & 0x7FFFFFFF, int(round(res * 10)))


# ---------------------------------------------------------------------------
# sensor stage


def psf_blur_nan(Z: np.ndarray, sigma_cells: float) -> np.ndarray:
    """Nan-aware Gaussian blur by normalised convolution.

    NoData cells stay NoData; valid cells are blurred with weights
    renormalised over their valid neighbourhood (no bleed-in of fill).
    """
    w = np.isfinite(Z).astype(np.float64)
    if w.sum() == 0 or sigma_cells <= 0:
        return Z.astype(np.float32)
    num = gaussian_filter(np.where(w > 0, Z, 0.0).astype(np.float64), sigma_cells,
                          mode="nearest")
    den = gaussian_filter(w, sigma_cells, mode="nearest")
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(den > 1e-6, num / np.maximum(den, 1e-12), np.nan)
    return np.where(w > 0, out, np.nan).astype(np.float32)


def sensor_degrade(Zr: np.ndarray, res: float, snr: float, seed_key: tuple,
                   blur_cells: float | None = None,
                   bad_pixel_frac: float = BAD_PIXEL_FRAC,
                   n_bad_lines: int = BAD_LINES) -> tuple[np.ndarray, dict]:
    """Apply the full sensor stage to one rung raster.

    seed_key = any hashable tuple labelling (arm, rung) — deterministic.
    Returns (degraded raster, stats dict).
    """
    sigma_cells = BLUR_SIGMA_CELLS.get(float(res), 1.0) if blur_cells is None else blur_cells
    Zb = psf_blur_nan(Zr, sigma_cells)
    sigma_rad = RAD_C * res / snr
    rng_noise = np.random.default_rng([42, 900, *seed_key])
    Zs = Zb + np.where(np.isfinite(Zb), rng_noise.normal(0.0, sigma_rad, Zb.shape), np.nan)
    # bad pixels: fixed fraction of finite cells -> NoData
    rng_bad = np.random.default_rng([42, 901, *seed_key])
    finite_idx = np.argwhere(np.isfinite(Zs))
    n_bad = int(round(bad_pixel_frac * len(finite_idx)))
    stats = {"sigma_cells": float(sigma_cells), "sigma_rad_m": float(sigma_rad),
             "n_bad_pixels": n_bad, "n_bad_lines": 0,
             "dZ_blur_med_m": float(np.nanmedian(np.abs(Zb - Zr))) if np.isfinite(Zb).any() else float("nan")}
    if n_bad > 0 and len(finite_idx) > 0:
        pick = rng_bad.choice(len(finite_idx), size=min(n_bad, len(finite_idx)),
                              replace=False)
        Zs[finite_idx[pick][:, 0], finite_idx[pick][:, 1]] = np.nan
    # bad lines: n full rows (kept inside the finite-data band) -> NoData
    rows_finite = np.where(np.isfinite(Zs).sum(axis=1) > 0)[0]
    if n_bad_lines > 0 and len(rows_finite) > 4 * n_bad_lines:
        lo, hi = rows_finite.min(), rows_finite.max()
        band = np.arange(lo + 2, hi - 1)  # avoid the outermost rows
        rng_lines = np.random.default_rng([42, 902, *seed_key])
        rows = rng_lines.choice(band, size=n_bad_lines, replace=False)
        Zs[rows, :] = np.nan
        stats["n_bad_lines"] = int(n_bad_lines)
        stats["bad_line_rows"] = [int(r) for r in rows]
    stats["valid_frac"] = float(np.isfinite(Zs).sum() / Zs.size)
    return Zs.astype(np.float32), stats


# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--repo-outdir", type=Path, required=True)
    ap.add_argument("--raster-outdir", type=Path, required=True)
    ap.add_argument("--rungs", type=float, nargs="+", default=[0.5, 1, 2, 5])
    ap.add_argument("--grid-spacing", type=float, default=0.5)
    ap.add_argument("--incidences", type=float, nargs="+", default=[45, 65, 85])
    ap.add_argument("--azimuths", type=float, nargs="+", default=[0, 90, 180, 270])
    ap.add_argument("--snrs", type=int, nargs="+", default=list(SNR_ARMS))
    ap.add_argument("--sigma0", type=float, default=0.33)
    ap.add_argument("--sigma-max", type=float, default=2.0)
    ap.add_argument("--slope-mask-degrees", type=float, default=10.0)
    ap.add_argument("--min-component", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    args.repo_outdir.mkdir(parents=True, exist_ok=True)
    args.raster_outdir.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/sensor_ladder")
    tmp.mkdir(parents=True, exist_ok=True)

    wbt = WhiteboxTools()
    import whitebox
    wbt.set_whitebox_dir(str(Path(whitebox.__file__).parent))
    wbt.set_working_dir("/tmp")
    wbt.verbose = False

    # ---- load cloud, fixed GT, master ------------------------------------
    data = np.load(args.npz)
    x, y, z = data["x"], data["y"], data["z"]
    print(f"[load] {len(x):,} points from {args.npz.name}", flush=True)
    gt, gt_geo = cloud_ground_truth(x, y, z, args.grid_spacing, threshold_depth=1.0)
    x_min, y_min, nx, ny, px = gt_geo
    Z0, tr0, valid0, _ = cloud_to_master_grid(x, y, z, args.grid_spacing)
    print(f"[gt  ] master {ny}x{nx} @ {px} m, void cells = {int(gt.sum())}", flush=True)

    rungs = sorted(set(args.rungs))

    # ---- illumination stage (replicates 13.3 arms bit-for-bit) ------------
    geoms = [(i, a) for i in args.incidences for a in args.azimuths]
    hapke_master = {}
    geom_voiding = {}
    for inc, az in geoms:
        R = render_geometry(Z0, args.grid_spacing, inc, az, HAPKE_PARAMS,
                            sigma0=args.sigma0, sigma_max=args.sigma_max)
        key = f"i{inc:g}_az{az:g}"
        # shadow voiding of void labels, BOTH denominators (skeptic fix)
        vm = np.isfinite(Z0)
        void_valid = gt & vm
        geom_voiding[key] = {
            "incidence_deg": inc, "azimuth_deg": az,
            "void_cells_shadowed_frac_allvoid": float(R["shadow"][gt].mean()),
            "void_cells_shadowed_frac_validvoid": float(R["shadow"][void_valid].mean()),
        }
        rng = np.random.default_rng([args.seed, int(inc), int(az)])
        noise = rng.normal(0.0, 1.0, size=Z0.shape)
        hapke_master[key] = Z0 + np.where(np.isfinite(R["sigma_z"]), R["sigma_z"] * noise, np.nan)

    inc, az = 65.0, 90.0
    Rn = render_geometry(Z0, args.grid_spacing, inc, az, HAPKE_PARAMS,
                         sigma0=args.sigma0, sigma_max=args.sigma_max)
    sig_only = np.where(np.isfinite(Z0),
                        np.minimum(args.sigma0 * np.sqrt(Rn["r_ref"] /
                                  np.maximum(Rn["refl"], 1e-3 * Rn["r_ref"])),
                                  args.sigma_max), np.nan)
    rng = np.random.default_rng([args.seed, 651, 659])
    hapke_master["noiseonly_i65"] = Z0 + sig_only * rng.normal(0.0, 1.0, Z0.shape)

    for i_ in sorted(args.incidences):
        subs = [v for k, v in geom_voiding.items() if v["incidence_deg"] == i_]
        a = np.mean([s["void_cells_shadowed_frac_allvoid"] for s in subs])
        b = np.mean([s["void_cells_shadowed_frac_validvoid"] for s in subs])
        print(f"[voiding] i={i_:g}: azimuth-mean allvoid {a:.3f} validvoid {b:.3f}", flush=True)

    # ---- arm schedule ------------------------------------------------------
    # arm name -> (master array, sensor spec or None)
    arms = {"baseline": (Z0, None)}
    arms["noiseonly_i65"] = (hapke_master["noiseonly_i65"], None)
    for snr in args.snrs:
        arms[f"sensor_snr{snr}"] = (Z0, {"snr": snr})
    for key in [f"i{i_:g}_az{a_:g}" for i_, a_ in geoms]:
        arms[key] = (hapke_master[key], None)
    for key in [f"i{i_:g}_az{a_:g}" for i_, a_ in geoms]:
        arms[f"hs_{key}_snr100"] = (hapke_master[key], {"snr": 100})
    if 65.0 in args.incidences and 90.0 in args.azimuths:
        for snr in (50, 200):
            if snr in args.snrs:
                arms[f"hs_i65az90_snr{snr}"] = (hapke_master["i65_az90"], {"snr": snr})

    # ---- paired ladder re-run (frozen split from baseline) -----------------
    from scipy.ndimage import zoom
    rows, sensor_stats = [], {}
    cal_masks = {}
    for arm_name, (Zm, spec) in arms.items():
        print(f"\n--- arm {arm_name} ---", flush=True)
        for r in rungs:
            if abs(r - args.grid_spacing) < 1e-9:
                Zr = Zm.astype(np.float32).copy()
            else:
                Zr, _ = resample(Zm, tr0, args.grid_spacing, r, method="average")
            # sensor stage AFTER Hapke/resample (composition)
            if spec is not None:
                seed_key = arm_seed(arm_name, r)
                Zr, sst = sensor_degrade(Zr, r, spec["snr"], seed_key)
                sensor_stats[f"{arm_name}@{r:g}"] = sst
            ny_r, nx_r = Zr.shape
            truth_r = zoom(gt.astype(np.float32), (ny_r / ny, nx_r / nx),
                           order=0).astype(bool) if (nx_r, ny_r) != (nx, ny) else gt
            if r in cal_masks:
                cal_mask, test_mask = cal_masks[r]
            else:
                score_proxy = np.isfinite(Zr)
                rng = np.random.default_rng(args.seed)
                ev = np.argwhere(score_proxy)
                perm = rng.permutation(len(ev))
                n_cal = len(ev) // 2
                cal_mask = np.zeros(Zr.shape, dtype=bool)
                cal_mask[ev[perm[:n_cal]][:, 0], ev[perm[:n_cal]][:, 1]] = True
                test_mask = score_proxy & ~cal_mask
                cal_masks[r] = (cal_mask, test_mask)
            m = run_rung(Zr, r, truth_r, cal_mask, test_mask, wbt, tmp,
                         min_component=args.min_component,
                         slope_mask_deg=args.slope_mask_degrees,
                         origin=(x_min, y_min))
            m.update({"arm": arm_name, "res_m": float(r)})
            rows.append(m)
            # store the perturbed rung raster (~/lunarvoid convention)
            gdir = args.raster_outdir / arm_name
            gdir.mkdir(parents=True, exist_ok=True)
            profile = {"driver": "GTiff", "dtype": "float32", "nodata": -9999.0,
                       "width": nx_r, "height": ny_r, "count": 1,
                       "transform": tr0 if abs(r - args.grid_spacing) < 1e-9 else
                       Affine(r, 0.0, tr0.c, 0.0, -r, tr0.f),
                       "compress": "deflate", "BIGTIFF": "IF_SAFER"}
            with rasterio.open(gdir / f"rung_{r:g}m.tif", "w", **profile) as dst:
                dst.write(np.where(np.isfinite(Zr), Zr, -9999.0).astype(np.float32), 1)
            print(f"[rung {r:g} m] F1={m['f1_test']:.3f} (+slope {m['f1_test_slope']:.3f}), "
                  f"P={m['precision_test']:.3f}, R={m['recall_test']:.3f}, "
                  f"valid {m['valid_frac']:.2%}", flush=True)

    df = pd.DataFrame(rows)
    csv_path = args.repo_outdir / "sensor_f1_comparison.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[out ] comparison table -> {csv_path}", flush=True)

    # ---- consistency check vs the committed 13.3 Hapke table ---------------
    hapke_csv = args.repo_outdir.parent / "hapke" / "hapke_f1_comparison.csv"
    consistency = {"file": str(hapke_csv), "max_abs_diff_f1_test_slope": None, "arms_checked": 0}
    if hapke_csv.exists():
        dfh = pd.read_csv(hapke_csv)
        merged = df.merge(dfh, on=["arm", "res_m"], suffixes=("", "_old"))
        d = (merged["f1_test_slope"] - merged["f1_test_slope_old"]).abs().max()
        consistency.update({"max_abs_diff_f1_test_slope": float(d),
                            "arms_checked": int(len(merged))})
        print(f"[consistency] vs committed 13.3 CSV: max |dF1| = {d:.6f} "
              f"over {len(merged)} matched rows", flush=True)

    # ---- composed degradation table ----------------------------------------
    def f1s(arm, r):
        sub = df[(df.arm == arm) & (df.res_m == r)]
        return float(sub["f1_test_slope"].iloc[0]) if len(sub) else float("nan")

    def hapke_mean(r, prefix="i"):
        sub = df[(df.arm.str.startswith(prefix)) & (~df.arm.str.startswith("sensor")) &
                 (~df.arm.str.startswith("hs_")) & (~df.arm.str.startswith("noiseonly")) &
                 (df.res_m == r)]
        vals = sub["f1_test_slope"].values
        return float(np.mean(vals)), float(np.min(vals)), float(np.max(vals))

    composed = {}
    for r in rungs:
        h_mean, h_min, h_max = hapke_mean(r)
        hs = df[(df.arm.str.startswith("hs_")) & (~df.arm.str.startswith("hs_i65az90_snr50")) &
                (~df.arm.str.startswith("hs_i65az90_snr200")) & (df.res_m == r)]
        hs_vals = hs["f1_test_slope"].values
        composed[f"{r:g}"] = {
            "baseline": f1s("baseline", r),
            "noiseonly_i65": f1s("noiseonly_i65", r),
            "sensor_snr50": f1s("sensor_snr50", r),
            "sensor_snr100": f1s("sensor_snr100", r),
            "sensor_snr200": f1s("sensor_snr200", r),
            "hapke_mean": h_mean, "hapke_min": h_min, "hapke_max": h_max,
            "hapkesensor_snr100_mean": float(np.mean(hs_vals)),
            "hapkesensor_snr100_min": float(np.min(hs_vals)),
            "hapkesensor_snr100_max": float(np.max(hs_vals)),
            "n_hapke_geoms": int(len(hs_vals)),
        }
        c = composed[f"{r:g}"]
        print(f"[composed {r:g} m] base {c['baseline']:.3f} | noise {c['noiseonly_i65']:.3f} "
              f"| sensor(s100) {c['sensor_snr100']:.3f} | hapke {c['hapke_mean']:.3f} "
              f"({c['hapke_min']:.3f}-{c['hapke_max']:.3f}) "
              f"| hapke+sensor(s100) {c['hapkesensor_snr100_mean']:.3f} "
              f"({c['hapkesensor_snr100_min']:.3f}-{c['hapkesensor_snr100_max']:.3f})", flush=True)

    # ---- summary ------------------------------------------------------------
    summary = {
        "task": "13.4 (P1.5) sensor-degradation stage + composed illumination x sensor arms",
        "release": RELEASE,
        "run_date": "2026-08-22",
        "source_npz": str(args.npz),
        "site": "IndianTunnel_NorthSurface (LLTB-1 ladder master)",
        "sensor_model": {
            "psf_blur": {"form": "nan-aware Gaussian, normalised convolution",
                         "sigma_cells_by_rung": {str(k): v for k, v in BLUR_SIGMA_CELLS.items()},
                         "rationale": "NAC-like IFOV-equivalent at the rung scales"},
            "radiometric": {"form": "sigma_z = C * res / SNR", "C": RAD_C,
                            "snr_arms": list(args.snrs),
                            "calibration": "SNR=100 @ 2 m -> 0.33 m, the Z2 TRANQPIT1 "
                                           "NAC-DTM residual-RMS anchor"},
            "dropouts": {"bad_pixel_frac": BAD_PIXEL_FRAC, "bad_lines": BAD_LINES},
            "applied_after": "Hapke illumination stage (arms compose: illumination x sensor)",
        },
        "protocol": {
            "gt": "FIXED from unperturbed cloud (sag_detect.cloud_ground_truth, 0.5 m, thr 1.0 m)",
            "cal_test_split": "frozen from baseline arm finite cells, seed 42",
            "detector": "production sag_detect chain (PD fill + Frangi 30-300 m + cal-half "
                        f"threshold tuning + component filter >= {args.min_component} + fixed "
                        f"{args.slope_mask_degrees:g} deg slope mask); NO re-tuning to rescue F1",
            "tuner_collapse_is_a_finding": True,
            "task12_guardrail": "entrance-trench+skylight mask NOT used as GT; NorthSurface "
                                "numbers reported separately from the v0.4 Section-8 site table",
        },
        "shadow_voiding_correction": {
            "note": "both denominators logged per azimuth (skeptic 2026-08-22); METHODS.md "
                    "quotes the all-void azimuth means",
            "per_geometry": geom_voiding,
            "azimuth_means": {
                f"i{i_:g}": {
                    "allvoid": float(np.mean([v["void_cells_shadowed_frac_allvoid"]
                                              for v in geom_voiding.values()
                                              if v["incidence_deg"] == i_])),
                    "validvoid": float(np.mean([v["void_cells_shadowed_frac_validvoid"]
                                                for v in geom_voiding.values()
                                                if v["incidence_deg"] == i_])),
                } for i_ in sorted(args.incidences)
            },
        },
        "composed_table_f1_test_slope": composed,
        "consistency_vs_133_csv": consistency,
        "sensor_stats": {k: {kk: vv for kk, vv in v.items() if kk != "bad_line_rows"}
                         for k, v in sensor_stats.items()},
        "csv": str(csv_path),
        "raster_dir": str(args.raster_outdir),
    }
    sum_path = args.repo_outdir / "sensor_summary.json"
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[out ] summary -> {sum_path}", flush=True)

    # ---- degradation-preview figure (baseline vs sensor vs hapke+sensor) ---
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), squeeze=False)
    prev = {"baseline": Z0, "sensor_snr100": None, "i65_az90": hapke_master["i65_az90"],
            "hs_i65_az90_snr100": None}
    sens_prev = {}
    for name in ("sensor_snr100", "hs_i65_az90_snr100"):
        Zr = prev["baseline"] if name.startswith("sensor") else hapke_master["i65_az90"]
        Zr, sst = sensor_degrade(np.asarray(Zr, dtype=np.float32), args.grid_spacing,
                                 100, arm_seed(name, args.grid_spacing))
        sens_prev[name] = (Zr, sst)
    panels = [("baseline", prev["baseline"]), ("sensor_snr100 @0.5m", sens_prev["sensor_snr100"][0]),
              ("Hapke i65 az90", prev["i65_az90"]),
              ("Hapke+sensor snr100", sens_prev["hs_i65_az90_snr100"][0])]
    for ax, (t, A) in zip(axes.flat, panels):
        im = ax.imshow(A, cmap="terrain", origin="lower")
        ax.set_title(t, fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        fig.colorbar(im, ax=ax, shrink=0.8)
    fig.suptitle("LLTB-1 v0.5 sensor stage (PSF + radiometric + dropouts), 0.5 m master")
    fig.tight_layout()
    fig_path = args.repo_outdir / "sensor_degradation_preview.png"
    fig.savefig(fig_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"[out ] preview -> {fig_path}", flush=True)
    print("[done]", flush=True)


if __name__ == "__main__":
    main()
