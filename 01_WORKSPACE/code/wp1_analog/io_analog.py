"""Shared IO + grid utils for the Indian Tunnel analog registration (Task 12).

Reuses the NASA .f32 / npz conventions of wp1_lla/convert_f32.py:
- 7-attr float32 point records, local metric site frame.
- Sentinel rule (LOW-10 mirror, session 52, 2026-09-11): any |x|, |y| or
  |z| > SENTINEL_MAX_M = 1e6 m -> drop (the previous 1e3 m heuristic would
  silently NaN the edges of any future >1 km analog site, e.g. SP Mountain
  ~1.5 km). MEASURED (session 51 read-only numpy pass): the gray band
  (1e3, 1e6] is NOT empty — Kingsbowl_orig.f32 has 37 points there (max
  |xyz| ~930,515.8 m) and Indian_NorthSurface_1x.f32 has 31 (max
  ~620,616.4 m); sites are <=1.2 km extent so these are wild outliers
  the old 1e3 rule silently NaNed. The new 1e6 rule KEEPS them
  visible-but-flagged: any KEPT |xyz| exceeding WARN_MAX_M = 100 m
  emits ONE warning per load_xyz call (file name, count, max value,
  cites "session 52 / LOW-10 mirror"). NaN xyz continue to drop
  naturally via the np.isfinite mask (NaN < X is False).
- Color/NIR sentinel semantics do not apply here (npz stores x/y/z
  only); only the coordinate sentinel is in scope.

Grid convention matches wp1_ladder/degrade.py cloud_to_master_grid:
  origin = (x_min, y_min) of the reference cloud, 0.5 m posting,
  transform = rasterio.from_bounds(...), row = y ascending (bounds-style
  transform; degrade.py writes rasters with from_bounds so row 0 is y_min).
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np

# Sentinel thresholds and helpers live in the shared IO module
# (v1 C1, adopted session 56). Re-exported under their historical
# names so existing consumers (register_cave, coarse_search,
# explore_indian_tunnel) and test_io_analog_sentinel.py continue
# to import them unchanged.
_HERE = Path(__file__).resolve().parent
_CODE = _HERE.parent
if str(_CODE) not in sys.path:
    sys.path.insert(0, str(_CODE))
from io_common import SENTINEL_MAX_M, WARN_MAX_M, keep_or_nan  # noqa: E402


def load_xyz(npz_path, max_points: int | None = None, seed: int = 42):
    """Load x/y/z from a wp1_lla npz, drop sentinels, optional RNG subsample.

    Sentinel policy (LOW-10 mirror, session 52):
      - drop xyz where any axis is sentinel (~1e38, ~inf, or any
        |axis| >= SENTINEL_MAX_M = 1e6 m). The shared ``keep_or_nan``
        helper applies |axis| >= SENTINEL_MAX_M, NaN-safe; the loader
        KEEPS the complement (~keep_or_nan).
      - if any KEPT |axis| > WARN_MAX_M (100 m), emit ONE warning naming
        npz_path, count, and max |axis| value (visible-but-flagged).
    Returns (x, y, z) float32 arrays.
    """
    data = np.load(npz_path)
    x = np.asarray(data["x"], dtype=np.float64)
    y = np.asarray(data["y"], dtype=np.float64)
    z = np.asarray(data["z"], dtype=np.float64)
    # v1 C1 refactor (session 56): keep_or_nan unifies the strict-< mask
    # with convert_f32's NaN-mask convention. The complement of
    # keep_or_nan equals np.isfinite(axis) & (|axis| < SENTINEL_MAX_M).
    ok = (
        ~keep_or_nan(x, sentinel_max_m=SENTINEL_MAX_M)
        & ~keep_or_nan(y, sentinel_max_m=SENTINEL_MAX_M)
        & ~keep_or_nan(z, sentinel_max_m=SENTINEL_MAX_M)
    )
    # Session-52 LOW-10 mirror: surfaces gray-band outliers the old 1e3
    # rule silently NaNed. KEPT-only (sentinel points already excluded
    # by `ok`); one warning per load_xyz call regardless of axis count.
    over_warn = ok & (
        (np.abs(x) > WARN_MAX_M) | (np.abs(y) > WARN_MAX_M) | (np.abs(z) > WARN_MAX_M)
    )
    if over_warn.any():
        max_abs = float(
            max(
                float(np.abs(x[over_warn]).max()),
                float(np.abs(y[over_warn]).max()),
                float(np.abs(z[over_warn]).max()),
            )
        )
        warnings.warn(
            f"{npz_path}: {int(over_warn.sum())} points with kept |xyz| > "
            f"{WARN_MAX_M:g} m (max {max_abs:.1f} m); sentinels (~1e38) are NaNed "
            f"only beyond {SENTINEL_MAX_M:g} m — verify this site's extent "
            f"(session 52 / LOW-10 mirror; gray zone between real data and sentinel)",
            stacklevel=2,
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
