# LUNARVOID Full-Project Audit — "Next Level" Improvement Plan

> **SUPERSEDED** by `plans/2026-09-04_Project_Audit_Next_Level_v2.md`
> (same day). v2 merges this audit with the Hermes agent's independent
> audit (`notes/2026-09-04_AUDIT_REVIEW.md`, 42 findings incl. 4 verified
> detector-correctness bugs this v1 missed), adjudicates the conflicts
> (packaging, sequencing), and adds Phase 0 (correctness triage before
> paper submission). Retained for the audit trail.

**Date:** 2026-09-04
**Auditors:** skeptic (papers), explore ×2 (code, data), orchestrator (ops)
**Method:** 4 parallel read-only sweeps + ground-truth recomputation (Garwood CI
recheck, registry recount, JSON↔paper number reconciliation, row-level
traceability walk for rows 1/139/278)
**Status:** AUDIT — no changes made to any audited artifact

---

## 1. Executive summary

The project is scientifically honest and operationally disciplined, but it sits
at **research-script maturity**, not release maturity, and both papers are
**not yet submittable as written** — Paper 1 for format reasons (fatal at
triage, fixable in days), Paper 2 for structural reasons (its "catalogue" is
mostly below-floor rows; needs reframe, fixable in ~1-2 weeks).

The single most valuable insight from the audit: **the registry's "278
candidates" are ~130 unique features** (98 duplicate coordinate pairs counted
at multiple rungs), and the headline FP rate double-counts rung duplicates in
one site while excluding them in another. A **unique-feature re-accounting**
(FP 9 → 6; rate 3.74 → 2.49 [0.92, 5.43] per 10⁴ km²) is a recomputation-only
fix that makes every downstream number stronger.

**Maturity verdicts:**

| Layer | Now | Next tier | Blockers |
|---|---|---|---|
| Science/claims | honest, calibration-context | survey-grade FP rate | sampling bias (no random-mare), single evidence leg |
| Paper 1 | NEEDS-WORK | submittable | IMRaD rewrite, FP re-accounting, cover-letter reconcile |
| Paper 2 | NEEDS-WORK | submittable | reframe as benchmark/protocol; PU eval redesign |
| Code | research-script (~15.3k LOC, 50 files) | reproducible pipeline | no package/env contract, no tests, no runner |
| Data | registry + 26 JSONs | traceable artifact set | 15 corrupt rows, MANIFEST holes, no provenance blocks |
| Ops | single-machine | resilient | 1.5 MB untracked IP, no backup, no CI |

---

## 2. Findings by domain

### 2.1 Papers (skeptic audit)

**Paper 1 — verdict NEEDS-WORK (science SOUND-with-objections)**

| # | Finding | Severity |
|---|---|---|
| P1-1 | Manuscript contains internal scaffolding: absolute paths, md5 hashes, gate verdicts, budget text ("$0 spent"), "pending user review" (lines ~7-22, 199-201, 608-615). Editor sees a gate report, not a paper. **Also conflicts with the user's cost-privacy directive.** | FATAL at triage |
| P1-2 | FP numerator double-counts rung duplicates (FECUNPIT: 6 FPs = 3 unique depressions × 2 rungs) while 21 above-floor INGENIIPIT rings are excluded by annotation — opposite rules for the same phenomenon. Unique-FP aggregate = 6 → **2.49 [0.92, 5.43]**. | MAJOR |
| P1-3 | "14 above-floor inferred void candidates" in the abstract are the 14 TPs **at catalogued pits** — re-detections, not new candidates. Zero novel above-floor rows exist. | MAJOR |
| P1-4 | "Six analog sites" is really **4 sites** (3 instances are the same trench-hosted tube); LOO deferred; Hapke/sensor arms run on one site only. Transfer defended, not validated. | MAJOR |
| P1-5 | Cover letter overpromises: "calibrated inference probabilities" (not delivered), "ten References" (8 verified), "hold out 50% of analog sites" (actual: per-rung cell splits). Kingsbowl row unverifiable (source dir empty). | MAJOR |
| P1-6 | Cites stale registry path `data/outputs/wp2_sag/candidate_registry.csv`. | MINOR |
| P1-7 | v0.4 "lifted results across sites" omits the cave_1x tune-slope regression caveat. | MINOR |

**Paper 2 — verdict NEEDS-WORK**

