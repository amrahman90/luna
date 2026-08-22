# LUNARVOID R1 — Next-Tasks Roadmap (execution order)

Date: 2026-08-21. Status: ACTIVE planning aid.
Relation to prior plans: supplements (does NOT supersede)
`2026-08-19_ZEROCOST_Roadmap.md`, which remains the source of truth for
step text and acceptance criteria. This file sequences the remaining 19
open steps into dispatchable cycles with dependencies, agents, and stop
points. When a step completes, tick it HERE and in the ZEROCOST roadmap.

## Entry decisions (user, pending)

- [x] **D1 — G0′ gate**: pass/fail on `2026-08-21_GATE_G0prime_report_v1.1.md`
  (7 PASS + 2 process-only). On PASS: flip report status line to
  FINAL-PASSED (paper-writer, 1-line edit) before Phase 1 dispatch.
  *(PASS, user 2026-08-21)*
- [x] **D2 — Task 8 stereo**: choose (a) local rerun [$0, long CPU,
  assets in place], (b) Tier-1 rental [$50-150 — §8 cost trigger,
  REQUIRES explicit user pre-approval before any spend], or
  (c) defer until after Paper 1. Does not block Phases 0-2.
  *(defer, default, user-directed proceed 2026-08-21)*

## Phase 0 — quick fixes (parallel, $0, ~1 cycle)

- [x] **P0.1 = Bug A.1** [geo-coder→verifier→archivist] Fix
  `wp1_ladder/degrade.py:153` `axes[i]` → `axes.flat[i]`; smoke test
  still PASS. S. MUST land before Phase-1 ladder reruns.
- [x] **P0.2 = Bug A.2** [geo-coder→verifier→archivist] Fix
  `wp0_scope_map/scope_map_v11.py` wrong EPSG (use conventions-skill
  eqc/longlat CRS pair); re-verify MARIUSCONE 23.95 ranking unchanged
  (or report change honestly). S.

## Phase 1 — analog ground truth + degradation rungs → LLTB-1 v0.5

- [x] **P1.1 = Step 12.1** [geo-coder] Register Indian Tunnel
  cave-interior point cloud to its DTM (ICP or documented manual
  transform; report residual error bars). M.
- [x] **P1.2 = Step 12.2** [geo-coder, depends P1.1] Rasterize cave
  centerline footprint → ground-truth void mask for cave rungs. S.
- [x] **P1.3 = Step 13.2** [archivist, record-only] Log vegetation-
  stripping OUT-OF-SCOPE decision in findings.md + CHANGELOG (terrestrial
  analog caveat for Paper 1 limitations). S.
- [x] **P1.4 = Step 13.3** [geo-coder, depends P0.1] Hapke synthetic
  illumination re-rendering of Indian Tunnel DTM; re-run ladder rungs
  affected. M-L.
- [x] **P1.5 = Step 13.4** [geo-coder, depends P1.4] Sensor-degradation
  rung (PSF/noise model); release **LLTB-1 v0.5** via the /release
  protocol: verify_v05 script prints `PASS: N/N`, evidence JSON into
  `admin/verification_evidence/`, smoke test PASS, skeptic review of any
  new headline claim. M.

## Phase 2 — Paper 1 figures + narration

- [x] **P2.1 = Step 16.3** [paper-writer→verifier→skeptic→archivist,
  depends P1.5] Drop degradation figures into the Paper 1 skeleton;
  results narration with claim discipline (inference language, FP per
  10^4 km^2 only where measured). M.

## Phase 3 — calibrated transfer to full mare set

- [x] **P3.1 = Step 18.3** [geo-coder→verifier→skeptic→archivist,
  depends P1.5] Calibrate on TRANQPIT1, transfer UNCHANGED to the other
  good-tier mare DTMs (per-DTM noise floors at Z2 scale first — G0′
  deferral row); populate `data/candidate_registry.csv`. L. Skeptic
  review mandatory (registry writes = candidate-tier claims). *(P3.1a:
  10/649 DTMs, 639 skipped — see findings 2026-08-22; DTM-production
  gap)* *(Phase 3 complete — N=7/10 on-disk of 649; tier A=0, B=0,
  C=44; skeptic downgrades applied; FP 3.71 [0.76,10.83] per 10^4
  km^2 calibration-context rate, NOT survey rate; G1 = DEMONSTRATION
  only)* *(N=21, 11 new DTMs fetched + Frangi expansion; registry
  44→257; cost $0; TYCHOPK 1.44 GiB deferred)*
