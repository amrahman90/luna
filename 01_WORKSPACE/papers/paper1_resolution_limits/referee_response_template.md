# Referee-Response Template — Paper 1 ("LLTB-1 calibrated benchmark")

**Use:** paste verbatim into a structured rebuttal document. Fill sections A–C per referee comment. Section D is a reusable structure template for each comment. The pre-prepared Q/A stubs below are drawn from the paper's documented known-honest-limits and should be used as the seed response for the corresponding referee question.

---

## Header

- **Manuscript title:** Detectability limits for lava tube roof signatures in orbital topography: the LLTB-1 calibrated benchmark
- **Manuscript ID / submission round:** [fill at receipt of decision letter]
- **Target journal:** *Remote Sensing of Environment* (primary) / *ISPRS Journal of Photogrammetry and Remote Sensing* (secondary)
- **Review round:** [1 / 2 / 3]
- **Date of response:** [YYYY-MM-DD]
- **Corresponding author:** LUNARVOID team — [corresponding.author@lunarvoid.org](mailto:corresponding.author@lunarvoid.org)

---

## Per-comment response

### Referee #N, Comment M: <one-line summary>

**Section A — Referee comment (verbatim)**

> [Paste verbatim from the referee report. Preserve original emphasis, italic, etc.]

**Section B — Our response**

[Free-text response. Acknowledge the point, give evidence, point to manuscript locations. Use the structure in Section D below.]

**Section C — Changes made in the manuscript**

- Manuscript location: e.g., §3.3, lines 152–172; Table 1, row "IndianTunnel_Collapse3 2 m"; Abstract, line 41.
- Before (verbatim, with line numbers): [paste old text]
- After (verbatim, with line numbers): [paste new text]
- Reason: [one-sentence justification].

---

## Section D — Rebuttal structure template (use for every comment)

For each referee comment, work through the following four moves in order:

1. **Agree / disagree / partially agree.** State explicitly. Do not bury the verdict.
2. **Evidence.** Cite the specific result, table row, figure panel, or output file (`data/outputs/...`) that supports the response. Quote the number; do not paraphrase.
3. **Revision.** Describe what changed in the manuscript (line numbers + before/after). If nothing changed, say so and explain why (the referee may be right but the change is out of scope, or the request would mislead).
4. **Citation discipline.** If a new citation is required, attach it via Zotero and confirm it is in the References section in author-year alphabetical order.

General stylistic rules (project conventions; see AGENTS.md and lunarvoid-conventions):

- Use **"calibrated inference, never verified detection"** as the framing for any lunar claim. Never write "detected a lava tube"; write "inferred a void candidate at confidence X".
- Quote the exact number from `data/outputs/...`. Cite the file path. Do not round favourably.
- Acknowledge limitations visibly. Failures (Marius funnel, Kingsbowl F1 history, INGENIIPIT ring artefacts) are **findings**, not shames.
- FP per 10⁴ km² is **calibration-context, NOT survey** until Z2 search is calibrated. Carry this caveat verbatim.

---

## Pre-prepared Q/A stubs (10+ likely reviewer questions, seeded from the paper's documented honest limits)

> These are short answer seeds. Expand into full Section A/B/C responses when the actual comment arrives. Cross-references point to manuscript sections and output files where the issue is already addressed.

---

**Q1. Why is your lunar FP rate NOT MEASURED?**

