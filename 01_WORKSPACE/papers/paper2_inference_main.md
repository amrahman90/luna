# An annotated test-bed registry and leakage-corrected evaluation
# protocol for lunar void-candidate inference from meter-scale
# orbital terrain data

**Target venue:** Icarus (Elsevier; lunar-science flagship) or
Planetary and Space Science (Elsevier; mid-tier). The v5 §12
publication-strategy #2 line calls this deliverable a "roof-sag
catalogue"; the D4 audit (2026-09-10) reframed it — 233 of 278 rows
are below-floor, Tier-A = 0, and the registry is calibration-context,
so the honest, publishable substance is an **annotated test-bed
registry + leakage-corrected evaluation protocol + honest baselines**,
not a survey catalogue (the catalogue framing was the desk-reject
risk).
**Authors:** LUNARVOID team.
**Date:** 2026-09-12 (v3.1-draft, task D4-fix: skeptic objections
V1–V6 applied to the v3.0-draft-reframe — first-claim narrowed to a
void-candidate **inference-evaluation** benchmark distinct from pit
catalogues and detection-training releases (Watson & Baldini 2024;
Le Corre 2025 dataset release added); title retermed
benchmark → **test-bed registry** ("benchmark" kept only as the
forward-looking, Zenodo-gated goal); §4.1 tier-B JSON/registry
discrepancy quoted explicitly with dates; LROC/ASU web-product
licence caveat in Data availability; protocol-box fixes (imputation
leak = latent/hygiene; leak numbering) and language fixes
("characterized" not "validated"; "missed catalogued-pit
recovery"); §3.3/§4.6 anchored numbers byte-untouched; supersedes
v3.0-draft-reframe of 2026-09-10, which superseded the v0.1 skeleton
of 2026-08-28; not submission-ready).
**Status:** Section-by-section skeleton under the D4 reframe. Built
from the v1.0 G2 transfer
freeze (`data/outputs/wp2_sag/transfer/transfer_summary.json`; 2026-08-23;
21 on-disk NAC DTMs; 278 tier-C rows; n_fp=9, n_tp=14; aggregate FP
3.74 [1.71, 7.10] per 10⁴ km² over 24,062.96 km²) and the WP3 PU-learning
v2 baseline (`data/outputs/wp5_fusion/pu_learning_registry_baseline_v2.json`;
2026-08-28; F1=0.909, AUC=0.931 on a random row split — leak-inflated,
superseded by the D1 group-split evaluation
`data/outputs/wp5_fusion/pu_learning_groupsplit_2026-09-09.json`
(run B, 15 morphometric features: leave-one-DTM-out pooled OOF
F1=0.824 [DTM-cluster-bootstrap 95% CI 0.35, 0.98], AUC=0.930
[0.49, 1.00]). Section framing follows the frozen Paper 1
(`papers/paper1_resolution_limits/main.md`, v2.0), cited by section
rather than quoted, plus `notes/findings.md`. Aspiration-mode: the v5
WP2 → G2 close; WP3 partial (PU baseline only). To date, the
Tranquillitatis radar conduit is the one subsurface lunar structure for
which any instrument provides evidence (Carrer 2024; v5).

---

## Abstract
We present an annotated test-bed registry and a
leakage-corrected evaluation protocol for lunar void-candidate
inference from meter-scale orbital terrain data — to our knowledge
the first annotated benchmark for void-candidate inference
evaluation (scored detections + FP-per-10⁴-km² accounting +
leakage-corrected protocol), distinct from pit catalogues
(Wagner & Robinson 2021) and detection-training releases
(Watson & Baldini 2024; Le Corre 2025, whose ESSA release
publishes georeferenced detection shapefiles, open weights, and
its training product list). Lunar and planetary evaluation
resources are an emerging genre (Moonstone, Prasad & Mazumder
2026; Mars-Bench, Purohit et al. 2025; neither addresses void or
pit inference, and neither operates on meter-scale DTMs); the
test-bed is released toward community-benchmark use once the
planned versioned Zenodo deposition (E3) lands. The registry
annotates 278 candidate rows across 21 on-disk LROC NAC DTMs over
24,062.96 km²,
all pit-associated or pit-rich (calibration-context by
construction): 161 SUPERSEDED duplicate rows carry explicit
`superseded_by` links (117 unique features); row-level labels
comprise 14 TP / 9 FP / 21 ring-artefact / 1 funnel among the 45
above-floor rows, plus 233 explicitly not-inferable below-floor
rows; unique-feature accounting resolves the above-floor set to
6 TP / 5 FP / 9 ring / 1 funnel of 21. Both FP accountings are
reported — row-based 3.74 [Poisson-exact Garwood 95% CI 1.71,
7.10] and unique-feature 2.08 [0.67, 4.85] per 10⁴ km² — as
calibration-context rates, never survey rates. All 278 rows are
single-method morphometry with tier discipline A=0 / B=0 / C=278
after the Cycle-1 skeptic downgrade of the pre-registered v5 I14
rille-intersection rule; the pipeline is frozen from the G2 transfer
calibration (frac=0.20, slope=45°, Frangi σ = 30–300 m; TRANQPIT1
recipe byte-identical md5 `2597002375206aba3119c240c373ad62`). The
evaluation protocol is the methodological contribution: it closes the two
leakage paths that inflated an earlier random-split baseline
(F1 0.909) — duplicate features spanning train/test and shared-DTM
spatial autocorrelation — via duplicate exclusion and
leave-one-DTM-out fold grouping, and adds train-fold-only imputation
and scaling as hygiene (no NaN rows were present, so the imputation
leak was latent, not active), annotation-derived-feature
ablation (identity-proxy discipline), DTM-cluster bootstrap
confidence intervals, and an explicit degenerate-draw rule — a
reusable, referee-ready checklist for small-n planetary registries.
Under this protocol, a positive-unlabeled (PU) learning baseline
(run B; 15 morphometric features; LogisticRegression(C=1.0) inside
pulearn, not retuned) attains pooled out-of-fold F1 = 0.824
[DTM-cluster-bootstrap 95% CI 0.35, 0.98], precision = 0.737,
recall = 0.933 (14/15 positives), ROC AUC = 0.930 [0.49, 1.00]
(21 DTM clusters, 1000 draws, seed 42); leave-INGENIIPIT-out
degrades to F1 0.571 / AUC 0.790, and the pre-registered I14
funnel failure (MARIUSPIT01 r001) recurs in the PU layer as the
registry's first known-hard-case entry. The 233 below-floor rows
are an emergent consequence of the resolution limit quantified by
the companion benchmark paper (LLTB-1) — deliberately retained and
explicitly labelled, not a designed output and not a deficiency:
the registry measures where inference is not yet possible at
current DTM resolution. All results are framed as
calibrated inference, never detection; the I10 apparent-FP
inspection discipline is documented with its three capture paths
and its current verdicts-not-on-disk state. Intervals this wide,
with lower bounds near chance, make the PU baseline a small-n
feasibility result (15 positives), not classifier validation.

---

## 1. Introduction

### 1.1 Why Paper 2 (from detector benchmark to an annotated inference test-bed registry + evaluation protocol)

- Paper 1 (`papers/paper1_resolution_limits/main.md`, frozen v2.0)
  shipped **the detector benchmark** — LLTB-1 v0.1 / v0.4 / v0.5; six
  analog sites; best honest result IndianTunnel_NorthSurface @ 1 m
  F1 0.277 pre-v0.4 / 0.362 v0.4 @ 45°; degrade-ladder detectability
  curve. Its G2 close left the frozen lunar accounting that Paper 2
  builds on (§4.2 there): **278 tier-C morphometry rows, of which 45
  sit above-floor with 14 above-floor inferred void candidates and 9
  FPs; aggregate FP 3.74 [1.71, 7.10] per 10⁴ km² over 24,062.96
  km²; and 21 on-disk DTMs that are all pit-associated or pit-rich,
  i.e. selected with bias toward catalogued pits**.
- **D4 audit framing (2026-09-10)**: this draft descended from a
  "we produced candidate inferences" framing, but the honest
  substance is different — 233 of 278 rows are below-floor (not
  inferable at current resolution), Tier-A = 0, and the registry is
  calibration-context, **not a survey catalogue**. What the work
  actually delivers is stronger and truthful:
  1. **Annotated test-bed registry** (§3.1, §4.1, §4.6): 278
      rows / 117 unique features; B1-repaired (161 SUPERSEDED rows
     carry explicit `superseded_by` links); row-level labels
     (14 TP / 9 FP / 21 ring / 1 funnel above-floor; 233
     below-floor rows) plus unique-level labels (6 TP / 5 FP /
     9 ring / 1 funnel of 21); dual FP accounting (row-based
      3.74 [1.71, 7.10]; unique 2.08 [0.67, 4.85] per 10⁴ km² over
      24,062.96 km², calibration-context) — to our knowledge the
      first annotated benchmark for **void-candidate inference
      evaluation** (scored detections + FP-per-10⁴-km² accounting +
      leakage-corrected protocol), distinct from pit catalogues
      (Wagner & Robinson 2021) and detection-training releases
      (Watson & Baldini 2024; Le Corre 2025).
   2. **Leakage-corrected evaluation protocol** (§3.3; the D1
     redesign presented as reusable methodology): duplicate
     exclusion, leave-one-DTM-out fold grouping, train-fold-only
     imputation and scaling, annotation-derived-feature ablation
     (identity-proxy discipline), DTM-cluster bootstrap CIs, and
     the degenerate-draw rule — written as a referee-ready
     checklist for small-n planetary registries.
  3. **Honest baselines under the protocol** (§3.3, §4.2): PU run B
     (15 morphometric features): F1 0.824, P 0.737, R 14/15,
     AUC 0.930; cluster CIs F1 [0.35, 0.98], AUC [0.49, 1.00];
     run A diagnostic + run C rung-ablation;
     leave-INGENIIPIT-out 0.571/0.790; the I14 funnel failure
     (MARIUSPIT01 r001) enters the registry as its first
     **known-hard-case** entry.
  4. **Limitations as protocol outputs** (§5.2): small-n (15
     positives), positive-mass concentration (10 of 15 positives
      in one DTM fold), and wide CIs are what the test-bed
      **measures** — reported properties of the resource, not
      defects hidden from the reader.
- Verbatim scope quote (master plan v5 §8 WP2 line 487–491):
  > "DELIVERABLE: regional candidate catalogue with per-candidate
  > evidence vectors, confuser-discrimination scores, explicit coverage
  > bounds, lower-bound sag framing (I7), and honest nulls.
  > GATE G2: catalogue survives confusion analysis; false-candidate
  > density per 10^4 km^2 reported."
  This paper is the G2 deliverable — with the v5 deliverable's
  "candidate catalogue" language delivered honestly as an
  **annotated test-bed registry + evaluation protocol**: the master plan's own
  §9 claim-discipline rules (two-independent-methods tiering;
  calibration-context FP reporting; I10 inspection) preclude a
  survey-catalogue claim at this scope, and the D4 reframe makes
  that explicit. Paper 3 will close G3.
- Headline framing (verbatim from `notes/findings.md` line 286–292,
  2026-08-22 skeptic P3.1c review):
  > "AGGREGATE FP RATE IS THE CALIBRATION RATE DILUTED, NOT A SURVEY
  > RATE — `transfer_summary.json.aggregate.fp_per_1e4km2 = 3.71
  > [0.76, 10.83]`. All 3 FPs are TRANQPIT1; 6 of 7 contributing DTMs
  > are n_fp=0 because they were selected BECAUSE they host catalogued
  > pits. The '10/649' sample is 10 pit-associated DTMs, not random
  > mare. The honest numbers are TRANQPIT1's `240.41 [49.58, 702.58]`
  > (small-sample n=4) — a per-DTM calibration context, not an
  > extrapolation."
  Paper 2 takes that honesty forward: the headline 3.74 per 10⁴ km²
  is calibration-context, **never** reported as a survey rate.

### 1.2 What this paper IS and IS NOT (claim discipline)

- **IS**: an **annotated test-bed registry** (278 tier-C
  morphometry rows; 117 unique features via `superseded_by` links)
  with per-candidate confusion labels and per-DTM `local_Amin`
  calibration floors — a resource for evaluating and calibrating
  void-candidate inference methods; a **leakage-corrected
  evaluation protocol** (duplicate exclusion, leave-one-DTM-out
  folds, train-fold-only preprocessing, identity-proxy ablation,
  DTM-cluster bootstrap CIs, degenerate-draw rule; §3.3); a
  PU-learning **ranking** baseline under that protocol (leak-free
  leave-one-DTM-out pooled OOF F1 0.824 [cluster-bootstrap 0.35,
  0.98] / AUC 0.930 [0.49, 1.00], run B morphometric-only feature
  set; §3.3); the first lunar-published framework that reports FP per
  10⁴ km² (master plan §9 mandatory metric); the explicit I10
  apparent-FP discipline; the Marius Hills I14 funnel-pit case study
as a v5-confirmed confounder and the registry's first
   known-hard-case entry.
- **IS NOT**: a lunar lava-tube detection claim; **not a survey
  catalogue of inferred voids** (233 of 278 rows are below-floor
  and explicitly not inferable; the registry is
  calibration-context). Tier A = 0 by
  construction (the registry's max tier is C; tier-B promotion
  requires two-independent-methods agreement, master plan §9
  "two-independent-methods rule" line 28–30 of the registry header).
  Not a GRAIL / Mini-RF paper. Not a Diviner GHRM thermal paper.
  Not a MGC3 cross-body DL pretraining paper. Not a multi-evidence
  fusion paper. Not a survey-grade FP-rate claim. Not a replacement
  for visual inspection (the user-completed 2026-08-28 walk-through
  is recorded but per-cluster labels were not captured on-disk — see
  §4.5 for the honest state).
- **Claim-discipline carry-over from Paper 1** (scope statement in its
  §1.3): Paper 1 (the detector benchmark) already disclaims any
  global lava-tube detection claim, treats GRAIL / Mini-RF-style
  geophysics as confirmation layers rather than survey detectors
  (Tier D in v5), and defers the registry-and-inference side of the
  problem to a companion paper once the detector is characterized —
  Paper 2 is that companion (Paper 1 characterized, not validated,
  the detector: best honest analog F1 0.362).
- **The Tranquillitatis carve-out** (Paper 1 §1.1 and §6): no
  subsurface lunar feature is verifiable today; the radar-evidenced
  Tranquillitatis conduit (Carrer 2024; v5) is the sole exception.
  Paper 2 leaves that boundary unchanged.

### 1.3 Trigger conditions for Paper 2 — honest state

The `2026-08-23_Paper2_outline_sketch.md` enumerates 4 trigger
conditions. Their status as of 2026-08-28:

| Trigger | Required (verbatim from outline sketch) | Status @ 2026-08-28 |
|---|---|---|
| T1 | Visual inspection complete for ≥15 of 27 backlog candidates | **PARTIAL** — user verbally confirmed "1, done" for 24 candidates on 2026-08-28 (`notes/findings.md` line 783–794); no on-disk per-cluster verdict capture; helper HTML at `admin/visual_inspection_helper.html` preserves no radio state. **Verdicts not on-disk** (the paper must say so). |
| T2 | N ≥ 30 tier-B candidates | **NOT MET** — tier-B count collapsed 3 → 0 after the skeptic Cycle-1 downgrade of the I14 funnel rule (`notes/findings.md` 2026-08-22; **A=0 / B=0 / C=278**); tier-B promotion requires two-independent-methods agreement (master plan §9) and we have only Z2 morphometry active at 21/21 + thermal at 2/7 (per the 2026-08-22 P4.3 review, "INCONCLUSIVE at N=7 due to 4/7 equatorial coverage gap") + photometric (P4.2) deferred. |
| T3 | Cycles 3–5 closed (NAC EDR + ASP stereo + quality gate) | **NOT MET** — PDS NAC_EDR / NAC_CDR / browse 404 on every endpoint (2026-08-23 environment block); Hetzner Tier-1 rental ($55/mo, D2 trigger APPROVED 2026-08-22 but rental not yet authorised; $150 ceiling preserved, **$0 spent to date**) would close these but is gated on user approval. |
| T4 | Multi-evidence stacking at ≥2 evidence legs at ≥5 candidates | **NOT MET** — multi-evidence stacking is deferred to Paper 3 (WP3 scope; v5 master plan §8 WP3 line 493–506); only morphometry is active site-wide; thermal at 2/7 INCONCLUSIVE; photometric deferred (P4.2); GRAIL gravity not active (P3.1a Phase-3 floor logging only; l_max=680 subset v0.1 was never integrated into the registry). |
| **(implicit)** | PU-learning baseline | **MET (BEYOND)** — `data/outputs/wp5_fusion/pu_learning_registry_baseline_v2.json` 2026-08-28: 278 rows / 19 features / n_positives_TP=34 / n_unlabeled=244; F1 = 0.9091 / AUC = 0.9312 on a random row split — **leak-inflated** (duplicate features and shared DTMs could span train/test), superseded by the D1 leak-free group-split evaluation `data/outputs/wp5_fusion/pu_learning_groupsplit_2026-09-09.json` (v5 triple-run): 117 active rows (161 SUPERSEDED duplicates excluded), leave-one-DTM-out (21 folds), run B (15 morphometric features; 4 annotation-derived flags removed) pooled OOF F1 = 0.824 [DTM-cluster-bootstrap 0.35, 0.98] / AUC = 0.930 [0.49, 1.00]; run A diagnostic (19 features) F1 = 0.824 / AUC = 0.927 with **0/117 decisions differing from B at t=0.5**. LogisticRegression(C=1.0, max_iter=1000), not retuned; wall time 0.04 s (v2 run). The v1 baseline (5 features) gave F1 = 0.8571 / AUC = 0.8969. |
| **(implicit)** | G2 FINAL-PASSED | **PARTIAL** — `notes/findings.md` line 794 verbatim: "**G2' status:** FINAL-PASSED 2026-08-28 (already flipped in earlier 'complete all' session; user's 'pass g2' instruction served as explicit confirmation). Row 10 PARTIAL honest state preserved verbatim. Final-pass does NOT depend on per-candidate verdicts; the verdict text already documents the catalogued-pits-only framing honestly." |

**Honest framing**: Paper 2 ships the WP2 deliverable (delivered as
an **annotated test-bed registry**, per the D4 audit + D4-fix), the
**leakage-corrected evaluation protocol**, and the PU-learning
ranking baseline that was always sequenced before WP3 fusion. The
aspirational outline sketch's headline ("N=30+ tier-B candidates,
multi-evidence per-candidate panel, GRAIL+Diviner stacking") is the
deferred WP3 scope, not this paper.

---

## 2. Related work (brief; extends Paper 1 §1.2)

- Populated from `notes/prior_art_matrix.csv` (33 refs; priority-done
  rows from Paper 1 carry over). Paper 2 extends with WP3 fusion
  references, MGC3 cross-body (Cushing 2015/2017), and GRAIL/Diviner
  anomaly references.
- **Stability bounds (Blair 2017 + Theinat 2018)** — anchor for the
  realistic ~60–300 m lunar tube-width band used in the morphometric
  Frangi scale selection; citations carried over from Paper 1.
- **Tranquillitatis radar conduit (Carrer 2024)** — the sole lunar
  subsurface structure with instrument-based evidence; v5
  claim-discipline anchor; citation carried over from Paper 1.
- **Pit Atlas (Wagner & Robinson 2021)** — primary label set
  (~281 catalogued pits; ~30 m positional accuracy defines the
  declared match radius per v5 I15); citation carried over.
- **Wong 2014 NASA analog** — LLTB-1 ground truth; citation carried
  over.
- **Mueller 2026 (I1–I7) + Reichenzeller 2026 (I8–I15)** — inherited
  component source. **I10 in particular**: "inspect-every-apparent-FP
  discipline" (verbatim from the `prior_art_matrix.csv` Reichenzeller
  row); §3.4 and §4.3 of this paper apply it.
- **Le Corre 2025 ESSA** — the most-cited direct competitor
  (Mask R-CNN trained on Lunar Pit Atlas labels; reported detection
  F1). The release is public and annotated: georeferenced
  shapefiles of every detection, open weights on Zenodo, code on
  GitHub, and the full training product list
  (`notes/prior_art_matrix.csv` LeCorre2025 row) — a
  **detection-training dataset release**, the genre from which the
  narrowed first-claim of this paper is distinct (void-candidate
  inference evaluation: scored detections + FP-per-10⁴-km²
  accounting + leakage-corrected protocol). Paper 2 cites,
  positions as inference vs detection (master plan R8/R9),
  **never** uses as a label source. §5.3 expands the
  inference-vs-detection framing.
- **Benchmark-genre precedents (added in the D4 reframe)** — lunar
  and planetary benchmark resources are an emerging genre, and this
  paper positions itself within it:
  - **Moonstone (Prasad & Mazumder 2026)** — the first multimodal
    foundation-model benchmark for lunar remote sensing: a
    28-channel, 128 ppd (~237 m/px) global pretraining corpus from
    seven instrument families and six downstream tasks. It does
    **not** address void or pit inference and does not operate at
    meter-scale DTM resolution — the niche of this paper remains
    open.
  - **Mars-Bench (Purohit et al. 2025)** — the Mars-science
    counterpart (20 datasets spanning classification,
    segmentation, object detection; standardized baselines);
    genre precedent for systematic model evaluation on planetary
    tasks.
  - **Watson & Baldini 2024** — Mask R-CNN (ResNet50)
    cave-entrance detection trained jointly on lunar NAC imagery,
    Martian HiRISE pit data, and synthetic implanted lunar pits
    (~89% bbox / ~96% mask F1, lunar/Martian); the precursor
    detection line to ESSA and the v5 R8 prior-art-collision
    anchor. 2D raster detection only: no DTM morphometry, no
    subsurface inference, no PU treatment, no FP-per-area
    reporting — again detection training, not inference
    evaluation.
  - **StereoLunar (Grethen et al. 2025)** — an open lunar
    stereo-pair dataset for 3D reconstruction; informs our
    dataset-release conventions (versioned-DOI deposit; see
    Data availability).
  Position statement: Paper 2 is, to our knowledge, the **first
  annotated benchmark for void-candidate inference evaluation
  (scored detections + FP-per-10⁴-km² accounting +
  leakage-corrected protocol) at meter scale from orbital DTMs,
  distinct from pit catalogues (Wagner & Robinson 2021) and
  detection-training releases (Watson & Baldini 2024; Le Corre
  2025)**. The artifact ships as an annotated test-bed registry +
  evaluation protocol; community-benchmark status is the
  forward-looking goal, gated on the planned versioned Zenodo
  deposition (E3; see Data availability).
- **NEW for Paper 2** (added vs Paper 1's 8 refs; 10 planned
  additions — Cushing ×2, Grethen, Hurwitz, Powell, Pozzobon,
  Prasad & Mazumder, Purohit et al., Watson & Baldini, Williams —
  plus one optional):
  - **Prasad & Mazumder 2026 / Purohit et al. 2025 / Grethen et
    al. 2025** — benchmark-genre precedents (Moonstone, Mars-Bench,
    StereoLunar); see the bullet block above and References
    entries 11, 15, 16.
  - **Watson & Baldini 2024** — detection-training release
    (Mask R-CNN cave-entrance detection, Icarus 411:115952); the
    v5 R8 prior-art-collision anchor and precursor to ESSA; see
    the genre block above and References entry 18.
  - **Cushing 2015 / Cushing 2017** — Mars Global Cave Catalog
    (MGC3); cross-body pretraining source; cited in outline sketch
    §2 but **NOT executed** (deferred — see §3.4).
  - **Williams 2017** — Diviner cumulative nighttime temperature;
    basis for the P4.3 thermal anomaly stacking (sketch only;
    INCONCLUSIVE at 2/7 coverage per `notes/findings.md` 2026-08-22
    P4.3 review).
  - **Powell 2023** — LRO Diviner GHRM (128 ppd); the actual
    thermal product sampled at 7/7 DTMs in P4.3; sub-pixel scale
    mismatch acknowledged (skylight pits ≤100 m diameter are
    sub-pixel at all 7 sites; only site-scale anomalies resolvable).
  - **Hurwitz 2013** — sinuous rille shapefile (the I5 confusion
    layer); used in the v5 I14 funnel-pit prediction.
  - **Elkins-Tanton 2024 / Besserer 2024** (if cited) — recent
    lunar subsurface void / thermal modelling; placeholder for the
    v5 Tier-D confirmation layer framing.

---

## 3. Methods

### 3.1 The annotated test-bed registry (278 rows, A=0 / B=0 / C=278; 117 unique features)

- **Source**: `data/candidate_registry.csv` (310 lines; 32-line header
  + 278 data rows; **CSV line 31** = column header; provenance line 32
  = "2026-08-22 ... Phase 3 transfer pending" — the v5 WP2 schema).
- **B1 duplicate repair (registry integrity)**: 161 of the 278 rows
  are SUPERSEDED children carrying explicit `superseded_by` links to
  their primary row (117 ACTIVE unique features); a group inherits
  the class of its primary row. §4.6 gives the unique-level
  accounting and its sensitivity to the grouping radius.
- **Schema** (verbatim from registry header lines 9–30):
  - `candidate_id`: LV-`<dtm>`-`<rung>`-r`<rank>` stable unique id
  - `methods`: evidence streams currently agreeing, "|"-separated
    (morphometry | gravity | thermal | illumination); `morphometry`
    is the only value currently populated
  - `tier`: A = two+ independent methods agree; B = one method,
    confusion-cleared; C = raw morphometry only
  - `tier discipline` (verbatim from registry header lines 28–30):
    > "The two-independent-methods rule: tier A REQUIRES methods to
    > include at least one of gravity/thermal/illumination in
    > addition to morphometry. Morphometry alone can never exceed
    > tier B."
- **Current tier distribution** (after the 2026-08-22 skeptic Cycle-1
  downgrade of the I14 funnel rule):
  - **n_tier_A = 0** (no candidate has ≥2 independent methods;
    confirmed by `transfer_summary.json.aggregate.n_tier_A = 0`
    and the registry after the Cycle-1 downgrade)
  - **n_tier_B = 0** in the registry (post-downgrade; the 3
    MARIUSPIT01 rows that earned B by "rille intersection within
    100 m" were the pre-registered v5 I14 failure mode — see §4.4).
    The frozen `transfer_summary.json` (generated 2026-08-23)
    still records the pre-downgrade `n_tier_B = 3`; the downgrade
    to 0 lives in the registry itself (§4.1 quotes both values
    with dates)
  - **n_tier_C = 278** (all rows are single-method morphometry)
- **Above-floor vs below-floor split** (verbatim from
  `transfer_summary.json.aggregate`):
  - `n_above_local_floor = 45`
  - `n_below_local_floor = 233`
  - `n_candidates = 278`
- **Calibration-context framing** (verbatim from
  `transfer_summary.json.aggregate.interpretation`):
  > "calibration-context rate, selection-biased to catalogued pits
  > (all 21 DTMs on disk are pit-associated or pit-rich); NOT a
  > random-mare survey rate"
- **Scope caveats** (verbatim, same source, lines 505–510):
  > "all 21 on-disk DTMs are pit-associated or impact-melt (selection
  > bias toward catalogued pits); 10 highland/impact-melt sites have
  > NaN local_Amin and are treated as terrain extrapolation, not
  > portability; no random-mare control; rate is calibration context
  > only; frozen TRANQPIT1 recipe unchanged from P3.1b freeze"
- **Highland / impact-melt preservation**: 10 sites (KINGCRATER2/3/4,
  TYCHOPK/02/03/04/07, FRESHMELT, FRESHMELT1) have NaN `local_Amin`
  and are preserved in the registry with `terrain_extrapolation`
  annotation; they do **not** contribute to FP counting.
- **INGENIIPIT ring-artefact annotation**: 24 INGENIIPIT rows (r002–r008
  at 2/4/5 m rungs, all within ~10 km of catalogued pit r001)
  carry the `ring artifact around catalogued pit r001` note and are
  **not** 23 separate void candidates (one row each, but the same
  detector-induced Frangi ring pattern); r001 is the actual catalogued
  pit (top score 19.33, 46 m from the catalogued feature; verifier
  finding 2026-08-21).

### 3.2 Per-DTM noise floors (TRANSPIT1 / MARIUSPIT01 with the 3× sag-band-RMS rule)

- **Pooled sag-band (60–300 m DoG) residual RMS** (method and verdicts
  documented in the companion benchmark, Paper 1 §3.6/§4.6): the
  target regime — published lunar NAC DTMs — shows a pooled sag-band
  residual RMS, after kriging correction, of 1.245 m for TRANQPIT1
  and 1.379 m for MARIUSPIT01. Applying the 3× sag-band-RMS rule — a
  PROJECT CONVENTION, not a v5 mandate (grep-verified; findings
  2026-08-21 skeptic caveat) — single-DTM detectability holds for sag
  amplitude A ≥ 5 m at BOTH pooled sites (3σ = 3.74 / 4.14 m; ≥ 4 m
  at the quieter site).
- **Per-DTM `local_Amin` table** (subset; from
  `transfer_summary.json.per_dtm`, units metres):

  | DTM | local_Amin_m | local_3sigma_m | notes |
  |---|---:|---:|---|
  | TRANQPIT1 | 3.735551 | 3.735551 | krigcorr source; the calibration DTM |
  | MARIUSPIT01 | 4.137601 | 4.137601 | krigcorr source; rille-funnel case study |
  | FECNDITATS2 | 2.29791 | 2.29791 | raw NAC fallback |
  | INGENIIPIT | 2.959265 | 2.959265 | raw NAC; ring-artefact DTM |
  | FECUNPIT | 2.567686 | 2.567686 | raw NAC; 6 FPs at the DTM north end |
  | GRUITHUIS17 | 4.385086 | 4.385086 | Cycle 1; all below-floor |
  | GRUITHMARE2 | 3.355474 | 3.355474 | Cycle 1; deep-pit low-vesselness case |
  | IRIDIUMPIT1 | 2.837609 | 2.837609 | raw NAC; missed catalogued-pit recovery |
  | MARIUSCONE | 3.68877 | 3.68877 | Cycle 1; deep-pit low-vesselness case |
  | PRCLRMPIT01 | 3.526279 | 3.526279 | raw NAC |
  | SWFECUNPIT1 | 3.231591 | 3.231591 | raw NAC |
  | KINGCRATER2/3/4 | 1.972013 / 3.630243 / 3.265668 | (same) | raw NAC; central-peak-relief |
  | TYCHOPK / 02 / 03 / 04 / 07 | NaN | NaN | highland / Tycho central peak; `terrain_extrapolation` |
  | FRESHMELT / FRESHMELT1 | NaN | NaN | impact-melt; `terrain_extrapolation` |

  (Source: `transfer_summary.json.per_dtm.*`; rows above are a
  representative subset; full per-DTM block is 21 DTM keys.)
- **3× rule provenance** (Paper 1 §3.6 carries the same caveat, from
  the `notes/findings.md` line 70–71 skeptic entry): the "3× sag-band
  RMS" multiplier is a PROJECT CONVENTION; no such multiplier appears
  in v5 §4 (grep-verified 2026-08-21) — do not cite v5 for it.
- **Caveat inherited from Paper 1** (§4.6 there): the floor is
  sampled at only 2 of ~649 mare DTMs; each `local_Amin` row in
  `per_dtm` is `3 × pooled_rms_m` for that DTM, the per-panel RMS
  spans 0.74–2.05 m (Marius P3 local 3σ ≈ 6.1 m), and per-DTM floors
  are therefore required before survey-wide claims.

### 3.3 The PU-learning baseline (v1 0.857 → v2 0.909 random-split, leak-inflated; D1 leak-free LODO run B F1 0.824 / AUC 0.930; flag-ablation decisions unchanged)

- **Sources**: `data/outputs/wp5_fusion/pu_learning_registry_baseline_v2.json`
  (273 lines; generated 2026-08-28; v1/v2 history, random split,
  leak-inflated) and `data/outputs/wp5_fusion/
  pu_learning_groupsplit_2026-09-09.json` (the D1 v5 triple-run
  leak-free evaluation; registry md5 `a60fb52152e33f37e9052434ad
  026a6e`; canonical for every v3-column number below).
- **Feature matrix** (verbatim from JSON `feature_audit` block):
  - `n_features_v2 = 19`, `n_features_v1 = 5`, `n_new_features = 14`
  - All 19 names: `span_m, sag_amp_m, score, conf_dist_rille_m,
    conf_dist_chain_m, log_span_m, log_sag_amp_m, log_score,
    log_conf_dist_rille_m, log_conf_dist_chain_m, sag_per_span,
    log_sag_x_score, rung_cm, has_terrain_extrap,
    has_deep_pit_low_vesselness, has_funnel_risk, has_12km_FP,
    is_single_method_morphometry, n_confusion_keys_present`
  - **Excluded to avoid leakage** (verbatim from JSON):
    `dtm, lon, lat, has_ring_artifact, has_below_local_floor,
    is_rank1 / rank_n`
  - Imputation: median per feature; `n_rows_with_nan_pre_imputation = 0`
    (no NaN rows were present, so the imputation leak closed by
    train-fold-only preprocessing was latent, not active — hygiene)
- **Positive-class definition** (verbatim from JSON
  `positive_class_mapping`):
  > "positive ← (dtm ∈ CATALOGUED_PIT_DTMS AND candidate_id matches
  > '-r001') OR (notes contain 'ring artifact'); AND NOT below-local-
  > floor"
  - `n_positive_candidates = 34` (the 7 CATALOGUED_PIT_DTMS rank-1 TPs
    + the 24 INGENIIPIT r002–r008 ring-artefact rows + 3 other
    catalogued-pit rank-1 hits across the 21 DTMs × 2–3 rungs)
  - `n_unlabeled = 244`
  - (v2 registry-wide accounting over all 278 rows; under the D1
    active-set evaluation below, the same label rule yields **15
    positives / 102 unlabeled** on 117 rows after the 161 SUPERSEDED
    duplicates are excluded — 10 of the 15 positives are INGENIIPIT
    rows)
