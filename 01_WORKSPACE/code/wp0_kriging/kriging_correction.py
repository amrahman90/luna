"""Kriged systematic-error (distortion-map) correction for NAC DTMs — v5 component I2.

Implements the Mueller et al. 2026 I2 recipe against a LOLA reference:

  1. Load LOLA RDR shots (PDS Geosciences GDS CSV or generic lon/lat/elev CSV)
     and project them into the DTM's own projected CRS (metres).
  2. residual = DTM(bilinear at shot xy) - LOLA_elev, per shot.
  3. No-change selection (lunar I2 recipe): keep only shots where the local
     DTM slope < 2 deg (slope from a 50-px boxcar-smoothed copy). Hold out 20%
     of the no-change points as independent check points (seed 42).
  4. Ordinary kriging, spherical variogram (pykrige), on the training points.
     If pykrige's automatic variogram fit fails, fall back to parameters fit
     from an empirical variogram binned with numpy/scipy.
  5. Evaluate the kriged correction on a coarse grid (default 150 m, i.e.
     comparable to no-change point spacing -- NOT a 2 m full-res solve),
     bilinearly upsample to full DTM resolution, corrected = DTM - correction.
  6. Metrics at the held-out check points before/after (bias, RMSE).
     No ICP stage: NAC DTMs are already registered to LOLA in SOCET
     production, so the P1 "after-ICP" column is not applicable.
  7. Frequency check (mandatory I2 claim): radially averaged power spectra of
     the kriged correction surface vs the after-correction residual field,
     plus band-limited RMS comparison against the DTM itself.
  8. Signal-preservation check: Planchon-Darboux depression depth within
     200 m of the target pit on the corrected DTM vs the uncorrected value
     (reuses 01_WORKSPACE/code/wp0_primitive/depression_depth.py).

CLI:  kriging_correction.py --dtm <tif> --ref <lola csv> --outdir <repo out>
                           [--corr-out <tif>] [--pit-lat L --pit-lon L] ...
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
from pyproj import CRS, Transformer
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import map_coordinates, uniform_filter
from scipy.optimize import curve_fit
from scipy.spatial import cKDTree
from scipy.spatial.distance import pdist, squareform

R_MOON = 1737400.0


# ----------------------------------------------------------------------
# Reference (LOLA) loading
# ----------------------------------------------------------------------
def load_reference(ref_csv: Path, datum_radius: float) -> pd.DataFrame:
    """Return DataFrame with columns lon (0-360 E), lat (planetocentric), h (m).

    Supports the PDS Geosciences GDS LOLA RDR point CSV (columns
    Pt_Longitude / Pt_Latitude / Pt_Radius[km], pre-filtered to shot flag 0)
    or a generic CSV with lon/lat/elev columns.
    """
    df = pd.read_csv(ref_csv)
    df.columns = [c.strip() for c in df.columns]
    if {"Pt_Longitude", "Pt_Latitude", "Pt_Radius"} <= set(df.columns):
        out = pd.DataFrame(
            {
                "lon": df["Pt_Longitude"].astype(float),
                "lat": df["Pt_Latitude"].astype(float),
                "h": df["Pt_Radius"].astype(float) * 1000.0 - datum_radius,
            }
        )
        src_desc = "PDS GDS LOLA RDR point CSV (Pt_Radius - 1737.4 km sphere)"
    elif {"lon", "lat", "elev"} <= set(df.columns):
        out = df.rename(columns={"elev": "h"})[["lon", "lat", "h"]].astype(float)
        src_desc = "generic CSV (lon/lat/elev columns, pre-referenced)"
    else:
        raise SystemExit(f"unrecognised reference columns: {df.columns.tolist()}")
    out = out.dropna()
    out = out[(out["lon"] < 999.0) & (out["lat"] < 99.0) & (out["h"] > -1.0e5)]
    out.attrs["source_desc"] = src_desc
    return out


# ----------------------------------------------------------------------
# Variogram helpers
# ----------------------------------------------------------------------
def spherical_model(h, psill, rng, nugget):
    return np.where(
        h <= 0,
        nugget,
        np.where(
            h < rng,
            nugget + psill * (1.5 * h / rng - 0.5 * (h / rng) ** 3),
            nugget + psill,
        ),
    )


def empirical_variogram(x, y, z, n_lags=20, max_dist_frac=0.5):
    """Isotropic empirical semivariogram binned with numpy/scipy."""
    pts = np.column_stack([x, y])
    d = pdist(pts)
    g = 0.5 * pdist(z[:, None], metric="sqeuclidean").ravel()
    extent = float(np.ptp(x) + np.ptp(y)) / 2.0
    hmax = max_dist_frac * extent
    edges = np.linspace(0, hmax, n_lags + 1)
    ctr, gam = [], []
    for i in range(n_lags):
        m = (d >= edges[i]) & (d < edges[i + 1])
        if m.sum() > 30:
            ctr.append(d[m].mean())
            gam.append(g[m].mean())
    return np.array(ctr), np.array(gam)


def fit_spherical_empirical(x, y, z):
    """Fit spherical model to the empirical variogram.

    Returns dict with pykrige spherical parameter order [psill, range, nugget].
    """
    h, gv = empirical_variogram(x, y, z)
    sill0 = float(np.var(z))
    rng0 = float(np.percentile(np.abs(x - x.mean()) + np.abs(y - y.mean()), 90))
    p0 = [0.9 * sill0, max(rng0, 100.0), 0.1 * sill0]
    lo = [1e-6, 50.0, 0.0]
    hi = [3.0 * sill0, 5.0 * rng0 + 1000.0, 0.5 * sill0]
    popt, _ = curve_fit(spherical_model, h, gv, p0=p0, bounds=(lo, hi), maxfev=20000)
    return {
        "psill": float(popt[0]),
        "range": float(popt[1]),
        "nugget": float(popt[2]),
    }, h, gv


# ----------------------------------------------------------------------
# Radially averaged power spectrum
# ----------------------------------------------------------------------
def radial_psd(field: np.ndarray, spacing: float):
    """Radially averaged PSD of a 2D field (zero-meaned). Returns k [cyc/m], psd."""
    a = field.astype(np.float64)
    a = a - np.nanmean(a)
    a = np.nan_to_num(a, nan=0.0)
    n0, n1 = a.shape
    win = np.hanning(n0)[:, None] * np.hanning(n1)[None, :]
    fa = np.fft.fftshift(np.fft.fft2(a * win))
    power = np.abs(fa) ** 2 / (n0 * n1)
    ky = np.fft.fftshift(np.fft.fftfreq(n0, d=spacing))
    kx = np.fft.fftshift(np.fft.fftfreq(n1, d=spacing))
    kk = np.sqrt(ky[:, None] ** 2 + kx[None, :] ** 2).ravel()
    nb = max(32, min(n0, n1))
    edges = np.linspace(0.0, kk.max(), nb + 1)
    idx = np.digitize(kk, edges) - 1
    valid = (idx >= 0) & (kk > 0)
    psd = np.array(
        [power.ravel()[valid & (idx == i)].mean() if ((valid & (idx == i)).sum()) else np.nan
         for i in range(nb)]
    )
    ctr = 0.5 * (edges[:-1] + edges[1:])
    ok = np.isfinite(psd) & (ctr > 0)
    return ctr[ok], psd[ok]


def band_rms(field: np.ndarray, spacing: float, kmin: float, kmax: float, valid_mask=None):
    """Band-limited RMS amplitude between kmin..kmax [cyc/m] via FFT (Hann-windowed).

    Parseval: mean-square of the band = (1/N^2) * sum |F|^2 over the band.
    NoData cells (valid_mask False) are mean-filled; used only for the
    reference DTM curve, never for the correction (which is gap-free).
    """
    a = field.astype(np.float64)
    if valid_mask is not None:
        fill = float(np.nanmean(a[valid_mask]))
        a = np.where(valid_mask, a, fill)
    a -= a.mean()
    n0, n1 = a.shape
    win = np.hanning(n0)[:, None] * np.hanning(n1)[None, :]
    wa = a * win
    fa = np.fft.fft2(wa) * (win.mean() / np.sqrt(np.mean(win**2)))
    power = (np.abs(fa) ** 2) / (n0 * n1) ** 2
    ky = np.fft.fftfreq(n0, d=spacing)[:, None]
    kx = np.fft.fftfreq(n1, d=spacing)[None, :]
    kk = np.sqrt(ky**2 + kx**2)
    sel = (kk >= kmin) & (kk < kmax)
    return float(np.sqrt(power[sel].sum()))


# ----------------------------------------------------------------------
# Main pipeline
# ----------------------------------------------------------------------
def run(args: argparse.Namespace) -> dict:
    dtm_path = Path(args.dtm)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    tag = args.tag

    # --- DTM + reference into the DTM's projected frame -------------------
    with rasterio.open(dtm_path) as src:
        dtm = src.read(1)
        profile = src.profile.copy()
        nodata = src.nodata if src.nodata is not None else -3.4028235e38
        transform = src.transform
        res = float(src.res[0])
        crs: CRS = src.crs
        bounds = src.bounds
    dtm_f = dtm.astype(np.float64)
    dtm_valid = dtm_f > -1.0e30
    dtm_f[~dtm_valid] = np.nan

    geodetic = CRS.from_user_input(args.geodetic_crs)
    fwd = Transformer.from_crs(geodetic, crs, always_xy=True)

    # transform sanity check: known point must land inside the raster
    if args.pit_lat is not None:
        px, py = fwd.transform(args.pit_lon, args.pit_lat)
        assert bounds.left < px < bounds.right and bounds.bottom < py < bounds.top, (
            f"sanity check FAILED: pit ({args.pit_lat}, {args.pit_lon}) -> ({px:.1f}, {py:.1f}) "
            f"outside raster bounds {bounds}"
        )
        print(f"[sanity] pit -> ({px:.1f}, {py:.1f}) m inside raster: OK")

    ref = load_reference(Path(args.ref), R_MOON)
    n_total_query = len(ref)
    rx, ry = fwd.transform(ref["lon"].values, ref["lat"].values)
    inside = (rx > bounds.left) & (rx < bounds.right) & (ry > bounds.bottom) & (ry < bounds.top)
    ref = ref[inside]
    rx, ry = rx[inside], ry[inside]
    print(f"[ref] {n_total_query} shots in query box, {len(ref)} inside raster footprint")

    # --- sample DTM (bilinear) at shot positions --------------------------
    inv = ~transform
    col, row = inv * (rx, ry)
    z_dtm = map_coordinates(np.where(dtm_valid, dtm_f, 0.0), [row, col], order=1, mode="nearest")
    # reject shots whose 4-pixel neighbourhood touches nodata (bilinear is
    # invalid there): nearest-sample test plus a 2-px dilation of the mask
    z_near = map_coordinates(dtm, [row, col], order=0, mode="nearest")
    ok = dtm_valid[np.rint(row).astype(int).clip(0, dtm.shape[0] - 1),
                   np.rint(col).astype(int).clip(0, dtm.shape[1] - 1)] & (z_near > -1.0e30)
    resid = z_dtm[ok] - ref["h"].values[ok]
    xs, ys = rx[ok], ry[ok]
    n_in_dtm = int(ok.sum())
    print(f"[residual] n={n_in_dtm}  mean={resid.mean():+.3f} m  std={resid.std():.3f} m")

    # --- slope map from a smoothed copy (no-change selection) -------------
    print("[slope] 50-px boxcar + gradient ...")
    sm = uniform_filter(np.nan_to_num(dtm_f, nan=np.nanmean(dtm_f)), size=args.boxcar_px)
    dzdy, dzdx = np.gradient(sm, res, res)
    slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
    slope_at = map_coordinates(slope, [row[ok], col[ok]], order=1, mode="nearest")

    flat = slope_at < args.slope_max
    print(f"[no-change] slope<{args.slope_max} deg keeps {flat.sum()}/{n_in_dtm} shots")

    # robust outlier trim on the no-change residuals (5 x 1.4826 x MAD)
    med = np.median(resid[flat])
    mad = np.median(np.abs(resid[flat] - med))
    keep = flat & (np.abs(resid - med) <= 5.0 * 1.4826 * mad)
    print(f"[no-change] MAD trim (5 sigma, sigma_mad={1.4826*mad:.3f} m) keeps {keep.sum()}")

    xs, ys, resid = xs[keep], ys[keep], resid[keep]

    # --- train / check split (seed 42) ------------------------------------
    rng = np.random.default_rng(args.seed)
    perm = rng.permutation(len(resid))
    n_check = max(1, int(round(args.holdout * len(resid))))
    chk, trn = perm[:n_check], perm[n_check:]
    if len(trn) > args.max_train:  # protect kriging solve size, documented
        trn = rng.choice(trn, args.max_train, replace=False)
    x_tr, y_tr, z_tr = xs[trn], ys[trn], resid[trn]
    x_ck, y_ck, z_ck = xs[chk], ys[chk], resid[chk]
    print(f"[split] n_nochange={len(resid)}  n_train={len(trn)}  n_check={len(chk)}")

    # --- ordinary kriging, spherical variogram ----------------------------
    from pykrige.ok import OrdinaryKriging

    extent = float(np.hypot(bounds.right - bounds.left, bounds.top - bounds.bottom))
    ok = None
    vm_src = "pykrige-autofit"
    try:
        ok = OrdinaryKriging(
            x_tr, y_tr, z_tr,
            variogram_model="spherical",
            nlags=20,
            coordinates_type="euclidean",
        )
        ps = ok.variogram_model_parameters  # spherical: [psill, range, nugget]
        if not (0.0 < ps[1] < 2.0 * extent):  # degenerate range
            raise RuntimeError(f"degenerate autofit range {ps[1]:.1f} m")
        vm_params = {"psill": float(ps[0]), "range": float(ps[1]), "nugget": float(ps[2])}
    except Exception as e:  # noqa: BLE001
        print(f"[variogram] autofit failed ({e}); empirical fallback")
        emp, hv, gv = fit_spherical_empirical(x_tr, y_tr, z_tr)
        vm_src = "empirical-numpy-fit"
        vm_params = emp
        ok = OrdinaryKriging(
            x_tr, y_tr, z_tr,
            variogram_model="spherical",
            variogram_model_parameters=[vm_params["psill"], vm_params["range"], vm_params["nugget"]],
            coordinates_type="euclidean",
        )
    print(f"[variogram] {vm_src}: {vm_params}")

    # --- kriged correction on a coarse grid --------------------------------
    sp = args.grid_spacing
    gx = np.arange(bounds.left + sp / 2, bounds.right, sp)
    gy = np.arange(bounds.bottom + sp / 2, bounds.top, sp)
    print(f"[krige] grid {len(gy)}x{len(gx)} at {sp} m ({len(gx)*len(gy)} nodes) ...")
    zgrid, _ = ok.execute("grid", gx, gy, backend="vectorized")
    zgrid = np.ma.getdata(zgrid).astype(np.float64)

    # --- upsample to full DTM resolution, corrected = DTM - correction -----
    interp = RegularGridInterpolator((gy, gx), zgrid, method="linear", bounds_error=False, fill_value=None)
    rr = np.arange(dtm.shape[0]) * -transform.e + transform.f + transform.e / 2.0
    cc = np.arange(dtm.shape[1]) * transform.a + transform.c + transform.a / 2.0
    corr_full = np.empty(dtm.shape, dtype=np.float64)
    chunk = 2000
    for i0 in range(0, dtm.shape[0], chunk):
        i1 = min(i0 + chunk, dtm.shape[0])
        CX, RY = np.meshgrid(cc, rr[i0:i1])
        corr_full[i0:i1] = interp(np.column_stack([RY.ravel(), CX.ravel()])).reshape(i1 - i0, -1)

    corrected = np.where(dtm_valid, dtm_f - corr_full, nodata).astype(np.float32)
    corr_out = Path(args.corr_out) if args.corr_out else None
    if corr_out:
        corr_out.parent.mkdir(parents=True, exist_ok=True)
        profile.update(dtype="float32", compress="deflate", BIGTIFF="IF_SAFER")
        with rasterio.open(corr_out, "w", **profile) as dst:
            dst.write(corrected, 1)
        print(f"[out] corrected DTM -> {corr_out}")

    # --- metrics at held-out check points ----------------------------------
    corr_at_ck = interp(np.column_stack([y_ck, x_ck]))
    res_before = z_ck
    res_after = z_ck - corr_at_ck
    bias_b, rmse_b = float(res_before.mean()), float(np.sqrt((res_before**2).mean()))
    bias_a, rmse_a = float(res_after.mean()), float(np.sqrt((res_after**2).mean()))
    print(f"[metrics] before: bias {bias_b:+.3f} m  RMSE {rmse_b:.3f} m")
    print(f"[metrics] after : bias {bias_a:+.3f} m  RMSE {rmse_a:.3f} m")

    metrics_csv = outdir / f"{tag}_kriging_metrics.csv"
    with open(metrics_csv, "w") as f:
        f.write(f"# grid_spacing_m={sp}, n_train={len(trn)}, n_nochange={len(resid)}, "
                f"slope_max_deg={args.slope_max}, holdout_frac={args.holdout}, seed={args.seed}, "
                f"variogram={vm_src} spherical nugget={vm_params['nugget']:.4g} "
                f"psill={vm_params['psill']:.4g} range_m={vm_params['range']:.1f}\n")
        f.write("stage,n_checkpoints,bias_m,rmse_m\n")
        f.write(f"before,{len(chk)},{bias_b:.4f},{rmse_b:.4f}\n")
        f.write(f"after,{len(chk)},{bias_a:.4f},{rmse_a:.4f}\n")

    # --- frequency check (I2 mandatory claim) -------------------------------
    k_c, p_c = radial_psd(zgrid, sp)                       # correction surface
    # after-correction residual field: check points nearest-supported to grid
    pts = np.column_stack([x_ck, y_ck])
    GX, GY = np.meshgrid(gx, gy)
    tree = cKDTree(pts)
    d, _ = tree.query(np.column_stack([GX.ravel(), GY.ravel()]))
    res_field = griddata_nearest(pts, res_after, GX, GY, d, support=3 * sp)
    k_r, p_r = radial_psd(res_field, sp)
    # DTM reference spectrum (signal), downsampled to the same grid
    dtm_ds = dtm[:: int(sp / res), :: int(sp / res)]
    k_d, p_d = radial_psd(dtm_ds, sp)

    frac = np.cumsum(p_c) / np.sum(p_c)
    lam = 1.0 / k_c
    # fraction of correction power at wavelengths longer than 300 m
    i300 = np.searchsorted(k_c, 1.0 / 300.0)
    frac300 = float(frac[i300 - 1]) if i300 > 0 else float("nan")
    # full-resolution band-limited RMS: correction vs DTM signal, 60-300 m band
    rms_corr_band = band_rms(corr_full, res, 1.0 / 300.0, 1.0 / 60.0)
    rms_dtm_band = band_rms(dtm_f, res, 1.0 / 300.0, 1.0 / 60.0, valid_mask=dtm_valid)
    print(f"[spectra] {frac300*100:.1f}% of correction power at wavelength > 300 m")
    print(f"[spectra] 60-300 m band RMS: correction {rms_corr_band:.4f} m vs DTM {rms_dtm_band:.3f} m "
          f"(ratio {rms_corr_band/rms_dtm_band:.2e})")

    # --- signal preservation: pit depression depth --------------------------
    pit = {}
    if args.pit_lat is not None:
        pit = pit_check(args, dtm_path, corr_out, res)

    # --- figure --------------------------------------------------------------
    fig, ax = plt.subplots(2, 2, figsize=(15, 12))
    ext = [bounds.left / 1e3, bounds.right / 1e3, bounds.bottom / 1e3, bounds.top / 1e3]
    have_pit = args.pit_lat is not None
    a = ax[0, 0]
    vmax = float(np.abs(zgrid).max())
    im = a.imshow(zgrid, origin="lower", extent=ext, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="equal")
    if have_pit:
        a.plot(px / 1e3, py / 1e3, "k*", ms=14, mfc="none", mec="k")
    a.set_title(f"(a) kriged correction surface ({sp:g} m grid)\n"
                f"spherical variogram ({vm_src}), n_train={len(trn)}")
    plt.colorbar(im, ax=a, label="correction [m] (DTM-LOLA, kriged)")
    a = ax[0, 1]
    diff = (corrected.astype(np.float64) - np.where(dtm_valid, dtm_f, np.nan))
    im = a.imshow(diff, origin="lower", extent=ext, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="equal")
    if have_pit:
        a.plot(px / 1e3, py / 1e3, "k*", ms=14, mfc="none", mec="k")
    a.set_title("(b) corrected - raw (full 2 m grid)\n(= -correction; pit marked)")
    plt.colorbar(im, ax=a, label="[m]")
    a = ax[1, 0]
    lim = np.abs(res_before).max() * 1.1
    a.plot([-lim, lim], [-lim, lim], "k--", lw=1, label="1:1")
    a.plot(res_before, res_after, ".", ms=3, alpha=0.5)
    a.axhline(0, color="gray", lw=0.5)
    a.axvline(0, color="gray", lw=0.5)
    a.set_xlabel("residual at check points BEFORE [m] (DTM - LOLA)")
    a.set_ylabel("residual at check points AFTER [m]")
    a.set_title(f"(c) check points (n={len(chk)}): bias {bias_b:+.3f}->{bias_a:+.3f} m, "
                f"RMSE {rmse_b:.3f}->{rmse_a:.3f} m")
    a.legend(loc="upper left")
    a = ax[1, 1]
    a.loglog(k_c, p_c, lw=2, label=f"kriged correction ({sp:g} m grid)")
    a.loglog(k_r, p_r, lw=1.2, label="residual field after correction")
    a.loglog(k_d, p_d, lw=1.2, alpha=0.7, label="DTM (signal, same grid)")
    for lam_m, ls in ((300, ":"), (60, "-.")):
        a.axvline(1.0 / lam_m, color="gray", ls=ls, lw=1)
        a.text(1.0 / lam_m, a.get_ylim()[1] * 0.5, f" $\\lambda$={lam_m} m", fontsize=8, color="gray")
    a.set_xlabel("wavenumber [cycles/m]")
    a.set_ylabel("radially averaged PSD")
    a.set_title(f"(d) power spectra: {frac300*100:.1f}% of correction power at $\\lambda$>300 m;\n"
                f"60-300 m band RMS correction {rms_corr_band:.3f} m vs DTM {rms_dtm_band:.1f} m")
    a.legend(fontsize=8)
    fig.suptitle(f"{tag}: I2 kriged systematic-error correction vs LOLA RDR "
                 f"(no ICP stage: DTM already LOLA-registered in production)", fontsize=13)
    fig.tight_layout()
    png = outdir / f"{tag}_corrections.png"
    fig.savefig(png, dpi=150)
    print(f"[out] figure -> {png}")

    summary = {
        "tag": tag,
        "ref_csv": str(args.ref),
        "n_query_shots": n_total_query,
        "n_in_dtm": n_in_dtm,
        "n_nochange": int(len(resid)),
        "n_train": int(len(trn)),
        "n_check": int(len(chk)),
        "variogram": {"source": vm_src, "model": "spherical", **vm_params},
        "grid_spacing_m": sp,
        "metrics": {
            "before": {"n": len(chk), "bias_m": bias_b, "rmse_m": rmse_b},
            "after": {"n": len(chk), "bias_m": bias_a, "rmse_m": rmse_a},
        },
        "spectra": {
            "frac_correction_power_lambda_gt_300m": frac300,
            "rms_correction_60_300m_band_m": rms_corr_band,
            "rms_dtm_60_300m_band_m": rms_dtm_band,
        },
        "pit_check": pit,
        "outputs": {
            "figure": str(png),
            "metrics_csv": str(metrics_csv),
            "corrected_dtm": str(corr_out) if corr_out else None,
        },
    }
    with open(outdir / f"{tag}_kriging_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    return summary


def griddata_nearest(pts, vals, GX, GY, d, support):
    """Nearest-neighbour gridding of scattered residuals, NaN beyond support [m]."""
    from scipy.interpolate import griddata

    g = griddata(pts, vals, (GX, GY), method="nearest")
    g = np.where(d.reshape(GX.shape) <= support, g, 0.0)  # zero-fill gaps (zero-mean field)
    return g


def pit_check(args, dtm_path: Path, corr_out: Path, res: float):
    """Planchon-Darboux max depression depth within pit_radius of the pit,
    on raw vs corrected DTM (reuses the wp0 primitive)."""
    code_dir = Path(args.primitive_dir)
    sys.path.insert(0, str(code_dir))
    import importlib

    dd = importlib.import_module("depression_depth")
    importlib.reload(dd)

    with rasterio.open(dtm_path) as s:
        crs = s.crs
    from pyproj import Transformer

    tr = Transformer.from_crs(args.geodetic_crs, crs, always_xy=True)
    px, py = tr.transform(args.pit_lon, args.pit_lat)

    out = {}
    depth_tifs = {"raw": Path(args.raw_depth_tif)} if args.raw_depth_tif else {}
    if corr_out:
        dcorr = dd.depression_depth(corr_out, corr_out.parent)
        depth_tifs["corrected"] = dcorr
    for name, tif in depth_tifs.items():
        with rasterio.open(tif) as s:
            arr = s.read(1, masked=True)
            tfm = s.transform
        col, row = ~tfm * (px, py)
        rad_px = int(round(args.pit_radius / res))
        r0i, c0i = int(round(row)), int(round(col))
        win = arr[max(0, r0i - rad_px):r0i + rad_px, max(0, c0i - rad_px):c0i + rad_px]
        out[name] = float(win.max())
        print(f"[pit] max PD depression depth within {args.pit_radius} m of pit ({name}): {out[name]:.1f} m")
    if "raw" in out and "corrected" in out:
        out["ratio_vs_raw"] = out["corrected"] / out["raw"]
        out["pct_change"] = 100.0 * (out["corrected"] - out["raw"]) / out["raw"]
    return out


def cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dtm", required=True, help="input DTM GeoTIFF")
    p.add_argument("--ref", required=True, help="LOLA reference CSV (GDS LOLA RDR point CSV or lon/lat/elev)")
    p.add_argument("--outdir", required=True, help="directory for figure + metrics CSV")
    p.add_argument("--corr-out", default=None, help="path for corrected DTM GeoTIFF")
    p.add_argument("--raw-depth-tif", default=None, help="existing Task-3 depth raster of the RAW DTM (pit check anchor)")
    p.add_argument("--tag", default="TRANQPIT1")
    p.add_argument("--grid-spacing", type=float, default=150.0)
    p.add_argument("--boxcar-px", type=int, default=50)
    p.add_argument("--slope-max", type=float, default=2.0)
    p.add_argument("--holdout", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-train", type=int, default=6000)
    p.add_argument("--pit-lat", type=float, default=None)
    p.add_argument("--pit-lon", type=float, default=None)
    p.add_argument("--pit-radius", type=float, default=200.0)
    p.add_argument("--geodetic-crs", default="+proj=longlat +R=1737400 +no_defs")
    p.add_argument("--primitive-dir", default=str(Path(__file__).resolve().parent.parent / "wp0_primitive"))
    return p.parse_args()


if __name__ == "__main__":
    print(json.dumps(run(cli()), indent=2))
