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
  - SCHEMA_COLUMNS                 : the frozen 15-column schema (registry
                                      header line 31)
  - RegistrySchemaError            : raised by validate_registry
  - validate_registry(df)          : schema + invariant checks; returns a
                                      summary dict (B1–B5 cluster tail,
                                      plan v2, session 57)
  - write_registry(df, path)       : quoted-CSV writer that reproduces the
                                      frozen registry byte-identically from
                                      its own parse (round-trip proof)

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

# ---------------------------------------------------------------------------
# Frozen-corpus constants (B1–B5 cluster tail, plan v2, session 57).
#
# The registry CSV `01_WORKSPACE/data/candidate_registry.csv` is sha-frozen
# (md5 below; cited in both papers, pinned in PROVENANCE_INDEX, shipped in
# the Zenodo deposit). It is NEVER rewritten in place; any writer must be
# able to REPRODUCE it byte-identically from its own parse (round-trip
# proof, writing to a temp path only).
#
# File layout: 30 comment-header lines (starting `#`, one of them the
# quoted `"# notes ..."` line), header line 31 = SCHEMA_COLUMNS, then 278
# data rows + 1 `# provenance:` comment artifact mid-file (audit LOW-11).
# ---------------------------------------------------------------------------
SCHEMA_COLUMNS: tuple[str, ...] = (
    "candidate_id", "lon", "lat", "dtm", "span_m", "sag_amp_m", "score",
    "confusion", "methods", "tier", "status", "first_found", "updated",
    "evidence", "notes",
)
FROZEN_REGISTRY_MD5 = "a60fb52152e33f37e9052434ad026a6e"
VALID_TIERS = frozenset({"A", "B", "C", "D"})
VALID_STATUSES = frozenset({"ACTIVE", "SUPERSEDED"})


class RegistrySchemaError(ValueError):
    """Registry schema/invariant violation detected by validate_registry."""


def _split_registry_file(path) -> tuple[list[str], str, list[list[str]]]:
    """Split a registry file into (comment_header_lines, csv_text, records).

    comment_header_lines: every line BEFORE the `candidate_id,` header,
    verbatim (keepends). csv_text: the header line + everything after.
    records: csv.reader records over csv_text (header record included;
    mid-file `#` comment records preserved in file order).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Registry CSV not found: {path}")
    with open(path) as f:
        lines = f.readlines()
    try:
        header_idx = next(i for i, ln in enumerate(lines)
                          if ln.startswith("candidate_id,"))
    except StopIteration:
        raise ValueError(f"No 'candidate_id,' header found in {path}") from None
    comment_header = lines[:header_idx]
    csv_text = "".join(lines[header_idx:])
    records = list(csv.reader(io.StringIO(csv_text)))
    return comment_header, csv_text, records


def load_registry(path) -> pd.DataFrame:
    """Load the candidate registry CSV with comment-header + CSV-quoting tolerance.

    The registry file has ~30 lines of `#`-prefixed header comments
    followed by a 15-column CSV. The `notes` field may contain quoted
    commas which breaks `pd.read_csv(comment=...)`. We parse via the
    csv module instead.

    Byte-fidelity side effect (session 57): the raw parse is stashed on
    the returned frame in ``df.attrs`` —

      - ``_raw_comment_header``: the comment-header lines, verbatim;
      - ``_csv_header_record``:  the parsed CSV header record;
      - ``_raw_records``:        post-header records in file order,
                                 including mid-file ``#`` comment
                                 records (needed for byte-identical
                                 re-emission by write_registry);
      - ``_registry_source``:    resolved source path string.

    These attrs are transparent to every existing consumer (pandas
    ignores attrs in .equals()/comparisons) and are what allows
    write_registry to round-trip the frozen file byte-identically —
    the numeric coercion below is lossy for strings like ``0.0050``.
    """
    comment_header, csv_text, records = _split_registry_file(path)
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
    # Raw-parse stash for byte-identical round-trips (see docstring).
    df.attrs["_raw_comment_header"] = comment_header
    df.attrs["_csv_header_record"] = records[0] if records else list(SCHEMA_COLUMNS)
    df.attrs["_raw_records"] = records[1:]
    df.attrs["_registry_source"] = str(Path(path).resolve())
    return df


def validate_registry(df: pd.DataFrame, *, strict: bool = True) -> dict:
    """Validate registry schema + invariants; return a summary dict.

    Raises RegistrySchemaError on:
      - wrong column names/order/count (must equal SCHEMA_COLUMNS);
      - any data row with != 15 fields after parse (strict=True, checked
        against the stashed raw parse when available);
      - duplicate candidate_id among status==ACTIVE rows;
      - tier outside {A,B,C,D};
      - status outside {ACTIVE,SUPERSEDED};
      - null/empty evidence on a data row.

    strict=False skips the raw-record field-count check (e.g. for frames
    built synthetically without attrs); all other checks always run.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise RegistrySchemaError("registry frame is empty or not a DataFrame")

    # 1. Column names/order/count (header line 31 of the frozen file).
    cols = list(df.columns)
    if cols != list(SCHEMA_COLUMNS):
        raise RegistrySchemaError(
            f"column schema mismatch: expected {len(SCHEMA_COLUMNS)} columns "
            f"{list(SCHEMA_COLUMNS)}, got {len(cols)} {cols}"
        )

    # 2. Raw field counts (only meaningful with the stashed raw parse).
    if strict:
        recs = df.attrs.get("_raw_records")
        if recs is not None:
            bad = [r for r in recs
                   if r and r[0] and not str(r[0]).startswith("#")
                   and len(r) != len(SCHEMA_COLUMNS)]
            if bad:
                raise RegistrySchemaError(
                    f"{len(bad)} data row(s) with != {len(SCHEMA_COLUMNS)} "
                    f"fields after parse; first offender starts "
                    f"{bad[0][:3]}"
                )

    # 3. Duplicate candidate_id among ACTIVE rows.
    active_ids = df.loc[df["status"] == "ACTIVE", "candidate_id"]
    dup = sorted(active_ids[active_ids.duplicated(keep=False)].unique())
    if dup:
        raise RegistrySchemaError(
            f"duplicate candidate_id among ACTIVE rows: {dup[:5]}"
            f"{' ...' if len(dup) > 5 else ''}"
        )

    # 4. Tier domain.
    bad_tier = sorted({t for t in df["tier"]} - set(VALID_TIERS))
    if bad_tier:
        raise RegistrySchemaError(f"tier outside {sorted(VALID_TIERS)}: {bad_tier}")

    # 5. Status domain.
    bad_status = sorted({s for s in df["status"]} - set(VALID_STATUSES))
    if bad_status:
        raise RegistrySchemaError(
            f"status outside {sorted(VALID_STATUSES)}: {bad_status}"
        )

    # 6. Null/empty evidence on a data row.
    ev = df["evidence"]
    null_ev = df.loc[ev.isna() | (ev.astype(str).str.strip() == "")
                     | (ev.astype(str) == "None"), "candidate_id"].tolist()
    if null_ev:
        raise RegistrySchemaError(
            f"null/empty evidence on {len(null_ev)} data row(s): "
            f"{null_ev[:5]}{' ...' if len(null_ev) > 5 else ''}"
        )

    tier_counts = {t: int((df["tier"] == t).sum()) for t in sorted(VALID_TIERS)}
    return {
        "n_rows": int(len(df)),
        "n_active": int((df["status"] == "ACTIVE").sum()),
        "n_superseded": int((df["status"] == "SUPERSEDED").sum()),
        "n_tier_A": tier_counts["A"],
        "n_tier_B": tier_counts["B"],
        "n_tier_C": tier_counts["C"],
        "n_tier_D": tier_counts["D"],
        "n_dtms": int(df["dtm"].nunique()),
        "n_ring_artifact_rows": int(df["notes"].str.contains(
            "ring artifact", regex=False).sum()),
    }


