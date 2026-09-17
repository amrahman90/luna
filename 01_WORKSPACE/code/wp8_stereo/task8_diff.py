#!/usr/bin/env python3
"""LUNARVOID WP8 / Step 8.4 — compare reproduced ASP stereo DEMs against the
published NAC DTM for Mare Tranquillitatis (TRANQPIT1).

PASS criterion (ZEROCOST roadmap L401, WP0 scope-map spec): the 90th
percentile of the |difference| against the published DTM must be within
relat_le = 0.72 m.

Method (this is the Task-8 PASS/FAIL evidence; see JSON `method` notes):
  1. Each reproduced DEM is reprojected onto the published DTM's grid
     (rasterio.warp.reproject, bilinear, num_threads=1). CRS strings are
     taken from the file WKTs (published: local equirectangular
     +proj=eqc +lat_ts=8 +lon_0=180 +R=1737400; reproduced: ASP
     stereographic +proj=stere +lat_0=8.63508 +lon_0=33.2026 +R=1737400).
     NO EPSG assumptions (conventions skill section 3).
  2. Valid mask = both rasters valid at a pixel. Requires >= 10,000
     common pixels else the pair is reported INSUFFICIENT OVERLAP.
  3. RELATIVE comparison: a best-fit plane (a + b*x + c*y, least squares
     on the common pixels, coordinates centred and scaled to km) is fit
     to the difference and REMOVED before the percentile statistic.
     Absolute geolocation / vertical-datum offsets between an ASP
     bundle-adjusted product and a SOCET GXP product are not part of
     relative precision. Raw (no-plane-removed) median + std are also
     reported for transparency.
  4. Statistics on the plane-removed difference: median, std, 68th/90th/
     95th percentile of |diff|, max |diff|, N pixels.
  5. Verdict per pair: PASS if 90th percentile |plane-removed diff|
     <= 0.72 m (reported at 1 cm precision).
  6. Outputs per pair: GeoTIFF of the plane-removed difference on the
     published grid (windowed to the overlap bbox, grid-aligned), PNG
     histogram (dimensions verified programmatically), and a shared JSON
     summary with per-pair stats + verdicts.

CPU discipline: single-threaded throughout (thread env vars pinned
before numpy import; reproject num_threads=1). No multiprocessing.

Usage:
    task8_diff.py [--ref PATH] [dem_paths ...] [--all] [--out-dir DIR]
                  [--date YYYY-MM-DD] [--relat-le M] [--min-pixels N]

    --all  compares the three known TRANQPIT1 pair DEMs (missing ones
           are recorded as pending in the JSON).

Exit code 0 if all compared pairs PASS (or none compared); 1 if any
compared pair FAILS; 2 on usage/IO error.
"""

from __future__ import annotations

import os

# Pin threading BEFORE numpy import (CPU-light discipline; an overnight
# stereo job owns most cores).
for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "GDAL_NUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import argparse
import datetime as _dt
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import Resampling, reproject, transform_bounds
from rasterio.windows import Window, from_bounds

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REF = Path.home() / "lunarvoid/data/dtms/TRANQPIT1/NAC_DTM_TRANQPIT1.TIF"
DEFAULT_OUT_DIR = REPO_ROOT / "01_WORKSPACE/data/outputs/wp8_stereo"
CANONICAL_DIR = Path.home() / "lunarvoid/data/outputs/wp8_stereo"
DEFAULT_PAIRS = [
    ("pair1", Path.home() / "lunarvoid/stereo/TRANQPIT1/pair1_M152655237/run-DEM.tif"),
    ("pair2", Path.home() / "lunarvoid/stereo/TRANQPIT1/pair2_M152662021/run-DEM.tif"),
    ("pair3", Path.home() / "lunarvoid/stereo/TRANQPIT1/pair3_M137332905/run-DEM.tif"),
]
# Mare Tranquillitatis pit (Wagner & Robinson 2014; used ONLY as a geodesy
# sanity anchor — it must land inside the published DTM frame).
PIT_LONLAT = (33.222, 8.335)


def pair_id_from_path(path: Path, fallback: int) -> str:
    for part in reversed(path.parts):
        if part.lower().startswith("pair"):
            digits = "".join(ch for ch in part if ch.isdigit())
            if digits:
                return f"pair{digits}"
    return f"pair{fallback}"


