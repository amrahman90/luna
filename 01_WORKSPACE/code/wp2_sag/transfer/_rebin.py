"""Shared fractional-scale rebin helper (Phase 0.3, Next-Level Plan v2).

Canonical rebin-to-rung semantics, extracted from
`score_raster_gen.py:144-160` (the documented-correct implementation).

Problem being solved (Hermes audit HIGH-3): four sister scripts used
    factor = max(1, int(round(rung / res_full)))
which silently produces the WRONG grid for non-integer rung ratios —
e.g. rung=5 m from a 2 m source gives factor=2 → a 4 m grid, not 5 m.
The correct semantics: fractional scale factor, ceil-based output
shape, and a transform derived from the ACTUAL output dimensions so
non-integer rungs retain the requested posting.

Usage:
    from _rebin import rebin_to_rung
    dtm_r, transform_r = rebin_to_rung(dtm_path, rung)

Returns (np.ndarray float, Affine). Nodata handling is left to the
caller (sentinels survive averaging as diluted values; callers that
need exact-sentinel masking do it after).
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the parent code/ dir is on sys.path so `_crs` is importable
# from this nested location (C9 single source-of-truth for CRS).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
import rasterio
from rasterio.enums import Resampling
from _crs import ANALOG_CRS_WKT  # C9: shared local-metric CRS


def rebin_to_rung(src_path, rung: float, resampling=Resampling.average):
    """Read a raster rebinned to ~`rung` m/px with fractional scale.

    Returns (array, transform). Array dtype is float32.
    """
    with rasterio.open(src_path) as src:
        H_src, W_src = src.height, src.width
        res_full = float(src.res[0])
        scale_factor = max(1.0, float(rung) / res_full)
        new_h = max(1, int(np.ceil(H_src / scale_factor)))
        new_w = max(1, int(np.ceil(W_src / scale_factor)))
        arr = src.read(1, out_shape=(new_h, new_w), resampling=resampling)
        # Derive transform from ACTUAL output dims so the posting is
        # preserved for non-integer ratios (e.g. 2 m -> 5 m = 2.5x).
        transform = src.transform * src.transform.scale(
            src.width / new_w, src.height / new_h
        )
    return arr.astype(np.float32), transform


def rebin_array(arr: np.ndarray, src_transform, src_res: float, rung: float):
    """In-memory variant: rebin an already-loaded array to ~rung m/px.

    Uses rasterio.warp.reproject between affine grids (average).
    Returns (new_array float32, new_transform).
    """
    import rasterio.warp
    from rasterio.transform import Affine

    h, w = arr.shape
    scale = max(1.0, float(rung) / src_res)
    new_h = max(1, int(np.ceil(h / scale)))
    new_w = max(1, int(np.ceil(w / scale)))
    dst_tr = Affine(src_res * scale, 0.0, src_transform.c,
                    0.0, -src_res * scale, src_transform.f)
    dst = np.zeros((new_h, new_w), dtype=np.float32)
    from _crs import ANALOG_CRS_WKT  # C9 (was: hardcoded "EPSG:32631")
    rasterio.warp.reproject(
        source=arr, destination=dst,
        src_transform=src_transform, dst_transform=dst_tr,
        src_crs=ANALOG_CRS_WKT, dst_crs=ANALOG_CRS_WKT,
        resampling=Resampling.average,
    )
    return dst, dst_tr


if __name__ == "__main__":
    # Self-test: 2 m -> 5 m must yield ~2.5x downscale (NOT 2x).
    import tempfile, os
    from rasterio.transform import from_origin
    rng = np.random.default_rng(42)
    Z = rng.uniform(0, 100, (200, 300)).astype(np.float32)
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as f:
        tmp = f.name
    profile = {
        "driver": "GTiff", "dtype": "float32", "nodata": -9999.0,
        "width": 300, "height": 200, "count": 1,
        "transform": from_origin(0, 0, 2.0, 2.0),  # 2 m/px source
        "crs": ANALOG_CRS_WKT,
    }
    with rasterio.open(tmp, "w", **profile) as dst:
        dst.write(Z, 1)
    arr, tr = rebin_to_rung(tmp, 5.0)
    os.unlink(tmp)
    assert arr.shape == (80, 120), f"FAIL: expected (80,120) for 5m from 2m (2.5x), got {arr.shape}"
    assert abs(abs(tr.a) - 5.0) < 0.01, f"FAIL: posting {abs(tr.a):.3f} != 5.0"
    print(f"PASS: 2 m -> 5 m gives {arr.shape} @ {abs(tr.a):.2f} m/px (fractional 2.5x, not integer 2x)")
