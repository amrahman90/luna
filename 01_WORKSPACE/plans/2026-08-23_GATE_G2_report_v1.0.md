# Gate G2 Report v1.0 — LUNARVOID (P3.1c N=7 → N=21 expansion)

> **Canonical install:** `papers/gate_reports/GATE_G2_report_v1.0.md`
> is the paper-writer's working copy. G2 extends G1 FINAL-PASSED
> 2026-08-22 (`plans/2026-08-22_GATE_G1_report_v1.0.md`, mirror at
> `papers/gate_reports/GATE_G1_report_v1.0.md`). DRAFT until a human G2
> decision lands.

---

**Date:** 2026-08-23 · **Version:** v1.0 · **Status:** DRAFT-FOR-REVIEW.

**Extends:** G1 FINAL-PASSED (N=7, 44 candidates; 5 PASS / 1 PARTIAL / 1
DEMONSTRATION / 1 DEFERRED / 1 DEFERRED-DTM-gap / 1 NOT MEASURED).
**G2 commits since G1:** `7860631` 11-new-LROC-NAC-DTM discovery (3.59 GB);
`4834c38` P3.1c N=19→N=21 (44 → 257 candidates; +213 rows; skeptic FECUNPIT
distance correction). Cost: $0 across 22 sessions (`admin/budget.md` 18 prior + 4 G2-cycle sessions).

## 1. What G1 cleared (1-line)

G1 at **5 PASS / 1 PARTIAL / 1 DEMONSTRATION / 1 DEFERRED / 1
DEFERRED-DTM-gap / 1 NOT MEASURED at $0** over N=7 good-tier mare NAC DTMs
(44 candidates; A=0, B=0, C=44; aggregate FP 3.71 [Poisson-exact (Garwood)
95% CI 0.76, 10.83] per 10⁴ km², calibration-context). G1 failure modes
carried in-row: Marius I14 funnel, Kingsbowl F1 history, 4/8 within-100 m
pit recovery, INGENIIPIT rocky-ejecta counter-evidence, 12-km TRANQPIT1
FPs, tier-B inversion, FP calibration-context, thermal 4/7 coverage gap,
ring artefacts. See G1 §3–5.

## 2. What G2 adds (since G1)

* **LROC NAC DTM acquisition (`7860631`)** — 11 new NAC DTMs (FECUNPIT,
  FRESHMELT, FRESHMELT1, KINGCRATER2/3/4, TYCHOPK, TYCHOPK02/03/04/07)
  via `code/wp8_stereo/fetch_lroc_dtms.py`; PDS3 RDR `pds.lroc.im-ldi.com`
  → 301 `pds.mcp.nasa.gov`; all 11 SHA-256s match
  `~/lunarvoid/data/fetch_log_lroc.csv` byte-for-byte; **3.59 GiB / $0 /
  PDS public domain**; LROC team (Arizona State University) attribution
  preserved in MANIFEST §LROC NAC DTMs.

* **TYCHOPK 1.44 GiB deferred** — memory ceiling (float64 + Frangi
  + scipy > 6 GiB peak; 20 GiB headroom insufficient). SHA-256
  `caf67354…cd2e0` on disk; not lost. Logged in `transfer_summary.json` +
  `METHODS.md`. Needs Tier-1 rental or tile-based processing.

* **Frangi score rasters (`4834c38`)** — 10 in-scope DTMs cached
  `score_<rung>m.tif` / `depth_<rung>m.tif` / `frangi_<rung>m.tif`
  triples at `~/lunarvoid/data/outputs/wp2_sag/score_rasters/<DTM>/`
  (84 GeoTIFFs; conventions §1). Generator
  `code/wp2_sag/transfer/score_raster_gen.py` with memory-efficient
  rasterio `out_shape=` rebin. FROZEN recipe: sigmas
  (30/60/100/150/200/300) m, PD fill, neigh=5, seed=42.

* **Registry N=7 → N=21** — 44 → 257 rows (+213); schema (15-col +
  provenance) preserved byte-identical; original 44 preserved (verified
  `comm -12`); **registry tiers: A=0, B=0, C=257** (MARIUSPIT01 3 remain
  downgraded C per I14 funnel-risk; `transfer_summary.json.aggregate.n_tier_B = 3`
  is the mechanical pre-downgrade count).

