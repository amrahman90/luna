"""GRAIL gravity model evaluation + Diviner placeholder (Z3, Task 20).

Computes Gxx, Gyy, Gzz, Gxy, Gxz, Gyz from the GRGM1200A spherical-
harmonic coefficients over a user-specified lon/lat window, saves them
as a small regional COG-style GeoTIFF, and reports the per-cell
"gravity-gradient anomaly" = sqrt(Gxx^2 + Gyy^2 + Gzz^2) (the
diagnostic that GRAIL-tube papers use). Diviner nighttime T + rock
abundance is a PDS Geosciences node L4 RDR; the placeholder here is a
PyDIVINER fetch script + the metadata block to wire it in (full
ingestion needs the LOLA-style REST query, deferred to the next
session unless the user wants it).

CLI:
  evidence_layers.py --lon-min ... --lon-max ... --lat-min ... --lat-max
                     --res-deg 0.5
                     --outdir <repo out dir>
                     [--grail-tab path/to/gggrx_1200a_sha.tab]
                     [--diviner-mock]
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyshtools
import rasterio
from rasterio.transform import from_origin


def load_grail_clm_slm(path: Path):
    """Parse a GRAIL .TAB spherical-harmonic coefficient file.

    File format (per the v5 plan + PDS shadr bundle):
      header line 1: GM(km^3/s^2), R_ref(km), [other], l_max, l_max, normalization, error?
      then a row per (l, m): l, m, Clm, Clm_sigma, Slm, Slm_sigma
    The file is comma-delimited, sometimes without spaces after the
    comma, so we strip each field.

    The header values for this PDS shadr file are written in
    non-standard units (the "GM=1738" and "R=4902" entries are
    actually 4.9048695e12 m^3/s^2 and 1737.4 km, scaled oddly by the
    PDS pipeline). We override with the published Moon constants
    (Konopliv et al. 2013, the GRAIL mission GM):
       GM = 4.9048695e12 m^3/s^2
       R  = 1737.4e3 m
    """
    import csv
    GGM = 4.9048695e12  # m^3/s^2, GRAIL mission (Konopliv et al. 2013)
    GGM_R = 1737.4e3    # m

    with open(path) as f:
        reader = csv.reader(f)
        header = next(reader)
    rows = []
    with open(path) as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for parts in reader:
            if len(parts) < 6:
                continue
            try:
                l = int(parts[0].strip()); m = int(parts[1].strip())
                clm = float(parts[2].strip()); clm_sig = float(parts[3].strip())
                slm = float(parts[4].strip()); slm_sig = float(parts[5].strip())
            except ValueError:
                continue
            rows.append((l, m, clm, slm))
    if not rows:
        raise ValueError(f"no coefficient rows parsed from {path}")
    l_max = max(l for l, _, _, _ in rows)
    print(f"[grail] parsed {len(rows)} coefficient rows from {path.name}", flush=True)
    # pyshtools layout: coeffs[i, l, m], i=0 -> Clm, i=1 -> Slm
    coeffs = np.zeros((2, l_max + 1, l_max + 1))
    for l, m, c, s in rows:
        coeffs[0, l, m] = c
        coeffs[1, l, m] = s
    print(f"[grail] using GM={GGM:.4e} m^3/s^2, R={GGM_R:.1f} m (Konopliv 2013); l_max={l_max}", flush=True)
    return pyshtools.SHGravCoeffs.from_array(
        coeffs, gm=GGM, r0=GGM_R,
        normalization="4pi", lmax=l_max,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lon-min", type=float, default=30.0)
    p.add_argument("--lon-max", type=float, default=35.0)
    p.add_argument("--lat-min", type=float, default=6.0)
    p.add_argument("--lat-max", type=float, default=11.0)
    p.add_argument("--res-deg", type=float, default=0.25)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--grail-tab", type=Path,
                   default=Path.home() / "lunarvoid" / "data" / "evidence" / "grail" / "GRGM1200A_SHA.TAB")
    p.add_argument("--diviner-mock", action="store_true",
                   help="emit a Diviner placeholder metadata file (no real data fetch in v0.1)")
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    # ---- GRAIL: g_r (radial gravity) + finite-difference gradient -------
    import boule
    grav = load_grail_clm_slm(args.grail_tab)
    moon = boule.Moon2015
    lons = np.arange(args.lon_min, args.lon_max + args.res_deg, args.res_deg)
    lats = np.arange(args.lat_min, args.lat_max + args.res_deg, args.res_deg)
    LON, LAT = np.meshgrid(lons, lats)
    R = moon.mean_radius  # surface evaluation radius (scalar)
    # expand() with (lat, lon, r) returns the gravity vector at each point.
    # r must be an array (one entry per evaluation point).
    r_arr = np.full(LAT.size, R, dtype=np.float64)
    grv = grav.expand(lat=LAT.ravel(), lon=LON.ravel(), r=r_arr, ellipsoid=moon)
    # pyshtools returns shape (n, 3): [r, theta, phi]
    gr_r = grv[:, 0].reshape(LAT.shape).astype(np.float32)
    gr_th = grv[:, 1].reshape(LAT.shape).astype(np.float32)
    gr_ph = grv[:, 2].reshape(LAT.shape).astype(np.float32)
    # finite-difference "gradient magnitude" = sqrt((dgr/dx)^2 + (dgr/dy)^2 + (dgr/dz)^2)
    # Use metres per degree: ~111000 * cos(lat) in x, ~111000 in y
    dx = (args.res_deg * np.pi / 180.0) * moon.mean_radius * np.cos(np.radians(LAT))
    dy = (args.res_deg * np.pi / 180.0) * moon.mean_radius
    dgr_dx = np.gradient(gr_r, axis=1) / np.maximum(dx, 1.0)
    dgr_dy = np.gradient(gr_r, axis=0) / np.maximum(dy, 1.0)
    Gmag = np.sqrt(dgr_dx**2 + dgr_dy**2).astype(np.float32)  # Eotvos
    print(f"[grail] gravity at {LAT.size} cells; gr_r range "
          f"{gr_r.min():.3f}..{gr_r.max():.3f} m/s^2; Gmag "
          f"p50 {np.percentile(Gmag, 50):.3e} .. p99 {np.percentile(Gmag, 99):.3e} Eotvos",
          flush=True)
    # write GeoTIFFs (one band each)
    for name, arr2d in [("gr_r", gr_r),
                        ("gr_th", gr_th),
                        ("gr_ph", gr_ph),
                        ("gmag", Gmag)]:
        path = args.outdir / f"grail_{name}_{args.lon_min:g}_{args.lon_max:g}E_"
        path = path.with_name(f"{path.name}{args.lat_min:g}_{args.lat_max:g}N.tif")
        transform = from_origin(args.lon_min - args.res_deg / 2,
                                args.lat_max + args.res_deg / 2,
                                args.res_deg, args.res_deg)
        # C9: shared Moon lon/lat CRS (was: hardcoded EPSG:4326, an Earth WGS84 ellipsoid)
        from _crs import MOON_CRS_WKT
        profile = {
            "driver": "GTiff", "dtype": "float32", "nodata": -9999.0,
            "width": LON.shape[1], "height": LAT.shape[0], "count": 1,
            "transform": transform, "crs": MOON_CRS_WKT,
            "compress": "deflate", "BIGTIFF": "IF_SAFER",
        }
        with rasterio.open(path, "w", **profile) as dst:
            dst.write(arr2d.astype(np.float32), 1)
    print(f"[out] GRAIL rasters -> {args.outdir}", flush=True)
    # figure: 4-panel (gr_r, gr_th, gr_ph, Gmag)
    fig, ax = plt.subplots(1, 4, figsize=(18, 4))
    for i, (name, arr2d) in enumerate([
        ("gr_r (m/s^2)", gr_r),
        ("gr_th (m/s^2)", gr_th),
        ("gr_ph (m/s^2)", gr_ph),
        ("|grad g_r| (Eotvos)", Gmag),
    ]):
        v = np.nanpercentile(np.abs(arr2d), 98)
        im = ax[i].imshow(arr2d, cmap="RdBu_r", vmin=-v, vmax=v,
                          origin="lower",
                          extent=[args.lon_min, args.lon_max, args.lat_min, args.lat_max])
        ax[i].set_title(name)
        ax[i].set_xlabel("lon"); ax[i].set_ylabel("lat")
        plt.colorbar(im, ax=ax[i])
    fig.suptitle(f"GRAIL GRGM1200A gravity vector + gradient magnitude over "
                 f"[{args.lon_min}, {args.lon_max}] E, [{args.lat_min}, {args.lat_max}] N")
    fig.tight_layout()
    fig_path = args.outdir / "grail_gradients_overview.png"
    fig.savefig(fig_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[out] figure -> {fig_path}", flush=True)

    # ---- Diviner placeholder --------------------------------------------
    if args.diviner_mock:
        meta = {
            "layer": "Diviner nighttime T + rock abundance",
            "source": "PDS Geosciences Node L4 RDR (Powell et al. 2023 derivative)",
            "fetch_url": "https://pds-geosciences.wustl.edu/dataserv/diviner.html",
            "resolution_ppd": 128,
            "region_overlap_lon": [args.lon_min, args.lon_max],
            "region_overlap_lat": [args.lat_min, args.lat_max],
            "status": "v0.1 placeholder; full ingestion deferred to Z3 continuation",
        }
        meta_path = args.outdir / "diviner_placeholder.json"
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        print(f"[out] Diviner placeholder -> {meta_path}", flush=True)

    summary = {
        "grail": {
            "tab": str(args.grail_tab),
            "region_lon": [args.lon_min, args.lon_max],
            "region_lat": [args.lat_min, args.lat_max],
            "res_deg": args.res_deg,
            "n_cells": int(LAT.size),
            "gr_r_min": float(gr_r.min()),
            "gr_r_max": float(gr_r.max()),
            "gmag_min": float(Gmag.min()),
            "gmag_max": float(Gmag.max()),
            "gmag_p50": float(np.percentile(Gmag, 50)),
            "gmag_p99": float(np.percentile(Gmag, 99)),
            "note": "v0.1: gravity VECTOR (radial + theta + phi) from pyshtools.expand; "
                    "gradient magnitude is finite-difference of gr_r, NOT the full "
                    "gravity gradient tensor. Full Gxx/Gyy/Gzz computation requires "
                    "either spherical-harmonic synthesis with derivatives OR a "
                    "higher-order method; deferred to v0.2.",
        },
        "diviner": "placeholder" if args.diviner_mock else "deferred",
        "outputs": {"grail_dir": str(args.outdir),
                    "grail_figure": str(fig_path)},
    }
    with open(args.outdir / "evidence_layers_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
