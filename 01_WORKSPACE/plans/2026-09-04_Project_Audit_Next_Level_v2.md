# LUNARVOID Next-Level Plan v2 — merged audit & remediation roadmap

**Date:** 2026-09-04
**Supersedes:** `01_WORKSPACE/plans/2026-09-04_Project_Audit_Next_Level.md` (v1, same day)
**Inputs merged:**
- **v1 audit** (opencode orchestrator): skeptic (papers) + explore ×2 (code, data) + ops review → paper-submission blockers, FP-accounting semantics, registry corruption, MANIFEST/provenance gaps, backup risk
- **Hermes audit** `notes/2026-09-04_AUDIT_REVIEW.md` (42 findings: 6 HIGH / 15 MED / 15 LOW / 4 DIR; every HIGH/MED re-verified by Hermes with direct file:line reads, subagent fan-out, and an honest RETRACTED log)
- Raw subagent evidence: `notes/2026-09-04_audit_security_tests_dx.md`, `data/outputs/audit/audit_findings.md`
- **Orchestrator spot-verification (this session):** 4/6 Hermes HIGH claims independently re-confirmed by grep (float64 absence, `if False` + fabricated JSON block, broken Paper 2 citation, integer rebin). All 4 confirmed.

**Complementarity:** Hermes deep-audited code correctness/security/docs and explicitly did NOT audit paper claims or data accounting; v1 deep-audited papers/data/ops and flagged code only at architecture level. The two audits overlap on exactly one finding (missing `scikit-image`) and otherwise interlock. Neither alone is sufficient; this plan is the union with conflicts adjudicated.

---

## 0. Adjudication log (v1 vs Hermes conflicts — rulings)

| # | Conflict | v1 said | Hermes said | Ruling (v2) |
|---|---|---|---|---|
| ADJ-1 | Packaging | Add `pyproject.toml` + `lltb1` console scripts (C2) | Do NOT package; write ADR "scripts-not-package" (LOW-14) — regression risk on published invocation paths, single-machine paper repo | **Adopt Hermes.** Fix requirements + add a thin `run_cycle.py` entry (both audits want this) but defer pip-packaging to an explicit trigger: first external user or Zenodo code release. Record ADR D6 with that trigger. |
| ADJ-2 | Sequencing | Phase A (paper submission) first | HIGH-2/-3/-4 correctness bugs may touch the frozen calibration → verify before publishing numbers | **Adopt Hermes.** New **Phase 0** (correctness triage + parity verification) gates Phase A. A paper submitted over unverified arithmetic is a retraction risk; a 1-2 day delay is not. |
| ADJ-3 | Registry row defects | 15 rows with 16 fields (unquoted commas) + 3 `methods="C"` violations | +1 comment-artifact row (279 parsed vs 278 real; `# provenance:` mid-file leaks as data) | **Both real, different bugs.** Fix all: quoting writer, schema validation, comment-skipping parser. |
| ADJ-4 | PU-learning | Statistical redesign needed (leakage via rung-duplicates in random split; n_pos=11 CI) | Code-level: byte-duplicated parsers, drifted `build_positive_mask`, brittle leakage guard (comment-only), always-NaN `roc_auc_test`, broken citation | **Both.** MED-15-style assert is the 30-minute guard; the group-split-by-DTM + bootstrap-CI redesign is the real fix. Sequence guard → redesign. |
| ADJ-5 | Test strategy | pytest scaffold + CI | Port the 7 ad-hoc verification_evidence scripts to pytest; add real-data E2E fixture on frozen analog input | **Adopt Hermes's fuller version** of v1's C4: pytest scaffold + E2E fixture + CI, keeping existing evidence JSONs as fixtures. |

---

## 1. Revised maturity verdict

| Layer | v1 verdict | v2 verdict (post-merge) |
|---|---|---|
| Detector arithmetic | "clean — reconciliation PASS" | **Qualified**: reconciliation of *recorded* numbers passes, but HIGH-2/-3/-4 mean some of those numbers were computed by code paths that violate the project's own documented conventions (float64, fractional rebin, rung-posting Frangi). Parity re-runs required before the numbers can be called verified. |
| Evidence integrity | "JSONs match scripts" | **One fabrication found** (MED-12): `v0_2_integration_test.json` contains a hardcoded `synthetic_smoke_test: passed=true` block never executed by that script. Cited in CHANGELOG session 34. Must be regenerated or retracted. |
| Environment | "not reproducible (deps missing)" | **Worse than v1 thought**: 8 imported packages missing incl. `scikit-image` (core detector); G0' gate claim "Tier-0 reproducible from requirements.txt" is currently **false** and needs an erratum after the fix. |
| Papers / science | NEEDS-WORK both | Unchanged (Hermes did not audit; v1 skeptic verdicts stand). |
| Registry | corrupt + duplicate-laden | Unchanged + comment-artifact row (ADJ-3). |

