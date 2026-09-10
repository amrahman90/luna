"""C4: the §7 smoke canary as a pytest.

Wraps ``code/smoke_test.py`` (synthetic analog cloud -> ladder -> VCI ->
sag detect per rung -> Z3.2 fusion) via a session-cached subprocess run
and asserts the KNOWN-GOOD anchors exactly, so any drift in the module
chain trips the suite.

Pinned values — PROVENANCE
--------------------------
- Pinned:     2026-09-10 by geo-coder (task C4).
- Code state: git cdb8f08 (clean tree) at pin time.
- Command:    ~/lunarvoid/venv/bin/python 01_WORKSPACE/code/smoke_test.py \
                  --outdir <tmp>
- f1_test values below are the FULL-PRECISION numbers read from
  smoke_summary.json (the console prints them rounded to 3 dp:
  0.392 / 0.000 / 0.800). The FUSION AUC is parsed from the canonical
  stdout line "FUSION : AUC=0.990" — the script prints 3 dp and writes
  no JSON key for it, so the printed value IS the canonical anchor
  (this mirrors verify_phase0_2026-09-04.py check 1).

RE-PIN PROCEDURE (deliberate changes only, after a user-approved
detector/module change): re-run the command above, paste the new
full-precision per-rung f1_test values and the FUSION AUC line into
SMOKE_F1 / SMOKE_FUSION_AUC, and update the date + ``git describe``
in this comment block. Never re-pin to "make the suite green" without
a documented reason — a mismatch here is the regression alarm.
"""
from __future__ import annotations

import re

import pytest

# --- pins (see provenance above) -------------------------------------------
SMOKE_F1: dict[float, float] = {
    0.5: 0.39160839160839167,
    2.0: 0.0,
    5.0: 0.8,
}
SMOKE_FUSION_AUC = 0.990
TOL = 1e-6  # dispatch spec: known-good values within 1e-6


def test_smoke_exits_zero(smoke_run):
    assert smoke_run["rc"] == 0, (
        f"smoke_test.py exited {smoke_run['rc']}:\n{smoke_run['stderr'][-800:]}")


def test_smoke_summary_written(smoke_run):
    assert smoke_run["summary"] is not None, "smoke_summary.json missing"


def test_smoke_rung_set(smoke_run):
    """The three canonical rungs, in order."""
    res = [r["res_m"] for r in smoke_run["summary"]["rungs"]]
    assert res == sorted(SMOKE_F1), f"rungs changed: {res} vs {sorted(SMOKE_F1)}"


@pytest.mark.parametrize("rung", sorted(SMOKE_F1), ids=lambda r: f"{r:g}m")
def test_smoke_f1_per_rung(smoke_run, rung):
    """Per-rung test-split F1 equals the pin within 1e-6 (exact det. pipeline)."""
    by_res = {r["res_m"]: r for r in smoke_run["summary"]["rungs"]}
    assert abs(by_res[rung]["f1_test"] - SMOKE_F1[rung]) <= TOL, (
        f"rung {rung} m: f1_test={by_res[rung]['f1_test']!r} "
        f"!= pin {SMOKE_F1[rung]!r}")


def test_smoke_fusion_auc(smoke_run):
    """Z3.2 fusion AUC equals 0.990 (canonical stdout line)."""
    matches = re.findall(r"FUSION\s*:\s*AUC=([\d.]+)", smoke_run["stdout"])
    assert matches, "no 'FUSION : AUC=...' line in smoke_test.py stdout"
    auc = float(matches[0])
    assert abs(auc - SMOKE_FUSION_AUC) <= TOL, (
        f"fusion AUC {auc!r} != pin {SMOKE_FUSION_AUC!r}")
