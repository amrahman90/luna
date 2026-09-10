"""C3: --cc-filter wiring tests (off/on/auto dispatch + AREA_MIN table).

Fast synthetic coverage for the sag_detect.apply_cc_filter dispatch and
the canonical AREA_MIN table in connected_component_filter. The real-data
parity/E2E coverage lives in test_e2e_fieg.py (filter-off pins, frozen
Paper 1/2 evidence) and in
data/outputs/wp1_detector/cc_filter_evaluation_v0_6.json (7-site battery).

Provenance: task C3 (LLTB-1 v0.6 candidate), 2026-09-10. Decision rule
outcome at authoring time: default --cc-filter off (auto improved 0/7
sites, non-regressing 7/7 — see cc_filter_evaluation_v0_6.json).
"""
from __future__ import annotations

import sys

import numpy as np
import pytest

from conftest import CODE_DIR

for _p in (str(CODE_DIR), str(CODE_DIR / "wp1_detector")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sag_detect  # noqa: E402
from connected_component_filter import (  # noqa: E402
    AREA_MIN_PER_RUNG,
    area_min_for_rung,
)


def _synth_score(seed: int = 42) -> np.ndarray:
    """Score raster with one 30-cell blob, three 4-cell specks, NaN corner."""
    rng = np.random.default_rng(seed)
    s = rng.normal(0.0, 0.05, (64, 64))
    s[20:26, 20:26] = 1.0            # 36-cell kept component
    s[50:52, 50:52] = 0.9            # 4-cell speck
    s[8:10, 40:42] = 0.9             # 4-cell speck
    s[40:42, 8:10] = 0.9             # 4-cell speck
    s[0, 0] = np.nan
    return s


# --- AREA_MIN table ---------------------------------------------------------

def test_area_min_table_matches_v02_plan():
    # V0.2_PLAN.md §4.1 (authoritative per task C3 dispatch)
    assert AREA_MIN_PER_RUNG == {0.5: 50, 1.0: 20, 2.0: 8, 5.0: 3, 8.0: 2, 10.0: 2}


@pytest.mark.parametrize("rung,expected", [(0.5, 50), (1.0, 20), (2.0, 8),
                                           (5.0, 3), (8.0, 2), (10.0, 2),
                                           (1.5, 20), (7.0, 2)])
def test_area_min_for_rung_lookup(rung, expected):
    assert area_min_for_rung(rung) == expected


# --- apply_cc_filter dispatch ------------------------------------------------

def test_off_mode_is_legacy_parity():
    """off == filter_small_components(min_component): v0.5 byte parity."""
    s = _synth_score()
    thr = 0.5
    pred, audit = sag_detect.apply_cc_filter(s, thr, "off", 5, None, 1.0)
    legacy = sag_detect.filter_small_components(s >= thr, min_size=5)
    assert np.array_equal(pred, legacy)
    assert audit["cc_filter"] == "off"
    assert audit["cc_area_min_effective"] == 5
    assert audit["cc_components_total"] == 4
    assert audit["cc_components_kept"] == 1
    assert audit["cc_components_dropped"] == 3
    assert audit["cc_components_dropped_ratio"] == pytest.approx(0.75)


def test_auto_mode_uses_table_and_module_engine():
    s = _synth_score()
    thr = 0.5
    pred, audit = sag_detect.apply_cc_filter(s, thr, "auto", 5, None, 1.0)
    assert audit["cc_area_min_effective"] == 20  # table @ 1 m rung
    # the 36-cell blob survives; the three 4-cell specks drop
    assert pred[20:26, 20:26].all()
    assert not pred[50:52, 50:52].any()
    assert not pred[8:10, 40:42].any()
    assert not pred[40:42, 8:10].any()
    assert audit["cc_components_dropped"] == 3
    assert audit["cc_cells_dropped"] == 12


def test_on_mode_uniform_area_min():
    s = _synth_score()
    thr = 0.5
    # uniform 4 keeps everything (specks are exactly 4 cells)
    _, audit = sag_detect.apply_cc_filter(s, thr, "on", 5, 4, 5.0)
    assert audit["cc_area_min_effective"] == 4
    assert audit["cc_components_dropped"] == 0
    # falls back to min_component when --cc-area-min is None
    _, audit2 = sag_detect.apply_cc_filter(s, thr, "on", 6, None, 5.0)
    assert audit2["cc_area_min_effective"] == 6
    assert audit2["cc_components_dropped"] == 3


def test_cc_filter_survives_thr0_predict_all():
    """thr=0 (tuner-collapse mode): an all-above-threshold surface is
    ONE component; the filter must keep it whole (minus the NaN cell),
    not NaN-break or empty it."""
    rng = np.random.default_rng(42)
    s = rng.uniform(0.5, 1.0, (64, 64))  # strictly positive everywhere
    s[0, 0] = np.nan
    pred, audit = sag_detect.apply_cc_filter(s, 0.0, "auto", 5, None, 0.5)
    assert pred.sum() == int(np.isfinite(s).sum())
    assert audit["cc_components_total"] == 1
    assert audit["cc_components_dropped"] == 0
    assert not pred[0, 0]  # NaN cell never predicts


# --- CLI surface (help text only; heavy runs live in the E2E file) -----------

def test_cli_has_cc_filter_flags(sag_help):
    assert "--cc-filter" in sag_help
    for choice in ("off", "on", "auto"):
        assert choice in sag_help
    assert "--cc-area-min" in sag_help


def test_cli_default_is_off():
    """Authoritative default check via the real parser (decision-rule
    outcome: default off — auto improved 0/7 sites, see the 7-site
    battery JSON; re-pin deliberately only)."""
    ap = sag_detect.build_arg_parser()
    args = ap.parse_args(["--npz", "x.npz", "--outdir", "y"])
    assert args.cc_filter == "off"
    assert args.cc_area_min is None
    assert args.min_component == 5