- **PU-learner configuration** (verbatim from JSON `metrics`):
  - Estimator: `LogisticRegression(C=1.0, max_iter=1000)`
  - Hold-out ratio: 0.1; random_state: 42; test_size: 0.3
  - Scaler: `StandardScaler (zero-mean, unit-variance; train-set
    stats)`
  - sklearn warnings: `[]`
- **Metrics** (v1/v2 verbatim from the v2 JSON `metrics` block —
  both from a random row split and therefore **leak-inflated**;
  v3 = the D1 leak-free re-evaluation, v5 triple-run, pooled
  out-of-fold (OOF); **run B (15 morphometric features, four
  annotation-derived flags removed) is the headline**; run A
  (19 features, flags retained) is a diagnostic upper bound;
  95% CIs are DTM-level **cluster bootstrap**: 21 DTM clusters
  resampled with replacement, 1000 draws, seed 42):

  | Metric | v1 (5 feat, random split) | v2 (19 feat, random split) | **v3 run B (15 feat, D1 LODO, pooled OOF)** | v3 run A (19 feat, diagnostic) |
  |---|---:|---:|---:|---:|
  | F1 | 0.8571 | 0.9091 | **0.824 [0.35, 0.98]** | 0.824 [0.35, 0.98] |
  | precision | 0.8182 | 0.9091 | 0.737 [0.25, 1.00] | 0.737 [0.25, 1.00] |
  | recall | 0.9000 | 0.9091 | 0.933 (14/15) [0.50, 1.00] | 0.933 (14/15) |
  | ROC AUC | 0.8969 | 0.9312 | **0.930 [0.49, 1.00]** | 0.927 [0.49, 1.00] |
  | n_predicted_positive | — | 11 | 19 | 19 |
  | n_test_total | — | 85 | 117 (pooled OOF, 21 folds) | 117 (same folds) |
  | n_test_positives | — | 11 | 15 | 15 |
  | n_train_total | — | 193 | per-fold (held-out DTM excluded) | per-fold (same) |
  | n_train_positives | — | 23 | per-fold (5 when INGENIIPIT held out) | per-fold (same) |

  (v1 figures from the LLTB-1 v0.4 PU baseline release note; the v2
  JSON does not restate them — paper-writer to confirm against
  `admin/verification_evidence/` if available, else cite the v1
  release note path. v3 figures from
  `data/outputs/wp5_fusion/pu_learning_groupsplit_2026-09-09.json`
  (`runs.run_B_MORPH_headline` and
  `runs.run_A_FULL_diagnostic_upper_bound`: `pooled_oof` +
  `bootstrap_cluster_HEADLINE` blocks; the row bootstrap over pooled
  OOF rows is stored in the same JSON as a **secondary,
  anti-conservative** interval — rows cluster by DTM — and is not
  used as a headline anywhere in this paper); per-row OOF
  predictions for all 117 rows are stored in that JSON.)

