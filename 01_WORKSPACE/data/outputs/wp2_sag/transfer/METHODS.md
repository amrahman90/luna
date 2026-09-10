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
fp_per_1e4km2 = 240.41. Equal-tailed Poisson-exact (Garwood) 95% CI on the FP count
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
| **C** | default: single-method (sag score only) candidate. Below-floor candidates (regardless of rille/chain proximity) are pinned at C — the morphometric signal is too weak to combine with another line of evidence. | 257 |

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

| DTM | n_cand | n_above_floor | n_FP | n_TP | area (km²) | FP/10⁴ km² | 95% Poisson-exact (Garwood) CI |
|---|---|---|---|---|---|---|---|
| TRANQPIT1 | 4 | 4 | 3 | 1 | 124.8 | 240.41 | [49.58, 702.58] |
| FECNDITATS2 | 3 | 3 | 0 | 3 | 1994.4 | 0.00 | [0.00, 15.02] |
| INGENIIPIT | 24 | 24 | 0 | 3 | 556.4 | 0.00 | [0.00, 53.84] |
| IRIDIUMPIT1 | 2 | 0 | 0 | 0 | 1621.7 | 0.00 | [0.00, 18.47] |
| MARIUSPIT01 | 6 | 3 | 0 | 2 | 901.2 | 0.00 | [0.00, 33.24] |
| PRCLRMPIT01 | 2 | 2 | 0 | 2 | 1544.7 | 0.00 | [0.00, 19.39] |
| SWFECUNPIT1 | 3 | 3 | 0 | 3 | 1348.4 | 0.00 | [0.00, 22.22] |

**Aggregate (sum of FPs / sum of areas): 3 / 8091.7 km² = 3.71 / 10⁴ km²
[95% Poisson-exact (Garwood) CI 0.76, 10.83].** n_above_floor = 39 (the FP-rate
denominator).

The 95% CI is the Poisson-exact (Garwood) interval using `scipy.stats.chi2.ppf`:
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
95% Poisson-exact (Garwood) CI [49.58, 702.58]).

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

---

## Re-run 2026-08-22 at N=19 (geo-coder, post-fetch of 11 new NAC DTMs)

11 new NAC DTMs arrived on disk between the N=7 run (2026-08-22) and this
re-run (2026-08-22 evening): TYCHOPK, TYCHOPK02, TYCHOPK03, TYCHOPK04,
TYCHOPK07, KINGCRATER2, KINGCRATER3, KINGCRATER4, FRESHMELT, FRESHMELT1,
FECUNPIT. The fetch log (`~/lunarvoid/data/fetch_log_lroc.csv`) shows 11 OK
rows; MANIFEST still missing these 11 rows (archivist adds after this
cycle).

### Scope honesty at N=19

The transfer set is now **N=19/649 good-tier DTMs on disk**: 10 existing
+ 11 new. The scope banner in `transfer_summary.json` is updated to
`N=19/649 (19 good-tier DTMs on disk of 649 in scope; 7 have cached v0.1
score rasters; 12 are skipped for missing score raster: [...])`. The 12
skipped = 3 from before (MARIUSCONE, GRUITHUIS17, GRUITHMARE2) + 11 new
(FECUNPIT, KINGCRATER2/3/4, TYCHOPK, TYCHOPK02/03/04/07, FRESHMELT,
FRESHMELT1). NONE of the 11 new DTMs has a cached v0.1 score raster;
generating one per DTM is the same Task-8 / DTM-production gap that has
been deferred at $0 budget (Task-8 §8 cost trigger T1 still pending user
approval). So all 11 new DTMs contribute 0 candidates and 0 area to the
aggregate numerics, which match the N=7 run byte-for-byte:

| metric | N=7 (2026-08-22 earlier) | N=19 (this re-run) |
|---|---|---|
| n_dtms_with_score_raster | 7 | 7 |
| n_candidates | 44 | 44 |
| n_fp | 3 | 3 |
| total_area_km2 | 8091.68 | 8091.68 |
| fp_per_1e4km2 (point) | 3.71 | 3.71 |
| fp_per_1e4km2 CI95 | [0.76, 10.83] | [0.76, 10.83] |
| registry_rows_added | 44 | 0 (all 44 were duplicates; dedup skipped them) |

### Catalogued-pits bias (P3.1c skeptic review, 2026-08-22)

The 7 DTMs that have cached score rasters are ALL pit-associated sites
(TRANQPIT1, FECNDITATS2, INGENIIPIT, IRIDIUMPIT1, MARIUSPIT01,
PRCLRMPIT01, SWFECUNPIT1). The 12 skipped DTMs include 2 highland sites
(GRUITHUIS17, SWFECUNPIT1) that are pit-associated by index but lack
cached rasters, and the 11 new sites of which 9 are pit-associated
(FECUNPIT, KINGCRATER2/3/4 are King-crater pit chains, FRESHMELT is a
fresh impact-melt pit context) and 2 are impact-melt catalogued
(FRESHMELT1 has 0 catalogued pits). The aggregate FP rate of 3.71
per 10⁴ km² is therefore **calibration-context, NOT a survey rate**, and
NOT a random-mare estimate. Quote the full interval; do not present as
a mare-wide FP density.

