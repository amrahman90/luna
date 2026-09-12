# Session 58 — vault-hygiene catch-up PENDING APPLY (archivist → orchestrator)

**Why pending:** the archivist's edit/write tools are permission-blocked on
`01_WORKSPACE/Lunar Lavatube knowledge/` — the allow rule exists but fails to
match the space-containing path (known opencode.json gap, first hit in session
44 / B7; same workaround used then: content prepared here, applied via
orchestrator bash). Everything below is FINAL content; apply mechanically.

## Apply instructions

1. `00_HOME.md` — apply the three replacements in §A (exact old → new strings).
2. Create 32 files `sessions/session_26.md` … `sessions/session_57.md` from
   §B — each block's `### →` header gives the target filename; the note body
   is everything after that header line (do not include the `### →` line or
   the surrounding `---` rules).
3. Format matches `sessions/session_25.md` / `session_24.md` house style:
   heading `# Session <NN> — <date>`, tags line, Headline, 3–6 bullets,
   MOC + CHANGELOG wikilinks.

## A. 00_HOME.md replacements

### A1 — Paper lines (replace the single Paper 1 line)

OLD:

```
- **Paper 1:** **v2.0 submission-ready** (IMRaD rewrite session 38; A6 assets v2.0 session 39; ninth reference Kelahan et al. 2026 session 41)
```

NEW:

```
- **Paper 1:** **v2.1 submission-ready** (IMRaD v2.0 session 38; v2.1 reference audit + method refs session 50)
- **Paper 2:** **v3.3-draft** (D4 test-bed reframe session 46; v3.3 submission polish session 49; 18 refs resolver-verified)
```

### A2 — v2-plan queue line (insert immediately AFTER the `Spend:` line)

```
- **v2-plan queue:** autonomous queue exhausted (sessions 51–57: sentinel hardening, io_common, B-cluster closed); remaining: D3 (deferred), NAC EDR re-probes (blocked), user-gated items
```

### A3 — footer (replace verbatim)

OLD:

```
_Entry MOC for the LUNARVOID Obsidian vault. Last touched: 2026-09-11 (B7 audit-hygiene refresh: post-B1 registry counts, gate statuses, Paper 1 v2.0 / PU v5 / skeptic F20)._
```

NEW:

```
_Entry MOC for the LUNARVOID Obsidian vault. Last touched: 2026-09-12 (session 58: retro-skeptic on 51/52/57; vault catch-up sessions 26–57; Paper 1 v2.1 / Paper 2 v3.3-draft)._
```

Registry/gate lines are already current — deliberately NOT touched.

## B. Session notes (32 files)

### → sessions/session_26.md

# Session 26 — 2026-08-23

> Tags: #session #cycle-1 #mare #registry #skeptic

**Headline:** P3.1c Cycle 1 close — GRUITHUIS17/GRUITHMARE2/MARIUSCONE scored; FP 6.06 → 4.28 per 10⁴ km².

- **What:** `transfer_apply.py` over 3 newly-Frangi-scored NAC DTMs → 18 new registry rows (10 GRUITHMARE2 + 6 GRUITHUIS17 + 2 MARIUSCONE), all below-local-floor, 0 new FPs. Skeptic fall-back annotation per site: GRUITHMARE2 (10 rows) + MARIUSCONE (2 rows) "deep-pit low-vesselness"; GRUITHUIS17 passes vesselness (frangi@score 0.0424 ≥ 0.02).
- **Numbers:** registry 257 → 275 LV- rows; area 14,840.27 → 21,046.16 km²; FP 6.06 → 4.28 per 10⁴ km² (numerator fixed at 9, denominator grew); rung 4 89→98, rung 5 91→100 candidates; smoke F1 0.392/0/0.800, fusion AUC 0.990; $0.
- **Deliverables:** registry rows + `transfer_summary.json` merge; scope banner N=21/649 (20 with score rasters, 1 skipped = TYCHOPK); MANIFEST unchanged (no raw acquisitions — rasters generated session 25).
- **Gotchas:** user reminder "FP rate stays at 6.06" was mathematically incorrect when adding 6,205.89 km² with 0 new FPs — the decrease is correct per P3.1c protocol.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_27.md

# Session 27 — 2026-08-23

> Tags: #session #cycle-2 #highland #registry

**Headline:** Cycle 2 close — TYCHOPK scored; FP 4.28 → 3.74 [1.71, 7.10] per 10⁴ km²; 21/21 DTMs with score rasters.

- **What:** TYCHOPK Frangi score rasters at 2+4+5 m (no tile-based fallback; 6.8 GiB Python peak on the 2 m rung); 3 rows annotated terrain_extrapolation risk (central-peak relief, below-local-floor, not independent void candidates — frangi@score 0.0185 borderline but depth 18.35 m shallow, NOT ≥ 100 m). Two `score_raster_gen.py` bug fixes: true fractional rasterio rebin (2→5 m = 2.5×, not rounded 2×) and depth output on the requested rung grid instead of the 5000-px Frangi grid.
- **Numbers:** wall 478.9 s (2 m: 260.3 / 4 m: 119.9 / 5 m: 98.7); depth_max 234 m; frangi_max 0.53; score_max 0.34; area +3,016.80 → 24,062.96 km²; n_fp unchanged at 9 → FP 3.74 [1.71, 7.10]; smoke PASS; $0.
- **Deliverables:** `~/lunarvoid/data/outputs/wp2_sag/score_rasters/TYCHOPK/{score,depth,frangi}_{2,4,5}m.tif` (296 MiB); registry 275+3 (TYCHOPK only); `transfer_summary.json` per-DTM entry.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_28.md

