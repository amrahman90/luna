# LUNARVOID — Findings Log (append-only)

Scientific memory: WHAT WE LEARNED, each claim with a traceable
evidence link. (The CHANGELOG records process; this records science.)
Append dated sections only — never edit or delete prior entries.
Reviewed by the skeptic agent; mined by paper-writer.

Format per entry:
`- CLAIM (confidence) — evidence: <path> — caveat: <known weakness>`

---

## findings 2026-08-21 (seed — backfilled headline results)

- Mare Tranquillitatis Pit depth recovered at 129.67 m from NAC DTM
  via Planchon-Darboux fill vs 105 m catalogued (fill-to-spill
  overshoot documented) (HIGH) — evidence:
  `data/outputs/wp0_primitive/pit_recovery_table.csv` — caveat:
  NoData fraction inside 200 m recorded per site.
- 7 of 8 covered pits recover ≥50% of catalogued depth; sole failure
  Marius Hills (14.56/40 m) matches the pre-registered v5 I14
  rille-funnel prediction (HIGH) — evidence: same table; notes
  `notes/2026-08-19_task4_sweep_notes.md`.
- Published NAC DTMs are already LOLA-registered at decimetre level:
  kriged I2 correction moves check-point RMSE only 0.373→0.327 m on
  TRANQPIT1 (1.425→0.541 m on MARIUSPIT01); correction is ~100%
  low-frequency (λ>300 m) and preserves pit depth to +0.05% (HIGH) —
  evidence: `data/outputs/wp0_kriging/*_kriging_metrics.csv`,
  `*_summary.json`.
- Sag detectability floor: sag-band (60–300 m) residual RMS
  1.25–1.38 m on flat mare ⇒ only ≥4 m amplitude sags are
  single-DTM detectable; 1–2 m sags require multi-evidence stacking
  (HIGH — this is the G1 answer) — evidence:
  `data/outputs/wp0_kriging/noise_floor_stats.csv`.
- Sag search recovers the catalogued pit within 100 m as top
  candidate on ALL 8 covered DTMs (scores 1.60–21.06; SW Fecunditatis
  lowest as the only highland site) (HIGH) — evidence:
  `data/outputs/wp2_sag/*/sag_search_summary.json`.
- LLTB-1 v0.4: best honest F1 0.362 (IndianTunnel_NorthSurface 1 m,
  tuned slope 45°); recall 1.00 wherever ≥5 void cells; per-site
  slope tuning regresses on IndianTunnel_cave_1x (use fixed 10°)
  (HIGH) — evidence: `admin/verification_evidence/2026-08-21_v04_tune_slope_verification.json`.

## findings 2026-08-21 (skeptic corrections, G0' report v1.1 review)

- CORRECTION — the 2026-08-21 entry above ("Sag search recovers the
  catalogued pit within 100 m as top candidate on ALL 8 covered DTMs
  (HIGH)") is REFUTED: verifier pit-distance measurement shows
  recovery within 100 m on 4/8 runs only (Ingenii 46 m, top of list;
  MTP 45 m at rank 11/29, score 3.72; Procellarum 38–77 m at ranks
  55/189); on the other 4 runs the closest candidate lies 1.2–2.6 km
  away, and each run's global top score lies 5–29 km from the
  catalogued pit (MTP top 21.06, ~12.5 km NNE) (HIGH, that the
  original claim is false) — evidence:
  `papers/gate_reports/G0prime_report_v1.1.md` row 8;
  `admin/verification_evidence/2026-08-21_z2_pit_distance_verification.md`
  (pending filing) — caveat: corrected claim is "detector responds at
  some real pits; ranking uncalibrated and dominated by uncorroborated
  candidates" at MEDIUM confidence (n=8, Wilson 95% CI on 4/8 ≈
  0.18–0.82; FP/10^4 km² NOT MEASURED; only 21/278 catalogued pits are
  tube-relevant, so pit response ≠ tube response).
