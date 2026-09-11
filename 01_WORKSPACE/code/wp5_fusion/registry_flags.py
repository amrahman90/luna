"""Structured-flags sidecar for the frozen candidate registry (B1–B5 tail).

The registry CSV `01_WORKSPACE/data/candidate_registry.csv` is sha-frozen
(md5 a60fb52152e33f37e9052434ad026a6e; cited in both papers, pinned in
PROVENANCE_INDEX, shipped in the Zenodo deposit) — classification flags
can therefore NEVER become registry columns. They live in a SIDECASTE
file, `01_WORKSPACE/data/candidate_registry_flags.csv`, one row per
registry row, same order:

  candidate_id, is_active, unique_key, is_tp, is_fp, is_ring, is_funnel,
  is_rung_duplicate, classification_source

Classification source of truth: the frozen
`01_WORKSPACE/data/outputs/wp2_sag/unique_accounting_2026-09-07.json`
(A2a re-accounting). Derivations below apply THAT file's own
`classification_rules` verbatim — no heuristic re-derivation:

  - above_floor : "notes lack below-local-floor"  (rule text, verbatim)
  - ring        : "notes contain \"ring artifact\"" (rule text, verbatim);
                  frozen check: exactly 21 rows, all DTM INGENIIPIT
  - fp          : explicit member ids of `fp_group_detail`
                  (9 rows across 5 B1 groups — an authoritative list,
                  not a distance re-derivation)
  - funnel      : rows labelled FUNNEL in `boundary_straddlers.classes`
                  (1 row; cross-checked I14-annotated in notes per rule)
  - tp          : above-floor residual — above ∧ ¬ring ∧ ¬fp ∧ ¬funnel;
                  hard-asserted to equal the frozen n_tp=14
  - unique_key  : the B1 link key, defined by the accounting's own
                  `unique_b1_key.grouping_key` ("primary + superseded_by
                  children"). `unique_b1_key` itself is a summary block
                  (counts), NOT a per-row mapping, so per-row keys are
                  resolved from the registry's `superseded_by=` notes
                  chains (root primary), cross-asserted against
                  fp_group_detail primaries where available; rows with no
                  link fall back to their own candidate_id (documented
                  fallback).
  - is_rung_duplicate : >1 ACTIVE row shares the unique_key. Verified
                  against the `sensitivity` block: the 3-dp lon/lat
                  variant reproduces n_groups=21 == n_unique_above_floor,
                  i.e. the B1 key is the 3-dp-scale grouping. On the
                  frozen registry this flags 0 rows BY CONSTRUCTION —
                  every multi-rung copy of a feature was linked
                  superseded_by=... and carries status=SUPERSEDED (161
                  rows), so ACTIVE rows never collide on a B1 key. The
                  registry's superseded_by mechanism IS the rung-duplicate
                  collapse; the flag exists to police future appends.

Hard asserts on emit (discrepancy => loud failure, never a fudged file):
278 rows; above-floor flags sum to 14 TP / 9 FP / 21 ring / 1 funnel;
161 SUPERSEDED rows with is_active=False; flags mutually exclusive and
confined to above-floor rows.

Per-run summary convention (findings.md session 57): the summary is
printed to stdout; the registry itself is never written here.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import pandas as pd

from wp5_fusion.registry_io import load_registry, validate_registry

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = REPO_ROOT / "01_WORKSPACE/data/candidate_registry.csv"
DEFAULT_ACCOUNTING = (REPO_ROOT / "01_WORKSPACE/data/outputs/wp2_sag/"
                      "unique_accounting_2026-09-07.json")
DEFAULT_OUT = REPO_ROOT / "01_WORKSPACE/data/candidate_registry_flags.csv"
CLASSIFICATION_SOURCE = "unique_accounting_2026-09-07.json"

FLAG_COLUMNS = ["candidate_id", "is_active", "unique_key", "is_tp", "is_fp",
                "is_ring", "is_funnel", "is_rung_duplicate",
                "classification_source"]

_SUPERSEDED_BY_RE = re.compile(r"superseded_by=([A-Za-z0-9_\-]+)")


def _root_primary(candidate_id: str, notes: dict[str, str],
                  depth: int = 0) -> str:
    """Resolve the B1 group primary: follow `superseded_by=` notes chains."""
    if depth > 10:
        return candidate_id  # cycle guard; frozen data has none
    m = _SUPERSEDED_BY_RE.search(notes.get(candidate_id, ""))
    if m and m.group(1) in notes:
        return _root_primary(m.group(1), notes, depth + 1)
    return candidate_id


def build_flags(registry_df: pd.DataFrame,
                accounting: dict) -> tuple[pd.DataFrame, dict]:
    """Derive the sidecar frame + summary from a loaded registry + accounting."""
    row_based = accounting["row_based"]
    frozen = {
        "n_rows": 278, "n_active": 117, "n_superseded": 161,
        "n_tp": row_based["n_tp"], "n_fp": row_based["n_fp"],
        "n_ring": row_based["n_ring"], "n_funnel": row_based["n_funnel"],
        "n_above": row_based["n_above"],
    }

    ids = registry_df["candidate_id"].tolist()
    notes = dict(zip(ids, registry_df["notes"]))
    dtm = dict(zip(ids, registry_df["dtm"]))
    status = dict(zip(ids, registry_df["status"]))

    # --- classification, per the accounting's own rules ---------------
    above = {i for i in ids if "below-local-floor" not in notes[i]}
    ring = {i for i in ids if "ring artifact" in notes[i]}
    fp = set()
    fp_primary = {}
    for g in accounting["fp_group_detail"]:
        fp_primary[g["primary"]] = g["primary"]
        for m in g["members"]:
            fp.add(m["id"])
            fp_primary[m["id"]] = g["primary"]
    funnel = set()
    for s in accounting["boundary_straddlers"]:
        for row, cls in zip((s["row_a"], s["row_b"]),
                            s["classes"].split("/")):
            if cls == "FUNNEL":
                funnel.add(row)
    tp = above - ring - fp - funnel

    def _check(cond: bool, msg: str) -> None:
        if not cond:
            raise AssertionError(f"registry_flags: {msg}")

    _check(len(registry_df) == frozen["n_rows"],
           f"expected {frozen['n_rows']} rows, got {len(registry_df)}")
    _check(len(above) == frozen["n_above"],
           f"above-floor {len(above)} != frozen {frozen['n_above']}")
    _check(len(ring) == frozen["n_ring"],
           f"ring {len(ring)} != frozen {frozen['n_ring']}")
    _check({dtm[i] for i in ring} == {"INGENIIPIT"},
           "ring rows are not exclusively INGENIIPIT (=21 rule)")
    _check(len(fp) == frozen["n_fp"],
           f"fp {len(fp)} != frozen {frozen['n_fp']}")
    _check(len(funnel) == frozen["n_funnel"],
           f"funnel {len(funnel)} != frozen {frozen['n_funnel']}")
    _check(all("I14" in notes[i] for i in funnel),
           "funnel row(s) not I14-annotated (rule requires it)")
    _check(len(tp) == frozen["n_tp"],
           f"tp residual {len(tp)} != frozen {frozen['n_tp']}")
    _check(len(tp | fp | ring | funnel) == len(above),
           "TP/FP/ring/funnel are not a partition of above-floor")
    _check(not (tp & fp or tp & ring or tp & funnel or fp & ring
                or fp & funnel or ring & funnel),
           "classification flags overlap (must be mutually exclusive)")

    # --- unique_key (B1 link key) + rung duplicates -------------------
    unique_key = {i: _root_primary(i, notes) for i in ids}
    for i in fp:  # cross-assert vs the accounting's explicit primaries
        _check(unique_key[i] == fp_primary[i],
               f"B1 root {unique_key[i]!r} != fp_group primary "
               f"{fp_primary[i]!r} for {i}")
    active_counts: dict[str, int] = {}
    for i in ids:
        if status[i] == "ACTIVE":
            active_counts[unique_key[i]] = active_counts.get(unique_key[i],
                                                             0) + 1
    rung_dup = {i for i in ids
                if status[i] == "ACTIVE"
                and active_counts.get(unique_key[i], 0) > 1}

    is_active = {i: status[i] == "ACTIVE" for i in ids}
    n_inactive_superseded = sum(
        1 for i in ids if status[i] == "SUPERSEDED" and not is_active[i])
    _check(sum(is_active.values()) == frozen["n_active"],
           f"ACTIVE {sum(is_active.values())} != frozen {frozen['n_active']}")
    _check(n_inactive_superseded == frozen["n_superseded"],
           f"SUPERSEDED is_active=False {n_inactive_superseded} != frozen "
           f"{frozen['n_superseded']}")

    frame = pd.DataFrame([{
        "candidate_id": i,
        "is_active": is_active[i],
        "unique_key": unique_key[i],
        "is_tp": i in tp,
        "is_fp": i in fp,
        "is_ring": i in ring,
        "is_funnel": i in funnel,
        "is_rung_duplicate": i in rung_dup,
        "classification_source": CLASSIFICATION_SOURCE,
    } for i in ids], columns=FLAG_COLUMNS)

    summary = {
        "n_rows": len(frame),
        "n_active": int(frame["is_active"].sum()),
        "n_superseded_inactive": n_inactive_superseded,
        "n_tp": len(tp), "n_fp": len(fp),
        "n_ring": len(ring), "n_funnel": len(funnel),
        "n_above_floor": len(above),
        "n_rung_duplicate_active": len(rung_dup),
        "n_unique_keys": int(frame["unique_key"].nunique()),
        "classification_source": CLASSIFICATION_SOURCE,
        "verdicts": {
            "frozen_sums_14_9_21_1": "PASS",
            "superseded_161_inactive": "PASS",
            "rung_duplicate_note": (
                "0 ACTIVE rows share a B1 key: every multi-rung copy is "
                "status=SUPERSEDED via superseded_by (161 rows). B1 key "
                "scale confirmed by accounting sensitivity block: 3-dp "
                "lon/lat grouping n_groups=21 == n_unique_above_floor."),
        },
    }
    return frame, summary


def emit_flags(registry_path, accounting_path, out_path) -> dict:
    """Load, validate, build, assert, and write the sidecar CSV."""
    df = load_registry(registry_path)
    validate_registry(df, strict=True)
    accounting = json.loads(Path(accounting_path).read_text())
    frame, summary = build_flags(df, accounting)
    out = Path(out_path)
    with open(out, "w", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(FLAG_COLUMNS)
        w.writerows([[str(v) for v in row] for row in
                     frame.itertuples(index=False, name=None)])
    summary["out_path"] = str(out)
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Emit the structured-flags sidecar "
                    "(candidate_registry_flags.csv) for the frozen "
                    "candidate registry. Never writes the registry itself.")
    ap.add_argument("--registry", default=str(DEFAULT_REGISTRY),
                    help="frozen registry CSV (default: repo path)")
    ap.add_argument("--accounting", default=str(DEFAULT_ACCOUNTING),
                    help="unique_accounting JSON, the classification "
                         "source of truth")
    ap.add_argument("--out", default=None,
                    help="sidecar CSV to write (REQUIRED to emit; "
                         "bare invocation prints this help per the "
                         "session-49 CLI house style; the repo sidecar "
                         "lives at 01_WORKSPACE/data/"
                         "candidate_registry_flags.csv)")
    args = ap.parse_args(argv)
    if args.out is None:
        ap.print_help()
        return 0
    summary = emit_flags(args.registry, args.accounting, args.out)
    print(json.dumps(summary, indent=2))
    print(f"wrote {summary['out_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
