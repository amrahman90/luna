# Work Queue 01 — Random-Mare Stereo Pipeline (DTM-Production Gap)

**Priority:** 2 (the DTM-production gap closer)
**Wall time:** 8-12 hours per DTM × 30 = ~15 days wall-clock
(parallelizable over the 24 vCPU; ~3 days total with 4-way parallel)
**Cost:** ~$5-10 in egress (30 DTMs × ~3 GB each = ~90 GB)
**Pre-req:** ISIS3 + ASP installed (bootstrap step); 2 TB NVMe mounted
at /mnt/lunarvoid-data.

## Task

Process 30 random-mare NAC DTMs end-to-end on the Hetzner cluster,
closing the **DTM-production gap** flagged at G1 (`plans/2026-08-22_GATE_G1_report_v1.0.md`
§3 row 9): only 10 of 649 good-tier mare NAC DTMs have on-disk rasters;
639 are missing.

The 30 DTMs are selected by the orchestrator as a stratified random
sample of the 639-missing set (random-mare surface type, no catalogued
pits, size class 2-10 km²).

## Steps

1. SSH to the Hetzner server: `ssh root@<server_ip>`.
2. Ensure the project repo + data indexes are up to date:
   ```
   rsync -avz /home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube/ \
       root@<server_ip>:/opt/lunarvoid/repo/
   ```
3. Run the discovery script to pick candidates:
   ```
   /opt/lunarvoid/venv/bin/python \
       /opt/lunarvoid/repo/01_WORKSPACE/code/wp8_stereo/enumerate_lroc_dtm_availability.py \
       --output /tmp/random_mare_30.csv \
       --filter random-mare --max 30
   ```
4. For each DTM:
   a. Download NAC DTMs from PDS (parallel xargs, 4-way):
      ```
      /opt/lunarvoid/venv/bin/python \
          /opt/lunarvoid/repo/01_WORKSPACE/code/wp8_stereo/fetch_lroc_dtms.py \
          --skip-existing --max 1 --dtm <dtm>
      ```
   b. (Skip ASP bundle-adjust for cached DTMs; only run for DTMs
      needing regeneration from raw EDRs.)
   c. Run the score raster pipeline:
      ```
      /opt/lunarvoid/venv/bin/python \
          /opt/lunarvoid/repo/01_WORKSPACE/code/wp2_sag/score_raster_gen.py \
          --npz <npz> --outdir /mnt/lunarvoid-data/outputs/<dtm>/
      ```
   d. Append to the registry if candidates found:
      ```
      /opt/lunarvoid/venv/bin/python \
          /opt/lunarvoid/repo/01_WORKSPACE/code/wp2_sag/transfer/transfer_apply.py \
          --dtm <dtm>
      ```
5. After all 30 are processed, run the per-DTM floor + tier
   aggregator:
   ```
   /opt/lunarvoid/venv/bin/python \
       /opt/lunarvoid/repo/01_WORKSPACE/code/wp0_kriging/per_dtm_floors.py
   ```

## Success criteria

- 30 random-mare DTMs are downloaded, score-rasterised, and
  transferred to the candidate registry.
- Per-DTM floors are aggregated for all 30.
- The candidate registry grows by 30 × N_candidates_per_dtm (typical
  10-50; total ~300-1500 new candidates).
- No OOM (cx52 has 128 GB; TYCHOPK was 6 GiB peak; 30-mare peak
  should be ~12 GiB).
- Score rasters are SHA-256 verified against the registry entries.

## Output paths

- DTMs: `/mnt/lunarvoid-data/dtms/<dtm>/NAC_DTM_<dtm>.TIF`
- Score rasters: `/mnt/lunarvoid-data/outputs/wp2_sag/score_rasters/<dtm>/`
- Registry: `01_WORKSPACE/data/candidate_registry.csv`
- Per-DTM floors: `01_WORKSPACE/data/outputs/wp0_kriging/per_dtm_floors.csv`

## Rollback

If a DTM fails (PDS 404, OOM, NaN-shower), the orchestrator logs it
in `admin/budget.md` "anomalies" and skips it; we don't retry
mid-cycle. After the burst cycle, the orchestrator reviews all
failures and decides whether to re-run specific DTMs.

## Cost

~$5-10 egress (PDS pulls) + $55-110 cluster rental = $60-120 of the
$150 ceiling. The 30-DTM cycle is the **single largest budget item**
in the rental; it consumes most of the ceiling.

## Verification

The orchestrator runs `code/smoke_test.py` at the END of each DTM to
confirm the v0.5 ladder's known-good numbers still pass (F1
0.39/0/0.80 synthetic; fusion AUC 0.990). The 30 new DTMs are added
to the candidate registry with tier C pending a second evidence leg
(gravity/thermal/illumination).
