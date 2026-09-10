#!/usr/bin/env python
"""build_provenance_index.py — B4 output provenance sidecar generator.

Walks 01_WORKSPACE/data/outputs/ and emits data/outputs/PROVENANCE_INDEX.md,
one row per current/canonical output artifact, with sha256, best-known
producing script, key inputs, date, cited-in and status.

Determinism
-----------
* File set: fixed walk of the outputs tree (see EXCLUDE rules below).
* Ordering: lexicographic by path (POSIX, relative to 01_WORKSPACE/).
* sha256: computed fresh each run.
* Date: `git log -1 --format=%as -- <path>` for git-tracked files
  (last-commit author date; stable across regenerations on the same
  commit), else filesystem mtime (YYYY-MM-DD) for gitignored rasters.
* Producer / inputs / cited-in / status: fixed mapping tables below.

Exclusions (noted in the generated header)
------------------------------------------
* audit/            — internal audit working notes, not project outputs.
* *.md              — hand-authored METHODS/NOTES documentation inside
                      outputs/ (4 files); provenance does not apply.
* PROVENANCE_INDEX.md itself.

No superseded/backup *copies* exist under data/outputs/ (the pre-B1
registry backup lives at data/candidate_registry_backup_2026-09-06.csv,
outside this tree; supersession is expressed as a status below instead).

Run (venv Python):
    ~/lunarvoid/venv/bin/python 01_WORKSPACE/code/tools/build_provenance_index.py
"""

from __future__ import annotations

import hashlib
import subprocess
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # .../Lunar_LavaTube
WS = REPO / "01_WORKSPACE"
OUT_ROOT = WS / "data" / "outputs"
INDEX_PATH = OUT_ROOT / "PROVENANCE_INDEX.md"

# ---------------------------------------------------------------------------
# Attribution rules. Each: (predicate on workspace-relative posix path,
# producer, key inputs, cited-in, status). First match wins.
# Cited-in restricted to papers/ (incl. gate reports), notes/findings.md,
# admin/CHANGELOG.md per B4 spec; "—" = none.
# ---------------------------------------------------------------------------
REG_MD5 = "a60fb521"  # post-B1 candidate_registry.csv md5 (prefix)
RULES: list[tuple] = []


def rule(pattern: str, producer: str, inputs: str, cited: str, status: str):
    RULES.append((pattern, producer, inputs, cited, status))


# --- wp0_primitive ----------------------------------------------------------
rule("data/outputs/wp0_primitive/", "code/wp0_primitive/sweep_pits.py",
     "8 covered-pit NAC DTMs + LROC pit atlas (depression_depth.py primitive)",
     "findings.md; G0' v1.1 report; Paper 1 figs README", "canonical")

# --- wp0_kriging ------------------------------------------------------------
rule("data/outputs/wp0_kriging/TRANQPIT1_kriging", "code/wp0_kriging/kriging_correction.py",
     "TRANQPIT1 NAC DTM + LOLA RDR tracks (ODE REST)", "G0' v1.1 report; Paper 1 figs README", "canonical")
rule("data/outputs/wp0_kriging/TRANQPIT1_corrections", "code/wp0_kriging/kriging_correction.py",
     "TRANQPIT1 NAC DTM + LOLA RDR tracks (ODE REST)", "G0' v1.1 report; Paper 1 figs README", "canonical")
rule("data/outputs/wp0_kriging/MARIUSPIT01_kriging", "code/wp0_kriging/kriging_correction.py",
     "MARIUSPIT01 NAC DTM + LOLA RDR tracks (ODE REST)", "G0' v1.1 report; Paper 1 figs README", "canonical")
rule("data/outputs/wp0_kriging/MARIUSPIT01_corrections", "code/wp0_kriging/kriging_correction.py",
     "MARIUSPIT01 NAC DTM + LOLA RDR tracks (ODE REST)", "G0' v1.1 report; Paper 1 figs README", "canonical")
rule("data/outputs/wp0_kriging/noise_floor", "code/wp0_kriging/noise_floor.py",
     "TRANQPIT1 + MARIUSPIT01 DTMs (7+8 flat-mare panels)", "G0' v1.1 report; Paper 1 figs README", "canonical")
rule("data/outputs/wp0_kriging/per_dtm_floors_summary", "code/wp0_kriging/_build_n14_summary.py",
     "N=14->21 on-disk NAC DTMs (top of wp0_scope_map_v11/target_ranking.csv)",
     "G1 + G2 reports; findings.md", "canonical")
rule("data/outputs/wp0_kriging/per_dtm_floors", "code/wp0_kriging/per_dtm_floors.py",
     "N=14->21 on-disk NAC DTMs (top of wp0_scope_map_v11/target_ranking.csv)",
     "G1 report; findings.md", "canonical")

# --- wp0_scope_map (v1 = superseded by v11) ---------------------------------
rule("data/outputs/wp0_scope_map/", "code/wp0_scope_map/scope_map.py",
     "278-pit LROC atlas x data/lroc_dtm_availability.csv", "—", "superseded (by wp0_scope_map_v11)")