- CAVEAT — the sag-floor entry above: pooled sag-band RMS 1.245 m
  (TRANQPIT1) / 1.379 m (MARIUSPIT01) ⇒ 3σ = 3.74 / 4.14 m, so
  "A≥4 m single-DTM detectable" holds strictly only at TRANQPIT1
  (4 m < 4.14 m at Marius). Per-panel RMS spans 0.74–2.05 m (Marius
  P3 local 3σ ≈ 6.1 m); floor sampled at only 2 of ~649 mare DTMs.
  Floor should read "≥5 m at both pooled sites (≥4 m at the quieter
  site)" until per-DTM floors exist (MEDIUM) — evidence:
  `data/outputs/wp0_kriging/noise_floor_stats.csv`. The "3× sag-band
  RMS" rule is a PROJECT CONVENTION; no such multiplier appears in
  v5 §4 (grep-verified 2026-08-21) — do not cite v5 for it.

## 2026-08-22 — skeptic review, Task 12 analog "void ground truth" (verdict: SOUND-with-objections)

- **Relabel required**: `void_mask_gt.tif` is an **entrance-trench +
  skylight footprint** over the NorthSurface window (1,146/1,151
  DTM-overlapping cells are open = 99.6%; roofed-void GT in-window is
  **5 cells / 1.25 m²**). It is NOT valid roofed-void ground truth for
  ladder/sag rung F1: n=5 supports no statistic, and 92.7% of mask cells
  have P-D depth exactly 0 (trench drains out the entrance) — grading a
  sag detector against these labels measures *surface-depression*
  detection, the confounder class (crater floor / rille shoulder), i.e.
  benchmark bias OPPOSITE the lunar sag thesis. v0.5 protocol must:
  (a) rename/flag the artifact; (b) exclude it from sag-rung F1;
  (c) report NorthSurface cave rungs separately with this caveat and
  never fold them into the §8 v0.4 site table.
- **Registration gate statistic**: headline "0.139 m trimmed RMSE" uses
  8,955/342k correspondences (2.6%) at the 0.25 m cap with ICP
  non-converged (100-iter cap, ΔRMS 0.008 ≫ eps 1e-7) and overlap=90%
  assumed vs ~entrance-only actual overlap. Gate on the dense numbers
  (9.3% inliers, 0.490 m RMS) instead. Seed→final yaw consistency
  verified (−102° seed vs −106.6° final; coarse "deg" sign convention
  is inverted, Rz=[[c,s],[−s,c]] — document it).
- **Notes wording fix**: NOTES says mask = "9.28% of valid DTM cells";
  2055/12402 = 16.6%. The 9.28% is the 1,151 DTM-overlapping cells /
  12,402 valid. JSON is correct; the notes sentence conflates.
- **Scale caveat**: analog is informative for trench/corridor morphology
  (9.5–14.5 m width, 50.6 m length) and pipeline mechanics, NOT
  quantitatively for 1–2 m sag amplitude F1 (0.49 m dense RMS ≈ half a
  rung cell; roof-depth p50 1.27 m from n=5 cells).

## finding 2026-08-21 — Indian Tunnel analog registration + mask semantics

Terrestrial analog study (El Malpais, NM); inference-neutral wording —
this constrains pipeline mechanics on Earth data, not any lunar claim.

- Registration (cave cloud → NorthSurface DTM): coarse yaw search + ICP
  (adjust-scale OFF) lands at dense-gate **9.3% inliers <1 m, RMS
  0.490 m**; trimmed ICP RMSE 0.139 m uses only 8,955/342k
  correspondences (2.6%) at the 0.25 m cap; effective overlap is
  **entrance-only 61.6%**, not the assumed 90% (MEDIUM — dense gate is
  the honest statistic) — evidence:
  `data/outputs/wp1_analog/registration/registration_report.json`,
  `coarse_search.json`.
- Corridor morphology: **50.6 m long × 9.5–14.5 m wide** — within the
  lunar-relevant skylight-conduit size class inferred for the
  Tranquillitatis conduit; width comparable to candidate mare tube
  spans (MEDIUM) — evidence: `data/outputs/wp1_analog/NOTES_task12_registration_mask.md`.
- **MASK SEMANTICS (relabel per skeptic, 2026-08-22 review):** the
  rasterized footprint is an **entrance-trench + skylight footprint**,
  NOT roofed-void ground truth (roofed-void in-window = 5 cells /
  1.25 m²; n=5 supports no statistic). It is **excluded from sag-rung
  F1 in v0.5**; NorthSurface cave rungs are reported separately and
  never folded into the §8 v0.4 site table (HIGH — benchmark-bias
  guardrail) — evidence:
  `data/outputs/wp1_analog/void_mask/entrance_trench_skylight_mask_stats.json`.
