# run_cycle.py — one-command lunar inference cycle (task C6)

Thin subprocess orchestrator for the CURRENT per-site lunar inference
cycle. Per **ADR D6 "scripts-not-package"** (ADJ-1 in
`plans/2026-09-04_Project_Audit_Next_Level_v2.md`; ADR text in the vault
at `Lunar Lavatube knowledge/decisions/D6 scripts-not-package.md`):
`run_cycle.py` **imports none of the chained scripts** — every step is an
exact venv-python invocation you can copy-paste and re-run by hand. It
adds no behaviour; it only sequences, times, and fails loudly.

## Usage

```bash
~/lunarvoid/venv/bin/python 01_WORKSPACE/code/run_cycle.py <SITE> \
    [--dtm-path PATH] [--cc-filter off|on|auto] \
    [--out-root ~/lunarvoid/data/outputs] [--dry-run] \
    [--skip-steps floors,score,transfer,accounting]
```

`--dry-run` prints the exact command graph (and evaluates the auto-skip
rules read-only) without executing anything. A failing step halts the
cycle, names the step, and prints the manual re-run command. Each run
writes a small provenance JSON to
`01_WORKSPACE/data/outputs/run_cycle/<SITE>_<UTC>.json`.

## Step graph (what actually exists today)

| # | Step | Command (source script) | Auto-skip rule |
|---|------|--------------------------|----------------|
| 0 | `site_check` | internal: resolve `~/lunarvoid/data/outputs/<SITE>/NAC_DTM_<SITE>_krigcorr.tif` else `~/lunarvoid/data/dtms/<SITE>/NAC_DTM_<SITE>.TIF` | never (fail-fast) |
| 1 | `floors` | `wp0_kriging/per_dtm_floors.py` (UNFILTERED) | skip if `<SITE>` already has a row in `data/outputs/wp0_kriging/per_dtm_floors.csv` |
| 2 | `score` | `wp2_sag/transfer/score_raster_gen.py --dtms <SITE> --rungs 2 4 5 --outdir <out-root>/wp2_sag/score_rasters` | skip if a score raster exists in EITHER root `transfer_apply.py` discovers |
| 3 | `transfer` | `wp2_sag/transfer/transfer_apply.py` (UNFILTERED) | — |
| 4 | `accounting` | `wp2_sag/transfer/unique_accounting.py` | — |

Environment wiring per ADR D6's CWD-luck constraint: children run with
`cwd = 01_WORKSPACE/code` and `PYTHONPATH = 01_WORKSPACE/code`
(venv python resolved from `$LUNARVOID_VENV_PYTHON`, default
`~/lunarvoid/venv/bin/python` — the sandbox python lacks numpy).

## Known gotchas encoded in the orchestrator (do NOT "fix" the scripts)

1. **`per_dtm_floors.py --dtm` TRUNCATES** the canonical
   `per_dtm_floors.csv` (the filtered run rewrites the whole file).
   `run_cycle` therefore only ever runs it unfiltered, and auto-skips
   when the site's (frozen) row already exists.
2. **`transfer_apply.py --dtms SITE` would clobber** the canonical
   `transfer_summary.json` with a single-site scope banner. The registry
   and summary layer is global and append-only, so the transfer step
   runs unfiltered (historical wall time ≈ 8–18 min for 35 pairs).
