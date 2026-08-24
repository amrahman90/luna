# Cover Letter — Paper 1 submission to *Remote Sensing of Environment*

**Date:** 2026-08-24
**To:** The Editor, *Remote Sensing of Environment*
**From:** LUNARVOID team — corresponding author: [corresponding.author@lunarvoid.org](mailto:corresponding.author@lunarvoid.org)
**Manuscript title:** "Detectability limits for lava tube roof signatures in orbital topography: the LLTB-1 calibrated benchmark"
**Manuscript type:** Original research article (benchmark paper)
**Word count (approx.):** ~6,800 (main text, excluding references and figure captions)

---

Dear Editor,

Please find enclosed our manuscript *"Detectability limits for lava tube roof signatures in orbital topography: the LLTB-1 calibrated benchmark"* for consideration as an original research article in *Remote Sensing of Environment*. The work introduces the LUNARVOID Terrestrial Benchmark v0.1 (LLTB-1), a six-site calibrated analog benchmark that characterises how a depth × Frangi-vesselness roof-sag detector degrades when surveyed terrestrial point clouds are downsampled, shadow-rendered, and sensor-blurred to LROC NAC observing conditions, and reports first-of-their-kind per-rung F1/P/R curves and FP-cell densities (predict-all tile extrapolation, not a survey rate) for the LROC NAC ground-sample-distance band.

The closest direct competitor is Le Corre et al. (2025, *Icarus* 441, 115548 — the ESSA Mask R-CNN detector), which reports ~89–96% F1 against Lunar Pit Atlas labels on NAC imagery alone. We position our contribution against ESSA on three substantive grounds: (i) ESSA's F1 figures are *detection* scores against the same catalogued pit set used in training, with no per-claim P(void) and no FP-per-area reporting — we report calibrated *inference* probabilities under the v5 claim-discipline framework and explicitly flag lunar FP per 10⁴ km² as **NOT MEASURED** until a survey-grade DTM population is processed; (ii) ESSA is a 2D-imagery detector, whereas LLTB-1 is a 3D morphometric benchmark that exercises a depression-depth × Frangi-vesselness chain with published physical-scale selection (the 30–300 m Blair / Theinat / Chwala lunar tube-width band) and a Planchon-Darboux epsilon fill chosen to recover shadowed pit floors; and (iii) we hold out 50% of analog sites for per-rung threshold re-tuning (a protocol ESSA does not require) and report the analog-scope caveat of our Hapke + sensor degradation arms (labels are trench-hosted; roofed-sag-on-open-mare is untested). We cite ESSA early and use its shapefiles only as a comparison set, never as labels. The one *instrumented* subsurface structure on the Moon evidenced by any instrument to date remains the Tranquillitatis radar conduit (Carrer et al. 2024, *Nature Astronomy*); every lunar result in our 278-row tier-C registry is **calibrated inference**, never verified detection.

The manuscript fits *RSE*'s scope on three counts: (i) it is fundamentally a *remote-sensing methodology* paper, framing camera and altimeter requirements for future missions seeking intact lunar lava tube roofs (§5.1); (ii) the degradation protocol — Hapke IMSA re-rendering at NAC illumination geometries composed with a NAC-like sensor stage (nan-aware Gaussian PSF; σ_z calibrated so SNR=100 @ 2 m ⇒ 0.33 m, anchored to TRANQPIT1) — is a planetary application of remote-sensing radiative-transfer and sensor modelling, with all 10 figures being remote-sensing figures (Hapke illumination grid; sensor-stage preview; kriging residuals ×2; pit depth recovery; noise-floor panels; scope map ×2; analog registration validation); and (iii) the calibration-context FP framing (3.74 [Poisson-exact 95% CI 1.71, 7.10] per 10⁴ km² over 24,062.96 km², *not* a survey rate) is a methodological contribution to honest base-rate reporting where ~20 tube-relevant lunar pits sit in a population of ~281 catalogued pits. Should the manuscript fall outside *RSE*'s scope, we would welcome transfer to *ISPRS Journal of Photogrammetry and Remote Sensing*.

**Declarations.** The authors declare no competing interests. The LLTB-1 derived rasters, code, and candidate registry are released openly at the LUNARVOID repository; the NASA Planetary Pits and Caves analog dataset (Wong 2014) is acknowledged as research/academic use only and is not redistributed (fetch scripts and licence gate in Data and Code Availability); LROC NAC DTMs are PDS public domain, fetched by product ID rather than mirrored; ISRO acknowledgement is not required (no Chandrayaan data used); LU5M812TGT craters were not used in this manuscript. All ten References are author-year, alphabetically sorted, and will be Zotero-attached at acceptance. The manuscript has not been published elsewhere and is not under consideration at another journal. CRediT author contributions and a single-author note are provided.

We thank you for your consideration and look forward to your response.

Sincerely,

**LUNARVOID team**
Corresponding author: [corresponding.author@lunarvoid.org](mailto:corresponding.author@lunarvoid.org)
Repository: [https://github.com/LUNARVOID/lunarvoid](https://github.com/LUNARVOID/lunarvoid) (open; derived artifacts mirrored under `01_WORKSPACE/data/outputs/`)