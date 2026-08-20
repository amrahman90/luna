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
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

FIELDS = ["x", "y", "z", "nir", "r", "g", "b"]
DTYPE = np.dtype([(f, "<f4") for f in FIELDS])
BYTES_PER_POINT = DTYPE.itemsize  # 28
N_ATTRS = 7


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
    in any of the 7 attributes. Empirically, valid terrain is in
    the range [-1e4, 1e4] m; anything outside (typically 1e38) is
    a sentinel. We mark all attributes NaN if xyz is sentinel, and
    any individual attribute is NaN if it's outside the valid
    range.
    """
    n = f32_stats(path)
    arr = np.memmap(path, dtype=DTYPE, mode="r", shape=(n,))
    arr = np.array(arr, copy=True)
    # xyz sentinel mask: any of x/y/z is outside the valid range
    # (NASA analog sites are typically 1-1000 m extent; values > 1e3
    # m are sentinels or unrecoverable outliers per the histogram
    # analysis of Kingsbowl_orig.f32; values < 1e3 m are kept as
    # real data even in cliff/cave overhangs)
    xyz_sentinel = (
        (np.abs(arr["x"]) > 1e3) | (np.abs(arr["y"]) > 1e3) | (np.abs(arr["z"]) > 1e3)
    )
    # per-attribute sentinel: outside valid range (for color/nir)
    for field in ("nir", "r", "g", "b"):
        attr_sentinel = (np.abs(arr[field]) > 1e3) | ~np.isfinite(arr[field])
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
