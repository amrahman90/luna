"""LLTB-1 VCI overhang detector (Z1, Task 14; v5 inherited I8).

Vertical Complexity Index (Reichenzeller et al. 2026 / van Ewijk 2011):
per voxel column of a height-binned point cloud, the Shannon evenness
of the height distribution.

  p_i = n_i / n        (fraction of points in height bin i)
  H    = -sum(p_i ln p_i)        (Shannon entropy)
  H_max= ln(n_HB)                (entropy of the uniform distribution)
  VCI  = H / H_max                (normalised, 0 = empty column, 1 = uniform)

For a 2.5D photogrammetric cloud, VCI -> 0 over flat ground and VCI
spikes at overhangs / pit walls (multiple distinct height modes within
one column). Threshold + local-maximum filter (neighbourhood 5) yields
candidate overhang cells; centroids are reported.

CLI:
  vci.py --npz path/to/analog.npz --outdir <repo out dir>
         [--pixel 0.5] [--h-min 1.0] [--h-max 30.0] [--h-bin 1.0]
         [--threshold 0.4] [--local-max 5]
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

# v1 C1 refactor (session 56): the inline rasterio GeoTIFF write was
# replaced with io_common.write_geotiff. Behaviour preserved: VCI cells
# of 0 are still translated to nodata=-1.0 on disk (the loader does
# `np.where(VCI > 0, VCI, -1.0)` BEFORE the call, so write_geotiff's
# NaN-or-finite-nodata translate becomes a no-op for the all-finite
# VCI array). The CRS stays ANALOG_CRS_WKT (default in write_geotiff).
_HERE = Path(__file__).resolve().parent
_CODE = _HERE.parent
if str(_CODE) not in sys.path:
    sys.path.insert(0, str(_CODE))
from io_common import write_geotiff  # noqa: E402


def vci_raster(x, y, z, pixel: float, h_min: float, h_max: float, h_bin: float):
    """Return VCI raster (H, H_max, n, x_min, y_min) at `pixel` posting."""
    finite = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[finite], y[finite], z[finite]
    if len(x) == 0:
        raise ValueError("no finite points in cloud")
    x_min, y_min = x.min(), y.min()
    x_max, y_max = x.max(), y.max()
    nx = max(1, int(np.ceil((x_max - x_min) / pixel)))
    ny = max(1, int(np.ceil((y_max - y_min) / pixel)))
    col = np.clip(((x - x_min) / pixel).astype(int), 0, nx - 1)
    row = np.clip(((y - y_min) / pixel).astype(int), 0, ny - 1)
    # height bins in [h_min, h_max] inclusive, width h_bin
    h_lo = np.floor(h_min / h_bin) * h_bin
    h_hi = np.ceil(h_max / h_bin) * h_bin
    edges = np.arange(h_lo, h_hi + h_bin, h_bin)
    n_HB = max(1, len(edges) - 1)
    # (row, col, h_bin_index) -> count
    zb = np.clip(((z - h_lo) / h_bin).astype(int), 0, n_HB - 1)
    # 3D histogram
    flat = row * (nx * n_HB) + col * n_HB + zb
    counts = np.bincount(flat, minlength=ny * nx * n_HB).reshape(ny, nx, n_HB)
    # VCI per column
    n_per_col = counts.sum(axis=2)            # (ny, nx)
    p = np.where(counts > 0, counts / np.maximum(n_per_col, 1)[:, :, None], 0.0)
    nz = counts > 0
    H = np.where(nz, -p * np.where(p > 0, np.log(p), 0.0), 0.0).sum(axis=2)
    H_max = np.log(n_HB)
    VCI = np.where(n_per_col > 0, H / H_max, 0.0).astype(np.float32)
    return VCI, n_per_col.astype(np.int64), (x_min, y_min, nx, ny, pixel, n_HB)


def local_maxima(raster: np.ndarray, neighbourhood: int) -> np.ndarray:
    """Return a boolean mask of local-max cells using a max-filter of size k."""
    from scipy.ndimage import maximum_filter

    mf = maximum_filter(raster, size=neighbourhood, mode="nearest")
    return (raster == mf) & (raster > 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--npz", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--pixel", type=float, default=0.5)
    p.add_argument("--h-min", type=float, default=1.0)
    p.add_argument("--h-max", type=float, default=30.0)
    p.add_argument("--h-bin", type=float, default=1.0)
    p.add_argument("--threshold", type=float, default=0.4)
    p.add_argument("--local-max", type=int, default=5)
    p.add_argument("--name", default="")
    args = p.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    data = np.load(args.npz)
    x, y, z = data["x"], data["y"], data["z"]
    print(f"[load] {len(x):,} points from {args.npz.name}", flush=True)

    VCI, n_col, geo = vci_raster(x, y, z, args.pixel, args.h_min, args.h_max, args.h_bin)
    x_min, y_min, nx, ny, px, n_HB = geo
    print(f"[vci ] {ny}x{nx} at {px} m, n_HB={n_HB}, "
          f"max(VCI)={VCI.max():.3f}, VCI>{args.threshold}: {(VCI >= args.threshold).sum()} cells",
          flush=True)

    # candidate centroids via local-max filter
    cand_mask = local_maxima(VCI, args.local_max) & (VCI >= args.threshold)
    cand_rows, cand_cols = np.where(cand_mask)
    cand_x = x_min + (cand_cols + 0.5) * px
    cand_y = y_min + (cand_rows + 0.5) * px
    cand_vci = VCI[cand_rows, cand_cols]
    cand_n = n_col[cand_rows, cand_cols]
    order = np.argsort(-cand_vci)
    cand_x = cand_x[order]; cand_y = cand_y[order]
    cand_vci = cand_vci[order]; cand_n = cand_n[order]
    print(f"[cent] {len(cand_x)} candidate centroids (top 5: VCI "
          f"{[f'{v:.2f}' for v in cand_vci[:5]]})", flush=True)

    # figure
    fig, ax = plt.subplots(1, 2, figsize=(13, 6))
    im0 = ax[0].imshow(VCI, cmap="viridis", origin="lower",
                       extent=[x_min, x_min + nx * px, y_min, y_min + ny * px])
    ax[0].set_title(f"VCI (pixel={px} m, h=[{args.h_min},{args.h_max}] m, h_bin={args.h_bin} m)")
    plt.colorbar(im0, ax=ax[0], label="VCI")
    ax[1].hist(VCI.ravel(), bins=80, color="#3b6fb6", edgecolor="white")
    ax[1].axvline(args.threshold, color="crimson", lw=1.5, ls="--",
                  label=f"threshold = {args.threshold}")
    ax[1].set_xlabel("VCI"); ax[1].set_ylabel("# cells"); ax[1].legend()
    ax[1].set_title(f"VCI histogram: n_cells={VCI.size}, "
                    f">thr = {(VCI >= args.threshold).sum()}")
    fig.suptitle(f"LLTB-1 VCI: {args.npz.name}")
    fig.tight_layout()
    fig_path = args.outdir / "vci_overview.png"
    fig.savefig(fig_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[out ] figure -> {fig_path}", flush=True)

    # VCI raster GeoTIFF (C9: shared ANALOG_CRS_WKT — was: hardcoded EPSG:32631;
    # v1 C1, session 56: inline rasterio.open replaced with io_common.write_geotiff)
    from rasterio.transform import Affine
    transform = Affine(px, 0.0, x_min, 0.0, px, y_min)
    out_tif = args.outdir / "vci.tif"
    # Pre-translate VCI==0 cells to the nodata sentinel (VCI uses 0 for
    # "no points in column"); write_geotiff's NaN-or-finite-nodata
    # translate is then a no-op for the all-finite pre-coerced array.
    vci_arr = np.where(VCI > 0, VCI, -1.0).astype(np.float32)
    write_geotiff(vci_arr, transform, out_tif, crs=None, nodata=-1.0)
    print(f"[out ] vci raster -> {out_tif}", flush=True)

    # centroids CSV
    import pandas as pd
    centroids = pd.DataFrame({
        "x_m": cand_x, "y_m": cand_y, "vci": cand_vci, "n_pts_in_col": cand_n,
    })
    centroids_path = args.outdir / "vci_centroids.csv"
    centroids.to_csv(centroids_path, index=False)
    print(f"[out ] centroids -> {centroids_path} ({len(centroids)} rows)", flush=True)

    # summary
    summary = {
        "source": str(args.npz),
        "n_points": int(len(x)),
        "pixel_m": float(px),
        "n_HB": int(n_HB),
        "vci_max": float(VCI.max()),
        "vci_p50": float(np.percentile(VCI, 50)),
        "vci_p90": float(np.percentile(VCI, 90)),
        "vci_p99": float(np.percentile(VCI, 99)),
        "threshold": float(args.threshold),
        "n_cells_above_threshold": int((VCI >= args.threshold).sum()),
        "n_centroids": int(len(centroids)),
        "out": {
            "vci_raster": str(out_tif),
            "centroids": str(centroids_path),
            "figure": str(fig_path),
        },
    }
    sum_path = args.outdir / "vci_summary.json"
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[out ] summary -> {sum_path}", flush=True)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
