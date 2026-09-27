# Outreach — Target Faculty List

> **Compiled**: 2026-09-27 (lunar-orchestrator)
> **For**: European CS/AI PhD program applications (Sept 2027 intake; deadlines Dec 2026 / Jan 2027)
> **Status**: First batch (Tier 1 + Tier 2 = 10 names) ready; send within 7 days
> **Selection criteria**: Faculty meeting ≥2 of 3 — (1) methodology focus (PU learning, calibration, Bayesian ML, uncertainty quant, distribution shift, geometric DL, multi-modal/multi-scale fusion); (2) scientific-application track record; (3) openness to cross-domain candidates with novel methodological contributions.

---

## Tier 1 — High priority (send FIRST)

### 1. Emtiyaz Khan — UCL Centre for AI
- **Role**: Associate Professor (UCL); also RIKEN AIP
- **Research area**: Bayesian learning, adaptation, uncertainty. Pioneer of methods that work under distribution shift + limited supervision.
- **Why fits**: LUNARVOID's "inference with error bars under sparse supervision" maps cleanly onto Khan's Bayesian-learning agenda; the case study is novel domain.
- **Cold-email angle**: "Could a conformal wrapper around a PU-trained classifier give tiered inferences with per-tier coverage guarantees that survive physical-completeness tests, not only i.i.d. ones?"
- **Recent relevant**: "Bayesian Learning for the Next Generation" position paper; continual learning without forgetting; practical methods for adapting under shift.
- **Contact**: emtiyaz.khan_AT_ucl.ac.uk (verify current address via UCL CS directory)

### 2. Bernhard Schölkopf — MPI for Intelligent Systems / ELLIS
- **Role**: Director, MPI-IS Tübingen; co-founder ELLIS
- **Research area**: Causality, ML for science, kernel methods, representation learning
- **Why fits**: "ML for science" godfather in Europe. LUNARVOID as a case study in calibrated scientific inference fits his group's methodology-first scientific-ML agenda.
- **Cold-email angle**: "How does causality interact with the FP-per-area metric when the negative class is fundamentally unknowable?"
- **Recent relevant**: "Toward Causal Representation Learning" (IEEE TPAMI 2021); "Causality for Machine Learning" chapter series; recent work on causal discovery in scientific domains.
- **Contact**: bs_AT_is.mpg.de

### 3. Yarin Gal — Oxford Computer Science / OII
- **Role**: Professor of Machine Learning (Oxford CS); Turing Fellow OII
- **Research area**: Uncertainty quantification, Bayesian deep learning, active learning, calibration
- **Why fits**: Direct calibration match — "calibrated inference with error bars" is the moon-physics analogue of NN uncertainty calibration. His group works actively on conformal prediction.
- **Cold-email angle**: "Does conformal prediction break down on morphometric data the same way it does on out-of-distribution medical or astronomical data?"
- **Recent relevant**: "Uncertainty in Deep Learning" PhD thesis (heavily cited); Concrete Dropout series; recent conformal prediction benchmarks.
- **Contact**: yarin.gal_AT_exeter.ox.ac.uk (Oxford uses ox.ac.uk — verify; some use the @eng.ox.ac.uk alias)

### 4. Fanny Yang — ETH Zürich
- **Role**: Professor of Computer Science + Statistics (ETH Zürich)
- **Research area**: Distribution shift, calibration, algorithmic fairness, robust statistics
- **Why fits**: Calibration under distribution shift is the direct thesis match. Yang's recent work on "calibration-aware algorithms" maps onto LUNARVOID's epistemic discipline.
- **Cold-email angle**: "Could the calibration-aware training framework extend to scientific domains where ground truth is fundamentally unknowable, and where the only honest metric is FP-per-area?"
- **Recent relevant**: "Post-hoc Calibration Without Ground Truth" series; recent work on distribution-shift-aware statistical inference.
- **Contact**: fanny.yang_AT_inf.ethz.ch

### 5. Gaël Varoquaux — INRIA
- **Role**: Research Director, INRIA; head of the Parietal team (ML for neuroscience)
- **Research area**: ML for science, statistical learning, open-source research tools (scikit-learn co-founder)
- **Why fits**: Open-science + ML-for-scientific-domains lineage. LUNARVOID's open release (GitHub, Zenodo-staged) and reproducible benchmark (124 tests, byte-identical pins) align with his group's culture.
- **Cold-email angle**: "What would an open reproducible benchmark look like for a planetary case study where the entire ground truth consists of one radar detection and ~20 catalogued candidates?"
- **Recent relevant**: nilearn, scikit-learn, recent reproducibility papers; open ML-for-science position pieces.
- **Contact**: gael.varoquaux_AT_inria.fr

---

## Tier 2 — Strong fit (send with first batch)

### 6. Carl Edward Rasmussen — Cambridge Department of Engineering
- **Role**: Professor (Cambridge); also visiting MPI-IS Tübingen
- **Research area**: Gaussian processes, Bayesian inference, scientific applications
- **Why fits**: Deep GP methodology + historical scientific-application lineage. Strong methods depth for the geophysics layer.
- **Cold-email angle**: "Would Gaussian-process calibration work for morphometric signal/uncertainty under extreme class imbalance?"
- **Recent relevant**: GP textbook (with Williams); recent papers on data-efficient Bayesian learning.
- **Contact**: cer24_AT_cam.ac.uk