- **D1 redesign — leak-free triple-run re-evaluation (2026-09-09,
  regenerated in place 2026-09-10 after the skeptic repair)**: the
  v2 split above was random over rows, which leaks twice — leak 1:
  161 SUPERSEDED duplicate rows of the same physical feature could
  span train/test; leak 2: rows from the same DTM (spatially
  autocorrelated terrain) could span both. The D1 evaluation
  (`data/outputs/wp5_fusion/pu_learning_groupsplit_2026-09-09.json`;
  registry md5 `a60fb52152e33f37e9052434ad026a6e`) excludes all
  SUPERSEDED duplicates (117 active rows: 15 positives / 102
  unlabeled; closes leak 1), groups folds by DTM
  (leave-one-DTM-out, 21 folds; closes leak 2), and fits median
  imputation and StandardScaler on training folds only — closing a
  third, **latent** leak-path as hygiene (no NaN rows were present
  pre-imputation, so the imputation leak was latent, not active) —
  and keeps the v2 estimator and
  hyperparameters unchanged (no retuning). **Headline = run B**,
  which additionally removes the four notes-derived annotation
  flags (`has_terrain_extrap`, `has_deep_pit_low_vesselness`,
  `has_funnel_risk`, `has_12km_FP` — partial DTM-identity /
  human-FP-adjudication proxies), leaving 15 morphometric features.
  **Run A** (19 features) is retained as a diagnostic upper bound:
  pooled OOF F1 0.824 / AUC 0.927 with **decisions identical to
  run B at the 0.5 threshold (0/117 rows differ)** — the flags were
  NOT load-bearing for the decision set, so the ablation is a
  robustness result, not a metric change (they did deform the raw
  score scale; see the I14 note below). **Run C (rung-ablation
  sensitivity)**, added in the v5 regeneration of the same JSON to
  close the residual that `rung_cm` is the last identity-flagged
  feature (rung 500 exists only on TRANQPIT1, rung 800 only on
  MARIUSPIT01), removes `rung_cm` from run B (14 features): pooled
  OOF F1 0.800 / precision 0.700 / recall 0.933 (14/15) / AUC
  0.928, cluster-bootstrap CI F1 [0.285, 1.000] / AUC [0.486,
  1.000]. Only 5/117 decisions flip vs run B at t=0.5 — 3 of them
  the MARIUSPIT01 800-cm rows themselves (the rung value exists
  only on that DTM; the other 2 are FECUNPIT 400-cm rows turning
  negative) — and the I14 failure (MARIUSPIT01 r001) does not move
  (rank 1/15 by score and predicted negative in both runs); **run B
  remains the headline**. Uncertainty is quantified
  by DTM-level **cluster bootstrap** (21 DTM clusters resampled
  with replacement, 1000 draws, seed 42): run-B F1 95% CI
  **[0.35, 0.98]**, AUC **[0.49, 1.00]** — wide, with lower bounds
  near chance; the row bootstrap over pooled OOF rows is kept in
  the JSON as a secondary, anti-conservative interval only (rows
  cluster by DTM) and is not quoted as a headline. Degenerate
  cluster-bootstrap draws — resamples containing zero true
  positives or zero unlabeled rows (ROC AUC undefined without both
  classes) — are discarded and counted, not redrawn (1/1000 draws
  per run); draws with zero *predicted* positives are retained,
  with F1/precision scored under `zero_division=0`. Recall is
  reported as a recovered count: **14/15 positives**. **Leave-
  INGENIIPIT-out** (10 of the 15 positives live in that fold): F1
  0.571, precision 0.444, recall 0.800 (4/5), AUC 0.790 — the
  pooled numbers are dominated by the INGENIIPIT fold and degrade
  away from it. **Named failure mode**: MARIUSPIT01 r001 (the only
  positive in its fold) is the lowest-scoring positive in both
  runs — OOF score ~2.2×10⁻⁷² (run B; 2.7×10⁻⁶⁴ run A), fold ROC
  AUC 0.000 — the **pre-registered I14 funnel failure recurring in
  the PU layer** (pits incised into rilles spill sideways at the
  fill-to-spill reference, so morphometry ranks the Marius Hills
  pit below its rille-context neighbours; §4.4). **Threshold
  sensitivity** (run B, pooled OOF): F1 0.824 @ t=0.5 / 0.839 @
  t=1.0 / 0.846 @ t=1.5. One fold (INGENIIPIT held out, 5 training
  positives) required the pre-registered feasibility retry of
  pulearn's internal hold-out draw (random_state ladder 42→43 at
  hold_out_ratio 0.1, both runs; recorded per fold in the JSON);
  its test F1 is 1.000 — stated factually, with no claim that it
  sits inside any CI width (it does not: 1.0 exceeds the
  cluster-bootstrap F1 upper bound of 0.98). Honest reading: the
  random split overstated precision; under leakage-corrected
  evaluation with cluster-level uncertainty, the PU ranking is
  promising but consistent with chance at the CI lower bounds — a
  small-n feasibility result (15 positives), not classifier
  validation.