# Session 28 — 2026-08-23

> Tags: #session #gate-g2 #deferred #cycle-6

**Headline:** Cycle 6 close — G2' row 10 flipped DEFERRED-DTM-gap-EXPANDED → DEFERRED-DTM-gap-PARTIAL; Cycles 3–5 deferred indefinitely.

- **What:** G2 report §3 verdict table, §5 risk list, §6 Step 2 (a)/(c) annotations updated (paper-writer + orchestrator); `papers/gate_reports/` and `plans/` mirrors byte-identical (diff-verified).
- **Numbers:** §4 claims/evidence stays as the G2 close snapshot (44→257, FP 6.06, 21 DTMs) — the substantive update flowed into Paper 1 v1.0 (Cycle 7); cost $0.
- **Gotchas:** Cycles 3–5 blocked: PDS S3 has NAC_DTM RDR but NAC_EDR 404s at every legacy endpoint; Cycle 4 depends on 3, Cycle 5 on 4. G2 still DRAFT-FOR-REVIEW pending user decision. Vault updates queued (TYCHOPK + MARIUSCONE/GRUITHMARE2/GRUITHUIS17 site notes, registry 257→278, FP 6.06→3.74).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_29.md

# Session 29 — 2026-08-23

> Tags: #session #paper-1 #cycle-7

**Headline:** Cycle 7 close — Paper 1 v1.0 SUBMISSION-READY (430 → 681 lines), modulo G2 user pass + Zotero attach.

- **What:** "Detectability limits for lava tube roof signatures in orbital topography: the LLTB-1 calibrated benchmark" — all sections promoted v0.2 → v1.0 incl. new §3.3.1 Cycles 1-2 update and Table 1a lunar aggregate; new deep-pit low-vesselness annotation rule (skeptic-authored). Verifier PASS-with-notes; skeptic SOUND-with-objections → 4 language fixes (§4.1 km² arithmetic; §6 "278 tier-C rows" framing; §3.3.1 "closed locally"; ~281 catalogued per Wagner & Robinson 2021).
- **Numbers:** registry 257 → 278 (+21); aggregate FP 6.06 → 3.74 [1.71, 7.10] per 10⁴ km² (calibration-context); 10 references author-year; verification greps: 11 "Cycles 1-2", 8 "calibration-context", 5 "Tranquillitatis radar conduit", 4 "3.74 [1.71, 7.10]", 0 forbidden phrases.
- **Gotchas:** 10/10 references unverified (Zotero offline; attach at next opportunity); G2 PARTIAL until user pass; target venue RSE / ISPRS Journal.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_30.md

# Session 30 — 2026-08-23

> Tags: #session #housekeeping #vault #methods

**Headline:** Post-Cycle 6 housekeeping rounds 1–6 — vault atomic notes, METHODS back-port, roadmap ticks, claim-discipline audit clean.

- **What:** Round 1 vault notes (gates/G2.md row-10 flip; Calibration-context FP 6.06 → 3.74 [1.71, 7.10] over 24,063 km²; NEW concepts/Deep-pit low-vesselness.md; artifacts/Candidate registry 257 → 278 with 12 deep-pit annotations; 4 site notes via BACKLOG_SITE_HINTS). Round 2: METHODS.md deep-pit rule back-port (710 → 801 lines). Round 3: outline.md v1.0 additions + Next_Tasks roadmap ticks (P5.5). Round 4: bibliography — Zotero MCP still offline. Round 5: NAC browse thumbnails BLOCKED (S3 = DTM RDR only; QuickMap lacks API) — manual procedure documented. Round 6: smoke + audits.
- **Numbers:** claim-discipline audit 137 .md files, 0 violations (3 meta-discussion false positives); smoke F1 0.392/0/0.800 + AUC 0.990; 278 tier-C rows; $0.
- **Gotchas:** 5th commit of the local Tier-1 plan lineage (Cycles 1, 2, 6, 7 + housekeeping).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_31.md

# Session 31 — 2026-08-23

> Tags: #session #housekeeping #paper-1 #release-note

**Headline:** Rounds 7–10 housekeeping — ZEROCOST roadmap sync, NAC EDR URL research backlog note, Paper 1 v1.0 release note.

- **What:** Round 7: ZEROCOST roadmap updated (G2 row PARTIAL note + Cycles 1-2 outcomes + Cycles 3-5 BLOCKED). Rounds 8-9: vault backlog note `backlog/PDS NAC_EDR URL research.md` (options A–E for resuming Cycles 3-5) preserving context for future sessions. Round 10: Paper 1 v1.0 release note `01_WORKSPACE/notes/2026-08-23_Paper1_v1.0_release_note.md` (~150 lines: cycles summary, paper state, pending actions). All committed at $0.
- **Numbers:** no numeric results this session; standing by for user-driven G2 pass + visual inspection + Zotero attach + submission.
- **Gotchas:** CHANGELOG numbering quirk — a second same-day entry ("complete all" autonomous surface exhaustion phase 2: opencode.json patch, 11-commit push, G2 PARTIAL honestly retained, playwright visual inspection blocked) is ALSO labelled session 31 in the appended CHANGELOG tail and is already mirrored in this vault as [[session_25]].

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_32.md

# Session 32 — 2026-08-28

> Tags: #session #pu-learning #visual-inspection #wp3 #curriculum

**Headline:** WP3 PU baseline on the 278-row registry (F1 0.857 / AUC 0.897 in 0.18 s) + user G2 confirmation + visual-inspection helper upgrade.

