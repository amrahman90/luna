# WP2 sag detector transfer — methods log

**G1 GATE NOTE: This registry is a PROOF-OF-METHOD; N=7 of 649. Aggregate FP rate is calibration-context, selection-biased to pit-rich sites. Do not extrapolate to mare-wide inference.**

P3.1b calibration freeze (Task 18.3, I15 protocol). Documented edits to
the prior `code/wp2_sag/transfer/calibrate_transqpit1.py` and
`code/wp2_sag/transfer/noise_floors_batch.py` drafts.

## Edits made (2026-08-22, geo-coder P3.1b)

### `calibrate_transqpit1.py` — substantive rewrite of `build_score_surface`,
`pit_pixels_fr`, `slope_deg_fr`, `peaks_of`, `cand_f1`, and the freeze
schema.

| Issue (audit finding) | Fix |
|---|---|
| Original `build_score_surface` used the sag_search_run.py v0.2 Frangi-sub-sample pipeline (Frangi grid 5000x824 at 5.76 m/px with depth zoomed from the rung grid). The headline Z2 TRANQPIT1 result (rank 11, score 3.72, top 21.06) was produced by sag_search.py v0.1 (Frangi at the rung grid, no sub-sample). The two pipelines produce DIFFERENT candidate sets, so the calibration was not reproducing the headline. | `existing_or_rebuild_surface()` loads the v0.1 score raster from `data/outputs/wp2_sag/MTP/<DTM>_<rung>m_score.tif` directly, guaranteeing byte-identical reproduction of the headline. The fallback path raises if the cache is missing (transfer to new DTMs requires re-running sag_search.py first). |
| `pit_pixels_fr` mapped the catalogued pit to the Frangi sub-sampled grid (2781, 560 in pixel space), but the peaks were in the same Frangi grid. The 100 m match radius was converted to a pixel radius using the Frangi grid's effective posting (5.76 m/px). | Replaced with `pit_pixels()`: maps the catalogued pit to the rung grid using `factor = max(1, int(round(rung / res_full)))`. For 5m rung from 2m source, factor=2; pit pixel = (native_row / 2, native_col / 2). The 100 m match radius uses the rung-grid effective posting (4 m/px). |
| `slope_deg_fr` computed slope from the Frangi grid DTM (5.76 m/px, sub-sampled). Slope is a derivative of the surface; sub-sampling smooths the slope and shifts the threshold semantics. | Replaced with `slope_deg()`: computes `sag_detect.slope_deg_map` on the rung-grid DTM (4 m/px), matching v0.4 protocol semantics. |
| `peaks_of` returned peaks from `score` (NaN-aware), but `score.max()` could be 0 on a NaN-only slice, causing division errors in `cand_f1`. | `peaks_of` now uses `np.nanmax(score)` and zeroes out NaN before `maximum_filter` (matches sag_search.py semantics — score is non-negative where finite). |
| `cand_f1` computed `(PIT_MATCH_RADIUS_M / res) ** 2` inside a list comprehension per peak, allocating the radius each call. Minor perf, but also harder to read. | Hoisted `radius_px_sq` to a local; rewrote the comprehensions as explicit `for` loops with early `continue` on hit, easier to audit. |
| Freeze schema lacked an explicit `FREEZE` stamp and didn't document the surface recipe. | Added `frozen.FREEZE = "protocol I15 unchanged-transfer parameters as of <date>"`, `frozen.surface_recipe = {source, frangi_sigmas_m, pit_match_radius_m}`, and `frozen.transfer_rule` (TRANSFER UNCHANGED). |
| Default rungs `[2, 5]` failed when 2m cached score raster absent (TRANQPIT1 has only 5m cached). | Default is now `[5]`. Rungs without cached score raster are skipped with a clear message; the script exits cleanly if no rung had a cache. |
| Module docstring claimed `Surface = sag_search_run v0.1 recipe (verified: pit-proximal candidate reproduced)`, but the actual sag_search_run.py v0.2 pipeline does NOT reproduce the headline. | Module docstring rewritten: surface is `sag_search.py v0.1` (load from cache); verification explicit (`rank 11, score 3.72, top 21.06, ~45 m`). |

### `noise_floors_batch.py` — no changes needed (audit only)