- Scale caveat: 0.490 m dense RMS ≈ half a rung cell (1 m); analog
  informs registration/mask pipeline mechanics, not 1–2 m sag-F1
  magnitudes (roof-depth p50 1.27 m from n=5 cells).
- All Task-12 artefacts under `data/outputs/wp1_analog/`
  (registration/, void_mask/, NOTES_task12_registration_mask.md);
  code under `code/wp1_analog/` (6 modules).

## 2026-08-22 — Step 13.3 Hapke re-render: illumination-dominance claim QUALIFIED (skeerk review)

Headline as proposed ("illumination is the dominant degradation mode for the sag
detector") is accepted ONLY with these qualifications (evidence:
`data/outputs/wp1_ladder/hapke/{METHODS.md,hapke_summary.json,hapke_f1_comparison.csv}`):

- **Analog-scoped**: mechanism is shadow voiding of TRENCH-HOSTED void labels
  (62/75/92% voided, azimuth means i=45/65/85 — independently recomputed from
  the committed renders + frozen GT: 0.615/0.753/0.918). A roofed-sag-on-open-
  mare target is UNTESTED by this experiment (METHODS caveat must ride along
  verbatim into Paper 1).
- **Attribution**: thr=0 predict-all = collapse of the PRODUCTION FIXED-CALIBRATION
  PIPELINE, not proven information loss at i=45-65 (predict-all recall there
  0.73-0.97); at i=85 recall ceiling 0.16-0.44 = genuine label voiding. No
  shadow-aware re-tune was run (by protocol); do not write "detector collapses".