- **What:** user reported visual inspection COMPLETE for all 27 candidates (3 FECUNPIT + 24 across 4 clusters) — per-cluster verdicts NOT captured on disk (audit note in findings.md with 3 capture paths; no tier-B auto-promotions). Helper HTML upgraded (zoom 9-14 → 12-14; 6 NAC thumbnails via Playwright; QuickMap v3 ignores lat/lon/zoom URL params — use the in-page search combobox; onerror fallback). G2 FINAL-PASSED (applied 2026-08-24) confirmed by user "pass g2". NAC EDR retry: 6 SKIP_EXISTS / 4 URL_NOT_FOUND; pds.mcp.nasa.gov flipped 404 → 403.
- **Numbers:** WP3 v1 PU: pulearn Elkanoto + LogisticRegression, 5 registry-native features, 70/30 split seed 42 → F1 0.857 / P 0.900 / R 0.818 / AUC 0.897; 34 positives vs 244 unlabeled; 0.18 s laptop CPU; a ranking, not detection.
- **Deliverables:** `data/outputs/wp5_fusion/pu_learning_registry_baseline.json`; `admin/visual_inspection_helper.html`; `data/wp8_stereo/retry_status_2026-08-28.md`; curriculum Phase 3 (lessons 0014-0019 + I1-I15 cheatsheet; 19/35).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_33.md

# Session 33 — 2026-08-28

> Tags: #session #paper-1 #references #curriculum

**Headline:** Paper 1 v1.2 — reference audit: 2 unverifiable refs dropped, remaining 8 all DOI-confirmed.

- **What:** user verified 6 Zotero-attached references; orchestrator audited DOIs. van Ewijk 2011 DOI resolved to a DIFFERENT paper → dropped (Reichenzeller 2026 sole VCI anchor). Chwala 2024 not in Crossref/arXiv/Scholar → dropped (stability bounds now Blair 2017 + Theinat 2018, "two anchors"). Carrer 2024 placeholder → real DOI 10.1038/s41550-024-02302-y; Blair 2017 → Icarus 282, 47-55; Theinat → 2018 AIAA 2018-5185; Le Corre 2025 initial + article # + DOI fixed. Companion docs (outline, cover letter, referee template) mirrored.
- **Numbers:** 8 references (was 10), all Crossref-confirmed; in-text Chwala mentions 2 → 0; curriculum Phase 4 complete (lessons 0020-0024; 24/35, 69%); commits `1310d3c` + `5596c62`.
- **Gotchas:** Zotero local API needs Settings → Advanced → "Allow other applications…" toggle (done this session).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_34.md

# Session 34 — 2026-09-04

> Tags: #session #paper-2 #pu-learning #curriculum #submission-package

**Headline:** Autonomous local-only surface exhausted — curriculum 35/35, Paper 2 draft, PU v2 (F1 0.909), LLTB-1 v0.2 note, submission package complete.

- **What:** curriculum Phases 5-7 built (~54 files, ~25K lines, gitignored: photogrammetry, writing & publication, project operations). Paper 2 draft `papers/paper2_inference_main.md` (945 lines, 14 refs, Icarus/PSS target). WP3 PU v2 `pu_learning_extended.py` (19 features). LLTB-1 v0.2 release note (connected-component filter integration test). NAC EDR re-test + UA-bypass probe FALSIFIED — migration diagnosis (old path 403, new path 404, early volumes migrated). Submission package finalized: GA PNG 1280×720 + `suggested_reviewers.md` (6 slots, cite-exclusion enforced).
- **Numbers:** PU v2 F1 0.857 → 0.909, AUC 0.897 → 0.931, 0.04 s; top importance log_sag_amp_m (+1.39); TRANSPIT1@5m thr=0 CC kill 23134→13311 (42.1%), catalogued pit survives; commit `96bd53a`.
- **Gotchas:** remaining items all user actions: submit Paper 1, Hetzner rental, inspection verdicts, reviewer emails.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_35.md

# Session 35 — 2026-09-04

> Tags: #session #audit #plan #phase-0

**Headline:** Dual-audit merge → Next-Level Plan v2 — Hermes 42-finding audit merged with the v1 audit; new Phase 0 correctness gate before Paper 1 submission.

- **What:** Hermes independent whole-project audit landed (`notes/2026-09-04_AUDIT_REVIEW.md`, 1,365 lines; 6 HIGH / 15 MED / 15 LOW / 4 DIR; 3 subagents + RETRACTED log). 4/4 spot-checked HIGHs confirmed: Frangi float64 upcast missing, integer-factor rebin (5 m rung → 4 m grid), Frangi at source posting, supply-chain TOFU + requirements missing 8 imports. Evidence-integrity: hardcoded `synthetic_smoke_test: passed` literal in `v0_2_integration_test.json`. Plan v2 written with 5 adjudications; v1 plan SUPERSEDED with banner.
- **Numbers:** Phase 0 blocks submission until parity tables vs frozen evidence (T5 ±5%).
- **Gotchas:** sessions 32-34 CHANGELOG entries sit at file bottom vs newest-first convention — folded into the B10 sweep.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_36.md

# Session 36 — 2026-09-04

> Tags: #session #phase-0 #hardening #parity

**Headline:** Plan v2 execution — Phase 0 correctness triage 7/7 PARITY-PASS + Phase C engineering hardening + Phase B ADRs.

