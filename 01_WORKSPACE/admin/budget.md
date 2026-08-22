# LUNARVOID — Budget Ledger

> All project spend, in USD, recorded here. Newest entry on top of the
> table; cost ceiling applies to the cumulative total below.

## Budget rules

- **$150 hard cap** for the Phase-6 Tier-1 rental cycle (user-set
  2026-08-22, G1 §8 T1 trigger APPROVED).
- **$800 master-plan ceiling** over 30 months (v5 Master Plan, v5 §8).
- **All spend requires orchestrator-initiated pre-approval.** Every
  receipt (invoice, VPS rental confirmation, GPU-hour receipt, egress
  charge) is recorded as a row in the table below on the day it is
  incurred; the row notes the approval link (commit hash or user
  message).
- **Spend tiers** (v5 §8 boundaries):
  - **Tier-0** = $0 — local compute, public-data downloads, free
    Colab/Kaggle GPU, free software. Default. No pre-approval required.
  - **Tier-1** = rented CPU/GPU (Hetzner, Vast.ai, RunPod, Lambda,
    etc.). Requires pre-approval and a row here.
  - **Tier-2** = HPC / institutional allocations. Out of scope for
    LUNARVOID in the 30-month plan unless v5 §8 T4 fires.

## Spend table

| Date | Item | Cost USD | Provider | Notes |
|---|---|---|---|---|
| 2026-08-22 | G1 FINAL-PASSED + Phase 6 plan + budget open | $0.00 | n/a | §8 T1 trigger APPROVED; cost ceiling $150 |
| 2026-08-22 | Session 18: Phase 5 record-only deferrals + G1 gate report | $0.00 | n/a | Phase 5 (21.2/21.3/21.4); verifier + skeptic clean |
| 2026-08-22 | Session 17: Phase 5 deferrals (PU + physics + MGC3) | $0.00 | n/a | record-only; LLTB-1 n too small for PU physics screen |
| 2026-08-22 | Session 16: Phase 4 P4.3 Diviner thermal N=7 | $0.00 | n/a | Powell 2023 grids (public); INGENIIPIT reclassed as rocky-ejecta counter-evidence |
| 2026-08-22 | Session 15: Phase 3 complete (mare transfer + registry) | $0.00 | n/a | N=7/649; A=0/B=0/C=44; FP 3.71 [0.76,10.83]/10^4 km^2 calibration-context only |
| 2026-08-22 | Session 14: P3.1a per-DTM floors | $0.00 | n/a | 10/649 DTMs; 639 skipped (DTM-production gap) |
| 2026-08-22 | Session 13: Phase 2 Paper 1 draft v0.2 | $0.00 | n/a | 68 lines; 10 figures index; FP-cell-density relabeled |
| 2026-08-22 | Session 12: Phase 1 complete + LLTB-1 v0.5 | $0.00 | n/a | verify_v05 11/11 PASS; Indian Tunnel mask guardrail |
| 2026-08-21 | Session 11: Task 12 Indian Tunnel analog + mask | $0.00 | n/a | RMS 0.490 m, entrance-only overlap; cave rungs separate |
| 2026-08-21 | Session 10: G0′ FINAL-PASSED (D1); Bug A.1 fixed, A.2 verified | $0.00 | n/a | Orchestrator lock released; autonomous loop resumed |
| 2026-08-21 | Session 9b: R1 roadmap (19 zero-cost steps, sequenced) | $0.00 | n/a | supplements ZEROCOST roadmap (no supersession) |
| 2026-08-21 | Session 9: Task 10 G0′ gate report v1.1 | $0.00 | n/a | 7 PASS + 2 process-only; Z2 claim refuted + corrected |
| 2026-08-21 | Session 8: R0 Task-8 local ASP close-out | $0.00 | n/a | local not viable; T1 trigger unchanged |
| 2026-08-21 | Session 7: agentic bring-over (skeptic, orchestrator, findings) | $0.00 | n/a | no acquisitions; new skill/SKILL.md files only |
| 2026-08-21 | Sessions 4-6: LLTB-1 v0.2/v0.3 + verification harness | $0.00 | n/a | scope-map refresh v1.1; 6 LLTB-1 sites |
| 2026-08-20 | Sessions 2-3: LLTB-1 v0.1 deliverable | $0.00 | n/a | Fieg end-to-end; 38 output files |
| 2026-08-19 | Session 1 + context: WP0 + nav (Tasks 1-7) | $0.00 | n/a | projects scaffold; AGENTS.md; v0 strategies confirmed |
| — | **Cumulative total** | **$0.00** | — | 18 prior sessions; Phase-6 rental pending P6.0 (credentials) |

## Phase 6 expected spend (planning line items, no row above yet)

- **Hetzner AX52-NVMe** (primary recommendation per VPS guide
  `00_SOURCE_ORIGINALS/VPS_Setup_Guide_Lunar_Photogrammetry.txt` +
  v5 Master Plan §7): ~€49/mo ≈ **~$55** for one month
  (24-core AMD EPYC 7402P, 128 GB RAM, 2×1 TB NVMe, 20 TB/mo traffic
  included). Wall-time: ~3 days for 308 NAC DTM stereo jobs (6
  concurrent pipelines × ~1-2 hr/pair). Spec exceeds v5 §7 targets
  (16-32 cores / 64-128 GB / 1-2 TB NVMe) at the lower cost bound.
- **Data egress**: **~$0** (Hetzner includes 20 TB/mo; ~30 GB of
  DTM pullback is negligible).
- **PDS NAC EDRs**: **$0** (public domain; fetched by product ID only).
- **Vast.ai H100 alternative**: **$1.5-2.5/hr × 24-72 hr = $36-180**
  (risk of cost overrun above $150 ceiling — discouraged unless the
  user explicitly approves).
- **Lambda Labs / RunPod** (H100/A100 spot): similar to Vast.ai
  ($36-180 for the same window; same overrun risk).

**Phase-6 spend window target:** stay ≤ $150 absolute (user-set hard
cap), prefer Hetzner AX52, fall back to Vast.ai only on user
pre-approval.
