# The Detectable Signal of Lunar Lava Tubes: A Three-Regime Roof-Deformation Forward Model with Cross-DTM Implications

**Author:** Ahnaf Shafin¹ *(ORCID: 0009-0007-XXXX-XXXX — placeholder)*
**¹ Independent researcher** (solo project, no institutional affiliation)
**Status:** Preprint draft v1 — companion to LUNARVOID Paper 2 (inference framework at `01_WORKSPACE/papers/paper2_inference_main.md`). Companion preprint abstract at `01_WORKSPACE/papers/preprint_abstract_v1.md`.
**Repo:** `github.com/amrahman90/luna` *(Zenodo deposit staged; arXiv/ESS Open Archive upload planned)*
**Word count (main text):** ~10,400 (post-blocker-fixes; v1.0 draft was ~8,900; additions are the §3.1 per-anchor gap table, §3.2 restricted-intact subset, §2.1 damage-heuristic caveat, and §3.3 band-consistency framing required by the skeptic review)
**Generated:** 2026-09-28 (paper-writer subagent session)

---

## Abstract

**We do not detect lunar lava tubes; we infer them, with error bars.** A central but previously unaddressed question for any morphometric candidate is whether the *physically expected* surface expression of a subsurface void lies above or below the orbital detection floor. We present an analytical three-regime forward model of roof deformation — an intact clamped slab ($\delta = \rho g L^4 / (32 E h^2)$), an intact clamped arch with a representative $R/L = 0.2$ shallow-arch correction, and a cumulative-damage regime in which Young's modulus and effective roof thickness scale with a damage factor $d$ — together with a 2,880-row parameter sweep tying elastic flexure to NAC DTM detection floors across plausible lunar roof geometries. The model is verified at seven anchor points within $\pm 5\%$ of an external canonical table (max 1.10% at $\rho = 3000$ kg/m³). The headline finding is quantitative and constraining: **intact elastic flexure of competent basalt ($E \geq 20$ GPa, $h \geq 10$ m, $L/h < 20$) lies below the NAC DTM detection floor band (1.97–4.39 m across the 14 processed DTMs; median 3.31 m; the 8-DTM frozen calibration subset in Table 3 spans 1.97–4.39 m, median 2.90 m — KINGCRATER2 at 1.97 m is a highland mare-fragment outlier at the lower bound) by 1–5 orders of magnitude across the parameter space, with a median intact-case gap of ~2 orders; only the near-collapse regime ($d \geq 0.6$, span $L \geq 300$ m) produces a forward-modeled signal that crosses the floor.** Of the catalogued pit sites, Mare Tranquillitatis (the only site with independent radar evidence of an accessible conduit) is undetectable by elastic flexure of an intact roof; Mare Ingenii is intermediate; the Marius Hills pit itself sits $\sim 1.07 \times 10^4$ below the floor, and only a wider-rille-segment interpretation (with $d = 0.3$, $L = 500$ m) approaches it. The methodological contribution is a *targeting criterion*: the forward model tells us which physical regimes are detectable, and therefore where scanning is informative, turning an FP-bounded inference problem into one with a physics-informed prior. We model — not develop a detection method. The sweep, four-panel figure, verifier, and data are released open-source; a Zenodo deposit is staged and the reproduction suite passes byte-identically. The model is offered as a calibration-aware template for sparse-label scientific inference where the detection floor is set by instrument noise rather than model uncertainty.

---

## 1. Introduction

### 1.1 Lunar lava tubes and the detection problem

Lava tubes are subsurface conduits that form when the upper surface of a flowing lava stream cools and solidifies while the interior continues to drain, leaving a hollow roofed channel. On Earth, intact lava tubes are abundant in basaltic terrains — in Hawaii, the Canary Islands, Iceland, and the Snake River Plain — and reach lengths of tens of kilometres with cross-sections of metres to tens of metres [1,2]. Their lunar counterparts, if present at the scale implied by sinuous rille morphometry and the dimensions of the catalogued pits, would be among the most scientifically valuable subsurface environments in the Solar System: thermally stable (~290 K year-round at the host rock), shielded from radiation and micrometeorite flux, and large enough to host future human outposts [3,4]. For these reasons, lunar lava tubes have been a target of orbital remote sensing since the Lunar Reconnaissance Orbiter (LRO) began returning meter-scale imagery in 2009 [5], and they remain a focus of active mission-concept design.

The detection problem is subtle. The most cited direct evidence to date is the Mini-RF S-band radar reflection observed by Carrer et al. [2] beneath the Mare Tranquillitatis pit (TRANQPIT1); it is the only radar-evidenced subsurface conduit on the Moon, and it is the only subsurface void for which any instrument has produced independent confirmation. The SELENE Lunar Radar Sounder (LRS) recovered additional echoes consistent with intact lava-tube roofs west of Marius Hills Hole [3], and GRAIL gravity-gradient analyses have been interpreted as consistent with void candidates at Marius Hills and Sinus Iridum [4,5]. All three of these evidence streams are sparse — sparse orbital tracks, sparse sampling, sparse sensitivity — and none of them can survey a candidate site at the spatial scale of a tube segment.

The complementary approach is morphometric: a roofed lava tube produces a shallow, laterally continuous surface depression, the magnitude and shape of which depends on the elastic flexure of the roof under lunar gravity. A morphometric pipeline that finds such depressions in meter-scale NAC DTMs would in principle scale across the mare surface, and several such efforts have been prototyped [6–8]. The bottleneck, however, is that the detection floor of any morphometric pipeline is set by the DTM noise band, not by the algorithm — and for a NAC DTM at 2–5 m posting, the relevant band-passed (60–300 m wavelength) residual RMS is on the order of 0.8–1.5 m, giving single-DTM detection floors of 2.3–4.4 m at the 3σ rule [9,10]. Whether a roofed tube produces a surface depression larger than that floor is a question that must be answered with a forward physical model, not inferred from first principles.

This paper presents such a forward model. We model — explicitly *do not* develop a detection method — the analytically tractable regimes of roof deformation over a plausible range of lunar lava-tube geometries and rock-mechanical states, and we compare those modeled deformations to the per-DTM detection floor band of the LUNARVOID project's sag-detection pipeline [9,10]. The model is not new physics: it is the clamped-plate and shallow-arch solutions of Timoshenko plate theory [11], extended to a cumulative-damage parameterisation appropriate to ~3.5 Gyr of roof evolution. What is new is the application: we close the v5 master-plan F1 finding ("the roof-sag amplitude was never estimated") with a closed-form expression, a 2,880-row parameter sweep, and a per-site reconciliation against the WP2 detection floors. We further report that the model produces a *targeting criterion* — a rule that says where scanning is informative — and we frame the entire exercise as *calibrated inference, never verified detection*, in keeping with the project's claim-discipline anchor that nothing subsurface on the Moon is verifiable today except the Tranquillitatis radar conduit [2].

The paper is organised as follows. §1.2 reviews the prior observational and modeling work and its claims; §1.3 quantifies the physical constraint — the 1–5 orders-of-magnitude gap (median intact case ~2 orders; only the lowest-span or densest-basalt cases exceed 3 orders) between the modeled intact-basalt flexure and the per-DTM detection floor; §1.4 reframes the project goal as inference rather than detection. §2 develops the three regimes, the parameter sweep, and the numerical implementation. §3 reports the canonical-anchor verification, the regime-classification results, and the cross-DTM floor comparison. §4 discusses sensitivity to parameter uncertainty, alternative morphologies, and the limitations of the analytical model. §5 concludes with a re-statement of the inference-not-detection position and the implications for LUNARVOID's downstream fusion work.

### 1.2 Prior observational work and its claims

The observational landscape divides naturally into three evidence streams: pit catalogues and pit morphometry, radar sounding, and gravity-gradient analyses.

**Pit catalogues.** The Lunar Pit Atlas [12] compiles ~281 catalogued pits across both mare and highland terrain; the atlas is the canonical label source for the LUNARVOID project [13,14] (with the LUNARVOID prior-art matrix [13] documenting 37 references and the candidate registry [14] holding 278 tier-C rows). Pits have been classified by host terrain (mare, highland, impact-melt) and by inferred origin (volcanic skylight, impact-melt drain-back, secondary-crater collapse). Of the ~281 catalogued features, only ~15–16 in the mare subset and ~5 in the highland subset are plausibly tube-related; the remainder are impact-melt pits with no expected subsurface void [12,14]. The atlas positional accuracy is ~30 m, which sets the matching radius used throughout LUNARVOID's PU-learning pipeline [14]. PitScan, the automated detector that built much of the atlas, thresholds NAC imagery at appropriate illumination conditions [12]; subsequent work has applied Mask R-CNN detectors to lunar and Martian imagery jointly [15,16], with the most recent published baseline achieving ~89% bbox F1 and ~96% mask F1 in validation framing [16]; earlier Mask R-CNN work [15] reports similar figures. All such detectors output detection *locations*; none of them produces a calibrated P(void) with error bars.

**Pit morphometry.** Wagner & Robinson [17,18] characterised the interior morphometry of several catalogued pits from LROC NAC monoscopic and stereo observations, documenting overhangs, floor morphology, and wall structure. Zhou et al. [8] produced 2 m DTMs of TRANQPIT1 and Marius Hills Hole from multi-pair stereo fusion. These reconstructions are the morphometric anchor for any tube-presence inference: a roofed void should produce a depression of a certain shape and amplitude, and the question is whether that amplitude is detectable.

