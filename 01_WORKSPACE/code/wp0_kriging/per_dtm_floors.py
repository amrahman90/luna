"""SLICE P3.1a — per-DTM Z2-scale noise floors for the LUNARVOID transfer set.

Extends the Task-6 noise-floor method (code/wp0_kriging/noise_floor.py) and
applies it per-DTM to every good-tier NAC DTM in the transfer set. The
transfer set in this session is the intersection of the scope-map v1.1
good-tier target list with the NAC DTMs that are present on disk under
~/lunarvoid/data/dtms/.

Output:
  01_WORKSPACE/data/outputs/wp0_kriging/per_dtm_floors.csv

Per row: dtm_name, site, lon_min, lon_max, lat_min, lat_max, n_panels,
pooled_rms_m, three_sigma_m, panel_min_rms, panel_max_rms,
local_Amin_m (= 3 x pooled_rms; project convention; flag in the column
header), mtime.

Kriging-corrected DTMs are preferred where available (preserves parity
with Task 6 which used TRANQPIT1/MARIUSPIT01 krigcorr inputs); for DTMs
without a krigcorr file, the raw NAC DTM is used and the skip logic
records the source-file choice in mtime provenance. SKIP any DTM whose
source file is missing or unreadable; log skips.

Seed 42 throughout; f32 sentinel: any |x| > 1000 m -> NaN.

CLI:
  per_dtm_floors.py [--out CSV] [--summary-out JSON]
                    [--min-panels N] [--scope-map CSV]
                    [--dtm-root DIR] [--outputs-root DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pyproj import Transformer

# reuse the Task-6 pipeline: panel extraction, residual variants, sag-band
# DoG — do NOT reimplement. Loaded lazily so a failure here is loud.
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code"))
from wp0_kriging import noise_floor  # noqa: E402

GEOD = noise_floor.GEOD  # "+proj=longlat +R=1737400 +no_defs"
DEFAULT_DTM_ROOT = Path.home() / "lunarvoid" / "data" / "dtms"
DEFAULT_OUT_ROOT = Path.home() / "lunarvoid" / "data" / "outputs"
DEFAULT_CRATER_CSV = Path.home() / "lunarvoid" / "data" / "index_layers" / "craters_lu5m812tgt" / "craters_0p4_5km_pm60.csv.gz"
DEFAULT_RILLE_SHP = Path.home() / "lunarvoid" / "data" / "index_layers" / "hurwitz_rilles" / "shapefile" / "SinuousRilles_obs.shp"
DEFAULT_SCOPE_MAP = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_scope_map_v11" / "target_ranking.csv"
DEFAULT_OUT_CSV = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_kriging" / "per_dtm_floors.csv"
DEFAULT_OUT_SUMMARY = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_kriging" / "per_dtm_floors_summary.json"

# minimum number of panels per DTM (project convention for P3.1a)
DEFAULT_MIN_PANELS = 4

# Project-convention label for local_Amin column header
LOCAL_AMIN_LABEL = "local_Amin_m_=_3x_pooled_rms_(project_convention)"


class Args:
    """Minimal argparse-like namespace that satisfies noise_flow.run_dtm."""

    def __init__(self, pit_list):
        # panel selection (mirror Task-6 defaults; min panels raised to 4
        # for P3.1a per project convention)
        self.slope_max = 2.0
        self.flat_frac = 0.98
        self.boxcar_px = 50
        self.nodata_max_frac = 0.05
        self.panel_sizes = [2000, 1500, 1200, 1000]
        self.min_km2 = 1.0
        self.cand_step = 250.0
        # exclusions
        self.pit_buffer = 3000.0
        self.crater_buffer = 250.0
        self.rille_buffer = 1000.0
        self.excl_cell = 100.0
        # detrend + sag band (preserved from Task 6)
        self.hp_window = 300.0
        self.sag_lo = 60.0
        self.sag_hi = 300.0
        self.sag_margin = 300.0
        # populated by main()
        self.pit = pit_list
        self.crater_csv = str(DEFAULT_CRATER_CSV) if DEFAULT_CRATER_CSV.exists() else None
        self.rille_shp = str(DEFAULT_RILLE_SHP) if DEFAULT_RILLE_SHP.exists() else None


def _find_source(dtm_name: str, dtm_root: Path, out_root: Path) -> tuple[Path, str] | None:
    """Return (path, source_label) for the best available NAC DTM, or None.

    Preference: krigcorr (in outputs) -> raw NAC DTM (in dtms). Skips are
    logged with reason in the caller; this function only resolves the path.
    """
    krig = out_root / dtm_name / f"NAC_DTM_{dtm_name}_krigcorr.tif"
    if krig.exists():
        return krig, "krigcorr"
    raw = dtm_root / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
    if raw.exists():
        return raw, "raw"
    return None


def _dtm_lonlat_window(path: Path) -> tuple[float, float, float, float]:
    """Compute the DTM footprint in Moon geographic lon/lat (-180..180).

    NAC DTMs use local equirectangular with central meridian varying per
    frame, so we transform the four corners via the DTM's CRS (skill §3).
    """
    with rasterio.open(path) as src:
        b = src.bounds
        crs = src.crs
    to_geog = Transformer.from_crs(crs, GEOD, always_xy=True)
    xs = [b.left, b.right, b.left, b.right]
    ys = [b.bottom, b.bottom, b.top, b.top]
    lons, lats = to_geog.transform(xs, ys)
    # normalise to -180..180
    lons = np.asarray(lons, float)
    lats = np.asarray(lats, float)
    lons = ((lons + 180.0) % 360.0) - 180.0
    return float(lons.min()), float(lons.max()), float(lats.min()), float(lats.max())


def _per_panel_rms(rows: list[dict], dtm: str) -> tuple[float, float]:
    """Min and max of per-panel sag-band RMS across the panels for one DTM.

    `rows` is the per-panel + POOLED list returned by noise_floor.run_dtm.
    Each panel produces two rows (poly2, hp300); we dedupe by panel_id
    since the DoG RMS is identical for both variants by construction.
    """
    per_panel = {}
    for r in rows:
        if r.get("dtm") != dtm:
            continue
        pid = r.get("panel_id", "")
        if pid == "POOLED":
            continue
        rms = r.get("sagband_rms_m")
        if rms is None or not np.isfinite(rms):
            continue
        per_panel[pid] = float(rms)
    if not per_panel:
        return float("nan"), float("nan")
    return float(min(per_panel.values())), float(max(per_panel.values()))


def _pit_lonlat(pit_name: str) -> tuple[float, float] | None:
    """Resolve a pit atlas entry name -> (lon_360, lat)."""
    pit_shp = Path.home() / "lunarvoid" / "data" / "index_layers" / "pit_atlas" / "LUNAR_PIT_LOCATIONS_180.SHP"
    if not pit_shp.exists():
        return None
    try:
        import geopandas as gpd
    except Exception:
        # silent by design: optional-dependency probe — geopandas missing
        # just disables pit-name lookup, caller falls back to None
        return None
    g = gpd.read_file(pit_shp)
    row = g[g["Name"] == pit_name]
    if row.empty:
        return None
    lon = float(row.iloc[0]["Longitude"])
    lat = float(row.iloc[0]["Latitude"])
    lon_360 = lon if lon >= 0 else lon + 360.0
    return lon_360, lat


def _pit_list_for_dtm(pit_names_cell: str) -> list[list[float]]:
    """Parse the scope-map pit_names cell (semicolon-separated names) into
    a list of [lon, lat] pairs in 0..360 (Task-6 noise_floor convention)."""
    if not isinstance(pit_names_cell, str) or not pit_names_cell.strip():
        return []
    out = []
    for nm in pit_names_cell.split(";"):
        nm = nm.strip()
        if not nm:
            continue
        ll = _pit_lonlat(nm)
        if ll is None:
            print(f"[pit] name not in pit atlas: {nm!r} (skipped for exclusion)")
            continue
        out.append([ll[0], ll[1]])
    return out


def run_one(dtm_name: str, scope_row: pd.Series, args_root) -> dict | None:
    """Run Task-6 noise-floor method on a single DTM.

    Returns the per-DTM row dict, or None on skip (with reason logged).
    """
    src = _find_source(dtm_name, args_root.dtm_root, args_root.out_root)
    if src is None:
        print(f"[skip] {dtm_name}: no NAC DTM under {args_root.dtm_root} or krigcorr under {args_root.out_root}")
        return None
    path, source_label = src
    try:
        size = path.stat().st_size
    except OSError as e:
        print(f"[skip] {dtm_name}: source {path} unreadable ({e})")
        return None
    print(f"\n=== {dtm_name} (source={source_label}, {size/1e6:.1f} MB) ===")

    pit_list = _pit_list_for_dtm(scope_row.get("pit_names", ""))
    if pit_list:
        print(f"[pit] {len(pit_list)} pit(s) -> {pit_list} (buffer {Args(pit_list).pit_buffer} m)")
    args = Args(pit_list)

    t0 = time.time()
    try:
        rows, hist = noise_floor.run_dtm(path, dtm_name, args)
    except SystemExit as e:
        print(f"[skip] {dtm_name}: noise_floor.run_dtm raised SystemExit ({e})")
        return None
    except Exception as e:
        print(f"[skip] {dtm_name}: noise_floor.run_dtm raised {type(e).__name__}: {e}")
        return None
    dt = time.time() - t0

    if len(hist["panels"]) < args_root.min_panels:
        print(f"[skip] {dtm_name}: only {len(hist['panels'])} panels found (need >={args_root.min_panels})")
        return None

    pooled_rms = float(hist["sag_rms"])
    pmin, pmax = _per_panel_rms(rows, dtm_name)
    lon_min, lon_max, lat_min, lat_max = _dtm_lonlat_window(path)
    amin = 3.0 * pooled_rms
    print(f"[ok ] {dtm_name}: {len(hist['panels'])} panels, "
          f"pooled sag-band RMS = {pooled_rms*100:.1f} cm, "
          f"3sigma = {amin:.2f} m, "
          f"per-panel [{pmin*100:.1f}, {pmax*100:.1f}] cm, "
          f"t={dt:.1f}s")

    return {
        "dtm_name": dtm_name,
        "site": str(scope_row.get("sitename", "")),
        "lon_min": round(lon_min, 4),
        "lon_max": round(lon_max, 4),
        "lat_min": round(lat_min, 4),
        "lat_max": round(lat_max, 4),
        "n_panels": int(len(hist["panels"])),
        "pooled_rms_m": round(pooled_rms, 6),
        "three_sigma_m": round(amin, 6),
        "panel_min_rms": round(pmin, 6),
        "panel_max_rms": round(pmax, 6),
        "local_Amin_m": round(amin, 6),
        "mtime": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds"),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scope-map", type=Path, default=DEFAULT_SCOPE_MAP)
    p.add_argument("--dtm-root", type=Path, default=DEFAULT_DTM_ROOT)
    p.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT_CSV)
    p.add_argument("--summary-out", type=Path, default=DEFAULT_OUT_SUMMARY)
    p.add_argument("--min-panels", type=int, default=DEFAULT_MIN_PANELS)
    p.add_argument("--dtm", action="append", default=None,
                   help="restrict to these DTM names (repeatable); default = all good-tier in scope map")
    args_root = p.parse_args()

    args_root.out.parent.mkdir(parents=True, exist_ok=True)
    args_root.summary_out.parent.mkdir(parents=True, exist_ok=True)

    scope = pd.read_csv(args_root.scope_map)
    scope_good = scope[scope["quality"] == "good"].copy()
    if args_root.dtm:
        keep = set(args_root.dtm)
        scope_good = scope_good[scope_good["DTM_NAME"].isin(keep)]
    print(f"[scope] {len(scope_good)} good-tier DTMs in scope map (filtered: {len(scope_good)}).")
    print(f"[roots] dtm={args_root.dtm_root} outputs={args_root.out_root}")

    rows = []
    skips = []
    t_start = time.time()
    for _, r in scope_good.iterrows():
        name = r["DTM_NAME"]
        row = run_one(name, r, args_root)
        if row is None:
            skips.append(name)
            continue
        rows.append(row)

    elapsed = time.time() - t_start
    df = pd.DataFrame(rows, columns=[
        "dtm_name", "site", "lon_min", "lon_max", "lat_min", "lat_max",
        "n_panels", "pooled_rms_m", "three_sigma_m",
        "panel_min_rms", "panel_max_rms", "local_Amin_m", "mtime",
    ])
    # the column header must be self-documenting: append the convention
    # label to local_Amin_m per project convention.
    df.columns = [
        "dtm_name", "site", "lon_min", "lon_max", "lat_min", "lat_max",
        "n_panels", "pooled_rms_m", "three_sigma_m",
        "panel_min_rms", "panel_max_rms",
        f"local_Amin_m",  # the unit/meaning is documented in METHODS.md
        "mtime",
    ]
    df.to_csv(args_root.out, index=False, float_format="%.6f")
    print(f"\n[out] per-DTM CSV -> {args_root.out} ({len(df)} rows)")

    if not df.empty:
        rms = df["pooled_rms_m"].to_numpy()
        med = float(np.median(rms))
        amin = df["local_Amin_m"].to_numpy()

        # Terrain split (mare vs highland) per dispatch 2026-08-22.
        # Highland sites = central peaks (TYCHO, KING) and Gruithuisen
        # domes (silicic, non-mare composition). SWFECUNPIT1 sits on
        # the SW highland edge of Mare Fecunditatis (findings.md
        # 2026-08-21 identifies it as the only highland site of the
        # original 8 covered DTMs). The mare subset excludes all
        # highland sites.
        HIGHLAND = {"GRUITHUIS17", "SWFECUNPIT1",
                    "TYCHOPK", "TYCHOPK02", "TYCHOPK03",
                    "TYCHOPK04", "TYCHOPK07",
                    "KINGCRATER2", "KINGCRATER3", "KINGCRATER4"}
        is_highland = df["dtm_name"].isin(HIGHLAND).to_numpy()
        mare_rms = rms[~is_highland]
        highland_rms = rms[is_highland]

        def _stats(arr):
            if len(arr) == 0:
                return {"n": 0,
                        "median_pooled_rms_m": None,
                        "min_pooled_rms_m": None,
                        "max_pooled_rms_m": None,
                        "median_local_Amin_m": None,
                        "sites": []}
            return {"n": int(len(arr)),
                    "median_pooled_rms_m": round(float(np.median(arr)), 6),
                    "min_pooled_rms_m": round(float(arr.min()), 6),
                    "max_pooled_rms_m": round(float(arr.max()), 6),
                    "median_local_Amin_m": round(float(np.median(amin[~is_highland])), 6)
                            if arr is mare_rms
                            else round(float(np.median(amin[is_highland])), 6),
                    "sites": sorted(df.loc[~is_highland if arr is mare_rms
                                           else is_highland, "dtm_name"].tolist())}

        summary = {
            "generated": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
            "n_processed": int(len(df)),
            "n_skipped": int(len(skips)),
            "skipped": skips,
            "min_panels": args_root.min_panels,
            "median_pooled_rms_m": round(med, 6),
            "min_pooled_rms_m": round(float(rms.min()), 6),
            "max_pooled_rms_m": round(float(rms.max()), 6),
            "median_local_Amin_m": round(float(np.median(amin)), 6),
            "elapsed_s": round(elapsed, 1),
            "csv": str(args_root.out),
            "sources_used": df.apply(lambda r: _find_source(r["dtm_name"], args_root.dtm_root, args_root.out_root)[1], axis=1).tolist(),
            "by_terrain": {
                "mare": _stats(mare_rms),
                "highland": _stats(highland_rms),
                "highland_sites_set": sorted(HIGHLAND),
                "highland_classification_note": (
                    "highland = Gruithuisen domes (silicic, non-mare), "
                    "SW Fecunditatis pit (SW rim of Mare Fecunditatis, "
                    "highland edge per findings.md 2026-08-21), and all "
                    "TYCHOPK* (Tycho central peak — highland composition) "
                    "+ KINGCRATER* (King crater peak — highland composition) "
                    "sites. Mare subset excludes these."),
            },
        }
    else:
        summary = {
            "generated": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
            "n_processed": 0,
            "n_skipped": int(len(skips)),
            "skipped": skips,
            "min_panels": args_root.min_panels,
            "elapsed_s": round(elapsed, 1),
            "csv": str(args_root.out),
        }
    with open(args_root.summary_out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[out] summary JSON -> {args_root.summary_out}")
    print(f"[done] {len(df)} processed, {len(skips)} skipped in {elapsed:.1f}s")


if __name__ == "__main__":
    main()