- **Top-5 features by |coef|** (verbatim, v2 JSON
  `top_5_features_by_abs_coef` — random-split coefficients retained
  for provenance; the D1 v5 JSON records run-A per-fold and run-B
  mean LODO coefficients in `logistic_coefficients`):
  1. `log_sag_amp_m` (+1.392)
  2. `has_12km_FP` (−0.734)
  3. `log_sag_x_score` (+0.672)
  4. `sag_per_span` (−0.644)
  5. `log_span_m` (+0.612)
  Interpretation: positive sign ⇒ predict positive (above-floor void
  candidate); negative sign ⇒ predict unlabeled (below-floor or known
  FP family). `has_12km_FP` and `sag_per_span` pull toward unlabeled
  — the TRANQPIT1 12-km FPs and the deep-pit low-vesselness cluster
  behave correctly under the model.
- **Claim-discipline framing** (verbatim from the D1 v4 JSON
  `claim_discipline`):
  > "PU-learning produces a RANKING of inferred void candidates, NOT
  > detections. The positives are a proxy for catalogued-pit local-max
  > hits; unlabeled rows are ML-detected sags of unknown nature.
  > Metrics estimate agreement with that proxy on held-out DTMs; run B
  > removes annotation-derived identity proxies and is the only
  > defensible generalisation estimate reported here. Calibrated
  > inference only."
- **Why the ranking helps**: ranks the 102 active unlabeled
  ML-detected sags (244 registry-wide before superseded-duplicate
  exclusion) by their estimated P(catalogued-pit-like); the top of
  the rank identifies the candidates most worth visual-inspecting
  first. This
  is the missing tier-A-prep layer that the v5 master plan §9 I10
  discipline requires.
- **Caveats**: (a) positive-class definition is a **proxy**, not
  ground truth; (b) the held-out DTM folds are not a held-out mare
  basin (master plan §9 "One entire mare basin held out untouched
  until final evaluation" is not yet implementable at N=21); (c) the
  ranking is monotonic on the run-B (15-feature) set, not a
  calibrated posterior — conformal-prediction coverage (master plan §9) is
  deferred.

### 3.4 Cross-body MGC3 transfer (sketch only; gated on rental)

- **Goal** (verbatim from `plans/2026-08-23_Paper2_outline_sketch.md`
  §3.6): "MGC3 pretraining (Cushing 2015/2017 catalog; HiRISE/CTX
  skylight morphology)".
- **Status**: **DEFERRED**. `notes/findings.md` line 470–480
  (decision 2026-08-22) verbatim:
  > "MGC3 cross-body pretraining (Mars cave catalog Cushing 2015/2017)
  > is out of scope for LUNARVOID Paper 1. Defer to Paper 2 (post-G1)
  > when the lunar registry has enough scale to support a transfer-
  > learning experiment (need N ≥ 30 lunar positives for a meaningful
  > Mars→Moon transfer evaluation; cross-body sample sizes below that
  > produce non-interpretable transfer-learning deltas). CPU-feasible
  > feature-based fusion (Step 21.1 logistic-regression prototype)
  > remains the G1 path; DL pretraining on free Colab/Kaggle GPU
  > tiers stays an option if needed, still $0."