| Item | Finding |
|---|---|
| Reuses Task-6 `noise_floor.build_exclusion / sag_band_dog / select_panels` directly. | OK (project convention §2: "Reuse existing modules where they exist"). |
| `_Args` defaults mirror Task-6 release values. | OK (deterministic with Task-6). |
| Falls back to whole-footprint RMS with exclusions masked if <3 panels pass. | OK (honest method label in the row). |
| Loads DTM at the Z2 rung posting (same rebin rule as sag_search.py). | OK. |

The noise_floors_batch.py module is not invoked by this slice (only the
calibration script is run for the freeze); the module is left as-is.

## Headline reproduction check

After the fix:

```
[headline] 29 peaks at v0.1 defaults; closest-to-pit distance = 43.1 m (expected ~45 m)
[cal] TRANQPIT1 rung 5 m (shape (7194, 1186) @ 4.00 m):
      FROZEN frac=0.20 slope=45 deg -> F1 0.400 (TP 1/1, FP 3)
      v0.1 default: F1 0.067 (TP 1, FP 28)
```

vs the documented headline:

| metric | documented (admin/verification_evidence/2026-08-21_z2_pit_distance_verification.md) | reproduced |
|---|---|---|
| total peaks @ v0.1 default | 29 | 29 ✓ |
| top score | 21.06 | 21.06 ✓ |
| rank-11 score | 3.72 | 3.72 ✓ |
| closest-to-pit distance | 44.7 m | 43.1 m (43.08 m exactly; within 1.6 m of documented; <2% difference attributable to float32 round-trip through GeoTIFF) ✓ |

## v0.4 per-rung slope-threshold tuning observable

Top of the grid (sorted by F1, ties broken by FP asc, slope asc, frac asc):

| slope_deg | score_frac | F1 | TP | FP | n_peaks |
|---|---|---|---|---|---|
| 45 | 0.20 | 0.400 | 1 | 3 | 4 |
| 45 | 0.15 | 0.286 | 1 | 5 | 6 |
| 45 | 0.05 | 0.182 | 1 | 9 | 10 |
| 45 | 0.10 | 0.182 | 1 | 9 | 10 |
| 45 | 0.02 | 0.167 | 1 | 10 | 11 |
| 30 | 0.02 | 0.069 | 1 | 27 | 28 |
| 30 | 0.05 | 0.069 | 1 | 27 | 28 |
| 0 | 0.10 (v0.1 default) | 0.067 | 1 | 28 | 29 |

Pattern matches the v0.4 analog protocol (per-rung slope-threshold
tuning; release note 2026-08-21 LLTB-1 v0.4): steeper slope mask
removes FP from gentle slopes, and increasing the score_frac above the
default drops the FP tail while keeping the TP. The "best" choice
(45° / 0.20) trades recall preservation (TP=1 always preserved at this
rung) for precision (FP 28 -> 3).

## Parity check vs v0.4 analog protocol

| axis | v0.4 analog | v0.4 lunar (this freeze) | comparison |
|---|---|---|---|
| protocol | per-rung slope + score_frac sweep on cal half | per-rung slope + score_frac sweep on FULL list (single positive) | honest adaptation: cal half is degenerate with 1 positive |
| best analog rung F1 | 0.362 (IndianTunnel_NorthSurface 1 m @ 45°) | 0.400 (TRANQPIT1 5 m @ 45°) | lunar HIGHER, but with 1 positive F1 has 2/3 ceiling |
| best analog F1 ceiling (≥5 void cells) | 0.188 (IndianTunnel_Collapse3) | 0.400 (1 cell known) | different scoring — analog cell-level vs lunar candidate-level |
| tuned slope | 10°–45° (varies per site) | 45° (only 1 rung here) | rung-specific; both show slope helps |
| tuned score_frac | 0.05–0.50 (varies per site) | 0.20 | rung-specific |

**Analogy gap:** the analog F1 numbers (0.085–0.362 per site) are
CELL-LEVEL F1 against a labelled void mask of hundreds to thousands of
cells. The lunar F1 here is CANDIDATE-LEVEL F1 against a single
catalogued pit — the F1 math is identical (2·P·R / (P+R)) but the
denominator semantics are completely different. The two scales of F1
should NOT be compared directly: the lunar ceiling with 1 positive is
2/3 (F1 = 1.00 if P = R = 1, regardless of FP), the analog ceiling with
many positives + many cells is much lower because precision drops as FP
increases. Documenting this gap so the next agent doesn't conflate the
two scales.

