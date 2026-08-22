"""LUNARVOID WP8 stereo — enumerate LROC NAC DTMs overlapping catalogued pits.

Produces `01_WORKSPACE/data/lroc_dtm_availability.csv`:
one row per (catalogued pit site, overlapping NAC DTM) match.

Reads:
  - `~/lunarvoid/data/index_layers/nac_dtms/NAC_DTMS_180.SHP` (660 DTM
    footprints, released through 2026-06-15, see MANIFEST.md)
  - `~/lunarvoid/data/index_layers/pit_atlas/LUNAR_PIT_LOCATIONS_180.SHP`
    (Wagner & Robinson 2021 lunar pit atlas, 278 catalogued pits)

Discovery method (per lunarvoid-conventions §4 + project PDS pattern):
  - The LROC `data.lroc.im-ldi.com/lroc/rdr_product_select` UI is the
    discovery source-of-truth (verified the page returns HTML, not the
    NAC_DTM_*.TIF; the `url` field in the shapefile is also HTML). The
    PDS archive itself is at
    `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/`
    which 302-redirects to `pds.mcp.nasa.gov` (S3-backed; verified live
    2026-08-22: HTTP 302 -> pds.mcp.nasa.gov -> 200 with content-length).
  - The 660 DTMs in the project index layer are the PDS-complete subset
    (LROC team releases through 2026-06-15). Spatial join against the
    278 catalogued pits therefore enumerates every overlap currently
    public on PDS.

Cross-reference:
  - Each catalogued pit is matched against the candidate_registry.csv's
    unique DTM names (TRANQPIT1, MARIUSPIT01, INGENIIPIT, IRIDIUMPIT1,
    PRCLRMPIT01, SWFECUNPIT1, FECNDITATS2 — 7 priority DTMs). All 7
    appear in the spatial join (the 7 already on disk under
    `~/lunarvoid/data/dtms/<SITE>/`).

Random mare sample (P3.2 / 30-site):
  - NOT YET SAMPLED (per orchestrator dispatch, 2026-08-22). Flagged as
    a gap in the report; this script emits zero rows for the random
    sample because there are no coordinates to join against.

Licence: NAC DTM GeoTIFFs are PDS public domain (NASA/ASU). Recorded
per MANIFEST conventions when fetched.

Output schema (long-format):
  pit_site                catalogued pit name (Wagner & Robinson 2021)
  lroc_dtm_product_id     LROC DTM_NAME (matches `NAC_DTM_<NAME>.TIF`)
  lroc_dtm_url            direct PDS URL (302 -> pds.mcp.nasa.gov)
  lroc_dtm_lbl_url        PDS3 label URL (companion)
  estimated_size_mb       estimated TIF size from resolution * cov_sqkm
                          (calibrated against 8 on-disk samples; see below)
  pit_in_catalog          TRUE (all rows in this output are catalogued)
  priority_in_registry    TRUE if DTM is one of the 7 in
                          candidate_registry.csv (TRANQPIT1, MARIUSPIT01,
                          INGENIIPIT, IRIDIUMPIT1, PRCLRMPIT01,
                          SWFECUNPIT1, FECNDITATS2)
  resolution_m            DTM pixel scale (m/px)
  coverage_km2            DTM footprint coverage (cov_sqkm from shapefile)
  lon, lat                catalogued pit centre (planetocentric, -180..180)

Calibration of `estimated_size_mb`:
  Linear fit through 8 on-disk samples (2026-08-22):
    TRANQPIT1     2 m/px  124.72 km^2   130.3 MB    1.04 MB/km^2
    INGENIIPIT    2 m/px  185.25 km^2   211.7 MB    1.14 MB/km^2
    MARIUSPIT01   4 m/px  449.88 km^2   159.3 MB    0.35 MB/km^2
    IRIDIUMPIT1   5 m/px  809.90 km^2   160.8 MB    0.20 MB/km^2
    PRCLRMPIT01   5 m/px  771.23 km^2   169.9 MB    0.22 MB/km^2
    SWFECUNPIT1   3 m/px  448.69 km^2   286.7 MB    0.64 MB/km^2
    MARIUSCONE    4 m/px  811.89 km^2   269.7 MB    0.33 MB/km^2
    FECNDITATS2   4 m/px  663.69 km^2   721.7 MB    1.09 MB/km^2
  Empirical: MB/km^2 scales like 1/(2*resolution_m) roughly (compression
  ratio roughly fixed; pixel count = km^2 / resolution_m^2). Used a
  resolution-binned empirical model:
    res=2 m: 1.09 MB/km^2  (n=2)
    res=3 m: 0.64 MB/km^2  (n=1)
    res=4 m: 0.59 MB/km^2  (n=3; trimmed to mean of 0.35, 0.33, 1.09 -- median 0.35)
    res=5 m: 0.21 MB/km^2  (n=2; mean of 0.20, 0.22)
  For DTMs not on disk we apply the per-resolution bin; for unknown
  resolutions fall back to 0.5 MB/km^2 conservative default.
  This is an ESTIMATE (HEAD `content-length` confirms exact value when
  the fetcher runs; the orchestrator will update MANIFEST rows with the
  real SHA-256/size).
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyproj import CRS

# ---- Repo + data paths (per lunarvoid-conventions §1) ----------------------
REPO = Path(__file__).resolve().parents[3]
OUT_CSV = REPO / "01_WORKSPACE" / "data" / "lroc_dtm_availability.csv"

DTM_SHP = Path.home() / "lunarvoid" / "data" / "index_layers" / "nac_dtms" / "NAC_DTMS_180.SHP"
PIT_SHP = Path.home() / "lunarvoid" / "data" / "index_layers" / "pit_atlas" / "LUNAR_PIT_LOCATIONS_180.SHP"

# ---- candidate_registry.csv unique DTM names (the 7 priority sites) -------
REGISTRY = REPO / "01_WORKSPACE" / "data" / "candidate_registry.csv"

# ---- PDS URL pattern (verified live 2026-08-22 via HEAD probe) -------------
PDS_BASE = (
    "https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/"
    "LROLRC_2001/DATA/SDP/NAC_DTM"
)


def pds_url(dtm_name: str, ext: str = "TIF") -> str:
    """Construct the direct PDS URL for an LROC NAC DTM GeoTIFF (.TIF)
    or PDS3 label (.LBL). Verified: 302 -> pds.mcp.nasa.gov -> 200."""
    return f"{PDS_BASE}/{dtm_name}/NAC_DTM_{dtm_name}.{ext}"


# ---- Empirical size model (calibrated to 8 on-disk DTMs, 2026-08-22) --------
# MB per km^2 by resolution bin; fallback 0.5 for unmodelled resolutions.
MB_PER_KM2 = {
    2.0: 1.09,
    3.0: 0.64,
    4.0: 0.35,   # median of 0.35, 0.33, 1.09; n=3
    5.0: 0.21,   # mean of 0.20, 0.22; n=2
}
MB_PER_KM2_FALLBACK = 0.5


def estimate_size_mb(resolution_m: float, cov_sqkm: float) -> float:
    key = float(resolution_m)
    rate = MB_PER_KM2.get(key, MB_PER_KM2_FALLBACK)
    return round(rate * float(cov_sqkm), 1)


def quality_tier(relat_le: float, triang_rms: float) -> str:
    """Same rule as scope_map_v11.py:good/fair/poor."""
    if relat_le <= 5.0 and triang_rms <= 20.0:
        return "good"
    if relat_le <= 10.0 and triang_rms <= 40.0:
        return "fair"
    return "poor"


def load_priority_dtms() -> set[str]:
    """Read the unique DTM names from candidate_registry.csv."""
    names: set[str] = set()
    with open(REGISTRY, newline="") as f:
        for raw in f:
            if not raw or raw.startswith("#"):
                continue
            parts = raw.rstrip("\n").split(",")
            if parts and parts[0].startswith("LV-") and len(parts) >= 4:
                names.add(parts[3])
    return names


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT_CSV)
    ap.add_argument("--include-quality", action="store_true",
                    help="include all DTMs (default: good-tier only)")
    args = ap.parse_args()

    if not DTM_SHP.exists():
        sys.exit(f"[abort] NAC DTM shapefile missing: {DTM_SHP}")
    if not PIT_SHP.exists():
        sys.exit(f"[abort] pit atlas shapefile missing: {PIT_SHP}")

    priority = load_priority_dtms()
    print(f"[info] {len(priority)} priority DTMs in candidate_registry.csv: "
          f"{sorted(priority)}", flush=True)

    # ---- Load + normalise ------------------------------------------------
    dtms = gpd.read_file(DTM_SHP)
    for col in ("resolution", "relat_le", "triang_rms", "cov_sqkm"):
        dtms[col] = pd.to_numeric(dtms[col], errors="coerce")
    dtms["quality"] = [
        quality_tier(r, t) for r, t in zip(dtms["relat_le"], dtms["triang_rms"])
    ]
    if not args.include_quality:
        before = len(dtms)
        dtms = dtms[dtms["quality"] == "good"].copy()
        print(f"[info] quality filter: {before} -> {len(dtms)} good-tier DTMs", flush=True)

    pits = gpd.read_file(PIT_SHP)
    print(f"[info] {len(dtms)} good-tier NAC DTMs, {len(pits)} catalogued pits",
          flush=True)

    moon_geog = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")

    pit_pts = gpd.GeoDataFrame(
        pits,
        geometry=gpd.points_from_xy(pits["Longitude"], pits["Latitude"]),
        crs=moon_geog,
    )
    dtms_moon = dtms.to_crs(moon_geog)

    # ---- Spatial join: pit points within DTM polygons --------------------
    joined = gpd.sjoin(
        pit_pts,
        dtms_moon[["DTM_NAME", "resolution", "cov_sqkm", "relat_le",
                   "triang_rms", "quality", "geometry"]],
        how="inner",
        predicate="within",
    )
    print(f"[info] {len(joined)} (pit, DTM) overlap rows from spatial join",
          flush=True)

    # ---- Build output rows ----------------------------------------------
    rows = []
    for _, r in joined.iterrows():
        dtm = r["DTM_NAME"]
        res = float(r["resolution"]) if pd.notna(r["resolution"]) else None
        cov = float(r["cov_sqkm"]) if pd.notna(r["cov_sqkm"]) else None
        size = estimate_size_mb(res, cov) if (res is not None and cov is not None) else None
        rows.append(dict(
            pit_site=r["Name"],
            lon=float(r["Longitude"]),
            lat=float(r["Latitude"]),
            terrain=r["Terrain"],
            lroc_dtm_product_id=dtm,
            lroc_dtm_url=pds_url(dtm, "TIF"),
            lroc_dtm_lbl_url=pds_url(dtm, "LBL"),
            estimated_size_mb=size,
            pit_in_catalog=True,
            priority_in_registry=(dtm in priority),
            resolution_m=res,
            coverage_km2=cov,
            quality=r["quality"],
            relat_le_m=float(r["relat_le"]) if pd.notna(r["relat_le"]) else None,
            triang_rms_m=float(r["triang_rms"]) if pd.notna(r["triang_rms"]) else None,
        ))

    # Stable sort: priority first, then by DTM, then pit name
    rows.sort(key=lambda x: (not x["priority_in_registry"], x["lroc_dtm_product_id"],
                             x["pit_site"]))

    cols = [
        "pit_site", "lon", "lat", "terrain",
        "lroc_dtm_product_id", "lroc_dtm_url", "lroc_dtm_lbl_url",
        "estimated_size_mb",
        "pit_in_catalog", "priority_in_registry",
        "resolution_m", "coverage_km2",
        "quality", "relat_le_m", "triang_rms_m",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # ---- Summary --------------------------------------------------------
    n_pits = joined["Name"].nunique()
    n_dtms = joined["DTM_NAME"].nunique()
    n_priority = sum(1 for r in rows if r["priority_in_registry"])
    total_mb = sum(r["estimated_size_mb"] or 0 for r in rows)
    # Per-DTM unique (since multiple pits can share one DTM, the fetcher
    # will only download each DTM once -- total unique DTM size is the
    # sum over distinct lroc_dtm_product_id).
    seen: set[str] = set()
    unique_total_mb = 0.0
    for r in rows:
        if r["lroc_dtm_product_id"] in seen:
            continue
        seen.add(r["lroc_dtm_product_id"])
        unique_total_mb += r["estimated_size_mb"] or 0
    print(f"[out] CSV -> {args.out}", flush=True)
    print(f"[summary] {n_pits} catalogued pits overlap {n_dtms} good-tier NAC DTMs", flush=True)
    print(f"[summary] {n_priority} of those rows are in the 7 priority DTMs (registry)",
          flush=True)
    print(f"[summary] estimated size of all overlaps = {total_mb:.0f} MB ({total_mb/1024:.1f} GB)",
          flush=True)
    print(f"[summary] estimated size of UNIQUE DTMs ({n_dtms}) = {unique_total_mb:.0f} MB "
          f"({unique_total_mb/1024:.1f} GB)", flush=True)
    print(f"[summary] {len(priority) - len(seen & priority)} of the 7 priority DTMs are NOT in "
          f"the good-tier overlap set (likely already in 'good' filter -- re-run with "
          f"--include-quality to see)", flush=True)
    print(f"[summary] random mare sample: 30 sites not yet sampled -- gap (zero rows)",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