- **What:** Phase 0: 0.1 requirements regen (53 pkgs, +8 missing imports); 0.2 Frangi float64 upcast; 0.3 fractional rebin helper `wp2_sag/transfer/_rebin.py`; 0.4 Frangi at rung posting; 0.5 measured smoke counts 66/4/2 replace fabricated 96/5/1 (kill_ratio 0.421 reproduces frozen 42%); 0.6 NaN-mask Frangi; 0.7 G0' erratum. Phase C: C8 sha-pinned extract_rar, C9 shared `_crs.py`, C10 shared `_http.py`, C12 commit-msg guard, C13 registry_io + LEAK assert, C14 roc_auc fix, C15-1..4. Phase B: B9 ADRs D3–D6, B6 regen_site_notes fix, A6 Paper-2 citation fix, E1 untracked-IP backup tarball.
- **Numbers:** parity report `admin/verification_evidence/2026-09-04_phase0_parity_report.md` 7/7 PASS; TRANQPIT1 floor 3.736 → 3.893 m (+4.20%, in tolerance); smoke byte-identical.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_37.md

# Session 37 — 2026-09-06

> Tags: #session #phase-0 #parity #reconciliation

**Headline:** v2 re-evaluation — parallel Hermes session discovered + Phase 0.1 redundant refresh.

- **What:** a 2026-09-04 Hermes-side session had already executed most of Plan v2 Phase 0 + parts of B/C/E (commits c7a7820, 6ec4be4, d80039e, 2b10a98, 1d5d8e3) — reconciled, not repeated. 4 DRIFT DTMs (GRUITHUIS17, KINGCRATER2/3/4) are random-mare sites outside the frozen TRANQPIT1 calibration set → headline FP unaffected; HIGH-3 cascade deferred to Tier-1. `code/setup/requirements.txt` refreshed 2026-09-06 (59 lines; fresh-venv PASS with pulearn/numpy<2.5 quirk documented). C12/C14/B9 reconciliation recorded done; execution-status checkbox block added to Plan v2.
- **Numbers:** parity 7/7 PARITY-PASS; smoke F1 0.392/0/0.800 + AUC 0.990 — exact match to frozen.
- **Gotchas:** HIGH-6 (requirements missing 8 imports) was true at initial commit and already remediated by c7a7820 — the 09-06 file is a refresh only.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_38.md

# Session 38 — 2026-09-07

> Tags: #session #registry #paper-1 #accounting

**Headline:** B1 registry repair (117 unique / 161 SUPERSEDED) + A1 Paper 1 v2.0 IMRaD + A2 unique-feature accounting 2.08 [0.67, 4.85].

- **What:** B1: 15 malformed rows fixed, 3 methods="C" → morphometry, 97 cross-rung duplicate groups → 161 SUPERSEDED with `superseded_by` (finest rung primary, earliest-id tie-break); idempotent; one-shot backup (MANIFEST row added). A1: Paper 1 IMRaD rewrite 729 → 297 lines / 8,281 words; A3/A4/A5 honesty fixes; skeptic objections all fixed. A2: `code/wp2_sag/transfer/unique_accounting.py` + evidence JSON (byte-deterministic; row-based regression 1e-9; referential integrity 161/161).
- **Numbers:** 278 = 117 ACTIVE + 161 SUPERSEDED; 45 above-floor = 21 primaries + 24 superseded; unique (B1 key, ~30 m): 6 TP + 5 FP + 9 ring + 1 funnel → 2.08 [0.67, 4.85] per 10⁴ km²; TRANQPIT1 geometry corrected to 16.5 / 132.8 m (two structures, ground-truthed by two independent haversine computations).
- **Gotchas:** the previously circulating unique-FP estimate "6 → 2.49 [0.92, 5.43]" was WRONG under B1's actual key; key is rounding-boundary-fragile — quote only with the key stated.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_39.md

# Session 39 — 2026-09-09

> Tags: #session #paper-1 #submission-assets

**Headline:** A6 submission-asset regeneration — referee template + graphical-abstract plan rebuilt v2.0-consistent; GA PNG deterministic.

- **What:** `referee_response_template.md` 285 → 246 lines (v2.0 preamble, 12-row frozen claim table with artifact paths, 6 response skeletons incl. row-vs-unique accounting and 16.5/132.8 m geometry). `graphical_abstract_plan.md` 224 → 169 lines (single-source 20-slot string table). `code/wp1_paper/generate_graphical_abstract.py` rebuilt to the 4-panel plan (retry 2 after verifier FAIL: stale "30 cells", "6 NASA analog sites", overstated "≥ 4 m sag" all purged).
- **Numbers:** PNG deterministic 1280×720, 108.3 KB, byte-identical double render (sha256 52a387e2…), quadrant-content assert; zero stale hits (82/226, "278 candidates", bare "14 candidates").
- **Deliverables:** Paper 1 package fully v2.0-consistent (main, outline, highlights, cover letter, referee template, GA plan, GA PNG, reviewers list).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_40.md

# Session 40 — 2026-09-10

> Tags: #session #pu-learning #d1 #leakage

**Headline:** D1 PU evaluation redesign (full chain) — leakage-corrected groupsplit; morphometric-only F1 0.824 / AUC 0.930; skeptic F15–F20 closed → SOUND.

- **What:** `code/wp5_fusion/pu_learning_groupsplit.py` + evidence JSON (deterministic sha 596a74f8…, 2×117 self-checked OOF arrays). Leak fixes: 161 SUPERSEDED excluded (117 ACTIVE: 15 P / 102 U); leave-one-DTM-out 21 folds; train-fold-only imputation + scaling. Old v2 random-split numbers (F1 0.909 / AUC 0.931) annotated leak-inflated. Skeptic-driven ablation dropped 4 annotation-derived flags → headline run B morphometric-only (15 features). Paper 2 §3.3 rewritten; abstract closes "a small-n feasibility result (15 positives), not classifier validation".
- **Numbers:** run B F1 0.824 / P 0.737 / R 14/15 / AUC 0.930; cluster-bootstrap 95% CIs F1 [0.35, 0.98], AUC [0.49, 1.00]; LOIO-INGENIIPIT F1 0.571 / AUC 0.790; threshold 0.824@0.5 / 0.839@1.0 / 0.846@1.5; MARIUSPIT01 r001 (I14 funnel failure) recurs at ~2.2e-72.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_41.md

