# Task 13.4 (P1.5) — Sensor-degradation stage + composed illumination × sensor arms (LLTB-1 v0.5)

Run date: 2026-08-22. Code: `01_WORKSPACE/code/wp1_ladder/sensor_degrade.py`
(seed 42, deterministic). Same master, GT, and frozen-split protocol as
Task 13.3 (`../hapke/METHODS.md`). Consistency: the baseline,
noise-only, and all 12 Hapke arms re-run here reproduce the committed
13.3 CSV to max |ΔF1| = 0.000000 over 56 matched rows.

## Sensor stage (applied AFTER the Hapke stage, per rung, so arms compose)

1. **PSF blur** — nan-aware Gaussian (normalised convolution; NoData
   stays NoData), effective σ in cells by rung: 0.5 @ 0.5 m, 1.0 @ 1 m,
   1.5 @ 2 m, 2.0 @ 5 m (NAC-like IFOV-equivalent: blur grows modestly
   relative to cell size as product GSD coarsens).
2. **Radiometric/sensor height noise** — σ_z = C·res/SNR, C = 16.5
   calibrated so SNR = 100 @ 2 m ⇒ 0.33 m, the Z2 TRANQPIT1 NAC-DTM
   residual-RMS anchor. SNR arms 50/100/200. (σ_z: 0.5 m rung
   0.08–0.17 m; 2 m rung 0.17–0.66 m; 5 m rung 0.41–1.65 m.)
3. **Dropouts** — 0.5 % bad pixels + 2 bad lines per rung, deterministic.

Arms: baseline; noiseonly_i65 (13.3 control); sensor_snr{50,100,200};
12 Hapke geometries (13.3 replication); hs_* = Hapke + sensor(SNR=100)
on all 12 geometries; SNR 50/200 sensitivity at i65/az90.

## Composed degradation table (test F1, +10° slope mask, frozen split)

| rung | baseline | noise-only i65 | sensor-only (SNR100) | Hapke mean (range) | Hapke+sensor SNR100 mean (range) |
|-----:|---------:|---------------:|---------------------:|-------------------:|--------------------------------:|
| 0.5 m | 0.349 | 0.300 | 0.309 | 0.096 (0.051–0.122) | 0.096 (0.051–0.122) |
| 1 m   | 0.276 | 0.252 | 0.262 | 0.101 (0.052–0.124) | 0.103 (0.052–0.125) |
| 2 m   | 0.254 | 0.179 | **0.122** | 0.115 (0.066–0.148) | 0.109 (0.067–0.138) |
| 5 m   | 0.154 | 0.154 | 0.175 | 0.144 (0.000–0.179) | 0.136 (0.000–0.175) |

Full arm × rung table (incl. SNR 50/200 and per-geometry rows):
`sensor_f1_comparison.csv`; stats: `sensor_summary.json`.

## Honest findings (regressions reported, nothing re-tuned)

- **Sensor-only costs little at 0.5–1 m** (−0.040 / −0.014 vs baseline
  at SNR100) but **regresses the 2 m rung 0.254 → 0.122** (SNR50:
  0.069, SNR200: 0.074). The SNR ordering is non-monotone — n_void = 53
  at 2 m and n_void = 8 at 5 m support no fine-grained statistic; treat
  the 2 m sensor cost as real (≈halved F1) and the SNR-resolved
  ordering as noise on a small test set.
- **Composition is approximately additive where both act**: at 2 m the
  Hapke arm already sits at the shadow-voided base rate, and the sensor
  stage keeps it there (0.115 → 0.109). At 0.5–1 m the Hapke tuner
  collapse (thr=0 predict-all) dominates so completely that the sensor
  stage changes nothing (0.096 → 0.096 / 0.101 → 0.103).
- **At 5 m the effect is ~nil** (0.154 → 0.175 sensor-only, 0.136
  composed; n_void = 8 — no statistic). Consistent with 13.3: the
  degradation story is a 0.5–2 m phenomenon.
- Tuning protocol unchanged by design: the production fixed-calibration
  tuner is left to its own devices on every arm; its collapse on
  shadow-degraded arms is itself a documented finding (13.3 METHODS),
  not rescued here.

## Protocol / caveats (carry into Paper 1)

- GT FIXED from the unperturbed cloud; cal/test split FROZEN from the
  baseline arm (seed 42); no re-tuning against any degraded arm.
- Analog-scope caveat (13.3, verbatim): the label population is
  trench-hosted — shadow-prone; a roofed-sag-on-open-mare target is
  UNTESTED by this experiment.
- Task-12 entrance-trench+skylight mask NOT used as GT; NorthSurface
  numbers stay separate from the v0.4 §8 site table.
- Benchmark, not a detection claim: calibrated inference, never
  verified detection.

## Files

- `sensor_f1_comparison.csv` — all 31 arms × 4 rungs.
- `sensor_summary.json` — model, protocol, composed table, shadow-
  voiding correction numbers (both denominators), sensor stats.
- `sensor_degradation_preview.png` — baseline / sensor / Hapke /
  Hapke+sensor panels at 0.5 m.
- Perturbed rung rasters: `~/lunarvoid/data/outputs/wp1_ladder/sensor/
  <arm>/rung_<r>m.tif`.