| # | Finding | Severity |
|---|---|---|
| P2-1 | The catalogue has no catalogue: 233/278 rows below the paper's own detectability floor; above-floor = 14 known-pit re-detections + 9 FPs + 21 ring artifacts + 1 funnel case; the 22 unclassified above-floor rows are never reconciled. | FATAL (as framed) |
| P2-2 | PU evaluation invalid as scored: random row split leaks rung-duplicates across train/test; positives are the same detector's rank-1 outputs (self-labeling); 244 unlabeled silently treated as negatives; test n_pos=11 → F1 0.909 CI ≈ [0.62, 0.98]; v1→v2 gain = one extra row. | FATAL/MAJOR |
| P2-3 | Positive class ≠ voids: ~20 of 281 catalogued pits are tube-relevant; ranking by pit-similarity is not void-likelihood. §5.3's "right positive class" is circular. | MAJOR |
| P2-4 | Premature artifacts: placeholder conclusion; "commit forthcoming" for primary JSON; refs unverified; I10 inspection verdicts "applied but not captured" (rests on an unrecorded verbal confirmation). | MAJOR |
| P2-5 | ~40% of Paper 2 recycles Paper 1 text verbatim → Elsevier dual-submission/text-recycling risk. | MAJOR |
| P2-6 | Terminology clash: n_tp=14 vs PU n_positives=34; stale "3.71 [0.76, 10.83]" quote. | MINOR |

**Cross-paper:** Paper 1 gates Paper 2 on "once LLTB-1 validates the detector" but no validation criterion is ever met (best F1 0.28-0.36) and Paper 2 proceeds anyway — needs an explicit, honest hand-off sentence.

### 2.2 Code (explore audit — 50 files, ~15.3k LOC)

| # | Finding | Severity |
|---|---|---|
| C-1 | No package/CLI: no `pyproject.toml`, no console entry; scripts run via venv path + `sys.path` hacks. | CRITICAL for release tier |
| C-2 | `requirements.txt` missing **scikit-image (Frangi!), pulearn, pyyaml**; no python-version pin → environment not reproducible. | CRITICAL |
| C-3 | CC filter (v0.2) validated standalone only — **not wired into `sag_detect`**; `AREA_MIN_PER_RUNG` table lives in the integration script, not the detector. | MAJOR |
| C-4 | Near-zero formal test coverage (0 pytest files, no conftest, no CI; `smoke_test.py` + CC self-test only). | MAJOR |
| C-5 | Hardcoded absolute paths (`/home/frostflux/...`) in 7 files. | MAJOR |
| C-6 | FROZEN recipe (score_frac=0.20, slope 45°, neigh=5, sigmas) copy-pasted in ≥3 files, no frozen-config module. | MAJOR |
| C-7 | Duplication families: PU-learning ×3 generations; score-gen ×3 (`sag_search` → `sag_search_run` → `score_raster_gen` — with the kriging hook NOT ported to v3); skeptic-annotation twins; noise-floors ×3; fetchers ×3; `wp3_fusion` vs `wp5_fusion` naming drift. | MAJOR |
| C-8 | 8 silent `except Exception` blocks; magic constants (hardcoded pit coords with dead `if False else` branch). | MINOR |
| C-9 | Lunar chain has no runner: 4 hand-ordered scripts; `run_lltb1.py` covers analog only. | MAJOR |

### 2.3 Data (explore audit)

| # | Finding | Severity |
|---|---|---|
| D-1 | **Registry corruption: 15 rows have 16 fields** (unquoted commas in notes; GRUITHMARE2 ×10, MARIUSCONE ×2, TYCHOPK ×3 — includes row 278); 3 rows carry `methods="C"` (schema violation). | CRITICAL — central artifact |
| D-2 | **98 duplicate lon/lat pairs** (same feature at 2-3 rungs, never deduped/superseded) → "278 candidates" ≈ ~130 unique features. | CRITICAL for claims |
| D-3 | MANIFEST holes: entire `outputs/` tree (128 tracked files) unmanifested; **3 DTMs backing 18 registry rows (GRUITHMARE2/GRUITHUIS17/MARIUSCONE) have no MANIFEST rows**; all wp8 files orphaned. | MAJOR |
| D-4 | Provenance: 0/26 output JSONs carry git SHA; only 1 carries input hashes; `score_raster_gen_summary.json` **overwritten per run → 13/14 score-raster dirs undocumented**. | MAJOR |
| D-5 | Per-candidate traceability DANGLES for all 278 rows: `transfer_summary.json` has per-DTM aggregates only, no per-candidate keys (peaks/rung/raster path never persisted). | MAJOR |
| D-6 | `METHODS.md` (801 lines) stops at 2026-08-23: zero mention of PU-learning v1/v2 or the v0.2 CC filter. | MAJOR |
| D-7 | Notes free-text is load-bearing: `has_12km_FP` features are regex over prose; 18 rows have "ring artifact" text duplicated twice; span_m ranges 40-19,933 m vs the 60-300 m prior. | MAJOR |
| D-8 | Minor: `INGENII/` dir byte-identical to `INGENIIPIT/` (~90 MB waste); retry-log `http_status` column reflects legacy endpoint only; `ua_bypass_probe_2026-08-30.md` dated 2026-09-04 internally. | MINOR |

