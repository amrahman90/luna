# Task 13.3 (P1.4) — Hapke synthetic-illumination re-render of the IndianTunnel_NorthSurface ladder master

Run date: 2026-08-22. Code: `01_WORKSPACE/code/wp1_ladder/hapke_render.py`
(seed 42, deterministic). Inputs: the LLTB-1 ladder master cloud
`IndianTunnel_NorthSurface_0.5m.npz` (61.0 M pts) and its 0.5 m master DTM
(250x131, relief 14.3 m, 37.9 % valid) — reproduced exactly
(median |dZ| vs on-disk `master_0.5m.tif` < 0.05 m, asserted).

## Photometric model

Standard Hapke **IMSA** (Hapke 1993, *Theory of Reflectance and Emittance
Spectroscopy*; Hapke 2012 2nd ed. Ch. 8S):

  r(i,e,g) = (w/4pi) * mu0/(mu0+mu) * [ (1+B(g)) P(g) + H(mu0) H(mu) - 1 ]

- Two-term Henyey-Greenstein P(g) (Hapke 1993 eq. 6.16), Chandrasekhar H
  via Hapke's 2-term rational approximation, opposition surge
  B(g) = B0 / (1 + tan(g/2)/h).
- **Parameters are lunar-mare literature values, NOT fitted** (this is an
  analog re-render): w=0.15 (mature mare visible range 0.11-0.19; Hapke
  1993 lunar fits), b=0.21, c=0.70 (backscattering regolith; Hapke 1993),
  h=0.05, B0=0.6 (typical lunar surge; Hapke et al. 2012, JGR). At
  g >= 45 deg the surge is <= 0.07 — negligible either way.
- **theta_bar omitted**: macroscopic roughness is NOT a parameter of IMSA.
  Typical mare theta_bar ~ 20-25 deg (Hapke et al. 2012) rescales absolute
  reflectance by an approximately geometry-constant factor that cancels in
  the relative-SNR use here. Documented omission, not a fit.
- Parameter insensitivity demonstrated directly: w=0.11 and w=0.19 arms at
  geometry (65 deg, 90 deg) give identical downstream F1s (to 3 decimals)
  to the w=0.15 arm — the photometric parameters do not drive the result.

## Geometry grid

- Incidence 45 / 65 / 85 deg (NAC range) x azimuth 0 / 90 / 180 / 270 deg
  (toward sun, CCW from +x) = 12 geometries. Nadir viewing (e=0); phase
  g = map-plane incidence. Per-facet mu0 from DTM normals; cast shadows by
  cell-quantised ray march (ray slope = cot(incidence) = tan(sun
  elevation) — verified against a 10 m synthetic wall: 10/21/114 m shadow
  lengths at 45/65/85 deg).
- Site relief 14.3 m; the void-label cells sit in the entrance-trench
  topography, which self/cast shadows readily. **CORRECTED 2026-08-22
  (skeptic review): azimuth-MEANS 62 % (i=45), 75 % (i=65), 92 % (i=85)
  of void cells are shadowed and removed (NoData); per-azimuth ranges
  52-68 % / 67-80 % / 85-95 %.** The numbers first reported here
  (68/79/95 % "of valid void-label cells") corresponded to favorable
  single azimuths and are superseded — both series (all-void-cell
  azimuth means vs valid-void-label per-azimuth) are now logged in
  `hapke_summary.json` (block `correction_2026-08-22`). Shadow voiding
  remains the dominant effect.

## Degradation pathway (how the render feeds the ladder)

Per geometry the master is rebuilt as what a NAC-like pipeline delivers:
1. shadowed cells (cast or self) -> NoData;
2. illumination-dependent height error sigma_z = sigma0 * sqrt(r_ref/r),
   shot-noise scaling, sigma0 = 0.33 m at the reference geometry —
   anchored to our own Z2 measurement (TRANQPIT1 NAC DTM residual RMS
   0.327 m), capped at 2.0 m, cells with r < 0.02 r_ref -> NoData;