- **Denominator inconsistency**: METHODS prints 68/79/95 ("valid void-label
  cells") vs headline 62/75/92 (all void cells) without stating denominators;
  neither series is logged in hapke_summary.json. Fix METHODS wording + log both.
- **Noise control**: single geometry (i=65); it is a generous upper bound on the
  noise pathway (keeps dim cells to 2.0 m cap that full arms NoData) —
  shadow-dominance is conservative. No double-count with v0.4 rungs (baseline
  arm unperturbed).
- **w-flatness is by construction** (r_ref scales with w in sigma_z): report as
  relative-SNR w-invariance, not general photometric insensitivity.
- **Rung dependence**: effect ~nil at 5 m (delta -0.009; n_void=8 — no
  statistic); claim is a 0.5-2 m phenomenon. Paper 1 must quote the
  per-geometry range (0.051-0.122), not only the 0.10 mean.

## finding 2026-08-22 — skeptic pre-submission review, Paper 1 v0.2 §4.5 + abstract

- CORRECTION — the i=85° recall ceiling "0.16–0.44" (2026-08-22 Hapke
  entry above; Paper 1 §4.5(b); METHODS.md §Headline) is a **0.5 m-rung
  statistic quoted without its rung restriction**: `recall_test_slope`
  at i85 spans 0.16–0.60 across rungs/azimuths (0.5 m: 0.161–0.443;
  1 m up to 0.539; 5 m up to 0.60 with n_void=8 caveat) — evidence:
  `data/outputs/wp1_ladder/hapke/hapke_f1_comparison.csv`, col
  `recall_test_slope`, all 16 i85 rows (HIGH). Paper must quote
  "(0.5 m rung)" beside the ceiling or it overstates label-voiding
  severity at 1–5 m. Verifier previously noted; unfixed in v0.2.
- CAVEAT — abstract's "the curve directly specifies camera and
  altimeter requirements" overclaims for a 6-site analog benchmark
  (v0.5 arms on ONE trench-labelled site; n_void=8 at 5 m): downgrade
  to "bounds/informs". Also: "best honest result F1=0.277" collides
  with the logged phrase "best honest F1 0.362" (v0.4, same site/rung)
  — qualify as "under the fixed-calibration protocol" or footnote v0.4.
- CAVEAT — §4.2/Table 1 is v0.4-free but only §4.5(a) says so;
  Kingsbowl footnote cites the v0.4 release note for F1 0.002 while
  that note's Kingsbowl number is 0.043 (history 0.002→0.045→0.043):
  declare the freeze in §4.2 and point to v0.4 numbers, or reviewers
  read stale/missing data. Trivial: §1.1 "~281 catalogued" vs log's
  278.

## decision 2026-08-22 — vegetation stripping out of scope

Vegetation removal for terrestrial analogs is OUT OF SCOPE for
LUNARVOID: the Indian Tunnel analog site is sparsely vegetated arid
terrain (El Malpais basalt flow), and a stripping step would add a
supervised ML dependency (training labels, model choice, per-site
validation) with no lunar counterpart — the Moon has no vegetation, so
the cost buys nothing transferable. Recorded as a limitation for
Paper 1 (analog-derived rungs may carry small vegetation-biased
residuals at 0.5–2 m rungs); revisit only if a drone campaign adds a
vegetated site.

## correction 2026-08-22 — paper v0.1 inherited claims

Three claims inherited by Paper 1 draft v0.1 from earlier log entries
were mis-scoped; caught by verifier FAIL + skeptic review, repaired in
draft v0.2 (evidence: `papers/paper1_resolution_limits/main.md`;
`data/outputs/wp1_ladder/hapke/hapke_f1_comparison.csv`):

- The "recall 0.73–0.97 under Hapke" figure was an **i=45°, 0.5–1 m
  rungs only** statistic; across the full span of rungs/azimuths
  recall runs **0.557–1.00**.
- The i=85° recall ceiling **0.16–0.44 is the 0.5 m rung** (1 m
  reaches **0.54**; 5 m **0.60**, n_void=8) — quote the rung beside
  the ceiling or label-voiding severity at 1–5 m is overstated.
- Abstract FP **3.8e10** was a **per-cell predict-all density** (CSV
  col `fp_per_1e4km2_test` extrapolation), **NOT FP/10^4 km²** —
  paper relabeled to FP-cell density; the lunar FP per 10^4 km² rate
  is **NOT MEASURED**.

## finding 2026-08-22 — per-DTM noise floors N=10/649 (P3.1a)

Per-DTM Z2-scale noise floors for the Phase-3 transfer set, computed
at every good-tier NAC DTM that has a source raster on disk under
`~/lunarvoid/data/(outputs/)`. **Inference language only** — these
are noise statistics, not detections of any subsurface void.

- **10/649 good-tier DTMs have on-disk NAC DTMs**: 2 used the
  krigcorr source (TRANQPIT1, MARIUSPIT01 — same inputs as Task 6);
  8 used the raw NAC DTM fallback. The remaining **639 of 649
  good-tier DTMs were skipped** because their source NAC DTM (or
  krigcorr derivative) is **not present on disk** under
  `~/lunarvoid/data/(outputs/)` (MEDIUM confidence; skip list logged
  in `per_dtm_floors_summary.json`). **(MEDIUM — CRITICAL GAP)** This
  is the **DTM-production gap that Task 8 rental was meant to
  solve** (D2 = deferred per user direction 2026-08-21). Phase-3
  transfer (P3.1c) will populate the registry from **N=10, not
  649**; this MUST be reflected in the G1 gate report as a
  **$0-scope limitation**.
- Pooled sag-band RMS range across N=10 DTMs: **0.766–1.462 m**;
  **median 1.147 m**; **local_Amin median 3.44 m** (project
  convention: `local_Amin = 3 × pooled_rms`). Sites covered:
  MARIUSCONE, MARIUSPIT01, PRCLRMPIT01, GRUITHUIS17, INGENIIPIT,
  TRANQPIT1, GRUITHMARE2, FECNDITATS2, IRIDIUMPIT1, SWFECUNPIT1
  (HIGH — deterministic, seed-42 pipeline, identical to Task 6
  method).
- **Sanity exact match vs Task 6 (HIGH):** TRANQPIT1 pooled RMS =
  **1.245184 m** vs Task-6 TRANQPIT1 = **1.245184 m** (6 dp);
  MARIUSPIT01 pooled RMS = **1.379200 m** vs Task-6 MARIUSPIT01 =
  **1.379200 m** (6 dp). Reproduction PASS for both. Caveat: raw
  floors (N=8 of 10) are systematically higher than krigcorr
  because I2 long-wavelength distortion is NOT removed (when
  krigging runs for the remaining 8 raw DTMs, expect pooled RMS
  to drop by the same factor seen on TRANQPIT1 — which was already
  well-registered so its raw ≡ krigcorr).
- **Implication:** P3.1c tiering uses per-DTM `pooled_rms_m` (NOT
  the convention `local_Amin`) with per-DTM F1 to bucket the
  transfer set into T1/T2/T3. `local_Amin` is the per-DTM
  detectability floor that tiering thresholds must clear. No
  "detection" wording anywhere; inference / FP-rate language only.
- Evidence: `data/outputs/wp0_kriging/per_dtm_floors.csv` (10
  rows), `data/outputs/wp0_kriging/per_dtm_floors_summary.json`
  (medians + skip list of 639 names), and
  `data/outputs/wp0_kriging/per_dtm_floors_METHODS.md` (panel rules,
  3× rule labelled as project convention, sanity checks).
- `data/candidate_registry.csv`: **skeleton preserved** (header +
  schema + tier-discipline comments + provenance line); **no
  candidate rows yet** — populating is P3.1c after transfer.

BACKLOG: Kingsbowl per-cell sag stats unrecoverable (source dir
empty) — optional Phase-3 re-run to repopulate; only F1 0.002/0.043
corroborated via the v0.4 release notes.

## 2026-08-22 — skeptic review, P3.1c registry + transfer (verdict: UNSOUND)

Tier-B inversion of the I14 funnel, calibration/transfer leakage,
unexplained large-amplitude FPs, ring-artifact inflation, n=7/10 scale.

- **TIER-B INVERSION OF I14 FUNNEL (CRITICAL)** — the 3 tier-B rows
  (MARIUSPIT01-0400cm-r001, r002, -0800cm-r002) earn tier B by the
  rule "rille intersection within 100 m" (`METHODS.md` L213–215).
  This is the **pre-registered v5 I14 failure mode** (pits incised
  into rilles spill sideways — it is a FINDING in this project, see
  2026-08-21 entries above). Promoting by the same criterion inverts a
  known confounder into a positive signal. **Downgrade all 3 to tier C
  with note "I14 funnel risk — rille intersection is the failure mode,
  not independent confirmation"** (HIGH — must fix before any G1
  registry citation). Tier-B count collapses 3 → 0; tier A stays 0.