# Session 41 — 2026-09-10

> Tags: #session #paper-1 #paper-2 #literature #recycling

**Headline:** D1-LOW run C + pre-submission literature sweep (Kelahan 2026 added as ninth ref) + A7 text-recycling pass (overlap → 3.13–3.29%).

- **What:** run C `rung_cm` ablation (14 features) F1 0.800, 5/117 decision flips vs B, I14 failure unmoved; degenerate-resample rule documented. Literature sweep 2025-01-01 → 2026-09-10 (3 query families; memo `notes/2026-09-10_presubmission_literature_sweep.md`): Kelahan et al. 2026 (arXiv:2608.09350, Beta-VAE anomaly search) added — complementary not competing; no 2025+ radar/SKS lunar subsurface work. A7 rewrites of shared prose; A7b stale "82/278" claim provenance-solved (82 = atlas-pit population overlapping NAC DTMs; registry 278 is a coincidental second 278).
- **Numbers:** shared-8-gram overlap 4.10–4.26% → 3.13–3.29%; remaining spans all class-(b) (8 refs, 4× sentinel statistic strings, 3 data-table rows); zero prose spans ≥20 tokens.
- **Gotchas:** "MARIUSPIT01 r001" is ambiguous across rungs — always qualify with rung.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_42.md

# Session 42 — 2026-09-11

> Tags: #session #provenance #methods #manifest

**Headline:** B2/B3/B4 — METHODS catch-up (801 → 943), PROVENANCE_INDEX sidecar (160 artifacts, 0 unattributable), MANIFEST outputs-tree.

- **What:** B3: METHODS.md pure append in house style (B1 registry repair; A2 unique accounting; D1 PU redesign v5 — 15+ numbers verified against evidence JSONs). B4: `data/outputs/PROVENANCE_INDEX.md` + deterministic builder `code/tools/build_provenance_index.py` (byte-identical double run; exclusions documented; ZERO in-place edits to cited artifacts). B2: MANIFEST "Derived outputs tree" section (11 rows + sidecar-provenance policy + cross-link).
- **Numbers:** 160 artifacts, 66 with cited-in links; cited shas preserved (registry md5 a60fb521…, groupsplit 3d360793…).
- **Gotchas:** B1–B5 cluster checkbox left unticked (no standalone MANIFEST line; session-42 precedent for deferred cluster ticks).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_43.md

# Session 43 — 2026-09-11

> Tags: #session #tests #ci #e2e

**Headline:** C4/C11/E4 — pytest scaffold (58 passed), real-data E2E fixture (Fieg pin), staged CI workflow.

- **What:** `code/tests/{conftest, test_smoke, test_verification_scripts, test_e2e_fieg}.py` + `code/pytest.ini` (strict markers, deterministic order, no-network autouse fixture). 5 ad-hoc verification scripts ported as 46 parametrized checks that RE-EXECUTE (not stored-JSON asserts). C11: `~/lunarvoid/data/lltb1/Fieg/Fieg_0.5m.npz` E2E with pinned `f1_test_slope = 0.029746281714785657` (tol 1e-5; auto-skip when data absent). E4: `admin/ci/ci.yml` + README — activation requires copying to `<root>/.github/workflows/`, a user-approved AGENTS.md root exception.
- **Numbers:** 58 passed / 0 failed locally (×2 identical); 45 passed + 13 reasoned skips with data hidden; smoke pins full precision (0.39160839160839167).
- **Gotchas:** bare-script CLI needs `PYTHONPATH=01_WORKSPACE/code` since the C9 `_crs` refactor; geo-coder write-denied on `admin/**` (allow-list) — ci files via bash per dispatch.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_44.md

# Session 44 — 2026-09-11

> Tags: #session #lltb1 #v0-5-1 #doc-hygiene

**Headline:** C3 CC-filter wired as LLTB-1 v0.5.1 (default OFF — no lift) + B7/B8/B11 doc hygiene.

- **What:** `sag_detect.py --cc-filter {off,on,auto}`; off-branch = v0.5 legacy path, 7/7 site parity within 2e-3, smoke exact pins; auto = per-rung AREA_MIN table + per-rung audit fields. B7: vault `00_HOME.md` refreshed (278 = 117 + 161; both FP accountings; gates FINAL-PASSED) — applied via orchestrator bash after the archivist hit the space-in-path permission gap (sidecar `notes/2026-09-11_B7_00_HOME_refresh_pending_apply.md` committed as provenance). B8: G1 mirror re-synced byte-identical (sha 5ad43dfb…). B11: findings.md +2 entries (Diviner GHRM 0.0-sentinel quirk; 3× band-passed sag-band-RMS criterion).
- **Numbers:** CC filter a no-op at 6/7 sites, −0.0028 F1 at IndianTunnel_NorthSurface → default OFF (confirms v0.2-era "documentation, not lift"); pytest 73.
- **Deliverables:** `data/outputs/wp1_detector/cc_filter_evaluation_v0_6.json`; `notes/2026-09-11_LLTB1_v0.5.1_release_note.md` (167 lines).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_45.md

# Session 45 — 2026-09-11

> Tags: #session #audit #exceptions #hardening

