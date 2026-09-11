"""LOW-10 mirror for io_analog.py: xyz sentinel-threshold hardening.

Audit: notes/2026-09-04_AUDIT_REVIEW.md [LOW-10] (session 52 mirror).
Same root cause as convert_f32: the 1e3 m heuristic would silently NaN
edges of any future >1 km analog site (e.g. SP Mountain ~1.5 km).

New spec (session 52, mirroring convert_f32, adapted to loader semantics):
- SENTINEL_MAX_M = 1e6 (was SENTINEL_ABS = 1e3): xyz dropped only beyond
  1e6 m; NaNs continue to drop naturally via the np.isfinite mask.
- WARN_MAX_M = 100.0: ONE warning per load_xyz call if any KEPT |xyz|
  exceeds 100 m; message names the npz, the count, and the max value,
  cites "session 52 / LOW-10 mirror".
- Public API (load_xyz, voxel_downsample, master_grid) signatures
  unchanged; consumers (register_cave, coarse_search, explore_indian_tunnel)
  import unchanged.
- The wp1_analog outputs (coarse_search.json, registration_report.json,
  preflight_clouds.png, registration_validation.png) ARE in the frozen
  provenance chain (PROVENANCE_INDEX rows 46-49, status=canonical, 2026-
  08-21). The frozen outputs are NOT regenerated — sha256 hashes remain
  stable; the loader hardening only changes behavior on FUTURE loads.

MEASURED corpus facts (session 51, geo-coder read-only numpy pass,
2026-09-11): the gray band (1e3, 1e6] is NOT empty. NorthSurface
npz keeps 31 finite points up to ~620,616 m that the OLD 1-km rule
silently dropped. After this fix those points are KEPT-but-flagged
(one warning naming the file + 31 + ~620,616.4 m), consistent with
the project-wide visible-but-flagged philosophy.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from conftest import CODE_DIR

for _p in (str(CODE_DIR), str(CODE_DIR / "wp1_analog")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import io_analog  # noqa: E402


def _write_npz(tmp_path: Path, name: str, points: list[dict]) -> Path:
    """Write a minimal wp1_lla-shaped npz (x/y/z float32) and return its path.

    Mirrors convert_f32's _write_f32 helper: same minimal-fidelity
    synthetic pattern, npz flavor instead of .f32.
    """
    n = len(points)
    arr_x = np.array([p["x"] for p in points], dtype=np.float32)
    arr_y = np.array([p["y"] for p in points], dtype=np.float32)
    arr_z = np.array([p["z"] for p in points], dtype=np.float32)
    p = tmp_path / name
    np.savez_compressed(p, x=arr_x, y=arr_y, z=arr_z)
    return p


# --- constants (LOW-10 mirror) -----------------------------------------------


def test_sentinel_constants_low10_mirror():
    """SENTINEL_MAX_M and WARN_MAX_M mirror convert_f32 exactly."""
    assert io_analog.SENTINEL_MAX_M == 1e6
    assert io_analog.WARN_MAX_M == 100.0
    # Old SENTINEL_ABS name removed (it was the 1e3 heuristic); ensure the
    # 1e3 value is no longer reachable through this loader module.
    assert not hasattr(io_analog, "SENTINEL_ABS")


# --- sentinel regimes -------------------------------------------------------


def test_sentinel_regimes_low10_mirror(tmp_path):
    """500 m kept; 5000 m kept (old code NaNed it); 1e38 NaNed.

    Mirrors convert_f32 test_xyz_sentinel_regimes_low10.
    """
    pts = [
        dict(x=500.0, y=-500.0, z=100.0),       # |xyz| ~ 500: kept, quiet
        dict(x=5000.0, y=0.0, z=0.0),          # >1 km site edge: KEPT now
        dict(x=0.0, y=0.0, z=-5000.0),         # >1 km site edge: KEPT now
        dict(x=1e38, y=0.0, z=0.0),            # true sentinel: dropped
        dict(x=0.0, y=2e38, z=0.0),            # true sentinel: dropped
    ]
    p = _write_npz(tmp_path, "regimes.npz", pts)
    x, y, z = io_analog.load_xyz(p)
    # regime 1: |xyz| = 500 -> kept (input row 0)
    assert np.isfinite(x[0]) and np.isfinite(y[0]) and np.isfinite(z[0])
    # regime 2: |xyz| = 5000 -> KEPT under SENTINEL_MAX_M=1e6
    assert np.isfinite(x[1]) and np.isfinite(z[2])
    # regime 3: ~1e38 -> sentinel dropped
    assert len(x) == 3


def test_sentinel_boundary_strict_inequality_low10_mirror(tmp_path):
    """|xyz| exactly 1e6 dropped (strict <); just inside kept.

    Mirrors convert_f32 test_sentinel_boundary_strict_inequality_low10.
    Note convert_f32 used strict > (1e6 KEPT, 1.1e6 NaNed) because
    read_f32 marks xyz sentinel THEN zeros them; loader drops with
    strict <  so the SAME edge value flips (1e6 dropped, 1e6 - epsilon
    kept). The point is the threshold and strictness are pinned.
    """
    pts = [
        dict(x=1e6 - 1.0, y=0.0, z=0.0),     # just under 1e6 -> KEPT
        dict(x=1e6, y=0.0, z=0.0),          # exactly 1e6   -> dropped
        dict(x=1.1e6, y=0.0, z=0.0),        # above 1e6     -> dropped
    ]
    p = _write_npz(tmp_path, "boundary.npz", pts)
    x, y, z = io_analog.load_xyz(p)
    assert np.isfinite(x[0])
    assert len(x) == 1


def test_nan_dropped_naturally_low10_mirror(tmp_path):
    """NaN/inf xyz drop naturally via the np.isfinite mask (no sentinel needed)."""
    pts = [
        dict(x=float("nan"), y=1.0, z=1.0),
        dict(x=1.0, y=float("inf"), z=1.0),
        dict(x=1.0, y=1.0, z=float("-inf")),
        dict(x=42.0, y=-7.0, z=3.0),  # ordinary, quiet
    ]
    p = _write_npz(tmp_path, "nan.npz", pts)
    x, y, z = io_analog.load_xyz(p)
    assert len(x) == 1
    assert x[0] == pytest.approx(42.0)


# --- warning semantics ------------------------------------------------------


def test_gray_zone_warning_fires_once_low10_mirror(tmp_path, recwarn):
    """Kept |xyz| > 100 m -> exactly ONE session-52 warning per load."""
    pts = [
        dict(x=150.0, y=0.0, z=0.0),     # over 100 m on x
        dict(x=0.0, y=5000.0, z=0.0),    # over 100 m on y (same call)
        dict(x=2.0, y=-3.0, z=1.0),      # quiet point
    ]
    io_analog.load_xyz(_write_npz(tmp_path, "warn.npz", pts))
    s52 = [w for w in recwarn.list if "session 52" in str(w.message)]
    assert len(s52) == 1  # once per load_xyz call even though x and y both exceed
    msg = str(s52[0].message)
    assert "100 m" in msg
    assert "1e+06 m" in msg
    assert "warn.npz" in msg
    assert "2 points" in msg
    assert "5000.0" in msg  # max reported is the y=5000 (greater than 150)


def test_no_warning_below_100m_or_when_only_sentinels_low10_mirror(tmp_path, recwarn):
    """All kept |xyz| <= 100 m -> no warning; sentinels never warn.

    Mirrors convert_f32 test_no_warning_below_100m_and_sentinel_excluded_low10.
    """
    pts = [
        dict(x=50.0, y=-60.0, z=100.0),   # boundary 100 m is NOT over (strict >)
        dict(x=1e38, y=0.0, z=0.0),       # sentinel: dropped, excluded from warn
    ]
    p = _write_npz(tmp_path, "quiet.npz", pts)
    x, y, z = io_analog.load_xyz(p)
    assert np.isfinite(x[0]) and len(x) == 1
    s52 = [w for w in recwarn.list if "session 52" in str(w.message)]
    assert not s52


def test_measured_gray_band_regime_low10_mirror(tmp_path, recwarn):
    """Session 51 MEASURED regime: Indian_NorthSurface_1x_0p5m.npz keeps
    31 finite points up to ~620,616 m that the OLD 1-km rule silently
    dropped; after this fix they are KEPT-but-flagged (one warning
    naming file + 31 + max ~620,616.4 m).

    Frozen corpus is NOT regenerated; this test pins the loader
    behavior on a synthetic faithful copy.
    """
    pts = [
        dict(x=620616.4, y=0.0, z=0.0),    # measured NorthSurface max
        dict(x=-620616.4, y=0.0, z=0.0),   # second wild outlier
        dict(x=42.0, y=-7.0, z=3.0),       # ordinary, quiet
    ]
    p = _write_npz(tmp_path, "north_surface_mirror.npz", pts)
    x, y, z = io_analog.load_xyz(p)
    # gray-band values are KEPT (finite) — would have been dropped at 1e3
    assert len(x) == 3
    assert np.isfinite(x[0]) and np.isfinite(x[1]) and np.isfinite(x[2])
    s52 = [w for w in recwarn.list if "session 52" in str(w.message)]
    assert len(s52) == 1
    msg = str(s52[0].message)
    assert "north_surface_mirror.npz" in msg
    assert "2 points" in msg
    assert "620616.4" in msg


# --- public API stability (consumers must still import) ---------------------


def test_consumer_imports_unchanged():
    """The three consumer modules reference io_analog's public names.

    Session-53 fix: this used to be an AST-parsing smoke test that
    papered over the latent landmine in ``explore_indian_tunnel.py``
    (which executed ``load_xyz + plt.savefig`` at module-import time).
    After the session-53 refactor that module is import-safe, so we
    can now do a real ``importlib.import_module`` and assert:

      (a) the module imports cleanly without side effects — the canonical
          ``preflight_clouds.png`` (PROVENANCE_INDEX row 47, sha256
          ``ea376b2f…``, status=canonical) mtime is unchanged across the
          import;
      (b) ``main`` exists and is callable;
      (c) ``OUT / "preflight_clouds.png"`` is still sha256 ``ea376b2f…``
          AFTER the import (no overwrite).

    The other two consumer modules (``register_cave``, ``coarse_search``)
    are still AST-checked for their ``from io_analog import ...``
    statement — those never ran side effects on import, so the real
    import approach below is sufficient for the third.
    """
    import importlib
    import importlib.util

    import ast

    # Real import of the refactored explore_indian_tunnel — proves
    # import-safety (no load_xyz / no savefig at import time).
    wp1 = CODE_DIR / "wp1_analog"
    canonical_png = CODE_DIR.parent / "data" / "outputs" / "wp1_analog" / "registration" / "preflight_clouds.png"
    CANONICAL_SHA = "ea376b2fb1b283a287e2348e54c09dd8901398a90760c1d5e46a6dc3e8d61b88"

    # (a) import is side-effect-free: mtime + sha256 of canonical PNG
    # must not change across the import.
    pre_mtime = canonical_png.stat().st_mtime
    pre_sha = _sha256_file(canonical_png)
    spec = importlib.util.spec_from_file_location(
        "explore_indian_tunnel", wp1 / "explore_indian_tunnel.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    post_mtime = canonical_png.stat().st_mtime
    post_sha = _sha256_file(canonical_png)
    assert pre_mtime == post_mtime, (
        f"explore_indian_tunnel import overwrote canonical PNG mtime "
        f"({pre_mtime} -> {post_mtime})"
    )
    assert pre_sha == CANONICAL_SHA and post_sha == CANONICAL_SHA, (
        f"canonical preflight_clouds.png sha256 drifted: pre={pre_sha} "
        f"post={post_sha} expected={CANONICAL_SHA}"
    )

    # (b) main exists and is callable; module also exposes quick_dtm
    # + SITES (useful to importers, per the refactor docstring).
    assert callable(getattr(mod, "main", None))
    assert callable(getattr(mod, "quick_dtm", None))
    assert {"NorthSurface", "Collapse3", "Cave1x"} <= set(mod.SITES)
    assert (mod.OUT / "preflight_clouds.png").name == "preflight_clouds.png"

    # Other two consumers (no side effects on import historically) —
    # keep the AST check for their ``from io_analog import ...`` line
    # so a silent rename of the loader still surfaces here.
    expected_io_imports = {
        "register_cave.py":     {"load_xyz", "voxel_downsample"},
        "coarse_search.py":     {"load_xyz", "voxel_downsample"},
    }
    for fname, names in expected_io_imports.items():
        tree = ast.parse((wp1 / fname).read_text())
        io_imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "io_analog":
                io_imports |= {n.name for n in node.names}
        assert names <= io_imports, (
            f"{fname} imports from io_analog: {sorted(io_imports)}; "
            f"expected at least {sorted(names)}"
        )

    # the names themselves must still resolve on the loader module
    assert hasattr(io_analog, "load_xyz")
    assert hasattr(io_analog, "voxel_downsample")
    assert hasattr(io_analog, "master_grid")


def _sha256_file(p: Path) -> str:
    """SHA-256 of a file in hex (helper for canonical-PNG assertions)."""
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def test_public_signatures_unchanged():
    """Public API signatures: load_xyz(npz_path, max_points=None, seed=42),
    voxel_downsample(x, y, z, voxel, seed=42), master_grid(x, y, spacing=0.5).
    Pin via inspect to fail loudly if anyone changes default semantics.
    """
    import inspect

    s_load = inspect.signature(io_analog.load_xyz)
    assert list(s_load.parameters) == ["npz_path", "max_points", "seed"]
    assert s_load.parameters["max_points"].default is None
    assert s_load.parameters["seed"].default == 42

    s_vd = inspect.signature(io_analog.voxel_downsample)
    assert list(s_vd.parameters) == ["x", "y", "z", "voxel", "seed"]
    assert s_vd.parameters["voxel"].default is inspect.Parameter.empty
    assert s_vd.parameters["seed"].default == 42

    s_mg = inspect.signature(io_analog.master_grid)
    assert list(s_mg.parameters) == ["x", "y", "spacing"]
    assert s_mg.parameters["spacing"].default == 0.5