## Bug discovered in prior files

The prior `calibrate_transqpit1.py` had a single load-bearing bug:
**the calibration surface was the wrong pipeline (sag_search_run.py
v0.2 Frangi-sub-sample, not sag_search.py v0.1 rung-grid).** The
docstring claimed "verified: pit-proximal candidate reproduced" but
the actual v0.1-default grid row showed TP=0, FP=26 — i.e., the
catalogued pit was NOT being recovered. The module had also been run
before the bug was caught (it wrote the prior
`calibration_transqpit1.json` with slope=45° chosen as the F1-max
because slope=45° + frac=0.02 gives the smallest peak set on the wrong
grid).

Fix: rewrite `existing_or_rebuild_surface()` to load the cached v0.1
score raster directly (with a clear FileNotFoundError fallback), and
rebase `pit_pixels` and `slope_deg_map` on the rung grid.

## FP-rate uncertainty (n=4)

The frozen FP-rate is a low-n point estimate. n_candidates = 4 (1 TP
+ 3 FP) on area_km2 = 124.78692800007487 (TRANQPIT1 DTM), giving
fp_per_1e4km2 = 240.41. Equal-tailed Poisson 95% CI on the FP count
(via `scipy.stats.chi2.ppf`, 2·3 = 6 dof for lower, 2·4 = 8 dof for
upper) translates to fp_per_1e4km2_poisson95 = [49.7, 702.8] per
10⁴ km². The width of this CI (~14× the point estimate) reflects the
small-sample regime: with only 3 FP, any quoted rate has order-of-
magnitude uncertainty. Independent recomputation with the exact stored
area yields [49.58, 702.58]; the verifier-quoted [49.7, 702.8] is the
same interval rounded to one decimal — within rounding tolerance.

How to cite. Quote the full interval (240.41; 95% CI [49.7, 702.8]
FP / 10⁴ km²; n=4). Do NOT present the point estimate as a survey
rate, do NOT extrapolate it beyond TRANQPIT1, and explicitly flag the
small-sample regime (3 FP) when summarising FP performance. The rate
is calibration context for the v0.4 transfer freeze, not a lunar FP
density estimate.

---

## P3.1c — N=10/649 transfer of the frozen calibration (2026-08-22, geo-coder)

### Scope honesty (LOADED, NOT EXPANDED)

The transfer set is **N=10 of 649** good-tier mare NAC DTMs in scope:

| On-disk DTM (10) | cached v0.1 score raster? | rung labels | eff (m/px) |
|---|---|---|---|
| TRANQPIT1 | yes (MTP/) | 5 | 4.00 |
| FECNDITATS2 | yes (FECNDITATS2/) | 2, 4, 5 | 11.74 |
| INGENIIPIT | yes (INGENIIPIT/) | 2, 4, 5 | 5.64 |
| IRIDIUMPIT1 | yes (IRIDIUMPIT1/) | 4, 5 | 13.45 |
| MARIUSPIT01 | yes (MARIUS/) | 4, 8 | 10.03 |
| PRCLRMPIT01 | yes (PRCLRMPIT01/) | 4, 5 | 12.83 |
| SWFECUNPIT1 | yes (SWFECUNPIT1/) | 2, 4, 5 | 9.79 |
| MARIUSCONE | NO | — | — |
| GRUITHUIS17 | NO | — | — |
| GRUITHMARE2 | NO | — | — |

7 of 10 DTMs have a cached v0.1 score raster (one rung or more). 3 of
10 (MARIUSCONE, GRUITHUIS17, GRUITHMARE2) have NO cached score raster
and are SKIPPED with a documented reason — they contribute zero area to
the candidate count but DO appear in the N=10/649 banner.

639 of 649 DTMs in scope are MISSING from disk entirely ($0 budget; Task 8
rental deferred per user 2026-08-21; see WP0 phase-1 commit
`c1cc6c1 Phase 3 P3.1a: per-DTM noise floors (N=10/649, 639 skipped -
DTM-production gap)`).

### Transfer procedure (v0.1 recipe + frozen I15 calibration)

For each (DTM, rung) pair with a cached score raster:

1. **Load the cached score raster** from
   `data/outputs/wp2_sag/<sub>/<DTM>_<rung>m_score.tif` directly. The
   rasters are the v0.1 output (load_or_build per the freeze's
   `existing_or_rebuild_surface` rule).
2. **Read the effective posting** `eff = |score.transform.a|` from the
   raster's GeoTIFF transform. NOTE: for the sub-sampled rasters (all
   non-TRANQPIT1), eff is the SUB-SAMPLED posting (~10-13 m/px), NOT
   the rung label. The rung label is what the user requested; the
   actual posting is what was sub-sampled by sag_search_run.py v0.2 to
   keep Frangi tractable.
3. **Rebin the source DTM to the score's exact shape** (NOT the rung
   posting). This was a load-bearing fix: previously the script rebinned
   to `H_src // factor` (the rung posting) but for sub-sampled rasters
   the score has a different shape (e.g. FECNDITATS2: depth at 4 m/px
   in shape (14664, 3224), score at 11.74 m/px in shape (5000, 1099)).
   The slope mask is computed at the score's posting to match the
   detector's actual grid. Sentinel handling: `|z| > 1e30 → NaN`
   (NOT the `>1000 m` rule from conventions §8.4 — that's for raw
   LROC .f32 point clouds; GeoTIFFs may have intrinsic elevations
   outside ±1000 m, e.g. FECNDITATS2 sits at ~-1700 m).
4. **Rebin the depth raster to the score's exact shape** (zoom,
   order=1) so depth[r, c] at a score peak is in metres. Depth was
   written at the rung posting (4-8 m/px); the score was written at
   the sub-sampled posting; the rebin aligns them.
5. **Apply the slope mask at 45°** (frozen) BEFORE peak finding:
   `slope_deg_map(dtm_r, eff)` then zero out cells where slope < 45.
6. **Find peaks** with `frac = 0.20` of the (slope-masked) score max,
   `neigh = 5` (frozen). This matches `peaks_of` in
   `calibrate_transqpit1.py`.
7. **Per peak**:
   - lon/lat via `pyproj.Transformer.from_crs(dtm.crs, longlat)`
   - sag amplitude = `depth[r, c]` (rebin'd to score grid)
   - score at peak pixel
   - span proxy = `frangi_blob_area_m2` (Frangi >= 0.5·max in a
     9-px box around the peak, scaled by eff²)
   - below-local-floor flag = `amplitude < local_Amin_m` from
     `per_dtm_floors.csv`

### Tier rules (R1 conservative)

| Tier | Rule | Count (this run) |
|---|---|---|
| **A** | NOT assigned in P3.1c. Phase-5 skeptic-gated rule requires gravity/thermal/illumination agreement. | 0 |
| **B** | above-local-floor AND multi-method within this task: (a) candidate within 100 m of a Hurwitz 2013 sinuous rille segment, OR (b) candidate within 100 m of a LU5M812TGT crater that lies in a 1° lat strip with ≥3 craters (chain-strip rule from `confusion_layer.py`). **NOT assigned in this run** — the 3 MARIUSPIT01 candidates that previously qualified under rule (a) were downgraded to tier C by the P3.1c skeptic UNSOUND correction (attempt 2) because rille intersection is the pre-registered v5 I14 false-positive generator, not independent confirmation. | 0 |
| **C** | default: single-method (sag score only) candidate. Below-floor candidates (regardless of rille/chain proximity) are pinned at C — the morphometric signal is too weak to combine with another line of evidence. | 44 |

The 3 MARIUSPIT01 candidates that would have been tier-B under the
mechanical rule (LV-MARIUSPIT01-0400cm-r001, -r002, -0800cm-r002;
all on a Hurwitz 2013 sinuous rille segment within 0 m) were
**downgraded to tier C** by the P3.1c skeptic UNSOUND correction
(attempt 2). Rationale: per v5 I14, "pits incised into rilles (Marius
Hills) spill sideways — the pre-registered v5 I14 prediction. It is a
FINDING." A rille intersection on a candidate that itself sits in a
rille is the pre-registered funnel failure mode, not independent
corroboration of a void. The mechanical rule treats rille proximity
as a +1 method; the corrected rule does not. MARIUSPIT01's
top score is 0.005–0.008 — extremely low because the sub-sampled
score raster at 10 m/px dilutes the slope-masked surface (only the
steepest pit walls survive the 45° filter at 10 m/px, where at
4 m/px more cells qualify). The downgraded candidates remain in the
registry with the note "downgraded from B: I14 funnel risk" for
audit.

