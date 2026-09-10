"""Task 4 (Z0.3) — sweep the depression-depth primitive across all 8
tube-relevant pits that have published NAC DTMs.

For each DTM product (single float32 GeoTIFF per product; the E/N-suffixed
products on the same page are the PDS IMG twins, not extra tiles): run the
Task-3 Planchon-Darboux fill (depression_depth.depression_depth), then
sample max depression depth within 200 m of each catalogued pit point.

Gotchas encoded here (learned in Task 3, see notes/):
- Longitude wrap: atlas lons are -180..180, NAC DTMs are local equirectangular
  spheres with product-specific lon_0; if the transformed point misses the
  raster bounds, retry with lon+/-360.
- Depth strings: ">25" -> 25 with a note; "N/A" -> NaN.
- Pit interiors are NoData (shadowed floors): recovered depth measures
  fill-to-spill of VALID pixels and can EXCEED catalogue depth; the NoData
  fraction within 200 m is recorded as a quality column.

Outputs (repo):
- 01_WORKSPACE/data/outputs/wp0_primitive/pit_recovery_table.csv
- 01_WORKSPACE/data/outputs/wp0_primitive/pit_recovery_summary.png
Raw intermediates (outside repo):
- ~/lunarvoid/data/outputs/<DTM>/NAC_DTM_<DTM>_depth.tif (+ _filled.tif)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from pyproj import CRS, Transformer
from rasterio.transform import rowcol

sys.path.insert(0, str(Path(__file__).resolve().parent))
from depression_depth import depression_depth  # noqa: E402

REPO = Path(__file__).resolve().parents[3]
RAW = Path.home() / "lunarvoid" / "data"
OUT_DIR = REPO / "01_WORKSPACE/data/outputs/wp0_primitive"
CATALOG = REPO / "01_WORKSPACE/data/outputs/wp0_scope_map/relevant_pits_x_dtms.csv"

MOON_SPHERE = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")
RADIUS_M = 200.0

# The 8 pit rows (pit name, DTM_NAME) per the Task-4 spec. PRCLRMPIT01
# covers two catalogued pits with one DTM; Marius Hills / Central Mare
# Fecunditatis pits each also appear in an alternate DTM (MARIUSCONE,
# FECUNPIT) which we do NOT use here.
PIT_ROWS = [
    ("Mare Tranquillitatis Pit", "TRANQPIT1"),
    ("Marius Hills Pit", "MARIUSPIT01"),
    ("Mare Ingenii Pit", "INGENIIPIT"),
    ("Southwest Mare Fecunditatis Pit", "SWFECUNPIT1"),
    ("Central Mare Fecunditatis Pit", "FECNDITATS2"),
    ("North Procellarum 1 Pit", "PRCLRMPIT01"),
    ("North Procellarum 2 Pit", "PRCLRMPIT01"),
    ("Sinus Iridum Pit", "IRIDIUMPIT1"),
]


def parse_depth(s):
    """'105' -> 105.0; '>25' -> 25.0 + note; 'N/A' -> NaN + note."""
    s = str(s).strip()
    try:
        return float(s), ""
    except ValueError:
        pass  # silent by design: parse cascade — try '>N' next, else NaN+note
    if s.startswith(">"):
        try:
            return float(s[1:]), f"catalogued '{s}' parsed as lower bound"
        except ValueError:
            pass  # silent by design: falls through to documented NaN+note
    return float("nan"), f"catalogued depth '{s}' unparsable -> NaN"


def _eqc_circle_x(src):
    """Full-circle x extent (m) of an equirectangular raster CRS, else None.

    Some NAC DTM GeoTIFFs store x in an UNWRAPPED frame (e.g. IRIDIUMPIT1:
    lon_0=0 with x ~ +7.05e6 m, i.e. ~331 degE), while pyproj wraps every
    lonlat input into [-180,180]. The only way to land in such a raster is
    to shift x post-transform by whole 360-deg turns.
    """
    p = src.crs.to_dict()
    if p.get("proj") != "eqc":
        return None
    import math
    R = p.get("R", p.get("a", 1737400.0))
    lat_ts = p.get("lat_ts", 0.0)
    return 2.0 * math.pi * R * math.cos(math.radians(lat_ts))


def pit_to_pixel(lat, lon, src):
    """Lat/lon (sphere R=1737400) -> (row, col, lon_used).

    Handles two wrap modes: +/-360 on input longitude AND +/-360-turn
    shifts in projected x (unwrapped rasters, e.g. IRIDIUMPIT1).
    """
    import math
    tr = Transformer.from_crs(MOON_SPHERE, src.crs, always_xy=True)
    b = src.bounds
    dx = _eqc_circle_x(src)
    shifts = [0.0] + ([n * dx for n in (-2, -1, 1, 2)] if dx else [])
    for cand in (lon, lon + 360.0, lon - 360.0):
        x0, y = tr.transform(cand, lat)
        for s in shifts:
            x = x0 + s
            if not (math.isfinite(x) and math.isfinite(y)):
                continue
            if b.left <= x <= b.right and b.bottom <= y <= b.top:
                r, c = rowcol(src.transform, x, y)
                return int(r), int(c), cand
    raise ValueError(f"pit ({lat}, {lon}) outside raster after lon and x wrap")


def sample_pit(depth_path, lat, lon):
    """Max depression depth + NoData fraction within RADIUS_M of the pit."""
    with rasterio.open(depth_path) as src:
        row, col, lon_used = pit_to_pixel(lat, lon, src)
        res = abs(src.transform.a)
        r_px = int(np.ceil(RADIUS_M / res))
        r0, r1 = max(0, row - r_px), min(src.height, row + r_px + 1)
        c0, c1 = max(0, col - r_px), min(src.width, col + r_px + 1)
        win = rasterio.windows.Window(c0, r0, c1 - c0, r1 - r0)
        arr = src.read(1, window=win)
        nodata = src.nodata
    rr, cc = np.ogrid[r0:r1, c0:c1]
    circle = (rr - row) ** 2 + (cc - col) ** 2 <= (RADIUS_M / res) ** 2
    valid = circle & (arr != nodata) & np.isfinite(arr)
    n_circle = int(circle.sum())
    n_valid = int(valid.sum())
    in_win = (r0 <= row < r1) and (c0 <= col < c1)
    return {
        "row": row,
        "col": col,
        "lon_used": lon_used,
        "max_depth_m": float(arr[valid].max()) if n_valid else float("nan"),
        "pit_pixel_depth_m": float(arr[row - r0, col - c0]) if in_win else float("nan"),
        "nodata_frac_200m": 1.0 - n_valid / n_circle if n_circle else float("nan"),
        "n_valid_px": n_valid,
        "res_m": res,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cat = pd.read_csv(CATALOG)

    dtms = sorted({d for _, d in PIT_ROWS})
    depth_rasters = {}
    for name in dtms:
        dtm_path = RAW / "dtms" / name / f"NAC_DTM_{name}.TIF"
        out_dir = RAW / "outputs" / name
        depth_path = out_dir / f"NAC_DTM_{name}_depth.tif"
        if not depth_path.exists():
            print(f"[fill] {name}: running Planchon-Darboux fill ...", flush=True)
            depth_path = depression_depth(dtm_path, out_dir)
        else:
            print(f"[skip] {name}: depth raster exists", flush=True)
        depth_rasters[name] = depth_path

    rows = []
    for pit_name, dtm_name in PIT_ROWS:
        sel = cat[(cat["Name"] == pit_name) & (cat["DTM_NAME"] == dtm_name)]
        if len(sel) != 1:
            raise SystemExit(f"catalog match error: {pit_name} x {dtm_name} -> {len(sel)} rows")
        rec = sel.iloc[0]
        lat, lon = float(rec["Latitude"]), float(rec["Longitude"])
        cat_d, cat_note = parse_depth(rec["Depth"])
        info = sample_pit(depth_rasters[dtm_name], lat, lon)
        recov = info["max_depth_m"]
        frac = recov / cat_d if cat_d and np.isfinite(cat_d) and cat_d > 0 else float("nan")
        note_bits = [cat_note] if cat_note else []
        note_bits.append(f"tile NAC_DTM_{dtm_name}.TIF; pit pixel ({info['row']},{info['col']}), lon_used={info['lon_used']:.2f}, {info['res_m']:.0f} m/px")
        rows.append({
            "Name": pit_name,
            "Terrain": rec["Terrain"],
            "catalogued_depth_m": cat_d,
            "recovered_depth_m": round(recov, 2),
            "recovered_frac": round(frac, 3) if np.isfinite(frac) else float("nan"),
            "dtm": dtm_name,
            "pass_50pct": bool(np.isfinite(frac) and frac >= 0.5),
            "nodata_frac_200m": round(info["nodata_frac_200m"], 3),
            "note": "; ".join(note_bits),
        })
        print(f"[pit ] {pit_name}: cat={cat_d} rec={recov:.1f} m frac={frac:.2f} "
              f"nodata={info['nodata_frac_200m']:.2f} pit_px={info['pit_pixel_depth_m']:.1f}", flush=True)

    df = pd.DataFrame(rows, columns=[
        "Name", "Terrain", "catalogued_depth_m", "recovered_depth_m",
        "recovered_frac", "dtm", "pass_50pct", "nodata_frac_200m", "note",
    ])
    csv_path = OUT_DIR / "pit_recovery_table.csv"
    df.to_csv(csv_path, index=False)
    print(f"[out ] {csv_path}")
    n_pass = int(df["pass_50pct"].sum())
    print(f"PASS {n_pass}/8 (threshold >=6)")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    short = {
        "Mare Tranquillitatis Pit": "M. Tranquillitatis",
        "Marius Hills Pit": "Marius Hills",
        "Mare Ingenii Pit": "M. Ingenii",
        "Southwest Mare Fecunditatis Pit": "SW M. Fecunditatis",
        "Central Mare Fecunditatis Pit": "C. M. Fecunditatis",
        "North Procellarum 1 Pit": "N. Procellarum 1",
        "North Procellarum 2 Pit": "N. Procellarum 2",
        "Sinus Iridum Pit": "S. Iridum",
    }
    labels = [short.get(n, n) for n in df["Name"]]
    x = np.arange(len(df))
    w = 0.38
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar(x - w / 2, df["catalogued_depth_m"], w, color="#8a8a8a", label="catalogued depth")
    colors = ["#2e8b57" if p else "#c0392b" for p in df["pass_50pct"]]
    ax.bar(x + w / 2, df["recovered_depth_m"], w, color=colors, label="recovered (sink-fill)")
    for i, (r, f, p) in enumerate(zip(df["recovered_depth_m"], df["recovered_frac"], df["pass_50pct"])):
        ax.text(x[i] + w / 2, r + 2, f"{f:.2f}", ha="center", fontsize=9,
                color="#2e8b57" if p else "#c0392b")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("depth (m)")
    ax.set_title("LUNARVOID WP0 Task 4 — pit depth recovery by depression-depth primitive\n"
                 f"(max sink-fill depth within 200 m; pass = recovered >= 50% catalogued; {n_pass}/8 pass)")
    ax.legend()
    fig.tight_layout()
    fig_path = OUT_DIR / "pit_recovery_summary.png"
    fig.savefig(fig_path, dpi=200)
    print(f"[out ] {fig_path}")


if __name__ == "__main__":
    main()
