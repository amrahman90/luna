# Hetzner Rental Kit — LUNARVOID Tier-1 Burst Compute

> **Status:** PREPARED, NOT LAUNCHED. The §8 T1 trigger (D2, $150
> ceiling) is **user-approved 2026-08-22** per `admin/budget.md` and
> `plans/2026-08-22_GATE_G1_report_v1.0.md` §3 row 9. The rental
> itself has **NOT been authorised** — see "Launch sequence" below.

## ⚠️ DO NOT RUN WITHOUT USER AUTHORIZATION

This kit is a **preparation**, not a launch. The `launch.sh` script
exists so that when the user explicitly says "launch the Hetzner
rental" (or equivalent), the cluster is reproducible in one command.
Running `launch.sh` without user permission violates the v5 §8 budget
discipline and the AGENTS.md rule "Cost: $0 spent (no actual compute
used)".

## Overview

The Hetzner burst rental is the Tier-1 compute tier for LUNARVOID
(`admin/budget.md` §"Spend tiers"). It exists to close the
**DTM-production gap** flagged at G1 (only 10 of 649 good-tier mare
NAC DTMs have on-disk rasters; 639 are missing) and the **30 random-mare
gap** flagged at G2 (TYCHOPK 1.44 GiB is deferred due to memory
ceiling on local Tier-0; needs ≥64 GB RAM and a fat NVMe).

The kit provisions a single Hetzner Cloud server (`cx52`):
- **CPU:** 24 vCPU (AMD EPYC 7402P / 7401P)
- **RAM:** 128 GB DDR4 ECC
- **Storage:** 2 × 1 TB NVMe (software RAID 0 for 2 TB scratch; or
  separate mount points if `variables.tf` `storage_layout = "split"`)
- **OS:** Ubuntu 22.04 LTS (NASA ISIS3 / USGS ASP binary compatible)
- **Bandwidth:** 20 TB/month egress (PDS NAC DTM pulls fit; LROC
  NAC EDRs + DTMs at ~3.6 GiB/sum from G2 cycle, well under the cap)
- **Cost:** ~$55/month on-demand (`cx52` rate 2026-Q3; verify in
  `variables.tf` before launch).

## Cost estimate (against $150 ceiling)

| Item | Cost USD | Notes |
|---|---|---|
| cx52 server, 1 month | 55.00 | Hetzner Cloud `cx52` on-demand rate |
| cx52 server, 2 months | 110.00 | Covers full Phase-6 burst cycle |
| Floating IPv4 (optional) | 4.50/month | Only if used; not in launch by default |
| **TOTAL 2 months** | **114.50** | **Below $150 ceiling** |
| **TOTAL 3 months** | **169.50** | **OVER ceiling — REJECTED by launch guard** |

The `launch.sh` script has a `$150 ceiling guard` that aborts if the
monthly cost × projected months > $150. Adjust the months in
`variables.tf::projected_rental_months` to either 1 (max) or 2 (max);
3-month rentals are rejected.

## Launch sequence

**Pre-launch checklist (mandatory):**

1. [ ] User explicitly says "launch the Hetzner rental" in chat.
2. [ ] Orchestrator has logged the approval in `admin/budget.md`
       (add a row to the spend table with the chat timestamp).
3. [ ] Hetzner Cloud API token is in `~/.hetzner_token` (do NOT
       commit it; create with `hcloud context create lvn` and run
       `hcloud context use lvn` to authenticate).
4. [ ] SSH keypair has been uploaded to the Hetzner project
       (otherwise terraform apply fails to provision the server).

**Launch command (after all four):**

```bash
cd 01_WORKSPACE/admin/hetzner_rental_kit
./launch.sh
```

The script will:
1. Run `terraform init` (downloads Hetzner provider).
2. Print the projected monthly cost and ask for confirmation.
3. Run `terraform apply -auto-approve` (provisions the server).
4. Wait for the server to be reachable (SSH banner up to ~3 min).
5. Run `bootstrap/install.sh` remotely (ISIS3 + ASP + Python deps).
6. Run `bootstrap/verify.sh` (smoke test post-install).
7. Print the server IP + SSH command and the first work-queue task.

**Wall time:** ~5 min from `terraform apply` to a usable cluster.
Bootstrap adds ~20 min for ISIS3 (~6 GB download) + ASP (~2 GB).

## Teardown procedure

When the work-queue is drained (or budget cap is hit, or after 2
months — whichever comes first), run:

```bash
cd 01_WORKSPACE/admin/hetzner_rental_kit
./teardown/nuke.sh
```