# --- wp0_scope_map_v11 (canonical scope map) --------------------------------
rule("data/outputs/wp0_scope_map_v11/", "code/wp0_scope_map/scope_map_v11.py",
     "NAC DTM index + Hurwitz 2013 rilles (Wayback) + LU5M812TGT craters (CC-BY-4.0)",
     "G0' v1.1 report; Paper 1 figs README", "canonical")

# --- wp1_analog -------------------------------------------------------------
rule("data/outputs/wp1_analog/registration/coarse_search.json", "code/wp1_analog/coarse_search.py",
     "Fieg Cave LiDAR cloud (LLTB-1 npz) + IndianTunnel_NorthSurface DTM",
     "findings.md; G1 report", "canonical")
rule("data/outputs/wp1_analog/registration/preflight_clouds.png", "code/wp1_analog/explore_indian_tunnel.py",
     "LLTB-1 analog LiDAR clouds", "—", "canonical")
rule("data/outputs/wp1_analog/registration/", "code/wp1_analog/register_cave.py",
     "coarse_search.json seed + Fieg cloud + NorthSurface DTM (ICP)",
     "findings.md; G1 report; Paper 1 figs README", "canonical")
rule("data/outputs/wp1_analog/void_mask/", "code/wp1_analog/make_void_mask.py",
     "registered cave cloud + IndianTunnel_NorthSurface DTM",
     "findings.md; G1 report; Paper 1 figs README", "canonical")

# --- wp1_detector -----------------------------------------------------------
rule("data/outputs/wp1_detector/v0_2_integration_test.json", "code/wp1_detector/v0_2_pipeline_integration.py",
     "LLTB-1 v0.2 pipeline + synthetic self-test",
     "—", "diagnostic (QA; MED-12 regeneration pending per audit plan v2 step 0.5)")

# --- wp1_ladder -------------------------------------------------------------
rule("data/outputs/wp1_ladder/hapke/", "code/wp1_ladder/hapke_render.py",
     "IndianTunnel_NorthSurface master DTM (Hapke IMSA re-render, i=45/65/85 az x4)",
     "G1 report; findings.md; Paper 1 figs README", "canonical")
rule("data/outputs/wp1_ladder/sensor/", "code/wp1_ladder/sensor_degrade.py",
     "LLTB-1 v0.5 detector + Hapke render arms", "G1 report; findings.md; Paper 1 figs README", "canonical")

# --- wp2_sag per-DTM sag searches ------------------------------------------
# Matches the 10 legacy per-DTM dirs (MTP, TRANQPIT1 etc.).
_SAG_CITED = {"sag_search_summary.json": "findings.md; G0' v1.1 + G1 reports"}

# --- wp2_sag confusion ------------------------------------------------------
rule("data/outputs/wp2_sag/confusion/", "code/wp2_sag/confusion_layer.py",
     "Hurwitz 2013 rilles + LU5M812TGT craters; DTM-specific",
     "G0' v1.1 report", "canonical")

# --- wp2_sag transfer -------------------------------------------------------
rule("data/outputs/wp2_sag/transfer/transfer_summary.json", "code/wp2_sag/transfer/transfer_apply.py",
     "candidate_registry.csv (md5 a60fb521...) + per_dtm_floors.csv + score rasters (21 DTMs); cycles merged via merge_cycle1.py",
     "Paper 1; Paper 2; findings.md; CHANGELOG; G1/G2 reports", "canonical")
rule("data/outputs/wp2_sag/transfer/calibration_transqpit1.json", "code/wp2_sag/transfer/calibrate_transqpit1.py",
     "TRANQPIT1 NAC DTM + LROC pit atlas (FROZEN I15 recipe)",
     "findings.md; G1 report; Paper 2; CHANGELOG", "canonical (frozen)")
rule("data/outputs/wp2_sag/transfer/diviner", "code/wp4_diviner/sample_diviner_at_candidates.py",
     "Powell 2023 GHRM Diviner (PDS) + 7-DTM candidate locations",
     "findings.md; G1 report", "canonical")

# --- wp2_sag top-level evidence --------------------------------------------
rule("data/outputs/wp2_sag/registry_repair_2026-09-06.json", "code/tools/repair_registry_v1.py",
     "candidate_registry.csv pre-repair (backup md5 d38d63fb...) -> repaired md5 a60fb521...",
     "CHANGELOG", "canonical")
rule("data/outputs/wp2_sag/unique_accounting_2026-09-07.json", "code/wp2_sag/transfer/unique_accounting.py",
     "registry md5 a60fb521... + relevant_pits_x_dtms.csv (md5 49dcf709...) + transfer_summary.json (md5 39c72f3c...)",
     "Paper 1; Paper 2; CHANGELOG", "canonical")

# --- wp3_fusion -------------------------------------------------------------
rule("data/outputs/wp3_fusion/MTP/diviner_placeholder.json", "code/wp3_fusion/evidence_layers.py",
     "Diviner metadata only (placeholder)", "—", "diagnostic (placeholder)")
rule("data/outputs/wp3_fusion/MTP/", "code/wp3_fusion/evidence_layers.py",
     "GRAIL GRGM1200A (l_max 680) + MTP window 30-35E/6-11N", "—", "canonical")

