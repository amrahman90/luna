"""B1–B5 tail (plan v2, session 57) — structured-flags sidecar pins.

Guards (against the frozen corpus + frozen accounting):
  - emitted sidecar row count == registry row count == 278;
  - above-floor classification sums == frozen 14 TP / 9 FP / 21 ring /
    1 funnel; SUPERSEDED is_active=False count == 161; ACTIVE == 117;
  - sidecar candidate_ids are a subset of (here: equal to) registry ids,
    same order;
  - flags are mutually exclusive and confined to above-floor rows;
  - deterministic emission: tmp emit == the shipped sidecar, byte-wise;
  - classification_source constant.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from conftest import CODE_DIR, REPO_ROOT
from wp5_fusion.registry_flags import (
    CLASSIFICATION_SOURCE, DEFAULT_ACCOUNTING, DEFAULT_OUT, DEFAULT_REGISTRY,
    emit_flags,
)
from wp5_fusion.registry_io import load_registry


@pytest.fixture(scope="module")
def registry_ids() -> list[str]:
    return load_registry(DEFAULT_REGISTRY)["candidate_id"].tolist()


@pytest.fixture(scope="module")
def emitted_path(tmp_path_factory) -> Path:
    """Emit once to tmp (never touches the repo sidecar)."""
    out = tmp_path_factory.mktemp("flags") / "flags.csv"
    emit_flags(DEFAULT_REGISTRY, DEFAULT_ACCOUNTING, out)
    return out


def _read(path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"candidate_id": str, "unique_key": str})


def test_emit_summary_matches_frozen_accounting(emitted_path):
    df = _read(emitted_path)
    acc = json.loads(DEFAULT_ACCOUNTING.read_text())
    rb = acc["row_based"]
    assert len(df) == 278
    assert (int(df["is_tp"].sum()), int(df["is_fp"].sum()),
            int(df["is_ring"].sum()), int(df["is_funnel"].sum())) \
        == (rb["n_tp"], rb["n_fp"], rb["n_ring"], rb["n_funnel"]) \
        == (14, 9, 21, 1)
    assert int(df["is_active"].sum()) == 117
    assert int((~df["is_active"]).sum()) == 161


def test_sidecar_ids_subset_of_registry(registry_ids, emitted_path):
    df = _read(emitted_path)
    assert set(df["candidate_id"]) <= set(registry_ids)
    assert df["candidate_id"].tolist() == registry_ids  # same row order
    assert len(df) == len(registry_ids) == 278


def test_flags_mutually_exclusive_and_above_floor_only(emitted_path):
    df = _read(emitted_path)
    n_flagged = df[["is_tp", "is_fp", "is_ring", "is_funnel"]].sum(axis=1)
    assert set(n_flagged.unique()) <= {0, 1}          # mutually exclusive
    assert int((n_flagged == 1).sum()) == 45          # above-floor rows only
    assert int((n_flagged == 0).sum()) == 278 - 45    # below-floor rows
    assert (df["classification_source"] == CLASSIFICATION_SOURCE).all()


def test_rung_duplicate_flag_is_structurally_zero_on_frozen_registry(
        emitted_path):
    """0 ACTIVE rows share a B1 key: all 161 multi-rung copies are
    SUPERSEDED via superseded_by (sensitivity block: 3-dp grouping
    n_groups=21 == n_unique_above_floor)."""
    df = _read(emitted_path)
    assert int(df["is_rung_duplicate"].sum()) == 0
    # unique_key collapses superseded chains: 117 keys == 117 ACTIVE rows
    active_keys = df.loc[df["is_active"], "unique_key"]
    assert active_keys.nunique() == 117


def test_emission_is_deterministic_vs_shipped_sidecar(emitted_path):
    assert DEFAULT_OUT.exists(), "shipped sidecar must exist in the repo"
    assert emitted_path.read_bytes() == DEFAULT_OUT.read_bytes()


def test_cli_help_is_clean():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(CODE_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    r = subprocess.run(
        [sys.executable, str(CODE_DIR / "wp5_fusion" / "registry_flags.py"),
         "--help"],
        capture_output=True, text=True, env=env, timeout=120,
        cwd=str(REPO_ROOT))
    assert r.returncode == 0, r.stderr[-300:]
    for flag in ("--registry", "--accounting", "--out"):
        assert flag in r.stdout
    assert "usage:" in r.stdout