This deletes the server (and any associated volumes), prints the
final invoice URL, and updates `admin/budget.md` with the actual
cost. **Never delete the server out-of-band** — `nuke.sh` is the
audited path; bypassing it leaves dangling volumes and IPs that
incur post-deletion charges.

## Work queue (priority order)

The `work_queue/` directory has one markdown file per priority task,
with expected wall time, success criteria, and output paths:

1. **00_pds_retry.md** — retry NAC_EDR fetches using the script at
   `code/wp8_stereo/retry_nac_edr_fetch.py`. PDS endpoints have been
   404 since 2026-08-23; the Hetzner egress is the same as local
   egress, but the server's stable network path is a good probe.

2. **01_stereo_pipeline.md** — process 30 random-mare NAC DTMs end-
   to-end (download → ASP bundle-adjust → DTM → score rasters).
   This is the **DTM-production gap closer** flagged at G1 row 9.

3. **02_sldem2015.md** — cross-elevation validation: align NAC DTMs
   against SLDEM2015 to confirm kriging-correction preserves the
   long-wavelength (>300 m) truth. Z2 sanity-check.

4. **03_p3_1c_n51.md** — re-run the per-DTM floors + candidate
   extraction at N=51 (currently N=21 at G2 + the 30 from #2). The
   first honest survey-rate candidate set.

5. **04_mgc3_paper2.md** — Mars Cushing 2015/2017 cross-body
   pretraining for Paper 2's Mars→Moon transfer argument. Deferred
   from P5.3 at G1; now feasible at N=51.

## Monitoring checklist (during the rental)

- [ ] Cost ticker: `hcloud server list` (month-to-date spend is in
       the Hetzner Cloud Console → Billing).
- [ ] Disk usage: 2 TB NVMe; expected to fill at ~1 TB after #2
       completes. The DTM scratch is **not persistent** across
       rentals — re-pull from PDS if a second rental cycle is needed.
- [ ] ISIS3/ASP versions: log them in
       `~/lunarvoid/data/admin/rental_<startdate>_versions.json`
       (created by `bootstrap/verify.sh`).
- [ ] Failed runs: do NOT retry with `--force`. Add a row to
       `admin/budget.md` "anomalies" section.

## What NOT to do

- **Do not run launch.sh without the four-step pre-checklist.**
- **Do not commit `~/.hetzner_token`** or any other secret. Use
  Hetzner contexts (`hcloud context create`) so the token is in
  `~/.config/hcloud/cli.toml` with file permissions 0600.
- **Do not put raw NAC DTMs in the LUNARVOID repo.** They live in
  `~/lunarvoid/data/dtms/<DTM>/`. The repo gets only CSV/JSON/PNG
  manifests and the bootstrap output.
- **Do not run `terraform destroy` directly.** Use `teardown/nuke.sh`
  (audited; logs to `budget.md`).
- **Do not extend the rental beyond 2 months** without re-approval.
  The $150 ceiling is hard; the `launch.sh` guard rejects 3-month
  projections.
- **Do not install GPU drivers.** The Hetzner cx52 is CPU-only; GPU
  work goes through Tier-2 (Colab/Kaggle, $0) or Tier-3 (Vast.ai/
  RunPod GPU hourly, separate trigger).

## Files in this kit

```
hetzner_rental_kit/
├── README.md                    # this file
├── launch.sh                    # one-shot launch (USER-ONLY)
├── terraform/
│   ├── main.tf                  # hcloud_server resource
│   └── variables.tf             # cost ceiling guard + server type
├── bootstrap/
│   ├── install.sh               # ISIS3 + ASP + Python deps
│   └── verify.sh                # post-install smoke test
├── work_queue/
│   ├── 00_pds_retry.md
│   ├── 01_stereo_pipeline.md
│   ├── 02_sldem2015.md
│   ├── 03_p3_1c_n51.md
│   └── 04_mgc3_paper2.md
└── teardown/
    └── nuke.sh                  # one-shot teardown
```

## Provenance

- Trigger: v5 Master Plan §8 T1 (Tier-1 burst rental); D2 approved
  2026-08-22 per `plans/2026-08-22_GATE_G1_report_v1.0.md` §3 row 9.
- Cost ceiling: $150 / 2 months (user-set 2026-08-22).
- Server type: `cx52` (24 vCPU, 128 GB RAM, 2×1 TB NVMe) chosen to
  match the v0.5 ladder's peak memory (TYCHOPK 6 GiB; modest at 128 GB
  but leaves headroom for ASP bundle adjustment which peaks at ~32 GB
  on the 30-mare DTM set).
- Status: PREPARED, NOT LAUNCHED.
