"""Shared IO + grid utils for the Indian Tunnel analog registration (Task 12).

Reuses the NASA .f32 / npz conventions of wp1_lla/convert_f32.py:
- 7-attr float32 point records, local metric site frame.
- sentinel rule: |x| or |y| or |z| > 1000 m -> drop (skill bug-catalog #4;
  the NorthSurface npz JSON still shows +-6e5 m z values inside its
  "finite" set, so we re-filter here regardless of what the JSON says).

Grid convention matches wp1_ladder/degrade.py cloud_to_master_grid:
  origin = (x_min, y_min) of the reference cloud, 0.5 m posting,
  transform = rasterio.from_bounds(...), row = y ascending (bounds-style
  transform; degrade.py writes rasters with from_bounds so row 0 is y_min).
"""
from __future__ import annotations

import numpy as np

SENTINEL_ABS = 1000.0


def load_xyz(npz_path, max_points: int | None = None, seed: int = 42):
    """Load x/y/z from a wp1_lla npz, drop sentinels, optional RNG subsample.

    Returns (x, y, z) float32 arrays.
    """
    data = np.load(npz_path)
    x = np.asarray(data["x"], dtype=np.float64)
    y = np.asarray(data["y"], dtype=np.float64)
    z = np.asarray(data["z"], dtype=np.float64)
    ok = (
        (np.abs(x) < SENTINEL_ABS)
        & (np.abs(y) < SENTINEL_ABS)
        & (np.abs(z) < SENTINEL_ABS)
        & np.isfinite(x)
        & np.isfinite(y)
        & np.isfinite(z)
    )
    x, y, z = x[ok], y[ok], z[ok]
    if max_points is not None and len(x) > max_points:
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(x), size=max_points, replace=False)
        x, y, z = x[idx], y[idx], z[idx]
    return x.astype(np.float32), y.astype(np.float32), z.astype(np.float32)


def voxel_downsample(x, y, z, voxel: float, seed: int = 42):
    """Deterministic voxel-grid downsample: one random point per voxel.

    Deterministic via fixed-seed permutation so voxels are visited in a
    stable order. Returns float32 arrays (subset of input).
    """
    xi = np.floor(x / voxel).astype(np.int64)
    yi = np.floor(y / voxel).astype(np.int64)
    zi = np.floor(z / voxel).astype(np.int64)
    key = (xi * 73856093) ^ (yi * 19349663) ^ (zi * 83492791)
    # stable order: sort by key then pick first occurrence of each key
    order = np.argsort(key, kind="stable")
    k = key[order]
    first = np.ones(len(k), dtype=bool)
    first[1:] = k[1:] != k[:-1]
    sel = order[first]
    return x[sel], y[sel], z[sel]


def master_grid(x, y, spacing: float = 0.5):
    """Exact degrade.py cloud_to_master_grid geometry for a reference cloud.

    Returns (nx, ny, x_min, y_min) matching
    rasterio.transform.from_bounds(x_min, y_min, x_min+nx*s, y_min+ny*s, nx, ny).
    """
    x_min, y_min = float(np.min(x)), float(np.min(y))
    x_max, y_max = float(np.max(x)), float(np.max(y))
    nx = max(1, int(np.ceil((x_max - x_min) / spacing)))
    ny = max(1, int(np.ceil((y_max - y_min) / spacing)))
    return nx, ny, x_min, y_min