# --- wp5_fusion -------------------------------------------------------------
rule("data/outputs/wp5_fusion/pu_learning_registry_baseline.json", "code/wp5_fusion/pu_learning_on_registry.py",
     "candidate_registry.csv (278 rows, pre-B1, 5 features)",
     "CHANGELOG", "superseded (by baseline_v2)")
rule("data/outputs/wp5_fusion/pu_learning_registry_baseline_v2.json", "code/wp5_fusion/pu_learning_extended.py",
     "candidate_registry.csv (278 rows, pre-B1, 19 features, random 70/30 split)",
     "Paper 2; CHANGELOG", "superseded (leak-inflated; by groupsplit v5)")
rule("data/outputs/wp5_fusion/pu_learning_comparison.json", "code/wp5_fusion/pu_learning_extended.py",
     "v1 vs v2 PU baselines on registry (278 rows)", "—", "diagnostic")
rule("data/outputs/wp5_fusion/pu_learning_groupsplit_2026-09-09.json", "code/wp5_fusion/pu_learning_groupsplit.py",
     "registry md5 a60fb521... (117 ACTIVE; 161 SUPERSEDED excluded); LODO 21 folds",
     "Paper 2; findings.md; CHANGELOG", "canonical")

# --- fallback for the per-DTM sag dirs (must come after all specific rules) --
rule("data/outputs/wp2_sag/", "code/wp2_sag/sag_search.py",
     "NAC DTM (per-dir; PD fill + Frangi; runner: sag_search_run.py)", "", "canonical")


def attr(rel: str, name: str):
    """Return (producer, inputs, cited_in, status) for a workspace-relative path."""
    for pattern, producer, inputs, cited, status in RULES:
        if rel.startswith(pattern):
            if pattern == "data/outputs/wp2_sag/":  # fallback: per-file cited-in
                cited = _SAG_CITED.get(name, "—")
            return producer, inputs, cited, status
    return "—", "—", "—", "canonical"


def git_date(rel_repo: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%as", "--", rel_repo],
            cwd=REPO, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out or None
    except subprocess.CalledProcessError:
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    files = []
    for p in sorted(OUT_ROOT.rglob("*")):
        if not p.is_file():
            continue
        rel_ws = p.relative_to(WS).as_posix()
        if rel_ws.startswith("data/outputs/audit/"):
            continue
        if p.suffix == ".md":
            continue
        files.append((rel_ws, p))
    files.sort(key=lambda t: t[0])

    rows = []
    unattributable = []
    n_cited = 0
    for rel_ws, p in files:
        producer, inputs, cited, status = attr(rel_ws, p.name)
        if producer == "—":
            unattributable.append(rel_ws)
        if cited != "—":
            n_cited += 1
        d = git_date(rel_ws) or date.fromtimestamp(p.stat().st_mtime).isoformat()
        rows.append((rel_ws, sha256(p), producer, inputs, d, cited, status))

    lines = [
        "# PROVENANCE_INDEX — output artifact provenance sidecars",
        "",
        "One row per current/canonical output artifact under `data/outputs/`.",
        "sha256 computed at generation time. Dates: last-commit author date",
        "(git-tracked files) or filesystem mtime (gitignored rasters).",
        "Producer = best-known script under `code/`.",
        "cited-in restricted to papers/ (incl. gate reports), `notes/findings.md`,",
        "`admin/CHANGELOG.md`; \"—\" = none.",
        "",
        "**Exclusions**: `audit/` (internal audit working notes); hand-authored",
        "`*.md` methods/notes inside outputs/ (per_dtm_floors_METHODS.md,",
        "NOTES_task12_registration_mask.md, wp1_ladder/hapke+sensor METHODS.md,",
        "wp2_sag/transfer/METHODS.md); this index itself. No superseded/backup",
        "*file copies* live under `data/outputs/` — supersession is recorded as a",
        "status (pre-B1 registry backup: `data/candidate_registry_backup_2026-09-06.csv`,",
        "outside this tree).",
        "",
        "Regenerate (deterministic; lexicographic path order):",
        "`~/lunarvoid/venv/bin/python 01_WORKSPACE/code/tools/build_provenance_index.py`",
        "",
        f"Generated: {date.today().isoformat()} | rows: {len(rows)} |"
        f" cited-in >=1: {n_cited} | unattributable producer: {len(unattributable)}",
        "",
        "| artifact | sha256 | producer | key inputs | date | cited-in | status |",
        "|---|---|---|---|---|---|---|",
    ]
    for rel_ws, dig, producer, inputs, d, cited, status in rows:
        lines.append(
            f"| `{rel_ws}` | `{dig}` | `{producer}` | {inputs} | {d} | {cited} | {status} |"
        )
    lines += ["", f"Unattributable producers ({len(unattributable)}): "
             + (", ".join(f"`{u}`" for u in unattributable) or "none") + ".", ""]
    INDEX_PATH.write_text("\n".join(lines))
    print(f"wrote {INDEX_PATH} ({len(rows)} rows, {n_cited} cited, "
          f"{len(unattributable)} unattributable)")


if __name__ == "__main__":
    main()