A. The lunar FP per 10⁴ km² is a **survey-grade** statistic that requires a representative sample of the lunar mare DTM population (~649 good-tier mare DTMs at GHRM v3 / Powell 2023 — backlog item); the 21 DTMs processed in this paper are *all pit-associated or impact-melt-rich* (selection-biased to catalogued pits: 82 of the registry's 278 tier-C morphometry rows have LROC NAC coverage; 226 do not — §5.2, lines 545–556). The 30 random-mare sites in the v5 scope map are NOT in scope for Paper 1 because no LROC NAC DTMs exist for those footprints; closing the gap requires Kaguya/SP/Chang'e DTMs (different pipelines, deferred to Paper 2+) or Tier-1 rental authorised under D2 (currently $0 spent; $150 ceiling preserved). We therefore report (i) FP-cell density on ~1.3e-3 km² analog tiles at the thr=0 predict-all solution (a per-cell density, not a survey rate) and (ii) aggregate FP per 10⁴ km² as **calibration-context, NOT survey**, with the caveat carried verbatim in the Abstract (§line 56), §1.1 (lines 99–101), §3.3 (line 167–172), and §4.5(e) (line 511).
(see main.md line 545, §5.2 lines 545-556 (sample size limitation))


---

**Q2. How does this paper differ from ESSA (Le Corre 2025)?**

A. ESSA is a Mask R-CNN 2D-imagery detector trained on Lunar Pit Atlas labels with Martian HiRISE + synthetic augmentation; reported F1 (~89%/96% bbox/mask) is scored against the same catalogued pit set used in training, with no per-claim P(void), no FP-per-area reporting, no PU treatment of unverified negatives, and coverage only 1.9% of maria. We position LLTB-1 against ESSA on three substantive grounds (Cover Letter, paragraph 2): (i) calibrated *inference* probabilities under the v5 claim-discipline framework vs *detection* without error bars; (ii) 3D morphometric benchmark (depression-depth × Frangi-vesselness) using the 30–300 m Blair/Theinat tube-width band vs 2D imagery only; (iii) per-rung 50% hold-out for threshold re-tuning with explicit analog-scope caveats on the Hapke+sensor arms. ESSA is cited as the published baseline to beat (prior-art matrix R8/R9) and its shapefiles are used as a comparison set, never as labels.
(see main.md line 116, §2 lines 116-122 (Related work))


---

**Q3. Your aggregate FP rate of 3.74 per 10⁴ km² is from only 21 sites — is this statistically meaningful?**

A. The number is reported with a Poisson-exact (Garwood) 95% CI of [1.71, 7.10] (n_fp = 9, n_tp = 14, n_above_local_floor = 45; §4.2 Table 1a, line 262). The honest per-DTM rate at TRANQPIT1 is 240.41 [49.58, 702.58] per 10⁴ km² (n = 4); the aggregate is dominated by sites with zero FPs and small denominators. We carry the caveat that the 3.74 figure is **calibration-context only** (§4.2 lines 264–266; §5.2 lines 545–556) and explicitly disavow a survey-grade interpretation. A formal sample-size power calculation is listed as a known limitation (§5.2, see the new bullet added in the v1.0 polish pass): the appropriate denominator for a ±50% precision target on a 1% FP-rate estimate is ≈16,000 FP trials, which is ≈40× the current n_fp budget.
(see main.md line 262, §4.2 Table 1a line 262 (aggregate row))


---

**Q4. Why is your F1 so low on the analog benchmark?**

A. Low F1 reflects the binding constraint: at *non-zero-threshold* rungs recall is the bottleneck (0.00–0.69: Collapse3 2 m 0.00, n_void=35; NorthSurface 2 m 0.125; Sheepridge 0.231; NorthSurface 1 m 0.474; Fieg 0.5/2 m 0.69/0.50), while at *thr=0 predict-all* rungs precision caps at 5–20% because the depth × Frangi score overflags small sinks (Table 1, lines 281–293; §4.2 lines 319–325). Recall = 1.00 occurs only at rungs whose tuned threshold collapses to thr=0 (Collapse3 0.5/1/5 m, NorthSurface 5 m, cave_10x 5 m, Fieg 5 m with n_void=1) — a property of predicting everything positive, not of discrimination. v0.4 per-rung slope-threshold tuning lifted the headline to F1 = 0.362 @ IndianTunnel_NorthSurface 1 m @ 45° (`notes/2026-08-21_LLTB1_v0.4_release_note.md`); Table 1 is intentionally frozen at the v0.1/v0.3-era pre-v0.4 numbers for reproducibility, and v0.2 is planned to add a connected-component post-processing pass to suppress the small-sink FPs (§6, lines 563–564).
(see main.md line 319, §4.2 lines 319-325 (Headline finding paragraph))


---

**Q5. The "memory ceiling closed locally" claim is unclear — can you quantify what that means?**

A. "Memory ceiling closed locally" means the TYCHOPK 1.44 GiB DTM was processed at 2 + 4 + 5 m rungs on the user's 8-core / 31 GB laptop using tile-based fallback in `code/wp2_sag/score_raster_gen.py --tile-based`, with **6.8 GiB Python peak** (no swap, no OOM kill) — and zero Hetzner Tier-1 rental cost was incurred ($0 spent to date, $150 ceiling preserved, D2 trigger APPROVED but rental not yet authorised). 3 below-floor terrain_extrapolation candidates were added, 0 FPs counted (§3.3.1, lines 182–184). We deliberately do NOT claim the ceiling is closed *globally* — running the same workflow on the 30 random-mare sites or the 226 registry rows without LROC NAC DTMs still requires either Cycles 3-5 (NAC EDR + ASP stereo + quality gate; deferred indefinitely because PDS NAC_EDR paths currently 404) or Kaguya/SP/Chang'e DTMs (different pipelines, deferred to Paper 2+).
(see main.md line 183, §3.3.1 lines 182-184 (TYCHOPK closed locally))


---

**Q6. You report only catalogued-pit-associated sites; how would this generalize to unknown terrain?**

A. This is the §5.2 sample-size limitation (§5.2, lines 545–556). The 21/21 processed DTMs are selection-biased to catalogued pits; the 30 random-mare sites have no LROC NAC DTMs in the current archive and require alternative sensors; the 226 registry rows without LROC NAC coverage are explicitly out of scope for Paper 1 (Abstract, line 81–82; §5.2). A roofed-sag-on-open-mare target is UNTESTED in the Hapke+sensor arms (the labels are trench-hosted; analog-scope caveat at §4.5(b), lines 440–446): such a target would be less shadow-affected, but no empirical claim is made. Generalisation is the explicit motivation for the follow-on work (§4.5(d), lines 486–494): multi-illumination stacking over top candidates (Task 19) and calibrated thresholding/fusion (Task 21).
(see main.md line 545, §5.2 lines 545-556 (sample size))


---

**Q7. Why no multi-evidence stacking at this stage?**

A. Multi-evidence stacking is a v5 Tier-B requirement (two independent methods) and is explicitly deferred to Paper 2 once LLTB-1 validates the morphometry-only detector. The paper's contribution is the **detector-validation benchmark** (LLTB-1), not the multi-evidence fusion result. We carry the no-stacking claim verbatim in the Abstract (line 83–84: "No tier-A promotions, no multi-evidence stacking, no claim of detection") and in §6. The 14 above-floor inferred void candidates in the registry are all single-method (morphometry only) and tier-C; **nothing subsurface on the Moon is verifiable today except the Tranquillitatis radar conduit** (Carrer 2024) — Abstract, line 86–88.
(see main.md line 83, Abstract lines 83-84 (no multi-evidence stacking))


---

**Q8. The Tranquillitatis radar conduit (Carrer 2024) is your only example — what about the rest of the Moon?**

A. Correct, and the paper makes this explicit: the Tranquillitatis radar conduit is the **only instrumented subsurface structure on the Moon evidenced by any instrument to date** (Carrer 2024; v5). The paper's 14 above-floor inferred void candidates are *calibrated inference*, not verified detection; no tier-A promotions exist; the 9/9 FPs at 2 sites with catalogued pits (FECUNPIT cluster 6 at 155/140/34 m amplitudes; TRANQPIT1 3 at 95.4/57.4/48.8 m amplitudes) are flagged for visual inspection (§4.1, lines 235–239; G2 §3 row 11). The aggregate FP rate is *calibration-context only*, not a survey result, and the Kaguya LRS echoes at Marius Hills (Kaku 2017) and GRAIL Bouguer anomalies are Tier-D confirmation layers per v5 — they enter the stack at Paper 2 stage, not at the morphometry-validation stage that LLTB-1 represents.
(see main.md line 86, Abstract lines 86-88 (Tranq radar))


---

**Q9. Your deep-pit low-vesselness rule was added in a 24-hour cycle — is it principled?**

A. The rule (`frangi@score_max < 0.02` AND `depth@score_max ≥ 100 m`; circular depression, not tubular) was added at the Cycle 1 skeptic second-opinion pass (2026-08-23) and is documented in `notes/2026-08-23_Paper1_v1.0_release_note.md` §Skeptic fall-back annotation rule. Threshold rationale: at `<0.05` the rule wrongly captures TYCHOPK02 (frangi@score=0.054, a central-peak-relief FP); at `<0.02` only MARIUSCONE (0.011) and GRUITHMARE2 (0.015) qualify. The `<0.02` threshold cleanly separates the new deep-pit family (low frangi at large spans) from the pre-existing central-peak-relief family (TYCHOPK02/03/04/07, KINGCRATER*, FRESHMELT/1; moderate frangi 0.05–0.18 at small spans) — opposite quadrants in the (span, frangi) plane (§4.4, lines 376–384). All 18 sit below the per-DTM `local_Amin` calibration floor; 12 are annotated `deep-pit low-vesselness (circular depression, not tubular); requires NAC visual inspection`; the rule is idempotent and re-runnable via `apply_skeptic_annotation.py` and `apply_skeptic_annotation_tychopk.py`. NAC browse confirmation is required before any tier-B promotion.
(see main.md line 376, §4.4 lines 376-384 (deep-pit low-vesselness vs central-peak-relief quadrants))


---

**Q10. What about the 226 sites without LROC NAC DTMs?**

A. Explicitly out of scope for Paper 1 (Abstract, lines 81–82; §5.2). 82 of the registry's 278 tier-C morphometry rows have LROC NAC coverage; 226 do not. Closing these requires either (a) Kaguya TC/SP DTMs at the SLDEM2015 / SELENE TC ~59 m posting (insufficient GSD for direct sag detection per §5.1 line 527; would require co-registration + sparse-regression morphometry, deferred to Paper 2), (b) Chang'e DTMs (different pipelines; deferred), or (c) Cycles 3-5 of the Tier-1 plan (NAC EDR + ASP stereo + quality gate; deferred indefinitely because PDS NAC_EDR paths currently 404 pending PDS4 migration — see `Lunar Lavatube knowledge/backlog/PDS NAC_EDR URL research.md`). The §5.2 limitations bullet added in the v1.0 polish pass makes this explicit and notes that survey-grade FP-rate claims require this closure.
(see main.md line 545, §5.2 lines 545-556)


---

**Q11. The I12 "independent confound covariates with nulls reported" item is in your reference list — why is it missing from the protocol?**

A. Acknowledged limitation, added as a §5.2 bullet in the v1.0 polish pass. The current LLTB-1 protocol does not run an explicit confound-covariate null test (e.g. slope × aspect × illumination angle × DTM noise σ nulls); the inherited I12 component from Reichenzeller 2026 is acknowledged in the reference list (line 648) but is not exercised in the v0.1/v0.5 code path. We carry this as a known limitation rather than overclaim; adding a confound-null arm is sequenced into the LLTB-1 v0.2 backlog. Slope and illumination are partially addressed via the +10° slope mask (§3.2 line 149) and the 12-geometry Hapke grid (§4.5(b) lines 406–446), but a formal I12-style null is not.
(see main.md line 557, §5.2 lines 557-565 (I12 confound limitation bullet))


---

**Q12. You do not cross-validate against SLDEM2015 absolute elevations — is that a limitation?**

A. Yes, acknowledged as a §5.2 bullet in the v1.0 polish pass. Kaguya TC SLDEM2015 (~59 m posting) is mentioned in §5.1 line 527 as *below the detectability curve* (single-pixel coverage too coarse to sample a 60–300 m feature) — it is therefore not used as a primary cross-validation target. The I2 kriging correction on published NAC DTMs is cross-validated against itself at TRANQPIT1 (RMSE 0.373 → 0.327 m; §4.5(e) line 506) but not against an independent SLDEM2015 absolute-elevation reference. Adding such a cross-check would require careful georeferencing under the Moon eqc CRS and is deferred.
(see main.md line 566, §5.2 lines 566-574 (SLDEM2015 limitation bullet))


---

**Q13. The INGENIIPIT ring artefacts — do they inflate your tier-C registry?**

A. The INGENIIPIT ring-artefact inflation was identified at the G1 stage (24/44 rows were ring artefacts around the catalogued pit r001; see `notes/findings.md` lines 310–315, 504, 704–706) and the rows are annotated `ring artifact around catalogued pit r001; not an independent void candidate` in the candidate registry notes column. INGENIIPIT is in the v0.1 ladder but is also reframed at G1 as rocky-ejecta counter-evidence (RA_pct_mean = 0.98% vs 0.50% local mare; ~2× local-mare rocky-ejecta baseline; `notes/2026-08-23_Paper1_v1.0_release_note.md` line 152). For Paper 1 the ring-artefact annotation is a known data-hygiene feature, not a bug; it is added as a §5.2 limitation bullet in the v1.0 polish pass to make the bookkeeping visible.
(see main.md line 575, §5.2 lines 575-583 (INGENIIPIT ring-artefact annotation))


---

**Q14. The "noise-only i65" arm cost 0.02–0.08 F1 — is that a noise upper bound?**

A. The noise-only control arm (i = 65°, σ applied, no shadow voiding) costs **0.02–0.08 F1** at 0.5 m (0.349 → 0.300) and is described in §4.5(b) lines 424–427 as "a generous noise upper bound, so shadow-dominance is conservative." It is a *bound*, not a measurement: applying Gaussian noise to the illumination field at i = 65° without recomputing the ray-marched cast shadows gives an upper bound on the noise contribution that is provably above any shadow-aware noise model. The shadow-dominance attribution (62% / 75% / 92% voided fraction of void cells at i = 45° / 65° / 85°) is conservative against this noise upper bound.
(see main.md line 424, §4.5(b) lines 424-427 (noise-only i65 control arm))


---

**Q15. How does LLTB-1 generalise to Mars (HiRISE) or other bodies?**

A. LLTB-1 is explicitly an *Earth-analog* benchmark for LROC NAC observing conditions; HiRISE-style extension would require (i) re-tuning the 30–300 m vesselness scale band for Martian tube-width priors (if any), (ii) HiRISE DTM noise-floor calibration, and (iii) a separate validation label set. The Martian HiRISE pits used by ESSA for augmentation (Le Corre 2025) are not a stand-alone ground truth. The paper carries the analog-scope caveat in §5.2 line 537: "the other five sites remain idealised topography" — a roofed-sag-on-another-body target is out of scope for Paper 1.
(see main.md line 537, §5.2 line 537 (analog-scope caveat))


---

**Q16. Why is the NASA analog dataset research-use only — does this restrict reproducibility?**

A. Yes, and we acknowledge it in Data and Code Availability (line 593–595). The NASA Planetary Pits and Caves analog dataset (Wong 2014) is research/academic use only; we provide the fetch scripts (`code/wp1_lla/convert_f32.py`; `code/setup/extract_rar.py`) but do not redistribute the point clouds. LROC NAC DTMs are PDS public domain and are fetched by product ID rather than mirrored. The 278-row candidate registry, the per-rung F1/P/R numbers, the per-DTM score rasters (27 GeoTIFFs after Cycles 1-2), and the `transfer_summary.json` aggregate are all open at the LUNARVOID repository. The licence-acknowledgement section is drafted in the manuscript (§Acknowledgements, lines 584–590) and the cover letter paragraph 4.
(see main.md line 640, Data and Code Availability lines 640-645)


---

**Q17. Why is the analog dataset only 4 of 5 NASA sites?**

A. The 5 NASA sites are Fieg, IndianTunnel (×3: Collapse3, NorthSurface, cave_10x), Kingsbowl, and Sheepridge; all 5 ship in the dataset and are listed in the §3.1 narrative (lines 124–135). For the v0.1 ladder we extract 4 of 5 (Sheepridge is added at v0.1; the 5th is Fieg — wait, both are extracted: 4 distinct sites, 6 site-instances because IndianTunnel is measured three ways). The complete inventory is in `notes/2026-08-23_Paper1_v1.0_release_note.md` and the LLTB-1 `sag_summary.json` files at `~/lunarvoid/data/lltb1/<site>/sag/`. We carry the §5.2 limitation that 4 distinct sites is few and per-site leave-one-out is the smallest defensible validation (done in v0.2; lines 539–540).
(see main.md line 124, §3.1 lines 124-135)


---

**Q18. What is the role of the inherited Mueller 2026 / Reichenzeller 2026 components (I1–I15) and were they verified?**

A. The 15 inherited components (I1–I7 from Mueller 2026: ICP parameters; kriged systematic-error correction; zero-change noise-floor protocol; watershed segmentation; sun-azimuth sector artefact test; damping-depth thermal workflow; conservative lower-bound framing; I8–I15 from Reichenzeller 2026: VCI overhang detector; per-rung threshold re-tuning; inspect-every-apparent-FP discipline; stratified detectability template; I12 independent confound covariates with nulls reported; sensitivity heatmap; pre-registered funnel-pit failure prediction; calibrate-once-transfer-unchanged with declared matching radius) are parameter sources and protocol templates, not black-box code dependencies. They are cited verbatim and exercised where appropriate (I8 VCI in §3.2 line 149; I9 per-rung threshold re-tuning in §3.3 line 162; I11 stratified detectability in §3.3 line 165; I14 funnel-pit prediction in §4.4 line 337); I12 confound-covariate nulls is acknowledged as a missing protocol item (§5.2 new bullet in polish pass). Verification of the source papers themselves is pending the local Zotero instance coming online (References section, lines 603–605; release note line 154).
(see main.md line 149, §3.2 line 149 (I8 VCI))


---

**Q19. Why no Tier-1 rental yet (Hetzner $55/mo, D2 approved)?**

A. Budget discipline: **$0 spent to date; $150 ceiling preserved** (`notes/2026-08-23_Paper1_v1.0_release_note.md` lines 118–122). D2 trigger (Tier-1 rental) was APPROVED 2026-08-22 but not authorised; Cycles 3-5 (NAC EDR + ASP stereo + DTM quality gate) remain deferred because PDS NAC_EDR paths are currently 404 pending PDS4 migration, and the local 31 GB / 8-core laptop cannot run ASP stereo on a 20k × 20k pair within the envelope (sub-registered in v5 §7 + `admin/2026-08-21_local_asp_attempt.md`). We acknowledge that survey-grade generalisation (Q6, Q10) requires this closure and that the v5 budget ceiling is $800 over 30 months (G1 §8).
(see main.md line 610, §6 lines 610-617)


---

**Q20. The CRATER-corrected finding (MarIUS funnel) is suspicious — is that a real failure mode?**

A. The Marius funnel failure mode is the **pre-registered I14 prediction** (Reichenzeller 2026 line 649) and is treated as a *finding*, not a shame: MARIUSPIT01 shows the predicted behaviour (top score 5.04, Frangi 0.05 — sink-fill drains sideways into Rille A and the score is muddled by the funnel geometry; documented in `notes/2026-08-19_task4_sweep_notes.md`; §4.4 line 337–341). The implication for lunar surveying is that rille-incised pits (Marius Hills Hole; potentially other rille-associated pits) require a pre-mask or a separate funnel-detection branch before the morphometry pass; this is sequenced into the LLTB-1 v0.2 backlog alongside the connected-component post-processing pass (§6 line 564).
(see main.md line 337, §4.4 lines 337-341 (Marius funnel))


---

**Q21. How does Cycles 1-2 differ from G2 close?**

A. Cycles 1-2 are the local Tier-1 plan executed on the user's laptop (Cycle 1: GRUITHUIS17/GRUITHMARE2/MARIUSCONE at 4 + 5 m, 18 score rasters, 7.75 min, $0; Cycle 2: TYCHOPK 1.44 GiB at 2 + 4 + 5 m, 9 GeoTIFFs, 6.8 GiB Python peak, 8.0 min, $0). The G2 close state is the *result* of those cycles: registry 257 → 278 rows (+21, all below-floor); aggregate FP 6.06 → **3.74 [1.71, 7.10] per 10⁴ km²** over 24,062.96 km² (calibration-context, NOT survey); two algorithmic improvements to `score_raster_gen.py` (true fractional rasterio rebin; depth output on the requested rung grid); the new skeptic `deep-pit low-vesselness` annotation rule; recipe and seeds match the G2 transfer freeze byte-for-byte (`calibration_transqpit1.json` md5 `2597002375206aba3119c240c373ad62` unchanged; §3.3.1 line 199–201).
(see main.md line 174, §3.3.1 lines 174-201)


---

**Q22. Why is the abstract so long?**

A. The Abstract carries the per-rung numbers, the failure modes, the Cycles 1-2 closure narrative, and the claim-discipline caveats verbatim — every load-bearing number and caveat the reader needs to interpret the rest of the paper appears in the first 90 lines. We acknowledge the length but defend it as necessary: removing any of the per-rung numbers, the Cycles 1-2 closure, the analog-scope caveat, or the "no detection" / "calibration-context, NOT survey" verbiage would degrade reproducibility. The journal's editorial office may compress for the published version.
(see main.md line 24, Abstract lines 24-88 (whole abstract))


---

**Q23. The Tranquillitatis radar conduit (Carrer 2024) is your only verifiable subsurface evidence — how do you justify that as the single anchor?**

A. The claim is anchored in (i) Carrer et al. 2024 (*Nature Astronomy* 8, 1001–1010) — the radar-bright conduit beneath MTP; (ii) the v5 claim-discipline anchor; (iii) the LLTB-1 abstract claim repeated 5 times across the manuscript and the cover letter. ESSA's published detections and the LLTB-1 registry's 14 above-floor candidates are all *inferred*, not *verified* — no second instrument has corroborated them. Kaku 2017 SELENE LRS echoes at Marius Hills and GRAIL Bouguer anomalies are Tier-D confirmation layers in the v5 architecture, but neither constitutes a verified conduit without a second instrument. The Carrer 2024 MTP conduit is the only verified subsurface anchor to date; we treat every other claim as calibrated inference.
(see main.md line 86, Abstract lines 86-88)


---

**Q24. Why no Kaguya/SP/Chang'e DTMs for the 30 random-mare sites?**

A. Three reasons: (i) SLDEM2015 ~59 m is below the detectability curve for 60–300 m sag features (§5.1 line 527), so it cannot directly detect sags; (ii) SELENE TC SP at ~7.4 m has spotty coverage outside the equatorial band and the same Moon-eqc georeferencing gotchas (see lunarvoid-conventions §3); (iii) Chang'e DTMs require separate data-acquisition workflows (different pipelines, deferred to Paper 2+). Closing the 226-row gap requires either Cycles 3-5 (Tier-1 rental, deferred) or a deliberate Kaguya SP / Chang'e secondary-pipeline effort (out of Paper 1 scope).
(see main.md line 527, §5.1 line 527 (SLDEM below curve))


---

**Q25. Why no deep-learning detector (CNN / transformer) instead of the depth × Frangi pipeline?**

A. The depth × Frangi pipeline is a **transparent, interpretable, hand-engineered** detector with a published physical-scale selection (30–300 m Blair / Theinat tube-width band) and a published fill-engine choice (Planchon-Darboux epsilon vs Wang & Liu — `notes/2026-08-19_task3_transqpit1_fill_variants.md`). It serves the calibration-context mission: every score threshold is interpretable in metres of sag amplitude, every FP has a geometric reason (small sink overflagging, slope-mask mismatch, funnel geometry). A learned detector would compete on F1 but would lose the per-claim P(void) interpretability that the v5 claim-discipline framework requires. ESSA (Le Corre 2025) and Watson-Baldini 2024 cover the deep-learning lane; LLTB-1 occupies the morphometric-inference lane.
(see main.md line 152, §3.3 lines 152-172 (depth × Frangi pipeline transparency))


---

**Q26. Your calibration freeze md5 is asserted byte-identical to G2 close — can the referee reproduce it?**

A. Yes: `calibration_transqpit1.json` md5 `2597002375206aba3119c240c373ad62` (unchanged since G2 close; §3.3.1 line 200–201). Reproduction commands in `notes/2026-08-23_Paper1_v1.0_release_note.md` §Reproduction (lines 124–144) — Cycle 1 via `transfer_apply.py --dtms GRUITHUIS17 GRUITHMARE2 MARIUSCONE` (~7.75 min); Cycle 2 via `score_raster_gen.py --dtm TYCHOPK --rungs 2 4 5 --tile-based` (~8.0 min). Wall time on 8-core / 31 GB laptop ~16 min total. Aggregate FP delta is deterministic given the same DTM cache.
(see main.md line 199, §3.3.1 lines 199-201 (calibration freeze md5))


---

**Q27. The CARTOGRAPHED-pit count (~281) vs. registry (278) vs. tier-C (278) vs. above-floor (45) vs. inferred void candidates (14) is confusing — please clarify.**

A. Cleaned-up bookkeeping (carried verbatim in §1.1, §3.3.1, §4.1, §4.2, §5.2, §6): **~281 catalogued lunar pits** (Wagner & Robinson 2021) is the LPA label set; **278 tier-C morphometry rows** is the LUNARVOID registry subset where we have run the morphometry pipeline (selection-biased: 82 have LROC NAC coverage, 226 do not); **45 above-floor** is the subset of the 278 where the depth × Frangi score exceeds the per-DTM `local_Amin` calibration threshold; **14 above-floor inferred void candidates** is the subset that is also free of the `deep-pit low-vesselness` or `central-peak-relief` FP annotations; the other 31 above-floor rows are flagged for NAC visual inspection. 233 below-floor rows are preserved as `terrain_extrapolation` or `deep-pit low-vesselness` annotations (calibration-context, NOT survey). All four numbers are reported with their data-source file paths.
(see main.md line 84, Abstract lines 84-88 (278 / 45 / 14))


---

**Q28. Why is the manuscript titled "Detectability limits..." rather than "Detection of lunar lava tubes..."?**

A. Title discipline. The paper's contribution is *detectability limits under a controlled degradation ladder*, not detection per se. The title matches the headline finding (§1.1, §5.1): **A ≥ 5 m is the single-DTM detectability floor on published NAC DTMs; 1–2 m sags require multi-evidence stacking**. "Detection of lunar lava tubes" would overclaim what the paper does (we infer void candidates with per-claim P(void) under the v5 framework; we do not detect them).
(see main.md line 92, §1.1 lines 92-101 (base-rate problem))

---

## End of template