### 7. Samuel Kaski — Aalto University / ELLIS
- **Role**: Professor (Aalto CS); ELLIS unit director
- **Research area**: ML for science, Bayesian optimization, human-in-the-loop, simulation-based inference
- **Why fits**: ML-for-science explicitly; novel-domain case studies welcomed by his group. The simulator-based inference connection is a natural bridge from LUNARVOID's calibrated inference.
- **Cold-email angle**: "How would you design a PU-learning experiment when the unlabeled set includes both unlabeled positives AND true negatives?"
- **Recent relevant**: Simulation-based inference (sbi) papers; user modelling for experimental design.
- **Contact**: samuel.kaski_AT_aalto.fi

### 8. Devis Tuia — EPFL Valais / ETH Zürich
- **Role**: Professor of Environmental ML and Earth Observation (EPFL Valais; joint affiliation with ETH Zurich)
- **Research area**: Geospatial ML, environmental remote sensing, image classification, Earth observation
- **Why fits**: Nearest geophysical-domain overlap (Earth observation + multi-scale fusion). The label-scarcity problem in Earth observation is structurally similar to the lunar case.
- **Cold-email angle**: "Would the LUNARVOID scale-bridging fusion (60-300 m morphometry vs 60 km gravity) interest your Earth-observation fusion work?"
- **Recent relevant**: Multimodal Earth observation benchmarks; recent papers on label-efficient Earth observation.
- **Contact**: devis.tuia_AT_epfl.ch

### 9. Jonas Peters — U Copenhagen / ETH Zürich / ELLIS
- **Role**: Professor (was U Copenhagen; reportedly affiliated with ELLIS network)
- **Research area**: Causality, statistical learning theory
- **Why fits**: Causality + statistical rigor. The "we don't know what's a negative" problem relates to causal identifiability with unobserved counterfactuals.
- **Cold-email angle**: "Is there a causal framing for 'tube-or-no-tube' that handles the case where 'no tube' is unverifiable?"
- **Recent relevant**: "Elements of Causal Inference" textbook; recent papers on identifiability with unobserved variables.
- **Contact**: jonas.peters_AT_ucl.ac.uk OR jonas_peters_AT_protonmail.com (verify current institution; he has changed affiliations recently)

### 10. Bertrand Thirion — INRIA / Saclay
- **Role**: Research Director (INRIA); head of the Parietal team (with Varoquaux)
- **Research area**: Statistical learning, neuroimaging, fMRI
- **Why fits**: Statistical learning for scientific domains. Familiar with label scarcity + multi-scale data fusion. Connection to Perrochon-style "one-landmark" calibration.
- **Cold-email angle**: "How does statistical learning for neuroscience handle the case where verification is one landmark and the rest is inference?"
- **Recent relevant**: Recent fMRI prediction papers; nilearn; recent student cohort ML papers.
- **Contact**: bertrand.thirion_AT_inria.fr

---

## Tier 3 — Adjacent (follow-up batch if Tier 1+2 responses are slow)

### 11. Philipp Hennig — U Tübingen / MPI-IS
- **Role**: Professor (Tübingen); MPI-IS dept. head
- **Research area**: Probabilistic numerics, Bayesian deep learning, uncertainty quantification
- **Why fits**: Probabilistic methods + uncertainty quantification in scientific computation.
- **Recent relevant**: Probabilistic-numerics framework; recent papers on stable Gaussian processes.
- **Contact**: philipp.hennig_AT_mpi-sws.org OR verify current

### 12. Marc Pollefeys — ETH Zürich / Microsoft
- **Role**: Professor (ETH CS); Microsoft Mixed Reality & AI lab (joint)
- **Research area**: Computer vision, 3D reconstruction, SLAM, neural rendering
- **Why fits**: The LUNARVOID Portal uses R3F for a 3D lunar globe + tube cutaway. Connection to vision researchers valuable for portfolio (and the project's 3D-viz is portfolio-quality).
- **Cold-email angle**: "Could the 3D-globe + cutaway visualisation in the LUNARVOID Portal tie in with 3D-vision work on dynamic scenes under sparse observations?"
- **Recent relevant**: Nerfstudio; 3D Gaussian splatting; recent SLAM papers.
- **Contact**: marc.pollefeys_AT_inf.ethz.ch

---

## Notes on what NOT to do

- **Don't skip Tier 1** — sending only to Tier 2-3 wastes the strongest opportunities.
- **Don't send all 10 in one batch with no spacing** — staggering across 5-7 days lets you adjust based on early responses.
- **Don't mass-send identical templates** — the [SPECIFIC PAPER] / [SPECIFIC METHODOLOGY] anchor in Template 1 makes each email read as 1:1, even when common scaffolded.
- **Don't over-pitch** — lead with the question, not the project. "Would X work?" reads better than "I built X and you should care."