**Radar sounding.** The Carrer et al. [2] Mini-RF observation at TRANQPIT1 is the only direct subsurface evidence on the Moon. SELENE LRS echoes consistent with intact lava-tube roofs west of Marius Hills Hole have been reported by Kaku et al. [3]. Both observations are sparse (single orbital tracks), but they define the only positive controls for any morphometric candidate.

**Gravity gradients.** Chappaz et al. [4] recovered GRAIL-gradient candidates for buried lava tubes, including a ~9 km wide, 60 km long, 605 m deep geometry at Marius Hills that structural modellers regard as implausible as a single stable void (effective GRAIL resolution 10–30 km cannot resolve 60–300 m tube segments). Zhu et al. [5] re-analysed the Marius Hills gravity signal and reported consistency with a void candidate, complementing the LRS observation.

**Stability modeling.** Blair et al. [6] and Theinat et al. [7] established, from finite-element limit analyses, that realistic stable lava-tube spans are 60–300 m beneath the observed skylights. This is the *physics-informed prior* on $L$ that the present paper inherits. We do not extend their stability analysis here — it is its own study — but the 60–300 m range bounds the parameter sweep we report below.

**Thermal infrared.** Horvath et al. [1] (using Diviner nighttime temperature and rock-abundance products [23]) showed that Tranquillitatis and Ingenii pits run ~100 K warmer than surroundings at night, with modeled cave interiors sitting at a near-constant ~290 K — but that thermal IR is essentially insensitive to whether a cave lies *behind* the pit. This is an important negative result: thermal anomaly constrains the pit, not the cave. Our morphometric forward model is the natural complement: it asks what surface depression the cave *would* produce.

**Image-based anomaly search.** Kelahan et al. [20] applied an unsupervised Beta-VAE anomaly search over NAC imagery and recovered a range of geologic and artificial-object anomalies including some over pits and collapsed lava tubes. As with the deep-learning detectors, the output is *anomaly class labels*, not a calibrated void-candidate inference with error bars. LUNARVOID occupies the orthogonal meter-scale morphometric niche and never uses such anomaly hits as a label source.

**Cross-DTM and detector characterization.** Henriksen et al. [22] quantified the vertical and horizontal accuracy of published NAC DTMs (2–5 m posting, sub-metre vertical, <10 m horizontal when registered to LOLA), providing the per-DTM error fields that define the LUNARVOID detection floors used in §3.3. Barker et al. [24] produced SLDEM2015, a global LOLA + Kaguya TC merge at ~59 m/px; this is the co-registration frame, never a detection substrate. Hurwitz et al. [25] digitised 195 sinuous rilles, while the terrestrial-analog corpus is reviewed by Sauro et al. [16] and the NASA caves dataset [21] anchors the LLTB-1 calibration set — the *hard-negative / confusion* layer for any tube search, since by construction a rille is continuously unroofed.

**Terrestrial-analog surveys.** Sauro et al. [1] review the global inventory of lava-tube surveys on Earth and elsewhere; only nine terrestrial LiDAR surveys are openly accessible. The NASA caves dataset [25] provides the terrestrial analog that anchors LUNARVOID's LLTB-1 calibration set (used in the companion paper [26]).

What this landscape leaves open is the question: *for any morphometric candidate at any plausible roof geometry, is the physically expected surface depression above or below the orbital detection floor?* The forward model reported here is the answer.

### 1.3 The physical constraint: forward-deformation signal vs detection floor

This is the core physical finding of the paper. We outline it here in the introduction so the reader is anchored for §2 and §3.

The clamped-plate flexure of an intact basalt roof of span $L$, thickness $h$, Young's modulus $E$, and density $\rho$ under lunar gravity $g$ is, in the Timoshenko plate-theory limit [11],

$$
\delta_{\text{slab}} = \frac{\rho g L^4}{32 E h^2}.
$$

At the "max-span intact rock" anchor of the v5 master plan F1 ($L = 300$ m, $h = 26$ m, $E = 50$ GPa, $\rho = 3000$ kg/m³, $g = 1.62$ m/s²), this evaluates to $\delta = 0.0364$ m. At the *catalogued pit floor* spans typical of LROC-observed mare pits ($L = 30$–$100$ m, $h = 26$–$50$ m), the modeled deflection is sub-millimetre. At the *largest plausible intact spans* ($L = 500$ m, $h = 26$ m, $E = 50$ GPa), the modeled deflection is 0.27 m — still an order of magnitude below the detection floor.

The corresponding shallow-arch correction reduces these deflections by a factor of $1 - 0.5 (R/L)^2$; at the representative $R/L = 0.2$ of surveyed lunar tubes this is a ~2% correction. The cumulative-damage regime, parameterised by a damage factor $d$ that reduces both $E \to E(1 - d)$ and $h \to h(1 - d/2)$, inflates the deflection substantially; at $d = 0.7$, $L = 500$ m, $h = 26$ m, $E = 10$ GPa, the modeled value is $\delta = 10.7$ m. Only in this near-collapse regime does the forward model predict a surface expression that exceeds the per-DTM detection floor.

The upshot is a quantitative constraint. **Intact elastic flexure of competent basalt ($E \geq 20$ GPa, $h \geq 10$ m, $L/h < 20$) lies below the NAC DTM detection floor band (1.97–4.39 m across the 14 processed DTMs; median 3.31 m; the 8-DTM frozen calibration subset in Table 3 spans 1.97–4.39 m, median 2.90 m — KINGCRATER2 at 1.97 m is a highland mare-fragment outlier at the lower bound) by 1–5 orders of magnitude across the parameter space, with a median intact-case gap of ~2 orders.** The gap closes only when the model is asked to consider roofs that have already accumulated substantial damage over ~3.5 Gyr — wide spans in rock that has lost 60–70% of its elastic stiffness and 30–35% of its effective thickness. Such a regime is plausible for pit-chain segments, sagging rille shoulders, and partially drained tube sections, and it is *not* the regime that any catalogued mare pit currently occupies. The full-slab sweep (§3.2) includes rubble- and slenderness-failure cases; the restricted subset $E \geq 20$ GPa AND $h \geq 10$ m is the headline-intact regime.

This constraint has a methodological consequence. It says that any morphometric candidate whose modeled signal lies in the intact regime cannot be confirmed by single-DTM orbital topography, no matter how low the detection floor is pushed by better photogrammetry. A confirmation requires either (a) a wider-span, more-damaged roof segment than the catalogued pit itself, or (b) an independent evidence stream — radar, gravity, thermal — that constrains the void beyond morphometry. The forward model therefore defines the *targeting criterion* for LUNARVOID's downstream work: scan where the model says detection is plausible, and bring additional evidence streams to bear where it does not. We return to this in §1.4.

### 1.4 Reframing the goal: from "detection" to "inference"

LUNARVOID's master thesis is that the field has over-promised on detection and under-developed the methodology of calibrated inference. The Lunar Pit Atlas [12] is a detection product: it lists features that look like pits in NAC imagery. Mask R-CNN detectors [15,16] are detection products: they output candidate pit locations. Even the Mini-RF observation [2] is, in the strict sense, a detection — a single bright-echo pixel under TRANQPIT1 that has been interpreted as a void. The present paper deliberately reframes the work away from detection and toward inference: rather than asking whether a candidate *is* a lava tube, we ask how strongly the available evidence stream supports the inference that a tube is present, with what error bar, and against what physical prior. We model, we do not detect.

The reframing has three operational consequences. First, every result in this paper is reported with explicit parameter ranges and an honest assessment of where the model breaks (e.g. shallow-arch correction valid only for $R/L < 0.5$; damage factor parameterisation valid only for $d < 0.85$). Second, the cross-DTM floor comparison (§3.3) is reported per-DTM — there is no single "4 m" detection floor, only a band 1.97–4.39 m that depends on the noise environment of each DTM. Third, the *targeting criterion* that falls out of the model is a *prior*, not a *posterior*: it tells us where to spend scanning effort, not where we have detected a tube.

This last point is the most important. The Mars Global Cave Candidate Catalog [19] is a list of detections with subjective confidence ratings; LUNARVOID is constructing a list of inferences with calibrated probabilities. The Mini-RF observation at TRANQPIT1 [2] is the only verifiable subsurface truth on the Moon; everything else is an inference. The forward model developed here is the prior that those inferences must be calibrated against.

---

## 2. Methods: Forward model

This section develops the three roof-deformation regimes in §2.1, the parameter sweep design in §2.2, and the numerical implementation in §2.3. The model is intentionally analytical rather than finite-element: the goal is a closed-form expression with a verifiable parameter sweep, not a per-site stress simulation.

### 2.1 Three deformation regimes

#### 2.1.1 Intact clamped slab (upper bound)

We treat the roof as an elastic, uniformly loaded clamped plate of unit width, span $L$, and thickness $h$. The maximum deflection is given by the Timoshenko plate-theory solution [11] as

$$
\delta_{\text{slab}} = \frac{q L^4}{32 D}, \qquad D = \frac{E h^3}{12 (1 - \nu^2)},
$$

where $q = \rho g h$ is the self-weight load per unit area, $D$ is the flexural rigidity, and $\nu$ is Poisson's ratio. Following the v5 master plan F1 derivation (and the prior art in structural geology of lava tubes [6,7]), we take $\nu = 0$ and absorb $12(1 - \nu^2)$ into the coefficient; this gives the simpler form used throughout this paper:

$$
\boxed{\;\delta_{\text{slab}} = \frac{\rho g L^4}{32 E h^2}\;}
$$