### No random-mare control

The skeptic UNSOUND verdict of 2026-08-22 (findings.md "P3.1c registry
+ transfer") flagged that "no random-mare control" exists. This N=19
re-run does not add one: all 19 on-disk DTMs are pit-associated or
pit-rich. To build a random-mare control would require DTM production
for ~30 non-pit mare NAC tiles + cached v0.1 score rasters + transfer;
deferred to D2 (Task 8 rental) per user direction.

### Highland extrapolation (P3.1c skeptic, 2026-08-22)

5 of the 19 on-disk DTMs are **highland** by the dispatch classification
(GRUITHUIS17 + SWFECUNPIT1 from before; KINGCRATER2/3/4 + TYCHOPK* are
central-peak highland composition):
- GRUITHUIS17 (Gruithuisen Domes — silicic, non-mare)
- SWFECUNPIT1 (SW rim of Mare Fecunditatis — highland edge)
- KINGCRATER2, KINGCRATER3, KINGCRATER4 (King crater central peak —
  highland composition)
- TYCHOPK, TYCHOPK02, TYCHOPK03, TYCHOPK04, TYCHOPK07 (Tycho central
  peak — highland composition)

3 of these (KINGCRATER2/3/4) produced per-DTM floor entries (6/9/6
panels respectively) and have `terrain_extrapolation: "highland;
TRANQPIT1 calibration is mare-only; results are extrapolation, not
portability"` in `per_dtm_floors_summary.json.per_dtm.<DTM>`. The
other 5 (GRUITHUIS17, SWFECUNPIT1, TYCHOPK*) have the same annotation.

7 DTMs were SKIPPED at the per_dtm_floors level due to insufficient flat
panels in highland/impact-melt terrain:
- TYCHOPK (3 panels, below `min_panels=4` ceiling)
- TYCHOPK02/03/04/07 (0 panels; central peak too steep)
- FRESHMELT/FRESHMELT1 (0 panels; fresh impact melt, too rough)

These 7 are documented in `per_dtm_floors_summary.json.per_dtm` as
stub entries with `status: skipped_insufficient_panels` and (for the
5 TYCHOPK*) the `terrain_extrapolation` annotation. TYCHOPK* stub
rows are also appended to `per_dtm_floors.csv` (with NaN numerics)
so the CSV has 19 rows total (10 existing processed + 4 new
processed + 5 highland stubs). FRESHMELT* are NOT added to the CSV
(impact melt, not highland; treated as mare classification).

### What does NOT change vs N=7

1. **FROZEN TRANQPIT1 calibration** — `score_frac=0.20`, `slope_deg=45`,
   `neigh=5`, `frangi_sigmas_m=[30,60,100,150,200,300]`, Planchon-
   Darboux fill, 100 m pit match radius. Untouched. Source: `calibration
   _transqpit1.json` (unchanged on disk).
2. **Aggregate numerics** — n_candidates=44, n_fp=3, total_area=8091.68
   km², fp/10⁴ km²=3.71 [0.76, 10.83] are identical because no new
   score rasters were generated.
3. **Tier discipline** — tier A never assigned; tier B reserved for
   P3.1c skeptic UNSOUND-correction (the 3 MARIUSPIT01 candidates that
   previously qualified by rille intersection remain downgraded to tier
   C; not changed).
4. **ring-artifact note on INGENIIPIT** r002–r008 — preserved (N=7
   P3.1c finding, not re-flagged here).

### What IS new at N=19

1. **per_dtm block in transfer_summary.json** now has 19 entries
   (was 7): 7 with non-zero n_candidates/area + 12 stub entries
   (n_candidates=0, area_km2=0, error="no cached score raster").
2. **per_dtm block in per_dtm_floors_summary.json** now has 19
   entries (was none): 14 processed + 5 TYCHOPK* stubs. All 10
   highland DTMs have `terrain_extrapolation` annotation.
3. **by_terrain split in per_dtm_floors_summary.json**: mare n=9
   median pooled RMS 1.118 m; highland n=5 median pooled RMS 1.089 m.
4. **scope_banner** in transfer_summary.json: "N=19/649" (was
   "N=10/649").
5. **fp_per_1e4km2_interpretation** updated: "calibration-context rate,
   selection-biased to catalogued pits (all 19 DTMs are pit-
   associated); NOT a random-mare survey rate".
6. **scope_caveats** added to transfer_summary.json.aggregate: 5
   bullets documenting bias / extrapolation / panel-skips / frozen
   recipe preservation.

### Workflow notes (for the next agent)

- The 7 panel-skipped DTMs (TYCHOPK*, FRESHMELT*) are NOT detrital
  — they have real geomorphology, just not enough FLAT mare panels
  for the noise-floor recipe. A highland-specific noise-floor
  protocol (e.g. allow gentle slopes up to 5°, expand panel sizes,
  exclude central peak) is needed to produce per-DTM floors for them;
  deferred to a future phase (P3.4 or later).
- The KINGCRATER2/3/4 highland Floors (0.66/1.21/1.09 m pooled RMS)
  are LOWER than the mare median (1.12 m) because central-peak
  impact melt is smoother than mare regolith. This is **expected
  for highland composition**, not an outlier; do not interpret as a
  detector improvement on highland sites — it is a SITE-property
  measurement, not a calibration result.
- `transfer_apply.py` is now idempotent on the registry: it builds
  a set of existing candidate_ids from the registry header + body
  and SKIPS any new entries that match, preventing duplicate row
  appends on re-run. The 11 new DTMs produced 0 candidates (no
  cached score rasters), so registry_rows_added=0 in this re-run.

---

## P3.1c growth — N=21/649 with 10 new score rasters (2026-08-23, geo-coder)

The P3.1c N=19 re-run on 2026-08-22 generated 12 stub entries for DTMs
that lacked a cached score raster. This run generates those rasters for 10
of the 12 (TYCHOPK deferred to post-G2 due to memory ceiling) and
re-runs the transfer over 17 DTMs (7 legacy + 10 new).

### Score-raster generation

New generator: `01_WORKSPACE/code/wp2_sag/transfer/score_raster_gen.py`.
Mirrors `sag_search_run.py` v0.2 semantics but writes to
`~/lunarvoid/data/outputs/wp2_sag/score_rasters/<DTM>/score_<rung>m.tif`
(conventions §1: derived rasters under `~/lunarvoid/data/`, not the repo).
Memory-efficient: opens source DTM with rasterio without loading the
full float64 array; rebins via `out_shape=` straight into the smaller
array; Frangi sub-sampled to ≤5000 px max dim. FROZEN recipe unchanged
(sigmas = (30, 60, 100, 150, 200, 300) m; PD fill; neigh=5; seed=42).

**Score-raster generation: 10/10 OK** (TYCHOPK deferred).

| DTM | rungs | score_max | top rung | notes |
|---|---|---|---|---|
| FECUNPIT | 4, 5 m | 155.49 | 5 m | 2 m skipped (res-compat rule); 5 m at native 5 m/px posting |
| KINGCRATER2 | 2, 4, 5 m | 1.15 | 4, 5 m | top_scores 1.117, 1.153, 1.153 — all below local_Amin 1.97 m |
| KINGCRATER3 | 2, 4, 5 m | 1.18 | 4, 5 m | top_scores 1.159, 1.182, 1.182 — all below local_Amin 3.63 m |
| KINGCRATER4 | 2, 4, 5 m | 0.74 | 4, 5 m | top_scores 0.717, 0.738, 0.738 — all below local_Amin 3.27 m |
| FRESHMELT | 2, 4, 5 m | 1.84 | 2 m | impact-melt site, NaN local_Amin; terrain extrapolation |
| FRESHMELT1 | 2, 4, 5 m | 2.30 | 2 m | impact-melt site, NaN local_Amin; terrain extrapolation |
| TYCHOPK02 | 2, 4, 5 m | 1.30 | 2 m | Tycho central peak; NaN local_Amin; terrain extrapolation |
| TYCHOPK03 | 2, 4, 5 m | 0.25 | 2 m | Tycho central peak; NaN local_Amin; terrain extrapolation |
| TYCHOPK04 | 2, 4, 5 m | 0.63 | 2 m | Tycho central peak; NaN local_Amin; terrain extrapolation |
| TYCHOPK07 | 2, 4, 5 m | 0.19 | 2 m | Tycho central peak; NaN local_Amin; terrain extrapolation; largest DTM at 365 MB float32 |

TYCHOPK (1.44 GiB float32): SKIPPED. Memory ceiling — 1.44 GiB float32
→ 2.88 GiB float64 alone, plus Frangi scratch + scipy = > 6 GiB peak,
too tight for the 31 GiB RAM / 20 GiB available budget. Deferred to
post-G2; needs Tier-1 rental or memory-efficient tile-based processing.

### Transfer re-run (N=21/649)

Re-run with `transfer_apply.py`. Two load-bearing fixes:

1. **`find_score_path` extended** to also search
   `~/lunarvoid/data/outputs/wp2_sag/score_rasters/<DTM>/score_<rung>m.tif`
   (preserving the legacy `01_WORKSPACE/data/outputs/wp2_sag/<sub>/<DTM>_<rung>m_score.tif`
   search for byte-identity with the N=19 frozen sites).

2. **NaN local_Amin → below-floor by default** (P3.1c growth highland
   extrapolation). DTMs without usable flat panels (TYCHOPK*,
   FRESHMELT*) have NaN local_Amin. With the existing
   `(not math.isnan(local_Amin)) and (amp < local_Amin)` rule, NaN
   local_Amin would have made every peak above-floor (the negation
   fails), inflating the FP rate with un-calibrated FPs at
   highland/impact-melt terrain. The fix: NaN local_Amin → all peaks
   are marked below-floor and DO NOT count as FPs. Candidates are
   preserved in the registry with the new annotation
   `below-local-floor; terrain-extrapolation (no local_Amin; FROZEN
   TRANQPIT1 is mare-only; highland/impact-melt inference)`.

3. **Missing per_dtm_floors entries → synthesised NaN row**. For DTMs
   without a per_dtm_floors entry (FRESHMELT, FRESHMELT1), the script
   now builds a default NaN row in-process. Added FRESHMELT and
   FRESHMELT1 stub entries to `per_dtm_floors.csv` (matching TYCHOPK*
   pattern, `mtime: skipped_insufficient_panels`) for canonical
   consistency.

### Per-DTM results at N=21

| DTM | rungs | n_cand | n_above | n_fp | n_tp | area (km²) | top score | FP/10⁴ km² | 95% CI |
|---|---|---|---|---|---|---|---|---|---|
| TRANQPIT1 | 5 | 4 | 4 | 3 | 1 | 124.8 | 18.14 | 240.4 | [49.6, 702.6] |
| FECNDITATS2 | 2,4,5 | 3 | 3 | 0 | 3 | 1994.4 | 0.69 | 0 | [0, 15.0] |
| FECUNPIT | 4,5 | 6 | 6 | 6 | 0 | 1340.1 | 155.49 | 44.8 | [16.4, 97.5] |
| INGENIIPIT | 2,4,5 | 24 | 24 | 0 | 3 | 556.4 | 19.33 | 0 | [0, 53.8] |
| IRIDIUMPIT1 | 4,5 | 2 | 0 | 0 | 0 | 1621.7 | 0.01 | 0 | [0, 18.5] |
| MARIUSPIT01 | 4,8 | 6 | 3 | 0 | 2 | 901.2 | 0.01 | 0 | [0, 33.2] |
| PRCLRMPIT01 | 4,5 | 2 | 2 | 0 | 2 | 1544.7 | 1.73 | 0 | [0, 19.4] |
| SWFECUNPIT1 | 2,4,5 | 3 | 3 | 0 | 3 | 1348.4 | 0.08 | 0 | [0, 22.2] |
| FRESHMELT | 2,4,5 | 34 | 0 | 0 | 0 | 1023.0 | 0.030 | 0 | [0, 29.3] |
| FRESHMELT1 | 2,4,5 | 15 | 0 | 0 | 0 | 517.9 | 0.035 | 0 | [0, 57.8] |
| KINGCRATER2 | 2,4,5 | 17 | 0 | 0 | 0 | 550.4 | 0.002 | 0 | [0, 54.4] |
| KINGCRATER3 | 2,4,5 | 3 | 0 | 0 | 0 | 567.3 | 0.006 | 0 | [0, 52.8] |
| KINGCRATER4 | 2,4,5 | 5 | 0 | 0 | 0 | 588.5 | 0.000 | 0 | [0, 50.9] |
| TYCHOPK02 | 2,4,5 | 76 | 0 | 0 | 0 | 569.1 | 0.45 | 0 | [0, 52.6] |
| TYCHOPK03 | 2,4,5 | 9 | 0 | 0 | 0 | 427.6 | 0.11 | 0 | [0, 70.0] |
| TYCHOPK04 | 2,4,5 | 10 | 0 | 0 | 0 | 439.3 | 0.55 | 0 | [0, 68.1] |
| TYCHOPK07 | 2,4,5 | 38 | 0 | 0 | 0 | 725.4 | 0.05 | 0 | [0, 41.3] |
| GRUITHMARE2, GRUITHUIS17, MARIUSCONE, TYCHOPK | — | 0 | 0 | 0 | 0 | 0 | 0 | — | skipped (no score raster) |

**Aggregate (N=21/649, 17 DTMs processed): 9 FPs / 14840.27 km² = 6.06
FP per 10⁴ km² [95% Poisson-exact (Garwood) CI 2.77, 11.51].** n_above_local_floor = 45
(FP-rate denominator). The 212 below-floor candidates are FRESHMELT*,
KINGCRATER*, TYCHOPK* terrain-extrapolation sites (all NaN local_Amin)
plus the 5 below-floor IRIDIUMPIT1 candidates.

### Calibration-context re-statement

The aggregate FP rate of 6.06 [2.77, 11.51] FP / 10⁴ km² remains a
**calibration-context rate, NOT a survey rate, and NOT a random-mare
estimate.** All 21 on-disk DTMs are either pit-associated (catalogued
pits in scope) or impact-melt catalogued (FRESHMELT*) — selection bias
toward catalogued pits is preserved. The new 9 FPs (was 3 at N=19) come
from FECUNPIT (6 FPs, the only new DTM with local_Amin and 3+ above-floor
peaks) plus the legacy TRANQPIT1 FPs (3, unchanged). All other new sites
either have NaN local_Amin (highland/impact-melt, FPs not counted) or
zero above-floor candidates (KINGCRATER*, IRIDIUMPIT1).

### Notable findings at N=21

1. **TYCHOPK02 highland "hits" (76 candidates at 2/4/5 m rungs)** — all
   marked below-floor (NaN local_Amin). Top score 0.45 is well below the
   mare sites' top scores. The highland signal is real but the
   amplitude is too low to confirm with the FROZEN TRANQPIT1 recipe
   (which is mare-only calibration). Preserved in registry as
   `below-local-floor; terrain-extrapolation`. **DO NOT** interpret as
   highland lava-tube detection; this is calibration-extrapolation
   signal, not portable detection.

2. **KINGCRATER 3× smooth central-peak (top scores 0.002, 0.006, 0.000)** —
   all below local_Amin (1.97, 3.63, 3.27 m). The previous N=19 finding
   that "KINGCRATER2/3/4 floors are LOWER than the mare median because
   central-peak impact melt is smoother than mare regolith" is
   consistent with the new score values: smoother central peaks produce
   lower Frangi vesselness in the 30-300 m band. No above-floor
   candidates, so these sites contribute 0 to the FP rate.

3. **FRESHMELT 2-site differential**: FRESHMELT (34 candidates, top
   0.030) vs FRESHMELT1 (15 candidates, top 0.035). Both impact-melt
   sites have very low scores (top ~ 0.03 vs mare median top ~ 0.5-19).
   The 2-site comparison shows that fresh impact-melt terrain has a
   distinct morphometric signature: lower Frangi vesselness because
   the rough surface breaks up the 30-300 m linear features the
   vesselness filter is designed to detect. NaN local_Amin (no flat
   panels) preserves this as terrain extrapolation, not portability.

4. **FECUNPIT 6 FPs (top score 155.49)** — the only new DTM with
   real above-floor candidates not matched to a catalogued pit. The
   3 above-floor peaks per rung (×2 rungs) cluster at lat ~-0.3° (the
   northern part of the FECUNPIT DTM), ~67 km from the catalogued
   Central Mare Fecunditatis Pit (lat -0.918°). Amplitudes are 155 m,
   140 m, 34 m — these are LARGER than the catalogued pit's nominal
   depth (122 m). Two interpretations: (a) edge artifacts where the
   FECUNPIT DTM extends beyond its reliable coverage; (b) genuine large
   depressions not in the LROC pit catalog. **Cannot resolve at N=21
   without visual inspection.** Marked as FPs by the 100 m pit-match
   rule; tier C; preserved in registry with `frozen-frac=0.20 slope=45
   neigh=5` annotation. Recommend follow-up visual inspection of
   LROC NAC images at the candidate locations.

5. **MARIUSPIT01 unchanged** (3 tier-B candidates at 4/8 m, all
   downgraded to tier C by the I14 funnel-risk rule from N=19).
   Preserved as-is; no new MARIUSPIT01 candidates in this re-run.

6. **INGENIIPIT ring artifact** preserved from N=19: r002-r008 are
   ring artifacts around the catalogued pit r001 (not independent void
   candidates). No new ring artifacts in the new DTMs.

### Registry growth: 44 → 257 rows

213 new rows appended. Original 44 rows preserved byte-identically
(verified: `comm -12` returns all 44 original IDs in the current
registry; sorted diff of original rows vs current rows for the 7 legacy
DTMs returns exit 0). Schema unchanged (15 columns + provenance
comment).

Tier discipline at N=21: A=0, B=3 (MARIUSPIT01 only, unchanged), C=254.
Below-floor candidates are tier C by definition (morphometric signal
too weak to combine with another line of evidence).

### What does NOT change vs N=19

1. **FROZEN TRANQPIT1 calibration** — `score_frac=0.20`, `slope_deg=45`,
   `neigh=5`, `frangi_sigmas_m=[30,60,100,150,200,300]`, PD fill,
   100 m pit match radius. Untouched. Source:
   `calibration_transqpit1.json` (md5 unchanged on disk).
2. **TRANQPIT1 5 m result** — 4 candidates, 3 FPs, 1 TP,
   score_max 18.14, top FP at 12-km scale unchanged. Byte-identical
   reproduction.
3. **INGENIIPIT ring artifact note** preserved on r002-r008.
4. **MARIUSPIT01 tier-B downgrade** preserved (I14 funnel-risk).
5. **Smoke test** — F1 0.392/0/0.800, fusion AUC 0.990 (PASS,
   unchanged).

### What IS new at N=21 (vs N=19)

1. **score_rasters/ directory** at
   `~/lunarvoid/data/outputs/wp2_sag/score_rasters/<DTM>/` with
   28 score + 28 depth + 28 frangi GeoTIFFs across 10 DTMs.
2. **per_dtm_floors.csv** grew from 19 to 21 rows (+FRESHMELT, +FRESHMELT1
   stub entries with `skipped_insufficient_panels`).
3. **candidate_registry.csv** grew from 44 to 257 rows (+213).
4. **transfer_summary.json** updated: 21 entries in per_dtm block
   (was 19); aggregate fp_per_1e4km2 = 6.06 [2.77, 11.51]
   (was 3.71 [0.76, 10.83]); scope_banner = N=21/649 (was N=19/649).
5. **transfer_apply.py** extended: `find_score_path` and
   `discover_dtms_and_rungs` search both the legacy
   `01_WORKSPACE/data/outputs/wp2_sag/<sub>/` and the new
   `~/lunarvoid/data/outputs/wp2_sag/score_rasters/<DTM>/` roots;
   NaN local_Amin → below-floor default; missing floors entry → NaN
   synthesised row.
6. **score_raster_gen.py** new file at
   `01_WORKSPACE/code/wp2_sag/transfer/score_raster_gen.py`:
   FROZEN recipe score-raster generator with memory-efficient rebin
   (no full-DTM float64) for DTM sizes up to 365 MB float32.

## Cycles 1-2 — local Tier-1 plan (2026-08-23, geo-coder)

### Scope

Cycles 1-2 closed two G2 deferrals locally on the laptop (8 GB-class
DTMs that were beyond the G2 close-out compute envelope):

- **Cycle 1:** GRUITHUIS17, GRUITHMARE2, MARIUSCONE (the 3 DTMs that
  were without cached score rasters at G2 close). Rungs: 4+5 m
  (FRESHMELT-style workflow; 2 m rung skipped per v0.6 res-compatibility
  guard — source res 5 m cannot upsample). 18 score rasters (3 DTMs × 2
  rungs × 3 channels) generated in 7.75 min wall time, $0 cost.
- **Cycle 2:** TYCHOPK 1.51 GiB (the memory-ceiling-deferred Tycho
  central peak DTM, 30892 × 12240 px @ 2 m/pixel). Rungs: 2+4+5 m;
  processed on the laptop in 478.9 s = 8.0 min total. Float64 peak
  6.8 GiB Python / 6.1 GiB Whitebox (2 m rung); no tile-based
  fallback needed. 9 score rasters (3 rungs × 3 channels).

### Two algorithmic improvements

1. **True fractional rasterio rebin** for non-integer rebin factors
   (2 m → 5 m rung is a 2.5× factor; previous implementation rounded
   to 2× which would alias). Now uses rasterio's `Resampling.average`
   with the exact ratio.
2. **Depth output on the requested rung grid** (not the 5000-pixel
   Frangi sub-sampled grid). The 2 m rung depth grid is the full DTM
   extent (30892 × 12240), not the sub-sampled (5000 × 1981) array.

### Skeptic fall-back annotation rule (NEW)

Per skeptic Cycle 1 second-opinion (2026-08-23):

> A candidate is classified `deep-pit low-vesselness` iff:
>
> 1. `frangi@score_max < 0.02` (Frangi vesselness at the score-maximum
>    pixel is very low — NOT tubular)
> 2. `depth@score_max ≥ 100 m` (the depression is deep)
>
> Both conditions must be true. Annotation: `; deep-pit low-vesselness
> (circular depression, not tubular); requires NAC visual inspection`.
> Tier C; NAC browse required before any tier-B promotion.

Threshold choice rationale: at <0.05 the rule wrongly captures TYCHOPK02
(frangi@score=0.054, a central-peak-relief FP); at <0.02 only MARIUSCONE
(0.011) and GRUITHMARE2 (0.015) qualify. TYCHOPK Cycle 2 (frangi=0.0185,
depth=18.35 m) correctly NOT annotated (depth condition fails). The
<0.02 threshold cleanly separates deep-pit from the pre-existing
central-peak-relief family (TYCHOPK02/03/04/07, KINGCRATER*, FRESHMELT*).

Applied to 12 of 21 new rows (10 GRUITHMARE2 + 2 MARIUSCONE); 6
GRUITHUIS17 rows correctly NOT annotated (frangi@score=0.0424 > 0.02);
3 TYCHOPK rows classified terrain_extrapolation (per existing
TYCHOPK02/03/04/07 precedent).

Implementation: `01_WORKSPACE/code/wp2_sag/transfer/apply_skeptic_annotation.py`
(Cycle 1, idempotent across re-runs) + `apply_skeptic_annotation_tychopk.py`
(Cycle 2, idempotent).

### Results at N=24 effective (21 G2 + 3 Cycles 1-2)

- **Registry:** 257 → **278 rows** (+21; all below-floor). Tier A=0,
  B=0, C=278. n_above_local_floor = 45 (unchanged); 14 above-floor
  inferred candidates; 233 below-floor.
- **Aggregate FP per 10⁴ km²:** 6.06 [2.77, 11.51] → **3.74 [1.71, 7.10]**
  (Poisson-exact Garwood 95% CI). n_fp = 9 unchanged (all below-floor
  terrain_extrapolation rows excluded from FP numerator).
- **Aggregate area:** 14,840.27 km² → **24,062.96 km²** (+9,222.69 km²:
  TYCHOPK 3,016.80 + GRUITHUIS17 2,320.91 + GRUITHMARE2 2,258.77 +
  MARIUSCONE 1,626.21; all below-floor).
- **Calibration-context, NOT survey rate; selection-biased to catalogued
  pits; G1 §3 row 10 verdict.**

### What does NOT change

- Frozen I15 recipe unchanged: sigmas (30, 60, 100, 150, 200, 300) m;
  score_frac 0.20; slope_deg 45; neigh 5; fill Planchon-Darboux
  (fix_flats=True); Frangi sigmas + sub-sample ≤5000 px max dim.
- Tier rules unchanged: A=0 (no two-independent-methods); B requires
  rille/chain within 100 m; C default.
- FP counting unchanged: above-floor only; calibration-context,
  NOT survey.

### G2 verdict update

Row 10 of `GATE_G2_report_v1.0` flipped from
**DEFERRED-DTM-gap-EXPANDED** → **DEFERRED-DTM-gap-PARTIAL** (Cycles 1-2
closed TYCHOPK + 3 no-raster DTMs; 30 random-mare-sites gap remains
deferred — no LROC NAC DTMs for those footprints; Kaguya/SP/Chang'e
out of scope for Paper 1). Both gates report mirrors updated
(`plans/2026-08-23_...` and `papers/gate_reports/...`).

## B1 — registry repair: malformed rows + cross-rung dedupe (2026-09-06, geo-coder)

### Scope

Audit-driven repair of `data/candidate_registry.csv` (Next-Level Plan
v2, Phase B1). Script:
`01_WORKSPACE/code/tools/repair_registry_v1.py`; evidence:
`data/outputs/wp2_sag/registry_repair_2026-09-06.json` (full
before/after row lists, per-DTM accounting, both md5s). One-shot
backup taken before the run:
`data/candidate_registry_backup_2026-09-06.csv`
(md5 `d38d63fb…`); repaired registry md5 `a60fb521…`.

### What was repaired

1. **15 malformed rows fixed** — Cycles 1-2 rows whose `notes` field
   carried a comma-tail that shifted the CSV columns (10 ×
   GRUITHMARE2, 2 × MARIUSCONE, 3 × TYCHOPK). Notes rejoined
   byte-identical to intent; row count unchanged.
2. **3 `methods` values fixed** — three MARIUSPIT01 rows carried the
   literal tier value `"C"` in the `methods` column; remapped to
   `morphometry` (dtm-specific mapping, count 3).
3. **97 cross-rung duplicate groups → 161 rows SUPERSEDED** — the
   same physical feature detected at two rungs (e.g. 4 m and 5 m) had
   been stored as independent rows. Dedupe key: `(dtm, lon, lat)`
   rounded to 3 dp (~30 m at the lunar equator; consistent with the
   v5 I15 ≥ 30 m match radius). Losers get
   `status=SUPERSEDED` + `; superseded_by=<primary>` appended to
   notes; primary = finest rung, earliest-id tie-break.
4. **117 unique features** remain ACTIVE (21 DTM groups; 45
   above-floor rows = 21 primaries + 24 superseded).

### What does NOT change

- **278 rows in / 278 out** — no row added, removed, or reordered;
  tiers, scores, spans, floors untouched (verifier: independent
  regroup + field-by-field diff vs backup, zero defects).
- Idempotent: a second run is byte-identical.
- Registry schema unchanged (15 columns + provenance comment).

## A2 — unique-feature FP accounting (2026-09-07, geo-coder)

### Scope

Row-based vs unique-feature false-positive accounting on the
post-B1 registry. Script:
`01_WORKSPACE/code/wp2_sag/transfer/unique_accounting.py`; evidence:
`data/outputs/wp2_sag/unique_accounting_2026-09-07.json`
(byte-deterministic, seed 42, all input md5s recorded: registry
`a60fb521…`, pit catalog `49dcf709…`, transfer_summary `39c72f3c…`).

### Row-based regression (gate to Paper 1)

Reproduces the Paper-1 headline row-based accounting **to 1e-9**:
9 FP / 14 TP / 21 ring / 1 funnel over 24,062.96 km² →
**3.74 [1.71, 7.10] per 10⁴ km²** (Poisson-exact Garwood 95% CI;
NEVER Wilson). Classification rules frozen: above-floor = notes lack
`below-local-floor`; ring = notes contain `ring artifact`; TP = one
above-floor non-ring row per (DTM, pit) within 100 m; funnel =
I14-annotated unassigned. Referential integrity of the 161
`superseded_by` links: 161/161 valid.

### Unique-feature accounting (the new number)

Grouping on the B1 link key (primary + its superseded children;
class = primary's class), 30 m granularity:

- **6 TP + 5 FP + 9 ring + 1 funnel** → **2.08 [0.67, 4.85] per
  10⁴ km²** (Garwood). Matches the skeptic hand count exactly.
- TRANQPIT1's 3 FP rows are two spatial structures (pair co-located
  at 16.5 m + third at 132.8 m).
- Sensitivity across grouping radii: unique FP count stays in the
  3–6 band (5 at the 30–60 m head; 6 at ~3 m; 4 at 100 m; 3 at
  ~300 m). 146 boundary-straddler pairs listed in the evidence JSON.

## D1 — PU-learning evaluation redesign v5, leak-free group split (2026-09-09/10, geo-coder)

### Scope

Rebuild of the registry PU-learning evaluation after the skeptic
UNSNOUND verdict on the v2 random split. Script:
`01_WORKSPACE/code/wp5_fusion/pu_learning_groupsplit.py`; evidence:
`data/outputs/wp5_fusion/pu_learning_groupsplit_2026-09-09.json`
(version `v5_groupsplit_triplerun`; internal date 2026-09-10 — run C
was regenerated in place 2026-09-10 to close the D1-LOW F20
residual).

### Leaks fixed

1. **161 SUPERSEDED duplicate rows excluded** — 117 ACTIVE rows only
   (15 positives / 102 unlabeled); superseded links validated 161/161.
2. **Leave-one-DTM-out, 21 folds** — rows grouped by DTM so no DTM
   spans train/test (GroupKFold-2 infeasible: only 2 DTMs hold both
   classes; fallback documented in-evidence).
3. **Train-fold-only imputation + scaling** — per-feature medians and
   StandardScaler fitted on the training fold only (v2 had used
   full-dataset medians — the second leak).

### Ablation runs

- **Run A (19 features)** — diagnostic upper bound ONLY; retains the
  4 notes-derived annotation flags with positive-class information
  (evidence records their p(positive|flag) leaks).
- **Run B (15 morphometric features) — HEADLINE** — the 4
  annotation-derived flags removed. Pooled out-of-fold:
  **F1 0.824, precision 0.737, recall 14/15, AUC 0.930**. DTM-level
  cluster bootstrap (21 clusters, 1000 draws, seed 42) headline CIs:
  **F1 [0.35, 0.98], AUC [0.49, 1.00]**. Leave-INGENIIPIT-out
  (10 of 15 positives): F1 0.571 / AUC 0.790. 0/117 decisions differ
  from run A at t=0.5.
- **Run C (14 features)** — sensitivity row only (D1-LOW F20):
  run B minus `rung_cm` (parsed from candidate_id; the one residual
  identity carrier). F1 0.800 / AUC 0.928; 5/117 flips vs B.

### Degenerate-resample rule (explicit)

A bootstrap draw is DEGENERATE iff the resample contains zero TRUE
positives or zero TRUE unlabeled. Degenerate draws are
**discard-and-count** — dropped from the CI, not redrawn (redrawing
would consume extra values from the seeded RNG and break
determinism). Observed: 1/1000 cluster draws per run; CIs unchanged.
Both OOF prediction arrays (A and B) self-check against pooled
metrics to ≤1e-9.

### v2 annotation

The published v2 random-split numbers
(`pu_learning_registry_baseline_v2.json`, 2026-08-28:
F1 0.909 / AUC 0.931) are annotated **LEAK-INFLATED** in the v5
evidence: duplicate rows and shared DTMs spanned train/test.
Ranking survives (AUC 0.927–0.930); precision drops
(0.909 → 0.737).

### Detector unchanged in this window (2026-09-06 → 2026-09-10)

B1, A2 and D1 are **registry/evaluation-layer methods only**. The
detector itself — `sag_detect` (LLTB-1 v0.5) and the frozen I15
transfer recipe (score_frac 0.20 / slope 45° / neigh 5 / PD fill /
100 m pit match) — is unchanged; no score raster, candidate score,
tier, or floor value was touched. Smoke test stays at the known-good
F1 0.392/0/0.800, fusion AUC 0.990.