def geodesy_sanity(ref: rasterio.io.DatasetReader) -> dict:
    """Confirm the known pit coordinate lands inside the reference DTM
    (conventions section 7: sanity-check geodesy before bulk stats)."""
    from pyproj import Transformer

    moon_geo = "+proj=longlat +R=1737400 +no_defs"
    tf = Transformer.from_crs(moon_geo, ref.crs, always_xy=True)
    x, y = tf.transform(PIT_LONLAT[0], PIT_LONLAT[1])
    row, col = ref.index(x, y)
    inside = 0 <= row < ref.height and 0 <= col < ref.width
    return {
        "pit_lon_deg_e": PIT_LONLAT[0],
        "pit_lat_deg": PIT_LONLAT[1],
        "map_x_m": float(x),
        "map_y_m": float(y),
        "ref_pixel_row_col": [int(row), int(col)],
        "inside_reference_dtm": bool(inside),
        "crs_route": "pyproj +proj=longlat +R=1737400 -> file WKT CRS",
    }


def compare_pair(
    pair: str,
    dem_path: Path,
    ref: rasterio.io.DatasetReader,
    relat_le: float,
    min_pixels: int,
    out_dir: Path,
    date: str,
) -> dict:
    rec: dict = {
        "status": None,
        "reproduced_dem": str(dem_path),
        "reproduced_crs_proj4": None,
        "n_common_px": 0,
    }

    with rasterio.open(dem_path) as src:
        rec["reproduced_crs_proj4"] = src.crs.to_proj4() if src.crs else None
        rec["reproduced_shape_wh"] = [src.width, src.height]
        rec["reproduced_nodata"] = src.nodata
        src_data = src.read(1)
        src_valid = np.isfinite(src_data) & (src_data != src.nodata)
        rec["reproduced_valid_frac_full_scene"] = round(
            float(src_valid.mean()), 4
        )
        src_transform, src_crs = src.transform, src.crs
        src_nodata = src.nodata
        src_bounds = src.bounds

        # Overlap window on the published grid (rounded outward, clipped):
        # integer pixel offsets keep the output exactly grid-aligned with
        # the published DTM (2 m cells, same CRS).
        tb = transform_bounds(src_crs, ref.crs, *src_bounds, densify_pts=41)
        fwin = from_bounds(tb[0], tb[1], tb[2], tb[3], ref.transform)
        win = Window(
            int(np.floor(fwin.col_off)),
            int(np.floor(fwin.row_off)),
            int(np.ceil(fwin.width)) + 1,
            int(np.ceil(fwin.height)) + 1,
        ).intersection(Window(0, 0, ref.width, ref.height))
        if win.width <= 0 or win.height <= 0:
            rec["status"] = "INSUFFICIENT OVERLAP"
            rec["note"] = (
                "reprojected reproduced-DEM footprint does not intersect "
                "the published DTM frame (possible geodesy/CRS problem)"
            )
            return rec
        dst_transform = ref.window_transform(win)

        ref_win = ref.read(1, window=win)
        dst = np.full((int(win.height), int(win.width)), np.nan, np.float32)
        reproject(
            source=src_data,
            destination=dst,
            src_transform=src_transform,
            src_crs=src_crs,
            src_nodata=src_nodata,
            dst_transform=dst_transform,
            dst_crs=ref.crs,
            dst_nodata=np.nan,
            resampling=Resampling.bilinear,
            num_threads=1,
        )

    ref_nodata = ref.nodata if ref.nodata is not None else -3.4028235e38
    ref_valid = np.isfinite(ref_win) & (ref_win != ref_nodata)
    warp_valid = np.isfinite(dst)
    both = ref_valid & warp_valid
    n = int(both.sum())
    rec["n_common_px"] = n
    rec["published_valid_frac_in_window"] = round(float(ref_valid.mean()), 4)

    if n < min_pixels:
        rec["status"] = "INSUFFICIENT OVERLAP"
        rec["note"] = f"only {n} common pixels (< {min_pixels} required)"
        return rec

    diff = (dst - ref_win)[both].astype(np.float64)

    # --- plane removal (relative precision; see module docstring) ---
    rows, cols = np.nonzero(both)
    xk = (cols - cols.mean()) / 1000.0  # km, centred
    yk = (rows - rows.mean()) / 1000.0
    A = np.column_stack([np.ones(n), xk, yk])
    coef, *_ = np.linalg.lstsq(A, diff, rcond=None)
    pr = diff - A @ coef  # plane-removed difference, metres

    absd = np.abs(pr)
    p68, p90, p95 = (float(v) for v in np.percentile(absd, [68, 90, 95]))
    raw_median, raw_std = float(np.median(diff)), float(np.std(diff))
    pr_median, pr_std = float(np.median(pr)), float(np.std(pr))
    # MAD (skeptic recommendation 2026-09-17): robust to pair3's 773 m
    # tail contamination that swells std but not MAD.
    pr_mad = float(np.median(np.abs(pr - pr_median)))

    rec.update(
        {
            "status": "compared",
            "raw_diff": {  # transparency only — NOT the PASS statistic
                "median_m": round(raw_median, 4),
                "std_m": round(raw_std, 4),
                "note": "includes vertical-datum + geolocation offsets; "
                "reproduced ASP DEM uses a scene-local height datum",
            },
            "plane_fit": {
                "form": "diff ~ a + b*x_km + c*y_km (least squares, "
                "common pixels)",
                "a_m": round(float(coef[0]), 4),
                "b_m_per_km": round(float(coef[1]), 6),
                "c_m_per_km": round(float(coef[2]), 6),
            },
            "plane_removed_diff": {
                "median_m": round(pr_median, 4),
                "std_m": round(pr_std, 4),
                "mad_m": round(pr_mad, 4),
                "abs_p68_m": round(p68, 2),
                "abs_p90_m": round(p90, 2),
                "abs_p95_m": round(p95, 2),
                "abs_max_m": round(float(absd.max()), 2),
                "abs_p90_m_full_precision": round(p90, 6),
            },
        }
    )
    verdict = "PASS" if p90 <= relat_le else "FAIL"
    rec["verdict"] = f"{verdict} (90th pct |plane-removed diff| = "
    f"{p90:.2f} m vs relat_le {relat_le:.2f} m)"

    # --- diff raster (plane-removed, published grid, overlap window) ---
    tif_path = out_dir / f"task8_diff_{pair}_{date}.tif"
    out = np.full(dst.shape, np.float32(ref_nodata), np.float32)
    out[both] = pr.astype(np.float32)
    profile = ref.profile.copy()
    profile.update(
        driver="GTiff",
        height=dst.shape[0],
        width=dst.shape[1],
        transform=dst_transform,
        dtype="float32",
        nodata=ref_nodata,
        compress="deflate",
        predictor=3,
    )
    with rasterio.open(tif_path, "w", **profile) as dstf:
        dstf.write(out, 1)
        dstf.set_band_description(1, "plane-removed diff (reproduced - published), m")
    rec["diff_tif"] = str(tif_path)
    rec["diff_tif_content"] = (
        "plane-removed difference (reproduced minus published), metres, "
        "on the published DTM grid (windowed to the overlap bbox; "
        "grid-aligned integer window of the published transform)"
    )

    # --- histogram PNG ---
    png_path = out_dir / f"task8_diff_{pair}_{date}.png"
    _histogram(png_path, pair, pr, p90, relat_le, n, verdict)
    rec["histogram_png"] = str(png_path)
    from PIL import Image  # lazy import (verification per conventions §7)

    with Image.open(png_path) as im:
        rec["histogram_png_dims_px"] = list(im.size)

    # canonical raster copy under ~/lunarvoid/data (conventions section 1)
    canon = CANONICAL_DIR / tif_path.name
    shutil.copy2(tif_path, canon)
    rec["canonical_tif"] = str(canon)

    rec["verdict_plain"] = verdict
    return rec