* **Aggregate FP 6.06 [Poisson-exact (Garwood) 95% CI 2.77, 11.51] per 10⁴ km²**
  over 14,840.27 km² (9 FPs, n_above_local_floor = 45). **Calibration-
  context rate only**, NOT survey — all 21 on-disk DTMs are pit-associated
  or impact-melt catalogued. Driver of 3.71 → 6.06: **FECUNPIT 6 FPs**
  (3 unique depressions × 2 rungs; amplitudes 155.49 / 140 / 34 m).

* **FECUNPIT distance correction (skeptic 2026-08-23)** — `dist_pit_m`:
  r001/r002 at **552.5 m**, r003 at **138.1 m** from the NEAREST catalogued
  pit in the atlas (NOT 67 km from the named Central Mare Fecunditatis Pit);
  r003 just outside the calibrated 100 m match radius (flagged FP); under
  150 m tolerance r003 would be a candidate TP. Visual inspection target =
  NAC frame of the 138–552 m *nearest* pit.

* **Highland / impact-melt extrapolation flagged** — 9 sites
  (`KINGCRATER2/3/4 + TYCHOPK02/03/04/07 + FRESHMELT + FRESHMELT1`)
  have NaN `local_Amin_m` (no flat panels under `min_panels=4`) → marked
  `terrain-extrapolation`; **0 FPs counted**; candidates preserved.
  **TYCHOPK02 76 below-floor** over-triggered on central peak (top
  score 0.45 vs mare 0.5–19); **NOT** a highland lava-tube detection —
  calibration extrapolation only.

* **30 random mare sites: still no LROC coverage** — catalogued-pits-only sampling bias persists; the 30-random-mare set is a Step-2 (post-rental) deliverable, not a G2 result.

* **Calibration freeze preserved** — `calibration_transqpit1.json`
  md5 = `2597002375206aba3119c240c373ad62` (unchanged across all G2
  edits). `surface_recipe`, `transfer_rule = "TRANSFER UNCHANGED"`,
  `pit_match_radius_m = 100` all unchanged.

## 3. G2 verdict table