3. rungs 0.5/1/2/5 m via degrade.py average resampling; detector chain =
   production sag_detect.py path (Planchon-Darboux fill, Frangi 30-300 m,
   per-rung threshold tuning on cal, component filter >= 5, fixed 10 deg
   slope mask).
4. **Noise-only control arm** (i=65 geometry, sigma applied but NO shadow
   voiding) isolates the noise pathway from the shadow pathway.

## Protocol (honesty)

- Ground truth FIXED from the unperturbed cloud (sag_detect
  cloud_ground_truth, 0.5 m, 1 m threshold) and the cal/test split FROZEN
  from the baseline arm (seed 42) — sag_detect.py otherwise re-derives GT
  from the same cloud it detects on, which would let photometric noise
  move the labels (confounder). Deltas are attributable to the perturbation.
- Task-12 entrance-trench+skylight mask is NOT used as sag ground truth
  (Task-12 GUARDRAILS). These NorthSurface sag-rung numbers are reported
  SEPARATELY from the v0.4 Section-8 site table; nothing here updates it.
- Regressions reported as-is; no re-tuning against the Hapke arms.

## Headline result (F1 test, +10 deg slope mask; 3-geometry summary)

| rung | baseline | noise-only i65 | Hapke geometries mean (range) | delta noise | delta shadow |
|-----:|---------:|---------------:|------------------------------:|------------:|-------------:|
| 0.5 m | 0.349 | 0.300 | 0.096 (0.051-0.122) | -0.049 | -0.252 |
| 1 m   | 0.276 | 0.252 | 0.101 (0.052-0.124) | -0.024 | -0.175 |
| 2 m   | 0.254 | 0.179 | 0.115 (0.066-0.148) | -0.075 | -0.139 |
| 5 m   | 0.154 | 0.154 | 0.144 (0.000-0.179) | +0.000 | -0.009 |

Mechanism: in every full-Hapke arm the calibration-half threshold
tuner collapses to the degenerate predict-all solution (thr=0) because
most label cells are shadow-voided. **Attribution (skeptic review,
2026-08-22): the thr=0 predict-all solution is a collapse of the
PRODUCTION FIXED-CALIBRATION PIPELINE, not proven information loss —
except i=85°, where label voiding is genuine information loss**
(predict-all recall at i=45-65 is 0.73-0.97; at i=85 the recall
ceiling is 0.16-0.44). No shadow-aware re-tune was run, by protocol —
the tuner-collapse behaviour is itself a documented finding, not a bug
to tune away. Mean test F1 (+10° slope mask) falls 0.35 → 0.10 across
the 12 geometries at 0.5 m, but the per-geometry spread is wide:
**always quote the per-geometry range 0.051-0.122 alongside the mean.**
Photometric noise alone (noise-only control) costs only ~0.02-0.08 F1.
**The illumination effect at NAC geometries is dominated by shadow
voiding of trench-hosted void cells, not photometric noise.**

Analog-scope caveat (must ride along VERBATIM into Paper 1): this
experiment's label population is trench-hosted (cave interior seen
through the trench/skylights) — exactly the shadow-prone population.
A roofed-sag-on-open-mare target is UNTESTED by this experiment; a
true flat-roof sag on open mare would be less shadow-affected. This
analog cannot test that pathway. Interpretation discipline: calibrated
inference, never verified detection.

## Files

- `render_i{45,65,85}_az{0,90,180,270}.tif` — 12 Hapke reflectance renders
  (float32 GeoTIFF, master transform, 0 = shadow).
- `hapke_render_grid.png` — 12-panel preview.
- `hapke_f1_comparison.csv` — all arms x rungs (F1, P, R, FP/10^4 km^2,
  valid frac, thresholds).
- `hapke_summary.json` — parameters, geometry stats (shadow fraction,
  sigma_z quantiles), per-arm F1 deltas, protocol + honesty notes.
- Perturbed masters/rungs (raster-scale): `~/lunarvoid/data/outputs/
  wp1_ladder/hapke/<geom>/` (raster-data convention).