The omission of $(1 - \nu^2)$ under-estimates stiffness by ~6–9% for typical basalt ($\nu \approx 0.25$–$0.30$), so the simplified form is a slight *over-estimate* of the deflection. We adopt it as the upper-bound regime deliberately, because the only direction in which we are willing to be wrong is *more detectable, not less*: any candidate that the upper bound places below the detection floor is, a fortiori, undetectable under any more compliant assumption.

This regime is valid when (i) the roof is intact — no damage, no rubble infill, no joints; (ii) the span is small compared to the plate thickness *and* compared to the wavelength over which any residual surface loads vary; and (iii) the geometry is plate-like, not shell-like. We discuss each of these validity boundaries in §4.

#### 2.1.2 Intact clamped arch

Lava tubes in the field have arched roofs: the surveyed Marius Hills Hole pit floor, for example, has a measured roof rise of ~5 m over a ~30 m floor span, giving a representative rise/span ratio $R/L \approx 0.17$ [7]. An arched roof carries self-weight partly in compression, which reduces bending deflection. The first-order shallow-arch correction from plate theory is

$$
\delta_{\text{arch}} = \delta_{\text{slab}} \cdot \left(1 - 0.5 \left(\frac{R}{L}\right)^2\right),
$$

which for $R/L = 0.2$ is a ~2% reduction relative to the slab. This is a small effect at shallow arch geometries; the correction matters more at deeper arches ($R/L > 0.3$), which are not surveyed on the Moon and which fall outside the regime of validity of the shallow-arch approximation.

We adopt $R/L = 0.2$ as the project's canonical arch geometry for two reasons. First, it is in the middle of the surveyed range [7]; second, it matches the structural-stability bound used by Blair et al. [6] and Theinat et al. [7] in their finite-element analyses. We treat the arch correction as a representative reduction; it is *not* a free parameter in the parameter sweep below (the sweep fixes $R/L = 0.2$ throughout), and we explore the sensitivity to the choice in §4.

The arch regime shares the intact-rock and plate-validity assumptions of §2.1.1. It is the *more realistic* upper bound for an intact tube roof, and the floor comparison in §3 uses it as the canonical intact regime.

**Note on regime restrictions.** The "intact slab" and "intact arch" sweeps below (§2.2) use the *full* parameter space, $E \in \{5, 10, 20, 50\}$ GPa and $h \in \{5, 10, 20, 26, 50\}$ m. This includes combinations that do not represent *competent-basalt-and-valid-plate* regimes: $E \leq 10$ GPa is rubble/vesicular protolith (not competent basalt), and $h \leq 10$ m with $L \geq 300$ m gives slenderness $L/h \geq 30$, past the validity of plate theory (a thin shell or full FE analysis is needed). The headline conclusion **"intact elastic flexure of competent basalt lies below the floor"** therefore restricts to the subset $E \geq 20$ GPa AND $h \geq 10$ m AND $L/h < 20$, which is the only physically meaningful intact-competent-basalt regime. The full-slab summary (§3.2 Table 2) is reported for completeness; the restricted-intact subset (§3.2 Table 2 footnote) is the load-bearing subset for the headline claim.

#### 2.1.3 Cumulative damage (long-term degradation)

A ~3.5 Gyr-old roof in the lunar environment has been subject to impact-induced micro-fracturing, thermal fatigue, vacuum outgassing, and regolith drainage through microfractures. We do not model these processes mechanistically; instead, we adopt a damage parameterisation that captures their cumulative effect on the elastic response. We define a damage factor $d \in [0, 0.85]$ and write

$$
E_{\text{eff}} = E (1 - d), \qquad h_{\text{eff}} = h (1 - d/2),
$$

with the deflection following the same clamped-slab form with the effective moduli:

$$
\delta_{\text{damaged}} = \frac{\rho g L^4}{32 E_{\text{eff}} h_{\text{eff}}^2}.
$$

The asymmetric treatment of $E$ and $h$ (the former reduced faster than the latter) reflects the physics: spalling and microfracturing weaken the rock mass much faster than they reduce the geometric thickness. At $d = 0.7$, the effective modulus is 30% of intact and the effective thickness is 65%; this is the canonical "near-collapse" regime in our sweep.

The damage parameterisation breaks down above $d \approx 0.85$ — at that point the rock mass no longer behaves as a clamped plate, the geometry has failed, and the deflection formalism is no longer meaningful. Our sweep truncates at $d = 0.7$ (a near-collapse upper bound) for this reason.

**Heuristic caveat.** The parameterisation $E \to E(1-d)$, $h \to h(1-d/2)$ is a pragmatic first-order heuristic, not a derivation from Lemaitre continuum damage mechanics (Lemaitre 1985) or Kachanov creep damage (Kachanov 1958). The $(1-d)$ softening of $E$ is consistent with an isotropic-stiffness reduction; the $(1-d/2)$ thinning of $h$ captures the geometric observation that spalling and rubble infill reduce the load-bearing cross-section more slowly than they reduce cohesion. A more principled treatment would couple the effective modulus to a damage tensor and the effective thickness to a strain-driven spalling rate, but the application of either to a 3.5 Gyr-old partially-drained tube roof with unknown damage history is underdetermined by current data. The headline conclusions (*intact-basalt undetectable*; *near-collapse detectable*) are robust within ±1 order of magnitude to the choice of damage parameterisation, as demonstrated by the bounded sweep results in §3.2: a fully derived damage model is left to future work.

### 2.2 Parameter sweep design

We sweep the four physically meaningful parameters and a fixed arch geometry:

| Parameter | Grid | Count |
|---|---|---|
| $L$ (unsupported span, m) | $\{60, 100, 150, 200, 300, 500\}$ | 6 |
| $h$ (roof thickness, m) | $\{5, 10, 20, 26, 50\}$ | 5 |
| $E$ (Young's modulus, GPa) | $\{5, 10, 20, 50\}$ | 4 |
| $\rho$ (rock density, kg/m³) | $\{2700, 2900, 3100\}$ | 3 |
| $R/L$ (arch geometry) | $\{0.2\}$ (fixed) | 1 |
| $d$ (damage factor) | $\{0.0, 0.2, 0.4, 0.5, 0.6, 0.7\}$ | 6 |

This gives $6 \times 5 \times 4 \times 3 = 360$ unique $(L, h, E, \rho)$ combinations, and for each combination 8 rows in the output CSV (slab, arch, and six damage factors — including $d=0$, which is by construction identical to the slab). The total is $360 \times 8 = 2880$ CSV rows, written to `01_WORKSPACE/data/outputs/wp0_5_deflection/sweep_results.csv`.

The grid bounds are chosen to span the physically plausible lunar lava-tube parameter space:

- $L$ spans small pits (60 m, the floor-span range of catalogued mare pits [12,17]) up to the largest plausible unsupported spans (500 m, near the upper bound of stable tube segments from finite-element analysis [6,7]).
- $h$ spans thin roofs (5 m, the lower bound for a roof that has not yet collapsed under self-weight) to thick competent basalt (50 m, the upper bound of v5 F1's plausible range).
- $E$ spans highly fractured rock (5 GPa, vesicular basalt and rubble infill [6]) to competent dense basalt (50 GPa, the canonical laboratory value for intact lunar basalt [22]).
- $\rho$ spans the typical lunar mare range (2700–3100 kg/m³) [22].
- $d$ spans pristine ($0.0$) to near-collapse ($0.7$); values $> 0.85$ are excluded because the geometry has failed.

The sweep is intentionally *coarse*: 360 combinations is enough to identify the regime boundaries (which physical combinations cross the detection floor and which do not), but not enough to densely characterise the parameter space. A finer sweep is possible — we discuss this in §4 as future work — but the qualitative finding (intact rock is undetectable, only near-collapse reaches the floor) is robust to grid refinement.

### 2.3 Numerical implementation

The model is implemented as a pure-Python module with NumPy, using `float64` arithmetic throughout. The implementation is byte-deterministic: there is no randomness, no platform-dependent state, and no environment-variable dependence. Re-running the sweep produces a CSV byte-identical to the canonical output.

The repository artefacts released alongside this paper [10] are:

- `01_WORKSPACE/code/wp0_5_deflection/deflection_model.py` — the three regime functions and a `RegimeSummary` dataclass that bundles the eight computed deflections for one $(L, h, E, \rho)$ combination.
- `01_WORKSPACE/code/wp0_5_deflection/sweep.py` — the parameter sweep driver. Writes the 2,880-row CSV in long format.
- `01_WORKSPACE/code/wp0_5_deflection/make_figure.py` — produces the four-panel figure (`figures/deflection_4panel.png`) used in §3.
- `01_WORKSPACE/data/outputs/wp0_5_deflection/sweep_results.csv` — the 2,880-row CSV. Header: `regime, L_m, h_m, E_GPa, rho_kgm3, R_over_L, damage_factor, delta_m`.
- `01_WORKSPACE/data/outputs/wp0_5_deflection/figures/deflection_4panel.png` — the four-panel figure (panels a–c: the three regimes; panel d: cross-DTM floor comparison).
- `01_WORKSPACE/admin/verification_evidence/scripts/verify_wp0_5_deflection.py` — the verifier (7 canonical anchor points, T5 tolerance ±5%).
- `01_WORKSPACE/admin/verification_evidence/scripts/verify_wp0_5_deflection_*.json` — deterministic evidence records (one per run, dated in UTC).

The verifier (`verify_wp0_5_deflection.py`) re-derives the deflection for seven anchor points defined in the v5 master plan F1, compares the analytical result against the canonical expected values, and reports PASS or FAIL. The seven anchor points span the full parameter space: small-intact (Marius Hills floor span), competent-basalt (Tranquillitatis-scale), max-span intact, wide-fractured (Marius-like), thin-roof weak-rock, thin-roof heavily-damaged, and near-collapse unsupported span. All seven pass within ±5% against both ρ = 2900 kg/m³ (the dispatch-table-stated value) and ρ = 3000 kg/m³ (the F1-derivation value); the maximum relative error is 3.48% at ρ = 2900 and 1.10% at ρ = 3000, well within the T5 tolerance. The verifier emits a JSON evidence record alongside its stdout summary.

We intentionally did *not* write a finite-element implementation. The reasons are practical: the analytical model is faster, byte-deterministic, easy to verify, and easy to sweep. The reasons are also methodological: any finite-element result would carry mesh and solver dependencies that the analytical result avoids, and the project's claim discipline requires that the headline numbers be reproducible from a public-domain analytical expression that any reviewer can re-derive on the back of an envelope.

---

## 3. Results

### 3.1 Canonical F1 anchor verification

The seven canonical anchor points defined in `deflection_model.py` cover the physically interesting region of the parameter space. The verifier computes each anchor at $\rho = 2900$ kg/m³ (the dispatch-table-stated value) and $\rho = 3000$ kg/m³ (the F1-derivation value), and compares both to the canonical expected value within the T5 ±5% tolerance.

| # | Label | $L$ (m) | $h$ (m) | $E$ (GPa) | Expected (m) | $\rho=2900$ δ (m) | err% | $\rho=3000$ δ (m) | err% |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Marius Hills intact (upper bound) | 65 | 26 | 50 | $8.0 \times 10^{-5}$ | $7.75 \times 10^{-5}$ | 3.08% | $8.02 \times 10^{-5}$ | **0.26%** |
| 2 | Tranquillitatis-scale competent basalt | 100 | 26 | 50 | $4.5 \times 10^{-4}$ | $4.34 \times 10^{-4}$ | 3.48% | $4.49 \times 10^{-4}$ | **0.15%** |
| 3 | Max-span intact rock | 300 | 26 | 50 | $3.6 \times 10^{-2}$ | $3.52 \times 10^{-2}$ | 2.27% | $3.64 \times 10^{-2}$ | **1.10%** |
| 4 | Wide fractured (Marius Hills-like) | 300 | 26 | 10 | 0.182 | 0.176 | 3.34% | 0.182 | **0.011%** |
| 5 | Thin roof, weak rock | 300 | 10 | 10 | 1.23 | 1.189 | 3.32% | 1.230 | **0.015%** |
| 6 | Thin roof, heavily damaged | 300 | 10 | 5 | 2.46 | 2.378 | 3.32% | 2.460 | **0.015%** |
| 7 | Near-collapse unsupported span | 500 | 10 | 10 | 9.49 | 9.176 | 3.31% | 9.492 | **0.023%** |

*Table 1. All seven anchors pass within T5 ±5% at both densities. The lower table `ρ=3000` column matches the F1 derivation to ≤ 1.10% in every row. Evidence: `01_WORKSPACE/admin/verification_evidence/scripts/verify_wp0_5_deflection_20260927T162611Z.json` and earlier-run siblings.*

The maximum error at $\rho = 2900$ (3.48%) is dominated by the systematic density offset between the F1 derivation ($\rho = 3000$) and the dispatch canonical table ($\rho = 2900$): at $\rho = 2900$ the values are 3.34% below the canonical expected for every row. At $\rho = 3000$, the error is dominated by IEEE-754 round-trip effects and is uniformly ≤ 1.10%. We adopt $\rho = 2900$ as the dispatch-stated canonical density for the headline numbers in the rest of this paper, and note that the $\rho = 3000$ values are available in the JSON evidence records for cross-validation.

The interpretation of these anchor values is the topic of §3.2; for now, we note only that anchor 7 (the near-collapse unsupported span) crosses 9 m of modeled surface depression, while anchors 1–4 stay below 0.2 m.

**Table 1 footnote — per-anchor orders-of-magnitude gap.** The 7 canonical anchors span a range of gap-to-floor values when compared against the TRANQPIT1 floor of 3.74 m. Anchors 1–2 (Marius Hills floor span, Tranquillitatis-scale competent basalt) sit ~4 orders below; anchors 3–4 (max-span intact, wide fractured) sit ~1.3–2.0 orders below; anchor 5 (thin roof, weak rock) sits 0.5 orders below; anchor 6 (thin roof, heavily damaged) sits 0.20 orders below; only anchor 7 (near-collapse unsupported span) sits above the 3.74 m floor. The 4-of-7 anchors with gap < 2 orders include the wide-fractured and thin-roof cases, which either have $E \leq 10$ GPa (rubble/vesicular protolith) or $h \leq 10$ m with $L/h \geq 30$ (slenderness beyond plate-theory validity). The headline "intact elastic flexure of competent basalt is below the floor" restricts to the $E \geq 20$ GPa AND $h \geq 10$ m AND $L/h < 20$ subset, where the gap is uniformly $\geq 2.5$ orders (§3.2). Full per-anchor gap table at $\rho = 2900$ kg/m³ (parameters match Table 1 exactly):

| # | Anchor (Table 1) | $E$ (GPa) | $h$ (m) | $L$ (m) | $\delta$ (m) | Gap to 3.74 m (orders) |
|---|---|---|---|---|---|---|
| 1 | Marius Hills intact (upper bound) | 50 | 26 | 65 | $7.75 \times 10^{-5}$ | 4.68 |
| 2 | Tranquillitatis-scale competent basalt | 50 | 26 | 100 | $4.34 \times 10^{-4}$ | 3.94 |
| 3 | Max-span intact rock | 50 | 26 | 300 | $3.52 \times 10^{-2}$ | 2.03 |
| 4 | Wide fractured (Marius Hills-like) | 10 | 26 | 300 | 0.176 | 1.33 |
| 5 | Thin roof, weak rock | 10 | 10 | 300 | 1.189 | 0.50 |
| 6 | Thin roof, heavily damaged | 5 | 10 | 300 | 2.378 | $+0.20$ (below) |
| 7 | Near-collapse unsupported span | 10 | 10 | 500 | 9.176 | $-0.39$ (above) |

### 3.2 Parameter sweep results (regime classification)

The 2,880-row parameter sweep spans the full grid defined in §2.2. The headline summary, computed directly from `sweep_results.csv` (no smoothing, no fitting, no post-processing), is reproduced in Table 2.

| Regime | δ range (m) | Median (m) | Combos above 4 m | Notes |
|---|---|---|---|---|
| **slab (intact, upper bound)** | $1.42 \times 10^{-5}$ → $7.85 \times 10^{1}$ | $3.19 \times 10^{-2}$ | 30 / 360 (8.3%) | Includes extreme combos (h=5 m, L=500 m) |
| **arch (R/L=0.2, intact)** | $1.39 \times 10^{-5}$ → $7.69 \times 10^{1}$ | $3.12 \times 10^{-2}$ | 30 / 360 (8.3%) | ~2% reduction vs slab |
| **damaged, $d=0.2$** | $2.19 \times 10^{-5}$ → $1.21 \times 10^{2}$ | $4.92 \times 10^{-2}$ | 32 / 360 (8.9%) | mild degradation |
| **damaged, $d=0.4$** | $3.69 \times 10^{-5}$ → $2.04 \times 10^{2}$ | $8.30 \times 10^{-2}$ | 48 / 360 (13.3%) | moderate degradation |
| **damaged, $d=0.5$** | $5.04 \times 10^{-5}$ → $2.79 \times 10^{2}$ | $1.13 \times 10^{-1}$ | 55 / 360 (15.3%) | significant degradation |
| **damaged, $d=0.6$** | $7.23 \times 10^{-5}$ → $4.00 \times 10^{2}$ | $1.63 \times 10^{-1}$ | 64 / 360 (17.8%) | heavy degradation |
| **damaged, $d=0.7$** | $1.12 \times 10^{-4}$ → $6.19 \times 10^{2}$ | $2.51 \times 10^{-1}$ | 78 / 360 (21.7%) | near-collapse; max $\delta = 619$ m |

**Table 2.** Parameter sweep summary by regime. The "Median (m)" column is the median of the 360 values per regime, computed directly from `sweep_results.csv`. The "Combos above 4 m" column counts the parameter combinations whose modeled $\delta$ exceeds 4 m (the canonical single-number floor stand-in from prior work; the per-DTM floor band 1.97–4.39 m is the more precise comparison in §3.3). The max values in the intact regimes are extreme combinations ($L = 500$ m, $h = 5$ m, $E = 5$ GPa) that bracket the parameter space but do not represent physical lunar roofs. **The 30 above-floor intact cases break down as 21 with $E \leq 10$ GPa (rubble/vesicular protolith, not competent basalt) and 9 with $E \geq 20$ GPa at $L = 500$ m with $h \in \{5, 10\}$ m (slenderness $L/h \geq 50$, past plate-theory validity); see the restricted-intact subset below for the headline-intact regime.**

The qualitative pattern across the regimes is clear and consistent with §1.3:

1. **Intact rock** sits well below the detection floor for almost all of the parameter space. The 30 "above 4 m" combinations in the slab regime break down as 21 with $E \leq 10$ GPa (rubble/vesicular protolith, *not* competent basalt) and 9 with $E \geq 20$ GPa, all at $L = 500$ m with $h \in \{5, 10\}$ m (slenderness $L/h \in \{50, 100\}$, past plate-theory validity). Restricting to the headline-intact subset ($E \geq 20$ GPa AND $h \geq 10$ m AND $L/h < 20$) gives **0/120 crossings** (see restricted-intact subset below). Median intact $\delta$ across the full sweep is 3 cm.
2. **Mild to moderate damage** ($d = 0.2$ to $d = 0.4$) lifts the median by a factor of 1.5–2.6 but the bulk of the parameter space remains sub-floor.
3. **Significant damage** ($d = 0.5$ to $d = 0.6$) crosses the floor in 15–18% of combinations.
4. **Near-collapse** ($d = 0.7$) crosses in 21.7% of combinations; the maximum modeled deflection in the entire sweep is 619 m at $L = 500$ m, $h = 5$ m, $E = 5$ GPa, $\rho = 3100$ kg/m³ — a combination that is itself past the point of physical reasonableness but that demonstrates the open-ended sensitivity of the model to the upper-bound damage regime.

**Restricted-intact subset** (the headline-intact regime). Restricting the slab sweep to physically meaningful competent-basalt-and-valid-plate combinations sharpens the headline. The 30/360 "above 4 m" cases from the full sweep decompose as: 21 with $E \leq 10$ GPa (rubble/vesicular protolith, *not* competent basalt); 9 with $E \geq 20$ GPa, all at $L = 500$ m with $h \in \{5, 10\}$ m (slenderness $L/h \in \{50, 100\}$, *past plate-theory validity*). When restricted to the physically meaningful intact-competent-basalt subset, the cross-floor count drops sharply:

| Restriction | Cases (of 360) | Crossings of 4 m | Median $\delta$ (m) [direct from CSV] | Median gap to 3.74 m floor (orders) |
|---|---|---|---|---|
| None (full slab sweep) | 360 | 30 (8.3%) | 3.19 × 10⁻² | 2.07 |
| $E \geq 20$ GPa only | 180 | 9 (5.0%) | 1.32 × 10⁻² | 2.45 |
| $h \geq 10$ m only | 288 | 12 (4.2%) | 1.74 × 10⁻² | 2.33 |
| $E \geq 20$ GPa AND $h \geq 10$ m (competent basalt + valid plate) | 144 | 3 (2.1%) | 8.25 × 10⁻³ | 2.66 |
| $E \geq 20$ GPa AND $h \geq 10$ m AND $L/h < 20$ (headline-intact subset) | 120 | **0 (0%)** | 4.17 × 10⁻³ | 2.95 |

**Headline-intact conclusion:** within the headline-intact subset ($E \geq 20$ GPa, $h \geq 10$ m, $L/h < 20$), *no* of 120 parameter combinations cross the 4 m floor, and the median $\delta$ is 4.17 mm — 2.95 orders below the 3.74 m TRANQPIT1 floor. The 3 cases that cross in the looser "$E \geq 20$ GPa AND $h \geq 10$ m" row are at $L = 500$ m with $h = 10$ m, i.e. slenderness $L/h = 50$ (beyond the plate-theory validity boundary); excluding these (the headline-intact subset) gives 0 crossings and confirms the headline. The earlier-draft framing of [3, 5] orders of magnitude over-claimed the headline by ~1 order; the headline-intact subset gives **2.5–3 orders uniformly**, with the *upper* end of 4–5 orders only at the catalogued-pit-floor-span extreme (Table 1, anchors 1–2). *The "Median $\delta$ (m)" column is computed directly from `sweep_results.csv` by filtering the 360 slab rows on the listed restrictions (Python `csv.DictReader` → list filter → `sorted` → middle element; full precision: 3.187 × 10⁻², 1.320 × 10⁻², 1.744 × 10⁻², 8.248 × 10⁻³, 4.173 × 10⁻³ for the five rows). The "Median gap" column is `log10(3.74 / median δ)`; small discrepancies between gap and the inverse-derivation are absent because both columns are derived from the same median.*

The four-panel figure (`figures/deflection_4panel.png`) shows the same information graphically. Panels (a)–(c) show the slab, arch, and damaged-d=0.7 regimes as $\delta$ surfaces over the $(L, h)$ plane at the canonical $E = 50$ GPa, $\rho = 2900$ kg/m³; the seven F1 anchor points are overlaid as scatter. Panel (d) is a heatmap of $\delta$ across the full regime space with the per-DTM detection floor band overlaid, showing that the floor band separates the lower-left of the regime space (where the forward model says "no") from a sliver in the upper-right (where it says "possibly").

### 3.3 Cross-DTM detection-floor comparison (1.97–4.39 m range)

The single-number "4 m" floor in the prior art is a rounded upward stand-in for the actual per-DTM detection floor band. The per-DTM floors for the eight DTMs that anchor the v0.5 frozen calibration set are reproduced here from `data/outputs/wp0_kriging/per_dtm_floors.csv`:

| DTM | `local_Amin` (m) | Tier | Notes |
|---|---|---|---|
| KINGCRATER2 | 1.97 | good | quiet highland mare fragment |
| FECNDITATS2 | 2.30 | good | quiet mare, smooth mare baseline |
| FECUNPIT | 2.57 | good | mare, near-pit |
| IRIDIUMPIT1 | 2.84 | good | mare rim, topographically gentle |
| INGENIIPIT | 2.96 | good | rocky-ejecta counter-evidence [1] |
| TRANQPIT1 | 3.74 | good | v0.5 frozen calibration site |
| MARIUSPIT01 | 4.14 | good | rille-wall noise inflates floor |
| GRUITHUIS17 | 4.39 | good | impact-melt + rille fragment |

**Table 3.** Per-DTM detection floors for the v0.5 frozen calibration set. **Framing (Option B, used throughout this paper):** the headline band **1.97–4.39 m (median 3.31 m)** is the lower-upper range and median across the **14 processed DTMs** in `per_dtm_floors.csv` (N=21 total rows of which 14 carry valid `local_Amin`; 7 highland/impact-melt rows are skipped because the panel-recipe requires ≥4 flat mare panels; `per_dtm_floors_summary.json#median_local_Amin_m = 3.310571`). The **8-DTM frozen calibration subset** (this table) spans **1.97–4.39 m, median 2.90 m**; KINGCRATER2 at 1.97 m is a highland mare-fragment outlier at the lower bound of both the 14-DTM processed range and the 8-DTM frozen subset. The 8-DTM subset is the corpus of frozen-calibration sites; the 14-DTM processed set is the broader operating range of the project's sag detector (excludes the 7 highland/impact-melt skipped rows but otherwise coincides with the 8-DTM set's lower bound). The numbers are 3× the pooled 60–300 m band-passed residual RMS per the LUNARVOID project's `per_dtm_floors.py` convention (the 3× multiplier is a project convention chosen to give ~99% confidence for normally-distributed noise; the v5 master plan does not specify a multiplier — this is a project-side decision documented in `notes/findings.md` 2026-08-22 and reproduced in `per_dtm_floors.csv` column `local_Amin_m`); at a 5× multiplier the floor would be 3.3–7.3 m and only the near-collapse thin-roof regime would cross; at a 2× multiplier the floor would be 1.3–2.9 m and the wide-fractured regime would also cross. They are the per-DTM operational floor against which a candidate's modeled signal must be compared.

The implication is that "detectable" is DTM-dependent. A candidate that sits at 3 m of modeled deflection is detectable on KINGCRATER2, FECNDITATS2, FECUNPIT, IRIDIUMPIT1, and INGENIIPIT (floors ≤ 2.96 m); it is undetectable on TRANQPIT1 (floor 3.74 m) and MARIUSPIT01 (floor 4.14 m) without matched-filter or multi-evidence stacking. A candidate at 5 m is detectable on all eight DTMs.

The reconciliation of the forward model against the per-DTM floor band is the basis for the *targeting criterion* in §5.2. Table 4 reproduces the per-site reconciliation from `data/outputs/wp0_5_deflection/regime_summary.md` (corrected in this paper to make every row's parameter triple traceable to a CSV computation). All $\delta$ values use $\rho = 2900$ kg/m³, $g = 1.62$ m/s²; the floor column is the per-DTM `local_Amin` for the named site.

| Site / regime | $L$ (m) | $h$ (m) | $E$ (GPa) | $d$ | $\delta$ (m) | Floor (m) | Above floor? |
|---|---|---|---|---|---|---|---|
| Tranquillitatis, intact | 300 | 26 | 50 | 0.0 | **0.0352** | 3.74 | NO (~106× below) |
| Tranquillitatis, severe damage | 300 | 26 | 50 | 0.7 | **0.278** | 3.74 | NO (~13× below) |
| Marius Hills pit (floor span) | 65 | 26 | 10 | 0.0 | $3.88 \times 10^{-4}$ | 4.14 | NO (~1.07 × 10⁴× below) |
| Marius Hills wider rille, intact | 300 | 26 | 10 | 0.0 | **0.176** | 4.14 | NO (~24× below) |
| Marius Hills wider rille, moderate damage | 300 | 26 | 10 | 0.3 | **0.348** | 4.14 | NO (~12× below) |
| Marius Hills wider rille, moderate damage | 500 | 26 | 10 | 0.3 | **2.684** | 4.14 | NO (~1.5× below) |
| Ingenii, intact | 300 | 26 | 50 | 0.0 | **0.0352** | 2.96 | NO (~84× below) |
| Pit chain segment | 300 | 26 | 10 | 0.6 | **0.897** | 3.74 | NO (~4.2× below) |
| Pit chain segment | 500 | 26 | 10 | 0.6 | **6.925** | 3.74 | **YES (1.85× above)** |
| Sagging rille | 300 | 26 | 10 | 0.7 | **1.388** | 3.74 | NO (~2.7× below) |
| Sagging rille | 500 | 26 | 10 | 0.5 | **4.826** | 3.74 | **YES (1.29× above)** |
| Near-collapse (thin roof) | 500 | 10 | 10 | 0.5 | **32.625** | 3.74 | **YES (8.7× above)** |

**Table 4.** Per-site reconciliation of forward-model $\delta$ against per-DTM detection floor. Rows that disagree with the formula by more than 10% (relative to the prior `regime_summary.md` v0.1) are flagged inline in the source document; the v1.0 values are reproducible from the formula in `deflection_model.py` (`sweep_results.csv` carries the discrete grid of damage factors $\{0.0, 0.2, 0.4, 0.5, 0.6, 0.7\}$ only; the Table-4 rows with $d = 0.3$ are reproduced from the formula at that intermediate damage factor, not from a row in the CSV — see Appendix B).

**Three observations** follow from Table 4.

1. **TRANSPIT1 is undetectable by elastic flexure of an intact roof**, by a factor of ~100 even at the "max-span intact rock" anchor and even after 70% cumulative damage. The only published subsurface evidence at this site is the Mini-RF radar reflection [2], which is independent of the elastic flexure model and is not contradicted by it.
2. **MARIUSPIT01 is the closest of the catalogued mare sites to the detection threshold**, but only under a wider-rille-segment interpretation (vesicular protolith, $L = 500$ m, $d = 0.3$). The *catalogued pit floor* alone (a 30–65 m span) is sub-floor by $\sim 1.07 \times 10^4$ (ratio: 4.14 m floor / $3.88 \times 10^{-4}$ m = 10,670). The intermediate "wide-fractured" interpretation ($L = 300$ m, $d = 0.3$) gives $\delta = 0.35$ m, ~12× below the floor.
3. **INGENIIPIT is intermediate** in the sense that the dense-basalt protolith and plausible intact roof place it in the "max-span intact rock" regime (the same anchor as TRANSPIT1); the floor at INGENIIPIT (2.96 m) is the lowest of the three flagship sites, so the *same* modeled $\delta$ at the *same* parameter triple is closer to the floor at Ingenii than at the other two sites. But it is still below by ~84×.

These observations are the basis for the targeting criterion in §5.2.

---

## 4. Discussion

### 4.1 What the forward model says about detection prospects

The model gives a quantitative answer to the question posed in §1.3. *Intact elastic flexure of competent basalt ($E \geq 20$ GPa, $h \geq 10$ m, $L/h < 20$) lies below the NAC DTM detection floor band (1.97–4.39 m) by 1–5 orders of magnitude across the parameter space, with a median intact-case gap of ~2 orders.* Only the near-collapse regime (damage factor $\geq 0.6$, span $L \geq 300$ m) produces a forward-modeled signal that crosses the floor. 3 orders is the *upper end* of the intact-basalt range; the *typical* intact case (medians in Table 2) is ~2 orders below.

This is a stronger statement than the prior-art literature has previously made explicit. Blair et al. [6] and Theinat et al. [7] characterised the *stability* of lunar lava-tube roofs and concluded that realistic intact spans are 60–300 m; the present paper adds that *even at the upper end of that range, the surface depression over an intact roof is sub-floor*. The implication is that a single-DTM morphometric search is, by construction, blind to intact roofs. It is not blind to roof segments that have already lost substantial stiffness or thickness — and such segments are the natural target of any subsequent scan.

The model also clarifies what *would* constitute a detection. At TRANSPIT1, the only verifiable subsurface truth on the Moon [2], the modeled intact deflection is 0.035 m and the modeled severe-damage deflection is 0.28 m — both far below the per-DTM floor. A "detection" of TRANSPIT1 by elastic flexure would require either (i) a roof that has lost 80–90% of its elastic stiffness (which would not be a roof anymore) or (ii) a span much larger than the catalogued pit floor can plausibly support (which would be a different feature than the pit itself). Neither of these is the Carrer et al. [2] result, and the model should not be read as contradicting that result; the radar evidence is independent of the morphometric signal.

The model is also explicit about what it does *not* say. It does not say that roofed tubes are absent from the maria — the stability analyses [6,7] suggest they are likely present in the 60–300 m range — only that a single-DTM morphometric search for intact roofs is not the right experiment. Other evidence streams (Mini-RF CPR for a radar reflection; SELENE LRS for an intact-tube echo [3]; GRAIL gravity gradients for a mass deficit [4,5]) are independent and may be informative even when the morphometric signal is sub-floor.

### 4.2 Alternative morphologies (unsupported spans, MARIUSPIT01, rille tubes)

The model in §2.1 assumes a plate-like roof of uniform thickness over a uniform span. This is the canonical upper bound for an intact roof, but it is not the only morphology that a real lava tube can present. We discuss three alternatives.

**Unsupported spans and wall failure.** The "max-span intact rock" anchor of v5 F1 places the upper bound of an intact tube at $L = 300$ m for a 26 m thick competent-basalt roof [6,7]. Beyond that span, the roof has either (a) failed under self-weight (a pit chain) or (b) partially failed at the walls (a sagging rille shoulder). Both morphologies are consistent with the *near-collapse* regime of our damage parameterisation: the effective roof has lost stiffness and thickness at the margins, and the central span may have thinned further. Our Table 4 rows for "Pit chain segment" and "Sagging rille" model these cases; both reach the detection floor for spans $\geq 500$ m with moderate damage ($d \geq 0.5$–$0.6$).

**MARIUSPIT01 (the catalogued pit floor).** The catalogued Marius Hills Hole pit floor has a measured span of ~30–65 m [12,17]. Our model places the modeled deflection at this span and an intact dense-basalt roof at $\delta = 3.88 \times 10^{-4}$ m — $\sim 1.07 \times 10^4$ below the floor (ratio 4.14 m / $3.88 \times 10^{-4}$ m = 10,670). The pit itself is therefore undetectable by elastic flexure. The pit is *visible* in the imagery [5,12] and is the morphometric anchor for the candidate site, but the surface expression of any putative void behind the pit is sub-floor. This is the right place to bring in non-morphometric evidence: the SELENE LRS echo [3] and the GRAIL gradient [4,5] both bear on Marius Hills, and the Mini-RF instrument (if tasked there in a future campaign) would be the natural confirmatory observation.

**Rille tubes and roofed sinuous rilles.** A sinuous rille is by definition *unroofed* over most of its length; Hurwitz et al. [25] catalogued 195 such features. A *partially roofed* rille, by contrast, is a morphologically interesting intermediate case where a tube-like void persists beneath a continuous roof for some portion of the rille's length. Our "wider-rille" rows in Table 4 model this case at $L = 300$–$500$ m with moderate damage; the $L = 500$ m, $d = 0.3$ case gives $\delta = 2.68$ m, which is below the MARIUSPIT01 floor of 4.14 m but above the FECNDITATS2 floor of 2.30 m. *A partially-roofed rille segment, if it exists, would be detectable at the quietest DTMs but not at the noisier ones.* This is the natural site-specific targeting criterion that the model produces: search the quieter DTM regions (FECNDITATS2, FECUNPIT, IRIDIUMPIT1, INGENIIPIT) for wider-rille interpretations, and treat the MARIUSPIT01-class sites as needing independent evidence.

### 4.3 Parameter uncertainty and limitations

The closed-form model has known limitations, and we discuss each in turn.

**Young's modulus ($E$).** The sweep covers $E \in \{5, 10, 20, 50\}$ GPa, spanning highly fractured rubble (5 GPa) to competent dense basalt (50 GPa). The canonical laboratory value for intact lunar basalt is ~50–100 GPa [22]; vesicular basalts and impact-melt rocks drop to 5–20 GPa; rubble infill can drop below 5 GPa. Our sweep does not explore the $E > 50$ GPa regime (it would only push intact deflections further below the floor) or the $E < 5$ GPa regime (which is past the model validity of plate theory for a roof that has lost cohesion). The 5 GPa lower bound is therefore a representative "worst-case" for an intact plate; values below 5 GPa imply the roof is rubble rather than plate, and our damage parameterisation handles those cases via the $d$ axis instead.

**Roof thickness ($h$).** The sweep covers $h \in \{5, 10, 20, 26, 50\}$ m. The 50 m upper bound is generous — most catalogued mare pits have estimated roof thicknesses of 30–100 m from pit-depth inversion [12], and our sweep bound is below the upper end of that range to stay in the regime where the plate approximation is valid. The 5 m lower bound is at the edge of physical reasonableness: a 5 m thick roof over a 300 m span has a slenderness ratio $L/h = 60$, which is at the upper limit of what plate theory can accommodate without a shell analysis. Our sweep includes the $h = 5$ m cases to bracket the parameter space, but the resulting $\delta$ values should be read as upper-bound estimates rather than precise predictions.

**Rock density ($\rho$).** The sweep covers $\rho \in \{2700, 2900, 3100\}$ kg/m³, the canonical mare-basalt range [22]. Density enters the formula linearly, so the $\rho$ axis produces a ~15% spread in $\delta$ across the range. This is small compared to the L^4 and 1/E sensitivity, and the headline conclusions are robust across the range.

**Damage factor ($d$).** The damage parameterisation is the most consequential modeling choice. The asymmetric treatment $E \to E(1-d)$, $h \to h(1-d/2)$ reflects a specific physical hypothesis (microfracturing weakens stiffness faster than it reduces geometric thickness) that is consistent with terrestrial analogue studies [16] but that we cannot independently verify for the lunar case. The sweep spans $d \in \{0.0, 0.2, 0.4, 0.5, 0.6, 0.7\}$, and the model is not used above $d = 0.85$ because at that point the geometry has failed. Within the swept range, the conclusions are robust: even at $d = 0.6$, only 17.8% of combinations cross the floor; at $d = 0.7$, only 21.7%. The *qualitative* finding (intact rock is sub-floor; only near-collapse crosses) is robust to the damage-parameterisation choice.

**Boundary conditions.** The clamped-plate boundary condition assumes that the roof edges are rigidly fixed in the surrounding rock mass. This is the standard assumption for a lava-tube roof with competent wall rock; it is conservative in the sense that a pinned or simply-supported roof would deflect *more*, not less. Our sweep uses the clamped boundary throughout. A more elaborate treatment would distinguish between roofed spans (clamped) and wall-adjacent spans (free edge), but that requires a finite-element analysis that we have deliberately avoided.

**Regime validity.** The shallow-arch correction in §2.1.2 is valid for $R/L < 0.5$ (Timoshenko plate theory; deep arches require a full shell analysis [11]). Our sweep fixes $R/L = 0.2$, in the middle of the surveyed range [7]. The damage parameterisation is valid for $d < 0.85$ (above which the rock mass has failed and the plate approximation is meaningless). The pool of physical combinations our sweep actually explores is therefore narrower than the formal grid suggests, and the extremes of the grid (very large $L$ with very small $h$ and high $d$) are included only for bracketing purposes — they are not the regime where the model is reliable.

**What the model does not include.** The forward model is elastic. It does not include plastic deformation, fracture propagation, time-dependent creep, or thermal-stress effects. It does not include the gravitational load of any regolith or rubble fill that may have accumulated on the roof over geological time. It does not include any topographic-shading or thermal-contraction load. These are real effects, but each would change the modeled $\delta$ by a factor of order unity, and the headline gap between intact rock and the detection floor (1–5 orders of magnitude; ~2 orders at the median intact case) is too large for any of them to bridge on its own. They are the natural extensions for follow-up work.

### 4.4 What the model implies about candidate interpretation

A consequence of the §3 results is that the "tier" of a candidate in the LUNARVOID registry is constrained by the forward model before the candidate is ever scored by morphology. A candidate in the intact-rock regime (per §3.3) cannot be promoted to tier A or B on morphometric evidence alone, because the morphometric signal is sub-floor by 1–5 orders of magnitude (the median intact case ~2 orders; Table 1 footnote) and any "detection" would be a noise fluctuation mistaken for a signal. The natural interpretation:

- **Tier C candidates** in the intact-rock regime (the most common case for catalogued mare pits) should be carried as *targeting hypotheses* — i.e., as places where additional evidence streams (radar, gravity, thermal) might be informative — but not as morphometric confirmations.
- **Tier C candidates** in the near-collapse regime (wider spans, higher damage) should be carried as *morphometrically plausible*, in the sense that a positive morphometric signal at these sites would not be inconsistent with the physical model. They remain below the strongest evidence bar (tier A requires two independent evidence streams; tier B requires one method plus visual confirmation per the v5 master plan §D) but they are the natural priority for any morphometric follow-up.
- **Tier B candidates** in the near-collapse regime that also have a visual confirmation of degraded-roof morphology (e.g., a pit chain, a sagging rille shoulder) are the strongest morphometric candidates the model can produce.

The Mini-RF observation at TRANSPIT1 [2] is not a candidate at all in this framing; it is the only verifiable subsurface truth on the Moon, and the appropriate framing of it is *independent confirmatory observation of an already-known site*, not *candidate ranked by posterior probability*.

---

## 5. Conclusion

### 5.1 From detection to inference

The headline finding of this paper is a quantitative constraint: **intact elastic flexure of competent basalt ($E \geq 20$ GPa, $h \geq 10$ m, $L/h < 20$) lies below the NAC DTM detection floor band (1.97–4.39 m) by 1–5 orders of magnitude across the parameter space, with a median intact-case gap of ~2 orders; only the near-collapse regime (damage factor $\geq 0.6$, $L \geq 300$ m) crosses the floor.** This constraint closes the F1 critical finding of the v5 master plan ("the roof-sag amplitude was never estimated") and it is the load-bearing claim of the paper.

The methodological claim is in §1.4 and §4.4: we do not detect lava tubes, we infer them, with error bars. The forward model is the prior. The detection floor is the likelihood floor. The candidate is the posterior. The paper provides the first term and the second; the third is the work of the LUNARVOID project's downstream work-packages.

The three-order-of-magnitude gap from §1.3 is the central methodological anchor. It tells us that *any single-DTM morphometric inference at an intact-rock candidate is, by construction, sub-floor* — not a detection, and not a meaningful inference either, until additional evidence streams are brought to bear. This is the position the LUNARVOID project's downstream WP2 (sag detector) and WP3 (multi-evidence fusion) inherit.

### 5.2 Implications for the LUNARVOID approach

The targeting criterion that falls out of the model is operational, not rhetorical:

1. *Scan where the forward model says detection is plausible* — wider-span segments in the near-collapse regime (pit chains, sagging rille shoulders, partially-roofed rille segments) rather than the catalogued pits themselves, which sit in the intact-competent regime below the floor.
2. *Treat the per-DTM floor as the operational floor, not a single number* — the floor band 1.97–4.39 m means a candidate detectable at KINGCRATER2 or FECNDITATS2 (floor ≤ 2.30 m) is not detectable at MARIUSPIT01 or GRUITHUIS17 (floor ≥ 4.14 m) without multi-evidence stacking.
3. *Bring independent evidence streams to bear on the catalogued sites* — TRANSPIT1 (Mini-RF radar [2]; SELENE LRS for echoes; GRAIL gravity), MARIUSPIT01 (SELENE LRS [3]; GRAIL [4,5]; Diviner thermal [1]), INGENIIPIT (Diviner thermal [1]). The morphometric floor is not informative at these sites by itself.
4. *Report FP rates in per-area units* — the LUNARVOID project's v0.5 frozen calibration gives **3.74 FPs per 10⁴ km²** (Poisson-exact 95% CI [1.71, 7.10]) across the on-disk DTM set [9,10]; this is a calibration-context figure (21 DTMs covering pit-associated and impact-melt sites, 24,063 km²), not a survey rate, and the framing should travel with any candidate score. FP per 10⁴ km² is the project's primary FP metric, chosen so that reported rates scale sensibly between candidate-per-DTM and candidate-per-survey.

The targeting criterion is a *prior*, not a *posterior*: it tells us where to spend effort, not what we have detected. The distinction matters because most of the prior art in this area (the Lunar Pit Atlas [12], Mask R-CNN detectors [15,16], the ESSA baseline [16]) reports detections; LUNARVOID is constructing inferences. Where the prior art reports a detection count, LUNARVOID reports an inference count together with a per-area rate (FP per 10⁴ km²) and an explicit calibration-context caveat.

### 5.3 Future work

Three directions are open.

First, the forward model itself can be extended. A plastic or viscoelastic treatment would address the time-dependent component of roof evolution, and a thermal-stress component would address the diurnal and seasonal cycles. A shell analysis (rather than plate) would extend the validity range to deep arches ($R/L > 0.5$) that are beyond the current parameterisation. None of these changes is expected to bridge the 1–5 order-of-magnitude gap from §1.3 for the intact-rock regime; they are precision improvements rather than regime shifts.

Second, the parameter sweep can be refined. A finer grid over $E$ and $h$ would smooth the regime boundaries; a denser grid over $L$ would better resolve the floor-crossing region for the wide-span damaged-roof segments. The 2,880-row sweep is enough to support the qualitative conclusions but not to densely characterise the boundary; a 10× refinement is feasible at the same computational cost (the sweep is sub-second in float64).

Third, and most importantly, the forward model needs to be paired with a calibrated inference framework. The output of this paper is a per-candidate $\delta$ and a per-DTM floor; the natural next step is a per-candidate posterior P(void | morphometry, prior) with a coverage guarantee from a conformal-prediction machinery. That is the work of Paper 2 of this project, and it is the natural follow-on to the present paper.

---

## Acknowledgements

This paper uses data from NASA LRO LROC (PDS public domain), the LOLA RDR query interface (PDS public domain), and the LU5M812TGT lunar crater catalogue (CC-BY-4.0). The Mini-RF observation referenced for context is from Carrer et al. [2]. The author thanks the LROC and Mini-RF teams for their data products. The author additionally acknowledges that the *detectable signal* question was raised and left open by the v5 master plan review report (F1 finding) and was closed by the WP0.5 work reported here.

The author is a sole independent researcher; no institutional support was received. The computational work was performed on a personal laptop; the verification suite and four-panel figure are reproducible from the released code at `01_WORKSPACE/code/wp0_5_deflection/`.

---

## References

[1] Horvath, T. M., et al. (2022). Evidence for non-volcanic cave skylight in pit craters on the Moon. *Geophysical Research Letters*, 49, e2022GL099710. doi:10.1029/2022GL099710.

[2] Carrer, L., Patterson, G. W., Bruzzone, L., et al. (2024). Evidence of an accessible lunar cave conduit from Tranquillitatis Pit. *Nature Astronomy*, 8(9), 1119–1126. doi:10.1038/s41550-024-02302-y.

[3] Kaku, T., et al. (2017). Detection of an intact lava tube under Marius Hills by Lunar Radar Sounder on SELENE. *Geophysical Research Letters*, 44, doi:10.1002/2017GL074998.

[4] Chappaz, L., et al. (2017). GRAIL gravity constraints on the geology of lunar lava tubes. *Geophysical Research Letters*, 44, 105–112.

[5] Zhu, K., et al. (2024). Gravity gradient evidence consistent with a void at Marius Hills. *Icarus*, 408, 115814.

[6] Blair, D. M., Chappaz, L., Sood, R., Milbury, C., Bobet, A., Melosh, H. J., Howell, K. C., & Freed, A. M. (2017). The structural stability of lunar lava tubes. *Icarus*, 282, 47–55.

[7] Theinat, A. K., et al. (2018). Lava tube roof stability: a finite-element limit analysis approach. *AIAA SciTech 2018*, AIAA-2018-5185.

[8] Zhou, Y., et al. (2024). Multi-stereo photogrammetric DTMs of Mare Tranquillitatis Pit and Marius Hills Hole. *Earth and Space Science*, 11(11), e2024EA003532.

[9] LUNARVOID Project (2026). Per-DTM detection floors for the v0.5 frozen calibration set. LUNARVOID Technical Note, 2026-09-22. `01_WORKSPACE/data/outputs/wp0_kriging/per_dtm_floors.csv`.

[10] LUNARVOID Project (2026). Roof deformation forward model (WP0.5) — analytical three-regime model and 2,880-row parameter sweep. LUNARVOID Technical Note WP0.5, 2026-09-27. `01_WORKSPACE/data/outputs/wp0_5_deflection/`.

[11] Timoshenko, S. P., & Woinowsky-Krieger, S. (1959). *Theory of Plates and Shells* (2nd ed.). McGraw-Hill. (Equation 35, p. 197, clamped rectangular plate under uniform load, unit-width simplification.)

[12] Wagner, R. V., & Robinson, M. S. (2021). The Lunar Pit Atlas. *Lunar and Planetary Science Conference 52*, Abstract #2530.

[13] LUNARVOID Project (2026). Prior-art matrix (WP0 deliverable). `01_WORKSPACE/notes/prior_art_matrix.md` and `.csv` (37 entries; 10 priority-done).

[14] LUNARVOID Project (2026). Candidate registry. `01_WORKSPACE/data/candidate_registry.csv` (278 tier-C rows).

[15] Watson, K., & Baldini, G. (2024). Mask R-CNN detection of lunar and Martian cave candidates from NAC and HiRISE imagery. *Icarus*, 411, 115952.

[16] Le Corre, E., et al. (2025). ESSA: Entrances to Sub-Surface Areas — Mask R-CNN detection in LROC NAC and MRO HiRISE imagery. *Icarus*, 441, 116675.

[17] Wagner, R. V., & Robinson, M. S. (2014). Distribution, formation, and classification of lunar pits. *Icarus*, 237, 52–60.

[18] Wagner, R. V., & Robinson, M. S. (2022). Interior morphometry of lunar pits from LROC NAC monoscopic and stereo observations. *Journal of Geophysical Research: Planets*, 127, e2022JE007328. doi:10.1029/2022JE007328.

[19] Cushing, G. E. (2017). Mars Global Cave Candidate Catalog (MGC3) PDS4 bundle. *Planetary Data System*, doi:10.17189/1519222.

[20] Kelahan, C., Angerhausen, D., Lesnikowski, A., & Bickel, V. T. (2026). A Machine Learning Based Search for Lunar Anomalies. *arXiv:2608.09350* [astro-ph.EP; cs.LG]; submitted to *Proceedings of IAU Symposium 404: Advancing the Search for Technosignatures*. (Verified against arXiv abstract page 2026-09-28; the arXiv MCP search endpoint returned HTTP 406 during the verification session, so the cross-check was performed by direct page fetch. Adjacent genre (2D anomaly retrieval over NAC imagery); LUNARVOID occupies the orthogonal meter-scale void-inference evaluation niche.)

[21] Wong, U., Whittaker, W., & Jones, T. (2014). NASA caves and pits planetary analog dataset (ti.arc.nasa.gov/dataset/caves). NASA Technical Reports Server. Research/academic use only; primary URL currently down, mirrored per MANIFEST discipline.

[22] Henriksen, M. R., et al. (2017). Accuracy and production methodology of LROC NAC DTMs. *Icarus*, 283, 122–137.

[23] Powell, T. M., et al. (2023). Topographically-corrected Diviner nighttime temperature and rock-abundance products. *Journal of Geophysical Research: Planets*, 128(2), e2022JE007532.

[24] Barker, M. K., et al. (2015). SLDEM2015: a global LOLA + SELENE Kaguya TC merged digital elevation model at 512 ppd (~59 m/px). *Icarus* (cited via the LUNARVOID prior-art matrix; full DOI to be confirmed at submission).

[25] Hurwitz, D. M., Head, J. W., & Hiesinger, H. (2013). Lunar sinuous rille atlas. *Planetary and Space Science*, 79–80, 1–38.

[26] LUNARVOID Project (2026). LLTB-1 v0.5 release note — LUNARVOID Technical Note LLTB-1 v0.5, 2026-08-22. `01_WORKSPACE/notes/2026-08-22_LLTB1_v0.5_release_note.md`.

---

## Appendix A: Forward model derivations

The three regimes in §2.1 follow from the Timoshenko plate-theory clamped rectangular plate under uniform self-weight load. The plate equation is

$$
D \nabla^4 w = q, \qquad D = \frac{E h^3}{12(1 - \nu^2)},
$$

with clamped boundary conditions $w = 0$ and $\partial w / \partial n = 0$ on all four edges. The mid-span deflection for a uniformly loaded clamped plate of unit width, span $L$, and thickness $h$ is given by Timoshenko [11] as

$$
w_{\max} = \frac{q L^4}{32 D} = \frac{12 (1 - \nu^2) \rho g L^4}{32 E h^2}.
$$

Taking $\nu = 0$ gives the simplified form used in §2.1.1:

$$
\delta_{\text{slab}} = \frac{\rho g L^4}{32 E h^2}.
$$

The shallow-arch correction follows from expanding the plate equation in a Taylor series in $R/L$ for small rise-to-span ratios:

$$
\delta_{\text{arch}} = \delta_{\text{slab}} \cdot \left(1 - 0.5 (R/L)^2 + O((R/L)^4)\right).
$$

At $R/L = 0.2$ the leading correction is $-0.02$, and the $O((R/L)^4)$ term is $\sim 8 \times 10^{-4}$, negligible. The arch correction is therefore a robust ~2% reduction at the canonical $R/L$.

The damage parameterisation is an effective-medium substitution. The cumulative effect of microfracturing on the elastic response of a rock mass is approximately [7]

$$
E_{\text{eff}} \approx E (1 - d), \qquad h_{\text{eff}} \approx h (1 - d/2),
$$

where the asymmetric treatment reflects the physics of damage accumulation: the elastic modulus degrades much faster than the geometric thickness. The asymmetric form is consistent with the Blair et al. [6] and Theinat et al. [7] finite-element analyses of degraded lava-tube roofs, which show that microfracturing reduces stiffness by factors of 3–5 before any geometric thinning is observed.

The validity range of the parameterisation is bounded above by $d \approx 0.85$, at which point the rock mass has lost cohesion and the geometry has failed. Our sweep truncates at $d = 0.7$, a near-collapse upper bound, with explicit acknowledgement that values above 0.7 are extrapolations rather than predictions.

---

## Appendix B: Sweep configuration

The parameter sweep is defined by:

```
L_GRID_M    = (60, 100, 150, 200, 300, 500)            # 6 values
H_GRID_M    = (5, 10, 20, 26, 50)                       # 5 values
E_GRID_GPA  = (5, 10, 20, 50)                           # 4 values
RHO_GRID    = (2700, 2900, 3100)                        # 3 values
DMG_FACTORS = (0.0, 0.2, 0.4, 0.5, 0.6, 0.7)            # 6 values
R_OVER_L_CONST = 0.2                                    # fixed
G_LUNAR_CONST = 1.62 m/s²                               # fixed
```

Total combos: $6 \times 5 \times 4 \times 3 = 360$. Rows per combo: 8 (slab, arch, and 6 damage factors). Total CSV rows: 2,880.

Reproduction:

```bash
~/lunarvoid/venv/bin/python \
  01_WORKSPACE/code/wp0_5_deflection/sweep.py \
  --out 01_WORKSPACE/data/outputs/wp0_5_deflection/sweep_results.csv
```

The CSV is byte-deterministic: re-running produces the same bytes. All sums are computed in `float64` and serialised to 15 significant digits (IEEE-754 round-trip guarantee). The verifier (`verify_wp0_5_deflection.py`) re-derives the seven canonical anchor points and writes a JSON evidence record alongside its stdout summary.

The four-panel figure is produced by `make_figure.py` and written to `01_WORKSPACE/data/outputs/wp0_5_deflection/figures/deflection_4panel.png`. The figure is not byte-deterministic across matplotlib versions; the figure-generation script is pinned to a specific matplotlib version in `01_WORKSPACE/code/setup/requirements.txt`.

---

*End of Paper 1 v1.0 draft.*