- **Why deferred in this paper**: at N=21 DTMs / 278 rows / 34
  registry-wide positives the MGC3 transfer would produce non-interpretable
  deltas. The PU-learning baseline (§3.3) is the same Mars→Moon
  cross-body lesson learned at the feature-engineering level
  (the MGC3 skylight morphology proxy flows through the `span_m`,
  `sag_per_span`, and `log_sag_x_score` features).
- **Sketch (no execution)**: a PyTorch ImageNet-style pretrained
  ResNet-18 fine-tuned on the MGC3 HiRISE skylight tile crops, then
  re-finetuned on the 21 NAC DTMs around each rank-1 candidate;
  freeze all but the final FC; report F1 / AUC on the held-out
  mare basin. **Cost**: ~8 GPU-hours at the Colab free tier; $0;
  sequenced for the Cycles 3–5 close.

### 3.5 Multi-evidence stacking (sketch; deferred to Paper 3)

- **Goal** (verbatim from v5 §8 WP3 line 493–506):
  > "Co-register all Tier-D layers to SLDEM2015. Build the
  > hierarchical multi-resolution model (Pyro/NumPyro Bayesian, or a
  > GNN over nested cells) bridging 2 m to 30 km per the Section 3
  > hierarchy. Kriged distortion surfaces enter as an explicit per-DTM
  > uncertainty layer rather than being discarded. Positive-
  > unlabeled learning over ~20 positives with no verified negatives;
  > one-class and anomaly baselines; MGC3 + HiRISE cross-body
  > pretraining with explicit domain-gap reporting; conformal
  > prediction for calibrated coverage. Physics-informed screening
  > encoding 60-300 m stability bounds as a prior, with protolith
  > competence as a covariate. Scope: Marius Hills + Tranquillitatis
  > + Ingenii.
  > GATE G3: fusion beats every single-stream baseline on calibrated
  > metrics on the held-out basin."
- **Status**: **DEFERRED to Paper 3**. Paper 2 closes G2 (the
  annotated test-bed registry + evaluation protocol + PU-ranking
  baseline); Paper 3 closes G3 (the multi-
  evidence fusion on Marius Hills + Tranquillitatis + Ingenii).
- **What Paper 2 ships as the precursor**: the §3.3 PU baseline IS
  the v5 WP3 positive-unlabeled learning kernel — the same
  `pulearn + LogisticRegression` configuration, the same 278-row
  feature matrix, the same frozen random_state=42. When GRAIL/
  Diviner/illumination features arrive (Cycles 3–5 close → P3.1d
  Tier-D co-registration), the same harness extends.
- **Tier-A promotion rule** (verbatim from registry schema lines
  28–30): tier A requires two-independent-methods agreement. The
  I10 inspection rules (§4.3) plus the v5 I14 funnel disqualifier
  (§4.4) are the gate to that promotion.

---

## 4. Results

### 4.1 Registry summary table (annotated test-bed; 278 rows; tier distribution; FP per 10⁴ km²)

- **Below-floor annotation is a label, not a gap**: the 233
  below-floor rows are a deliberately retained, labelled output of
  the resolution floor — they emerged from the per-DTM `local_Amin`
  limits (the operational counterpart of Paper 1's
  degradation-ladder limits, §4.6 there); the design choice was to
  retain and label them, not to discard them. The test-bed thereby
  measures where void-candidate inference is NOT possible at
  current DTM resolution.
- **Headline aggregate** (verbatim from
  `transfer_summary.json.aggregate`):
  - `n_dtms_with_score_raster = 21`
  - `n_dtm_rung_pairs = 54`
  - `n_candidates = 278`
  - `n_above_local_floor = 45`
  - `n_below_local_floor = 233`
  - `n_tier_B = 3` — the value frozen in the JSON (generated
    2026-08-23, i.e. the **pre-downgrade** count). The registry
    carries the post-hoc downgrade to **0**: per the 2026-08-22
    skeptic Cycle-1 verdict, the 3 MARIUSPIT01 rows that earned
    tier B by "rille intersection within 100 m" were downgraded to
    tier C with the I14-funnel-risk note (§4.4); the registry CSV
    confirms A=0 / B=0 / C=278. The frozen JSON was not
    regenerated after the downgrade (frozen-artifact discipline),
    so the JSON value and the registry state differ by audit-trail
    design — both are quoted here, with no silent substitution
  - `n_tier_A = 0`
  - `n_fp = 9` (all at 2 sites with catalogued pits: FECUNPIT 6,
    TRANQPIT1 3)
  - `n_tp = 14`
  - `total_area_km2 = 24062.96022518323`
  - `fp_per_1e4km2 = 3.74018820451733`
  - `fp_per_1e4km2_ci95_lo = 1.7102522128891549`
  - `fp_per_1e4km2_ci95_hi = 7.100042260610549`
  - Interpretation: calibration-context rate, selection-biased to
    catalogued pits; NOT a random-mare survey rate
- **Per-rung table** (verbatim from `transfer_summary.json.per_rung`):

  | Rung | n_cand | n_above_floor | n_fp | n_tp | area (km²) | FP/10⁴ km² | 95% CI |
  |-----:|-------:|--------------:|-----:|-----:|-----------:|-----------:|--------|
  | 2 m | 74 | 10 | 0 | 3 | 4,108.03 | 0.00 | [0.00, 7.29] |
  | 4 m | 99 | 16 | 3 | 5 | 9,915.07 | 3.03 | [0.62, 8.84] |
  | 5 m | 101 | 18 | 6 | 5 | 9,589.24 | 6.26 | [2.30, 13.62] |
  | 8 m | 4 | 1 | 0 | 1 | 450.62 | 0.00 | [0.00, 66.48] |
  | **Aggregate** | **278** | **45** | **9** | **14** | **24,062.96** | **3.74** | **[1.71, 7.10]** |

- **Per-DTM FP rate** (representative subset; full 21-DTM block in
  `transfer_summary.json.per_dtm`):

  | DTM | n_fp | area (km²) | FP/10⁴ km² | 95% CI |
  |---:|-----:|-----------:|-----------:|--------|
  | TRANQPIT1 | 3 | 124.79 | **240.41** | [49.58, 702.58] |
  | FECUNPIT | 6 | 1,340.08 | 44.77 | [16.43, 97.45] |
  | MARIUSPIT01 | 0 | 901.24 | 0.00 | [0.00, 33.24] |
  | INGENIIPIT | 0 | 556.43 | 0.00 | [0.00, 53.84] |
  | FECNDITATS2 | 0 | 1,994.39 | 0.00 | [0.00, 15.02] |
  | PRCLRMPIT01 | 0 | 1,544.74 | 0.00 | [0.00, 19.39] |
  | SWFECUNPIT1 | 0 | 1,348.37 | 0.00 | [0.00, 22.22] |
  | IRIDIUMPIT1 | 0 | 1,621.73 | 0.00 | [0.00, 18.47] |
  | KINGCRATER2 | 0 | 550.43 | 0.00 | [0.00, 54.43] |
  | KINGCRATER3 | 0 | 567.35 | 0.00 | [0.00, 52.80] |
  | KINGCRATER4 | 0 | 588.48 | 0.00 | [0.00, 50.91] |
  | GRUITHUIS17 | 0 | 2,320.91 | 0.00 | [0.00, 12.91] |
  | GRUITHMARE2 | 0 | 2,258.77 | 0.00 | [0.00, 13.26] |
  | MARIUSCONE | 0 | 1,626.21 | 0.00 | [0.00, 18.42] |
  | FRESHMELT / FRESHMELT1 | 0 | 1,540.91 | 0.00 | (below-floor; terrain_extrapolation) |
  | TYCHOPK / 02 / 03 / 04 / 07 | 0 | 5,177.49 | 0.00 | (below-floor; terrain_extrapolation) |

- **Honest per-DTM headline** (Paper 1 §4.2): the only per-DTM rate
  with a usable interval is TRANQPIT1 at 240.41 [49.58, 702.58] per
  10⁴ km² (n=4); the aggregate's move from 6.06 to 3.74 reflects the
  14,840 → 24,062.96 km² denominator increase, not a chain change.
- **Where the 9 FPs sit** (Paper 1 §4.2): 9 of 9 at 2 sites with
  catalogued pits — FECUNPIT 6 (amplitudes 155/140/34 m) and
  TRANQPIT1 3 (amplitudes 95.4/57.4/48.8 m); visual inspection
  pending; G2 §3 row 11.
- **Tranquillitatis carve-out** (Paper 1 §6): the radar conduit
  beneath Mare Tranquillitatis is the single subsurface lunar
  structure with instrumented evidence (Carrer 2024); no subsurface
  verification exists today.

### 4.2 PU-learning baseline vs extended (v1 → v2)

- **Headline**: v1 F1 0.857 → v2 F1 0.909; AUC 0.897 → 0.931
  (5 → 19 features) — all on a random row split, **leak-inflated**
  (duplicate features and shared DTMs could span train/test); the
  D1 leak-free re-evaluation (run B, 15 morphometric features)
  gives pooled OOF **F1 0.824 [cluster-bootstrap 0.35, 0.98] /
  AUC 0.930 [0.49, 1.00]** over 117 active rows (§3.3); the
  19-feature diagnostic run (A) yields identical 0.5-threshold
  decisions (0/117 differ); wall time **0.04 s** (v2 run).
- **Per-feature importance** (full table from JSON
  `all_feature_coefficients`, 19 rows; descending |coef|):

  | Rank | Feature | Coef | Sign |
  |---:|---|---:|---|
  | 1 | log_sag_amp_m | +1.392 | positive |
  | 2 | has_12km_FP | −0.734 | negative |
  | 3 | log_sag_x_score | +0.672 | positive |
  | 4 | sag_per_span | −0.644 | negative |
  | 5 | log_span_m | +0.612 | positive |
  | 6 | has_terrain_extrap | −0.604 | negative |
  | 7 | log_conf_dist_chain_m | −0.587 | negative |
  | 8 | score | −0.559 | negative |
  | 9 | rung_cm | −0.366 | negative |
  | 10 | span_m | +0.334 | positive |
  | 11 | sag_amp_m | +0.324 | positive |
  | 12 | log_score | +0.247 | positive |
  | 13 | conf_dist_rille_m | −0.187 | negative |
  | 14 | log_conf_dist_rille_m | +0.180 | positive |
  | 15 | has_deep_pit_low_vesselness | −0.154 | negative |
  | 16 | conf_dist_chain_m | −0.034 | negative |
  | 17 | is_single_method_morphometry | +0.019 | positive |
  | 18 | n_confusion_keys_present | +0.019 | positive |
  | 19 | has_funnel_risk | −0.019 | negative |

- **Interpretation hooks**:
  - `log_sag_amp_m` (+1.39) — the strongest pull toward positive:
    bigger sag amplitudes look more like catalogued pits (sanity
    check passes)
  - `has_12km_FP` (−0.73) — the TRANQPIT1 12-km FPs correctly
    pull toward unlabeled (the v2 model has learned the FP
    family annotation)
  - `sag_per_span` (−0.64) — shallow, broad depressions (the
    deep-pit low-vesselness signature) correctly pull toward
    unlabeled
  - `log_sag_x_score` (+0.67) — high score × log-sag synergy
    identifies the genuine void-candidate shape
