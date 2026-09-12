# R3 — LUNARVOID Periodic Status Report (terminal state)

**Date:** 2026-09-12 (HEAD `c5be2a2`, execution session 58 state)
**Author:** paper-writer (B10 Part 3 — terminal report)
**Built from:** `admin/CHANGELOG.md` sessions 48–58 + `git log` (not from memory). Every number below carries its CHANGELOG session citation; frozen registry md5 `a60fb52152e33f37e9052434ad026a6e` verified at HEAD.
**Supersedes as live status doc:** `plans/2026-09-12_R2_Status_Report.md` (sessions 47 snapshot, 71 lines).
**Supersession precedent:** R1 (untracked, user-gated) → R2 → R3.

---

## 1. TL;DR

- **Both papers submission-ready** — Paper 1 v2.1 (12 refs, 3 method refs added, 8 of 9 prior refs resolver-corrected verbatim) and Paper 2 v3.3-draft (18 refs, 6 biblio fixes, first-claim hedged); verifier PASS-with-notes on both.
- **Gates G0′ / G1 / G2 all FINAL-PASS** (final delegation session 32; D1 erratum 0.7 restates reproducibility true-as-of 2026-09-04).
- **v2-plan autonomous queue exhausted** — B-cluster closed (session 57), C-io_common + C5 + C15 delivered (sessions 51/55/56), PROVENANCE row-47 pointer + row-48 annotation applied (sessions 54/58), `__main__` guard refactor (session 53).
- **NAC reclassified BLOCKED → MEDIUM-OPEN (s59) → HIGH-OPEN-CHAIN (s60)** — session-49's "blocked" was a wrong-URL call; WMS RDR metadata chain verified-fetchable (RDR product page 23,154 B; `view_rdr` HTML 10,370 B at sha256 `bb2c525c1ad622bc185c4e7c13a3febcf99a4780d83c8e77a88dc3cabb53c571`; PDS dataset `LRO-L-LROC-5-RDR-V1.0` + `LROLRC_2001` bundle + `view_rdr_product` IMG-download link one hop deeper); IMG byte-signature verification deferred to user-gated pipeline (Tier-0 budget eligible).
- **Vault current to session 58** — 32 atomic notes (sessions 26–57) written via orchestrator bash under the space-in-path permission gap (session-44 precedent); `00_HOME.md` refreshed.
- **Retro-skeptic closed the session-58 protocol gap** — sessions 51/52/57 findings blocks had entered without skeptic review; session-58 retro-review SOUND-with-wording for 51/57, UNSOUND framing for 52 (warning-band conflated with gray-band — corrected: 85,273/85,304 are real swath-edge geometry, only 31 ghosts).
- **124 tests green** on HEAD `c5be2a2`; frozen registry md5 unchanged; deposit CHECKSUMS 10/10.
- **$0 spent** over 58 sessions; Tier-1 / Tier-2 untouched; all probes Tier-0 or HTTP-only.

## 2. Papers status

### 2.1 Paper 1 — v2.1 submission-ready (session 50)

- 12 references (was 9 in v2.0): 8 of 9 prior refs resolver-corrected verbatim — Blair author order, Carrer author list, Mueller + Reichenzeller conflated titles, Theinat venue (AIAA SPACE), Wagner & Robinson 2021 conflated title, Wong initials; Wong 2014 attribution verified via Wayback (session 51).
- 3 load-bearing METHOD references added (skeptic must-have, session 50): **Planchon & Darboux 2002** *Catena* 46(2):159–176 (epsilon fill); **Wang & Liu 2006** *IJGIS* 20(2):193–213 (breach fill); **Garwood 1936** *Biometrika* 28(3/4):437–442 (Poisson-exact CI). In-text anchors at first-use sites (L87 ×2, L113).
- Population phrasing fix: "~281" → "~300" at 8 sites (281 was the impact-melt subset; shapefile = 278; JGR-2022 "almost 300").
- Reviewer-conflict catch: Bickel demoted (real conflict = co-authorship on Kelahan 2026, not Blair 2017); Mittelholz promoted.
- Package consistency: TRANQPIT1 two-structure intact (17/133 m main; 16.5/132.8 m template); "to our knowledge" hedge retained §1.3; GA plan → v2.1; referee template self-count refreshed (307 lines / 8,617 words). Verifier **PASS-with-notes**.

### 2.2 Paper 2 — v3.3-draft submission-grade (session 49)

