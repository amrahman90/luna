# Paper 2 — outline sketch (aspirational; post-Paper-1)

> Tags: #plan #paper-2 #mgc3 #cross-body #deferred #post-rental #post-visual-inspection

Sketch of Paper 2 — the "extension / cross-body / multi-evidence" paper. This is a pre-emptive outline for when the current blockers clear (visual inspection, Cycles 3-5, Tier-A promotion).

## Trigger conditions (all must be true)

1. **Visual inspection complete** for at least 15 of 27 backlog candidates (the user's most-leveraged action)
2. **N ≥ 30 tier-B candidates** (currently 0; needs visual inspection promotion + tier-A evidence)
3. **Cycles 3-5 closed** (NAC EDR + ASP stereo + quality gate) — either PDS URL pattern found OR Hetzner rental authorized
4. **Multi-evidence stacking at ≥2 evidence legs** at ≥5 candidates (morphometry + gravity/thermal/illumination)

## Target venue

**Icarus** (Elsevier; lunar science flagship) — primary
**Planetary and Space Science** (Elsevier; mid-tier) — secondary
**Remote Sensing of Environment** (Elsevier; method-paper slot) — tertiary (if Paper 1 accepted at RSE, Paper 2 to Icarus)

## Tentative title

> "Multi-evidence inference of lunar lava-tube roof candidates from
> LROC NAC morphometry, GRAIL gravity, and Diviner thermal: calibrated
> tier-A promotions at N=30+ across 24 on-disk DTMs."

## Section sketch (NOT yet drafted)

### §1 Introduction
- Calibration transferability argument (Paper 1 was ~5 m GSD; Paper 2 extends to multi-rung + multi-evidence)
- Tier-A requires ≥2 independent evidence legs (Paper 1 §3.3 noted but did not implement)
- Bracketed claim discipline: "morphometrically similar to void signature + thermal/gravity consistent with subsurface cavity; warranting follow-up"

### §2 Background — multi-evidence lunar void detection
- Wagner & Robinson 2021 (Pit Atlas; ~281 catalogued)
- Williams 2017 (Diviner cumulative nighttime temperature)
- Powell 2023 (LRO Diviner GHRM)
- Cushing 2015 / 2017 (Mars Global Cave Catalog — MGC3 cross-body pretraining)
- Le Corre 2025 (ESSA Mask R-CNN — comparison)
- Carrer 2024 (Tranquillitatis radar conduit — the only verified subsurface evidence)

### §3 Methods
- §3.1 Detector chain at 4 multi-evidence rungs (2, 5, 10, 20 m)
- §3.2 GRAIL GRGM1200A gravity anomaly stacking (l_max=680; v0.1)
- §3.3 Diviner thermal anomaly detection (Powell 2023 GHRM)
- §3.4 Multi-evidence fusion (Bayesian OR-rule with calibration priors)
- §3.5 Tier rules — A requires ≥2 independent methods (Paper 1 §3); B requires rille/chain within 100 m; C single-method
- §3.6 MGC3 pretraining (Cushing 2015/2017 catalog; HiRISE/CTX skylight morphology)

### §4 Results
- §4.1 N=30+ tier-B candidates after visual inspection (FECUNPIT r003 borderline + ring-artifact de-weighting + GRUITHMARE2/MARIUSCONE reclassification)
- §4.2 Multi-evidence per-candidate score (gravity + thermal agreement)
- §4.3 Tier-A promotion table (≥2 evidence legs)
- §4.4 Failure modes — extended FP family including:
  - central-peak-relief (Paper 1 §4.4)
  - deep-pit low-vesselness (Paper 1 §4.4; skeptic Cycle 1 rule)
  - thermal-gravity disagreement (NEW for Paper 2 — candidate with morphometry signal but thermal/gravity inconsistent)
  - **tier-A over-promotion** (NEW — paper-writer should flag any tier-A that lacks ≥2 evidence legs)

### §5 Discussion
- §5.1 Sample size N=30+ — calibration-context rate; selection-bias caveats
- §5.2 Honest limitations — visual-inspection dependence; thermal coverage gaps; gravity resolution at l_max=680 (~6 km Rayleigh)
- §5.3 What this paper is and is NOT (inference vs detection)

### §6 Conclusion
- Tier-A promotion rate vs Paper 1 (A=0)
- MGC3 cross-body transferability
- Future: NAC DTMs from Tier-1 rental; SLDEM2015 absolute-elevation; I12 confound covariates

## Scope

- **Length**: ~9 pages (similar to Paper 1)
- **Figures**: ~8 (multi-evidence per-candidate panels; tier-A promotion heatmap; MGC3 pretraining loss curves)
- **Tables**: ~4 (tier-A promotions; thermal-gravity agreement; FP rate by tier; coverage gaps)
- **References**: ~15-20 (extends Paper 1's 10; adds MGC3 / Icarus-specific literature)

## What's needed BEFORE drafting

1. **Visual inspection verdicts** for 15-27 backlog candidates (user-driven via LROC QuickMap; ~30-60 min)
2. **Cycles 3-5 close** (PDS NAC_EDR URLs OR Hetzner rental; ~1-3 days wall time)
3. **P5.2 physics screen** implementation (currently deferred; ~2 weeks; tier-A promotion requires span prior 60-300 m + ≥2 independent methods)
4. **GRAIL GRGM1200A l_max=1200** full download (deferred from v0.1 subset; ~600s timeout issue)
5. **SLDEM2015 normalisation** (Step 18.1; ~30 LOC; deferred from G0′)
6. **I12 confound covariates** (LOLA track density + NAC image count per DTM; deferred from G0′)
7. **MGC3 cross-body pretraining** (Cushing 2015/2017 catalog; HiRISE/CTX archive negotiation — outside master-plan §8 budget)

## Time estimate

If all blockers clear by end of August 2026:
- Cycles 3-5 close: 1-3 days (rental)
- P5.2 physics screen: 2 weeks
- Visual inspection: 1 day (user-driven)
- Paper 2 drafting: 2 weeks
- Submission: 2 weeks (paper-writer → verifier → skeptic → archivist)
- **Total: ~6 weeks to Paper 2 v1.0 submission**

## Cost estimate (if rental authorized)

- Hetzner AX52: ~$55/month (vs $150 cap; can run for 1 month)
- Cold storage / egress: $0 (within Hetzner allowance)
- Total: **$55** (well within $150 cap)

## Wikilinks

- [[../papers/paper1_resolution_limits/main]] — Paper 1 foundation
- [[concepts/I14 funnel risk]] — Paper 1 I14 rule (Paper 2 may refine)
- [[concepts/Deep-pit low-vesselness]] — Paper 1 Cycle 1 rule (Paper 2 may add more failure modes)
- [[concepts/I12 funnel risk]] — Paper 2 NEW (multi-evidence gate)
- [[backlog/Deferred items]] — MGC3 / PU / physics screen / SLDEM2015 / I12 all here
- [[decisions/Tier-1 trigger]] — Hetzner AX52 authorized but not launched
- [[gates/G2]] — G2' PARTIAL is Paper 1's final gate; G3 will be Paper 2's

## Status

**This outline is aspirational; no work has begun on Paper 2.** The Paper 1 v1.0 release is the project's current deliverable. Paper 2 will be initiated once the 7 trigger conditions above are met (estimated 6-12 weeks out, depending on rental authorization and visual-inspection completion rate).