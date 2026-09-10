"""C11: real-data end-to-end fixture test — Fieg 0.5 m analog LiDAR.

Chain (all against REAL on-disk artifacts, which are the ground truth
per conventions §7):

  1. locate the frozen analog input  <LUNARVOID_DATA>/lltb1/Fieg/Fieg_0.5m.npz
     (61,519,449 bytes, 11,703,363 points, source Fieg_A.f32 — the
     duplicates Fieg_A_0p5m.npz / Fieg_0.5m.npz are byte-identical
     conversions; Fieg_0.5m.npz is the run_lltb1.py naming product)
  2. run the production LLTB-1 v0.5 detector path —
     wp1_detector/sag_detect.py CLI (run_lltb1.py's v0.1 driver stages
     convert_f32 -> degrade -> vci -> sag_detect; the npz+rungs stage
     IS sag_detect.py) — at its documented default: FIXED
     --slope-mask-degrees 10 (conventions §5 + LLTB-1 table note:
     tune-slope regresses cave_1x, use fixed 10 deg), --min-component 5,
     --seed 42, rung 0.5 m only.
  3. ground truth = sag_detect.cloud_ground_truth: 21x21 nan-robust
     median local envelope, threshold 1.0 m (conventions §2 — the
     5x5-min variant is the historical session-2 bug).
  4. assert the test-split F1 (post component-filter + slope mask,
     'f1_test_slope') equals the PIN within 1e-5, AND independently
     recompute that F1 from the saved score/pred/slope_ok rasters plus
     a GT recomputed from the npz — the pinned number must survive a
     from-rasters reconstruction, not just a summary read.

Local-only: skips (with reason) when the npz is absent — e.g. on CI or
when LUNARVOID_DATA points at an empty dir (the C11 skip-verification).

PINNED VALUE — PROVENANCE
-------------------------
- f1_test_slope = 0.029746281714785657   (primary pin, 1e-5 tolerance)
- f1_test       = 0.02023809523809524    (pre-slope, secondary pin)
- threshold     = 0.15890802115201988    (cal-half tuned score threshold)
- gt void cells = 84 on the 150x194 master grid (0.3 %)
- Pinned: 2026-09-10 by geo-coder (task C11).
- Code state: git cdb8f08 (clean tree) at pin time.
- Pin command:
    PYTHONPATH=01_WORKSPACE/code ~/lunarvoid/venv/bin/python \
        01_WORKSPACE/code/wp1_detector/sag_detect.py \
        --npz ~/lunarvoid/data/lltb1/Fieg/Fieg_0.5m.npz \
        --outdir <tmp> --rungs 0.5
  (PYTHONPATH is required since the C9 shared-_crs refactor; production
  callers import wp1_detector.sag_detect with code/ on sys.path.)
- Cross-check: 0.0297 matches the "v0.3 default gave F1=0.0297" note in
  verify_v04_tune_slope.py — continuity with the stored evidence.

RE-PIN PROCEDURE (deliberate only): after a user-approved detector
change, re-run the pin command, paste the new full-precision
f1_test_slope / f1_test / threshold / gt cells above, and update the
date + git describe in this comment. An unexpected mismatch is the
regression alarm — investigate, do not re-pin.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from conftest import CODE_DIR, DATA_ROOT

for _p in (str(CODE_DIR), str(CODE_DIR / "wp1_detector")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

NPZ = DATA_ROOT / "lltb1/Fieg/Fieg_0.5m.npz"

# --- pins (see provenance above) -------------------------------------------
PIN_F1_SLOPE = 0.029746281714785657
PIN_F1_TEST = 0.02023809523809524
PIN_THRESHOLD = 0.15890802115201988
PIN_GT_VOID_CELLS = 84
PIN_SHAPE = (150, 194)
TOL = 1e-5

pytestmark = [pytest.mark.localdata, pytest.mark.slow]


def _skip_if_no_data():
    if not NPZ.exists():
        pytest.skip(
            f"Fieg analog npz is local-only: {NPZ} absent "
            f"(LUNARVOID_DATA={DATA_ROOT}); CI and hidden-data runs skip")


@pytest.fixture(scope="module")
def e2e(sag_run):
    """One detector run per session, shared by the tests below."""
    _skip_if_no_data()
    return sag_run(NPZ, [0.5])


def test_detector_run_succeeds(e2e):
    assert e2e["rc"] == 0, f"sag_detect rc={e2e['rc']}: {e2e['stderr'][-400:]}"
    assert e2e["summary"] is not None, "sag_summary.json not produced"


def test_pinned_config_echo(e2e):
    """The run used the documented defaults (guards silent default drift)."""
    r0 = e2e["summary"]["rungs"][0]
    assert r0["res_m"] == 0.5
    assert r0["slope_mask_degrees"] == 10.0, "fixed 10-deg slope mask required"
    assert r0["slope_mask_tuned"] is False, "--tune-slope must be OFF here"
    assert r0["min_component"] == 5
    assert tuple(r0["shape"]) == PIN_SHAPE


def test_pinned_f1_values(e2e):
    r0 = e2e["summary"]["rungs"][0]
    assert abs(r0["f1_test_slope"] - PIN_F1_SLOPE) <= TOL, (
        f"f1_test_slope={r0['f1_test_slope']!r} != pin {PIN_F1_SLOPE!r}")
    assert abs(r0["f1_test"] - PIN_F1_TEST) <= TOL
    assert abs(r0["threshold"] - PIN_THRESHOLD) <= TOL


def test_ground_truth_recomputed_from_npz(e2e):
    """21x21 nan-robust-median GT recomputed from the raw cloud matches
    the run's master-grid void-cell count (conventions §2 semantics)."""
    import sag_detect
    data = np.load(NPZ)
    gt, _geo = sag_detect.cloud_ground_truth(
        data["x"], data["y"], data["z"], 0.5, threshold_depth=1.0)
    assert gt.shape == PIN_SHAPE
    assert int(gt.sum()) == PIN_GT_VOID_CELLS == e2e["summary"]["gt_void_cells_master"]


