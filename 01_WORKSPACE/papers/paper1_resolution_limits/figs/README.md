# Paper 1 — figures index (Task 16.3)

Every figure is a byte-identical copy of a committed artifact. No new
computation was performed for this index; each row maps the copy to its
authoritative source path and generating script. Numbers quoted in the
draft are traced to the artifact CSV/JSON, never to the PNG.

| Copy (in this dir) | Authoritative source | Generating script | Used in draft | Caption / numbers trace |
|---|---|---|---|---|
| `fig_ladder_hapke_grid.png` | `data/outputs/wp1_ladder/hapke/hapke_render_grid.png` | `code/wp1_ladder/hapke_render.py` | §4.5(b) | 12-panel Hapke IMSA re-render of the IndianTunnel_NorthSurface master (i=45/65/85° × az=0/90/180/270°). Geometry stats: `hapke/hapke_summary.json`. |
| `fig_ladder_sensor_preview.png` | `data/outputs/wp1_ladder/sensor/sensor_degradation_preview.png` | `code/wp1_ladder/sensor_degrade.py` | §4.5(c) | Baseline / sensor-only / Hapke / Hapke+sensor panels at 0.5 m (LLTB-1 v0.5). Numbers: `sensor/sensor_summary.json` block `composed_table_f1_test_slope`; per-arm rows `sensor/sensor_f1_comparison.csv`. |
| `fig_wp0_kriging_tranqpit1.png` | `data/outputs/wp0_kriging/TRANQPIT1_corrections.png` | `code/wp0_kriging/kriging_correction.py` | §4.5(e) | Kriged I2 correction, TRANQPIT1. Check RMSE 0.373→0.327 m: `wp0_kriging/TRANQPIT1_kriging_metrics.csv`, `*_summary.json`. |
| `fig_wp0_kriging_mariuspit01.png` | `data/outputs/wp0_kriging/MARIUSPIT01_corrections.png` | `code/wp0_kriging/kriging_correction.py` | §4.5(e) | Second instrument-geometry case; check RMSE 1.425→0.541 m: `wp0_kriging/MARIUSPIT01_kriging_metrics.csv`. |
| `fig_wp0_noise_floor_panels.png` | `data/outputs/wp0_kriging/noise_floor_panels.png` | `code/wp0_kriging/noise_floor.py` | §4.5(e) | Flat-mare residual histograms per panel; sag-band pooled RMS 1.245 m (TRANQPIT1) / 1.379 m (MARIUSPIT01): `wp0_kriging/noise_floor_stats.csv` (POOLED rows). |
| `fig_wp0_pit_recovery.png` | `data/outputs/wp0_primitive/pit_recovery_summary.png` | `code/wp0_primitive/sweep_pits.py` | §4.4 | 8-pit depression-depth recovery (7/8 ≥50% of catalogued; Marius funnel failure): `wp0_primitive/pit_recovery_table.csv`. |
| `fig_wp0_transqpit1_depth_check.png` | `data/outputs/wp0_primitive/TRANQPIT1_depth_check.png` | `code/wp0_primitive/depression_depth.py` | §4.4 | Hillshade + depth overlay at Mare Tranquillitatis Pit; recovered 129.67 m vs 105 m catalogued: `wp0_primitive/pit_recovery_table.csv`. |
| `fig_scope_map_v11_overview.png` | `plans/figures/wp0_scope_map_v11_overview.png` | `code/wp0_scope_map/scope_map_v11.py` | §1 | DTM × pit × rille × crater-density intersection map: `data/outputs/wp0_scope_map_v11/target_ranking.csv`. |
| `fig_scope_map_v11_rille_density.png` | `plans/figures/wp0_scope_map_v11_rille_density.png` | `code/wp0_scope_map/scope_map_v11.py` | §1 | Rille-density ranking (top target MARIUSCONE): `data/outputs/wp0_scope_map_v11/rille_dtms_intersect.csv`. |
| `fig_analog_registration_validation.png` | `data/outputs/wp1_analog/registration/registration_validation.png` | `code/wp1_analog/register_cave.py` (+ `coarse_search.py`, `icp.py`) | §3.1 / §4.5(a) | Cave-cloud→DTM registration (dense gate 9.3% inliers <1 m, RMS 0.490 m): `wp1_analog/registration/registration_report.json`. Shown with the Task-12 mask-semantics caveat — the rasterized footprint is an entrance-trench + skylight footprint, NOT roofed-void GT (`wp1_analog/void_mask/entrance_trench_skylight_mask_stats.json`). |

Notes:

- Outline tags F1–F3 (`data/outputs/wp1/detectability_curve.png` etc.)
  remain per-site auto-outputs under `~/lunarvoid/data/lltb1/<site>/sag/`
  (raster-data convention: outside the repo). The per-site detectability
  panels are referenced in §4.1 by that path; they are NOT copied here.
- Licence guard: all analog-derived figures ship as derived renders only
  (NASA analog dataset, research/academic use); LROC/PDS inputs are
  public domain.
