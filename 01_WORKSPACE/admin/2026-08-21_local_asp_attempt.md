# Task 8 — Local ISIS+ASP stereo reproduction attempt (TRANQPIT1)

> Written 2026-08-21 (execution session 8, R0 Task-8 close-out).
> This is the Step-8.5 either-way log. Steps 8.1-8.2 done; 8.3-8.4 open.

## Install record (Step 8.1 — DONE)

- Miniforge at `~/miniforge3`; ISIS as conda env `isis`
  (`~/miniforge3/envs/isis`), separate from the uv venv.
- ASP: prebuilt binary tarball, version 3.7.0, at
  `~/lunarvoid/asp/StereoPipeline-3.7.0-2026-06-08-x86_64-Linux`.

## EDR inventory (Step 8.2 — DONE)

Six LROC NAC EDR `.IMG` products (3 stereo pairs) under
`~/lunarvoid/data/edr/TRANQPIT1/` (+ `fetch_log.txt`):

- M137332905LE / M137332905RE
- M152655237LE / M152655237RE
- M152662021LE / M152662021RE

## Progress record (Steps 8.3-8.4 — NOT completed)

- The documented chain (lronac2isis → spiceinit → lronaccal →
  lronacecho → bundle_adjust → parallel_stereo → point2dem) never ran
  to completion; the time-box expired and the attempt was abandoned
  mid-chain.
- `~/lunarvoid/stereo/TRANQPIT1/` contains exactly ONE processed cube
  (`M152655237LE.cub`) plus `print.prt`. No bundle_adjust output, no
  stereo run logs, no output DTM.
- Step 8.4 (difference vs published TRANQPIT1) not attempted: no DTM
  to compare.

## VERDICT

local not viable as-run — attempt incomplete within time-box; Tier-1
rental stays in the §8 cost-boundary table

Failure branch of Step 8.5: the cost boundary stays as Section 8; the
T1 trigger (Tier-1 rental for the 8-pit build queue) is unchanged.

## Assets in place for an optional rerun

- ISIS env + ASP 3.7.0 binary installed and untouched.
- All 6 EDR products fetched — no re-download needed.
- 154 GB free disk (40 GB floor respected). Scratch guideline is
  100-250 GB per pair: a single pair fits only at the low end with
  aggressive intermediate cleanup (`--keep-only`); re-check before
  any rerun.
- Hardware caveat stands: 31 GB RAM / 8 cores vs ASP guidance ~40 GB /
  16 cores for ~20k x 20k pairs — keep the roadmap mitigation flags
  (`--processes 4 --corr-memory-limit-mb 5000`).
