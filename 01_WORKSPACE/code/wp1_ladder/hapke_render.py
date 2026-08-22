"""Hapke-IMSA synthetic-illumination re-rendering of the LLTB-1 analog
master DTM + paired ladder re-run (Z1 Task 13.3 / P1.4, 2026-08-22).

What this does
--------------
1. Renders the IndianTunnel_NorthSurface ladder master (0.5 m DTM,
   mean-z binning of the source cloud, i.e. degrade.py's
   cloud_to_master_grid) under 12 synthetic solar geometries spanning
   the lunar NAC range: incidence 45/65/85 deg x azimuth
   0/90/180/270 deg, nadir viewing (phase g = map incidence).
   Reflectance model: standard Hapke IMSA
       r(i,e,g) = w/4pi * mu0/(mu0+mu) * [(1+B(g)) P(g) + H(mu0)H(mu)-1]
   (Hapke 1993; 2012 2nd ed. Ch. 8S) with two-term Henyey-Greenstein
   P(g) and the C-regime opposition surge B(g). Parameters are
   lunar-mare literature values, NOT fitted - see METHODS.md next to
   the outputs.

2. Rebuilds each geometry's master DTM as the analog of what a
   NAC-like pipeline would deliver: original elevations + (a) cast +
   self shadowing (ray-marched over the DTM facets -> NoData cells)
   and (b) shot-noise-scaled height error sigma_z(i) = sigma0 *
   sqrt(r_ref / r_cell) with sigma0 = 0.33 m anchored to our own Z2
   TRANQPIT1 NAC-DTM residual RMS (0.327 m).

3. Re-runs the affected ladder rungs (0.5/1/2/5 m) through the SAME
   detector chain as production sag_detect.py (Planchon-Darboux fill
   -> Frangi 30-300 m -> depth*vesselness score -> per-rung threshold
   tuning -> connected-component filter -> 10 deg slope mask), with
   one protocol change for honesty: the ground truth and the
   calibration/test split are FIXED from the unperturbed baseline arm
   (sag_detect.py derives GT from the same cloud it detects on, which
   would let photometric noise move the labels - a confounder).
   Baseline arm = same code path, unperturbed master. Every per-rung
   F1 delta is therefore attributable to the Hapke perturbation only.

Protocol / honesty notes
------------------------
- Entrance-trench+skylight mask (Task 12) is NOT used as ground truth
  (Task-12 GUARDRAILS); the LLTB-1 cloud-derived void label set is
  used, as in all ladder rungs.
- These NorthSurface sag-rung numbers are reported SEPARATELY from
  the v0.4 Section-8 site table; nothing here updates it.
- Regressions are reported, never tuned away. A negligible delta IS
  the result (null-result rung).

CLI:
  hapke_render.py --npz ~/lunarvoid/data/lltb1/IndianTunnel_NorthSurface/lltb1/IndianTunnel_NorthSurface_0.5m.npz \
                  --repo-outdir 01_WORKSPACE/data/outputs/wp1_ladder/hapke \
                  --raster-outdir ~/lunarvoid/data/outputs/wp1_ladder/hapke \
                  [--rungs 0.5 1 2 5] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
import whitebox
from rasterio.transform import Affine, from_bounds
from scipy.ndimage import map_coordinates
from whitebox import WhiteboxTools

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code"))

from wp1_detector.sag_detect import (  # noqa: E402
    _f1_from_pred,
    cloud_ground_truth,
    filter_small_components,
    f1_at_threshold,
    frangi_vesselness,
    sink_fill_planchon,
    slope_deg_map,
    tune_threshold,
    write_geotiff,
)
from wp1_ladder.degrade import cloud_to_master_grid, resample  # noqa: E402

# ---------------------------------------------------------------------------
# Hapke IMSA model.  Lunar-mare literature values, not fitted:
#   w  = 0.15   single-scattering albedo, mid-visible mature mare;
#               Hapke (1993) lunar fits span ~0.11-0.19 by band.
#   b  = 0.21   2-lobe Henyey-Greenstein asymmetry (Hapke 1993).
#   c  = 0.70   backward-lobe weight (regolith is backscattering).
#   h  = 0.05   opposition-surge angular width (typical lunar value;
#               Hapke et al. 2012 JGR).
#   B0 = 0.6    opposition amplitude.  At g>=45 deg the surge is
#               anyway <=0.07 (negligible; documented, not fitted).
#   theta_bar: NOT a parameter of IMSA (the isotropic multiple
#               scattering approximation has no roughness term).
#               Typical mare theta_bar ~ 20-25 deg (Hapke et al. 2012)
#               would rescale ABSOLUTE reflectance by an approximately
#               geometry-constant factor that cancels in the relative
#               signal-to-noise use here.  Omission documented.
HAPKE_PARAMS = {"w": 0.15, "b": 0.21, "c": 0.70, "h": 0.05, "B0": 0.60}


def chandrasekhar_H(x: np.ndarray, w: float) -> np.ndarray:
    """Hapke's 2-term rational approximation of the H function."""
    return (1.0 + 2.0 * x) / (1.0 + 2.0 * x * np.sqrt(np.clip(1.0 - w, 0.0, 1.0)))


