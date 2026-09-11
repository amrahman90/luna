"""C1 — io_common.py shared module pins (v1 C1, adopted session 56).

Guards the v1 C1 refactor (the #1 reproducibility blocker):
  - sentinel constants are the LOW-10 standardised values (regression
    detector for accidental 1e3 / 1e30 re-introductions);
  - ``LLTB1_DATA`` resolves to ``<home>/lunarvoid/data`` (the path
    resolver that replaces hard-coded ``/home/frostflux/lunarvoid/...``
    literals across the six caller files);
  - ``keep_or_nan`` reproduces the documented mask semantics
    (``|arr| >= sentinel_max_m``, NaN-safe);
  - ``write_geotiff`` round-trips float32 to disk with the chosen
    nodata and ANALOG_CRS_WKT default;
  - ``AREA_MIN_PER_RUNG`` matches the canonical V0.2_PLAN.md §4.1
    table byte-for-byte AND is the same dict object as the
    v0_2_pipeline_integration copy (verify by ``is``);
  - behaviour-preservation: ``sag_detect.write_geotiff`` is the
    re-exported ``io_common.write_geotiff`` (the v3 smoke pin
    f1 0.392/0/0.800 and the v0.2 E2E pin 0.029746281714785657 do
    not drift because of this module).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import Affine

# conftest.py inserts CODE_DIR (01_WORKSPACE/code) onto sys.path, but
# the WP1 sub-modules used by the behaviour-preservation tests live
# one level down. Mirror the explicit inserts the other test files
# use so pytest can resolve `import sag_detect` directly.
from conftest import CODE_DIR

for _p in (str(CODE_DIR), str(CODE_DIR / "wp1_detector"),
           str(CODE_DIR / "wp1_lla"), str(CODE_DIR / "wp1_analog")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import io_common  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Sentinel constants — LOW-10 regression detector
# ---------------------------------------------------------------------------


def test_sentinel_constants_low10():
    """LOW-10 standardised values; guards against 1e3/1e30 reintroductions.

    The audit `notes/2026-09-04_AUDIT_REVIEW.md` [LOW-10] standardised on
    SENTINEL_MAX_M=1e6 (not the old 1e3 heuristic and not the v1
    draft's |x|>1e30 analog placeholder). Session 51+52 measured the
    gray band (1e3, 1e6] is non-empty in real analog files; the
    1e30 placeholder was rejected as super-generous. ATTR_SENTINEL_MAX
    is the SEPARATE colour/NIR bound (colors [0,255]); intentionally
    not unified with the coordinate sentinel.
    """
    assert io_common.SENTINEL_MAX_M == 1e6
    assert io_common.WARN_MAX_M == 100.0
    assert io_common.ATTR_SENTINEL_MAX == 1e3
    assert io_common.F32_NODATA == -9999.0
    assert np.isnan(io_common.GTIFF_NODATA_NAN)
    # explicit "the 1e3 heuristic must NOT come back" assertion
    assert io_common.SENTINEL_MAX_M != 1e3
    # explicit "the v1 draft's 1e30 placeholder must NOT come back"
    assert io_common.SENTINEL_MAX_M != 1e30


# ---------------------------------------------------------------------------
# 2. Path resolver
# ---------------------------------------------------------------------------


def test_lltb1_data_resolves_to_home_lunarvoid_data():
    """LLTB1_DATA must equal <home>/lunarvoid/data (conventions §1).

    This is the single source of truth that replaces the hard-coded
    `/home/frostflux/lunarvoid/data` literal across v0_2_pipeline_integration,
    cc_filter_eval_v0_6, and any other caller. The assertion uses
    ``Path.home()`` directly (NOT a hardcoded path) so the test is
    portable across user accounts and CI.
    """
    assert io_common.LLTB1_DATA == Path.home() / "lunarvoid" / "data"
    assert io_common.LLTB1_HOME == Path.home() / "lunarvoid"
    assert io_common.LLTB1_VENV_PY == (
        Path.home() / "lunarvoid" / "venv" / "bin" / "python"
    )
    # the canonical hierarchy: HOME > DATA > venv
    assert io_common.LLTB1_DATA.parent == io_common.LLTB1_HOME
    assert io_common.LLTB1_VENV_PY.parent.parent.parent == io_common.LLTB1_HOME


# ---------------------------------------------------------------------------
# 3. keep_or_nan semantics
# ---------------------------------------------------------------------------


def test_keep_or_nan_docstring_example():
    """The dispatch spec's worked example, exact.

    ``keep_or_nan(arr=[10, 500, 5000, 1e38, np.nan])`` returns
    ``[False, False, False, True, True]`` — 5000 is the regime-flip
    from session 51 (old 1e3 NaNed it, new 1e6 keeps it); 1e38 and
    NaN are the downstream-sentinel classes (NaN-safe).
    """
    arr = np.array([10.0, 500.0, 5000.0, 1e38, np.nan])
    mask = io_common.keep_or_nan(arr)
    assert mask.tolist() == [False, False, False, True, True]


def test_keep_or_nan_attr_bound_uses_attr_sentinel_max():
    """When attr=True, the bound is ATTR_SENTINEL_MAX (1e3), not SENTINEL_MAX_M.

    Colors/NIR live in [0, 255]; the 1e3 bound is the LOW-10 value
    for those byte-scale attributes. Keeping the attribute sentinel
    SEPARATE from the coordinate sentinel (which is metres) is
    intentional and documented in io_common.
    """
    arr = np.array([10.0, 500.0, 1500.0, np.nan])
    mask_attr = io_common.keep_or_nan(arr, attr=True)
    # 500 kept (|.| < 1e3); 1500 NaNed (|.| >= 1e3); NaN NaNed (NaN-safe).
    assert mask_attr.tolist() == [False, False, True, True]


def test_keep_or_nan_nan_safe_inputs():
    """NaN inputs -> True (mask), so np.where(mask, nan, x) round-trips NaN."""
    arr = np.array([np.nan, np.nan, np.nan])
    mask = io_common.keep_or_nan(arr)
    assert mask.all()
    # the round-trip test
    out = np.where(mask, np.nan, arr)
    assert np.isnan(out).all()


def test_keep_or_nan_custom_sentinel_max():
    """Custom sentinel_max_m kwargs work (used by callers that want
    the 1e6 default but allow per-call overrides)."""
    arr = np.array([50.0, 200.0, 500.0])
    mask = io_common.keep_or_nan(arr, sentinel_max_m=300.0)
    assert mask.tolist() == [False, False, True]


# ---------------------------------------------------------------------------
# 4. write_geotiff round-trip
# ---------------------------------------------------------------------------


def test_write_geotiff_round_trip(tmp_path):
    """Write a 3x4 float32 array, read it back, assert values/nodata/driver."""
    rng = np.random.default_rng(42)
    arr = rng.random((3, 4), dtype=np.float32) * 100.0
    arr[1, 2] = np.nan  # one NaN cell -> must translate to nodata on disk
    transform = Affine(0.5, 0.0, 1000.0, 0.0, 0.5, 2000.0)
    out = tmp_path / "round_trip.tif"
    io_common.write_geotiff(arr, transform, out, crs=None, nodata=-9999.0)
    assert out.exists()

    with rasterio.open(out) as ds:
        assert ds.driver == "GTiff"
        assert ds.dtypes == ("float32",)
        assert ds.nodata == -9999.0
        assert ds.shape == (3, 4)
        assert ds.transform == transform
        data = ds.read(1)
    # finite cells round-trip exactly
    finite = np.isfinite(arr)
    np.testing.assert_array_equal(data[finite], arr[finite])
    # NaN cell translated to the chosen nodata
    assert data[1, 2] == -9999.0


def test_write_geotiff_default_nan_nodata_translates_to_f32_nodata():
    """Default nodata=NaN -> non-finite cells become F32_NODATA (-9999.0).

    This is the v1 C1 spec contract: ``GTIFF_NODATA_NAN`` (the
    preference for new rasters) falls back to ``F32_NODATA``
    (-9999.0) when a finite nodata is demanded by rasterio's
    GeoTIFF profile (GDAL can't write NaN as the nodata sentinel).
    """
    arr = np.array([[1.0, np.nan], [np.inf, 4.0]], dtype=np.float32)
    transform = Affine(1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    out = tmp_path_factory_unique() / "nan.tif"
    io_common.write_geotiff(arr, transform, out)  # default nodata=NaN
    with rasterio.open(out) as ds:
        assert ds.nodata == io_common.F32_NODATA
        data = ds.read(1)
    assert data[0, 0] == 1.0 and data[1, 1] == 4.0
    assert data[0, 1] == io_common.F32_NODATA  # NaN -> -9999.0
    assert data[1, 0] == io_common.F32_NODATA  # +inf -> -9999.0


def tmp_path_factory_unique():
    """Per-call tmp dir (pytest tmp_path is a fixture; this is a plain helper)."""
    import tempfile
    return Path(tempfile.mkdtemp(prefix="io_common_"))


# ---------------------------------------------------------------------------
# 5. AREA_MIN_PER_RUNG — equals canonical, same object as v0.2 pipeline
# ---------------------------------------------------------------------------


def test_area_min_table_matches_canonical():
    """The io_common copy must equal the connected_component_filter
    canonical byte-for-byte (V0.2_PLAN.md §4.1 is authoritative)."""
    from connected_component_filter import AREA_MIN_PER_RUNG as CANONICAL
    assert dict(io_common.AREA_MIN_PER_RUNG) == dict(CANONICAL)
    # Spot-check the keys + values explicitly (a one-character dict
    # typo here would crash the C3 --cc-filter auto arm at runtime).
    assert io_common.AREA_MIN_PER_RUNG[0.5] == 50
    assert io_common.AREA_MIN_PER_RUNG[1.0] == 20
    assert io_common.AREA_MIN_PER_RUNG[2.0] == 8
    assert io_common.AREA_MIN_PER_RUNG[5.0] == 3
    assert io_common.AREA_MIN_PER_RUNG[8.0] == 2
    assert io_common.AREA_MIN_PER_RUNG[10.0] == 2


def test_area_min_table_same_object_as_v0_2_pipeline_integration():
    """The v0.2 integration script imports io_common.AREA_MIN_PER_RUNG;
    the two names must reference the SAME dict object (so a future
    edit to io_common is reflected in the v0.2 script's table the
    next time it runs)."""
    from v0_2_pipeline_integration import AREA_MIN_PER_RUNG as V02_TABLE
    assert V02_TABLE is io_common.AREA_MIN_PER_RUNG


# ---------------------------------------------------------------------------
# 6. Behaviour-preservation — sag_detect.write_geotiff re-export
# ---------------------------------------------------------------------------


def test_sag_detect_write_geotiff_is_io_common_reexport():
    """``sag_detect.write_geotiff`` is the SAME function object as
    ``io_common.write_geotiff`` (v1 C1 re-export). The v0.5 E2E pin
    f1_test_slope = 0.029746281714785657 (test_e2e_fieg.py) and the
    smoke pins f1 0.392/0/0.800 + AUC 0.990 (test_smoke.py) must
    not drift because of this refactor — the detector's CLI does
    not call write_geotiff directly, but the v0.6 evaluation
    harness and any custom caller that does `import sag_detect;
    sag_detect.write_geotiff(...)` keep working unchanged.
    """
    import sag_detect
    assert sag_detect.write_geotiff is io_common.write_geotiff


def test_pinned_f1_values_still_in_place():
    """The pinned F1 numbers are unchanged (regression alarm guard).

    These constants live in the existing tests; the C1 refactor does
    not edit test_e2e_fieg.py or test_smoke.py. This test re-asserts
    the pin values to make any accidental edit to those constants
    fail LOUDLY here (rather than drift silently elsewhere).
    """
    import test_e2e_fieg as e2e
    import test_smoke as smk
    assert e2e.PIN_F1_SLOPE == 0.029746281714785657
    assert e2e.PIN_F1_TEST == 0.02023809523809524
    assert e2e.PIN_THRESHOLD == 0.15890802115201988
    assert smk.SMOKE_F1[0.5] == 0.39160839160839167
    assert smk.SMOKE_F1[2.0] == 0.0
    assert smk.SMOKE_F1[5.0] == 0.8
    assert smk.SMOKE_FUSION_AUC == 0.990