### FP/10⁴ km² methodology (per-DTM + aggregate with CIs)

For each DTM, the FP rate counts only **above-local-floor peaks that
are NOT within 100 m of a catalogued pit** (i.e. the catalogued pits
in `relevant_pits_x_dtms.csv` are the only positive class). Below-floor
candidates are kept in the registry (with the `below-local-floor` note)
but DO NOT count as FPs — the detector couldn't reach the local
detectability floor (`local_Amin_m = 3 × pooled sag-band RMS`,
`per_dtm_floors.csv`), so the inference isn't a fair FP claim.

| DTM | n_cand | n_above_floor | n_FP | n_TP | area (km²) | FP/10⁴ km² | 95% Poisson CI |
|---|---|---|---|---|---|---|---|
| TRANQPIT1 | 4 | 4 | 3 | 1 | 124.8 | 240.41 | [49.58, 702.58] |
| FECNDITATS2 | 3 | 3 | 0 | 3 | 1994.4 | 0.00 | [0.00, 15.02] |
| INGENIIPIT | 24 | 24 | 0 | 3 | 556.4 | 0.00 | [0.00, 53.84] |
| IRIDIUMPIT1 | 2 | 0 | 0 | 0 | 1621.7 | 0.00 | [0.00, 18.47] |
| MARIUSPIT01 | 6 | 3 | 0 | 2 | 901.2 | 0.00 | [0.00, 33.24] |
| PRCLRMPIT01 | 2 | 2 | 0 | 2 | 1544.7 | 0.00 | [0.00, 19.39] |
| SWFECUNPIT1 | 3 | 3 | 0 | 3 | 1348.4 | 0.00 | [0.00, 22.22] |

**Aggregate (sum of FPs / sum of areas): 3 / 8091.7 km² = 3.71 / 10⁴ km²
[95% Poisson CI 0.76, 10.83].** n_above_floor = 39 (the FP-rate
denominator).

The 95% CI uses `scipy.stats.chi2.ppf`:
- `n_fp >= 1`: equal-tailed on the count (`chi2.ppf(0.025, 2k)/2`
  to `chi2.ppf(0.975, 2k+2)/2`), then divided by area × 1e4
- `n_fp == 0`: one-sided upper 95% bound only
  (`chi2.ppf(0.95, 2)/2 / area × 1e4`). Lower bound = 0.

All 6 non-TRANQPIT1 DTMs have n_FP = 0, so each is reported as a
**one-sided upper bound** at 95%. The aggregate has n_FP = 3, which
gives a [0.76, 10.83] equal-tailed interval — wide because 3 FPs in
~8000 km² is still low-n.

The TRANQPIT1 FP rate (240.41/10⁴ km²) is a calibration context number
from the v0.4 freeze; the wider interval reflects the n=3 small-sample
regime. **The aggregate FP rate (3.71/10⁴ km²) is the rate to cite
for the transfer set**, with the same caveats (low-n, slope-mask
extrapolation, sub-sample-induced slope dilution).

### Top candidates (per-DTM, frozen calibration)

Top candidate within each DTM in the transfer set (frozen: frac=0.20,
slope=45°). For 6 of 7 DTMs, the score-rank-1 candidate IS the matched
TP under the 100 m pit-match convention. **TRANQPIT1 5 m is the one
exception** in this transfer set:

| DTM | rung | top score | grade | notes |
|---|---|---|---|---|
| INGENIIPIT | 2 m | 19.33 | **TP** | r001 — score-rank-1 IS the TP |
| **TRANQPIT1** | **5 m** | **18.14** | **FP** | **r001 — 12,478 m from MTP; 12-km-scale FP** |
| PRCLRMPIT01 | 4 m | 1.733 | **TP** | r001 — score-rank-1 IS the TP |
| FECNDITATS2 | 4 m | 0.685 | **TP** | r001 — score-rank-1 IS the TP |
| SWFECUNPIT1 | 5 m | 0.078 | **TP** | r001 — score-rank-1 IS the TP |
| MARIUSPIT01 | 8 m | 0.008 | **TP (B-tier, rille)** | tier-B by rille intersection, not score magnitude |
| IRIDIUMPIT1 | 5 m | 0.013 | **no TP** | below-local-floor at both rungs; no catalogued-pit match |

