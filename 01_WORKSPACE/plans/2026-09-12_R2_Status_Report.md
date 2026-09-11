# R2 — LUNARVOID Periodic Status Report

**Date:** 2026-09-12 (B10, execution session 47 state)
**Author:** archivist (task B10 Part 2)
**Built from:** `admin/CHANGELOG.md` sessions 1–47 + `git log --oneline` (not from memory). Every number below carries its CHANGELOG session citation.
**Supersedes as live status doc:** `plans/2026-08-21_R1_Roadmap_draft.md` (untracked; see §6).

---

## 1. Executive state

- **Curriculum:** 35/35 lessons complete across 7 phases (session 34; gitignored `learning/`, ~25K lines).
- **Gates:** G0′ FINAL-PASSED 2026-08-21 (D1, erratum 0.7 restates reproducibility true-as-of 2026-09-04); G1 FINAL-PASSED 2026-08-22 (human decision); G2 FINAL-PASSED 2026-08-24 (user delegation; session 32 records the user confirmation).
- **Paper 1 v2.0 — submission-ready, complete package** (sessions 38–41): IMRaD rewrite 8,281 words; honesty apparatus (A3/A4); 9 references (9th = Kelahan et al. 2026, arXiv:2608.09350, session 41); cover letter, highlights, referee template, graphical abstract PNG (sha 52a387e2…), reviewers list all v2.0-consistent (session 39).
- **Paper 2 v3.1-draft** (session 46, `5adc3cc`): reframed to *annotated test-bed registry + leakage-corrected evaluation protocol*; novelty narrowed and distinguished from pit catalogues / detection-training releases; references 14 → 18; skeptic V1–V6 addressed.
- **LLTB-1 v0.5.1** (session 44, `398fada`): CC filter wired as `--cc-filter {off,on,auto}`, **default off** (v0.5 parity byte-identical; honest eval: no-op 6/7 sites).
- **E3 Zenodo package staged, upload user-gated** (session 47, `2f5b1ff`): `data/zenodo_deposit_v1.0/` (~0.6 MB; CHECKSUMS 10/10).
- Audit-remediation plan (`2026-09-04_Project_Audit_Next_Level_v2.md`): Phases 0/A/C substantially closed; B closed except the B1-B5 remainder; D1/D4 done; open items in §4–5 below.

## 2. Frozen scientific results (all CHANGELOG-cited)

| Result | Value | Source (session) |
|---|---|---|
| Row-based FP rate | **3.74 [1.71, 7.10] per 10⁴ km²** (n_fp 9 / 24,062.96 km², 21 DTMs; calibration-context) | 27 (close), 38 (reproduced to 1e-9), 47 (C6 guarded run reproduced exactly) |
| Unique-feature FP rate | **2.08 [0.67, 4.85] per 10⁴ km²** (5 unique FPs; ~30 m key, stable 30–60 m; 6 TP + 5 FP + 9 ring + 1 funnel) | 38 |
| Registry | **278 = 117 ACTIVE (15 P / 102 U) + 161 SUPERSEDED**, all tier C | 38 (B1), 40, 46 (verifier recount) |
| Above-floor rows | **45 = 14 TP + 9 FP + 21 ring + 1 funnel** (skeptic-reproduced exactly); 233 below-floor = labelled resolution-floor output | 38, 46 (V4) |
| PU v5 run B (morphometric-only, 15 features) | **F1 0.824 / P 0.737 / R 14/15 / AUC 0.930**; cluster-bootstrap 95% CIs **F1 [0.35, 0.98] / AUC [0.49, 1.00]**; decisions identical to full-19 run at t=0.5 (0/117) | 40 |
| PU v5 run A (19 features) | AUC **0.927** (AUC range 0.927–0.930 across runs; decisions identical to B) | 40 |
| PU v5 run C (`rung_cm` ablation, 14 features) | **F1 0.800 / AUC 0.928**; cluster CIs F1 [0.285, 1.000] / AUC [0.486, 1.000]; 5/117 flips vs B; I14 failure unmoved | 41 |
| Leave-INGENIIPIT-out | **F1 0.571 / AUC 0.790** (10/15 positives in that fold) | 40 |
| TRANQPIT1 3 row-FPs | = **two** spatial structures (16.5 m pair + 132.8 m third; double-haversine ground truth; earlier "≤0.1 m" claim refuted) | 38 |
| PU v2 legacy numbers | F1 0.909 / AUC 0.931 annotated **leak-inflated** (random split, full-dataset imputation) | 40 |
| I14 funnel recurrence | MARIUSPIT01 0400cm-r001 score ~2.2e-72, rank 1/15, predicted negative in B and C — pre-registered failure recurring in the PU layer | 40, 41 |

## 3. Infrastructure state