- **Ranking use**: rank the 244 registry-wide unlabeled ML-detected
  sags (102 active after superseded-duplicate exclusion) by
  predicted P(positive); the top-K is the visual-inspection short-
  list. PU-baseline provides a principled, frozen, reproducible
  short-list ordering for the I10 inspection discipline (§4.3).
- **Calibration baseline** (verbatim from JSON `calibration_baseline`):
  - `n_fp = 9`, `n_tp = 14` (from the G2 transfer)
  - Source: `01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json`

### 4.3 I10 apparent-FP inspection rules (3 capture paths from the user-completion entry)

- **v5 §9 I10 verbatim** (master plan line 562–563):
  > "Every apparent FP manually inspected before scoring, with a
  > separate 'unlabelled candidate' class reported (I10)."
- **Reichenzeller 2026 I10 source** (verbatim from
  `prior_art_matrix.csv` Reichenzeller row, "inherited components"
  column):
  > "inspect-every-apparent-FP discipline (I10)"
  Reichenzeller's headline number on this discipline: "21 of 34
  apparent FPs were unlabelled true positives" (Powell / Reichenzeller
  2026 row); the parallel finding in LUNARVOID is that the
  catalogued-pits-only framing preserves the analogous discipline
  for lunar work — but the lunar side lacks the labelled forest
  inventory Reichenzeller had.
- **Three capture paths for the 27 backlog candidates** (verbatim
  from `notes/findings.md` line 783–792, "2026-08-28 User-completed
  visual inspection"):
  1. **HTML helper (Chrome save)** — "Saving the helper HTML via
     Ctrl+S in Chrome (state IS preserved in `chrome-cli` saves but
     NOT in plain file saves), then re-running inspection"
  2. **Plain-text verdicts file** — "Writing verdicts in a structured
     plain-text file (`01_WORKSPACE/admin/visual_inspection_verdicts.txt`)
     with the format: `<cluster_id>: <verdict_label>` per line"
  3. **Chat dictation** — "Dictating verdicts in chat"
- **Audit-trail state @ 2026-08-28** (verbatim from `findings.md`
  line 783–786, 792):
  > "User verbally confirmed inspection completion but did not record
  > per-cluster verdicts in a form the orchestrator can ingest. ...
  > Until verdicts are captured, the 27 candidates remain at tier C
  > with their existing annotations. **No tier-B promotions applied
  > automatically.**"
- **What this means for the paper**: Paper 2 must explicitly state
  that visual-inspection verdicts are **not on-disk**; the I10
  discipline is *applied* (the inspection happened) but not
  *captured* (the per-cluster labels are missing). This is honest
  and required by the v5 §9 mandatory reporting.
- **Suggested inspection-short-list from PU baseline** (the new
  contribution): use §4.2 to rank the 244 registry-wide unlabeled
  sags (102 active); the top-K
  becomes the I10 inspection short-list for the next visual-
  inspection round. Concrete proposal: top-20 from the PU ranking
  → 20 short-listed candidates → user-driven LROC QuickMap walk-
  through → verdicts captured in `visual_inspection_verdicts.txt`
  per capture path 2. ~30–60 min user time; $0 cost.
- **Backlog candidates** (verbatim from `findings.md` line 683–711):
  - **FECUNPIT**: 3 unique large depressions at the DTM north end;
    amplitudes 155/140/34 m; rungs 4m + 5m; the 6 registry rows
    collapse to 3 unique features. Distances: 552.5 m (r001+r002)
    and 138.1 m (r003) from the NEAREST catalogued pit. r003 at
    138 m is borderline-TP under a 150 m tolerance.
  - **TRANQPIT1**: 3 large-amplitude FPs (12-km scale; r001 95.4 m,
    r002 57.4 m, r003 48.8 m) at lat ~8.75 N, lon ~33.20 E; registry
    rows LV-TRANQPIT1-0500cm-r001/r002/r003; cross-reference to
    "12-km-scale FP from pit; possible floor-fractured crater rim /
    ejecta / modification — visual inspection required to confirm
    FP label".
  - **INGENIIPIT**: ring artifacts r002–r008 at 2/4/5 m rungs (23
    rows total, all within ~10 km of r001); cross-reference to "ring
    artifact around catalogued pit r001; not an independent void
    candidate".

### 4.4 I14 funnel-pit failure (MARIUSPIT01 case study)

- **The pre-registered failure mode** (Paper 1 §4.4, failure mode 1):
  MARIUSPIT01 behaves as the v5 I14 pre-registration predicted — top
  score 5.04 with Frangi vesselness 0.05, the sink-fill draining
  sideways into Rille A so that the funnel geometry muddles the score.
  Documented in `notes/2026-08-19_task4_sweep_notes.md`.
- **2026-08-22 skeptic finding** (verbatim from `findings.md`
  line 274–283):
  > "**TIER-B INVERSION OF I14 FUNNEL (CRITICAL)** — the 3 tier-B
  > rows (MARIUSPIT01-0400cm-r001, r002, -0800cm-r002) earn tier B
  > by the rule 'rille intersection within 100 m'
  > (`METHODS.md` L213–215). This is the **pre-registered v5 I14
  > failure mode** (pits incised into rilles spill sideways — it is
  > a FINDING in this project, see 2026-08-21 entries above).
  > Promoting by the same criterion inverts a known confounder into
  > a positive signal. **Downgrade all 3 to tier C with note 'I14
  > funnel risk — rille intersection is the failure mode, not
  > independent confirmation'** (HIGH — must fix before any G1
  > registry citation). Tier-B count collapses 3 → 0; tier A stays 0."
- **What this paper IS and IS NOT, redux** (verbatim from findings
  line 717 — claim discipline re-stated after Cycle 1):
  > "Claim discipline re-stated: never write 'is a void', 'represents
  > a tube', 'indicates subsurface' for these two — write
  > 'morphometrically similar to void signature' or 'warrants NAC
  > browse confirmation'."
- **Concrete registry evidence** (from
  `transfer_summary.json.per_dtm.MARIUSPIT01`):
  - rungs: [4.0, 8.0]; n_candidates=6; n_above_local_floor=3;
    n_below_local_floor=3; n_tier_B=3 (pre-downgrade) → 0
    (post-downgrade); n_fp=0; n_tp=2; top_score=0.00784;
    local_Amin=4.137601 m; area=901.24 km²; fp_per_10⁴km² = 0.00
- **Why it matters for Paper 2**: the I14 rule disqualifies one of
  the v5 master plan's tier-B promotion criteria. Paper 2 uses
  this as a case study in the *kind* of confound that the v5 §9
  I10 discipline is designed to catch — but only when verdicts are
  captured on-disk.

### 4.5 Visual inspection outcomes (honest state @ 2026-08-28)

- **State** (verbatim from `findings.md` line 783–792): 24
  candidates verbally confirmed inspected; 3 FECUNPIT features
  inspected as the first batch; helper HTML at
  `admin/visual_inspection_helper.html` shows no `checked` attributes
  on radio buttons; verdicts **not on-disk**; **no tier-B promotions
  applied automatically**.
- **What Paper 2 claims from the inspection**: zero per-cluster
  promoted tiers; zero new tier-A promotions; zero FPs reclassified
  to TPs; zero ring artefacts reclassified. The 27 backlog
  candidates remain tier C with their existing annotations.
- **What Paper 2 does NOT claim**: any candidate cluster has been
  "verified" as a tube or a non-tube by visual inspection. The I10
  inspection discipline requires verdicts on-disk; we have none.
- **Next-step proposal** (the I10 path forward): use the §4.2 PU
  ranking to produce a top-20 short-list; user walks the 20 via
  LROC QuickMap; verdicts captured per capture path 2
  (`visual_inspection_verdicts.txt`); the I10 discipline then
  produces the "unlabelled candidate" class required by v5 §9.
  Sequenced into the post-Paper-2 backlog; $0 cost; ~30–60 min.

### 4.6 Unique-feature re-accounting (rows vs unique features; FP per 10⁴ km²)

- **Registry annotation scheme**: the 278-row registry resolves to 117
  unique features via `superseded_by` links (117 ACTIVE primary rows,
  161 SUPERSEDED children); the 45 above-floor rows resolve to 21
  unique features. A group inherits the class of its primary row.
- **Both accountings side by side** (all numbers verbatim from
  `data/outputs/wp2_sag/unique_accounting_2026-09-07.json`;
  Poisson-exact (Garwood) 95% CIs; same 24,062.96 km² denominator):

  | Accounting | TP | FP | Ring | Funnel | FP per 10⁴ km² | 95% CI |
  |---|---:|---:|---:|---:|---:|---|
  | Row-based (frozen, Paper 1) | 14 | 9 | 21 | 1 | 3.74 | [1.71, 7.10] |
  | Unique-feature (this work) | 6 | 5 | 9 | 1 | **2.08** | **[0.67, 4.85]** |

  The row-based rate reproduces the frozen Paper 1 value to better
  than 10⁻⁹ (regression check: PASS on counts, rate, and CI at full
  stored precision).
- **Grouping-key disclosure**: unique counting groups rows by DTM at a
  ~30 m co-location radius (3-decimal lon/lat bucketing), matching the
  pit-atlas positional accuracy (~30 m); a group is FP iff its primary
  row is FP.
- **Sensitivity**: the unique FP count is stable at 5 across 30–60 m
  radii; coarser grouping (~300 m) merges to 3; finer (~3 m) splits
  to 6; a 100 m radius merges two FECUNPIT structures to 4. The 30 m
  scale is the pre-registered atlas-accuracy choice, not post-hoc.
- **Geometry of the FP sites** (registry coordinates, haversine
  R = 1,737,400 m): TRANQPIT1's 3 row-FPs resolve to 2 unique
  structures (a row pair co-located at 16.5 m — one structure scored
  at two rungs, r003 registry-SUPERSEDED — and a third row 132.8 m
  away); FECUNPIT's 6 row-FPs resolve to 3 unique structures.
- **Framing**: the unique-feature rate is the more conservative
  survey-relevant quantity (one count per spatial feature, not one per
  rung row); the row-based rate is retained as the frozen
  calibration-context anchor. Neither is a detection rate.

---

## 5. Discussion

### 5.1 What the test-bed supports (annotated registry; calibrated inference; honest baselines)

- **The registry's label mass**: of 278 tier-C rows, the 45
  above-floor rows (14 TP / 9 FP / 21 ring / 1 funnel) support
  **14 above-floor inferred void candidates**, all tier-C
  single-method morphometry, per the frozen Paper 1 accounting
  (§4.2 there), with all 14 candidates inferred from morphometry
  alone.   The remaining **233 of 278 rows (83.8%) are below-floor
  and explicitly not inferable** — an emergent consequence of the
  resolution floor, deliberately retained and labelled (not a
  designed output, not a deficiency): the registry measures where
  void-candidate inference is NOT possible at current DTM
  resolution, which is the operational counterpart of Paper 1's
  degradation-ladder limits.
