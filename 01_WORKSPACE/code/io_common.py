"""io_common.py — LUNARVOID shared IO module (v1 C1, adopted session 56).

Four pillars, in one place, imported by every WP1 / WP2 / WP3 caller:

1. **Path resolver** (``LLTB1_HOME`` / ``LLTB1_DATA`` / ``LLTB1_VENV_PY``).
   Single source of truth for the ``~/lunarvoid`` tree so callers stop
   hard-coding ``/home/frostflux/lunarvoid/...`` (the C5 reproducibility
   blocker). ``LLTB1_DATA = ~/lunarvoid/data`` is where rasters live
   (conventions §1 — never mirror into the repo); ``lltb1/`` and
   ``analog/`` sub-directories live under it.

2. **Sentinel constants** — the LOW-10 standardised values (audit
   ``notes/2026-09-04_AUDIT_REVIEW.md``, session 51 + 52 measurement).
   ``SENTINEL_MAX_M = 1e6`` and ``WARN_MAX_M = 100.0`` are the unified
   thresholds for both lunar (DTM) and analog (LiDAR) inputs (the
   session-51 measured corpus showed the gray band (1e3, 1e6] is non-
   empty in real analog files, so the original 1e3 heuristic would
   have silently NaNed wild outliers and any future >1 km site).
   ``ATTR_SENTINEL_MAX = 1e3`` is the SEPARATE colour/NIR per-attribute
   bound (colors are [0, 255]) — kept distinct from ``SENTINEL_MAX_M``
   because they live in different units (intensity vs metres).
   ``F32_NODATA = -9999.0`` and ``GTIFF_NODATA_NAN = float('nan')``
   standardise the two file-format nodata conventions.

3. **``keep_or_nan(arr, *, sentinel_max_m, attr)``** — single helper
   that returns a NaN mask for ``|arr| >= sentinel_max_m`` (or
   ``|arr| >= ATTR_SENTINEL_MAX`` when ``attr=True``), NaN-safe
   (NaN inputs → True so the caller NaNs them and the output
   preserves the input NaN). Replaces the two near-identical inline
   blocks in ``convert_f32.py`` and ``io_analog.py``.

4. **``write_geotiff(arr, transform, path, crs, nodata, *, dtype)``** —
   semantics-equivalent copy of the local helper in
   ``code/wp1_detector/sag_detect.py`` (NaN-or-finite-nodata translate
   + rasterio GTiff float32). Also re-exported from ``sag_detect`` for
   the in-module callers that pre-date this refactor.

Plus ``AREA_MIN_PER_RUNG`` — a copy of the canonical per-rung
``area_min`` table (V0.2_PLAN.md §4.1, ``(GSD ratio)^2`` scale-
awareness rationale in ``connected_component_filter.py``). The
canonical dict lives in ``connected_component_filter.py``; this copy
exists so io_common has zero external dependencies on WP1 sub-modules
(it can still be imported by WP2 / WP3 / paper code that doesn't
need WP1's whitebox / skimage / scipy.ndimage machinery at import
time).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

import numpy as np

try:
    import rasterio
    from rasterio.transform import Affine
except ImportError:  # pragma: no cover — rasterio is in the freeze
    rasterio = None  # type: ignore[assignment]
    Affine = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# 1. Path resolver — single source of truth for ~/lunarvoid/...
# ---------------------------------------------------------------------------
LLTB1_HOME = Path.home() / "lunarvoid"
LLTB1_DATA = LLTB1_HOME / "data"
LLTB1_VENV_PY = LLTB1_HOME / "venv" / "bin" / "python"


# ---------------------------------------------------------------------------
# 2. Sentinel constants (LOW-10 standardised; session 51+52 measured corpus)
# ---------------------------------------------------------------------------
# Unified coordinate sentinel for both lunar DTM and analog LiDAR
# (session 51: gray band (1e3, 1e6] is non-empty in real analog files;
# original 1e3 heuristic would have silently NaNed wild outliers and
# any future >1 km site like SP Mountain ~1.5 km).
SENTINEL_MAX_M: float = 1e6

# Gray-zone warning threshold (kept |xyz| in (100 m, 1e6] is surfaced
# via warnings.warn(..., stacklevel=2) and a side-channel diagnostics
# dict, never silently NaNed or silently kept).
WARN_MAX_M: float = 100.0

# NASA .f32 / wp1_lla npz sentinel for "no data" in any of the 7
# attributes. Distinct from SENTINEL_MAX_M (the coordinate sentinel);
# the f32 file format ships -9999.0 as the explicit nodata marker,
# while SENTINEL_MAX_M is the magnitude-driven sentinel applied to
# x/y/z in metres.
F32_NODATA: float = -9999.0

# Preferred GeoTIFF nodata marker for NEW rasters. Falls back to
# F32_NODATA when the caller passes a finite nodata via the
# ``write_geotiff(..., nodata=...)`` kwarg.
GTIFF_NODATA_NAN: float = float("nan")

# Colour / NIR per-attribute bound (separately scoped: colour bytes are
# [0, 255], not metres; the 1e3 bound is the original LOW-10 value and
# is intentionally NOT unified with SENTINEL_MAX_M).
ATTR_SENTINEL_MAX: float = 1e3


# ---------------------------------------------------------------------------
# AREA_MIN_PER_RUNG — canonical per-rung area_min table copy
# ---------------------------------------------------------------------------
# Authority: V0.2_PLAN.md §4.1; scale-awareness rationale ((GSD ratio)^2)
# documented in wp1_detector.connected_component_filter.AREA_MIN_PER_RUNG.
# This copy exists so io_common has no WP1 submodule dependency. The
# table values MUST match connected_component_filter.AREA_MIN_PER_RUNG
# byte-for-byte; the test_io_common.py::test_area_min_table_matches_canonical
# test pins the equality.
AREA_MIN_PER_RUNG: dict[float, int] = {
    0.5: 50,
    1.0: 20,
    2.0: 8,
    5.0: 3,
    8.0: 2,
    10.0: 2,
}


# ---------------------------------------------------------------------------
# 3. keep_or_nan — NaN mask helper
# ---------------------------------------------------------------------------
def keep_or_nan(
    arr: Union[np.ndarray, "array-like"],
    *,
    sentinel_max_m: float = SENTINEL_MAX_M,
    attr: bool = False,
) -> np.ndarray:
    """Return a boolean mask: True for cells to be NaNed.

    The mask is True when ``|arr| >= sentinel_max_m`` (or
    ``|arr| >= ATTR_SENTINEL_MAX`` when ``attr=True``) AND when the
    input is NaN — NaN-safe means NaN inputs round-trip to NaN
    outputs (so the mask must be True for NaN inputs even though
    ``|NaN| >= thr`` is False).

    Usage::

        mask = keep_or_nan(arr["x"])
        arr["x"] = np.where(mask, np.nan, arr["x"])

        # inverse (the io_analog "kept" idiom):
        ok = ~keep_or_nan(x, sentinel_max_m=SENTINEL_MAX_M)

    NaN-safe: input NaN -> output mask True.
    """
    thr = ATTR_SENTINEL_MAX if attr else sentinel_max_m
    a = np.asarray(arr)
    if not np.issubdtype(a.dtype, np.floating):
        a = a.astype(np.float64, copy=False)
    return (np.abs(a) >= thr) | np.isnan(a)


# ---------------------------------------------------------------------------
# 4. write_geotiff — semantics-equivalent extract from sag_detect
# ---------------------------------------------------------------------------
def write_geotiff(
    arr: np.ndarray,
    transform: "Affine",
    path: Union[str, Path],
    crs: Optional[str] = None,
    nodata: float = GTIFF_NODATA_NAN,
    *,
    dtype: str = "float32",
) -> None:
    """Write a single-band GeoTIFF with rasterio.

    Semantics-equivalent to the local ``write_geotiff`` that lived in
    ``wp1_detector/sag_detect.py`` (extracted session 56, v1 C1):
    rasterio GTiff float32, deflate compression, BIGTIFF IF_SAFER,
    NaN-or-finite-nodata translate (NaN cells in the input become
    the ``nodata`` value on disk; finite nodata is preserved as-is).

    Parameters
    ----------
    arr : np.ndarray
        2-D array (rows, cols). Non-finite cells are translated to
        ``nodata`` on disk.
    transform : rasterio.transform.Affine
        Affine mapping array coordinates to CRS coordinates.
    path : str | Path
        Output ``.tif`` path. Parent directory must exist.
    crs : str, optional
        CRS string / WKT. Defaults to ``ANALOG_CRS_WKT`` (the shared
        local-metric placeholder from ``_crs.py``). Pass an explicit
        CRS (e.g. ``"EPSG:4326"`` or a proj4) for a non-analog site.
    nodata : float, default ``GTIFF_NODATA_NAN``
        GeoTIFF nodata value. Finite values pass through; non-finite
        values (NaN, +/-inf) fall back to ``F32_NODATA`` (the standard
        finite sentinel used by the WP2 ladder).
    dtype : str, default "float32"
        Output dtype (GeoTIFF band dtype).
    """
    if rasterio is None:
        raise RuntimeError(
            "rasterio is required for io_common.write_geotiff; "
            "install it via the venv freeze (requirements.txt)"
        )
    if crs is None:
        from _crs import ANALOG_CRS_WKT
        crs = ANALOG_CRS_WKT
    profile = {
        "driver": "GTiff",
        "dtype": dtype,
        "nodata": float(nodata) if np.isfinite(nodata) else F32_NODATA,
        "width": arr.shape[1],
        "height": arr.shape[0],
        "count": 1,
        "transform": transform,
        "crs": crs,
        "compress": "deflate",
        "BIGTIFF": "IF_SAFER",
    }
    with rasterio.open(path, "w", **profile) as dst:
        arr2 = np.where(np.isfinite(arr), arr, profile["nodata"]).astype(np.float32)
        dst.write(arr2, 1)