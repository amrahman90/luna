"""LOW-10: convert_f32.py xyz sentinel-threshold hardening.

Audit: notes/2026-09-04_AUDIT_REVIEW.md [LOW-10] (subagent CORR-10).
Old behavior: |x|/|y|/|z| > 1e3 m was treated as sentinel — a
heuristic tuned to the current 4 analog sites (all <1 km extent)
that would silently NaN the edges of any future >1 km site
(e.g. SP Mountain ~1.5 km).

New spec (session 51 correction: NOT dormant — measured gray band is
non-empty; Kingsbowl_orig.f32 has 37 points with |xyz| in (1e3, 1e6]
(max ~930,515.8 m), Indian_NorthSurface_1x.f32 has 31 (max
~620,616.4 m); the frozen corpus is NOT regenerated, and any future
re-run must review gray-band points explicitly):
- true sentinel ~1e38; xyz NaNed only beyond SENTINEL_MAX_M = 1e6;
- one warning per read_f32 call if any KEPT |xyz| > WARN_MAX_M (100 m);
- gray-band counts/max also exposed via convert_f32.LAST_READ_DIAGNOSTICS;
- color/NIR bound unchanged: ATTR_SENTINEL_MAX = 1e3 (colors [0,255]).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from conftest import CODE_DIR

for _p in (str(CODE_DIR), str(CODE_DIR / "wp1_lla")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import convert_f32  # noqa: E402


def _write_f32(tmp_path, points: list[dict]) -> Path:
    """Write a tiny synthetic .f32 (7 attrs/point) and return its path."""
    arr = np.zeros(len(points), dtype=convert_f32.DTYPE)
    for i, p in enumerate(points):
        for k, v in p.items():
            arr[i][k] = v
    f = tmp_path / "synth.f32"
    f.write_bytes(arr.tobytes())
    return f


def test_sentinel_constants_low10():
    assert convert_f32.SENTINEL_MAX_M == 1e6
    assert convert_f32.WARN_MAX_M == 100.0
    assert convert_f32.ATTR_SENTINEL_MAX == 1e3  # color/NIR bound, unchanged


def test_xyz_sentinel_regimes_low10(tmp_path):
    """500 m kept; 5000 m kept (old code NaNed it); 1e38 NaNed."""
    pts = [
        dict(x=500.0, y=-500.0, z=100.0, nir=120.0, r=200.0, g=150.0, b=100.0),
        dict(x=5000.0, y=0.0, z=0.0, nir=120.0, r=200.0, g=150.0, b=100.0),  # >1 km site edge
        dict(x=0.0, y=0.0, z=-5000.0, nir=120.0, r=200.0, g=150.0, b=100.0),
        dict(x=1e38, y=0.0, z=0.0, nir=120.0, r=200.0, g=150.0, b=100.0),  # true sentinel
        dict(x=0.0, y=2e38, z=0.0, nir=120.0, r=200.0, g=150.0, b=100.0),
    ]
    out = convert_f32.read_f32(_write_f32(tmp_path, pts))
    # regime 1: |xyz| = 500 -> kept, all attrs finite
    for f in ("x", "y", "z", "nir", "r", "g", "b"):
        assert np.isfinite(out[f][0]), f
    # regime 2: |xyz| = 5000 -> KEPT under SENTINEL_MAX_M=1e6 (would
    # have been NaNed by the pre-LOW-10 1e3 threshold)
    for f in ("x", "y", "z"):
        assert np.isfinite(out[f][1]), f
        assert np.isfinite(out[f][2]), f
    # regime 3: ~1e38 -> sentinel: whole xyz triple NaNed
    for f in ("x", "y", "z"):
        assert np.isnan(out[f][3]), f
        assert np.isnan(out[f][4]), f
    # per-attribute colors survive the xyz sentinel (unchanged behavior)
    assert np.isfinite(out["nir"][3]) and np.isfinite(out["r"][3])


def test_sentinel_boundary_strict_inequality_low10(tmp_path):
    """|xyz| exactly 1e6 kept (strict >); just above NaNed."""
    pts = [
        dict(x=1e6, y=0.0, z=0.0),
        dict(x=0.0, y=0.0, z=1.1e6),
    ]
    out = convert_f32.read_f32(_write_f32(tmp_path, pts))
    assert np.isfinite(out["x"][0])
    assert np.isnan(out["z"][1]) and np.isnan(out["x"][1])


def test_gray_zone_warning_fires_once_low10(tmp_path, recwarn):
    """Kept |xyz| > 100 m -> exactly ONE LOW-10 warning per read."""
    pts = [
        dict(x=150.0, y=0.0, z=0.0),   # over 100 m on x
        dict(x=0.0, y=5000.0, z=0.0),  # over 100 m on y (same read)
        dict(x=2.0, y=-3.0, z=1.0),    # quiet point
    ]
    convert_f32.read_f32(_write_f32(tmp_path, pts))
    low10 = [w for w in recwarn.list if "LOW-10" in str(w.message)]
    assert len(low10) == 1  # once per read even though x and y both exceed
    msg = str(low10[0].message)
    assert "100 m" in msg and "1e+06 m" in msg and "synth.f32" in msg


def test_no_warning_below_100m_and_sentinel_excluded_low10(tmp_path, recwarn):
    """All kept |xyz| <= 100 m -> no warning; sentinels never warn."""
    pts = [
        dict(x=50.0, y=-60.0, z=100.0),  # exactly 100 m is NOT over (> strict)
        dict(x=1e38, y=0.0, z=0.0),      # sentinel: NaNed, excluded from warn
    ]
    out = convert_f32.read_f32(_write_f32(tmp_path, pts))
    assert np.isfinite(out["x"][0]) and np.isnan(out["x"][1])
    assert not [w for w in recwarn.list if "LOW-10" in str(w.message)]


def test_attr_sentinel_bound_unchanged_low10(tmp_path):
    """Color/NIR bound stays 1e3 (colors are [0,255]) — pinned unchanged."""
    pts = [
        dict(x=1.0, y=1.0, z=1.0, nir=250.0, r=255.0, g=0.0, b=128.0),
        dict(x=1.0, y=1.0, z=1.0, nir=2000.0, r=255.0, g=0.0, b=128.0),
    ]
    out = convert_f32.read_f32(_write_f32(tmp_path, pts))
    assert np.isfinite(out["nir"][0])
    assert np.isnan(out["nir"][1]) and np.isfinite(out["r"][1])


def test_measured_gray_band_regime_low10(tmp_path, recwarn):
    """Session 51: the MEASURED regime — wild outliers in the gray band
    are kept + flagged, never silently NaNed or silently kept.

    Motivating corpus (read-only numpy count, geo-coder session 51,
    2026-09-11, confirming the verifier):
      ~/lunarvoid/data/lltb1/Kingsbowl/f32/Kingsbowl_orig.f32
        — 37 points with |xyz| in (1e3, 1e6], max 930,515.8 m
      ~/lunarvoid/data/lltb1/IndianTunnel_NorthSurface/f32/
        Indian_NorthSurface_1x.f32 — 31 points, max 620,616.4 m
    Sites are <=1.2 km extent, so these are wild outliers; the old 1e3
    filter NaNed them, the 1e6 threshold keeps them visible-but-flagged.
    The frozen npz corpus is NOT regenerated (regeneration forbidden).
    """
    pts = [
        dict(x=930515.8, y=0.0, z=0.0),    # measured Kingsbowl max (gray band)
        dict(x=0.0, y=-620616.4, z=0.0),   # measured NorthSurface max
        dict(x=1e38, y=0.0, z=0.0),        # true sentinel -> NaNed
        dict(x=42.0, y=-7.0, z=3.0),       # ordinary point, no warning
    ]
    out = convert_f32.read_f32(_write_f32(tmp_path, pts))
    # gray-band values are KEPT (finite) — would have been NaNed at 1e3
    assert np.isfinite(out["x"][0]) and np.isfinite(out["y"][1])
    # true sentinel still NaNed; ordinary point untouched
    assert np.isnan(out["x"][2]) and np.isfinite(out["x"][3])
    # exactly one LOW-10 warning, reporting both gray points + the max
    low10 = [w for w in recwarn.list if "LOW-10" in str(w.message)]
    assert len(low10) == 1
    msg = str(low10[0].message)
    assert "2 points" in msg and "930515.8" in msg
    # diagnostics side channel (session 51): no warning-text parsing needed
    d = convert_f32.LAST_READ_DIAGNOSTICS
    assert d["n_gray_band"] == 2
    assert d["n_xyz_sentinel"] == 1
    assert d["gray_band_max_abs_m"] == pytest.approx(930515.8, abs=0.1)
    assert d["n_total"] == 4