3. **Re-generating score rasters for a legacy-cached site would shadow
   the frozen raster** (new root wins over the legacy
   `data/outputs/wp2_sag/<sub>/` cache in `transfer_apply`'s discovery)
   and desync the registry rows reproduced from it. Auto-skip protects
   the cache; Cycles 1-2 practice was generation for new sites only.
4. **`--cc-filter` has no lunar consumer today.** Task C3 wired
   `--cc-filter off|on|auto` into the ANALOG detector
   (`wp1_detector/sag_detect.py`); no wp2_sag script accepts it.
   `on`/`auto` print a warning and are recorded in the run log only.

## Registry discipline (unchanged)

`transfer_apply.py` appends new candidate rows idempotently (dedup by
`candidate_id`), so a no-change re-run appends **zero** rows — that is
correct. Skeptic annotations, tier-B/A promotions, and registry repairs
are **MANUAL by design** (append-only discipline) and are deliberately
not chained. The cycle ends at outputs + registry/summary state.

## Frozen-artifact guard (C6-retry, 2026-09-10)

**The gotcha.** The chained scripts write canonical repo paths *by
design*: `transfer_apply.py` regenerates
`data/outputs/wp2_sag/transfer/transfer_summary.json` on every run (a
fresh `runtime_s` field ⇒ new bytes even when every number reproduces)
and rewrites `data/candidate_registry.csv` whenever new rows append;
`unique_accounting.py` rewrites
`data/outputs/wp2_sag/unique_accounting_<date>.json`, which embeds
`transfer_summary.json`'s md5. The first C6 delivery let a real run
overwrite two frozen evidence files this way; they were restored from
git by the orchestrator. The retry closes that gap.

**The guard.** Before step 1, `run_cycle` copies + sha256s the frozen
set — `candidate_registry.csv`, `transfer_summary.json`,
`calibration_transqpit1.json`, `unique_accounting_*.json`,
`data/outputs/wp5_fusion/*.json` — into a snapshot dir under the run's
out-root (`~/lunarvoid/data/outputs/run_cycle_guard/<SITE>_<ts>/`, raw
area, never the repo). After **every** step (and once more post-run)
the set is re-hashed: ANY change — including a file *created* under a
frozen glob — is restored byte-identical from the snapshot, a
prominent warning names the step that wrote canonically, and the
incident lands in the run JSON as
`frozen_writes_blocked: [{file, step, action: restored}]`. The run's
own results live ONLY in `data/outputs/run_cycle/<SITE>_<ts>.json`,
which also carries the full guard block (per-file `sha256_before` /
`sha256_after`, `all_byte_identical_after_run`).

Two consequences worth knowing:

- Restoring **between** steps matters: `unique_accounting.py` reads the
  frozen `transfer_summary.json` (not the transfer step's fresh
  rewrite), so its own rewrite reproduces the canonical bytes and no
  second incident fires — the guard fixes both victims, one transitively.
- If a *new-site* cycle genuinely should append registry rows, the
  guard will restore them away: the intended rows survive in the
  snapshot dir for manual review/promotion (registry writes stay
  MANUAL by design).

## Honest chain gaps (steps that do NOT exist yet)

- **CC post-filter on the lunar chain** — the C3 `--cc-filter` wiring
  lives in the analog `sag_detect.py` path only.
- **Kriging correction step** — `wp0_kriging/kriging_correction.py` is
  not per-site chainable (v1 C-7 note: its in-process wiring was never
  ported); the chain consumes a krigcorr raster when present, else raw.
- **Skeptic annotation** — `apply_skeptic_annotation*.py` are
  single-use, constants-baked forks (audit LOW-15); not parameterised,
  so not chained.
- **Fusion / PU-learning / Diviner steps** — registry-wide analytics
  (`wp5_fusion`, `wp4_diviner`), not part of the per-site DTM cycle.

## Verification evidence (2026-09-10, C6-retry)

- Guard unit test (scratch snapshot dir): simulated clobber of
  `transfer_summary.json` → restored byte-identical + incident
  attributed to the right step; simulated file created under the
  `unique_accounting_*.json` glob → deleted + incident. ALL PASS.
- Real cycle on TRANQPIT1 (guard live): floors/score auto-skip;
  transfer 1045.4 s — aggregate reproduced EXACTLY (278 candidates,
  45 above floor, FP 9 / 24062.96 km² = 3.74 [1.71, 7.10] per 10⁴
  km²), zero new registry rows; accounting 1.6 s, FP 3.7402
  [1.7103, 7.1000] regressed — all 8 frozen artifacts sha256-identical
  before/after (`sha256sum -c` OK; e.g. transfer_summary.json
  `3580b331…`, registry `8105fe3e…`). Guard fired ONCE — step
  `transfer` rewrote `transfer_summary.json` (fresh `runtime_s`),
  restored + warned + recorded. Accounting itself wrote byte-identical
  output (it consumed the *restored frozen* summary, md5 match). Run
  log with full guard block:
  `data/outputs/run_cycle/TRANQPIT1_20260910T180154Z.json`.
- Suite: 73/73 pytest green; smoke test at known-good F1
  0.392/0.000/0.800, fusion AUC 0.990.

## Verification evidence (2026-09-10, first delivery — superseded by the retry above)

- Dry-run on TRANQPIT1: floors/score auto-skip, transfer + accounting
  commands printed. Full-generation path dry-run-checked on GRUITHMARE2
  with a scratch `--out-root`.
- Real cycle on TRANQPIT1: transfer 1016.9 s (17m59s) — aggregate
  reproduced EXACTLY (278 candidates, 45 above floor, FP 9 / 24062.96
  km² = 3.74 [1.71, 7.10] per 10⁴ km²); accounting 1.7 s, reconciliation
  PASS; registry md5 byte-identical before/after (`a60fb521…`, zero new
  rows). Run log: `data/outputs/run_cycle/TRANQPIT1_20260910T173218Z.json`.
- Failure path: injected exit-7 child → step named, re-run command
  printed, rc propagated.
- Suite: 73/73 pytest green; smoke test at known-good F1
  0.392/0.000/0.800, fusion AUC 0.990.
