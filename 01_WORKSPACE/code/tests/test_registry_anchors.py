"""B5 anchors-resolve proof (plan v2, session 57) — executable provenance.

For EVERY registry data row (278), the (dtm, rung) anchor derived from
the row itself — dtm column + rung parsed from the candidate_id suffix
by registry_io.parse_rung_cm (cm; /100 -> m, e.g.
`LV-FECUNPIT-0500cm-r003` -> 5.0 m) — must resolve to an entry in
transfer_summary.json `pair_results` (54 per-(DTM x rung) dicts), and
the evidence column must point at that same transfer context as
`<transfer_summary path>#<candidate_id>`.

B5 verdict carried by this test: per-candidate records live IN the
registry (peaks = sag_amp_m/span_m/score, rung in the id suffix) with
evidence pointers joining to pair_results (raster path via
pair_results.source_score_tif) — "anchors resolve, proven executable"
while this test stays green.
"""
from __future__ import annotations

import json
from pathlib import Path

from conftest import REPO_ROOT
from wp5_fusion.registry_io import load_registry, parse_rung_cm

REGISTRY = REPO_ROOT / "01_WORKSPACE/data/candidate_registry.csv"
TRANSFER = (REPO_ROOT / "01_WORKSPACE/data/outputs/wp2_sag/transfer/"
            "transfer_summary.json")


def _load_pairs() -> dict[tuple[str, float], dict]:
    ts = json.loads(TRANSFER.read_text())
    return {(p["dtm"], float(p["rung_m"])): p for p in ts["pair_results"]}


def test_all_registry_rows_anchor_to_transfer_pairs():
    df = load_registry(REGISTRY)
    pairs = _load_pairs()
    assert len(pairs) == 54  # per-(DTM x rung) context dict count is frozen

    unresolved = []
    for row in df.itertuples(index=False):
        rung_m = parse_rung_cm(row.candidate_id) / 100.0
        pair = pairs.get((row.dtm, rung_m))
        if pair is None:
            unresolved.append((row.candidate_id, row.dtm, rung_m))
    assert not unresolved, (
        f"{len(unresolved)}/278 registry rows do not resolve to a "
        f"transfer_summary pair_results entry: {unresolved[:5]}"
    )


def test_evidence_pointers_join_registry_to_transfer_context():
    df = load_registry(REGISTRY)
    prefix = ("01_WORKSPACE/data/outputs/wp2_sag/transfer/"
              "transfer_summary.json#")
    for row in df.itertuples(index=False):
        assert row.evidence == f"{prefix}{row.candidate_id}", (
            f"evidence pointer for {row.candidate_id} does not follow the "
            f"<transfer_summary.json>#<candidate_id> join convention: "
            f"{row.evidence!r}"
        )


def test_anchors_rung_units_are_metres_consistent():
    """parse_rung_cm returns cm; /100 gives the metres used by rung_m.
    Sanity: every registry rung lands on the 2/4/5/8 m ladder."""
    df = load_registry(REGISTRY)
    rungs_m = {parse_rung_cm(cid) / 100.0 for cid in df["candidate_id"]}
    assert rungs_m <= {2.0, 4.0, 5.0, 8.0}