**Headline:** C7 silent-exception audit — 65 real `except` sites swept; 0 bare; 2 dangerous silences fixed; 26 silent-by-design markers.

- **What:** `wp3_fusion/evidence_layers.py` (GRAIL coefficient rows silently dropped on ValueError — gravity corruption now visible) and `wp4_diviner/sample_diviner_at_candidates.py` (registry rows silently dropped) now warn loudly on stderr with zero control-flow change. 26 `# silent by design: <reason>` markers added to load-bearing silences so future audits skip them.
- **Numbers:** 6 docstring false-positives excluded; 28 sites touched, 16 files, +42/−18; audit record `data/outputs/audit/silent_except_audit_2026-09-11.json` (65 site records); pytest 73, smoke byte-match 0.392/0/0.800 + AUC 0.990.
- **Gotchas:** with C7 done the C-track remainder was C6 only (closed session 47).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_46.md

# Session 46 — 2026-09-12

> Tags: #session #paper-2 #d4 #reframe

**Headline:** D4 Paper 2 benchmark → test-bed reframe; v3.0-draft-reframe → v3.1-draft (1149 → 1434 lines).

- **What:** title "An annotated test-bed registry and leakage-corrected evaluation protocol for lunar void-candidate inference from meter-scale orbital terrain data"; novelty narrowed per skeptic V1 (ESSA/Le Corre 2025 already released an annotated detection dataset). Genre positioning verified via arXiv + DOI resolver: Moonstone (2607.03644), Mars-Bench (2510.24010), StereoLunar (2510.18172), Watson & Baldini 2024 (Icarus 411:115952, Mars-domain). Skeptic fixes V2–V6b applied: n_tier_B=3 quoted with dated downgrade, ASU web-terms vs PDS licence caveat, leak renumbering, 233-below-floor as deliberate labelled output.
- **Numbers:** references 14 → 18; 0 unqualified "first annotated benchmark"; §4.6 byte-identical; independent registry recount 278 = 117 ACTIVE + 161 SUPERSEDED, all tier C.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_47.md

# Session 47 — 2026-09-12

> Tags: #session #c6 #run-cycle #zenodo #e3

**Headline:** C6 run_cycle chain with frozen-artifact guard + E3 Zenodo deposit PREP (upload user-gated).

- **What:** thin subprocess chain `floors → score → transfer → accounting` per site (ADR D6 scripts-not-package); dry-run; pre-run snapshot + per-step re-hash + byte-restore-on-change over the frozen evidence set, proven on a real TRANQPIT1 run (8 shas byte-identical; one canonical write blocked and restored, incident in the run JSON). Retry-1 incident: canonical transfer_summary + unique_accounting overwritten — restored byte-identical from git BEFORE commit. E3: licence audit memo `notes/2026-09-12_E3_licence_audit.md`; atlas question RESOLVED (registry labels trace to the PDS LUNAR_PIT_LOCATIONS shapefile, public domain, cite Wagner & Robinson 2021); deposit staged at `data/zenodo_deposit_v1.0/` (README + metadata + CHECKSUMS 10/10 + deposit/ ~0.6 MB).
- **Numbers:** aggregate reproduced exactly (278 candidates; FP 3.74 [1.71, 7.10]); pytest 73.
- **Gotchas:** 5 user decisions pending (licences CC-BY-4.0/MIT, creators, token/upload, ADR D6 wording, ORCID) — deposit NOT public without ①–③.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_48.md

# Session 48 — 2026-09-12

> Tags: #session #b10 #r2-status #paper-2 #prior-art

**Headline:** B10 roadmap sync (19 boxes ticked with commit evidence) + R2 status report + Paper 2 v3.2 cosmetics + prior-art matrix 37 refs.

- **What:** Next-Level v2 plan sweep — A1–A5, A7, B7/B8/B11, B10, C3, C4/C11/E4, C6, C7, D1, D4, E3-prep ticked; deliberate non-ticks annotated (B1–B5 cluster, C-io_common, C5, C15-remainder, D3, user-gated). R2 status report `plans/2026-09-12_R2_Status_Report.md` (6 sections from CHANGELOG truth) supersedes the untracked R1 draft. Paper 2 v3.1 → v3.2-draft cosmetics (ref block alphabetized with one in-text ripple; single-line H1; header date fix; 37-ref mentions). Prior-art matrix +4 genre rows (Kelahan, Prasad & Mazumder, Purohit, Grethen) with D4 niche verdicts.
- **Numbers:** 19 boxes ticked; 37 refs, 10 priority-done.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_49.md

# Session 49 — 2026-09-12

> Tags: #session #paper-2 #v3-3 #cli-safety #nac-edr

**Headline:** Paper 2 v3.2 → v3.3-draft submission polish (all refs resolver-verified) + eval CLI safety + NAC EDR S3 re-probe (still blocked).

- **What:** bibliographic corrections: Powell → JGR Planets 128(2) e2022JE007532; Williams #18 conflated title → verbatim Diviner global-temperatures (Icarus 283); Hurwitz nonexistent Icarus 225 → PSS 79–80; "Pozzobon" earthquake-pounding paper → Sauro et al. 2020 review (ESR 209, 103288); Cushing LPSC numbers corrected to PDS bundle + AbSciCon 2017; Besserelike nonexistent record deleted. Skeptic wording applied (first-claim hedge; code-availability on-request + E3-tied). Number fixes from v1 JSON + registry ground truth (P/R detransposed 0.9000/0.8182; INGENIIPIT ring 21 = 21 ring + 13 r001). CLI: groupsplit + extended bare → help + `--run` gate (was a ~20-min battery).
- **Numbers:** 18 refs (8 shared with Paper 1 + 10 new); frozen v5 numbers untouched; pytest 73; S3 bucket `pds-img-archive-prod` exists but every path → 403 AccessDenied.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_50.md