- **AGGREGATE FP RATE IS THE CALIBRATION RATE DILUTED, NOT A SURVEY
  RATE** — `transfer_summary.json.aggregate.fp_per_1e4km2 = 3.71 [0.76,
  10.83]`. All 3 FPs are TRANQPIT1; 6 of 7 contributing DTMs are n_fp=0
  because they were selected BECAUSE they host catalogued pits. The
  "10/649" sample is **10 pit-associated DTMs, not random mare**. The
  honest numbers are TRANQPIT1's `240.41 [49.58, 702.58]` (small-sample
  n=4) — a per-DTM calibration context, not an extrapolation. (HIGH —
  G1 headline must reframe.)

- **CALIBRATION/TRANSFER LEAKAGE** — `calibration_transqpit1.json`
  tunes `frac=0.20 / slope=45°` on TRANQPIT1 alone (single positive;
  50/50 split degenerate). "Transfer" to 9 other DTMs applies the
  un-re-tuned threshold; this is portability demonstration, NOT
  held-out evaluation. The v0.4 release note / I15 freeze protocol
  acknowledges this implicitly but the framing as "transfer evaluation"
  overstates it. (MEDIUM — terminology.)

- **TRANQPIT1 12-km FPs ARE UNEXPLAINED LARGE FEATURES** — registry
  rows 73–75 (r001 95.4 m, r002 57.4 m, r003 48.8 m amplitude, all
  12.5 km NNE of MTP). These are LARGE Mare Tranquillitatis features,
  not noise-spike FPs. Visual inspection (floor-fractured crater rim,
  ejecta blanket, post-emplacement modification?) is REQUIRED before
  the "FP" label sticks; the morphometric signal is real, the void
  interpretation is unsupported. (MEDIUM — must inspect before Paper 1.)