def henyey_greenstein_2(g_rad: np.ndarray, b: float, c: float) -> np.ndarray:
    """Two-term HG single-particle phase function, Hapke (1993) eq. 6.16.

    c weights the BACKWARD lobe (g = 0); (1-c) the forward lobe (g=pi).
    """
    g = np.asarray(g_rad, dtype=np.float64)
    fwd = (1.0 - b**2) / (1.0 + b**2 + 2.0 * b * np.cos(g)) ** 1.5
    bwd = (1.0 - b**2) / (1.0 + b**2 - 2.0 * b * np.cos(g)) ** 1.5
    return (1.0 - c) * fwd + c * bwd


def hapke_imsa(mu0, mu, g_rad, p: dict = HAPKE_PARAMS) -> np.ndarray:
    """Hapke IMSA bidirectional reflectance (Hapke 1993 / 2012 Ch. 8S).

    mu0 = cos(incidence), mu = cos(emission), both on the FACET normal.
    mu0<=0 (self-shadowed facet) returns 0.
    """
    mu0 = np.clip(np.asarray(mu0, dtype=np.float64), 0.0, None)
    mu = np.clip(np.asarray(mu, dtype=np.float64), 0.0, None)
    g = np.asarray(g_rad, dtype=np.float64)
    B = p["B0"] / (1.0 + np.tan(np.clip(g, 0.0, np.pi - 1e-9) / 2.0) / p["h"])
    P = henyey_greenstein_2(g, p["b"], p["c"])
    term = (1.0 + B) * P + chandrasekhar_H(mu0, p["w"]) * chandrasekhar_H(mu, p["w"]) - 1.0
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (p["w"] / (4.0 * np.pi)) * (mu0 / (mu0 + mu)) * term
    return np.where((mu0 > 0) & (mu > 0), r, 0.0)


# ---------------------------------------------------------------------------
# geometry on the DTM grid


def facet_normals(Z: np.ndarray, res: float):
    """Unit normals n = normalise(-dz/dx, -dz/dy, +1) with z up.

    Row axis is +y, col axis is +x (degrade/sag array convention,
    row 0 = y_min).  NaN cells -> NaN normal components.
    """
    Zf = np.where(np.isfinite(Z), Z, np.nanmean(Z[np.isfinite(Z)]))
    dz_dy, dz_dx = np.gradient(Zf, res)
    norm = np.sqrt(dz_dx**2 + dz_dy**2 + 1.0)
    return -dz_dx / norm, -dz_dy / norm, 1.0 / norm


def sun_vector(inc_deg: float, az_deg: float):
    """Unit vector TOWARD the sun; az CCW from +x in the map (row=y,
    col=x) frame, incidence from +z.  Returns (sx, sy, sz)."""
    i = np.radians(inc_deg)
    a = np.radians(az_deg)
    return np.cos(a) * np.sin(i), np.sin(a) * np.sin(i), np.cos(i)