**Bottom line:** v1 said "the math is right, the accounting is wrong." Hermes showed the *math engines* themselves have convention-violating code paths. The recorded numbers may still be fine (the correct code paths exist in sister modules and the caches may have been built by them) — but that is now an open empirical question that Phase 0 answers.

---

## 2. Phase 0 — Correctness triage & parity verification (NEW; blocks Phase A)

**Goal:** determine, with evidence, whether the published/frozen headline numbers survive the documented-correct code paths. Every fix ships with a parity check against frozen evidence (tolerance per T5 protocol: ±5%; smaller deltas documented).

| # | Task | Source | Effort | Acceptance |
|---|---|---|---|---|
| 0.1 | **Requirements regen** — `pip freeze --local` into `code/setup/requirements.txt`; verify `from skimage.filters import frangi` imports in a fresh-venv smoke; add generation-date header; fix `whitebox` version in conventions skill §1 (2.4.0 → 2.3.6) | Hermes HIGH-6 + MED-11 | S | fresh `pip install -r` runs `smoke_test.py` green |
| 0.2 | **Frangi float64 upcast** in `sag_detect.py` + `sag_search.py` (`Zf = Zf.astype(np.float64)` before `frangi()`); re-run LLTB-1 v0.5 verification + smoke test; **parity table** old-vs-new per-site F1 | Hermes HIGH-2 | S + parity M | parity table committed; any site ΔF1 > tolerance → escalate (numbers regenerate → papers update) |
| 0.3 | **Fractional rebin helper** `wp2_sag/transfer/_rebin.py` extracted from `score_raster_gen.py:144-160`; replace integer-factor blocks in `sag_search_run.py`, `noise_floors_batch.py`, `calibrate_transqpit1.py`, `transfer_apply.py`; parity-check the 21-DTM noise floors and TRANQPIT1 frozen calibration | Hermes HIGH-3 | M | floors + calibration reproduce within tolerance or delta documented |
| 0.4 | **Frangi at rung posting** in `score_raster_gen.py` (sub-sample `dtm_r`, set `effective_rung = rung`); regenerate affected score rasters for >5000-px DTMs (TYCHOPK07, FRESHMELT); parity vs cached | Hermes HIGH-4 | S + regen M | regenerated rasters hashed; registry Amin/scores reconciled |
| 0.5 | **Evidence-integrity fix**: remove `if False` in `v0_2_pipeline_integration.py`; actually call `catalogued_pit_region()` and assert (887, 608); run the real synthetic self-test and emit measured counts (or delete the block and reference `smoke_test.py`); regenerate `v0_2_integration_test.json`; append correction note to CHANGELOG | Hermes MED-12 | S | regenerated JSON contains only measured values |
| 0.6 | **NaN-mask Frangi** (replace nanmean fill with NaN in / finite-mask out) in the 4 `frangi_vesselness` sites; synthetic NoData-band fixture test | Hermes MED-3 | S | phantom-edge vesselness gone in fixture |
| 0.7 | **G0' gate erratum** — one-paragraph amendment to the G0' report: reproducibility claim restated as true-as-of 0.1 (requirements complete), with the interim gap acknowledged | consequence of HIGH-6 | S | erratum row in both gate mirrors |

**Phase 0 exit:** parity report (one file, `admin/verification_evidence/2026-09-XX_parity_report.md`) stating per-check: UNAFFECTED / AFFECTED-Delta<X> / REGENERATED. Papers cite this report in Data Availability.

---

## 3. Phase A — Paper 1 submission package (revised; gated on Phase 0)

Unchanged from v1 unless Phase 0 regenerates numbers (then A2 uses corrected values), plus:

| # | Task | Source |
|---|---|---|
| A1 | IMRaD rewrite; strip internal scaffolding (paths, hashes, gate verdicts, budget text, review-status) → Data Availability | v1 P1-1 |
| A2 | Unique-feature FP re-accounting (FP 9→6; 3.74→2.49 [0.92, 5.43]); report both definitions; reconcile the 22 unclassified above-floor rows | v1 P1-2/P2-1 |
| A3 | "14 re-detections, zero novel above-floor candidates" honesty sentence | v1 P1-3 |
| A4 | 4-sites-not-6 honesty + LOO either done or criterion-stated | v1 P1-4 |
| A5 | Cover-letter/metadata reconcile (8 refs, no "probabilities" claim, real split description, stale registry path) | v1 P1-5/P1-6 |
| A6 | **Paper 2:849 citation fix** `pu_learning_baseline_v2.py` → `pu_learning_extended.py` | Hermes MED-13 (verified this session) |
| A7 | Text-recycling pass on Paper 2 (<10% verbatim overlap with Paper 1) | v1 P2-5 |

---

## 4. Phase B — Registry & documentation repair

v1 B1-B5 (quoted-CSV writer + schema validation + structured flags + 15-row/3-row fixes + comment-skip parser (ADJ-3) + dedupe 98 rung-duplicates with SUPERSEDED + MANIFEST completion + provenance blocks + per-run summaries + per-candidate records + METHODS.md PU-v2/CC-filter sections), plus Hermes doc items:

| # | Task | Source |
|---|---|---|
| B6 | `regen_site_notes.py`: skip mid-file `#` rows; fix/remove `ci_method` read (empty `()` in 21 site notes); delete unused `MOC_SITES` or implement it; re-run regen | Hermes LOW-11 |
| B7 | Vault `00_HOME.md` 257→278 refresh; superseded banner on 2026-08-20 v0.2 release note (or rename newer note v0.6); registry-count fork closed | Hermes LOW-7/-12 |
| B8 | Gate-mirror hygiene: canonical = `plans/`; G1 wording divergence fixed; md5-check step or pointer files | Hermes LOW-13 |
| B9 | ADRs D3 (frozen TRANQPIT1 calibration), D4 (deep-pit 0.02/100 m rule), D5 (Planchon-Darboux mandate), D6 (scripts-not-package, per ADJ-1) — each ~15 lines, cross-linked from MOC | Hermes MED-14 + LOW-14 |
| B10 | Roadmap sync sweep (tick delivered boxes; commit R1 draft with lineage note; R2 rebuild from CHANGELOG) | Hermes MED-8/-9, LOW-5 |
| B11 | Findings-log entries: Diviner 0.0-sentinel quirk; 3× pooled-RMS convention citation | Hermes LOW-4/-3 |

---

## 5. Phase C — Engineering hardening

v1 C-items retained (shared `io_common` absorbing sentinel/GeoTIFF/frozen-recipe/path-resolver; wire CC filter into `sag_detect` with AREA_MIN table; pytest scaffold + CI; archive superseded code; `run_cycle.py` one-command lunar chain; silent-except audit), plus:

| # | Task | Source |
|---|---|---|
| C8 | **Supply-chain pin**: HTTPS mirrors first + `EXPECTED_SHA256` + verify-before-`ar x` in `extract_rar.py`; aggregate mirror errors | Hermes HIGH-5, LOW-6 |
| C9 | **Shared CRS module** `code/_crs.py` (MOON_CRS_WKT, ANALOG_CRS_WKT); replace EPSG:4326/32631 literals in `confusion_layer.py`, `evidence_layers.py`, `vci.py`, `degrade.py` | Hermes MED-2 |
| C10 | **Shared HTTP helper** (project UA + retry); all fetchers import it | Hermes MED-4 |
| C11 | **Real-data E2E fixture test**: frozen `Fieg_0.5m.npz` → `sag_detect` → assert F1 within 1e-5 of pinned | Hermes MED-6 |
| C12 | **Commit-msg cost guard** hook (`admin/git-hooks/commit-msg`) enforcing the forbidden-phrase list | Hermes HIGH-1 |
| C13 | `registry_io.py` extraction (shared loader/parser for PU v1/v2); reconcile `build_positive_mask` drift; `LEAK_FEATURES` assert (quick half of ADJ-4) | Hermes MED-13/MED-15 |
| C14 | Fix-or-drop always-NaN `roc_auc_test` in `pu_learning_baseline.py` (or archive the file per v1 retirement) | Hermes MED-7 |
| C15 | Small fixes batch: `retry_nac_edr_fetch` csv.DictReader; `parallel_range_download` pwrite; graben placeholder drop; HEAD-probe sleep reorder; sentinel constant + per-chunk warning | Hermes LOW-1a/b/c, LOW-8, LOW-10 |