- **INGENIIPIT 24/44 ROWS ARE RING ARTIFACTS AROUND THE CATALOGUED
  PIT** — registry rows 36–59. r001 (87.7 m, score 19.33) IS the
  catalogued pit (score-rank-1 TP by 100 m convention). r002–r008 are
  within ~10 km of r001 with 17–60 m amplitudes — these are Frangi
  ring artifacts around the known feature, not 23 separate void
  candidates. Add note column entry "ring artifact around catalogued
  pit (r001)" for r002–r008 (HIGH — at least 23 rows mislabelled as
  "inferred void candidates").

- **N=7/10 SCOPE = PROOF-OF-METHOD, NOT SCIENCE CLAIM** — registry
  covers 7 of 10 on-disk DTMs of 649 in scope; 8092 km² ≈ 4% of
  in-scope mare NAC DTM coverage (assuming 649 × ~300 km² ≈ 2e5 km²).
  Aggregate FP rate generalises to nothing without the 639-DTM held-out
  set. **G1 gate report MUST label the registry "DEMONSTRATION only —
  N=7 of 649; generalisation deferred to D2 DTM production"** (HIGH —
  required for honest G1).

- **IRIDIUMPIT1 IS A MISSED DETECTION (negative evidence)** —
  `transfer_summary.json.per_dtm.IRIDIUMPIT1`: n_candidates=2, both
  below-local-floor, n_tp=0 on 1621.7 km². The detector fails to
  recover the catalogued IRIDIUMPIT1 pit at all. This contradicts any
  claim of "robust recovery on the transfer set" — add to registry
  notes / paper as the detector's success varies by site. (MEDIUM.)

- **REGISTRY NUMERICS SPOT-CHECKED ✓** — `LV-INGENIIPIT-0200cm-r001`
  score 19.3345 matches `transfer_summary.json` top_score 19.3345375;
  `LV-FECNDITATS2-0400cm-r001` 0.6853 matches 0.68532246;
  `LV-MARIUSPIT01-0400cm-r001` methods="morphometry|rille" matches
  tier-B rule; `calibration_transqpit1.json` frozen {slope=45, frac=0.2,
  F1=0.4, TP=1, FP=3} matches reproduction block. Numerics OK; tier
  labels ✗ per above. Evidence:
  `01_WORKSPACE/data/candidate_registry.csv`,
  `01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json`,
  `01_WORKSPACE/data/outputs/wp2_sag/transfer/calibration_transqpit1.json`.

## decision 2026-08-22 — multi-illumination azimuth test deferred

Multi-illumination azimuth test (Step 18.2) deferred — pending the
Task-19 photometric-stereo stack build (P4.2) where azimuth
variation comes for free as part of multi-illumination stacking.
This decision is recorded, not abandoned.

## 2026-08-22 — skeptic review, P4.3 Diviner thermal + rock abundance at N=7 (verdict: UNSOUND)

Five real objections (each falsifiable, with resolution); numbers
spot-checked against `diviner_summary.json` + `diviner_thermal.csv`
+ `code/wp4_diviner/sample_diviner_at_candidates.py`. The honesty
fix to the 24/44 headline (g1_honesty block) is good but
INSUFFICIENT — the `interpretation` block still misframes the result.

- **O1 — "no 2σ anomaly except INGENIIPIT" framing is dishonest at
  2/7 coverage** (HIGH). With 4/7 DTMs in the Powell GHRM
  equatorial/sub-arctic gap (TRANQPIT1, MARIUSPIT01, IRIDIUMPIT1,
  PRCLRMPIT01 — all `all_sentinel_or_NaN_in_box`) and 1/7 partial
  (SWFECUNPIT1: TBOL ok, RA all sentinel), the `interpretation`
  sentence "Thermal non-detection … IS a RESULT" reads as a global
  null when it is actually a coverage gap. `g1_honesty.coverage`
  flags 2/7 fully usable but `interpretation` does not reference it.
  Resolution: rewrite `interpretation` to "INCONCLUSIVE at N=7 due
  to 4/7 equatorial coverage gap; the 2/7 fully usable sites show
  one marginal 2σ anomaly at INGENIIPIT only" — and the G1 gate
  report must echo this verbatim.