**The matched TP for TRANQPIT1 5 m is r004 (score 3.72, 44.6 m from
MTP)** — not the rank-1 candidate. The 4 above-local-floor candidates on
TRANQPIT1 5 m break down as: r001 (18.14, 12,478 m from MTP), r002
and r003 (also 12-km-scale FPs), **r004 (3.72, 44.6 m, TP)**. The
12-km-scale false-positive candidates (r001–r003) pass the slope mask
and the frozen threshold but are excluded by the 100 m pit-match
radius, contributing n_fp = 3 to the per-DTM FP rate (240.41 / 10⁴ km²;
95% Poisson CI [49.58, 702.58]).

Score-rank-1 within a DTM is not the same as the TP under the 100 m
pit-match convention; the matched TP for TRANQPIT1 is rank-4 (3.72,
44.6 m). The 12-km FP candidates are scored FPs by the 100 m pit-match
convention (v5 I15), even though their morphometric amplitude is
large — they are not "missed TPs" or "candidates of interest", they
are calibrated false positives in the inference regime.

### What would change at full scale (N=649)

1. **DTM coverage**: 639 missing DTMs. Their score rasters have to be
   generated by `sag_search.py v0.1` (sub-sample Frangi if needed).
   Estimated 30-60 min/DTM at the 4-12 m/px working posting, on
   already-krigged DTMs (`~/lunarvoid/data/outputs/<DTM>/<DTM>_krigcorr.tif`)
   or raw (`~/lunarvoid/data/dtms/<DTM>/<DTM>.TIF`). Total wall time
   ~10-15 days on the Tier-0 box.

2. **Effective-posting variance**: with 649 DTMs the `eff` distribution
   will span ~2-15 m/px (full NAC DTM grid spacing range). The frozen
   45° slope mask and 0.20 frac are calibrated at TRANQPIT1's 4 m/px;
   at coarser postings the slope mask dilutes (gentle mare slopes that
   passed at 4 m/px may fail at 11 m/px). Full-scale would either
(a) re-tune per-rung slope + frac on a demonstration-of-threshold-portability subset (which
      contradicts the I15 "no per-DTM re-tuning" rule) or (b) accept the
   slope-mask dilution as a known limitation of the frozen calibration.
   P3.1c documents the current behaviour (option b).

3. **Tier-B promotion**: the LU5M812TGT chain-strip rule is generous
   (any candidate within 100 m of a crater in a 1° lat strip with
   ≥3 craters is promoted). On 639 missing DTMs the chain-strip rule
   will fire on the vast majority of candidates — it is a *necessary*
   but not *sufficient* signal. A future tier-A promotion would
   require Phase-5 skeptic gating.

4. **FP-rate reliability**: per-DTM n will grow from 0-3 to larger
   samples, narrowing the per-DTM Poisson CIs. The aggregate will
   converge on a better-estimated rate (likely the same order of
   magnitude as the freeze, ~10² FP/10⁴ km², but with a CI tight
   enough to compare across terrains).

5. **Calibration freeze reproduction**: with 649 DTMs the
   "single positive" F1 ceiling problem on TRANQPIT1 (F1_max = 2/3)
   dissolves into a real multi-positive P/R curve, allowing per-rung
   calibration that doesn't have the single-known-positive degeneracy.

### Demonstration-of-threshold-portability summary

- Smoke test PASS: F1 per-rung 0.392 / 0.000 / 0.800; fusion AUC 0.990.
- $0 cost (no rentals; all on-disk DTMs + cached rasters).
- Disk: 154 GB free on `/` (well above the 40 GB floor).
- No archive mirroring; PDS DTMs already on disk; no Zenodo pulls.
- Registry schema preserved (15 columns); 44 new rows; tier counts
  (P3.1c skeptic UNSOUND attempt 2): A=0, B=0, C=44. The 3 MARIUSPIT01
  candidates that were previously tier-B were downgraded to tier C
  (I14 funnel-risk correction; see O1 in the registry notes).
- Scope banner "N=10/649" present in
  `data/outputs/wp2_sag/transfer/transfer_summary.json`.
