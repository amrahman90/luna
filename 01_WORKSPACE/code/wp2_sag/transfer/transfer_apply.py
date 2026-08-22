"""P3.1c — apply the FROZEN Z2 calibration (Task 18.3, I15 protocol) to the
N=10 on-disk DTMs, populate the candidate registry with inference-language
rows, and emit the transfer summary with honest per-DTM + aggregate FP/10⁴ km².

Scope (LOADED — N=10/649 is the $0-scope limitation, documented in
findings.md 2026-08-22):
  - 10 DTM sites on disk under ~/lunarvoid/data/dtms/.
  - 7 of those 10 have a cached v0.1 Z2 score raster on disk
    (TRANQPIT1, IRIDIUMPIT1, INGENIIPIT, FECNDITATS2, MARIUSPIT01,
     PRCLRMPIT01, SWFECUNPIT1). These are the 7 sites processed below.
  - 3 of those 10 (MARIUSCONE, GRUITHUIS17, GRUITHMARE2) have NO cached
    v0.1 score raster and are SKIPPED with a documented reason. They
    contribute ZERO area to the candidate count but ARE part of the
    N=10/649 honesty banner.
  - 639 of 649 good-tier mare DTMs are MISSING from disk entirely
    ($0 budget; Task 8 rental deferred per user 2026-08-21). Not
    touched here.

Frozen calibration (load_or_build the cached score raster; do NOT
re-tune per DTM; allowed rungs per the sag_search.py 0.6 res rule):
  - score_frac = 0.20
  - slope_deg  = 45
  - neigh      = 5
  - Frangi sigmas = (30, 60, 100, 150, 200, 300) m
  - fill       = Planchon-Darboux (already baked into the cached score)

Tier rules (conservative; per R1):
  - Default tier C: single-method (sag score only) candidate.
  - Tier B: multi-method within this task. Either
      B-rille  : candidate within 100 m of a Hurwitz sinuous rille
      B-chain  : candidate within 100 m of a LU5M812TGT crater
                 that lies in a 1° lat strip with >=3 craters
                 (chain-strip rule, same as confusion_layer.py)
    OR, if neither, it stays tier C.
  - Tier A: NOT assigned. Phase-5 skeptic-gated rule requires
    gravity/thermal/illumination agreement (not computed in P3.1c).

FP/10⁴ km² honesty:
  - per-DTM FP rate = (n_above_local_floor FPs) / area_km2 * 1e4
    (candidates with sag amplitude < local_Amin are kept but flagged
     'below-local-floor' and DO NOT count as FPs — they are
     explicitly excluded from the FP-rate denominator because the
     detector couldn't reach the detectability floor).
  - Poisson 95% CI via scipy.stats.chi2.ppf
      n_fp  = 0 -> one-sided upper bound (chi2.ppf(0.95, 2)/2 / area)
      n_fp >=1 -> equal-tailed (chi2.ppf(0.025, 2k)/2, chi2.ppf(0.975, 2k+2)/2)
  - Aggregate = sum FPs / sum areas, with the same Poisson CI on
    the summed FP count.

Outputs (repo, small files only):
  01_WORKSPACE/data/candidate_registry.csv        (appended — schema preserved)
  01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json
  01_WORKSPACE/data/outputs/wp2_sag/transfer/METHODS.md (appended)

Raw rasters stay under ~/lunarvoid/data/ (per conventions §1).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pyproj import CRS, Transformer
from rasterio.enums import Resampling
from scipy.ndimage import maximum_filter
from scipy.stats import chi2

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp1_detector"))
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp2_sag"))
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp0_primitive"))

from sag_detect import slope_deg_map  # noqa: E402
from sweep_pits import pit_to_pixel  # noqa: E402

RAW = Path.home() / "lunarvoid" / "data"
WP2 = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag"
TRANSFER_DIR = WP2 / "transfer"
REGISTRY = REPO / "01_WORKSPACE" / "data" / "candidate_registry.csv"
FLOORS_CSV = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_kriging" / "per_dtm_floors.csv"
PIT_CATALOG = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_scope_map" / "relevant_pits_x_dtms.csv"
RILLE_SHP = RAW / "index_layers" / "hurwitz_rilles" / "shapefile" / "SinuousRilles_obs.shp"
CRATER_CSV = RAW / "index_layers" / "craters_lu5m812tgt" / "craters_0p4_5km_pm60.csv.gz"
CATALOG = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_scope_map" / "relevant_pits_x_dtms.csv"
MOON_R = 1737400.0
MOON_GEOG = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")

# ---- FROZEN (P3.1b) -----------------------------------------------------
FROZEN_FRAC = 0.20
FROZEN_SLOPE = 45.0
FROZEN_NEIGH = 5
FROZEN_SIGMAS = (30, 60, 100, 150, 200, 300)
FROZEN_PIT_MATCH_RADIUS_M = 100.0  # Z2 pit-distance verification convention
B_RADIUS_M = 100.0  # tier-B intersection radius
TWOPI = 2.0 * math.pi
LOG2 = math.log(2.0)


def dtm_source(dtm_name: str) -> Path:
    """Source DTM path (krigcorr preferred; raw fallback)."""
    krig = RAW / "outputs" / dtm_name / f"NAC_DTM_{dtm_name}_krigcorr.tif"
    raw = RAW / "dtms" / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
    return krig if krig.exists() else raw


def find_score_path(dtm_name: str, rung: float) -> Path | None:
    """Locate the cached v0.1 score raster across all per-DTM subdirs."""
    for sub in WP2.iterdir():
        if not sub.is_dir():
            continue
        cand = sub / f"{dtm_name}_{rung:g}m_score.tif"
        if cand.exists():
            return cand
    return None


def load_score_and_dtm(dtm_name: str, rung: float):
    """Load the v0.1 score raster + the DTM rebinned to the SCORE's grid.

    The cached score raster's effective posting may differ from the rung
    label because sag_search_run.py v0.2 sub-sampled Frangi to <=5000 px
    max dim. To match v0.1 slope semantics (slope at the same grid as
    the score), we rebin the DTM to the SCORE's exact shape, NOT to
    the rung posting.

    Returns dict with: score, dtm_r, eff, shape, crs, transform, factor,
    source_score_tif, from_cache.
    """
    score_path = find_score_path(dtm_name, rung)
    if score_path is None:
        return None
    with rasterio.open(score_path) as s:
        score = s.read(1).astype(np.float64)
        if s.nodata is not None:
            score = np.where(score == s.nodata, np.nan, score)
        eff = float(abs(s.transform.a))
        crs = s.crs
        transform = s.transform
        shape = (s.height, s.width)
        score_nodata = s.nodata
    # rebin DTM to SCORE's exact shape (not the rung posting).
    # This ensures slope_deg_map runs at the same posting as the score.
    path = dtm_source(dtm_name)
    with rasterio.open(path) as src:
        res_full = float(src.res[0])
        H_src, W_src = src.height, src.width
        # The score raster's factor relative to the source DTM
        factor = max(1, int(round(H_src / shape[0])))
    with rasterio.open(path) as src:
        dtm_r = src.read(1, out_shape=shape,
                         resampling=Resampling.average).astype(np.float64)
        if src.nodata is not None:
            # exact sentinel match for non-f32 nodata
            dtm_r = np.where(dtm_r == src.nodata, np.nan, dtm_r)
            # f32 sentinel guard (|x|>1e30) for partial-cell averages
            # where the sentinel gets diluted below exact match
            # (NOT the >1000m mask from conventions §8.4 — that's for
            # f32 raw point files where elevation is intrinsically
            # within ±1000m; GeoTIFF DTMs may have offsets, e.g.
            # FECNDITATS2 sits at ~-1700m elevation)
            dtm_r = np.where(np.abs(dtm_r) > 1e30, np.nan, dtm_r)
    return {
        "score": score, "dtm_r": dtm_r, "eff": eff, "shape": shape,
        "crs": crs, "transform": transform, "factor": factor,
        "source_score_tif": str(score_path),
        "from_cache": True,
    }


def peaks_of(score, frac, neigh=FROZEN_NEIGH):
    """v0.1 peak finder: local maxima >= frac*max with neigh kernel."""
    if not np.isfinite(score).any():
        return []
    smax = float(np.nanmax(score))
    if smax <= 0:
        return []
    s_for_max = np.where(np.isfinite(score), score, 0.0)
    mf = maximum_filter(s_for_max, size=neigh, mode="nearest")
    thr = frac * smax
    rr, cc = np.where((s_for_max == mf) & (s_for_max >= thr) & np.isfinite(score))
    return [(int(r), int(c)) for r, c in zip(rr, cc)]


def load_depth_for(dtm: str, rung: float) -> np.ndarray | None:
    """Load the cached depth raster, rebinned to the SCORE's exact shape.

    For DTMs where sag_search_run.py sub-sampled Frangi to <=5000 px,
    the depth raster was written at the rung posting but the score was
    written at the sub-sampled posting. Rebin depth (mean) to the
    score's grid so depth[r, c] at a score peak is in metres.

    Returns None if absent.
    """
    p = find_score_path(dtm, rung)
    if p is None:
        return None
    depth_path = Path(str(p).replace("_score.tif", "_depth.tif"))
    if not depth_path.exists():
        return None
    with rasterio.open(depth_path) as f:
        z = f.read(1).astype(np.float64)
        if f.nodata is not None:
            z = np.where(z == f.nodata, np.nan, z)
        depth_shape = (f.height, f.width)
    score_shape = (p.stat().st_size,)  # placeholder, replaced below
    with rasterio.open(p) as s:
        score_shape = (s.height, s.width)
    if depth_shape == score_shape:
        return z
    # rebin depth to score's shape (scipy zoom, order=1 like sag_search_run.py)
    from scipy.ndimage import zoom
    zr = zoom(z, (score_shape[0] / depth_shape[0],
                   score_shape[1] / depth_shape[1]), order=1)
    return zr.astype(np.float64)


def frangi_blob_area_m2(dtm_r, frangi_path: Path, peak_rc, r_floor: float) -> float:
    """Area in m^2 where Frangi >= 0.5*Frangi_max in a 3*rung-box around the
    peak. Returns NaN if the frangi raster is unavailable."""
    if not frangi_path.exists():
        return float("nan")
    with rasterio.open(frangi_path) as f:
        F = f.read(1).astype(np.float64)
        if f.nodata is not None:
            F = np.where(F == f.nodata, np.nan, F)
    r, c = peak_rc
    H, W = F.shape
    box = int(3 * round(3.0))  # 9 px window (rough scale proxy)
    r0, r1 = max(0, r - box), min(H, r + box + 1)
    c0, c1 = max(0, c - box), min(W, c + box + 1)
    sub = F[r0:r1, c0:c1]
    sub_max = float(np.nanmax(sub)) if np.isfinite(sub).any() else 0.0
    if sub_max <= 0:
        return float("nan")
    n_above = int((sub >= 0.5 * sub_max).sum())
    return float(n_above) * r_floor * r_floor


def load_rille_index():
    """Hurwitz rille shapefile -> projected (x,y) list in Moon_EC (eqc 180).
    Returns GeoDataFrame in Moon_EC metres."""
    import geopandas as gpd
    gdf = gpd.read_file(RILLE_SHP)
    # Source is already Moon_EC eqc central_meridian=180 metres
    return gdf


def build_crater_chain_index(dtm_bbox: tuple):
    """LU5M812TGT craters in longlat inside dtm_bbox, grouped by 1-deg lat
    strip; returns set of (lon, lat) for craters in strips with >=3 craters.

    dtm_bbox = (min_lon, min_lat, max_lon, max_lat)
    """
    cr = pd.read_csv(CRATER_CSV)
    cr = cr[cr["D_eq_km"].between(0.4, 5.0)]
    cr = cr[cr["Latitude"].abs() <= 60.0]
    minx, miny, maxx, maxy = dtm_bbox
    # small buffer
    buf = 0.1
    in_box = cr[(cr["Longitude"] >= minx - buf) & (cr["Longitude"] <= maxx + buf)
                & (cr["Latitude"] >= miny - buf) & (cr["Latitude"] <= maxy + buf)]
    if len(in_box) == 0:
        return set()
    in_box = in_box.copy()
    in_box["lat_strip"] = (in_box["Latitude"] // 1.0).astype(int)
    chain_pts = set()
    for _, g in in_box.groupby("lat_strip"):
        if len(g) >= 3:
            for _, r in g.iterrows():
                chain_pts.add((float(r["Longitude"]), float(r["Latitude"])))
    return chain_pts


def haversine_m(lon1, lat1, lon2, lat2):
    """Great-circle distance in metres (sphere R=1737400)."""
    la1, la2 = math.radians(lat1), math.radians(lat2)
    dlat = la2 - la1
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return MOON_R * c


def rille_min_dist_m(lon, lat, rille_gdf):
    """Minimum distance from (lon, lat) to any Hurwitz rille, in metres.
    Uses shapely nearest-geometry distance via geodesic approx (metres in
    Moon_EC; Moon_EC is eqc 180 so we can use it as a Cartesian proxy
    at the latitude band, but for accuracy we project the query point
    to Moon_EC first)."""
    from shapely.geometry import Point
    # project (lon, lat) into Moon_EC (eqc central_meridian=180)
    tr = Transformer.from_crs(MOON_GEOG, rille_gdf.crs, always_xy=True)
    px, py = tr.transform(lon, lat)
    qp = Point(px, py)
    # distance in Moon_EC metres (close to true metres at small scales)
    s = rille_gdf.geometry
    # vectorised nearest distance
    d = s.distance(qp)
    if len(d) == 0:
        return float("inf")
    return float(d.min())


def chain_min_dist_m(lon, lat, chain_pts):
    """Min distance from (lon, lat) to any chain-strip crater, metres."""
    if not chain_pts:
        return float("inf")
    return min(haversine_m(lon, lat, c[0], c[1]) for c in chain_pts)


def poisson_fp_ci(n_fp: int, area_km2: float):
    """FP/10^4 km^2 point + 95% Poisson CI. Uses chi2.ppf.

    n_fp = 0 -> one-sided upper 95% bound only.
    n_fp >= 1 -> equal-tailed CI on the count, then divided by area.
    """
    if area_km2 <= 0:
        return (float("nan"), float("nan"), float("nan"))
    if n_fp == 0:
        # one-sided upper: chi2.ppf(0.95, 2*0+2)/2 / area
        upper_count = chi2.ppf(0.95, 2) / 2.0
        return (0.0, 0.0, upper_count / area_km2 * 1e4)
    lo_count = chi2.ppf(0.025, 2 * n_fp) / 2.0
    hi_count = chi2.ppf(0.975, 2 * n_fp + 2) / 2.0
    return (n_fp / area_km2 * 1e4,
            lo_count / area_km2 * 1e4,
            hi_count / area_km2 * 1e4)


def discover_dtms_and_rungs() -> list[tuple[str, float]]:
    """Walk wp2_sag/<sub>/<DTM>_<rung>m_score.tif and return sorted unique
    (DTM, rung) pairs."""
    out = set()
    for sub in WP2.iterdir():
        if not sub.is_dir():
            continue
        for f in sub.glob("*_score.tif"):
            m = re.match(r"(.+)_(\d+(?:\.\d+)?)m_score\.tif", f.name)
            if m:
                out.add((m.group(1), float(m.group(2))))
    return sorted(out)


def load_floors() -> dict:
    """per_dtm_floors.csv -> dict dtm_name -> row."""
    df = pd.read_csv(FLOORS_CSV, comment="#")
    return {r["dtm_name"]: r for _, r in df.iterrows()}


def candidate_id(dtm: str, rung: float, rank: int) -> str:
    """Stable unique ID LV-<dtm>-<rung>cm-rank<NN>."""
    rung_cm = int(round(rung * 100))
    return f"LV-{dtm}-{rung_cm:04d}cm-r{rank:03d}"


def transfer_dtm_rung(dtm: str, rung: float, floors_row, rille_gdf,
                      registry_lines: list, debug: bool = False) -> dict:
    """Apply the frozen recipe to one (DTM, rung) pair. Append registry lines
    (text mode) and return a per-pair stats dict."""
    surf = load_score_and_dtm(dtm, rung)
    if surf is None:
        return {"dtm": dtm, "rung_m": rung, "error": "no cached score raster"}
    eff = surf["eff"]
    score = surf["score"]
    dtm_r = surf["dtm_r"]
    transform = surf["transform"]
    crs = surf["crs"]
    valid = np.isfinite(dtm_r)
    area_km2 = float(valid.sum()) * eff * eff / 1e6

    # slope mask at 45 deg (FROZEN)
    slope = slope_deg_map(dtm_r, eff)
    slope_ok = slope >= FROZEN_SLOPE
    masked = np.where(slope_ok & np.isfinite(score), score, 0.0)
    peaks = peaks_of(masked, FROZEN_FRAC)
    if not peaks:
        return {"dtm": dtm, "rung_m": rung, "n_candidates": 0,
                "area_km2": area_km2, "n_above_local_floor": 0,
                "n_tier_B": 0, "n_below_local_floor": 0,
                "top_score": float(np.nanmax(score)) if np.isfinite(score).any() else 0.0,
                "from_cache": True, "source_score_tif": surf["source_score_tif"]}

    # local noise floor (per-DTM) from per_dtm_floors.csv
    local_3sigma = float(floors_row["three_sigma_m"]) if floors_row is not None else float("nan")
    local_Amin = float(floors_row["local_Amin_m"]) if floors_row is not None else float("nan")

    # prepare tier-B lookups: rille, chain (only need to build for the
    # DTM's footprint, not per-peak)
    # DTM bbox in lon/lat (transform gives projected metres; use CRS+transform)
    with rasterio.open(surf["source_score_tif"]) as s:
        bounds = s.bounds
    # transform: projected CRS -> longlat
    tr = Transformer.from_crs(crs, MOON_GEOG, always_xy=True)
    min_lon, min_lat = tr.transform(bounds.left, bounds.bottom)
    max_lon, max_lat = tr.transform(bounds.right, bounds.top)
    # account for central_meridian (some DTMs use central_meridian=0)
    # ensure min/max are ordered
    if min_lon > max_lon:
        min_lon, max_lon = max_lon, min_lon
    if min_lat > max_lat:
        min_lat, max_lat = max_lat, min_lat
    # wrap: if interval crosses +/- 180, normalise by sorting
    dtm_bbox = (min_lon, min_lat, max_lon, max_lat)

    chain_pts = build_crater_chain_index(dtm_bbox)

    # sort peaks by score desc
    depth_arr = load_depth_for(dtm, rung)  # parallel depth raster
    peak_records = []
    for r, c in peaks:
        x, y = transform * (c + 0.5, r + 0.5)
        # transform projected -> lon/lat
        lon, lat = tr.transform(x, y)
        # amplitude = depression depth (filled - raw) at peak pixel
        depth_m = float(depth_arr[r, c]) if (depth_arr is not None
                                              and np.isfinite(depth_arr[r, c])) else float("nan")
        # score at peak pixel
        score_v = float(score[r, c])
        # span proxy: load frangi raster and compute blob area
        frangi_path = Path(surf["source_score_tif"].replace("_score.tif", "_frangi.tif"))
        span_m2 = frangi_blob_area_m2(dtm_r, frangi_path, (r, c), eff)
        peak_records.append({
            "row": r, "col": c, "lon": lon, "lat": lat,
            "x_m": float(x), "y_m": float(y),
            "score": score_v,
            "depth_proxy_m": depth_m,
            "span_m2": span_m2,
        })
    peak_records.sort(key=lambda d: -d["score"])

    # tier promotion
    # Tier discipline (R1, conservative):
    #   - below-local-floor candidates stay tier C (no multi-method
    #     promotion; the morphometric signal is too weak to combine with
    #     another line of evidence).
    #   - above-floor candidates get tier B if a rille or chain-strip
    #     crater lies within 100 m.
    #   - tier A never assigned in P3.1c.
    n_tier_B = 0
    n_above = 0
    n_below = 0
    n_above_FP = 0  # for FP rate
    registry_local = []
    for rank, p in enumerate(peak_records, start=1):
        cid = candidate_id(dtm, rung, rank)
        amp = p["depth_proxy_m"]
        below_floor = (not math.isnan(local_Amin)) and (amp < local_Amin)
        # Always compute distances (used in registry's confusion field too)
        d_rille = rille_min_dist_m(p["lon"], p["lat"], rille_gdf)
        d_chain = chain_min_dist_m(p["lon"], p["lat"], chain_pts)
        # default tier C
        tier = "C"
        methods = "morphometry"
        confusion = ""
        if not below_floor:
            # only above-floor candidates are eligible for tier B
            if d_rille <= B_RADIUS_M:
                tier = "B"
                methods = "morphometry|rille"
                confusion = f"rille/0m"
            elif d_chain <= B_RADIUS_M:
                tier = "B"
                methods = "morphometry|crater-chain"
                confusion = f"chain/0m"
        if tier == "B":
            n_tier_B += 1
        if below_floor:
            n_below += 1
        else:
            n_above += 1
            # FPs are above-floor candidates NOT within 100 m of a catalogued
            # pit. We compute the FP status against this DTM's catalogued pit
            # list below.
        registry_local.append({
            "candidate_id": cid, "dtm": dtm, "rung_m": rung, "rank": rank,
            "lon": p["lon"], "lat": p["lat"], "x_m": p["x_m"], "y_m": p["y_m"],
            "score": p["score"], "sag_amp_m": amp, "span_m2": p["span_m2"],
            "local_3sigma_m": local_3sigma, "local_Amin_m": local_Amin,
            "d_rille_m": d_rille, "d_chain_m": d_chain,
            "tier": tier, "methods": methods, "confusion": confusion,
            "below_local_floor": below_floor,
        })

    # determine FP count: above-floor peaks NOT within 100m of a catalogued pit
    pit_rows = pd.read_csv(PIT_CATALOG)
    this_dtm_pits = [(float(r.Latitude), float(r.Longitude)) for _, r in
                     pit_rows[pit_rows["DTM_NAME"] == dtm].iterrows()]
    n_fp = 0
    for rec in registry_local:
        if rec["below_local_floor"]:
            continue  # not counted as FP
        is_near_pit = any(
            haversine_m(rec["lon"], rec["lat"], plon, plat) <= FROZEN_PIT_MATCH_RADIUS_M
            for plat, plon in this_dtm_pits
        )
        if not is_near_pit:
            n_fp += 1
    n_tp = 0
    for plat, plon in this_dtm_pits:
        if any(
            (not rec["below_local_floor"]) and
            haversine_m(rec["lon"], rec["lat"], plon, plat) <= FROZEN_PIT_MATCH_RADIUS_M
            for rec in registry_local
        ):
            n_tp += 1

    # write registry lines (text mode; one CSV row per candidate)
    for rec in registry_local:
        notes = "below-local-floor" if rec["below_local_floor"] else ""
        if rec["tier"] == "B":
            notes = (notes + "; " if notes else "") + "tier-B multi-method"
        # confusion field
        conf = rec["confusion"] or f"n/a|rille={int(rec['d_rille_m'])}m|chain={int(rec['d_chain_m'])}m"
        # methods field already populated
        registry_lines.append(",".join([
            rec["candidate_id"],
            f"{rec['lon']:.6f}",
            f"{rec['lat']:.6f}",
            rec["dtm"],
            f"{rec['span_m2']:.1f}" if not math.isnan(rec["span_m2"]) else "n/a",
            f"{rec['sag_amp_m']:.3f}",
            f"{rec['score']:.4f}",
            conf,
            rec["methods"],
            rec["tier"],
            "ACTIVE",
            date.today().isoformat(),
            date.today().isoformat(),
            f"01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json#"
            f"{rec['candidate_id']}",
            notes or "frozen-frac=0.20 slope=45 neigh=5",
        ]))

    return {
        "dtm": dtm, "rung_m": rung, "eff_m": eff, "shape": list(surf["shape"]),
        "from_cache": True, "source_score_tif": surf["source_score_tif"],
        "n_candidates": len(registry_local),
        "n_above_local_floor": n_above, "n_below_local_floor": n_below,
        "n_tier_B": n_tier_B, "n_fp": n_fp, "n_tp": n_tp,
        "top_score": float(peak_records[0]["score"]) if peak_records else 0.0,
        "local_3sigma_m": local_3sigma, "local_Amin_m": local_Amin,
        "area_km2": area_km2, "n_pits_in_dtm": len(this_dtm_pits),
        "registry_count": len(registry_local),
    }


def score_to_depth(score, dtm_r, r, c):
    """DEPRECATED — use load_depth_for() instead. Kept as a stub for any
    external callers; in this module, depth is loaded directly from the
    cached depth raster (parallel to the score raster)."""
    return float("nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", type=Path, default=TRANSFER_DIR)
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    ap.add_argument("--dtms", nargs="+", default=None,
                    help="restrict to these DTMs (default: all 10 on-disk)")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    floors = load_floors()
    rille_gdf = load_rille_index()
    print(f"[init] rille GDF: {len(rille_gdf)} features; "
          f"floors table: {len(floors)} dtms", flush=True)

    pairs = discover_dtms_and_rungs()
    if args.dtms:
        pairs = [p for p in pairs if p[0] in args.dtms]
    print(f"[init] processing {len(pairs)} (DTM, rung) pairs across "
          f"{len(set(p[0] for p in pairs))} unique DTMs", flush=True)

    # registry: read existing skeleton; preserve header & comments
    with open(args.registry) as f:
        reg_text = f.read()
    reg_lines = reg_text.rstrip("\n").split("\n")
    # find last comment line / blank line
    insert_at = len(reg_lines)
    registry_lines = []  # new data rows to append
    pair_results = []
    for dtm, rung in pairs:
        floors_row = floors.get(dtm)
        if floors_row is None:
            print(f"[skip] {dtm} rung {rung:g} m: no entry in per_dtm_floors.csv",
                  flush=True)
            pair_results.append({"dtm": dtm, "rung_m": rung,
                                 "error": "no per-DTM floor in CSV"})
            continue
        t1 = time.time()
        r = transfer_dtm_rung(dtm, rung, floors_row, rille_gdf, registry_lines)
        r["runtime_s"] = round(time.time() - t1, 2)
        pair_results.append(r)
        if "error" in r:
            print(f"[err] {dtm} rung {rung:g} m: {r['error']}", flush=True)
        else:
            print(f"[ok] {dtm} rung {rung:g} m: {r['n_candidates']} candidates, "
                  f"{r['n_above_local_floor']} above floor, {r['n_tier_B']} tier-B, "
                  f"FP={r['n_fp']} TP={r['n_tp']} | area={r['area_km2']:.2f} km^2 | "
                  f"top={r['top_score']:.2f} | {r['runtime_s']} s", flush=True)

    # build per-DTM aggregate (across rungs)
    per_dtm = {}
    for r in pair_results:
        if "error" in r and "n_candidates" not in r:
            per_dtm.setdefault(r["dtm"], {"error": r.get("error", "unknown")})
            continue
        d = per_dtm.setdefault(r["dtm"], {
            "rungs": [], "n_candidates": 0, "n_above_local_floor": 0,
            "n_below_local_floor": 0, "n_tier_B": 0, "n_fp": 0, "n_tp": 0,
            "area_km2": 0.0, "top_score": 0.0, "local_Amin_m": r.get("local_Amin_m"),
            "local_3sigma_m": r.get("local_3sigma_m"),
        })
        d["rungs"].append(r["rung_m"])
        d["n_candidates"] += r["n_candidates"]
        d["n_above_local_floor"] += r["n_above_local_floor"]
        d["n_below_local_floor"] += r["n_below_local_floor"]
        d["n_tier_B"] += r["n_tier_B"]
        d["n_fp"] += r["n_fp"]
        d["n_tp"] += r["n_tp"]
        d["area_km2"] += r["area_km2"]
        if r["top_score"] > d["top_score"]:
            d["top_score"] = r["top_score"]
    # per-DTM FP/10^4 km^2 + CI
    for dtm, d in per_dtm.items():
        if "error" in d:
            continue
        pt, lo, hi = poisson_fp_ci(d["n_fp"], d["area_km2"])
        d["fp_per_1e4km2"] = pt
        d["fp_per_1e4km2_ci95_lo"] = lo
        d["fp_per_1e4km2_ci95_hi"] = hi
        d["rungs"] = sorted(set(d["rungs"]))

    # per-rung aggregate
    per_rung = {}
    for r in pair_results:
        if "n_candidates" not in r:
            continue
        key = r["rung_m"]
        d = per_rung.setdefault(key, {"n_candidates": 0, "n_above_local_floor": 0,
                                      "n_tier_B": 0, "n_fp": 0, "n_tp": 0,
                                      "area_km2": 0.0})
        d["n_candidates"] += r["n_candidates"]
        d["n_above_local_floor"] += r["n_above_local_floor"]
        d["n_tier_B"] += r["n_tier_B"]
        d["n_fp"] += r["n_fp"]
        d["n_tp"] += r["n_tp"]
        d["area_km2"] += r["area_km2"]
    for rung, d in per_rung.items():
        pt, lo, hi = poisson_fp_ci(d["n_fp"], d["area_km2"])
        d["fp_per_1e4km2"] = pt
        d["fp_per_1e4km2_ci95_lo"] = lo
        d["fp_per_1e4km2_ci95_hi"] = hi

    # aggregate
    total_cands = sum(d.get("n_candidates", 0) for d in per_dtm.values())
    total_above = sum(d.get("n_above_local_floor", 0) for d in per_dtm.values())
    total_below = sum(d.get("n_below_local_floor", 0) for d in per_dtm.values())
    total_tierB = sum(d.get("n_tier_B", 0) for d in per_dtm.values())
    total_fp = sum(d.get("n_fp", 0) for d in per_dtm.values())
    total_tp = sum(d.get("n_tp", 0) for d in per_dtm.values())
    total_area = sum(d.get("area_km2", 0.0) for d in per_dtm.values())
    # N=10/649 honesty: count of DTM sites that have NAC DTM on disk
    n_10 = len(floors)
    n_score_raster = len(set(p[0] for p in pairs))
    n_no_raster = sorted(set(floors.keys()) - set(p[0] for p in pairs))

    agg_pt, agg_lo, agg_hi = poisson_fp_ci(total_fp, total_area)

    summary = {
        "generated": date.today().isoformat(),
        "scope_banner": f"N={n_10}/649 (10 good-tier DTMs on disk of 649 in scope; "
                        f"{n_score_raster} have cached v0.1 score rasters; "
                        f"{len(n_no_raster)} are skipped for missing score raster: {n_no_raster})",
        "frozen_calibration": {
            "score_frac": FROZEN_FRAC, "slope_deg": FROZEN_SLOPE,
            "neigh": FROZEN_NEIGH, "frangi_sigmas_m": list(FROZEN_SIGMAS),
            "pit_match_radius_m": FROZEN_PIT_MATCH_RADIUS_M,
            "tier_B_radius_m": B_RADIUS_M,
            "fill": "planchon_darboux (fix_flats=True; baked into cached rasters)",
            "source_freeze": "01_WORKSPACE/data/outputs/wp2_sag/transfer/calibration_transqpit1.json",
        },
        "tier_discipline": {
            "A": "NOT assigned in P3.1c (Phase-5 skeptic-gated; requires "
                 "gravity/thermal/illumination agreement)",
            "B": "multi-method within this task: rille intersection within "
                 f"{B_RADIUS_M:g} m (Hurwitz 2013) OR LU5M812TGT crater-chain "
                 "intersection within 100 m (1-deg lat strip with >=3 craters)",
            "C": "single-method (sag score only) candidate",
        },
        "per_rung": {f"{k:g}": v for k, v in per_rung.items()},
        "per_dtm": {d: v for d, v in sorted(per_dtm.items())},
        "aggregate": {
            "n_dtms_with_score_raster": n_score_raster,
            "n_dtms_skipped_no_raster": len(n_no_raster),
            "dtms_skipped": n_no_raster,
            "n_dtm_rung_pairs": len(pair_results),
            "n_candidates": total_cands,
            "n_above_local_floor": total_above,
            "n_below_local_floor": total_below,
            "n_tier_B": total_tierB,
            "n_tier_A": 0,
            "n_fp": total_fp,
            "n_tp": total_tp,
            "total_area_km2": total_area,
            "fp_per_1e4km2": agg_pt,
            "fp_per_1e4km2_ci95_lo": agg_lo,
            "fp_per_1e4km2_ci95_hi": agg_hi,
            "fp_per_1e4km2_n_above_floor": total_above,
        },
        "pair_results": pair_results,
        "registry_rows_added": len(registry_lines),
        "runtime_s": round(time.time() - t0, 1),
    }
    out_json = args.outdir / "transfer_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[out] {out_json}")
    print(f"[agg] N={n_10}/649; {n_score_raster} DTMs with rasters, "
          f"{len(n_no_raster)} skipped; "
          f"{total_cands} candidates ({total_above} above floor, {total_below} below), "
          f"{total_tierB} tier-B, 0 tier-A | "
          f"FP {total_fp}/{total_area:.2f} km^2 = "
          f"{agg_pt:.2f}/1e4km2 [95% CI {agg_lo:.2f}, {agg_hi:.2f}] | "
          f"{summary['runtime_s']} s", flush=True)

    # append registry rows
    if registry_lines:
        # verify the last line of reg_text is the provenance comment
        # (we keep all comments, then append data rows)
        new_text = reg_text.rstrip("\n") + "\n" + "\n".join(registry_lines) + "\n"
        with open(args.registry, "w") as f:
            f.write(new_text)
        print(f"[out] appended {len(registry_lines)} rows -> {args.registry}")
    else:
        print(f"[out] NO new registry rows (no candidates produced)")


if __name__ == "__main__":
    main()