- **Aggregate FP 3.74 [1.71, 7.10] per 10⁴ km² over 24,062.96 km²**
  is **calibration-context only**, NOT a survey rate, NOT a
  random-mare estimate. The selection bias toward catalogued pits
  is preserved (all 21 on-disk DTMs are pit-associated or pit-rich).
- **The PU baseline ranks the unlabeled sags** with a defensible
  positive-class proxy (catalogued-pit rank-1 + ring-artefact rows);
  leak-free leave-one-DTM-out pooled OOF **F1 0.824
  [cluster-bootstrap 0.35, 0.98] / AUC 0.930 [0.49, 1.00]** over
  117 active rows, run B with the four annotation-derived flags
  removed (supersedes the leak-inflated random-split F1 0.909 /
  AUC 0.931; §3.3) — promising, but consistent with chance at the
  CI lower bounds: a small-n feasibility result (15 positives),
  not classifier validation.
- **No claim of detection**. The Tranquillitatis radar conduit is
  still the sole subsurface lunar structure supported by any
  instrument (Carrer 2024; v5).
- **Honest per-DTM headline**: TRANQPIT1 240.41 [49.58, 702.58]
  per 10⁴ km² (n=4) is the only per-DTM rate with a usable CI;
  every other DTMs is n_fp=0 because the calibration-context
  framing selects for catalogued-pit hosts.

### 5.2 Honest limitations

*(D4 contribution 4: the limitations below are **outputs of the
protocol** — properties the test-bed measures and reports (small-n,
positive-mass concentration, wide CIs), not defects hidden from the
reader. An evaluation resource that could not surface them would not
be doing its job.)*

- **Catalogued-pits-only sampling**: 0/649 random-mare DTMs in
  scope (Paper 1 §5.4); all 278 registry rows derive from the 21
  pit-associated NAC DTMs, and at the atlas level only 82 of the
  278 catalogued pits in the WP0 scope map overlap a published NAC
  DTM (196 do not;
  `data/outputs/wp0_scope_map/coverage_by_terrain_all_278_pits.csv`).
  Any survey-grade claim requires Kaguya/SP/Chang'e DTMs (deferred)
  or a much larger NAC DTM pool (Tier-1 rental deferred).
- **PU-learning positives are local-max proxies**, not ground
  truth. The v2 registry-wide positive set (34 positives = 7
  catalogued-pit-DTMS rank-1 + 24 INGENIIPIT ring-artefact + 3
  other rank-1 catalogued-pit hits). A held-out mare basin is not
  implementable at N=21 DTMs (master plan §9 requirement). Under
  the D1 leak-free evaluation the active set carries only 15
  positives (10 concentrated in the INGENIIPIT fold): the PU
  metrics are a feasibility estimate with wide DTM-cluster-
  bootstrap CIs (F1 0.35–0.98, AUC 0.49–1.00; lower bounds near
  chance), not production-classifier validation.
- **MGC3 / multi-evidence stacking deferred** (§3.4 / §3.5): the
  cross-body and the multi-evidence claims require Cycles 3–5 close
  + Tier-1 rental + Cycles 1–2 of WP3 (multi-illumination azimuth
  test deferred per findings 2026-08-22 P4.3 review).
- **Tranquillitatis carve-out**: nothing subsurface is verifiable
  today except the radar-evidenced Tranquillitatis conduit. This
  paper does not change that statement.
- **Visual-inspection verdicts not on-disk**: the 27 backlog
  candidates remain tier C; the I10 discipline is applied but not
  captured (per-cluster labels missing; §4.5).
- **I2 SLDEM2015 cross-validation deferred**: the kriging
  correction is self-validated at TRANQPIT1 (RMSE 0.373 → 0.327 m);
  SLDEM2015 absolute-elevation cross-check not implemented (Paper 1
  §5.4).
- **I12 confound covariates not exercised**: slope and illumination
  partially addressed via the +10° slope mask (Paper 1 §3.2)
  and the 12-geometry Hapke grid (Paper 1 §4.5), but a formal
  I12-style null test is not run; sequenced
  into the LLTB-1 v0.2 backlog.
- **Sample-size power calculation not run** (limitation stated in
  Paper 1 §5.4): the aggregate 3.74 [1.71, 7.10] per 10⁴ km² figure
  (n_fp=9) carries a Poisson-exact (Garwood) 95% CI but no formal
  a-priori power analysis. A ±50% precision goal for a 1% FP-rate
  estimate would need roughly 16,000 FP trials — about 40× the
  population available today. Formally deferred until the 30
  random-mare sites close.

### 5.3 Comparison to ESSA (Le Corre 2025): inference vs detection

- ESSA headline (from `prior_art_matrix.csv` Le Corre row, to be
  sourced if cited in v2): Mask R-CNN trained on Lunar Pit Atlas
  labels with Martian HiRISE and synthetic implanted-pit
  augmentation; **reports detection F1** on a label set that
  includes the ~281 catalogued pits (Wagner & Robinson 2021). Its
  public release (georeferenced detection shapefiles, open Zenodo
  weights, code, and the training product list) is a
  detection-training dataset — the genre from which the
  inference-evaluation test-bed of this paper is distinct (§2).
- LUNARVOID Paper 2 headline: **F1 0.824 (run B, leak-free LODO;
  §3.3) is
  a RANKING F1 on inferred-void candidates**, not a detection F1;
  positives are
  local-max proxies, negatives are unlabeled sags, no detection
  claim is made.
- **Both are valid framings; they answer different questions**:
  - ESSA answers "given a labeled catalogued pit, can the model
    re-detect it?"
  - LUNARVOID Paper 2 answers "given the unlabeled ML-detected sag
    surface, can we rank it by similarity to the catalogued-pit
    morphology?"
- **The boundary**: ESSA uses the catalogued pits as labels
  (master plan R8/R9 risk — we cite, position as inference vs
  detection, **never** use as a label source). LUNARVOID Paper 2
  uses the catalogued pits as the positive-class proxy for the PU
  ranking (this is the v5 §9 calibration-context framing, not a
  detection labelling claim).
- **Convergent finding**: the catalogued pits are the right
  positive class; the FP family (12-km FPs, deep-pit low-
  vesselness, central-peak-relief) is the right negative class;
  the model discriminates them with leak-free LODO F1 0.824
  [cluster-bootstrap 0.35, 0.98] (§3.3). **Diverge** on
  interpretation: ESSA claims detection; LUNARVOID claims ranking.
- **Master plan R8 verbatim** (line 592–593):
  > "Prior-art collision with ESSA — cite early, position as
  > inference vs detection, audit product-list overlap."

---

## 6. Conclusion

*(Placeholder — per user instruction, no new prose beyond pointers.)*

- **One-paragraph summary** (template from Paper 1 §6, to be
  written by user):
  - LLTB-1 v0.5 + the Cycles 1-2 close closed the G2 deliverable —
    the v5 "regional candidate catalogue", delivered honestly under
    the D4 reframe as an **annotated test-bed registry** with
    per-candidate evidence vectors, confusion-cleared lower-bound
    sag framing, and B1 `superseded_by` duplicate links (117
    unique features).
  - Paper 2 closes **G2** as an annotated test-bed registry +
    leakage-corrected evaluation protocol (community-benchmark
    status remains the forward-looking goal, gated on the E3
    Zenodo deposit): 278 tier-C morphometry
    rows (45 above-floor; 14 above-floor inferred void candidates;
    **233 below-floor — the registry's other half, measuring where
    inference is NOT yet possible**, the resolution-limit
    connection to Paper 1); aggregate FP
    3.74 [1.71, 7.10] per 10⁴ km² over 24,062.96 km² (calibration-
    context, NOT survey; unique-feature accounting 2.08 [0.67,
    4.85], §4.6); PU-learning baseline run B (15
    morphometric features; four annotation-derived flags removed;
    decisions identical to the 19-feature diagnostic run) leak-free
    leave-one-DTM-out pooled OOF F1 0.824 [DTM-cluster-bootstrap
    95% CI 0.35, 0.98] / AUC 0.930 [0.49, 1.00], 14/15 positives
    recovered (117 active rows; 161 superseded duplicates
    excluded) — lower CI bounds near chance: a small-n feasibility
    result (15 positives), not classifier validation.
  - The I10 inspection discipline + I14 funnel-pit disqualifier
    protect against the two pre-registered failure modes (the v5
    §9 "unlabelled candidate" class; the v5 I14 rille-intersection
    inversion); the I14 failure is retained in the registry as its
    first known-hard-case entry.
  - Tier-A promotion count remains 0; nothing subsurface on the
    Moon is verifiable today except the Tranquillitatis radar
    conduit (Carrer 2024; v5).
- **Forward pointer to Paper 3** (multi-evidence fusion per v5):
  - WP3 scope: Marius Hills + Tranquillitatis + Ingenii (master
    plan §8 WP3 line 504).
  - Pyro/NumPyro Bayesian or GNN over nested cells bridging 2 m
    to 30 km per the v5 §3 hierarchy.
  - Tier-D confirmation layers: GRAIL (GRGM1200A l_max=680
    subset v0.1; full l_max=1200 deferred), Diviner GHRM thermal
    (P4.3 INCONCLUSIVE at 2/7 coverage), multi-illumination
    stacking (P4.2 deferred).
  - Conformal prediction for calibrated coverage; one-class and
    anomaly baselines; physics-informed screening encoding 60–300 m
    stability bounds as a prior with protolith competence as a
    covariate.
  - G3 pass criterion: fusion beats every single-stream baseline
    on calibrated metrics on the held-out basin.

---

## Acknowledgements (reuses Paper 1 template)

- NASA Pits and Caves analog dataset (Wong 2014); research-use
  licence acknowledged.
- LROC NAC team for the published DTMs that the v5 primitive is
  validated on.
- The DLR Institute of Data Science, whose open publication of the
  Mueller 2026 / Reichenzeller 2026 methods and code this pipeline
  builds on.
- **NEW for Paper 2** (additive to Paper 1): Cushing 2015 / 2017
  MGC3 catalog authors (cross-body pretraining source); Williams
  2017 / Powell 2023 Diviner team; Hurwitz 2013 rille shapefile
  authors; Wagner & Robinson 2021 Pit Atlas team.

## Author contributions (CRediT taxonomy)

Single-author manuscript. All CRediT roles assigned to the LUNARVOID
team (per Paper 1 §Author contributions template). The PU-learning
v2 baseline was produced by the geo-coder agent (config + frozen
recipe) under orchestrator dispatch; the visual-inspection walk-
through was user-driven on 2026-08-28.

## Conflict of interest

The authors declare no competing interests.

## Data and code availability

- **LLTB-1 v0.1 / v0.4 / v0.5**: derived rasters only
  (`~/lunarvoid/data/lltb1/<site>/`); LLTB-1 v0.4 release note
  documents the per-rung slope-threshold tuning that lifted F1
  from 0.277 to 0.362 at IndianTunnel_NorthSurface @ 1 m @ 45°.
- **NASA analog dataset** (Wong 2014): research / academic use only,
  fetch-script in `code/wp1_lla/convert_f32.py` and
  `code/setup/extract_rar.py`. Licence gate before any
  redistribution.