def write_registry(df: pd.DataFrame, path, *, comment_header=None) -> Path:
    """Write a registry CSV with csv.writer QUOTE_MINIMAL.

    Byte-fidelity contract (session 57): when `df` carries the raw-parse
    attrs stashed by load_registry AND its candidate_id order matches the
    stashed records, the raw records are re-emitted verbatim — including
    the mid-file `# provenance:` comment artifact — which reproduces the
    frozen registry byte-identically (md5 a60fb521…; proven by
    test_registry_io_writer.py). This path is required because the
    numeric coercion in load_registry is lossy for literals like
    "0.0050".

    Otherwise (attrs missing or row order diverged — the repair path for
    genuinely edited frames) the CURRENT df values are serialized with
    str(); that output is schema-valid but NOT byte-guaranteed against
    the frozen file.

    `comment_header` (list of verbatim lines, keepends) overrides the
    stashed header; if neither is available, raise — the writer never
    invents a comment header.
    """
    if comment_header is None:
        comment_header = df.attrs.get("_raw_comment_header")
    if not comment_header:
        raise ValueError(
            "write_registry: no comment_header available. Pass the 30-line "
            "header explicitly or load the source registry with "
            "load_registry() so the raw header is stashed in df.attrs."
        )

    recs = df.attrs.get("_raw_records")
    header_rec = df.attrs.get("_csv_header_record") or list(SCHEMA_COLUMNS)
    use_raw = False
    if recs is not None:
        raw_ids = [r[0] for r in recs
                   if r and r[0] and not str(r[0]).startswith("#")]
        if raw_ids == [str(x) for x in df["candidate_id"].tolist()]:
            use_raw = True

    with open(path, "w", newline="") as f:
        f.write("".join(comment_header))
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(header_rec)
        if use_raw:
            w.writerows(recs)
        else:
            # Repair path: serialize current values. NOT byte-guaranteed
            # (float str() drops trailing zeros, e.g. 0.0050 -> "0.005").
            w.writerows([[str(v) for v in row] for row in
                         df[list(SCHEMA_COLUMNS)].itertuples(index=False,
                                                             name=None)])
    return Path(path)


def parse_confusion(confusion_str: str, kind: str) -> float:
    """Extract `kind=distance_m` from a confusion field. 1e6 if missing."""
    if not isinstance(confusion_str, str):
        return 1e6
    for m in _CONFIDENCE_RE.finditer(confusion_str):
        if m.group(1) == kind:
            try:
                return float(m.group(2))
            except ValueError:
                return 1e6  # silent by design: regex guarantees digits — defensive only
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
    "SCHEMA_COLUMNS", "FROZEN_REGISTRY_MD5", "VALID_TIERS", "VALID_STATUSES",
    "RegistrySchemaError", "validate_registry", "write_registry",
]