def _histogram(path: Path, pair: str, pr: np.ndarray, p90: float,
               relat_le: float, n: int, verdict: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    lim = float(np.percentile(np.abs(pr), 99.9))
    lim = max(lim, 3.0 * float(np.std(pr)), 1.0)
    fig, ax = plt.subplots(figsize=(7.0, 4.2), dpi=150)
    ax.hist(np.clip(pr, -lim, lim), bins=151, color="#4477aa",
            edgecolor="none")
    for v in (-relat_le, relat_le):
        ax.axvline(v, color="#cc3311", ls="--", lw=1.4,
                   label=f"$\\pm{relat_le:.2f}$ m (relat_le)")
    ax.axvline(-p90, color="k", ls=":", lw=1.2)
    ax.axvline(p90, color="k", ls=":", lw=1.2,
               label=f"90th pct $|d|$: {p90:.2f} m")
    ax.set_xlabel("plane-removed difference (reproduced $-$ published) [m]")
    ax.set_ylabel("pixels")
    ax.set_title(
        f"TRANQPIT1 {pair}: DEM reproduction vs published DTM "
        f"({verdict}, N={n:,})"
    )
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dems", nargs="*", type=Path,
                    help="reproduced DEM GeoTIFF path(s)")
    ap.add_argument("--all", action="store_true",
                    help="run the three known TRANQPIT1 pair DEMs")
    ap.add_argument("--ref", type=Path, default=DEFAULT_REF,
                    help="published reference DTM")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--date", default=_dt.date.today().isoformat())
    ap.add_argument("--relat-le", type=float, default=0.72,
                    help="PASS threshold at the 90th percentile, metres")
    ap.add_argument("--min-pixels", type=int, default=10_000)
    args = ap.parse_args(argv)

    if not args.dems and not args.all:
        ap.error("give DEM path(s) or --all")
    pairs = (
        [(pair_id_from_path(p, i + 1), p) for i, p in enumerate(args.dems)]
        if args.dems
        else list(DEFAULT_PAIRS)
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    CANONICAL_DIR.mkdir(parents=True, exist_ok=True)

    summary: dict = {
        "task": "8.4 — reproduced vs published TRANQPIT1 DEM comparison",
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "spec": {
            "relat_le_m": args.relat_le,
            "percentile": 90,
            "pass_rule": "90th percentile of |plane-removed diff| <= relat_le",
            "source": "01_WORKSPACE/plans/2026-08-19_ZEROCOST_Roadmap.md "
            "L401; 01_WORKSPACE/plans/2026-08-19_WP0_scope_map.md "
            "(TRANQPIT1 relat_le 0.72 m)",
        },
        "reference": {},
        "geodesy_check": {},
        "method": [
            "Reproduced DEMs reprojected onto the published DTM grid "
            "(rasterio.warp.reproject, bilinear, num_threads=1; overlap "
            "window rounded outward to integer published-grid pixels).",
            "CRS taken from file WKTs: published local equirectangular "
            "(+proj=eqc +lat_ts=8 +lon_0=180 +R=1737400) vs ASP "
            "stereographic (+proj=stere +lat_0=8.63508 +lon_0=33.2026 "
            "+R=1737400). No EPSG assumptions (both Moon sphere).",
            "Valid mask = both rasters valid; >= 10,000 common pixels "
            "required else INSUFFICIENT OVERLAP.",
            "RELATIVE comparison: best-fit plane (a + b*x + c*y) removed "
            "from the difference before percentile statistics — absolute "
            "geolocation/vertical-datum offsets between an ASP "
            "bundle-adjusted product and a SOCET product are not part of "
            "relative precision. Raw (no-plane) median/std also reported.",
            "Caveats: bilinear resampling smooths sub-pixel detail "
            "(grids are both 2 m but not axis-aligned); reproduced DEM "
            "covers only the ~362 m x 28.8 km LE/RE overlap strip with "
            "~16% valid pixels (dense-matching coverage), so statistics "
            "characterise that strip only, not the full DTM frame.",
            "diff TIFs store the PLANE-REMOVED difference on the "
            "published grid (windowed, grid-aligned); plane coefficients "
            "in this JSON allow recovery of the raw difference field.",
        ],
        "pairs": {},
    }

    with rasterio.open(args.ref) as ref:
        summary["reference"] = {
            "path": str(args.ref),
            "crs_proj4": ref.crs.to_proj4() if ref.crs else None,
            "shape_wh": [ref.width, ref.height],
            "res_m": [ref.transform.a, -ref.transform.e],
            "nodata": ref.nodata,
        }
        summary["geodesy_check"] = geodesy_sanity(ref)
        for pair, path in pairs:
            if not path.exists():
                summary["pairs"][pair] = {
                    "status": "pending",
                    "reproduced_dem": str(path),
                    "note": "DEM not produced yet (stereo run incomplete)",
                }
                print(f"[{pair}] PENDING (no DEM at {path})")
                continue
            print(f"[{pair}] comparing {path} ...", flush=True)
            rec = compare_pair(
                pair, path, ref, args.relat_le, args.min_pixels,
                args.out_dir, args.date,
            )
            summary["pairs"][pair] = rec
            if rec["status"] == "compared":
                pr90 = rec["plane_removed_diff"]["abs_p90_m"]
                print(
                    f"[{pair}] N={rec['n_common_px']:,}  "
                    f"raw median {rec['raw_diff']['median_m']:+.2f} m  "
                    f"plane-removed: median {rec['plane_removed_diff']['median_m']:+.2f} m, "
                    f"std {rec['plane_removed_diff']['std_m']:.2f} m, "
                    f"p90 {pr90:.2f} m -> {rec['verdict_plain']}"
                )
            else:
                print(f"[{pair}] {rec['status']}: {rec.get('note', '')}")

    json_path = args.out_dir / f"task8_diff_{args.date}.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[json] {json_path}")

    verdicts = [
        p.get("verdict_plain")
        for p in summary["pairs"].values()
        if p.get("status") == "compared"
    ]
    if any(v == "FAIL" for v in verdicts):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