| # | G2 criterion | Measured | Verdict |
|---|---|---|---|
| 1 | LLTB-1 v0.5 degradation (carried from G1) | 11/11 verify PASS; shadow-voiding 62/75/92% at i=45/65/85°; analog-scoped caveat preserved verbatim into Paper 1. `data/outputs/wp1_ladder/{hapke,sensor}/` | **PASS** |
| 2 | v0.5 degradation regression-free at N=21 | Smoke test PASS (F1 per-rung 0.392/0.000/0.800; fusion AUC 0.990); rung-restricted i=85° recall ceiling 0.16–0.44 at 0.5 m (1 m → 0.54; 5 m → 0.60, n_void=8) unchanged. `admin/verification_evidence/2026-08-22_v05_verification.json` | **PASS** |
| 3 | Registry provenance + tier discipline at N=21 | 257 rows; **A=0, B=0 in registry** (C=257); MARIUSPIT01 I14 downgrades preserved byte-identical (mechanical `n_tier_B = 3` is pre-downgrade); original 44 preserved (`comm -12`); INGENIIPIT 21 explicitly tagged ring artifact (of 24 total INGENIIPIT rows; 3 share the r001 catalogued-pit location and are not independently ring-tagged) + TRANQPIT1 12-km FP rows in-row; FECUNPIT 3-unique-distance + 9 highland/impact-melt annotations in-row. | **PASS** |
| 4 | Per-DTM noise-floor portability + by-terrain split NEW | **N=19** (was N=10 at G1; +FRESHMELT/FRESHMELT1 stubs at N=21); pooled RMS 0.657–1.462 m; **by-terrain split NEW: mare n=9 median 1.118 m / 3σ 3.355 m; highland n=5 median 1.089 m / 3σ 3.266 m**; skipped-insufficient-panels accounting correct on TYCHOPK*+FRESHMELT*; TRANQPIT1/MARIUSPIT01 reproduce Task-6 6-dp exact. `per_dtm_floors_summary.json` `by_terrain` | **PASS** |
| 5 | Diviner thermal (carried from G1, not re-run) | 2/7 fully usable (INGENIIPIT, FECNDITATS2); 4/7 all-sentinel Powell 2023 equatorial/sub-arctic gap; 1/7 partial (SWFECUNPIT1); **INGENIIPIT +2.65 K reframed as rocky-ejecta counter-evidence** (RA 0.98 % vs 0.50 % local mare ≈2×); tube-scale sub-pixel at Powell 128 ppd. Same artifacts as G1. | **PARTIAL** |
| 6 | Calibration freeze reproducible + audit trail | md5 = `2597002375206aba3119c240c373ad62` unchanged across all G2 edits; frozen `{slope=45, frac=0.2, F1=0.4, TP=1, FP=3}` reproduces byte-identical on TRANQPIT1 5 m (29 peaks, top 21.06, rank-11 3.72, closest 43.08 m) | **PASS** |
| 7 | **Highland / impact-melt extrapolation NEW at G2** | 9 DTMs tested; 0 FPs counted (NaN `local_Amin` → below-floor default prevents inflation); TYCHOPK02 76 below-floor over-trigger = calibration-extrapolation signal. **Method handled; FROZEN recipe is mare-only — portability claim deferred.** | **DEMONSTRATION (method works; scale insufficient for science claim)** |
| 8 | Multi-evidence stacking at G2 sites | Morphometry-only at all 17 processed DTMs; thermal INCONCLUSIVE at 2/7; photometric P4.2 still deferred. **Cannot claim multi-evidence stacking at G2.** Same as G1. | **DEMONSTRATION (method works; scale insufficient for science claim)** |
| 9 | Tier-A promotions (≥ 2 independent evidence legs) | **A = 0 by design** — physics screen + tier-A promotion deferred (P5.2); `aggregate.n_tier_A = 0`; I14 funnel-risk tier-B downgrades still active. Same as G1. | **DEFERRED** |
| 10 | Full-mare transfer (N=649) + survey-grade FP rate | DEFERRED-DTM-gap-PARTIAL: The G2 DTM gap covered TYCHOPK memory ceiling + GRUITHUIS17/GRUITHMARE2/MARIUSCONE no-cached-raster + 30 random mare sites with no LROC NAC coverage. Cycles 1-2 (2026-08-23) of the local Tier-1 plan resolved the first two: Cycle 1 processed the 3 no-raster DTMs at rungs 4+5 m (FRESHMELT-style workflow; 18 score rasters, 0 above-floor candidates, 12 annotated 'deep-pit low-vesselness' per skeptic new fall-back rule); Cycle 2 processed TYCHOPK at all 3 rungs 2+4+5 m on the laptop (6.8 GiB Python peak; 3 below-floor candidates, terrain-extrapolation). The 30 random mare sites remain deferred because no LROC NAC DTMs exist for those regions (LROC NAC DTMs overlap only 82/278 catalogued pit footprints; 226 sites have no coverage; Kaguya/SP/Chang'e DTMs would close these but are out of scope for Paper 1). FP rate improved from 6.06 → 3.74 [1.71, 7.10] per 10⁴ km² over 21,046 → 24,063 km² (calibration-context, NOT survey). $0 cost; 278 registry rows total. | **DEFERRED-DTM-gap-PARTIAL** |
| 11 | Lunar FP per 10⁴ km² as a survey rate | Aggregate **6.06 [2.77, 11.51]** is calibration-context (FECUNPIT 6 FPs at 155/140/34 m, 552.5/138.1 m from nearest catalogued pit, UNVERIFIED; plus TRANQPIT1 3 FPs unchanged); all 9 FPs at 2 sites with catalogued pits; honest per-DTM = TRANQPIT1 240.41 [49.58, 702.58]. 3.71 → 6.06 driven entirely by FECUNPIT 3-unique-depression cluster (visual inspection pending) | **NOT MEASURED** |

*Suffix note:* the DEFERRED-DTM-gap-PARTIAL tag (row 10) denotes Cycles 1-2 (2026-08-23) closure of the TYCHOPK memory ceiling + GRUITHUIS17/GRUITHMARE2/MARIUSCONE no-cached-raster sub-items; the underlying 30-random-mare-no-LROC-coverage gap remains and is blocked on §8 T1 trigger for NAC DTMs (out-of-scope alt-DTM sources: Kaguya/SP/Chang'e deferred to Paper 2+).

**Outcome: 5 PASS / 1 PARTIAL / 2 DEMONSTRATION (multi-evidence +
highland extrapolation) / 1 DEFERRED / 1 DEFERRED-DTM-gap-PARTIAL /
1 NOT MEASURED.** All G1 honesty elements preserved (4/8 within-100 m;
I14 tier-B downgrade → 0 B in registry; FP calibration-context; thermal
gap; INGENIIPIT rocky-ejecta; multi-evidence morphometry-only; tier-A =
0; TRANQPIT1 12-km FPs; INGENIIPIT ring artefacts; FRESHMELT impact-melt
context). G2 adds: by-terrain split; FECUNPIT distance correction;
highland extrapolation handling; TYCHOPK 1.44 GiB deferral.

## 4. What we can now claim (G2 inference language)

FP rate **NOT MEASURED** at survey scale; only honest per-DTM rate is
**TRANQPIT1 240.41 [49.58, 702.58] per 10⁴ km²** (n=4). Aggregate 6.06
[2.77, 11.51] over 14,840 km² is calibration-context (selection-biased);
N=7 → N=21 jump driven entirely by FECUNPIT's 3 unique large depressions
(552.5 / 138.1 m from nearest catalogued pit; amplitudes 155 / 140 / 34 m;
**visual inspection of the NAC frame at the 138–552 m nearby pit required
before any G3 inference**; r003 borderline-TP under 150 m tolerance).
Detector chain **ran on 17 of 21 on-disk NAC DTMs at the demonstrated noise floor (4 deferred: TYCHOPK 1.44 GiB memory ceiling + GRUITHUIS17/GRUITHMARE2/MARIUSCONE no cached score raster); 9 of the 17 flagged terrain_extrapolation (TYCHOPK02/03/04/07, KINGCRATER2/3/4, FRESHMELT, FRESHMELT1); highland extrapolation deferred** (TYCHOPK + 8 deferred/excluded; IRIDIUMPIT1 missed; KINGCRATER* below-floor extrapolation, 0 FPs counted; full per-DTM accounting in `transfer_summary.json` per_dtm entries) at the demonstrated noise floor (≥ 4 m at TRANQPIT1, ≥ 5 m at MARIUSPIT01 pooled under 3 × sag-band-RMS; per-DTM 0.657–1.462 m, median 1.103 m; **by-terrain split NEW: mare n=9 median 1.118 m, highland n=5 median 1.089 m** — central-peak impact melt smoother than mare regolith, NOT a portability result). The **Tranquillitatis radar conduit remains the only
subsurface structure on the Moon evidenced by any instrument today**
(Carrer 2024). Registry: **257 inferred void candidates at tier C, all
single-method (morphometry only)**; catalogued-pit recovery on 6 of 7
legacy DTMs (FECUNPIT non-recovery at N=21: 0 TPs, 6 FPs — large depressions
outside 100 m, NOT detector failure but a morphometric signal flagged for
inspection). Highland / impact-melt extrapolation produces **0 candidate FPs**
at the calibration threshold (9 sites tested). Thermal evidence
**INCONCLUSIVE** (2/7 coverage; INGENIIPIT +2.65 K = rocky-ejecta counter-
evidence; tube-scale sub-pixel at Powell 128 ppd). Multi-evidence stacking
**morphometry-only at G2**. Nothing subsurface on the Moon is verifiable
today except the Tranquillitatis radar conduit.

## 5. What does NOT pass G2

* Multi-evidence stacking (morphometry only; thermal INCONCLUSIVE; photometric P4.2 + azimuth P4.2b deferred).
* Tier-A promotions (0 by design; physics screen + span-prior deferred; I14 funnel inversion active).
* Full-mare FP rate (DTM gap partial: Cycles 1-2 (2026-08-23) closed TYCHOPK + GRUITHUIS17/GRUITHMARE2/MARIUSCONE; 30 random mare sites only remain deferred — no LROC NAC DTMs for those regions; aggregate 3.74 [1.71, 7.10] per 10⁴ km² over 24,063 km², calibration-context, NOT survey; 278 registry rows).
* Site-scale → tube-scale thermal extrapolation (Powell 128 ppd; sub-pixel at all 7 DTMs).
* Highland / impact-melt portability claim (FROZEN TRANQPIT1 mare-only; 9 sites show 0 FPs but the test is extrapolation, not portability).
* **FECUNPIT visual-inspection verdict — 3 unique depressions pending**; r003 borderline-TP under 150 m tolerance.
* TYCHOPK 1.44 GiB + 3 priority DTMs (`MARIUSCONE`, `GRUITHMARE2`, `GRUITHUIS17`) — **closed 2026-08-23 by Cycles 1-2 of the local Tier-1 plan (laptop; tile-based; 6.8 GiB Python peak)**; +4 priority DTMs still without cached score rasters.
* 30-random-mare control (no LROC coverage; **N=7 → N=21 is catalogued-pits-only**, not random).
* LROC NAC GSD detectability curve generalisation beyond 11 of 21 on-disk DTMs.
* (g) **SLDEM2015 normalisation (Step 18.1) — deferred from G0'**; needed for absolute-elevation cross-validation, deferred to post-G2.
* (h) **I12 confound covariates (LOLA track density, NAC image count) — deferred from G0' §3**; needed for FP-rate stratification, deferred to post-G2.

## 6. Path to full G2 (numbered, roadmap-anchored)

**Non-goal:** LUNARVOID will not claim lava-tube detection at G2 or any
upstream gate; only calibrated inference. Tranquillitatis radar conduit
remains the only instrumented subsurface evidence on the Moon.

1. **Visual inspection (§8, cost $0, no rental required)** — LROC NAC browse at: (a) FECUNPIT 3 depressions (138/552.5/552.5 m from nearest pit; amps 155/140/34 m; rows LV-FECUNPIT-0400cm-r001/r002/r003 + 0500cm); (b) TRANQPIT1 3 large 12-km FPs (95.4/57.4/48.8 m; lat ~ 8.75 N, lon ~ 33.20 E; rows 73–75); (c) INGENIIPIT 21 ring artifacts (r002–r008 × 3 rungs = 21 of 24 total rows; 3 share r001 location; rows 37–43/45–51/53–59).
2. **Hire Tier-1 rental (~$55 Hetzner AX52-NVMe; user pre-approves)**:
   (a) TYCHOPK 1.44 GiB — **closed 2026-08-23 by Cycle 2 (laptop; tile-based; 6.8 GiB Python peak)**; (b) 30 random-mare LROC NAC fetches +
   stereo-rebuild + krigcorr — **still open (no LROC NAC coverage on those footprints)**; (c) cached v0.5 score rasters for 7 priority
   sites — **MARIUSCONE/GRUITHMARE2/GRUITHUIS17 closed 2026-08-23 by Cycle 1 (FRESHMELT-style workflow; 18 score rasters, 0 above-floor)**; +4 sites still open; (d) ASP/ISIS
   reproducibility demo on 5–10 DTMs.
3. **MGC3 cross-body pretraining (Paper 2)** — Mars Cushing 2015/2017
   cave catalog; cross-body PU once N ≥ 30 lunar positives; blocked on
   DTM-production gap.
4. **PU-learning baselines at N ≥ 30 (P5.1)** — scikit-learn + `pulearn`;
   positive = catalogued-pit-recovered TP; growth via Step 2 (rental).
5. **Physics screen + tier-A promotion (P5.2)** — span prior (60–300 m)
   needs explicit pit-width rungs (Frangi blob proxy insufficient); ≥ 2
   independent evidence legs (needs Steps 1–4); rille-intersection NOT a
   +1 method per I14.
6. **SLDEM2015 absolute-elevation normalisation (Step 18.1, deferred from G0')** — cross-validate NAC DTM elevations against SLDEM2015; required for G3 absolute-depth claim. Deferred to post-G2.
7. **I12 confound covariates (deferred from G0' §3)** — LOLA track density + NAC image count per tile; stratify FP rate by DTM quality, rule out coverage-driven over-trigger on highland sites. Deferred to post-G2.
8. **User call on §8 T1 trigger** — if never approved, G2 stays
   DEMONSTRATION forever. Trigger APPROVED 2026-08-22 (D2, $150 ceiling)
   but rental approved but not yet authorised; cost posture unchanged
   from G1: $0 spent, $150 ceiling, $800 master-plan ceiling
   (`admin/budget.md`).

## 7. Cost audit

**$0.00 spent to date** across 22 sessions to date (matches `admin/budget.md` 18 prior + 4 G2-cycle sessions). All Tier-0 local;
no paid GPU, APIs, VPS, rentals, or storage. 11-new-LROC fetch = $0
(PDS public domain; sha256-verified). 84 score-raster GeoTIFFs under
`~/lunarvoid/data/outputs/wp2_sag/score_rasters/` = $0 (peak ~ 3 GB during
TYCHOPK07 365 MB float32). First possible spend remains **§8 T1 (Tier-1
rental) at ~ $55 for Hetzner AX52-NVMe** (24-core EPYC 7402P, 128 GB RAM,
2 × 1 TB NVMe, 20 TB/mo traffic), closing every deferred item in §6 Step 2 (rental).
Trigger user-approved at G1 (2026-08-22, D2) but rental itself not yet
authorised; **$150 ceiling preserved**.

## 8. Visual-inspection backlog (carry-forward to G3)

All require LROC NAC browse-product inspection before any G3 claim.
Logged verbally in `notes/findings.md` 2026-08-23 (NOT in registry schema —
15-col invariant) — cross-reference is notes-side only.

* **FECUNPIT 3 unique large depressions** — 552.5 m (r001/r002), 138.1 m (r003) from NEAREST catalogued pit (NOT 67 km from named Central Mare Fecunditatis Pit); amplitudes 155 / 140 / 34 m; rungs 4+5 m; rows LV-FECUNPIT-0400cm-r001/r002/r003 + 0500cm counterparts. Two readings: (a) FECUNPIT DTM edge artefacts; (b) genuine large depressions not in LROC pit catalog. **r003 at 138 m is borderline-TP under 150 m tolerance — 100 m calibration is frozen.** Cannot resolve at N=21 without LROC NAC inspection.
* **TRANQPIT1 3 large-amplitude FPs** (12-km scale) at lat ~ 8.75 N, lon ~ 33.20 E — amplitudes 95.4 / 57.4 / 48.8 m; rows 73–75 (LV-TRANQPIT1-0500cm-r001/r002/r003); visual targets = floor-fractured crater rim / ejecta / post-emplacement modification. Visual inspection REQUIRED before any G3 carry-over.
* **INGENIIPIT 21 ring artefacts** (21 ring artifacts = r002–r008 × 3 rungs of 24 total rows; 3 share r001 catalogued-pit location, not independently ring-tagged) at all 3 rungs (r002–r008, ~ 10 km from r001) — amplitudes 17–60 m; rows 37–43/45–51/53–59; visual target = LROC NAC pair at catalogued pit (lat ~ −35.95, lon ~ 166.05) to confirm ring pattern is Frangi filter artefact and not real void cluster.

---

*Data credits + traceability:* PDS/LROC/LOLA public domain (NASA/ASU LROC
team attribution preserved); LU5M812TGT CC-BY-4.0; Hurwitz et al. 2013 PSS
79-80 (cite, no explicit licence); NASA Pits and Caves analog (Wong 2014)
research/academic use only, no redistribution; Powell 2023 LRO Diviner GHRM
(PDS public domain, sha256-verified 2026-08-22); Williams, J.-P., et al. 2017,
Icarus 283, 300–325 (Diviner cumulative nighttime T algorithm); no Chandrayaan data used to
date (ISRO acknowledgement not triggered). Every number points to a CSV/JSON
in `01_WORKSPACE/data/outputs/...` or a dated `notes/findings.md` entry.
Skeptic corrections driving G1+G2 verdicts: Task 12 (mask semantics + dense
gate); Hapke (shadow-voiding + per-geometry range + i=85° rung restriction);
P3.1c (I14 inversion, FP calibration-context, ring-artefact inflation, N=7/649
scope label, mechanical vs registry tier-B, by-terrain split); P4.3 (Diviner
coverage gap + INGENIIPIT rocky-ejecta + multi-evidence-stacking limitation);
2026-08-23 (FECUNPIT distance 67 km → 138/552.5 m + r003 borderline-TP under
150 m).
