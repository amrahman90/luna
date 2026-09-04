"""Shared registry_io for PU-learning (C13 — Next-Level Plan v2).

Extracted from `wp5_fusion/pu_learning_baseline.py`,
`wp5_fusion/pu_learning_on_registry.py`, and
`wp5_fusion/pu_learning_extended.py`. The three scripts all imported
near-byte-equivalent copies of `load_registry()` and
`parse_confusion()` (Hermes audit MED-15).

This module exposes:
  - load_registry(path)            : returns a DataFrame with numeric
                                     coercion + comment-header tolerance
  - parse_confusion(s, kind)       : distance value from a confusion field
  - count_confusion_keys(s)        : number of rille/chain/... keys
  - parse_rung_cm(candidate_id)    : rung from candidate_id (rung in cm)
  - LEAK_FEATURES (set)            : features that MUST NOT enter the
                                     classifier (positive-class identity
                                     or trivially-correlated with it)
  - assert_no_leak(features)       : the 30-min guard. Raises if any
                                     LEAK_FEATURES is in the feature list.

The full ADJ-4 redesign (group-split by DTM, bootstrap CIs,
agreement-with-proxy framing) is deferred to D1.
"""
from __future__ import annotations

import csv
import io
import re
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Features that MUST NOT enter the classifier. Adding any of these would
# silently inflate F1 by either encoding the positive-class identity
# directly or being trivially correlated with it.
# ---------------------------------------------------------------------------
LEAK_FEATURES: frozenset[str] = frozenset({
    "dtm",                # positive def includes "dtm in CATALOGUED_PIT_DTMS"
    "lon", "lat",         # identify the DTM
    "has_ring_artifact",  # in positive def: notes contain "ring artifact"
    "has_below_local_floor",  # every positive is above_floor by construction
    "is_rank1",           # candidate_id suffix -r001 is in positive def
    "rank_n",             # rank is in positive def
})


def assert_no_leak(feature_names) -> None:
    """Raise ValueError if any LEAK_FEATURES is in `feature_names`.

    Called from build_extended_features() (and analogous builders in
    pu_learning_baseline.py) BEFORE the classifier is fit. Cheap;
    catches the "I added a feature without realising it leaks"
    refactor regression.
    """
    bad = LEAK_FEATURES & set(feature_names)
    if bad:
        raise ValueError(
            f"LEAK_FEATURES detected in feature list: {sorted(bad)}. "
            f"This would silently inflate PU-learning metrics; remove "
            f"the feature (or remove it from LEAK_FEATURES if you have "
            f"a documented reason to include it)."
        )


# ---------------------------------------------------------------------------
# Registry I/O — the byte-equivalent loader shared by all three scripts.
# ---------------------------------------------------------------------------
_CONFIDENCE_RE = re.compile(r"(rille|chain|ridge|graben|bg)=(\d+(?:\.\d+)?)m")
_RUNG_RE = re.compile(r"-(\d{3,4})cm-")


def load_registry(path) -> pd.DataFrame:
    """Load the candidate registry CSV with comment-header + CSV-quoting tolerance.

    The registry file has ~30 lines of `#`-prefixed header comments
    followed by a 15-column CSV. The `notes` field may contain quoted
    commas which breaks `pd.read_csv(comment=...)`. We parse via the
    csv module instead.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Registry CSV not found: {path}")
    with open(path) as f:
        lines = f.readlines()
    try:
        header_idx = next(i for i, ln in enumerate(lines) if ln.startswith("candidate_id,"))
    except StopIteration:
        raise ValueError(f"No 'candidate_id,' header found in {path}") from None
    csv_text = "".join(lines[header_idx:])
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = [r for r in reader
            if r.get("candidate_id") and not str(r["candidate_id"]).startswith("#")]
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"0 data rows loaded from {path}")
    for col in ("lon", "lat", "span_m", "sag_amp_m", "score"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["dtm"] = df["dtm"].astype(str)
    df["candidate_id"] = df["candidate_id"].astype(str)
    df["methods"] = df["methods"].astype(str)
    df["tier"] = df["tier"].astype(str)
    df["notes"] = df["notes"].fillna("").astype(str)
    df["confusion"] = df["confusion"].astype(str)
    return df


def parse_confusion(confusion_str: str, kind: str) -> float:
    """Extract `kind=distance_m` from a confusion field. 1e6 if missing."""
    if not isinstance(confusion_str, str):
        return 1e6
    for m in _CONFIDENCE_RE.finditer(confusion_str):
        if m.group(1) == kind:
            try:
                return float(m.group(2))
            except ValueError:
                return 1e6
    return 1e6


def count_confusion_keys(confusion_str: str) -> int:
    """How many rille/chain/ridge/graben/bg distances are present?"""
    if not isinstance(confusion_str, str):
        return 0
    return sum(1 for _ in _CONFIDENCE_RE.finditer(confusion_str))


def parse_rung_cm(candidate_id: str) -> float:
    """Parse the rung (in cm) from a candidate_id like 'LV-TRANQPIT1-200cm-r001'."""
    m = _RUNG_RE.search(candidate_id)
    return int(m.group(1)) if m else float("nan")


__all__ = [
    "LEAK_FEATURES", "assert_no_leak",
    "load_registry", "parse_confusion", "count_confusion_keys", "parse_rung_cm",
]