def cast_shadow(Z: np.ndarray, res: float, inc_deg: float, az_deg: float) -> np.ndarray:
    """Boolean cast-shadow mask via cell-quantised ray march.

    From each valid cell, march toward the sun in 0.5-cell steps; the
    cell is shadowed if any terrain along the ray rises above the ray
    height Z(cell) + t*res*tan(i).  NaN terrain does not block.
    March length covers the full grid diagonal.
    """
    ny, nx = Z.shape
    # vertical rise of the sun ray per metre of horizontal advance toward
    # the sun = cot(incidence) = tan(sun elevation).  NB: NOT tan(i) —
    # incidence is from ZENITH, so high incidence (low sun) => LONG
    # shadows.  (Bug caught by the synthetic-wall unit check: with
    # tan(i) a 10 m wall at i=85 deg cast <1 m instead of ~114 m.)
    elev_rad = np.radians(max(1e-6, 90.0 - inc_deg))
    ray_slope = np.tan(elev_rad)
    dx, dy, _ = sun_vector(inc_deg, az_deg)
    # horizontal unit direction toward the sun in cell units
    dlen = np.hypot(dx, dy)
    if dlen < 1e-9:  # incidence 0: no cast shadow
        return np.zeros_like(Z, dtype=bool)
    ux, uy = dx / dlen, dy / dlen
    rows_f, cols_f = np.indices(Z.shape, dtype=np.float64)
    valid = np.isfinite(Z)
    shadow = np.zeros(Z.shape, dtype=bool)
    max_t = 2.0 * np.hypot(ny, nx)
    t = 0.5
    Zfill = np.where(valid, Z, -np.inf)
    while t < max_t:
        pr = rows_f + t * uy
        pc = cols_f + t * ux
        inside = (pr >= 0) & (pr <= ny - 1) & (pc >= 0) & (pc <= nx - 1)
        if not inside.any():
            break
        terr = map_coordinates(Zfill, [pr, pc], order=1, mode="constant", cval=-np.inf)
        ray = Zfill + t * res * ray_slope
        blocked = np.nan_to_num(terr, nan=-np.inf) > ray
        shadow |= (valid & inside & blocked)
        # stop when no un-shadowed valid cell still has its ray inside
        # the grid (cells whose ray left the grid are simply not blocked)
        active = valid & ~shadow
        if not active.any() or not (inside & active).any():
            break
        t += 0.5
    return shadow


def render_geometry(Z: np.ndarray, res: float, inc_deg: float, az_deg: float,
                    p: dict = HAPKE_PARAMS, sigma0: float = 0.33,
                    unusable_frac: float = 0.02, sigma_max: float = 2.0):
    """Hapke render of the master DTM + the perturbation fields.

    Returns dict with refl (float32, 0 in shadow), shadow (bool, cast OR
    self), sigma_z (NaN where unusable), g_rad (scalar, map-plane phase
    angle = incidence for nadir viewing), and r_ref (flat-facet
    reference reflectance at this geometry).
    """
    nx_, ny_, nz_ = facet_normals(Z, res)
    sx, sy, sz = sun_vector(inc_deg, az_deg)
    mu0 = nx_ * sx + ny_ * sy + nz_ * sz          # cos incidence on facet
    mu = np.clip(nz_, 0.0, None)                  # nadir emission on facet
    g = np.radians(inc_deg)                       # phase = map incidence (nadir view)
    refl = hapke_imsa(mu0, mu, g, p).astype(np.float32)
    self_shadow = mu0 <= 0.0
    shadow = self_shadow | cast_shadow(Z, res, inc_deg, az_deg)
    refl = np.where(shadow, 0.0, refl).astype(np.float32)
    # reference reflectance: flat facet (mu0=cos i, mu=1) at this geometry
    r_ref = float(hapke_imsa(np.cos(np.radians(inc_deg)), 1.0, g, p))
    # shot-noise-scaled height error: sigma_z = sigma0 * sqrt(r_ref / r)
    with np.errstate(divide="ignore", invalid="ignore"):
        sig = sigma0 * np.sqrt(r_ref / np.maximum(refl, 1e-12))
    unusable = shadow | (refl < unusable_frac * r_ref) | ~np.isfinite(Z)
    sig = np.where(unusable, np.nan, np.minimum(sig, sigma_max)).astype(np.float32)
    return {"refl": refl, "shadow": shadow, "sigma_z": sig,
            "r_ref": r_ref, "g_rad": float(g)}


