"""Diviner nighttime T + rock abundance sampler for the 7 candidate DTMs.

Reads Powell 2023 GHRM products (Powell et al. 2023, LRO Diviner Global
High-Resolution Mosaics; PDS Geosciences Node
urn:nasa:pds:lro_diviner_derived1:data_derived_ghrm):

  dghrm_tbol_m_70s70n_tif.tif  (17920 x 46080, float32, 128 ppd, ~237 m/px,
                                equirectangular, lon -180..180, lat -70..+70,
                                bolometric nighttime T at midnight, K)
  dghrm_ra_sam_70s70n_tif.tif   (same shape, rock abundance areal fraction,
                                seasonally-averaged monthly; "SAM")

For each row of `candidate_registry.csv`, sample mean +/- SD in a 1-km
box (centered on the candidate lon/lat) from BOTH rasters, plus the
local mare-median T in the surrounding 20x20 km box excluding the 1-km
inner box (so the local reference is NOT contaminated by the candidate).
Compute delta_T = T(candidate) - T(mare-median) and report whether each
candidate is > 2 sigma above mare-median.

Output:
  - diviner_thermal.csv (one row per candidate; columns documented below)
  - diviner_summary.json (per-DTM aggregates + global N=7 banner)

Geo conventions: per project lunarvoid-conventions §3 (Moon eqc with
R=1737400 m, planetocentric lon/lat). The GHRM GeoTIFFs use equirectangular
on R=1737400 m, central meridian 0 (not 180 like most LROC products), so
we transform candidate lon -180..180 -> image column coordinate via the
GeoTIFF's transform directly (no pyproj round-trip needed; the raster
geotransform is authoritative).

Sentinel handling: the PDS4 XML for both products declares
`missing_constant = NaN`, but in the actual GeoTIFF (Powell 2023,
urn:nasa:pds:lro_diviner_derived1) the missing-data sentinel is the
float32 value 0.0 (NOT NaN). This was confirmed empirically: a 1000x1000
equatorial patch contains ~96% zeros and 4% physically-realistic nighttime
T values clustered at 95-125 K; a rock-abundance patch shows the same
96/4 split with values reaching ~0.2. For TBOL, 0 K is non-physical; for
RA, the empirical density pattern (96% identical to TBOL) confirms 0.0
is the converted sentinel, not a valid "no rock" measurement. We treat
0.0 as missing in BOTH rasters via the `VALID_MIN` threshold below. This
matches the underlying FITS blanking semantics described in Williams et
al. (2017) Icarus 283, 300-325 (Diviner L4 processing).

Claim discipline (per lunarvoid-conventions §5/§6): "calibrated inference,
never verified detection". We report the value with error bars; if the
delta-T is consistent with the mare-median, that IS a finding (a null
result for a thermal-anomaly hypothesis at G1 demonstration scale).
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import rasterio
from rasterio.windows import Window

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "01_WORKSPACE" / "data"

DEFAULT_TBOL = Path("/home/frostflux/lunarvoid/data/evidence/diviner/dghrm_tbol_m_70s70n_tif.tif")
DEFAULT_RA   = Path("/home/frostflux/lunarvoid/data/evidence/diviner/dghrm_ra_sam_70s70n_tif.tif")

# Site list (lon, lat, dtm, span_m) keyed by DTM. Sourced from candidate_registry.csv.
DTMS_IN_SCOPE = [
    "TRANQPIT1", "MARIUSPIT01", "INGENIIPIT", "IRIDIUMPIT1",
    "PRCLRMPIT01", "SWFECUNPIT1", "FECNDITATS2",
]
DEMO_BANNER = "DEMONSTRATION ONLY; N=7 of 649 good-tier mare DTMs sampled " \
              "(P4.3 Powell 2023 thermal/rock evidence at G1 scale; Phase-3 G1 banner)"

# Sampling parameters (per task spec)
INNER_HALF_M = 500.0          # 1-km box half-side -> ±500 m
OUTER_HALF_M = 10000.0        # 20-km box half-side for local mare reference

# 1 sigma threshold (per task: "fraction > 2 sigma above mare-median")
SIGMA_THRESHOLD = 2.0

# Sentinel handling (Powell 2023 GHRM). See module docstring: 0.0 is
# the actual missing-data sentinel in the GeoTIFF (PDS4 XML says NaN,
# but the GeoTIFF stores 0.0). We require a strictly positive value.
# For TBOL: 0 K is non-physical. For RA: the 96%-zeros density pattern
# at the equator matches TBOL exactly, so the zeros are sentinel noise,
# not a valid "bare mare" measurement.
TBOL_VALID_MIN_K = 0.0   # exclusive; 0.0 treated as missing
RA_VALID_MIN_FRAC = 0.0  # exclusive; 0.0 treated as missing (see docstring)


def _valid_mask(arr: np.ndarray, valid_min: float) -> np.ndarray:
    """Return boolean mask of pixels with a real measurement.

    RA 0.0 exclusion biases against bare-mare pixels; the inner-box RA may
    be slightly over-estimated if mare-reference pixels are stripped.
    Document as upper-bound. Powell NaN-vs-0.0 sentinel mapping is an
    upstream PDS quirk; consider requesting NaN-as-sentinel in P4.4.
    """
    return np.isfinite(arr) & (arr > valid_min)


def pixel_window(raster: rasterio.io.DatasetReader, lon: float, lat: float,
                 half_m: float):
    """Return a rasterio Window centred on (lon, lat) covering half_m metres.

    Uses the raster's own CRS transform (per lunarvoid-conventions §3;
    GHRM is equirectangular on R=1737400 m, central meridian 0).

    Returns: (Window, half_m_x_deg, half_m_y_deg)
    """
    # Equirectangular: 1 deg lon = pi*R*cos(lat)/180 metres;
    #                   1 deg lat = pi*R/180 metres.
    R = 1737400.0
    # half-size in degrees
    cos_lat = math.cos(math.radians(lat))
    half_dlon = half_m / (math.pi * R / 180.0 * max(cos_lat, 1e-6))
    half_dlat = half_m / (math.pi * R / 180.0)
    transform = raster.transform
    inv = ~transform
    # centre pixel coords (fractional)
    cx, cy = inv * (lon, lat)
    # width/height in pixels
    win_w = max(int(math.ceil(half_dlon / abs(transform.a))), 1) * 2 + 1
    win_h = max(int(math.ceil(half_dlat / abs(transform.e))), 1) * 2 + 1
    col_off = int(round(cx - win_w / 2))
    row_off = int(round(cy - win_h / 2))
    col_off = max(0, col_off)
    row_off = max(0, row_off)
    if col_off + win_w > raster.width:
        col_off = raster.width - win_w
    if row_off + win_h > raster.height:
        row_off = raster.height - win_h
    return Window(col_off, row_off, win_w, win_h), half_dlon, half_dlat


def read_window(raster: rasterio.io.DatasetReader, win: rasterio.windows.Window):
    arr = raster.read(1, window=win, masked=False)
    return np.asarray(arr, dtype=np.float32)


def sample_at(raster: rasterio.io.DatasetReader, lon: float, lat: float,
              half_m: float, valid_min: float):
    """Sample mean/SD/finite-count of `raster` in a centred half_m x half_m box.

    `valid_min` is the strict-lower threshold (sentinel handling):
    any pixel <= valid_min (including 0.0 = sentinel, NaN, inf) is
    counted as missing. See module docstring.

    Returns: dict(mean=..., sd=..., n=..., n_valid=..., win=..., reason=None)
    """
    win, half_dlon, half_dlat = pixel_window(raster, lon, lat, half_m)
    arr = read_window(raster, win)
    valid = arr[_valid_mask(arr, valid_min)]
    if valid.size == 0:
        # Distinguish "no raster data here" from "all-sentinel": if even
        # some pixels had non-NaN finite values, those were sentinels.
        any_present = int(np.sum(np.isfinite(arr)))
        return dict(mean=None, sd=None, n_total=int(arr.size), n_valid=0,
                    n_present=any_present,
                    half_dlon_deg=half_dlon, half_dlat_deg=half_dlat,
                    win=dict(col_off=int(win.col_off), row_off=int(win.row_off),
                             width=int(win.width), height=int(win.height)),
                    reason="all_sentinel_or_NaN_in_box")
    return dict(
        mean=float(np.mean(valid)),
        sd=float(np.std(valid, ddof=1)) if valid.size > 1 else 0.0,
        n_total=int(arr.size),
        n_valid=int(valid.size),
        n_present=int(np.sum(np.isfinite(arr))),
        win=dict(col_off=int(win.col_off), row_off=int(win.row_off),
                 width=int(win.width), height=int(win.height)),
        half_dlon_deg=half_dlon,
        half_dlat_deg=half_dlat,
        reason=None,
    )


def sample_local_mare_median(raster: rasterio.io.DatasetReader,
                             lon: float, lat: float,
                             inner_half_m: float, outer_half_m: float,
                             valid_min: float):
    """Sample the local mare-median T (or RA) in the 20x20 km box
    EXCLUDING the inner 1-km box around the candidate.

    `valid_min`: strict-lower threshold for sentinel handling.

    Returns: dict(median=..., mad=..., iqr=..., n_valid=..., reason=None)
    """
    # Read the outer window then mask out the inner.
    win_out, _, _ = pixel_window(raster, lon, lat, outer_half_m)
    arr_out = read_window(raster, win_out)
    win_in, _, _ = pixel_window(raster, lon, lat, inner_half_m)
    arr_in = read_window(raster, win_in)
    # Build a mask of the same shape as arr_out where arr_in lands.
    # rasterio windows are aligned to the same transform (same origin &
    # pixel size) so the inner window in absolute coords:
    # inner col range = [win_in.col_off, win_in.col_off + win_in.width)
    # outer col range = [win_out.col_off, win_out.col_off + win_out.width)
    # The inner window's pixel-coords within the outer block:
    inner_col_in_out = win_in.col_off - win_out.col_off
    inner_row_in_out = win_in.row_off - win_out.row_off
    h, w = arr_out.shape
    # Build sentinel-mask of arr_out excluding the inner (set inner to NaN
    # so the sentinel-aware filter drops them).
    arr_copy = arr_out.copy()
    c0 = max(inner_col_in_out, 0)
    c1 = min(inner_col_in_out + win_in.width, w)
    r0 = max(inner_row_in_out, 0)
    r1 = min(inner_row_in_out + win_in.height, h)
    if c0 < c1 and r0 < r1:
        arr_copy[r0:r1, c0:c1] = np.nan
    valid = arr_copy[_valid_mask(arr_copy, valid_min)]
    if valid.size == 0:
        return dict(median=None, mad=None, iqr=None, q1=None, q3=None,
                    n_valid=0,
                    reason="all_sentinel_or_NaN_in_outer_box")
    median = float(np.median(valid))
    q1 = float(np.percentile(valid, 25))
    q3 = float(np.percentile(valid, 75))
    iqr = q3 - q1
    mad = float(np.median(np.abs(valid - median)))
    return dict(median=median, mad=mad, iqr=iqr,
                q1=q1, q3=q3, n_valid=int(valid.size), reason=None)


def fmt(v, prec=2):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return "NO_DATA"
    return f"{v:.{prec}f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", type=Path,
                    default=DATA_DIR / "candidate_registry.csv")
    ap.add_argument("--tbol", type=Path, default=DEFAULT_TBOL)
    ap.add_argument("--ra", type=Path, default=DEFAULT_RA)
    ap.add_argument("--out-csv", type=Path,
                    default=DATA_DIR / "outputs" / "wp2_sag" / "transfer" / "diviner_thermal.csv")
    ap.add_argument("--out-json", type=Path,
                    default=DATA_DIR / "outputs" / "wp2_sag" / "transfer" / "diviner_summary.json")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    np.random.seed(args.seed)

    # ---- Load registry -----------------------------------------------------
    rows = []
    with open(args.registry, newline="") as f:
        reader = csv.reader(f)
        for raw in reader:
            if not raw or raw[0].startswith("#"):
                continue
            rows.append(raw)
    header = rows[0]
    # columns: candidate_id, lon, lat, dtm, span_m, sag_amp_m, score, confusion,
    #          methods, tier, status, first_found, updated, evidence, notes
    cid_idx = header.index("candidate_id")
    lon_idx = header.index("lon")
    lat_idx = header.index("lat")
    dtm_idx = header.index("dtm")
    span_idx = header.index("span_m")
    candidates = []
    for r in rows[1:]:
        if len(r) <= max(cid_idx, dtm_idx):
            continue
        try:
            candidates.append(dict(
                candidate_id=r[cid_idx],
                lon=float(r[lon_idx]),
                lat=float(r[lat_idx]),
                dtm=r[dtm_idx],
                span_m=float(r[span_idx]),
            ))
        except (ValueError, IndexError):
            continue
    print(f"[info] loaded {len(candidates)} candidates from {args.registry.name}",
          flush=True)

    # Filter to in-scope DTMs (the 7 DTMs in the demo banner)
    candidates = [c for c in candidates if c["dtm"] in DTMS_IN_SCOPE]
    print(f"[info] {len(candidates)} candidates within 7-DTM scope "
          f"({', '.join(DTMS_IN_SCOPE)})", flush=True)

    # ---- Sanity-check geodesy (per conventions §7) -----------------------
    # Open both rasters
    if not args.tbol.exists():
        sys.exit(f"[abort] TBOL raster missing: {args.tbol}")
    if not args.ra.exists():
        sys.exit(f"[abort] RA raster missing: {args.ra}")
    with rasterio.open(args.tbol) as src_t, rasterio.open(args.ra) as src_r:
        print(f"[info] TBOL raster: {src_t.width}x{src_t.height} "
              f"dtype={src_t.dtypes[0]} crs={src_t.crs} "
              f"transform={src_t.transform}", flush=True)
        print(f"[info] RA   raster: {src_r.width}x{src_r.height} "
              f"dtype={src_r.dtypes[0]} crs={src_r.crs} "
              f"transform={src_r.transform}", flush=True)
        # Sanity-check geodesy on known TRANQPIT1 (33.20, 8.75) -> must be
        # inside the raster (lat in ±70°, lon in ±180°).
        for cand in candidates[:1]:
            win, hdlon, hdlat = pixel_window(src_t, cand["lon"], cand["lat"], 100.0)
            arr = read_window(src_t, win)
            valid = arr[_valid_mask(arr, TBOL_VALID_MIN_K)]
            print(f"[sanity] TBOL {cand['candidate_id']} @ ({cand['lon']},{cand['lat']}): "
                  f"100m-box mean T = {np.mean(valid):.2f} K (n_valid={valid.size}/{arr.size})  "
                  f"[n_present_finite={int(np.sum(np.isfinite(arr)))}]",
                  flush=True)
            win2, _, _ = pixel_window(src_r, cand["lon"], cand["lat"], 100.0)
            arr2 = read_window(src_r, win2)
            valid2 = arr2[_valid_mask(arr2, RA_VALID_MIN_FRAC)]
            print(f"[sanity] RA   {cand['candidate_id']} @ ({cand['lon']},{cand['lat']}): "
                  f"100m-box mean RA = {np.mean(valid2):.5f} (n_valid={valid2.size}/{arr2.size})",
                  flush=True)

        # ---- Sample ----------------------------------------------------
        out_rows = []
        for cand in candidates:
            lon, lat = cand["lon"], cand["lat"]
            try:
                t_in = sample_at(src_t, lon, lat, INNER_HALF_M, TBOL_VALID_MIN_K)
                r_in = sample_at(src_r, lon, lat, INNER_HALF_M, RA_VALID_MIN_FRAC)
                t_out = sample_local_mare_median(
                    src_t, lon, lat,
                    INNER_HALF_M, OUTER_HALF_M, TBOL_VALID_MIN_K)
            except Exception as e:
                print(f"[warn] sample failed for {cand['candidate_id']}: {e}",
                      flush=True)
                t_in = dict(mean=None, sd=None, n_valid=0, n_total=0,
                            n_present=0,
                            reason=f"exception:{type(e).__name__}",
                            win=dict(col_off=-1, row_off=-1, width=0, height=0))
                r_in = dict(mean=None, sd=None, n_valid=0, n_total=0,
                            n_present=0,
                            reason=f"exception:{type(e).__name__}",
                            win=dict(col_off=-1, row_off=-1, width=0, height=0))
                t_out = dict(median=None, iqr=None, q1=None, q3=None,
                             mad=None, n_valid=0,
                             reason=f"exception:{type(e).__name__}")

            # delta T = T(candidate) - T(mare-median)
            delta_t = None
            sigma_dist = None
            is_anomaly_2sigma = False
            if (t_in["mean"] is not None and t_out["median"] is not None
                    and t_out["iqr"] is not None and t_out["iqr"] > 0):
                delta_t = t_in["mean"] - t_out["median"]
                # use IQR / 1.349 as a robust sigma estimate
                robust_sigma = t_out["iqr"] / 1.349
                if robust_sigma > 0:
                    sigma_dist = delta_t / robust_sigma
                    is_anomaly_2sigma = sigma_dist > SIGMA_THRESHOLD

            out_rows.append(dict(
                candidate_id=cand["candidate_id"],
                dtm=cand["dtm"],
                lon=lon,
                lat=lat,
                span_m=cand["span_m"],
                # Inner 1-km box thermal
                T_K_mean=t_in["mean"],
                T_K_sd=t_in["sd"],
                T_n_valid=t_in["n_valid"],
                T_n_total=t_in["n_total"],
                T_reason=t_in["reason"] or "",
                # Inner 1-km box rock abundance (fraction -> %)
                RA_pct_mean=(r_in["mean"] * 100.0 if r_in["mean"] is not None else None),
                RA_pct_sd=(r_in["sd"] * 100.0 if r_in["sd"] is not None else None),
                RA_n_valid=r_in["n_valid"],
                RA_n_total=r_in["n_total"],
                RA_reason=r_in["reason"] or "",
                # Local mare reference (20 km box excluding inner 1 km)
                T_mare_median_K=t_out["median"],
                T_mare_q1_K=t_out["q1"],
                T_mare_q3_K=t_out["q3"],
                T_mare_iqr_K=t_out["iqr"],
                T_mare_n_valid=t_out["n_valid"],
                T_mare_reason=t_out["reason"] or "",
                # Derived
                delta_T_K=delta_t,
                sigma_dist=sigma_dist,
                is_anomaly_2sigma=bool(is_anomaly_2sigma),
            ))

    # ---- Write CSV ---------------------------------------------------------
    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    cols = list(out_rows[0].keys()) if out_rows else [
        "candidate_id", "dtm", "lon", "lat", "span_m",
        "T_K_mean", "T_K_sd", "T_n_valid", "T_n_total", "T_reason",
        "RA_pct_mean", "RA_pct_sd", "RA_n_valid", "RA_n_total", "RA_reason",
        "T_mare_median_K", "T_mare_q1_K", "T_mare_q3_K", "T_mare_iqr_K",
        "T_mare_n_valid", "T_mare_reason",
        "delta_T_K", "sigma_dist", "is_anomaly_2sigma",
    ]
    with open(args.out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"[out] CSV -> {args.out_csv}  ({len(out_rows)} rows)", flush=True)

    # ---- Per-DTM aggregate + global N=7 banner -----------------------------
    n_total = len(out_rows)
    n_no_data_t = sum(1 for r in out_rows if r["T_K_mean"] is None)
    n_no_data_ra = sum(1 for r in out_rows if r["RA_pct_mean"] is None)
    n_anomaly = sum(1 for r in out_rows if r["is_anomaly_2sigma"])
    delta_t_vals = [r["delta_T_K"] for r in out_rows if r["delta_T_K"] is not None]
    sigma_vals = [r["sigma_dist"] for r in out_rows if r["sigma_dist"] is not None]

    per_dtm = {}
    for d in DTMS_IN_SCOPE:
        sub = [r for r in out_rows if r["dtm"] == d]
        if not sub:
            continue
        d_deltas = [r["delta_T_K"] for r in sub if r["delta_T_K"] is not None]
        d_anom = [r for r in sub if r["is_anomaly_2sigma"]]
        per_dtm[d] = dict(
            n_candidates=len(sub),
            n_T_no_data=sum(1 for r in sub if r["T_K_mean"] is None),
            n_RA_no_data=sum(1 for r in sub if r["RA_pct_mean"] is None),
            n_anomaly_2sigma=len(d_anom),
            frac_anomaly_2sigma=(len(d_anom) / len(sub)) if sub else None,
            delta_T_K=dict(
                min=min(d_deltas) if d_deltas else None,
                p25=(np.percentile(d_deltas, 25) if d_deltas else None),
                median=(np.median(d_deltas) if d_deltas else None),
                p75=(np.percentile(d_deltas, 75) if d_deltas else None),
                max=max(d_deltas) if d_deltas else None,
            ),
        )

    summary = dict(
        banner=DEMO_BANNER,
        scope=dict(
            dtms_in_scope=DTMS_IN_SCOPE,
            n_dtms=len(DTMS_IN_SCOPE),
        ),
        data=dict(
            tbol_path=str(args.tbol),
            ra_path=str(args.ra),
            tbol_size_bytes=args.tbol.stat().st_size,
            ra_size_bytes=args.ra.stat().st_size,
            tbol_sha256=hashlib.sha256(args.tbol.read_bytes()).hexdigest(),
            ra_sha256=hashlib.sha256(args.ra.read_bytes()).hexdigest(),
            citation="Powell et al. 2023 (LRO Diviner GHRM, PDS Geosciences Node urn:nasa:pds:lro_diviner_derived1:data_derived_ghrm); see also Williams et al. 2017 Icarus 283, 300-325 (cumulative nighttime T algorithm).",
            licence="PDS public domain",
        ),
        sampling=dict(
            inner_box_half_m=INNER_HALF_M,
            outer_box_half_m=OUTER_HALF_M,
            sigma_threshold=SIGMA_THRESHOLD,
            sigma_estimate="IQR/1.349 (robust Gaussian-equivalent)",
            sentinel_handling=(
                "Powell 2023 GHRM GeoTIFFs encode the missing-data sentinel "
                "as float32 0.0 (NOT NaN as the PDS4 XML claims; verified "
                "empirically at equator: 96% of pixels are 0.0 with the "
                "remaining 4% physically realistic). TBOL 0 K is non-physical; "
                "RA 0.0 fraction matches the TBOL density pattern so it is "
                "treated as the same sentinel, not a valid bare-mare value. "
                "Pixels with value <= 0.0 (including NaN/inf) are excluded "
                "from all aggregates."
            ),
            tbol_valid_min_K=TBOL_VALID_MIN_K,
            ra_valid_min_frac=RA_VALID_MIN_FRAC,
        ),
        global_summary=dict(
            n_candidates=n_total,
            n_no_data_T=n_no_data_t,
            n_no_data_RA=n_no_data_ra,
            n_anomaly_2sigma=n_anomaly,
            frac_anomaly_2sigma=(n_anomaly / n_total) if n_total else None,
            delta_T_K_summary=dict(
                min=min(delta_t_vals) if delta_t_vals else None,
                p25=(np.percentile(delta_t_vals, 25) if delta_t_vals else None),
                median=(np.median(delta_t_vals) if delta_t_vals else None),
                p75=(np.percentile(delta_t_vals, 75) if delta_t_vals else None),
                max=max(delta_t_vals) if delta_t_vals else None,
                iqr=((np.percentile(delta_t_vals, 75)
                      - np.percentile(delta_t_vals, 25)) if delta_t_vals else None),
            ),
            sigma_dist_summary=dict(
                min=min(sigma_vals) if sigma_vals else None,
                p25=(np.percentile(sigma_vals, 25) if sigma_vals else None),
                median=(np.median(sigma_vals) if sigma_vals else None),
                p75=(np.percentile(sigma_vals, 75) if sigma_vals else None),
                max=max(sigma_vals) if sigma_vals else None,
            ),
        ),
        per_dtm=per_dtm,
        interpretation=(
            "Calibrated inference, not detection (lunarvoid-conventions §5). "
            "Thermal non-detection (delta-T consistent with mare-median within "
            "robust 2-sigma) is a RESULT, not silence: it constrains the "
            "thermal-anomaly hypothesis at the G1 demonstration scale."
        ),
        generated_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        seed=args.seed,
    )

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[out] JSON -> {args.out_json}", flush=True)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    sys.exit(main() or 0)