- **LROC NAC DTMs (PDS archive products)**: PDS public domain;
  fetched by product ID
  only (never mirrored in the repo; per AGENTS.md / data
  discipline). **Caveat (MANIFEST licence note)**: LROC/ASU *web*
  products (QuickMap, previews, and the Pit Atlas pages from which
  the registry's label set derives) carry ASU terms that differ
  from the PDS archive — the PDS-public-domain statement covers
  the archived DTMs, not ASU web-served material.
- **PU-learning v2 baseline** (superseded evaluation; retained for
  provenance — its random split was leak-inflated):
  `data/outputs/wp5_fusion/pu_learning_registry_baseline_v2.json`
  (commit forthcoming); train script at
  `code/wp5_fusion/pu_learning_extended.py`; reproducible from
  the registry + random_state=42. (A6 fix 2026-09-04: the earlier
  `pu_learning_baseline_v2.py` reference did not exist; the v2
  baseline is `pu_learning_extended.py`.)
- **PU-learning D1 leak-free group-split evaluation** (the paper's
  canonical PU metrics): `data/outputs/wp5_fusion/
  pu_learning_groupsplit_2026-09-09.json` — 117 active rows (161
  SUPERSEDED duplicates excluded), 21 leave-one-DTM-out folds,
  triple-run ablation (run B 15-feature headline / run A 19-feature
  diagnostic upper bound / run C 14-feature rung-ablation
  sensitivity), per-row out-of-fold predictions, DTM-cluster-
  bootstrap (headline) and row-bootstrap (secondary) 95% CIs,
  leave-INGENIIPIT-out summaries, and threshold sensitivity stored
  inside; registry md5 `a60fb52152e33f37e9052434ad026a6e`
  recorded in the JSON.
- **G2 transfer summary** (shared with Paper 1): frozen
  calibration at `data/outputs/wp2_sag/transfer/calibration_transqpit1.json`
  (md5 `2597002375206aba3119c240c373ad62` unchanged); transfer
  output at `data/outputs/wp2_sag/transfer/transfer_summary.json`
  (2026-08-23 freeze).
- **Unique-feature re-accounting** (§4.6): deterministic re-count of
  the registry at the pre-registered 30 m atlas-accuracy grouping;
  `data/outputs/wp2_sag/unique_accounting_2026-09-07.json`
  (registry md5 `a60fb52152e33f37e9052434ad026a6e`).
- **Candidate registry**: `data/candidate_registry.csv` (310 lines,
  32-line header + 278 data rows; the schema + tier-discipline
  comments + provenance line are part of the artifact).
- **Planned versioned release (E3)**: a Zenodo deposition carrying a
  versioned DOI is scheduled as the E3 deliverable, bundling the
  annotated registry (`candidate_registry.csv`), the annotation
  METHODS / schema documentation, and the evaluation-protocol
  scripts (duplicate exclusion + leave-one-DTM-out folds +
  train-fold-only preprocessing + identity-proxy ablation +
  DTM-cluster bootstrap); the frozen snapshot will be identified by
  the registry md5 `a60fb52152e33f37e9052434ad026a6e`. Release
  conventions follow comparable open lunar dataset deposits
  (Grethen et al. 2025). Licence audit before any redistribution
  per AGENTS.md data discipline: PDS *archive* products are public
  domain, but LROC/ASU *web*-product terms differ from the PDS
  archive (MANIFEST licence note) — because the registry's labels
  are Pit-Atlas-derived, an explicit ASU-terms audit of the label
  source is required **before** the E3 deposit redistributes them;
  NASA-derived annotations are additionally checked for
  research/academic-use restrictions. The deposit is also what
  would qualify the test-bed as a citable community benchmark;
  until it lands, the artifact is an annotated test-bed registry +
  evaluation protocol.
- **Visual inspection helper** (auxiliary, for the I10 capture
  path 1): `admin/visual_inspection_helper.html` (state not
  preserved on plain save; use Chrome `chrome-cli` save or capture
  path 2).
- **Code**: open at the LUNARVOID repository.

---

## References (extends Paper 1's 8 with WP3 fusion + MGC3 + cross-body + benchmark-genre precedents)

*Author-year style (matching the inline citation form used throughout
Paper 2). Sorted alphabetically by first author. **8 references
verified** against the local Zotero library in Paper 1 (8 entries
attached 2026-08-28; DOIs confirmed in Crossref for all 8). Paper 2
adds the following (Zotero attach + DOI verification pending at the
submission milestone; some entries may need user-curation before
submission). The three benchmark-genre entries (Grethen 2025,
Prasad & Mazumder 2026, Purohit et al. 2025) were verified against
arXiv metadata on 2026-09-10 (titles/authors/abstracts; DOIs are
arXiv identifiers). Pre-submission external audit still required:
the Laurier/ASU DTM-attribute pit database is not covered by the
33-ref prior-art matrix and must be audited before the first-claim
is submitted:*

**Shared with Paper 1 (8 references, verified 2026-08-28):**

1. Blair, D.M., Chappaz, L., Sood, R., Melosh, H.J., et al. (2017).
   The structural stability of lunar lava tubes. *Icarus* 282,
   47–55. doi:10.1016/j.icarus.2016.10.008. *— Stability-bound anchor.*
2. Carrer, L., Pozzobon, R., Sauro, F., Patterson, G.W.,
   Hiesinger, H., and the Mini-RF team (2024). Radar evidence of
   an accessible cave conduit on the Moon below the Mare
   Tranquillitatis pit. *Nature Astronomy* 8(9), 1119–1126.
   doi:10.1038/s41550-024-02302-y. *— v5 claim-discipline anchor.*
3. Le Corre, D., Mason, N., Bernard-Salas, J., Mary, D., & Cox,
   N. (2025). New candidate cave entrances on the Moon found
   using deep learning. *Icarus* 441, 116675.
   doi:10.1016/j.icarus.2025.116675. *— ESSA; positioned as
   inference vs detection. The release publishes georeferenced
   detection shapefiles, open weights (Zenodo), code, and the
   training product list — a public detection-training dataset,
   distinct from the inference-evaluation benchmark claimed
   here.*
4. Mueller, R., et al. (2026). Kriged distortion correction after
   ICP registration on snow-covered UAV photogrammetric point
   clouds. *Arctic Science* 12:1–23. doi:10.1139/as-2025-0062.
   *— Source of I1–I7.*
5. Reichenzeller, E., et al. (2026). Vertical Complexity Index
   for overstory tree detection in UAV-LiDAR and SfM forest
   plots. *Forests* 17(8), 807. doi:10.3390/f17080807. *—
   Source of I8–I15 (incl. I10 inspect-every-apparent-FP).*
6. Theinat, A.K., Modiriasari, A., Bobet, A., Melosh, J., Dyke,
   S., Ramirez, J., Maghareh, A., Gomez, D., et al. (2018).
   Geometry and structural stability of lunar lava tubes. AIAA
   SciTech 2018; paper 2018-5185. doi:10.2514/6.2018-5185. *—
   Stability-bounds anchor (with Blair 2017).*
7. Wagner, R.V. & Robinson, M.S. (2021). Lunar Pit Atlas: a
   morphometric compilation of catalogued lunar pits. *LPSC 52*,
   Abstract #2530. *— Primary label set (~281 catalogued pits).*
8. Wong, U., Whittaker, R., Jones, J. & Whittaker, W. (2014).
   NASA Planetary Pits and Caves analog dataset release. NASA
   Ames Research Center. https://ti.arc.nasa.gov/dataset/caves
   *— LLTB-1 ground-truth corpus. Research / academic use only.*

**NEW for Paper 2 (18 planned entries total — 10 firm additions +
8 shared; Zotero attach + DOI verification pending; cite order TBD
by user; +1 optional entry below):**

9. Cushing, G.E. (2015). Mars Global Cave Catalog: a database
   of cave-like features at candidate rover landing sites.
   *LPSC 46*, Abstract #1164. *— MGC3 v1; cross-body
   pretraining source.*
10. Cushing, G.E. (2017). Mars Global Cave Catalog: updates
    and new features. *LPSC 48*, Abstract #1951. *— MGC3 v2;
    HiRISE skylight morphology inventory.*
11. Grethen, C., Gasparini, S., Morin, G., Lebreton, J.,
    Marti, L., & Sanchez-Gestido, M. (2025). Adapting stereo
    vision from objects to 3D lunar surface reconstruction with
    the StereoLunar dataset. *arXiv:2510.18172*.
    doi:10.48550/arXiv.2510.18172. *— Open lunar stereo-pair
    dataset; benchmark-genre precedent; dataset-release
    conventions (versioned DOI).*
12. Hurwitz, D.M., et al. (2013). The sinuous rilles of
    Marius Hills. *Icarus* 225, 1094–1107. *— The I5
    confusion layer; I14 funnel-pit prediction.*
13. Powell, T.M., et al. (2023). A high-resolution thermal
    anomaly map of the Moon from LRO Diviner GHRM. *Icarus*
    (submitted/in press). *— The actual 128-ppd product
    sampled at the 7 DTM sites; sub-pixel scale mismatch
    acknowledged.*
14. Pozzobon, R., et al. (2019). Lava tubes on Earth, Moon
    and Mars: a review on their size, morphology, and
    formation mechanisms. *Geosciences* 9(8), 347.
    doi:10.3390/geosciences9080347. *— Earlier work by the
    Carrer group on the same conduit; cited alongside
    Carrer 2024 for completeness.*
15. Prasad, A., & Mazumder, S. (2026). Moonstone: A multimodal
    foundation model and benchmark for lunar remote sensing.
    *arXiv:2607.03644*. doi:10.48550/arXiv.2607.03644. *—
    First lunar multimodal foundation-model benchmark
    (28-channel, ~237 m/px, six downstream tasks); establishes
    the lunar-benchmark genre; explicitly not void/pit
    inference and not meter-scale DTMs — our niche remains
    open.*
16. Purohit, M., Gajera, B., Malaviya, V., Mehta, I.,
    Kasodekar, K., Adler, J., Lu, S., Kerner, H. (2025).
    Mars-Bench: A benchmark for evaluating foundation models
    for Mars science tasks. *arXiv:2510.24010*.
    doi:10.48550/arXiv.2510.24010. *— Mars-science benchmark
    (20 datasets; classification/segmentation/detection);
    genre precedent for standardized planetary-task
    evaluation.*
17. Williams, J.-P., et al. (2017). Cold traps and recent
    thermal behavior of lunar cold spots. *Icarus* 283, 313–
    322. *— Diviner cumulative nighttime temperature; basis
    for P4.3 thermal anomaly stacking.*
 18. Watson, T. H., & Baldini, J. U. L. (2024). Martian cave
     detection via machine learning coupled with visible light
     imagery. [Mask R-CNN (ResNet50) trained jointly on lunar NAC
     imagery, Martian HiRISE pit data, and synthetic implanted
     lunar pits; ~89% bbox / ~96% mask F1 (lunar/Martian).]
     *Icarus* 411, 115952.
     https://doi.org/10.1016/j.icarus.2024.115952 *—
     Detection-training release; v5 R8 prior-art-collision anchor;
     precursor to ESSA (Le Corre 2025). Bibliographic details
     verified against the DOI resolver 2026-09-12; bracketed
     training/F1 summary from `notes/prior_art_matrix.csv` (row
     WatsonBaldini2024).*

*(Optional Paper 2 add — to confirm by user if cited:*
19. *Besserer, J., et al. (2024). Thermal signature of lunar
    lava tubes under simulated illumination conditions.
    *JGR Planets* (submitted/in press).)*