# ---------------------------------------------------------------------------
# detector chain (mirror of sag_detect.main rung loop, GT+split injected)


def run_rung(Zr: np.ndarray, res: float, truth_r: np.ndarray, cal_mask: np.ndarray,
             test_mask: np.ndarray, wbt: WhiteboxTools, tmpdir: Path,
             min_component: int = 5, slope_mask_deg: float = 10.0,
             frangi_sigmas=(30, 60, 100, 150, 200, 300), origin=(0.0, 0.0)) -> dict:
    """One rung of the production sag chain on an injected DTM array."""
    ny, nx = Zr.shape
    tr = Affine(res, 0.0, origin[0], 0.0, res, origin[1])  # geokeys for WBT
    dtm_tif = tmpdir / f"dtm_{res:g}.tif"
    fill_tif = tmpdir / f"filled_{res:g}.tif"
    write_geotiff(Zr.astype(np.float32), tr, dtm_tif, nodata=-9999.0)
    sink_fill_planchon(wbt, dtm_tif, fill_tif)
    with rasterio.open(fill_tif) as fs, rasterio.open(dtm_tif) as ds:
        fill = fs.read(1).astype(np.float32)
        dtm = ds.read(1).astype(np.float32)
        fill_nd = fs.nodata
    fill_v = np.where(fill == (fill_nd if fill_nd is not None else -9999.0), np.nan, fill)
    dtm_v = np.where(dtm == -9999.0, np.nan, dtm)
    depth = np.maximum(fill_v - dtm_v, 0.0)
    V = frangi_vesselness(dtm_v, res, sigmas=tuple(frangi_sigmas))
    score = (np.where(np.isfinite(depth), depth, 0.0) *
             np.where(np.isfinite(V), V, 0.0)).astype(np.float32)
    thr, f1_cal = tune_threshold(score[cal_mask], truth_r[cal_mask])
    pred_full = filter_small_components(score >= thr, min_size=min_component)
    slope_deg = slope_deg_map(dtm, res)
    slope_ok = (slope_deg >= slope_mask_deg) & np.isfinite(slope_deg) if \
        np.any(np.isfinite(slope_deg)) else np.zeros_like(dtm, dtype=bool)
    m_tst = _f1_from_pred(pred_full[test_mask], truth_r[test_mask])
    m_slope = _f1_from_pred((pred_full & slope_ok)[test_mask], truth_r[test_mask])
    cell_area_km2 = (res * res) / 1e6
    n_test = int(test_mask.sum())
    fp_1e4 = m_tst["fp"] * 1e4 / (n_test * cell_area_km2) if n_test else float("nan")
    return {
        "threshold": float(thr), "f1_cal": float(f1_cal),
        "f1_test": float(m_tst["f1"]), "f1_test_slope": float(m_slope["f1"]),
        "precision_test": float(m_tst["precision"]),
        "recall_test": float(m_tst["recall"]),
        "precision_test_slope": float(m_slope["precision"]),
        "recall_test_slope": float(m_slope["recall"]),
        "fp_per_1e4km2_test": float(fp_1e4),
        "valid_frac": float(np.isfinite(dtm_v).sum() / dtm_v.size),
        "n_void_cells": int(truth_r.sum()),
        "n_test_cells": n_test,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--npz", type=Path, required=True,
                    help="source cloud npz (x, y, z) of the ladder master")
    ap.add_argument("--repo-outdir", type=Path, required=True,
                    help="repo deliverable dir (renders, CSV, JSON)")
    ap.add_argument("--raster-outdir", type=Path, required=True,
                    help="~/lunarvoid dir for derived perturbation rasters")
    ap.add_argument("--rungs", type=float, nargs="+", default=[0.5, 1, 2, 5])
    ap.add_argument("--grid-spacing", type=float, default=0.5)
    ap.add_argument("--incidences", type=float, nargs="+", default=[45, 65, 85])
    ap.add_argument("--azimuths", type=float, nargs="+", default=[0, 90, 180, 270])
    ap.add_argument("--sigma0", type=float, default=0.33,
                    help="height noise at reference geometry (m); Z2 TRANQPIT1 anchor")
    ap.add_argument("--sigma-max", type=float, default=2.0)
    ap.add_argument("--slope-mask-degrees", type=float, default=10.0)
    ap.add_argument("--min-component", type=int, default=5)
    ap.add_argument("--sensitivity-w", type=float, nargs="*", default=[0.11, 0.19],
                    help="extra w values at geometry (65,90) for a parameter-"
                         "sensitivity row set")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    args.repo_outdir.mkdir(parents=True, exist_ok=True)
    args.raster_outdir.mkdir(parents=True, exist_ok=True)
    tmp = Path("/tmp/hapke_ladder")
    tmp.mkdir(parents=True, exist_ok=True)

    # whitebox runtime configuration (conventions skill section 8)
    wbt = WhiteboxTools()
    wbt.set_whitebox_dir(str(Path(whitebox.__file__).parent))
    wbt.set_working_dir("/tmp")
    wbt.verbose = False

    # ---- load cloud, GT, master -----------------------------------------
    data = np.load(args.npz)
    x, y, z = data["x"], data["y"], data["z"]
    print(f"[load] {len(x):,} points from {args.npz.name}", flush=True)
    gt, gt_geo = cloud_ground_truth(x, y, z, args.grid_spacing, threshold_depth=1.0)
    x_min, y_min, nx, ny, px = gt_geo
    print(f"[gt  ] master {ny}x{nx} @ {px} m, void cells = {int(gt.sum())}", flush=True)

    Z0, tr0, valid0, _ = cloud_to_master_grid(x, y, z, args.grid_spacing)
    print(f"[grid] master {Z0.shape}, valid frac {valid0.mean():.3f}", flush=True)

    # sanity check vs the on-disk ladder master (same binning code path)
    on_disk = Path.home() / ("lunarvoid/data/lltb1/IndianTunnel_NorthSurface/"
                             "lltb1/ladder/master_0.5m.tif")
    if on_disk.exists():
        with rasterio.open(on_disk) as src:
            Zd = src.read(1)
        both = np.isfinite(Z0) & np.isfinite(Zd)
        med_abs = float(np.median(np.abs(Z0[both] - Zd[both])))
        print(f"[sanity] vs on-disk master_0.5m.tif: median|dZ| = {med_abs:.4f} m "
              f"(finite overlap {both.sum()} cells)", flush=True)
        assert med_abs < 0.05, "master mismatch vs on-disk ladder master"

    # ---- geometries + Hapke renders --------------------------------------
    geoms = [(i, a) for i in args.incidences for a in args.azimuths]
    renders, arms = {}, {"baseline": Z0}
    geom_meta = {}
    for inc, az in geoms:
        R = render_geometry(Z0, args.grid_spacing, inc, az, HAPKE_PARAMS,
                            sigma0=args.sigma0, sigma_max=args.sigma_max)
        key = f"i{inc:g}_az{az:g}"
        renders[key] = R
        # reflectance render -> repo (small float32 GeoTIFF, master transform)
        render_tif = args.repo_outdir / f"render_{key}.tif"
        profile = {"driver": "GTiff", "dtype": "float32", "nodata": -9999.0,
                   "width": Z0.shape[1], "height": Z0.shape[0], "count": 1,
                   "transform": tr0, "compress": "deflate", "BIGTIFF": "IF_SAFER"}
        with rasterio.open(render_tif, "w", **profile) as dst:
            dst.write(np.where(np.isfinite(R["refl"]), R["refl"], -9999.0), 1)
        # perturbed master -> ~/lunarvoid
        rng = np.random.default_rng([args.seed, int(inc), int(az)])
        noise = rng.normal(0.0, 1.0, size=Z0.shape)
        Zp = Z0 + np.where(np.isfinite(R["sigma_z"]), R["sigma_z"] * noise, np.nan)
        gdir = args.raster_outdir / key
        gdir.mkdir(parents=True, exist_ok=True)
        with rasterio.open(gdir / "master_0.5m_hapke.tif", "w", **profile) as dst:
            dst.write(np.where(np.isfinite(Zp), Zp, -9999.0).astype(np.float32), 1)
        arms[key] = Zp
        geom_meta[key] = {
            "incidence_deg": inc, "azimuth_deg": az,
            "shadow_frac_of_valid": float(R["shadow"][np.isfinite(Z0)].mean()),
            "unusable_frac_of_valid": float((~np.isfinite(R["sigma_z"]))[np.isfinite(Z0)].mean()),
            "sigma_z_med_m": float(np.nanmedian(R["sigma_z"])),
            "sigma_z_p95_m": float(np.nanpercentile(R["sigma_z"], 95)) if np.isfinite(R["sigma_z"]).any() else None,
            "r_ref": R["r_ref"],
            "refl_med_flat": float(np.median(R["refl"][np.isfinite(Z0) & ~R["shadow"]])),
        }
        print(f"[render] {key}: shadow {geom_meta[key]['shadow_frac_of_valid']:.1%}, "
              f"sigma_z med {geom_meta[key]['sigma_z_med_m']:.2f} m "
              f"p95 {geom_meta[key]['sigma_z_p95_m']:.2f} m", flush=True)

    # NOISE-ONLY CONTROL arm: photometric height noise at geometry (65, 90)
    # but WITHOUT cast/self-shadow removal and without the unusable rule —
    # isolates the noise pathway from the shadow-voiding pathway.
    inc, az = 65.0, 90.0
    Rn = render_geometry(Z0, args.grid_spacing, inc, az, HAPKE_PARAMS,
                         sigma0=args.sigma0, sigma_max=args.sigma_max)
    sig_only = np.where(np.isfinite(Z0),
                        np.minimum(args.sigma0 * np.sqrt(Rn["r_ref"] /
                                  np.maximum(Rn["refl"], 1e-3 * Rn["r_ref"])),
                                  args.sigma_max),
                        np.nan)
    rng = np.random.default_rng([args.seed, 651, 659])  # stream distinct from geometry arms
    arms["noiseonly_i65"] = Z0 + sig_only * rng.normal(0.0, 1.0, size=Z0.shape)
    geom_meta["noiseonly_i65"] = {
        "incidence_deg": inc, "azimuth_deg": az,
        "shadow_frac_of_valid": 0.0,  # by construction
        "unusable_frac_of_valid": 0.0,
        "sigma_z_med_m": float(np.nanmedian(sig_only)),
        "sigma_z_p95_m": float(np.nanpercentile(sig_only, 95)),
        "r_ref": Rn["r_ref"], "refl_med_flat": None,
        "note": "noise-only control (no shadow voiding, no unusable rule)",
    }
    print(f"[render] noiseonly_i65 (control): sigma_z med "
          f"{geom_meta['noiseonly_i65']['sigma_z_med_m']:.2f} m, "
          f"p95 {geom_meta['noiseonly_i65']['sigma_z_p95_m']:.2f} m", flush=True)

    # sensitivity arms: extra w values at geometry (65, 90)
    sens_meta = {}
    for w_val in args.sensitivity_w:
        p2 = dict(HAPKE_PARAMS)
        p2["w"] = w_val
        inc, az = 65.0, 90.0
        R = render_geometry(Z0, args.grid_spacing, inc, az, p2,
                            sigma0=args.sigma0, sigma_max=args.sigma_max)
        key = f"w{w_val:g}_i65_az90"
        rng = np.random.default_rng([args.seed, int(inc), int(az)])
        noise = rng.normal(0.0, 1.0, size=Z0.shape)
        arms[key] = Z0 + np.where(np.isfinite(R["sigma_z"]), R["sigma_z"] * noise, np.nan)
        sens_meta[key] = {"w": w_val, "geometry": [inc, az],
                          "sigma_z_med_m": float(np.nanmedian(R["sigma_z"])),
                          "shadow_frac_of_valid": float(R["shadow"][np.isfinite(Z0)].mean())}
        print(f"[render] {key} (sensitivity): sigma_z med "
              f"{sens_meta[key]['sigma_z_med_m']:.2f} m", flush=True)

    # ---- paired ladder re-run --------------------------------------------
    from scipy.ndimage import zoom
    rows = []
    cal_masks = {}
    for arm_name, Zarm in arms.items():
        print(f"\n--- arm {arm_name} ---", flush=True)
        for r in sorted(set(args.rungs)):
            if abs(r - args.grid_spacing) < 1e-9:
                Zr, _ = Zarm.copy(), None
            else:
                Zr, _ = resample(Zarm, tr0, args.grid_spacing, r, method="average")
            ny_r, nx_r = Zr.shape
            truth_r = zoom(gt.astype(np.float32), (ny_r / ny, nx_r / nx),
                           order=0).astype(bool) if (nx_r, ny_r) != (nx, ny) else gt
            if r in cal_masks:  # fixed split from baseline arm's score surface
                cal_mask, test_mask = cal_masks[r]
            else:
                # build the split exactly as sag_detect does (seed 42) on the
                # BASELINE arm's finite-score cells, then freeze it for all arms
                score_proxy = np.isfinite(Zr)  # superset of finite-score cells
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
            print(f"[rung {r:g} m] F1={m['f1_test']:.3f} (+slope {m['f1_test_slope']:.3f}), "
                  f"P={m['precision_test']:.3f}, R={m['recall_test']:.3f}, "
                  f"valid {m['valid_frac']:.2%}", flush=True)

    df = pd.DataFrame(rows)
    csv_path = args.repo_outdir / "hapke_f1_comparison.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[out ] comparison table -> {csv_path}", flush=True)

    # ---- headline deltas (per rung: baseline vs each geometry) ------------
    base = df[df.arm == "baseline"].set_index("res_m")
    deltas = {}
    for key in [k for k in arms if k != "baseline"]:
        sub = df[df.arm == key].set_index("res_m")
        deltas[key] = {
            float(r): {
                "f1_test_slope_base": float(base.loc[r, "f1_test_slope"]),
                "f1_test_slope_hapke": float(sub.loc[r, "f1_test_slope"]),
                "delta_f1_slope": float(sub.loc[r, "f1_test_slope"] - base.loc[r, "f1_test_slope"]),
                "f1_test_base": float(base.loc[r, "f1_test"]),
                "f1_test_hapke": float(sub.loc[r, "f1_test"]),
                "delta_f1": float(sub.loc[r, "f1_test"] - base.loc[r, "f1_test"]),
            } for r in sorted(set(args.rungs))
        }
    max_abs_delta = max(abs(v["delta_f1_slope"]) for arm in deltas.values()
                       for v in arm.values())
    null_result = bool(max_abs_delta < 0.02)

    # ---- render preview grid ---------------------------------------------
    n_geom = len(geoms)
    fig, axes = plt.subplots(3, max(4, n_geom // 3), figsize=(3.2 * max(4, n_geom // 3), 10),
                             squeeze=False)
    for idx, (inc, az) in enumerate(geoms):
        key = f"i{inc:g}_az{az:g}"
        ax = axes.flat[idx]
        R = renders[key]
        show = np.where(~R["shadow"], R["refl"], np.nan)
        im = ax.imshow(show, cmap="gray", origin="lower")
        ax.set_title(f"i={inc:g} az={az:g}\nshadow "
                     f"{geom_meta[key]['shadow_frac_of_valid']:.0%}", fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    for idx in range(n_geom, axes.size):
        axes.flat[idx].axis("off")
    fig.suptitle("Hapke IMSA synthetic illumination — IndianTunnel_NorthSurface master "
                 f"(w={HAPKE_PARAMS['w']}, b={HAPKE_PARAMS['b']}, c={HAPKE_PARAMS['c']}, "
                 f"h={HAPKE_PARAMS['h']}, B0={HAPKE_PARAMS['B0']}; nadir view)")
    fig.tight_layout()
    fig_path = args.repo_outdir / "hapke_render_grid.png"
    fig.savefig(fig_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    print(f"[out ] render grid -> {fig_path}", flush=True)

    # ---- summary ----------------------------------------------------------
    summary = {
        "task": "13.3 (P1.4) Hapke synthetic-illumination re-render + ladder re-run",
        "source_npz": str(args.npz),
        "site": "IndianTunnel_NorthSurface (LLTB-1 ladder master)",
        "hapke_params": HAPKE_PARAMS,
        "hapke_notes": [
            "Standard IMSA (Hapke 1993; Hapke 2012 2nd ed. Ch. 8S); parameters are "
            "lunar-mare literature values, NOT fitted (analog re-render).",
            "theta_bar (macroscopic roughness) is NOT a parameter of IMSA; omitted "
            "and documented in METHODS.md.",
            "Opposition surge negligible at these phase angles (g = incidence >= 45 deg).",
        ],
        "noise_model": {
            "sigma0_m_at_reference": args.sigma0,
            "anchor": "Z2 TRANQPIT1 NAC DTM residual RMS 0.327 m (project measurement)",
            "scaling": "shot noise: sigma_z = sigma0 * sqrt(r_ref / r_cell)",
            "sigma_cap_m": args.sigma_max,
            "unusable_rule": "shadowed OR refl < 0.02*r_ref OR master NaN -> NoData",
            "seed": args.seed,
        },
        "geometry_grid": {"incidences_deg": args.incidences,
                          "azimuths_deg": args.azimuths,
                          "viewing": "nadir (e=0); phase g = map-plane incidence"},
        "protocol": {
            "gt": "FIXED from unperturbed cloud (sag_detect.cloud_ground_truth, 0.5 m, "
                  "thr 1.0 m) — not recomputed per arm (avoids label drift confounder)",
            "cal_test_split": "frozen from baseline arm finite cells, seed 42, reused "
                              "verbatim in every arm",
            "detector": "production sag_detect chain: PD fill + Frangi 30-300 m + "
                        "threshold tuning on cal + component filter >= 5 + fixed "
                        f"{args.slope_mask_degrees:g} deg slope mask",
            "rungs_m": sorted(set(args.rungs)),
            "honesty": [
                "Task-12 entrance-trench+skylight mask NOT used as sag ground truth "
                "(Task-12 GUARDRAILS).",
                "Reported separately from the v0.4 Section-8 site table.",
                "Regressions reported as-is; no re-tuning against the Hapke arms.",
            ],
        },
        "geometries": geom_meta,
        "sensitivity_arms": sens_meta,
        "f1_deltas_vs_baseline": deltas,
        "max_abs_delta_f1_slope": float(max_abs_delta),
        "null_result": null_result,
        "csv": str(csv_path),
        "renders_dir": str(args.repo_outdir),
        "raster_dir": str(args.raster_outdir),
        "render_grid_png": str(fig_path),
    }
    sum_path = args.repo_outdir / "hapke_summary.json"
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[out ] summary -> {sum_path}", flush=True)
    print(f"[done] max |delta F1(+slope)| = {max_abs_delta:.3f} "
          f"-> {'NULL RESULT (negligible photometric effect)' if null_result else 'material effect — see CSV'}",
          flush=True)


if __name__ == "__main__":
    main()