# Session 50 — 2026-09-12

> Tags: #session #paper-1 #v2-1 #references

**Headline:** Paper 1 v2.0 → v2.1 submission QA — 8 of 9 references fixed (Crossref/arXiv/ADS-verified); three load-bearing method refs added.

- **What:** Blair 2017 author order (Melosh wrongly 4th); Carrer 2024 author list; Mueller 2026 conflated title → Arctic Science 12(1); Reichenzeller 2026 → VCI stem-detection title; Theinat 2018 AIAA venue; Wagner & Robinson 2021 conflated title → "Occurrence and origin of lunar pits…"; Wong 2014 initials swapped. Population "~281" → "~300" at 8 sites (281 was the impact-melt subset). Method refs added: Planchon & Darboux 2002, Wang & Liu 2006, Garwood 1936. Reviewer conflicts: Bickel demoted (co-author on Kelahan 2026), Mittelholz promoted.
- **Numbers:** refs 9 → 12 across the package; frozen numbers spot-checked (3.74 ×7, 24,062.96 ×8, 278/117/233/45, 2.08 [0.67, 4.85]).
- **Gotchas:** Wong 2014 attribution rests on a dead NASA page → Wayback verify queued (done session 51, clean).

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_51.md

# Session 51 — 2026-09-12

> Tags: #session #sentinels #low-10 #data-quality

**Headline:** Wong-2014 Wayback verification clean + C15/LOW-10 sentinel hardening; verifier-caused gray-band recount (37/31) overturned the "dormant change" claim.

- **What:** archived NASA Ames attribution block matches Paper 1's Wong reference verbatim — flag closed, no paper change. `convert_f32.py`: `SENTINEL_MAX_M = 1e6`, `WARN_MAX_M = 100.0`, `ATTR_SENTINEL_MAX = 1e3`; additive `LAST_READ_DIAGNOSTICS`; per-read warning names file/count/max. Round-1 "dormant" claim FALSE — recount found 37 gray-band points (|xyz| ∈ (1e3, 1e6], max ≈930,515.8 m) in Kingsbowl_orig.f32 and 31 (max ≈620,616.4 m) in Indian_NorthSurface_1x.f32; frozen corpus NOT regenerated. Mixed-provenance npz pinned: `IndianTunnel_surface/…npz` KEEPS the 31 finite gray points while the `lltb1/` copy NaNs them (findings `## data-quality — session 51`). verify_phase0 + verify_v02 docstring fixes.
- **Numbers:** tests 73 → 80; smoke canary unchanged (F1 0.392/0/0.800, AUC 0.990); zero writes under `~/lunarvoid/data/`.
- **Gotchas:** `io_analog.py` has its own `SENTINEL_ABS = 1000.0` on a separate path → session 52. Retro-skeptic session 58: block SOUND-with-wording; NEW disclosure — PROVENANCE row 48's registration consumed the finite-ghost npz copy as reference (clamped by coarse_search np.clip, 31/60.9M, negligible); row 48 annotated.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_52.md

# Session 52 — 2026-09-12

> Tags: #session #io-analog #sentinels #provenance

**Headline:** io_analog LOW-10 mirror (`SENTINEL_ABS = 1000` → `SENTINEL_MAX_M = 1e6` + >100 m warn) with provenance pre-flight; C-class import-side-effect flag.

- **What:** same constant-naming convention as convert_f32; public API (`load_xyz`, `voxel_downsample`, `master_grid`) unchanged. Verifier-required provenance pre-flight: PROVENANCE rows 46–49 outputs byte-identical pre/post. Import-side-effect incident caught mid-debug (module-level savefig overwrote the canonical PNG) — restored via git checkout, sha re-verified. Real-data magnitudes measured on the npz files (NorthSurface 85,304 kept points >100 m, max 620,616.4; cave_1x 11,777, max 105.4). C-class flag: `explore_indian_tunnel.py` runs load_xyz + savefig at import (no `__main__` guard) → session 53.
- **Numbers:** tests 80 → 89; NaN drop behavior unchanged.
- **Gotchas:** framing corrected by retro-skeptic session 58 (UNSOUND framing, numbers correct): 85,273 of the 85,304 are real swath-edge geometry in (100, 1000] (median 102.3 m — a 65×125 m scanner-frame site legitimately spans >100 m) + the same 31 ghosts; the old loader NaNed only the 31; cave_1x's 11,777 all ≤105.4 m, zero gray-band. Demanded rewording in findings.md `## skeptic — session 58 (retro)`.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_53.md

# Session 53 — 2026-09-12

> Tags: #session #refactor #import-safety

**Headline:** `explore_indian_tunnel.py` `__main__` guard refactor — CLI byte-identical; canonical PNG sha-guarded.

- **What:** side-effect-bearing code (npz loading, per-site cloud prints, `plt.savefig` to canonical `preflight_clouds.png`, frame-consistency block) wrapped in `def main()`; module level kept cheap/reusable (imports, REPO, SITES, quick_dtm). AST test replaced with a real `exec_module` import asserting (a) canonical PNG mtime + sha256 `ea376b2f…` unchanged across import, (b) `main`/`quick_dtm` callable, `SITES` populated. Symmetry confirmed: register_cave, make_void_mask, coarse_search already guarded — this closed the last gap.
- **Numbers:** pre/post deterministic sha `4ed3c058…` ≡ identical (purely structural refactor); canonical PNG restored to `ea376b2f…` (row 47 match); tests 89 (no net change).
- **Gotchas:** canonical row 47 pins the historical sha while today's run would produce `4ed3c0…` → session-54 pointer.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_54.md

