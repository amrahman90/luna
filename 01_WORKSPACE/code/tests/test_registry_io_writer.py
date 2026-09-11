"""B1–B5 tail (plan v2, session 57) — registry writer + validator pins.

Guards:
  - write_registry reproduces the FROZEN registry byte-identically from
    its own parse (load -> write(tmp) -> md5 == frozen md5 AND bytes
    equal AND frames equal) — the round-trip proof that any future
    registry repair can be made byte-accountable;
  - validate_registry summary counts match the frozen corpus
    (278 rows / 117 ACTIVE / 161 SUPERSEDED);
  - each schema mutation (drop col / rename col / duplicate ACTIVE id /
    bad tier / bad status / null evidence) raises RegistrySchemaError;
  - write_registry refuses to invent a comment header.
"""
from __future__ import annotations

import hashlib

import pandas as pd
import pytest

from conftest import REPO_ROOT
from wp5_fusion.registry_io import (
    FROZEN_REGISTRY_MD5, RegistrySchemaError, SCHEMA_COLUMNS,
    load_registry, validate_registry, write_registry,
)

FROZEN = REPO_ROOT / "01_WORKSPACE/data/candidate_registry.csv"


@pytest.fixture(scope="module")
def registry_df() -> pd.DataFrame:
    return load_registry(FROZEN)


# --- round-trip proof --------------------------------------------------------

def test_write_registry_roundtrips_frozen_bytes(registry_df, tmp_path):
    tmp = tmp_path / "repro.csv"
    write_registry(registry_df, tmp)
    got = tmp.read_bytes()
    assert hashlib.md5(got).hexdigest() == FROZEN_REGISTRY_MD5
    assert got == FROZEN.read_bytes()          # byte-identity, not just hash


def test_write_registry_roundtrips_frame(registry_df, tmp_path):
    tmp = tmp_path / "repro.csv"
    write_registry(registry_df, tmp)
    reloaded = load_registry(tmp)
    assert reloaded.equals(registry_df)


def test_frozen_registry_md5_unchanged():
    """The frozen corpus itself must never drift (sha-frozen file)."""
    assert hashlib.md5(FROZEN.read_bytes()).hexdigest() == FROZEN_REGISTRY_MD5


# --- validator summary + mutation injections ---------------------------------

def test_validate_summary_matches_frozen_counts(registry_df):
    s = validate_registry(registry_df, strict=True)
    assert s["n_rows"] == 278
    assert s["n_active"] == 117
    assert s["n_superseded"] == 161
    assert s["n_active"] + s["n_superseded"] == s["n_rows"]
    assert s["n_ring_artifact_rows"] == 21


def _keep_attrs(df: pd.DataFrame, mutated: pd.DataFrame) -> pd.DataFrame:
    """Re-stash the raw parse after a mutation (pandas ops may drop attrs)."""
    mutated.attrs.update(df.attrs)
    return mutated


def test_mutation_drop_column_raises(registry_df):
    d = registry_df.drop(columns=["tier"])
    with pytest.raises(RegistrySchemaError, match="column schema mismatch"):
        validate_registry(_keep_attrs(registry_df, d))


def test_mutation_rename_column_raises(registry_df):
    d = registry_df.rename(columns={"span_m": "width_m"})
    with pytest.raises(RegistrySchemaError, match="column schema mismatch"):
        validate_registry(_keep_attrs(registry_df, d))


def test_mutation_extra_column_raises(registry_df):
    d = registry_df.assign(extra="x")
    with pytest.raises(RegistrySchemaError, match="column schema mismatch"):
        validate_registry(_keep_attrs(registry_df, d))


def test_mutation_duplicate_active_id_raises(registry_df):
    d = registry_df.copy()
    first_active = d.index[d["status"] == "ACTIVE"][0]
    last = d.index[-1]
    assert d.loc[last, "status"] == "SUPERSEDED" or True  # id dup is the point
    d.loc[last, "candidate_id"] = d.loc[first_active, "candidate_id"]
    d.loc[last, "status"] = "ACTIVE"
    with pytest.raises(RegistrySchemaError, match="duplicate candidate_id"):
        validate_registry(_keep_attrs(registry_df, d))


def test_mutation_bad_tier_raises(registry_df):
    d = registry_df.copy()
    d.loc[d.index[0], "tier"] = "X"
    with pytest.raises(RegistrySchemaError, match="tier outside"):
        validate_registry(_keep_attrs(registry_df, d))


def test_mutation_bad_status_raises(registry_df):
    d = registry_df.copy()
    d.loc[d.index[0], "status"] = "DOWNGRADED"
    with pytest.raises(RegistrySchemaError, match="status outside"):
        validate_registry(_keep_attrs(registry_df, d))


def test_mutation_null_evidence_raises(registry_df):
    d = registry_df.copy()
    d.loc[d.index[0], "evidence"] = None
    with pytest.raises(RegistrySchemaError, match="null/empty evidence"):
        validate_registry(_keep_attrs(registry_df, d))


def test_mutation_raw_short_row_raises_in_strict_mode(registry_df):
    """A raw record with != 15 fields must fail strict validation."""
    d = registry_df.copy()
    d.attrs["_raw_records"] = d.attrs["_raw_records"] + [["LV-X-0100cm-r001",
                                                          "1.0", "2.0"]]
    with pytest.raises(RegistrySchemaError, match="!= 15 fields"):
        validate_registry(d, strict=True)
    # strict=False skips the raw-record check (documented escape hatch)
    validate_registry(d, strict=False)


# --- writer guard rails -------------------------------------------------------

def test_write_registry_requires_comment_header(registry_df, tmp_path):
    d = registry_df.copy()
    d.attrs.clear()  # simulate a frame built without a raw parse
    with pytest.raises(ValueError, match="comment_header"):
        write_registry(d, tmp_path / "nope.csv")


def test_write_registry_repair_path_serializes_current_values(
        registry_df, tmp_path):
    """Attrs-order mismatch (edited/re-sorted frame) falls back to the
    str()-serialization path; output stays schema-valid and reloadable."""
    d = registry_df.copy()
    d.attrs["_raw_records"] = []  # force the fallback branch
    tmp = tmp_path / "repair.csv"
    write_registry(d, tmp, comment_header=registry_df.attrs["_raw_comment_header"])
    reloaded = load_registry(tmp)
    # Same coercion path on both sides -> frames equal (values + dtypes);
    # the repair path is value-preserving, only byte-literal formatting
    # (e.g. "0.0050") may differ from the frozen file.
    assert reloaded.equals(d)
    s = validate_registry(reloaded, strict=False)
    assert s["n_rows"] == 278
