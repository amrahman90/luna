"""LLTB-1 terrestrial-analog ingestion (Z1, Task 11) — NASA Planetary
Pits and Caves Analog Dataset (Wong, Whittaker, Jones & Whittaker 2014,
ti.arc.nasa.gov/dataset/caves).

Format: 7-attribute float32 per point, little-endian, sequential, no
delimiters. Attribute order (per the dataset README + supplemental PDF):
  0: x_coord  (metres, local site frame)
  1: y_coord  (metres, local site frame)
  2: z_coord  (metres, local site frame)
  3: NIR_reflect
  4: R_color
  5: G_color
  6: B_color

The dataset ships in RAR archives (unrar/7z to extract). This module
streams a single .f32 into a numpy structured array, then writes a
LAS 1.4 file (point format 7, RGB + NIR packed into the standard fields
plus a custom NIR byte). Without laspy in the env, it falls back to
writing an uncompressed COPC-equivalent: a flat .npz of the structured
array (regenerable, no licence-redistribution concerns). Conversion to
LAS via laspy happens only when a downstream task needs it.

CLI:
  convert_f32.py --f32 path/to/file.f32 --out path/to/out.las
                 [--laspy] [--site SITE] [--notes "..."]
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# Sentinel thresholds and helpers live in the shared IO module
# (v1 C1, adopted session 56). This re-export block keeps the
# convert_f32.SENTINEL_MAX_M / WARN_MAX_M / ATTR_SENTINEL_MAX names
# working for existing test_convert_f32_sentinel.py and the
# run_lltb1.py driver without changing the surface.
_HERE = Path(__file__).resolve().parent
_CODE = _HERE.parent
if str(_CODE) not in sys.path:
    sys.path.insert(0, str(_CODE))
from io_common import (  # noqa: E402
    ATTR_SENTINEL_MAX,
    SENTINEL_MAX_M,
    WARN_MAX_M,
    keep_or_nan,
)

FIELDS = ["x", "y", "z", "nir", "r", "g", "b"]
DTYPE = np.dtype([(f, "<f4") for f in FIELDS])
BYTES_PER_POINT = DTYPE.itemsize  # 28
N_ATTRS = 7

# Diagnostics from the most recent read_f32 call (session 51): a
# best-effort side channel so downstream tools can see the gray-band
# count without parsing the warning text. Purely additive — the
# read_f32 return signature is unchanged (caller grep 2026-09-11:
# only convert_f32.main() and tests/test_convert_f32_sentinel.py;
# run_lltb1.py drives this module as a CLI subprocess).
LAST_READ_DIAGNOSTICS: dict = {}


def f32_stats(path: Path) -> int:
    """Return exact point count (no header; pure sequential binary)."""
    n_bytes = path.stat().st_size
    if n_bytes % BYTES_PER_POINT != 0:
        raise ValueError(
            f"{path}: size {n_bytes} not multiple of {BYTES_PER_POINT} bytes per point"
        )
    return n_bytes // BYTES_PER_POINT


def read_f32(path: Path) -> np.ndarray:
    """Memory-map the .f32 and return a structured array of {n, 7} float32.

    NASA Pits & Caves .f32 files use a sentinel value for "no data"
    in any of the 7 attributes. The true sentinel magnitude is ~1e38;
    xyz values are NaNed only beyond SENTINEL_MAX_M = 1e6 m (LOW-10,
    audit 2026-09-04; the previous 1e3 m heuristic would silently NaN
    the edges of any future >1 km analog site, e.g. SP Mountain
    ~1.5 km). MEASURED (session 51, 2026-09-11): the gray band
    (1e3, 1e6] is NOT empty — Kingsbowl_orig.f32 carries 37 wild
    outlier points there (max |xyz| ~930,515.8 m) and
    Indian_NorthSurface_1x.f32 carries 31 (max ~620,616.4 m). Those
    are kept as visible-but-flagged: any KEPT |xyz| exceeding
    WARN_MAX_M = 100 m emits one warning per read, and the counts/max
    are recorded in LAST_READ_DIAGNOSTICS (and the CLI summary JSON).
    The frozen npz corpus is NOT regenerated (regeneration is
    forbidden); gray-band points in any future conversion must be
    explicitly reviewed, not silently kept or dropped. Individual
    color/NIR attributes are NaNed outside ATTR_SENTINEL_MAX = 1e3
    (colors are [0,255]; unchanged).
    """
    n = f32_stats(path)
    arr = np.memmap(path, dtype=DTYPE, mode="r", shape=(n,))
    arr = np.array(arr, copy=True)
    # xyz sentinel mask: any of x/y/z beyond SENTINEL_MAX_M (true
    # sentinel ~1e38; 1e6 leaves headroom for future >1 km sites).
    # Previously the literal 1e3 m. MEASURED (session 51): this change
    # is NOT dormant — Kingsbowl_orig.f32 has 37 points with |xyz| in
    # (1e3, 1e6] (max ~930,515.8 m) and Indian_NorthSurface_1x.f32 has
    # 31 (max ~620,616.4 m): wild outliers the old filter silently
    # NaNed and the new threshold deliberately keeps visible-but-
    # flagged. (LOW-10, audit 2026-09-04; counts re-measured
    # 2026-09-11. Frozen corpus NOT regenerated — any future re-run
    # must review gray-band points explicitly.)
    # v1 C1 refactor (session 56): keep_or_nan is the shared helper
    # that produces the per-axis NaN mask (|axis| >= SENTINEL_MAX_M,
    # NaN-safe). Unifies with io_analog's load_xyz (which previously
    # used strict <, kept <1e6; now unified on the same >= semantics
    # via io_common.keep_or_nan).
    xyz_sentinel = (
        keep_or_nan(arr["x"])
        | keep_or_nan(arr["y"])
        | keep_or_nan(arr["z"])
    )
    # gray-zone early alert (once per read): kept |xyz| > WARN_MAX_M.
    # MEASURED non-empty (session 51): the real hits so far are wild
    # outliers (hundreds of km on <=1.2 km sites), not large sites —
    # surfaced in the warning, LAST_READ_DIAGNOSTICS, and the CLI
    # summary JSON instead of staying silent.
    kept = ~xyz_sentinel
    over_warn = kept & (
        (np.abs(arr["x"]) > WARN_MAX_M)
        | (np.abs(arr["y"]) > WARN_MAX_M)
        | (np.abs(arr["z"]) > WARN_MAX_M)
    )
    mx = (
        max((float(np.abs(arr[f][over_warn]).max()) for f in ("x", "y", "z")), default=0.0)
        if over_warn.any()
        else 0.0
    )
    if over_warn.any():
        warnings.warn(
            f"{path.name}: {int(over_warn.sum())} points with kept |xyz| > "
            f"{WARN_MAX_M:g} m (max {mx:.1f} m); sentinels (~1e38) are NaNed "
            f"only beyond {SENTINEL_MAX_M:g} m — verify this site's extent "
            f"(LOW-10 gray zone between real data and sentinel)",
            stacklevel=2,
        )
    # session 51: expose the gray-band count/max without warning-text
    # parsing. Mutates the module-level dict in place; return value and
    # call signature unchanged.
    LAST_READ_DIAGNOSTICS.clear()
    LAST_READ_DIAGNOSTICS.update(
        path=str(path),
        n_total=int(len(arr)),
        n_xyz_sentinel=int(xyz_sentinel.sum()),
        n_gray_band=int(over_warn.sum()),
        gray_band_max_abs_m=mx,
    )
    # per-attribute sentinel: outside valid range (for color/nir).
    # ATTR_SENTINEL_MAX is the SEPARATE colour/NIR bound (1e3); see
    # io_common.ATTR_SENTINEL_MAX docstring for why it differs from
    # the coordinate sentinel. The shared keep_or_nan(attr=True)
    # helper applies |arr| >= ATTR_SENTINEL_MAX with NaN-safe semantics.
    for field in ("nir", "r", "g", "b"):
        attr_sentinel = keep_or_nan(arr[field], attr=True)
        arr[field] = np.where(attr_sentinel, np.nan, arr[field])
    # zero out xyz where sentinel (all attributes set to NaN)
    for field in ("x", "y", "z"):
        arr[field] = np.where(xyz_sentinel, np.nan, arr[field])
    return arr


def write_las(arr: np.ndarray, out: Path, site: str = "", notes: str = "") -> None:
    """Write LAS 1.4 (point format 3) with RGB. NIR -> intensity."""
    import laspy

    header = laspy.LasHeader(point_format=3, version="1.4")
    header.offsets = [float(arr["x"].min()), float(arr["y"].min()), float(arr["z"].min())]
    header.scales = [0.001, 0.001, 0.001]
    header.global_encoding = (header.global_encoding & ~0x01) | 0x01  # GPS time
    if site:
        for k, v in [("site", site.encode()[:32]), ("notes", notes.encode()[:64])]:
            try:
                header.vlrs.append(laspy.VLR(user_id=k, record_id=0, description=v.decode(errors="ignore")))
            except Exception:
                # silent by design: VLR site/notes tags are cosmetic LAS
                # metadata; point payload is written regardless
                pass

    las = laspy.LasData(header)
    las.x = arr["x"].astype(np.float64)
    las.y = arr["y"].astype(np.float64)
    las.z = arr["z"].astype(np.float64)
    # colourise: NIR->intensity (uint16), RGB u16
    nir = np.clip(arr["nir"], 0, np.nanpercentile(arr["nir"], 99.9) if np.isfinite(arr["nir"]).any() else 1.0)
    if not np.isfinite(nir).all():
        nir = np.nan_to_num(nir, nan=0.0)
    if nir.max() > 0:
        nir = nir / nir.max()
    las.intensity = (nir * 65535.0).astype(np.uint16)
    r = np.clip(arr["r"], 0, 1) if arr["r"].max() <= 1.5 else np.clip(arr["r"] / 255.0, 0, 1)
    g = np.clip(arr["g"], 0, 1) if arr["g"].max() <= 1.5 else np.clip(arr["g"] / 255.0, 0, 1)
    b = np.clip(arr["b"], 0, 1) if arr["b"].max() <= 1.5 else np.clip(arr["b"] / 255.0, 0, 1)
    if not np.isfinite(r).all(): r = np.nan_to_num(r, 0.0)
    if not np.isfinite(g).all(): g = np.nan_to_num(g, 0.0)
    if not np.isfinite(b).all(): b = np.nan_to_num(b, 0.0)
    las.red = (r * 65535.0).astype(np.uint16)
    las.green = (g * 65535.0).astype(np.uint16)
    las.blue = (b * 65535.0).astype(np.uint16)
    las.gps_time = np.zeros(len(arr), dtype=np.float64)
    las.write(str(out))


def summarise(arr: np.ndarray) -> dict:
    """Return the headline summary statistics for an LLTB-1 analog cloud."""
    finite = np.isfinite(arr["x"]) & np.isfinite(arr["y"]) & np.isfinite(arr["z"])
    out = {
        "n_total": int(len(arr)),
        "n_finite": int(finite.sum()),
        "frac_finite": float(finite.mean()),
        "x_min_m": float(arr["x"][finite].min()) if finite.any() else None,
        "x_max_m": float(arr["x"][finite].max()) if finite.any() else None,
        "y_min_m": float(arr["y"][finite].min()) if finite.any() else None,
        "y_max_m": float(arr["y"][finite].max()) if finite.any() else None,
        "z_min_m": float(arr["z"][finite].min()) if finite.any() else None,
        "z_max_m": float(arr["z"][finite].max()) if finite.any() else None,
        "z_p50_m": float(np.percentile(arr["z"][finite], 50)) if finite.any() else None,
        "nir_nan_frac": float(np.isnan(arr["nir"]).mean()),
        "r_nan_frac": float(np.isnan(arr["r"]).mean()),
        "g_nan_frac": float(np.isnan(arr["g"]).mean()),
        "b_nan_frac": float(np.isnan(arr["b"]).mean()),
    }
    out["x_range_m"] = out["x_max_m"] - out["x_min_m"] if out["n_finite"] else None
    out["y_range_m"] = out["y_max_m"] - out["y_min_m"] if out["n_finite"] else None
    return out


def cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--f32", type=Path, required=True, help="input .f32 file")
    p.add_argument("--out", type=Path, required=True, help="output .las or .npz path")
    p.add_argument("--laspy", action="store_true", help="force LAS output (requires laspy)")
    p.add_argument("--site", default="")
    p.add_argument("--notes", default="")
    return p.parse_args()


def main():
    args = cli()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    print(f"[f32 ] {args.f32} ({args.f32.stat().st_size} bytes)", flush=True)
    n = f32_stats(args.f32)
    print(f"[f32 ] exact point count: {n:,}", flush=True)
    arr = read_f32(args.f32)
    summary = summarise(arr)
    # session 51: gray-band visibility in the summary JSON/log without
    # warning-text parsing (n_gray_band_xyz = kept |xyz| in (100 m, 1e6]).
    summary["n_xyz_sentinel"] = LAST_READ_DIAGNOSTICS["n_xyz_sentinel"]
    summary["n_gray_band_xyz"] = LAST_READ_DIAGNOSTICS["n_gray_band"]
    summary["gray_band_max_abs_m"] = LAST_READ_DIAGNOSTICS["gray_band_max_abs_m"]
    summary["source"] = str(args.f32)
    summary["generated_utc"] = datetime.now(timezone.utc).isoformat()
    summary["site"] = args.site
    summary["notes"] = args.notes
    summary["out"] = str(args.out)

    if args.laspy or args.out.suffix.lower() == ".las":
        try:
            write_las(arr, args.out, site=args.site, notes=args.notes)
            print(f"[out ] LAS -> {args.out}", flush=True)
        except ImportError:
            print("[warn] laspy not installed; falling back to .npz", flush=True)
            np.savez_compressed(args.out.with_suffix(".npz"), x=arr["x"], y=arr["y"], z=arr["z"],
                                nir=arr["nir"], r=arr["r"], g=arr["g"], b=arr["b"])
            print(f"[out ] npz -> {args.out.with_suffix('.npz')}", flush=True)
            summary["out"] = str(args.out.with_suffix(".npz"))
    else:
        np.savez_compressed(args.out, x=arr["x"], y=arr["y"], z=arr["z"],
                            nir=arr["nir"], r=arr["r"], g=arr["g"], b=arr["b"])
        print(f"[out ] npz -> {args.out}", flush=True)

    summary_path = args.out.with_suffix(".json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[out ] summary -> {summary_path}", flush=True)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