**Number reconciliation:** registry↔transfer_summary **PASS** (278/9/14/45/24,062.96 exact); transfer_summary↔Paper 1 §4 **PASS**; PU comparison JSON↔scripts **PASS**. The pipeline's arithmetic is clean — the problems are accounting semantics (D-2) and schema (D-1), not math.

### 2.4 Ops (orchestrator audit)

| # | Finding | Severity |
|---|---|---|
| O-1 | **1.5 MB of gitignored intellectual property with zero backup**: vault (516K, 100 atomic notes) + learning workspace (972K, 35 lessons). Single-disk-of-failure for 2 months of knowledge work. User chose local-only, but no local backup exists either. | HIGH |
| O-2 | No CI (no `.github/workflows`) — nothing runs the smoke test automatically. | MEDIUM |
| O-3 | Hetzner rental kit built but unlaunched → Cycles 3-5, random-mare control, MGC3, multi-evidence all blocked on a user decision pending since 2026-08-22. | MEDIUM (decision debt) |
| O-4 | Visual-inspection verdicts still unrecorded (radio buttons never persisted); Tier-B promotions impossible until captured. | MEDIUM |
| O-5 | Backup branch `backup/pre-cost-rewrite-original` still pushed to remote alongside rewritten master. | LOW |

---

## 3. The critical path — four phases to next level

### Phase A — Submission blockers (Paper 1 first) — ~3-5 days, $0

**A1. Paper 1 journal-format rewrite.** Full IMRaD; strip all internal
scaffolding (paths, hashes, gates, budget text, review-status notes) into a
Data Availability + reproducibility statement. This is the desk-reject fix.
Effort M.

**A2. Unique-feature FP re-accounting.** Recompute the headline as unique
depressions (FP 9 → 6; 3.74 → 2.49 [0.92, 5.43]) AND keep the raw-rate
variant with both definitions in a table. Requires deduping rung-duplicate
coordinates (overlaps D-2). Report both; explain the rule. Effort S
(recomputation) + M (prose).

**A3. Fix the "14 candidates" sentence** → "14 re-detections of catalogued
pits at above-floor scores; zero novel above-floor candidates exist in the
calibration-context set." One honest sentence, kills objection P1-3. Effort S.

**A4. Analog-site honesty**: "four sites (six map instances; three instances
are the same tube)" + move LOO from "deferred" to either done (it's cheap —
4 sites) or explicitly future work with a criterion. Effort S-M.

**A5. Cover-letter + metadata reconciliation**: 8 references, no
"probabilities" claim, actual split description, fix stale registry path
(P1-6). Effort S.

**A6. Sync reviewer list** with the 6 populated candidates; verify the
`[verify]` emails/affiliations. Effort S (user assist).

### Phase B — Registry & data repair — ~2-4 days, $0

**B1. Registry schema hardening.** Fix 15 corrupt rows + 3 `methods="C"`
rows; introduce quoted-CSV writer (csv module, not `",".join`); add
structured flag columns (`is_ring_artifact`, `fp_12km`, `superseded_by`)
instead of prose-regex; dedupe rung-duplicates with status=SUPERSEDED. Effort
M. **Blocks A2.**

**B2. MANIFEST completion.** Add outputs-tree, 3 missing DTM rows, wp8 files;
make `score_raster_gen.py` emit per-run `summary_<site>_<ts>.json` instead of
overwriting. Effort S-M.

**B3. Provenance blocks.** One shared helper (git SHA + input sha256 + frozen
params + timestamp) stamped into every output JSON writer. Effort S.

**B4. METHODS.md catch-up.** PU v1/v2 section + v0.2 CC-filter section +
Cycles 1-2 closure already there. Effort M.

**B5. Per-candidate records in transfer_summary** (peaks, rung, raster path,
run id) so the 278 anchors resolve. Effort M.

### Phase C — Engineering hardening — ~1-2 weeks, $0

**C1. `io_common.py`** (sentinel guards unified: |x|>1000 lunar / |x|>1e30
analog / −9999; GeoTIFF write; frozen-recipe constants; path resolver).
Effort S-M. Kills the #1 reproducibility blocker.

**C2. Environment contract.** Fix requirements.txt (scikit-image, pulearn,
pyyaml); pin python; add `pyproject.toml` + `lltb1` console script. Effort S-M.