- **pytest: 73 passed** (58 from session 43 + 15 v0.5.1 mode tests, session 44; 73 confirmed through session 47). 46 checks *re-execute* the ported verifications, not stored-JSON asserts.
- **Smoke pins (full precision):** F1 0.39160839160839167 / 0.0 / 0.8; fusion AUC 0.990; tol 1e-6 (session 43).
- **Real-data E2E pin:** `Fieg_0.5m.npz → sag_detect` → f1 **0.029746281714785657** tol 1e-5 (session 43); auto-skips when data absent.
- **C6 run_cycle chain + frozen-artifact guard** (session 47): snapshot/re-hash/byte-restore over registry + 4 evidence JSONs; guarded TRANQPIT1 run — 8 shas byte-identical, 1 blocked write restored; retry-1 incident documented in the run JSON.
- **PROVENANCE_INDEX: 160 artifacts**, 66 cited-in, 0 unattributable; deterministic builder; zero in-place edits to cited evidence (session 42).
- **CI: staged, not active** — `admin/ci/ci.yml` + README; activation is a user-gated root-`.github/` exception (session 43).
- **C7 silent-except audit done** (session 45): 65 sites, zero bare excepts, 2 dangerous silences fixed (GRAIL rows, Diviner sampling), 26 silent-by-design markers.
- **C13 registry_io + LEAK assert**, C8 supply-chain pin, C9/C10 shared CRS/HTTP, C12 commit-msg guard: done (sessions 36–37).

## 4. User-gated queue

| Item | What is needed |
|---|---|
| **E3 Zenodo upload** | ① confirm CC-BY-4.0 (data) + MIT (code); ② creator list for metadata; ③ Zenodo token + upload go; ④ optional ADR D6 wording revisit; ⑤ optional ORCID (session 47). Package ready at `data/zenodo_deposit_v1.0/`. |
| **R1 draft commit** | User go-ahead to `git add plans/2026-08-21_R1_Roadmap_draft.md` with lineage note (B10 portion skipped this session per gate). |
| **CI activation** | User-approved exception to the AGENTS.md root-clean rule: copy `admin/ci/ci.yml` → `<root>/.github/workflows/` (session 43). |
| **D2 inspection-verdict capture** | User eyes on the visual-inspection backlog (FECUNPIT 3 + TRANQPIT1 3 + INGENIIPIT 21 candidates, session 24); verdicts never persisted. |
| **D5 rental launch** | User authorization per §8 stop conditions; Hetzner kit complete (12 files, DO-NOT-RUN banners, session 31); unlocks Cycles 3-5 + random-mare survey rate. |
| **Zotero attaches** | Kelahan 2026 (arXiv:2608.09350); Watson & Baldini 2024 (Icarus 411:115952); ESSA/Le Corre 2025 (Icarus, DOI-verified); +3 genre refs — Moonstone 2607.03644, Mars-Bench 2510.24010, StereoLunar 2510.18172 (sessions 41, 46; earlier Paper-1 refs pending per session 29). |
| **E2 conventions-skill exposure / vault mirror** | User approval for a tracked `admin/` mirror (`.opencode/` deliberately untracked 2026-08-23). |

## 5. Open non-gated items

- **Paper 2 polish pass** — cosmetics queued (session 46: NEW-ref block ordering Williams #17/Watson #18, title hard-wrap; session 44: eval-script `--help`). *Disk note 2026-09-12: the cosmetic fixes are applied but UNCOMMITTED in the working tree as "v3.2-draft" (header date corrected to 2026-09-12 at commit time; this session commits it as v3.2-draft).*
- **prior_art_matrix genre rows** — appended this session (4 rows: Kelahan, Prasad&Mazumder, Purohit, Grethen; committed with this batch); Laurier/ASU pit database audit item flagged (session 46).
- **B10 remainder** = R1 draft commit only (user-gated, §4).
- **Cycles 3–5 NAC EDR re-probe** — root cause identified as PDS S3 bucket migration (LROLRC_2001 not yet in pds-img-archive-prod; session 34); 4-stage retry script exists; re-probe when PDS settles, patch queued.
- **Engineering remainders (v2 plan, unticked 2026-09-12):** B1-B5 cluster tail (quoted-CSV writer, schema validation, structured flag columns, per-run summary files, B5 per-candidate records), C-io_common, C5 code archival, C15 remainder (sentinel constant + per-chunk warning), D3 analog LOO.

## 6. Version lineage note

- **R1** = `plans/2026-08-21_R1_Roadmap_draft.md` — an *untracked* draft (never committed; its commit is user-gated). Retained for the audit trail.
- **R2** (this file) supersedes R1 as the live status document. It is rebuilt from CHANGELOG truth (sessions 1–47) + `git log`, per the B10 dispatch of 2026-09-12; the R1-commit portion of B10 was skipped as user-gated.
- Next periodic report (R3) should again rebuild from the CHANGELOG, not from this file.