- 18 references (was 14 in v3.1): 6 resolver-verified biblio corrections — Powell *JGR Planets* 128(2) e2022JE007532; Williams Diviner *Icarus* 283:300–325; Hurwitz *PSS* 79–80:1–38 (was nonexistent *Icarus* 225); Sauro 2020 *ESR* 209:103288 (replaced misresolved "Pozzobon"); both Cushing records corrected (PDS 2015 + AbSciCon 2017 LPI Contrib. 1965 #3708 MGC3); Besserer / Elkins placeholders dropped.
- v1 PU numbers fixed (baseline JSON + registry as ground truth): P/R detransposed → **P 0.9000 / R 0.8182 / AUC 0.8968**; INGENIIPIT ring **24/23 → 21** in 4 places (independent recount: 34 = 21 ring + 13 r001, IRIDIUMPIT1 below-floor).
- Skeptic-demanded wording verbatim: first-claim hedged ("to our knowledge, the first framework in the lunar literature to make FP per 10⁴ km² a mandatory reporting metric…"); code-availability corrected to on-request + E3-tied.
- Eval CLI safety: bare invocation now prints help + exits; `--run` gate; `--list-runs`; `--version` sha. Verifier **PASS + delta re-pass PASS-with-notes**.

## 3. Gates — FINAL-PASS

| Gate | Status | Citation |
|---|---|---|
| **G0′** | FINAL-PASS (2026-08-21 v1.1; D1 erratum 0.7 restates reproducibility true-as-of 2026-09-04) | `plans/2026-08-21_GATE_G0prime_report_v1.1.md` |
| **G1** | FINAL-PASS (2026-08-22; human decision) | `plans/2026-08-22_GATE_G1_report_v1.0.md` |
| **G2** | FINAL-PASS (2026-08-24; user delegation; session 32 records the user confirmation) | `plans/2026-08-23_GATE_G2_report_v1.0.md` |

All three verdicts stand; no new gate decisions opened in sessions 48–58.

## 4. Frozen scientific numbers (all CHANGELOG-cited; byte-identically reproducible)

| Result | Value | Source |
|---|---|---|
| Row-based FP rate | **3.74 [1.71, 7.10] per 10⁴ km²** (n_fp 9 / 24,062.96 km², 21 DTMs; calibration-context) | sessions 27, 38, 47 |
| Unique-feature FP rate | **2.08 [0.67, 4.85] per 10⁴ km²** (5 unique FPs; ~30 m key) | 38 |
| Registry md5 | **`a60fb52152e33f37e9052434ad026a6e`** (verified at HEAD) | 57 + HEAD audit |
| Registry partition | **278 = 117 ACTIVE + 161 SUPERSEDED**, all tier C | 38, 46 |
| Above-floor partition | **45 = 14 TP + 9 FP + 21 ring + 1 funnel**; 233 below-floor | 38, 46, 57 |
| v1 PU (P2 v3.3 ground truth) | **P 0.9000 / R 0.8182 / AUC 0.8968** | `data/outputs/wp5_fusion/pu_learning_registry_baseline.json` (HEAD; session 49 recount) |
| PU v5 run B | F1 **0.824** / P 0.737 / R 14/15 / AUC **0.930** | 40 |
| INGENIIPIT ring | **21** (was 24/23, 4 places corrected) | 49 |
| TRANQPIT1 3 row-FPs | **two** spatial structures — 16.5 m pair + 132.8 m third | 38 |
| Frozen registry md5 reproducibility | **byte-identical** under C-io_common refactor + sentinel hardening | 56, 57 |

## 5. Engineering surface since R2 (sessions 48–58; v2-plan queue → CLOSED)

- **C15 / LOW-10 sentinels** (sessions 51–52): `convert_f32.py` `SENTINEL_MAX_M=1e6 / WARN_MAX_M=100.0 / ATTR_SENTINEL_MAX=1e3`, `F32_NODATA=-9999.0`; mirrored in `io_analog.py` (LOW-10 house style); sentinel regression guards; **tests 73 → 80 → 89**. Verifier-caught: NOT dormant — 37 + 31 gray-band points (real swath-edge geometry in (100, 1e6]) intentionally kept visible-but-flagged.
- **C-io_common (v1 C1)** (session 56): new `code/io_common.py` (175 lines, 4 pillars + frozen-recipe constants): path resolver `LLTB1_HOME/DATA/VENV_PY` (no hardcoded username); sentinel constants; `keep_or_nan` helper unifying 2 inline masks; `write_geotiff` extracted; `AREA_MIN_PER_RUNG` dict identity-preserved (same object). 6 callers refactored, 2 hardcoded `/home/frostflux/...` paths removed. 12 new tests; suite **89 → 101**.
- **C5 SUPERSEDED banners** (session 55): docstring banners on `pu_learning_baseline.py` + `pu_learning_on_registry.py`; `repair_registry_v1.py` deliberately NOT touched (PROVENANCE row 168 canonical, ships in E3). Convention note in `findings.md`.
- **B1–B5 cluster tail** (session 57): `registry_io` gains `SCHEMA_COLUMNS` (15) + `RegistrySchemaError` + `validate_registry(strict)` + `write_registry(df, path, comment_header)` with raw-parse attrs (round-trip **BYTE-IDENTICAL** — md5 `a60fb521…` reproduced from own parse; independent verifier confirmed). Structured-flags sidecar `candidate_registry_flags.csv` (278 rows, 14/9/21/1 partition, 161/117, `is_rung_duplicate=0` — supersession resolves all multi-rung copies; scope note distinguishes from papers' row-level 278→117 / 45→21 counts). B5 verdict proven executable via `test_registry_anchors.py` — **278/278 rows resolve to 54 `pair_results`** on `(dtm, rung_m)`. Suite **101 → 124**.
- **Misc** (sessions 53/54): `__main__` guard refactor for `explore_indian_tunnel.py` (canonical preflight_clouds.png `ea376b2f…` intact; CLI byte-identical pre/post, sha `4ed3c058…`); PROVENANCE_INDEX row 47 notes-column pointer to `findings.md ## data-quality — session 52`.

## 6. Protocol quality (NEW — session 58 was the first formal recheck)

- **State integrity at HEAD: ALL PASS** (frozen registry md5 unchanged; deposit CHECKSUMS 10/10; MANIFEST sidecar sha verified `1c884a1e…`; PROVENANCE row-47 pointer present; row-48 finite-ghost annotation; suite 124 green).
- **Retro-skeptic on findings blocks 51/52/57** (protocol gap closed): session-51 SOUND-with-wording (counts reproduced exactly 37/31; mixed provenance decisively confirmed); session-52 **UNSOUND framing corrected** — 85,304 ">100 m" points decompose as **85,273 real swath-edge geometry** in (100, 1000] (median 102.3 m — a 65×125 m scanner-frame site legitimately extends past 100 m) + the same 31 ghosts (old loader dropped only the 31, not all 85,304); session-57 SOUND-with-wording (117/161/45→21 reproduced; `unique_key` is root-primary not 3-dp string). New disclosure: PROVENANCE row 48's registration consumed the finite-ghost npz copy as reference — clamped by `coarse_search` `np.clip`, 31/60.9M points, negligible.
- **Vault catch-up** (sessions 26–57, 32 atomic notes written): `sessions/session_26.md` … `session_57.md` (one per CHANGELOG session, format matching `session_25.md`); `00_HOME.md` refreshed (Paper 1 → v2.1, Paper 2 → v3.3-draft, last-touched → session 58, "v2-plan autonomous queue exhausted" line added). Applied via orchestrator bash under the space-in-path permission gap (session-44 B7 precedent).
- **Process deviations logged (no action)**: (a) commit `0721854` body contains an elided absolute path (`/home/frostflux/...`) violating the `01_WORKSPACE/`-prefix rule — logged, no history rewrite (rewrite remedy is reserved for cost-phrase violations); (b) sessions 49–56 CHANGELOG entries + commits applied by orchestrator directly rather than via archivist dispatch (established in-project precedent, outcome-verified).

## 7. NAC reclassification (R3 adds; probed session 59)

- Session-49 "blocked" diagnosis was wrong-URL: `s3://lroc-eda-nac/` does not exist (HTTP 404); LROC serves via WMS, not a public S3 mirror.
- **Direct WMS probes session 59** (cheap, ~25 KB total, $0, no GPU):

  | URL | HTTP | Notes |
  |---|---|---|
  | `https://wms.lroc.asu.edu/lroc/` | 302 | root, alive |
  | `https://wms.lroc.asu.edu/lroc/rdr_product_select?product_id=M104203891S` | 302 → 23,154 B HTML | real RDR product page |
  | `https://wms.lroc.asu.edu/lroc/dtm_product_select?dtm_id=LDAM_NAC_DTM_M104203891_25CM` | 1,722 B | DTM archive endpoint responds |
  | `https://pds.nasa.gov/ds-view/pds/viewProfile.jsp?dsid=LRO-L-LROC-2-EDR-V1.0` | 200 | PDS archive alive |
  | `https://s3.us-west-2.amazonaws.com/lroc-eda-nac/` | 404 | the wrong-URL origin of session-49's "blocked" claim |

- The path is **open at the URL level** — `aws` CLI is not installed on this host (no need; WMS is the real endpoint).
- What was (and remains) missing is the fetch pipeline: a NAC fetch script that issues the WMS product query, parses the response, georeferences/clip-extracts a small region around Mare Tranquillitatis Pit, and lands a 2–5 m DTM at the canonical `data/outputs/wp1_lla/TRANQPIT1/` location. That pipeline is the WP0 first-reproduction goal (master plan §M0).
- **HIGH-confidence: reclassified from BLOCKED to MEDIUM-OPEN (session 59) -> HIGH-OPEN (session 60 verified-fetch, sha256 `bb2c525c1ad622bc185c4e7c13a3febcf99a4780d83c8e77a88dc3cabb53c571`)**; HIGH is strictly with respect to "WMS RDR chain is fetchable + exposes the metadata needed for the next fetch (PDS dataset `LRO-L-LROC-5-RDR-V1.0` + LROLRC bundle `LROLRC_2001` + `view_rdr_product` IMG-download link one hop deeper)" — the IMG byte-signature verification remains deferred to the user-gated NAC fetch pipeline (§11(b)). Pending user call to start the pipeline (Tier-0 budget eligible; would be the first WP0 reproduction since cycle 2 close). Full observation logged in `findings.md ## data-acquisition — session 60` (session 59 entry retained for provenance).

## 8. Remaining open items

- **D3 LOO cross-validation** — deliberately deferred (frozen-science-adjacent; would touch the FP accounting). Re-opening moves the frozen science; user-gated.
- **NAC fetch pipeline** — reclassified MEDIUM-OPEN (see §7), pending user call.
- **User-gated queue** (unchanged from R2 except as marked):
  - **E3 Zenodo deposit** (`data/zenodo_deposit_v1.0/`, CHECKSUMS 10/10 verified) — licence CC-BY-4.0 / MIT confirm, creator list, token + upload go, optional ADR D6 wording revisit, optional ORCID.
  - **R1 draft commit** — `plans/2026-08-21_R1_Roadmap_draft.md` still untracked (git status confirmed); lineage note ready.
  - **Journal submissions** — Paper 1 v2.1 / Paper 2 v3.3 (verifier PASS-with-notes on both); user owns journal-portal access.
  - **CI activation** — user-approved root-`.github/` exception; `admin/ci/ci.yml` + README staged.
  - **D2 visual-verdict capture** — eyes-on for FECUNPIT 3 + TRANQPIT1 3 + INGENIIPIT 21 candidates (session 24 backlog); verdicts never persisted.
  - **D5 Hetzner rental launch** — Hetzner kit complete (12 files, DO-NOT-RUN banners, session 31); unlocks Cycles 3–5 + random-mare survey.
  - **Zotero attaches** — Kelahan 2026 (arXiv:2608.09350), Watson & Baldini 2024 (*Icarus* 411:115952), ESSA/Le Corre 2025 (*Icarus*), +3 genre refs (Moonstone 2607.03644, Mars-Bench 2510.24010, StereoLunar 2510.18172). Pending user/local-Zotero access.
  - **E2 skill decision** — vault-mirror / conventions-skill exposure still untracked (per session 43 finding).
  - **Laurier/ASU pit-database audit item** — external (prior-art matrix audit), separate decision.

## 9. Spend ledger

**$0 over 31 sessions** (sessions 1–58). All probes Tier-0 or HTTP-only. Tier-1 (rented CPU/GPU) untouched; Tier-2 (paid GPU) untouched. No user-approved cost trigger fired. Ledger at `01_WORKSPACE/admin/budget.md`.

## 10. Test discipline

**124 passed, 6 warnings, 128.49 s on HEAD `c5be2a2` (orchestrator fresh pytest session 59; earlier 8-warning / 179-s runs referenced verifier scripts and a wider warning surface — suite count identical).**
- Smoke pins (full precision): F1 `0.39160839160839167 / 0.0 / 0.8` per rung; fusion AUC **0.990**; tol 1e-6 (`tests/test_smoke.py`).
- Real-data E2E pin: `Fieg_0.5m.npz → sag_detect` → f1 **`0.029746281714785657`** tol 1e-5 (`tests/test_e2e_fieg.py`).
- Pin guards: `tests/test_io_common.py` asserts `e2e.PIN_F1_SLOPE == 0.029746281714785657`, `smk.SMOKE_F1[0.5] == 0.39160839160839167`, `smk.SMOKE_FUSION_AUC == 0.990`.
- Verifier scripts: `verify_v02_f32dir_and_filter.py` **PASS: 21/21 (ALL OK)**; `verify_v03_slope_mask.py` 15/15; `verify_v04_tune_slope.py` 11/11.
- f1 pins **byte-identical** through sentinel hardening (session 51) + `io_common` refactor (session 56).

## 11. Recommendation for user

The autonomous engineering program has reached a natural completion point. All frozen-science, all paper-claim integrity, all v2-plan engineering boxes are done. Suggested next actions (pick any order, no urgency):

- (a) **commit R1 draft** — `plans/2026-08-21_R1_Roadmap_draft.md` still untracked; one commit with lineage note.
- (b) **authorise NAC fetch pipeline** — Tier-0; first WP0 reproduction since cycle 2; would deliver the Mare Tranquillitatis pit DTM end-to-end through the v0.2 ladder.
- (c) **authorise D3 LOO reopen** — frozen science will move (FP accounting will change); required for transfer-generalization criterion claim in Paper 1 §5.4.
- (d) **decide E3 Zenodo deposit** — licence (CC-BY-4.0 / MIT), creator list, token + upload go; package is staged and verified.
- (e) **submit Paper 1 v2.1 / Paper 2 v3.3** — verifier PASS-with-notes on both; user owns journal-portal access and editor list.

---

## 12. Reproducibility appendix

- **Code:** `01_WORKSPACE/code/` (LLTB-1 v0.5.1 CC-filter; v0.2 ladder; PU learning groupsplit v1; `io_common.py` v1 C1; `registry_io.py` with `SCHEMA_COLUMNS` + `validate_registry` + `write_registry`).
- **Data manifests:** `01_WORKSPACE/data/MANIFEST.md`, `01_WORKSPACE/data/outputs/PROVENANCE_INDEX.md` (186 lines, 160+ artifacts).
- **Zenodo deposit v1.0** (`data/zenodo_deposit_v1.0/`): 10 files (CHECKSUMS 10/10 verified) — `candidate_registry.csv`, `PROVENANCE_INDEX.md`, `METHODS.md`, `transfer_summary.json`, `unique_accounting_2026-09-07.json`, `pu_learning_groupsplit_2026-09-09.json`, plus 4 protocol scripts.
- **Test suite:** `01_WORKSPACE/code/tests/` — 124 tests, smoke + E2E pins byte-identical.
- **Frozen registry:** md5 `a60fb52152e33f37e9052434ad026a6e` (`data/candidate_registry.csv`); sidecar `data/candidate_registry_flags.csv` md5 `88da3ec5c92d7de319aac416068e0402`.
- **Sentinel constants:** `code/io_common.py` (`SENTINEL_MAX_M=1e6`, `WARN_MAX_M=100.0`, `ATTR_SENTINEL_MAX=1e3`, `F32_NODATA=-9999.0`).
- **Verifier scripts:** `01_WORKSPACE/admin/verification_evidence/scripts/verify_v02_f32dir_and_filter.py` (21/21), `verify_v03_slope_mask.py` (15/15), `verify_v04_tune_slope.py` (11/11).

## 13. Version lineage note

- **R1** = `plans/2026-08-21_R1_Roadmap_draft.md` — untracked draft; never committed; user-gated.
- **R2** = `plans/2026-09-12_R2_Status_Report.md` — sessions 47 snapshot (71 lines).
- **R3** (this file) — terminal state at HEAD `c5be2a2`, sessions 48–58 delta. Live status doc.
- R3 is the last R-numbered status report: the v2-plan autonomous queue is exhausted and the remaining items are user-gated or external. Future changes will be tracked via CHANGELOG + the B10-status ticks, not via R-numbered reports.