# Session 54 — 2026-09-12

> Tags: #session #provenance #row-47

**Headline:** PROVENANCE_INDEX row 47 notes-column pointer to the findings.md session-52 data-quality block.

- **What:** `preflight_clouds.png` row's `—` notes expanded to cite `findings.md ## data-quality — session 52`: canonical on-disk sha `ea376b…` preserved (frozen state); the script's post-session-52/53 deterministic sha is `4ed3c0…` (documented in findings.md) — future readers can trace the why without guessing.
- **Numbers:** no new evidence, no file regeneration, no SHA change; zero writes under `~/lunarvoid/data/`.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_55.md

# Session 55 — 2026-09-12

> Tags: #session #c5 #superseded-code #conventions

**Headline:** C5 archive superseded code — 2 docstring banners + 1 convention note; signal-only, no code moved.

- **What:** `wp5_fusion/pu_learning_baseline.py` bannered SUPERSEDED by extended + groupsplit; `pu_learning_on_registry.py` bannered SUPERSEDED by groupsplit (PROVENANCE row 183 already pins its output as historical evidence). `code/tools/repair_registry_v1.py` deliberately NOT touched (row 168 canonical; ships in the E3 Zenodo deposit) — recorded as a C5 false positive so future sweeps skip it. Convention note appended to findings.md: banner at top, never delete/move (PROVENANCE citations must stay resolvable), no caller/import edits, no MANIFEST row.
- **Numbers:** pytest 89 passed in 88 s; grep clean — no live imports of either file across code/, tests/, notes/.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_56.md

# Session 56 — 2026-09-12

> Tags: #session #io-common #refactor #low-10

**Headline:** C-io_common (v1 C1) — new shared IO module `code/io_common.py` (4 pillars + AREA_MIN_PER_RUNG); 6 callers refactored; 2 hardcoded absolute paths removed.

- **What:** path resolver via `Path.home()` (LLTB1_HOME/DATA/VENV_PY); LOW-10 sentinel constants (`SENTINEL_MAX_M = 1e6`, `WARN_MAX_M = 100.0`, `ATTR_SENTINEL_MAX = 1e3`, `F32_NODATA = -9999.0`); `keep_or_nan` drop-mask helper; `write_geotiff` extracted from sag_detect; `AREA_MIN_PER_RUNG` identity-preserved (`is` True from consumer). Callers: convert_f32, io_analog, sag_detect, vci, v0_2_pipeline_integration (hardcoded `/home/frostflux/lunarvoid/data` removed), cc_filter_eval_v0_6.
- **Numbers:** tests 89 → 101 (12 new incl. sentinel lock + tmp_path GeoTIFF round-trip); f1 pins preserved (0.39160839160839167 / 0.029746281714785657 / AUC 0.990); verify_v02 21/21, v03 15/15, v04 11/11 — PASS-ALL; zero `~/lunarvoid/data` writes.
- **Gotchas:** one boundary test updated for `>` → `>=` at the exact 1e6 threshold (zero real-data impact). Commit 0721854's body carries an elided absolute path — process deviation logged session 58, no rewrite.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

### → sessions/session_57.md

# Session 57 — 2026-09-12

> Tags: #session #b-cluster #registry-io #sidecar

**Headline:** B1–B5 cluster tail — byte-identical quoted-CSV writer + strict schema validation + structured-flags sidecar + B5 anchors proof; tests 101 → 124; B-cluster closed.

- **What:** `registry_io` gains `SCHEMA_COLUMNS` (15) + `validate_registry(strict)` (summary 278/117/161 on the frozen file) + `write_registry` via csv.writer QUOTE_MINIMAL with raw-parse attrs — round-trip proof BYTE-IDENTICAL (md5 `a60fb52152e33f37e9052434ad026a6e`, verifier-reproduced). New `registry_flags.py` + ONE data file `data/candidate_registry_flags.csv` (frozen registry untouched; classification from unique_accounting's OWN rules). Finding of record: `is_rung_duplicate` = 0 structurally (all multi-rung copies already SUPERSEDED via `superseded_by`; scope note distinguishes from the papers' row-level 278→117 / 45→21 counts). B5 executable proof `tests/test_registry_anchors.py`: 278/278 rows resolve to 54 pair_results on (dtm, rung_m). CLI bare → help. Conventions block in findings.md; bookkeeping: B-cluster box ticked + MANIFEST row (md5 88da3ec5…).
- **Numbers:** 278 rows; 14 TP + 9 FP + 21 ring + 1 funnel = 45 above-floor; 117 ACTIVE / 161 SUPERSEDED; tests 124; smoke canary unchanged.
- **Gotchas:** retro-skeptic session 58: SOUND-with-wording — `unique_key` is the accounting root-primary, not a 3-dp string; NEW disclosure: 6 cross-DTM near-duplicate ACTIVE pairs (12 rows, below-floor: FRESHMELT/FRESHMELT1 ×5 + TYCHOPK/TYCHOPK04 ×1) unresolved by `superseded_by` — below-floor, outside FP accounting.

MOC: [[mocs/MOC Sessions & Ops]] · Wikilink to canonical CHANGELOG: [[../admin/CHANGELOG]]

---

**APPLIED 2026-09-12 (orchestrator bash, per §Apply instructions):** 32 session notes written (sessions 26–57; sessions/ now complete 01–57); 00_HOME A1/A2/A3 applied and verified. Vault is gitignored — no vault files enter git. This staging note is retained as the audit record of the transfer.
