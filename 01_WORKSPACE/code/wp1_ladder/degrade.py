"""LLTB-1 degradation ladder (Z1, Task 13).

Resamples an analog surface DTM (or npz cloud -> rasterised) through a
lunar-like GSD ladder using rasterio's average-resampling, with valid-pixel
support (NOT nearest-neighbour, which thins the support per v5 WP1 spec).

Rungs (per v5 Section 8 Task 13.1): 2 cm, 0.5 m, 2 m, 5 m, 60 m.
Hapke photometry + NAC-like MTF + sensor noise are deferred to a Blender
or ASP-SfS step; the deliverable here is the clean GSD ladder over a
fixed 0.5 m master (the original analog resolution or the master from
the conversion step).

CLI:
  degrade.py --npz path/to/analog.npz --outdir <repo out dir>
             [--rungs 0.02 0.5 2 5 60]
             [--grid-spacing 0.5]    # master res from the source cloud
             [--method average]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.transform import Affine, from_bounds
from scipy.interpolate import griddata


def cloud_to_master_grid(x, y, z, grid_spacing: float):
    """Bin a point cloud to a regular (y, x) grid using the median z per cell.

    Returns (Z, transform, valid_mask, x_min, y_min, nx, ny).
    `grid_spacing` is the master posting in source-cloud units (metres
    here; analog site frame).
    """
    x = np.asarray(x); y = np.asarray(y); z = np.asarray(z)
    finite = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[finite], y[finite], z[finite]
    x_min, y_min = x.min(), y.min()
    x_max, y_max = x.max(), y.max()
    nx = max(1, int(np.ceil((x_max - x_min) / grid_spacing)))
    ny = max(1, int(np.ceil((y_max - y_min) / grid_spacing)))
    col = np.clip(((x - x_min) / grid_spacing).astype(int), 0, nx - 1)
    row = np.clip(((y - y_min) / grid_spacing).astype(int), 0, ny - 1)
    Z = np.full((ny, nx), np.nan, dtype=np.float64)
    cnt = np.zeros((ny, nx), dtype=np.int64)
    np.add.at(Z, (row, col), z)
    np.add.at(cnt, (row, col), 1)
    valid = cnt > 0
    Z[valid] = Z[valid] / cnt[valid]
    transform = from_bounds(x_min, y_min, x_min + nx * grid_spacing, y_min + ny * grid_spacing, nx, ny)
    return Z, transform, valid, (x_min, y_min, nx, ny)


def resample(Z: np.ndarray, src_tr, src_res: float, target_res: float, method: str = "average"):
    """Resample (Z, src_tr) to a new posting target_res using rasterio.warp."""
    import rasterio.warp

    valid = np.isfinite(Z)
    fill = float(np.nanmean(Z[valid])) if valid.any() else 0.0
    Z_filled = np.where(valid, Z, fill).astype(np.float32)

    src_h, src_w = Z_filled.shape
    dst_w = max(1, int(round(src_w * src_res / target_res)))
    dst_h = max(1, int(round(src_h * src_res / target_res)))
    dst_tr = Affine(target_res, 0.0, src_tr.c, 0.0, -target_res, src_tr.f)
    dst = np.full((dst_h, dst_w), fill, dtype=np.float32)
    rasterio.warp.reproject(
        source=Z_filled,
        destination=dst,
        src_transform=src_tr,
        dst_transform=dst_tr,
        src_crs="EPSG:32631",  # any local metric CRS; transform is what matters
        dst_crs="EPSG:32631",
        resampling={"average": rasterio.warp.Resampling.average,
                    "bilinear": rasterio.warp.Resampling.bilinear,
                    "cubic": rasterio.warp.Resampling.cubic,
                    "nearest": rasterio.warp.Resampling.nearest}[method],
    )
    # restore "no-data" where the resampled cell pulled in the fill
    # (approximate: a cell is "valid" iff >= 1 valid source cell contributed)
    # We use a cheap proxy: re-mask by the warped validity grid.
    vmask_src = valid.astype(np.uint8)
    vmask_dst = np.zeros((dst_h, dst_w), dtype=np.uint8)
    rasterio.warp.reproject(
        source=vmask_src,
        destination=vmask_dst,
        src_transform=src_tr,
        dst_transform=dst_tr,
        src_crs="EPSG:32631",
        dst_crs="EPSG:32631",
        resampling=rasterio.warp.Resampling.average,
    )
    out = np.where(vmask_dst > 0, dst, np.nan).astype(np.float32)
    return out, dst_tr


def degradation_ladder(npz_path: Path, outdir: Path, rungs, grid_spacing: float, method: str):
    outdir.mkdir(parents=True, exist_ok=True)
    data = np.load(npz_path)
    x, y, z = data["x"], data["y"], data["z"]
    print(f"[load] {len(x):,} points, source CRS is local metric", flush=True)

    Z0, tr0, valid0, info = cloud_to_master_grid(x, y, z, grid_spacing)
    print(f"[grid] master shape {Z0.shape} at {grid_spacing} m; "
          f"valid frac {valid0.mean():.3f}", flush=True)

    master_tif = outdir / f"master_{grid_spacing:g}m.tif"
    profile = {
        "driver": "GTiff", "dtype": "float32", "nodata": np.nan,
        "width": Z0.shape[1], "height": Z0.shape[0], "count": 1,
        "transform": tr0, "compress": "deflate", "BIGTIFF": "IF_SAFER",
    }
    with rasterio.open(master_tif, "w", **profile) as dst:
        dst.write(Z0.astype(np.float32), 1)
    print(f"[out ] master -> {master_tif}", flush=True)

    summary = {
        "source": str(npz_path),
        "n_points": int(len(x)),
        "master_grid_m": float(grid_spacing),
        "master_shape": list(Z0.shape),
        "master_valid_frac": float(valid0.mean()),
        "rungs": [],
    }
    # squeeze=False -> axes is ALWAYS a 2-D ndarray (matplotlib >=3.8 Axes
    # objects are not subscriptable; bug A.1 fix).
    fig, axes = plt.subplots(1, len(rungs), figsize=(4 * len(rungs), 4), squeeze=False)
    for i, r in enumerate(rungs):
        Zi, tri = resample(Z0, tr0, grid_spacing, r, method=method)
        npx = Zi.size
        nv = int(np.isfinite(Zi).sum())
        zrange = (float(np.nanmin(Zi)), float(np.nanmax(Zi))) if nv else (None, None)
        out_tif = outdir / f"rung_{r:g}m.tif"
        with rasterio.open(out_tif, "w", **profile | {
            "width": Zi.shape[1], "height": Zi.shape[0], "transform": tri
        }) as dst:
            dst.write(Zi, 1)
        # hillshade panel
        if nv and r <= 5.0:
            dz = np.gradient(Zi, r)
            slope = np.pi / 2.0 - np.arctan(np.hypot(dz[1], dz[0]))
            aspect = np.arctan2(-dz[1], dz[0])
            az, al = np.radians(315.0), np.radians(45.0)
            hs = np.clip(255.0 * (np.sin(al) * np.sin(slope) +
                                   np.cos(al) * np.cos(slope) * np.cos(az - aspect)), 0, 255)
            axes.flat[i].imshow(hs, cmap="gray", origin="upper")
        else:
            axes.flat[i].imshow(np.where(np.isfinite(Zi), Zi, np.nan), cmap="terrain", origin="upper")
        axes.flat[i].set_title(f"{r:g} m\n({Zi.shape[0]}x{Zi.shape[1]}, {nv/npx:.0%} valid)")
        axes.flat[i].set_xticks([]); axes.flat[i].set_yticks([])
        summary["rungs"].append({
            "res_m": float(r), "shape": list(Zi.shape),
            "valid_frac": float(nv / npx),
            "z_min_m": zrange[0], "z_max_m": zrange[1],
            "out": str(out_tif),
        })
        print(f"[rung] {r:>5} m -> {Zi.shape} valid {nv/npx:.2%} -> {out_tif.name}", flush=True)
    fig.suptitle(f"LLTB-1 degradation ladder from {npz_path.name}\n"
                 f"(source: {len(x):,} points; method={method})")
    fig.tight_layout()
    fig_path = outdir / "ladder_overview.png"
    fig.savefig(fig_path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[out ] figure -> {fig_path}", flush=True)
    summary["figure"] = str(fig_path)

    sum_path = outdir / "ladder_summary.json"
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[out ] summary -> {sum_path}", flush=True)
    return summary


def cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--npz", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--rungs", type=float, nargs="+", default=[0.02, 0.5, 2, 5, 60])
    p.add_argument("--grid-spacing", type=float, default=0.5,
                   help="master posting for the source cloud (metres)")
    p.add_argument("--method", default="average", choices=["average", "bilinear", "cubic", "nearest"])
    return p.parse_args()


if __name__ == "__main__":
    args = cli()
    degradation_ladder(args.npz, args.outdir, args.rungs, args.grid_spacing, args.method)