def test_f1_recomputed_from_rasters(e2e):
    """Independent reconstruction: score/pred/slope_ok GeoTIFFs + seed-42
    50/50 split + recomputed GT must reproduce f1_test_slope exactly."""
    import rasterio
    import sag_detect

    outdir = e2e["outdir"]
    with rasterio.open(outdir / "score_0.5m.tif") as ds:
        score = ds.read(1)
    with rasterio.open(outdir / "pred_0.5m.tif") as ds:
        pred = ds.read(1) > 0.5
    with rasterio.open(outdir / "slope_ok_0.5m.tif") as ds:
        slope_ok = ds.read(1) > 0.5

    # rebuild the identical 50/50 split (seed 42 over finite-score cells)
    rng = np.random.default_rng(42)
    ev = np.argwhere(np.isfinite(score))
    perm = rng.permutation(len(ev))
    n_cal = len(ev) // 2
    cal_mask = np.zeros(score.shape, dtype=bool)
    cal_mask[ev[perm[:n_cal]][..., 0], ev[perm[:n_cal]][..., 1]] = True
    test_mask = np.isfinite(score) & ~cal_mask

    data = np.load(NPZ)
    gt, _geo = sag_detect.cloud_ground_truth(
        data["x"], data["y"], data["z"], 0.5, threshold_depth=1.0)

    r0 = e2e["summary"]["rungs"][0]
    # (a) the saved pred raster is exactly filter(score >= thr, min_size=5)
    pred_rebuilt = sag_detect.filter_small_components(
        score >= r0["threshold"], min_size=5)
    assert np.array_equal(pred_rebuilt, pred), \
        "saved pred_0.5m.tif does not reproduce from score + threshold + filter"
    # (b) the headline F1 recomputes from the rasters
    m = sag_detect._f1_from_pred((pred & slope_ok)[test_mask], gt[test_mask])
    assert abs(m["f1"] - r0["f1_test_slope"]) <= 1e-9, (
        f"raster-recomputed F1 {m['f1']!r} != summary {r0['f1_test_slope']!r}")
    assert abs(m["f1"] - PIN_F1_SLOPE) <= TOL