- [x] **P3.2 = Step 18.2** [decision] Multi-illumination azimuth test —
  confirm deferral pending Phase 4 stack; record decision. S.
  *(decision 2026-08-22 — recorded, not abandoned; azimuth variation
  comes for free in the Task-19 photometric-stereo stack build (P4.2);
  see findings.md "decision 2026-08-22 — multi-illumination azimuth
  test deferred")*

## Phase 4 — multi-evidence stacking (top candidates)

- [ ] **P4.1 = Step 19.1** [geo-coder, depends P3.1] For top ~20
  registry candidates: fetch NAC CDRs BY PRODUCT ID ONLY (no archive
  mirroring; MANIFEST rows per fetch). M.
- [ ] **P4.2 = Step 19.2** [geo-coder, depends P4.1] Photometric-stereo
  consistency check (independent-illumination agreement). M.
- [x] **P4.3 = Step 20.2** [geo-coder, parallel with P4.1-2] Diviner
  nighttime T + rock abundance (Powell 2023 grids) at candidate sites;
  thermal non-detection recorded as evidence, not silence. M.

## Phase 5 — calibration, gate G1, Paper 1

- [x] **P5.1 = Step 21.2** [geo-coder] PU-learning baselines (scikit-
  learn; positive = catalogued pits, unlabeled = sweep). M.
  *(deferred to post-G1 — see findings 2026-08-22)*
- [x] **P5.2 = Step 21.3** [geo-coder→skeptic] Physics screen (60-300 m
  span prior + depth-to-width) → final tier assignment in registry;
  skeptic review mandatory before any tier-A promotion (two independent
  methods rule). M. *(deferred to post-G1 — see findings 2026-08-22)*
- [x] **P5.3 = Step 21.4** [record-only] MGC3 cross-body pretraining —
  deferred (document in CHANGELOG). S. *(deferred to post-G1 — see findings 2026-08-22)*
- [x] **P5.4 — G1 gate report** [paper-writer→verifier→skeptic→USER]
  Compile G1 report (v0.5 benchmark, transfer results, stacked
  candidates, PU calibration, honest Marius/funnel failures).
  **HALT for human G1 decision.** M. *(FINAL-PASSED 2026-08-22; §8 T1 trigger APPROVED; cost ceiling $150)*
- [ ] **P5.5 — Paper 1 v1.0** [paper-writer→verifier→skeptic→archivist,
  depends P5.4 approval] Full draft, figures, cover letter; LLTB-1
  Zenodo release tag. L.

## Optional / opportunistic (manual, no dispatch)

- Weekly lit-scan: `~/lunarvoid/venv/bin/python
  01_WORKSPACE/admin/orchestrator/pipeline.py --only weekly-lit-scan`
- skeptic-review / verify-regression tasks from tasks.yaml as needed.

## Dependency graph (text)

D1 ─→ Phase 1 ─→ P2.1
P0.1 ─→ P1.4 ─→ P1.5 ─→ {P2.1, P3.1}
P1.1 ─→ P1.2 ─→ P1.4 (ground truth)
P3.1 ─→ P4.1 ─→ P4.2 ; P4.3 ∥ P4.1
{P3.1, P4.2, P4.3} ─→ P5.1 ─→ P5.2 ─→ P5.4 ─→ P5.5
D2 (Task 8) — independent track; rental path gated on user approval.

## Standing rules (unchanged)

Review chain geo-coder→verifier→(skeptic for claims)→archivist per
task; $0 spend unless §8 trigger approved; 00_SOURCE_ORIGINALS/
read-only; outputs in 01_WORKSPACE/ or ~/lunarvoid/data/; disk floor
40 GB; claim discipline enforced everywhere; T5 = ±5% v0.x
reproduction failure halts releases.

---

# PHASE 6 — Task 8 Tier-1 rental + G2 *(BLOCKED on P6.0 — credentials)*

> G1 FINAL-PASSED 2026-08-22 (commit `33cce63`); §8 T1 trigger
> APPROVED; cost ceiling $150 (user-set 2026-08-22). VPS guide primary
> recommendation: **Hetzner AX52-NVMe** (~$55/mo, 24-core, 128 GB,
> 2×1 TB NVMe, 20 TB/mo included). Wall-time estimate: 3 days for
> 308 NAC DTM stereo jobs on 6 concurrent pipelines.

- [ ] **P6.0 — credentials & provider (USER GATE; halt until user
  provides API key or root password + provider choice)**
- [ ] **P6.1 — rental provisioning** (Hetzner AX52 or equivalent per
  v5 §7; spec recorded in `admin/budget.md`)
- [ ] **P6.2 — ISIS3 + ASP install on rental** (~30 min; snapshot from
  local install or fresh)
- [ ] **P6.3 — NAC EDR fetch for top 308 target DTMs** (parallel;
  reuse `code/wp8_stereo/` if present, else create; ~30 min)
- [ ] **P6.4 — stereo pipeline run** (ASP parallel, 6 concurrent
  pipelines; ~3 days wall time; checkpoint + resume)
- [ ] **P6.5 — DTM quality gate** (≥2/3 must pass RMS < 2 m vs
  TRANQPIT1/MARIUSPIT01 reference)
- [ ] **P6.6 — pull DTMs back to local** (`rsync` to
  `~/lunarvoid/data/outputs/<SITE>/`; 308 × ~100 MB ≈ 30 GB)
- [ ] **P6.7 — re-run P3.1a (per_dtm_floors) + P3.1c (transfer_apply)
  at new N** (verify per-DTM floors match N=10 calibration)
- [ ] **P6.8 — G2 gate report** (paper-writer → verifier → skeptic →
  **USER GATE** — human G2 decision)