**C3. Wire CC filter into `sag_detect`** with the AREA_MIN table in the
detector module; retire the inline variant. Effort S.

**C4. pytest scaffold.** Port smoke_test + CC self-test; add sentinel-guard
tests, registry round-trip test, calibration-holdout discipline test. Target:
the 5 highest-value untested paths from the audit. Effort M.

**C5. Archive superseded code** (`code/_archive/` + README): PU ×2, sag_search
lineage, annotation twins (after merging into one `--site` script). Effort S.

**C6. One-command lunar chain**: `lltb1 run --site X` chaining
score_raster_gen → noise_floors → transfer_apply with the frozen config.
Effort M.

**C7. GitHub Actions CI** running the smoke test + pytest on push. Effort S.

### Phase D — Scientific strengthening — 1-3 weeks, $0 until rental

**D1. PU-learning evaluation redesign** (fixes P2-2): group-split by DTM
(leak-proof), bootstrap CIs on F1/AUC, repeated CV, reframe metric as
"agreement with detector-rank-1 proxy," report n_pos CIs honestly. Effort M.

**D2. Capture inspection verdicts** (user eyes, ~30-60 min with a
plain-text capture form) → unblocks Tier-B logic and I10 section of Paper 2.
Effort S + user.

**D3. LOO across the 4 analog sites** (see A4). Effort S-M.

**D4. Paper 2 reframe** as "benchmark + protocol" paper: the catalogue is the
protocol output, the contribution is the calibrated pipeline + honest null
result ("zero novel above-floor candidates in calibration-context"), PU as
ranking-baseline with redesigned eval, unique-feature accounting throughout,
<10% verbatim overlap with Paper 1. Effort M-L.

**D5. Rental decision** (user): launch Hetzner → Cycles 3-5 stereo + 30
random-mare control DTMs → converts "calibration-context FP rate" into
"survey FP rate," the single biggest scientific upgrade available. Unblocks
MGC3 + multi-evidence (tier-B reachable with a second evidence leg).

### Cross-cutting

**X1. Backup the untracked IP.** Vault + learning → encrypted archive to a
second location (user's choice: private gist, USB, private remote branch).
~10 min. Ends the single-point-of-failure risk for 2 months of notes.

**X2. Zenodo release prep** (after Phase B+C): registry + code + METHODS as a
versioned DOI — turns the central artifact into a citable community resource
and satisfies journal data-availability requirements in advance.

---

## 4. Priority matrix (impact ÷ effort)

| Rank | Item | Phase | Effort | Unblocks |
|---|---|---|---|---|
| 1 | A1 Paper 1 IMRaD rewrite | A | M | submission |
| 2 | B1 Registry schema fix + dedupe | B | M | A2, D4, X2 |
| 3 | A2 Unique-FP re-accounting | A | S+M | stronger headline everywhere |
| 4 | C1+C2 io_common + env contract | C | S-M | all reproduction, CI, release |
| 5 | D1 PU eval redesign | D | M | Paper 2 credibility |
| 6 | B2+B3 MANIFEST + provenance | B | S-M | traceability, Zenodo |
| 7 | C3 Wire CC filter | C | S | closes v0.2 plan |
| 8 | X1 Backup untracked IP | — | S | resilience |
| 9 | C4 pytest scaffold + C7 CI | C | M | regression safety |
| 10 | D4 Paper 2 reframe | D | M-L | second submission |
| 11 | D5 Rental (user decision) | D | $ | survey-grade FP, tier-B |

**Recommended order:** A1 → B1 → A2 → A3-A6 → (submit Paper 1) → C1-C3 in
parallel with D1 → B2-B4 → D4 → C4-C7 → D5 when ready.

---

## 5. What "next level" looks like when done

- **Two submitted papers** with consistent, unique-feature accounting and
  zero text recycling; Paper 1's honesty apparatus intact but journal-shaped.
- **A registry that is a citable artifact**: schema-valid, deduped, flagged,
  MANIFEST-complete, per-candidate traceable to hashed rasters, Zenodo DOI.
- **A pipeline a stranger can run**: `pip install`-able, one command per
  site, CI-green, tests on the sentinel/registry/calibration paths that
  currently trust convention.
- **A stronger FP claim**: unique-feature rate + survey rate (post-rental),
  replacing the current calibration-context-only framing.
- **Zero single points of failure**: vault + learning backed up; outputs
  provenance-stamped; superseded code archived, not deleted.

All of Phase A-D except D5 and D2's eye-time is $0 and autonomous-ready; D5
(rental) and paper submission remain user decisions per stop conditions.