- **O2 — INGENIIPIT +2.65 K is the WRONG SIGN for a void cooling
  signature** (HIGH). Powell TBOL is *cumulative nighttime
  bolometric T*. A void should *cool* at night (loss of radiative
  coupling to regolith); +2.65 K is *warmer* than mare median.
  Almost certainly a rocky ejecta signature — consistent with
  `RA_pct_mean = 0.98 %` at INGENIIPIT vs `0.50 %` at FECNDITATS2
  (≈2× local mare). The summary frames this anomaly as the sole
  thermal finding; it is in fact evidence *against* the tube
  hypothesis at this site (rock field, not void). Resolution:
  reframe INGENIIPIT anomaly as "rocky ejecta, not void cooling;
  inconsistent with tube hypothesis at this site" and downgrade
  from "result" to "inconclusive / counter-evidence for the
  thermal-anomaly leg".

- **O3 — RA 0.0 exclusion biases against bare mare** (MEDIUM).
  `_valid_mask` uses `arr > 0.0` (line 95 of
  `sample_diviner_at_candidates.py`). Genuine rock-free mare
  (0.0 areal fraction) is real signal, not a sentinel. The
  docstring's "96 % pattern matches TBOL" argument is partly
  circular — TBOL is missing in the equatorial gap so RA is too,
  but at sub-arctic latitudes (e.g. INGENIIPIT −36°, IRIDIUMPIT1
  +46°) where TBOL IS valid, the RA 0.0 density may genuinely
  include bare mare. At INGENIIPIT the inner box RA (0.98 %) vs
  the mare-reference RA (computed from the 20×20 km outer box
  excluding the 1-km inner) may be over-estimated if bare-mare
  pixels are stripped from the reference. Resolution: log
  excluded-RA histogram per DTM; document the upper-bound bias;
  prefer NaN-as-sentinel in P4.4 if Powell product supports it.

- **O4 — Sub-pixel spatial-scale mismatch unacknowledged** (HIGH).
  Powell 2023 GHRM is 128 ppd: 236.9 m/px at equator, ~150 m/px
  at INGENIIPIT (−36°), ~81 m/px at IRIDIUMPIT1 (+46°). Inner
  box is 1×1 km (half_m = 500, line 77). Skylight pits
  (typically ≤100 m diameter) are sub-pixel at all 7 DTMs and
  barely resolvable at IRIDIUMPIT1. The "1-km box thermal mean"
  is therefore averaged over mostly mare pixels with the pit
  occupying <1 px — i.e. the experiment cannot resolve a tube-
  scale thermal anomaly at this resolution; it can only resolve
  site-scale anomaly if the ejecta field is ≥1 px (~237 m).
  Resolution: add per-DTM pixel size to `per_dtm`; the G1
  thermal claim must state "site-scale only; tube-scale
  unresolved at Powell 2023 resolution".

- **O5 — Multi-evidence stacking broken at G1** (HIGH). Only Z2
  morphometry is active at 7/7 DTMs; thermal at 2/7 fully usable;
  photometric (P4.2) is deferred. The G1 gate report cannot
  honestly claim "multi-evidence stacking" when only one of three
  planned evidence legs has site-wide coverage. Resolution:
  G1 gate report must state "multi-evidence STACKING
  DEMONSTRATION is morphometry-only at G1; thermal at 2/7;
  photometric (P4.2) deferred to post-G1".

- **NUMBERS SPOT-CHECKED ✓** — INGENIIPIT delta_T 2.6484527 K
  matches `diviner_summary.json.per_dtm.INGENIIPIT.delta_T_K.max`
  and CSV row 5; 24/44 = 0.5454545454 matches
  `global_summary.frac_anomaly_2sigma`; INGENIIPIT n_candidates=24
  = 8 candidate positions × 3 scale tiers (2/4/5 m) — verified by
  counting CSV rows 5–28; TRANQPIT1 n_candidates=4 = rows 42–45;
  IRIDIUMPIT1 all-sentinel reason matches rows 29–30. Trace OK;
  INTERPRETATION not OK.

- **SUGGESTED DOWNGRADE** — P4.3 thermal tier from "G1 result
  (null)" to "G1 INCONCLUSIVE due to 4/7 coverage gap + 2/7
  INGENIIPIT anomaly inconsistent with void-cooling hypothesis
  (rocky-ejecta alternative)". Multi-evidence stacking claim
  held at DEMONSTRATION-only with morphometry as the sole active
  leg.
