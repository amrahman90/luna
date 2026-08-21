# Verification Evidence

This directory holds the **deterministic, versioned records** of
the ad-hoc verification runs that confirm each module's correctness
against the real NASA analog / lunar data the project depends on.

The verification scripts themselves live here too, so future
agents can re-run them and re-generate the records.

## What's here

```
verification_evidence/
├── README.md                                          <- this file
├── 2026-08-20_v01_v02_smoke_test_verification.json     v0.1/v0.2 smoke (session 3)
├── 2026-08-21_v02_regression_verification.json         v0.2 regression (session 5)
├── 2026-08-21_v03_lift_verification.json               v0.3 slope-mask lift (session 5)
└── scripts/
    ├── verify_v02_f32dir_and_filter.py                 the v0.2 verification script
    └── verify_v03_slope_mask.py                        the v0.3 verification script
```

## How to use this

```bash
# Re-run v0.2 verification (regression check)
~/lunarvoid/venv/bin/python 01_WORKSPACE/admin/verification_evidence/scripts/verify_v02_f32dir_and_filter.py

# Re-run v0.3 verification (lift check)
~/lunarvoid/venv/bin/python 01_WORKSPACE/admin/verification_evidence/scripts/verify_v03_slope_mask.py
```

Each script writes a fresh `/tmp/hermes-verify-vXX-*.json` for the
ongoing session and prints `PASS: N/N (ALL OK)` on success.

## Why ad-hoc and not a test suite

These are **ad-hoc verifications**, not a project test suite. The
proper pytest + fixtures suite is a v0.2+ backend deliverable
(captured in the `lunarvoid-lltb1-build` skill under
"v0.4 candidates"). The reason this is recorded as evidence and
not a test: the project's deliverable is the **end-to-end numbers
on real data**, not the unit-test count. The verification scripts
exercise the same code paths against the same data the headline
results are derived from.

## Verification matrix (latest run)

| Commit | Verification | Result | JSON |
|---|---|---|---|
| `574015b` Initial commit | v01_v02_smoke (16 checks) | ALL OK | `2026-08-20_v01_v02_smoke_test_verification.json` |
| `49b9927` LLTB-1 v0.2 | v02 regression (21 checks) | ALL OK | `2026-08-21_v02_regression_verification.json` |
| `cbc384c` LLTB-1 v0.2.1 | implicit (no code changes) | — | — |
| `d81addd` LLTB-1 v0.3 | v03 lift (15 checks) | ALL OK | `2026-08-21_v03_lift_verification.json` |
| `TBD` LLTB-1 v0.4 | v04 tune-slope (11 checks) | ALL OK | `2026-08-21_v04_tune_slope_verification.json` |

When a new commit lands, append a new JSON and update this table.

## What the verifications check

### v0.2 (verify_v02_f32dir_and_filter.py)
- `wp1_lla/convert_f32.py`: sentinel filter (no |xyz| > 1e3 m),
  full finite, range sanity, CLI run, .npz written
- `wp1_detector/sag_detect.py`: `filter_small_components()`
  exists, behaves correctly on synthetic masks, CLI
  `--min-component` flag works, summary has new fields
- `wp1_lla/run_lltb1.py`: empty `--f32-dir` triggers
  auto-discovery under `~/lunarvoid/data/analog/<site>/[subdir/]`,
  suffix stripping for `_10x`, `_1x`, etc.
- `code/setup/extract_rar.py`: `get_bsdtar()` returns the local
  install path, multi-mirror fallback present

### v0.3 (verify_v03_slope_mask.py)
- `wp1_detector/sag_detect.py`: `slope_mask()` exists, behaves
  correctly on flat/steep/NaN/disabled surfaces
- CLI `--slope-mask-degrees` flag present and wired
- End-to-end on Fieg_A: `f1_test_slope` and `slope_mask_degrees`
  fields in `sag_summary.json`, `slope_ok_*.tif` audit raster
  written
- Lift verification on Kingsbowl 5m: F1 raw 0.0019 -> +slope
  0.0447 (>=10x lift)

### v0.4 (verify_v04_tune_slope.py)
- `wp1_detector/sag_detect.py`: `slope_deg_map()` returns the
  continuous slope-degree map; `tune_slope_threshold()` picks
  the F1-maximising slope on the calibration half
- CLI `--tune-slope` flag present and wired (and `--help` doesn't
  crash with `TypeError: %o format` after the help-string tweak)
- End-to-end on Fieg_A with `--tune-slope`: `slope_mask_tuned`
  field is True, `slope_mask_degrees` is the *tuned* value (not
  the 10° default), F1 `+slope` lifts above 0.05 (we see 0.137)
- v0.3 regression: re-running verify_v03_slope_mask.py still
  passes 15/15 (no regression on the slope_mask path)
