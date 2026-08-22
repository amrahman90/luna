# per_dtm_floors — methods (SLICE P3.1a)
Per-DTM Z2-scale noise floors for the LUNARVOID transfer set. Reuses the
Task-6 panel-extraction + pooled-RMS pipeline
(`code/wp0_kriging/noise_floor.py`); do NOT reimplement. Driver:
`code/wp0_kriging/per_dtm_floors.py`.
## DTM list & source-file rule
Good-tier subset (relat_le <= 5 m, triang_rms <= 20 m) of
`wp0_scope_map_v11/target_ranking.csv`. Source per DTM, in order:
  1. `~/lunarvoid/data/outputs/<DTM>/NAC_DTM_<DTM>_krigcorr.tif`
     (kriging-corrected; preferred for parity with Task 6).
  2. `~/lunarvoid/data/dtms/<DTM>/NAC_DTM_<DTM>.TIF` (raw fallback).
Missing source -> SKIP + log. This run: 639 of 649 good-tier DTMs
skipped because their NAC DTMs are not on disk yet.
## Panel selection
Mirrors Task 6 with min panels raised 3 -> 4 (P3.1a convention). Each
DTM split into 3x3 zone grid (center + 4 corners + 4 edges). Per zone:
try panel sizes {2000,1500,1200,1000} m and flat gates
{0.98,0.90,0.80,0.70} (relaxed per zone until one passes). Panel
passes when: valid-px >= 0.95, slope < 2 deg from 50-px boxcar,
NOT in 3 km pit buffer (if known), NOT in 250 m + LU5M812TGT rim
buffer (0.4-5 km subset), NOT in 1 km Hurwitz rille buffer. Panels
picked near mare target centre and away from pit when pit known;
DTMs without a known pit (GRUITHUIS17, GRUITHMARE2) drop the pit
exclusion and keep the 4-7 best zones.
## Residual + sag-band
Same as Task 6: hp300 (DTM minus 300-m boxcar) and poly2 (DTM minus
2nd-order poly) residuals; pooled sag-band RMS = RMS of
DoG(s_hi=300 m) - DoG(s_lo=60 m) over cropped panel interior (300 m
margin). This is the noise competing with a 60-300 m roof sag (v5
component I3).
## Three-sigma rule
`local_Amin_m = 3 x pooled_rms_m` (project convention): a single
60-300 m sag of amplitude A is detectable in principle iff A >
local_Amin. Column-header convention:
`local_Amin_m = 3x pooled_rms (project convention)`.
## Batch + skip handling
`per_dtm_floors.py [--dtm NAME ...]` iterates the good-tier scope
list. Failures (no source file, panel count < 4, exception in
`run_dtm`) logged + skipped; CSV written with all that succeeded.
f32 sentinel: any |x| > 1000 m -> NaN (inherited from
`noise_floor.run_dtm`).
## Sampling caveat
Only 10 of 649 good-tier DTMs had NAC DTMs on disk for this run;
2 used krigcorr (TRANQPIT1, MARIUSPIT01), 8 used raw. Raw floors are
systematically higher than krigcorr (I2 removes long-wavelength
distortion). When krigging runs for the remaining 8 DTMs, expect
their pooled RMS to drop by the same factor as TRANQPIT1 (krigcorr
pooled RMS = 1.245 m matches raw because TRANQPIT1 was already
well-registered — skill §5).
## Sanity check vs Task 6
TRANQPIT1 pooled RMS = 1.245184 m (matches 1.245184 m to 6 dp).
MARIUSPIT01 pooled RMS = 1.379200 m (matches 1.379200 m to 6 dp).
Reproduction PASS for both.
## Downstream
P3.1c tiering uses `pooled_rms_m` per DTM (NOT `local_Amin_m`) with
per-DTM sag-detection F1 to bucket the transfer set into T1/T2/T3
tiers. `local_Amin` is the per-DTM detectability floor that tiering
thresholds must clear.