**Dropped from v1 (per ADJ-1):** `pyproject.toml` + console-script packaging → replaced by ADR D6 + `run_cycle.py`. **Kept from v1, not in Hermes:** kriging-hook port audit when retiring `sag_search.py` (v1 C-7 note: the in-process kriging wiring was never ported to the v3 generator).

---

## 6. Phase D — Scientific strengthening (unchanged in substance)

D1 PU eval redesign (group-split by DTM, bootstrap CIs, agreement-with-proxy framing — the full half of ADJ-4); D2 inspection-verdict capture (user eyes); D3 LOO; D4 Paper 2 benchmark/protocol reframe; D5 rental decision (unlocks random-mare survey rate, Cycles 3-5, second evidence leg — kit ready, user authorization required per stop conditions; see `admin/budget.md` Phase-6 lines).

---

## 7. Phase E — Ops & resilience (expanded from v1 X-items)

| # | Task | Source |
|---|---|---|
| E1 | **Backup untracked IP** (~1.5 MB vault + learning, and now also the gitignored single-copy conventions/protocol skills) to a second location; user picks medium | v1 O-1 + Hermes MED-11 |
| E2 | Conventions-skill exposure decision: version-fixed now (0.1); tracked `admin/` mirror **requires user approval** (user untracked `.opencode/` deliberately 2026-08-23) | Hermes MED-11, adjudicated |
| E3 | Zenodo release prep (registry + code + METHODS, versioned DOI) after B+C; satisfies journal data-availability | v1 X2 |
| E4 | CI workflow running smoke + pytest (pairs with C4/C11) | v1 + Hermes DIR-3/4 |

---

## 8. Revised priority matrix

| Rank | Item | Phase | Effort | Why this order |
|---|---|---|---|---|
| 1 | 0.1 requirements regen | 0 | S | falsifies-nothing, unblocks everything, fixes gate claim |
| 2 | 0.2-0.4 correctness fixes + parity table | 0 | S-M | numbers must be trustworthy before they're published |
| 3 | 0.5 evidence-integrity regen | 0 | S | a fabricated PASS in an evidence file is poison |
| 4 | A1 IMRaD rewrite | A | M | desk-reject fix; start after 0.2-0.4 verdict |
| 5 | B1 registry schema + dedupe | B | M | blocks A2, D4, E3 |
| 6 | A2 unique-FP re-accounting | A | S+M | headline strength |
| 7 | C8 supply-chain pin; C13 registry_io + leak assert | C | S | cheap, high-risk-killing |
| 8 | 0.7/A5/A6 gate erratum + citation fixes | A | S | claim hygiene |
| 9 | C9/C10 shared CRS/HTTP; io_common | C | S-M | converges with 0.3 helper |
| 10 | C11 E2E fixture + C4 pytest + E4 CI | C | M | locks in Phase 0 forever |
| 11 | E1 backup IP | E | S | resilience; do early, costs minutes |
| 12 | B6-B11 doc/ADR sweep | B | S | paper-supporting provenance |
| 13 | D1 PU redesign; D2 verdicts; D4 reframe | D | M-L | Paper 2 credibility |
| 14 | C pytest remainder + archives + run_cycle | C | M | release tier |
| 15 | D5 rental decision; E3 Zenodo | D/E | user | stop-condition items |

**Critical path:** 0.1 → 0.2/0.3/0.4 (parallel) → parity report → A1 → B1 → A2 → A3-A7 → **submit Paper 1** → C-track and D-track in parallel → Paper 2 → release tier.

---

## 9. What "next level" looks like (v2 restatement)

v1's vision unchanged, plus: **every published number is reproducible from a requirements-complete fresh venv by a CI job**, every evidence JSON contains only measured values, and the three most-contested scientific decisions (frozen calibration, deep-pit rule, PD fill) have ADRs a referee can read in five minutes. The Hermes audit's meta-lesson is institutionalized: multi-agent fan-out with retraction logging caught three errors a single-pass audit made — keep skeptic/verifier fan-out on every future gate.

*Cost figures intentionally omitted here (see `admin/budget.md`); per user directive, commit messages carry no cost information.*
