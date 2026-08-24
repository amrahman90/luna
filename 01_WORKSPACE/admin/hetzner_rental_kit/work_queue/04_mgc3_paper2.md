# Work Queue 04 — Mars Cushing 2015/2017 Cross-Body Pretraining

**Priority:** 5 (lowest; deferred from P5.3 at G1)
**Wall time:** ~6 hours (CPU-feasible feature-based first pass; DL
pretraining is optional, separate trigger)
**Cost:** $0 (Mars Cushing data is public; no egress)
**Pre-req:** work-queue #1 + #3 complete; N=51 candidate registry.

## Task

Implement the MGC3 cross-body pretraining from Cushing 2015 (Mars
tubes) and Cushing 2017 (Moon tubes comparative review) for Paper 2's
Mars→Moon transfer argument.

This is the **deferred P5.3 task** (`plans/2026-08-21_Next_Tasks_Roadmap.md`):
"PU-learning + conformal (Task 21.2); the v5 base-rate framing needs
calibrated posterior probabilities, which is the next deliverable once
the LLTB-1 v0.4 numbers are pinned." Now that we have N=51 candidates
and the v0.5 ladder ceiling, the MGC3 cross-body feature engineering
is feasible.

## Why MGC3 specifically

Cushing 2015 identified ~1000 candidate Martian tube skylights from
THEMIS imagery; the MGC3 (Mars Global Cave Catalog) is the analogous
Mars-side dataset. The features that distinguish Martian tubes from
non-tubes (rim sharpness, shadow persistence, depth-to-diameter ratio)
   can be cross-body pretrained on Mars and fine-tuned on the Moon.

## Steps

1. SSH to the Hetzner server.
2. Download the MGC3 catalog from the USGS Astrogeology node (public;
   SHA-256 + licence logged in `data/MANIFEST.md`).
3. For each MGC3 candidate, compute the equivalent features:
   - rim_sharpness (gradient at the rim cells)
   - shadow_persistence (max shadow length over illumination angles)
   - depth_to_diameter_ratio (recovered depth / inferred diameter)
4. Train a CPU logistic regression with class-weight balancing on
   MGC3 (P=U=~500 each after the I9 protocol).
5. Apply the MGC3-trained classifier to the LUNARVOID N=51 candidates;
   report the per-candidate cross-body probability.
6. Compare the cross-body probabilities to the per-DTM PU-learning
   posterior from `code/wp5_fusion/pu_learning_baseline.py`.

## Success criteria

- MGC3 features extracted for 1000+ Martian candidates.
- Logistic regression AUC on MGC3 holdout > 0.7 (the published
  Cushing 2015 baseline).
- Cross-body transfer AUC on LUNARVOID candidates > 0.6 (above
  chance; cross-body).
- Note saved at `01_WORKSPACE/notes/<date>_mgc3_cross_body.md`
  summarising the cross-body transfer quality.

## Output paths

- MGC3 features: `01_WORKSPACE/data/outputs/wp5_fusion/mgc3_features.csv`
- Trained model: `01_WORKSPACE/data/outputs/wp5_fusion/mgc3_logreg.joblib`
- Cross-body probabilities:
  `01_WORKSPACE/data/outputs/wp5_fusion/cross_body_probs.csv`
- Note: `01_WORKSPACE/notes/<date>_mgc3_cross_body.md`
- Paper 2 section draft: `01_WORKSPACE/papers/paper2/mgc3_section.md`

## Rollback

If MGC3 cross-body AUC < 0.6 (i.e., worse than chance), the result
is a documented negative — the cross-body features don't transfer
from Mars to Moon. Paper 2's MGC3 section becomes a discussion-only
item, not a positive result. No automatic rollback.

## Cost

$0 (MGC3 catalog is public; THEMIS data is small).

## Verification

The smoke test gains a MGC3 cross-body AUC check: it must remain
> 0.6 (cross-body sanity). A regression below 0.6 means the MGC3
features have drifted from the published Cushing baseline.

## Strategic value

This is the **only** work-queue item that is *primarily* for Paper 2
rather than Paper 1 / the G3 gate. It is here because the $150
ceiling has $30-50 of slack after #1-#3 (depending on #1's egress)
and MGC3 is the highest-leverage Paper 2 deliverable per `plans/2026-08-23_Paper2_outline_sketch.md`.
