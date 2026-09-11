# Suggested Reviewers — Paper 1 ("LLTB-1 calibrated benchmark")

**Status:** POPULATED with real, verified-by-literature candidates
(filled 2026-09-04 by the reviewer-finder agent via Crossref).
Emails and current affiliations still require verification.
**Target journal:** *Remote Sensing of Environment* (primary).
**Format:** RSE-style table; one primary + 1–2 alternates per slot.

---

## Important caveat

> Every name below was found in a real, indexed publication (Crossref
> query, 2026-09-04) and the representative citation is given so the
> user can verify it. **No email addresses were retrievable** — all
> `[verify email]` fields must be filled from the corresponding-author
> line of the cited paper before submission. Affiliations flagged
> `[verify]` were not returned in the Crossref affiliation field and
> are inferred from the paper's home institution; check them.
>
> **Cited-reference exclusion applies.** The pre-submission checklist
> below forbids suggesting any co-author of a Paper 1 reference. The
> current twelve references are Blair 2017, Carrer 2024, Garwood 1936,
> Kelahan 2026, Le Corre 2025, Mueller 2026, Planchon & Darboux 2002,
> Reichenzeller 2026, Theinat 2018, Wagner & Robinson 2021, Wang & Liu
> 2006, and Wong 2014; their authors (including
> **V. T. Bickel, a Kelahan et al. 2026 co-author — added as the ninth
> reference on 2026-09-10, after this file was first populated**) are
> therefore listed only as *excluded-but-obvious* names, never as
> primaries. Closely associated earlier works (Wagner & Robinson
> 2014/2022, Henriksen 2017, Chwała 2024, van Ewijk 2011, Zhou 2024,
> Costello 2026) are treated as excluded as well. The primaries below
> are deliberately independent of the reference list.
>
> **Conflict of interest:** the LUNARVOID team has no current
> collaborations, shared grants, or shared affiliations with any
> person named below. All entries default to *no known conflict*;
> re-verify within 30 days of submission.

---

## Rationale framework

The paper spans five expertise areas:

1. **Lunar pit detection / planetary cave detection** — direct
   competitor ESSA (Le Corre 2025); LROC NAC pit catalogs (Wagner &
   Robinson 2021); methodology inheritance from Wagner & Robinson.
2. **Photogrammetry + point-cloud kriging** — Mueller 2026 I1–I7
   components; kriged distortion correction after ICP registration
   on UAV photogrammetric point clouds.
3. **Forest / VCI / UAV-LiDAR** — Reichenzeller 2026 I8–I15; VCI for
   overstory tree detection in UAV-LiDAR and SfM forest plots; van
   Ewijk 2011 VCI original.
4. **Lava tube stability** — Blair 2017; Chwala 2024; Theinat 2018 —
   the 60–300 m lunar tube-width band that anchors the vesselness
   scale selection.
5. **Radar sounder** — Carrer 2024 Mini-RF S-band imaging of the
   Tranquillitatis conduit; the only instrumented subsurface
   evidence on the Moon to date.

A balanced 4–6 reviewer slate should cover at least areas 1, 2, and
4; area 5 strengthens the radar-anchor discussion; area 3 covers the
methodological inheritance.

---

## Reviewer suggestions (populated 2026-09-04)

### R1 — Lunar pit / planetary cave detection (direct competitor area)

**PRIMARY**

| Field | Value |
|---|---|
| **Name** | Anna Mittelholz |
| **Affiliation** | Institute of Geophysics, ETH Zürich, Switzerland [verify] |
| **Email** | [verify email — corresponding author line, recent ETH publications] |
| **Representative pubs** | Gómez Jodar, Mittelholz & Bickel (2025), "Geologic and Thermophysical Characterization of Lunar Volcanic Pits". — Ritter, Karatekin, Mittelholz & Stähler (2024), "Exploring subsurface extent and physical properties of lunar lava tubes using surface microgravity survey". |
| **Expertise (1 sentence)** | Geophysical characterisation of lunar volcanic pits and lava tubes — bridges pit detection and the gravity-confirmation layer (v5 Tier D). |
| **Why qualified (1 sentence)** | She characterises the exact target population (lunar volcanic pits) with independent geophysics, so she can audit the detection-vs-inference positioning and the base-rate argument without being an ESSA co-author. |
| **Conflict-of-interest note** | No known conflict. Not a co-author of any Paper 1 reference (verified against the nine-reference list 2026-09-11). Note: frequent co-author of V. T. Bickel (now excluded, below) — collaboration-network proximity only, no cited-reference conflict. |

**ALTERNATES**

- **Lingli Mu** — State Key Laboratory of Remote Sensing Science /
  Beijing Normal University & CAS [verify]. Li, Mu, Zhang, Dong & He
  (2025), "Martian Skylight Identification Based on the Deep Learning
  Model", *Remote Sensing* 17(15). Closest published analogue to
  ESSA outside the ESSA group; strong on the base-rate/false-positive
  framing. No known conflict.
- *Excluded but obvious:* **Valentin T. Bickel** (Center for Space and
  Habitability, University of Bern [verify — previously MPS
  Göttingen])* — was the original R1 primary (Bickel, Moseley,
  Lopez-Francos & Shirley 2021, "Peering into lunar permanently
  shadowed regions with deep learning", *Nature Communications*
  12:5607), but became **a co-author of a Paper 1 cited reference**
  when Kelahan, Angerhausen, Lesnikowski & Bickel (2026,
  arXiv:2608.09350) was added as the ninth reference on 2026-09-10;
  barred by the cited-reference exclusion rule. Do not suggest.
- *Excluded but obvious:* Daniel Le Corre (ESSA first author) — direct
  competitor **and** a Paper 1 cited author; do not suggest.

### R2 — LROC NAC DTM production / lunar morphometry

**PRIMARY**

| Field | Value |
|---|---|
| **Name** | Ryodo Hemmi |
| **Affiliation** | University of Tokyo, Dept. of Systems Innovation [verify]; co-author team spans JAXA |
| **Email** | [verify email — corresponding author line, PSJ 2025] |
| **Representative pubs** | Hemmi, Inoue, Kikuchi, Sato, Miyamoto, Otake & Yamamoto (2025), "LROC NAC-derived Meter-scale Topography of the Moon's South Polar Landing Sites: Digital Terrain Models and Their Quality Assessments", *Planetary Science Journal*, doi:10.3847/psj/ae10a4. |
| **Expertise (1 sentence)** | Production **and formal quality assessment** of meter-scale LROC NAC stereo DTMs, including vertical-precision budgets and LOLA co-registration. |
| **Why qualified (1 sentence)** | Paper 1's entire GSD-rung argument (0.5–10 m) and the `local_Amin` floor rest on what a NAC DTM can and cannot resolve; Hemmi is the most recent independent author of a NAC-DTM *quality assessment*, so he can audit the rung ladder and the per-DTM calibration-floor bookkeeping without being a Henriksen 2017 co-author. |
| **Conflict-of-interest note** | No known conflict; not a co-author of any Paper 1 reference. |

**ALTERNATES**

- **Benjamin D. Boatwright** — Dept. of Earth, Environmental and
  Planetary Sciences, Brown University [verify]. Boatwright & Head
  (2024), "Shape-from-shading Refinement of LOLA and LROC NAC Digital
  Elevation Models", *Planetary Science Journal* 5(5). Directly
  relevant to the illumination-degradation arm (§4.5). No known
  conflict.
- **Jan-Peter Muller / Yu Tao** — Imaging Group, UCL Mullard Space
  Science Laboratory. Muller, Tao & Walter (2024), "Digital Terrain
  Models of the NASA ARTEMIS sites from single LROC-NAC images using
  the UCL MADNet retrieval system", EPSC2024-1170. Single-image DTM
  retrieval — a useful sceptic on posting-vs-true-resolution. No known
  conflict.
- *Excluded but obvious:* R. V. Wagner and M. S. Robinson (ASU/LROC),
  and M. R. Henriksen / E. J. Speyerer (ASU) — the natural label-set
  authorities, but all are Paper 1 cited authors and are barred by the
  checklist. Note for the editor that the pit-catalog authority is
  necessarily excluded.

### R3 — Photogrammetry / point-cloud geostatistics (UAV domain)

**PRIMARY**

| Field | Value |
|---|---|
| **Name** | Branden Walker |
| **Affiliation** | Cold Regions Research Centre, Wilfrid Laurier University, Waterloo, ON, Canada |
| **Email** | [verify email — corresponding author line, Arctic Science 2021] |
| **Representative pubs** | Walker, Wilcox & Marsh (2021), "Accuracy assessment of late winter snow depth mapping for tundra environments using Structure-from-Motion photogrammetry", *Arctic Science* 7(3). |
| **Expertise (1 sentence)** | Accuracy assessment and error budgeting of SfM photogrammetric surfaces over low-texture snow-covered terrain — the same venue and problem class as the inherited Mueller 2026 components. |
| **Why qualified (1 sentence)** | Can audit I1–I7 (kriged I2 distortion correction, ICP parameters, zero-change noise-floor protocol, §3.3.1 line 199; §4.5(e) line 506) and the calibration-freeze reproducibility claim from inside the same literature, while being independent of the Mueller/DLR group. |
| **Conflict-of-interest note** | No known conflict. Verify he is not a Mueller 2026 co-author (Mueller et al. 2026, *Arctic Science* 12:1–23, doi:10.1139/as-2025-0062) — same journal, different group (DLR); confirm before submission. |

**ALTERNATES**

- **Yves Bühler** — WSL Institute for Snow and Avalanche Research SLF,
  Davos, Switzerland. Bührle, Marty, Eberhard, Stoffel, Hafner &
  Bühler (2022), "Spatially continuous snow depth mapping by airplane
  photogrammetry", *The Cryosphere* 17. Deep on systematic-error
  correction in repeat photogrammetric surfaces. No known conflict.
- **Ayman Habib** — Lyles School of Civil Engineering, Purdue
  University, USA. Zhou, Hasheminasab & Habib (2021),
  "Tightly-coupled camera/LiDAR integration for point cloud generation
  from GNSS/INS-assisted UAV mapping systems", *ISPRS J.
  Photogrammetry and Remote Sensing* 180. The strongest available
  auditor of registration geometry and residual-error modelling. No
  known conflict.
- *Geostatistics-specific fallback:* **Thomas Sanchez / David
  Conciatori** (Dept. of Civil and Environmental Engineering, Laval
  University), "Terrestrial laser scanning for structural inspection
  with Kriging interpolation", *Structure and Infrastructure
  Engineering* (2020) — on-target for the kriging step specifically,
  off-target for the planetary framing. Use only if a
  kriging-methods specialist is explicitly requested.

### R4 — Forest canopy structural complexity / UAV-LiDAR (VCI inheritance)

**PRIMARY**

| Field | Value |
|---|---|
| **Name** | Yanjun Su |
| **Affiliation** | State Key Laboratory of Vegetation and Environmental Change, Institute of Botany, Chinese Academy of Sciences, Beijing |
| **Email** | [verify email — corresponding author line, RSE 2022] |
| **Representative pubs** | Liu, Ma, Wu, Hu, Liu, Liu, Guo & Su (2022), "A novel entropy-based method to quantify forest canopy structural complexity from multiplatform lidar point clouds", *Remote Sensing of Environment* 282:113280. |
| **Expertise (1 sentence)** | Entropy-based vertical canopy complexity metrics (the direct methodological family of the Vertical Complexity Index) computed across TLS, UAV-LiDAR and ALS platforms. |
| **Why qualified (1 sentence)** | The VCI is an entropy statistic on vertical point distributions; Su's group published the leading RSE paper on exactly that statistic's cross-platform behaviour, so they can audit I8–I15 (VCI overhang detector, per-rung threshold re-tuning, stratified detectability template, sensitivity heatmap, §4.4 lines 337–384) and are already an RSE-community reviewer. |
| **Conflict-of-interest note** | No known conflict; not a co-author of van Ewijk 2011 or Reichenzeller 2026. |

**ALTERNATES**

- **Nicholas C. Coops** — Integrated Remote Sensing Studio, Faculty of
  Forestry, University of British Columbia, Canada. Queinnec, White &
  Coops (2021), "Comparing airborne and spaceborne photon-counting
  LiDAR canopy structural estimates across different boreal forest
  types", *Remote Sensing of Environment* 262. Senior authority on
  LiDAR structural metrics and on degrading point density between
  sensing platforms — precisely the LLTB-1 rung experiment in a
  forest guise. No known conflict.
- **Benjamin T. Fraser** — Dept. of Natural Resources and the
  Environment, University of New Hampshire, USA. Fraser, Congalton &
  Ducey (2025), "Quantifying the Accuracy of UAS-Lidar Individual Tree
  Detection Methods Across Height and DBH Size Classes", *Remote
  Sensing* 17(6). Specialist in **stratified** detection-accuracy
  reporting by object size — the same discipline as the stratified
  detectability curve. No known conflict.
- *Excluded but obvious:* Paul Treitz / K. van Ewijk (Queen's
  University) — authors of the original VCI paper (van Ewijk et al.
  2011, PE&RS; dropped from Paper 1's reference list at v1.1, but
  methodologically adjacent to the cited Reichenzeller et al. 2026);
  treated as excluded by the checklist.

### R5 — Lava tube stability / structural mechanics (FEM)

**PRIMARY**

| Field | Value |
|---|---|
| **Name** | Zhizhong Kang |
| **Affiliation** | School of Land Science and Technology, China University of Geosciences (Beijing) |
| **Email** | [verify email — corresponding author line, Electronics 2025] |
| **Representative pubs** | Wang, Kang, Ye, Yang & Qi (2025), "Validating Lava Tube Stability Through Finite Element Analysis of Real-Scene 3D Models", *Electronics* 14(15). |
| **Expertise (1 sentence)** | Finite-element stability analysis of lava tubes driven by **measured real-scene 3D point-cloud geometry** rather than idealised cross-sections. |
| **Why qualified (1 sentence)** | Uniquely placed to judge whether the 60–300 m vesselness-scale window (§3.3 line 158; §4.5(e) line 496; §5.1 line 525) is a defensible physical prior, because his group derives stable-span bounds from the same kind of surveyed analog point clouds LLTB-1 degrades. |
| **Conflict-of-interest note** | No known conflict; not a co-author of Blair 2017 or Theinat 2018. |

**ALTERNATES**

- **Peng-Zhi Pan** — State Key Laboratory of Geomechanics and
  Geotechnical Engineering, Institute of Rock and Soil Mechanics,
  Chinese Academy of Sciences, Wuhan. Liu, Pan, Xiao, Zhao, Wang, Xie,
  Wang, Feng & Du (2026), "The influence of layered roof on the
  stability of lunar lava tubes", *Icarus* 437. The most recent
  independent span-stability treatment; directly comparable to the
  Chwała bounds. No known conflict.
- **Long Xiao** — Planetary Science Institute, School of Earth
  Sciences, China University of Geosciences (Wuhan). Co-author of the
  above; adds lunar-geology context to a purely mechanical review.
  No known conflict.
- *Excluded but obvious:* Marcin Chwała, Goro Komatsu, Junichi
  Haruyama (Chwała 2024) and A. K. Theinat / A. Bobet / S. J. Dyke
  (Theinat 2018) — all cited or closely associated authors; barred.

### R6 — Radar sounder / lunar subsurface (Tranquillitatis anchor)

**PRIMARY**

| Field | Value |
|---|---|
| **Name** | Roberto Orosei |
| **Affiliation** | Istituto di Radioastronomia, Istituto Nazionale di Astrofisica (INAF-IRA), Bologna, Italy |
| **Email** | [verify email — corresponding author line, Remote Sensing 2025] |
| **Representative pubs** | Nozawa, Haruyama, Kumamoto, Iwata, Toyokawa, Head & Orosei (2025), "Detection of Small-Scale Subsurface Echoes Using Lunar Radar Sounder and Surface Scattering Simulations with a DEM-Generated Surface", *Remote Sensing* 17(10). — El Awag, Genova, Orosei et al. (2026), "Lunar Radar Sounding for Ice Deposits and Subsurface Void Detection", *Remote Sensing*. |
| **Expertise (1 sentence)** | Planetary radar sounding (MARSIS/SHARAD heritage) and, most relevantly, **surface-clutter simulation from DEMs** to decide whether a subsurface echo is real. |
| **Why qualified (1 sentence)** | He can verify the paper's single hardest external claim — that the Tranquillitatis conduit is the *only* instrumented subsurface structure on the Moon (Abstract lines 86–88; §4.1 line 239; §6 line 615) — and, because his method couples DEM surface roughness to radar clutter, he is also competent on the topographic side of the argument. |
| **Conflict-of-interest note** | No known conflict; not a Carrer 2024 or Kaku 2017 co-author. Note he co-publishes with Haruyama (a Chwała 2024 co-author) — collaboration-network proximity only, not a cited-author conflict; flag to the editor if strict. |

**ALTERNATES**

- **Takao Kobayashi** — Korea Institute of Geoscience and Mineral
  Resources (KIGAM), Daejeon [verify]. Kobayashi, Kim, Lee & Song
  (2021), "Nadir Detection of Lunar Lava Tube by Kaguya Lunar Radar
  Sounder", *IEEE TGRS* 59(9). The most direct independent
  lava-tube-by-radar precedent; fully independent of the Carrer
  group. No known conflict.
- **Francesca Bovolo / Elena Donini** — Fondazione Bruno Kessler
  (FBK), Trento, Italy. Donini, Bovolo & Bruzzone (2021), "An
  Unsupervised Deep Learning Method for Subsurface Target Detection in
  Radar Sounder Data", IGARSS 2021. Ideal on the
  detection-statistics side. **Caution:** Trento-based and
  co-publishing with L. Bruzzone, a Carrer 2024 co-author — treat as
  institutionally proximate to the direct-anchor authors.
- *Excluded but obvious:* L. Carrer, R. Pozzobon, F. Sauro, G. W.
  Patterson, L. Bruzzone (Carrer 2024, *Nature Astronomy*) — the
  anchor paper's own authors; barred by the checklist.


---

## Suggested slate composition

A 4-reviewer minimum slate: **R1 + R3 + R4 + R5** (covers areas 1,
2, 3, 4 — all required expertise areas).
A 5-reviewer slate: **R1 + R3 + R4 + R5 + R6** (adds radar-anchor
audit, strengthens the claim-discipline review).
A 6-reviewer slate: **all 6 above** (R1 + R2 split is unusual but
covers both the direct-competitor and the LROC-pit-catalog
perspectives; consider R2 instead of R1 if a direct-competitor
reviewer is judged inappropriate by the editor).

---

## RSE submission-system fields (when filling)

RSE Editorial Manager typically asks for:

- **First name / Last name**
- **Email**
- **Institution**
- **Department**
- **Country**
- **Expertise keywords** (suggested):
  - R1: lunar pit detection; deep learning; planetary caves
  - R2: LROC NAC; lunar pits; planetary morphometry
  - R3: photogrammetry; kriging; ICP registration; UAV LiDAR
  - R4: vertical complexity index; forest remote sensing; UAV
  - R5: lava tube stability; geomechanics; planetary surfaces
  - R6: radar sounder; Mini-RF; lunar subsurface

---

## Final pre-submission checklist

- [ ] No reviewer is a co-author of any reference cited in Paper 1
  (R8/R9 in `notes/prior_art_matrix.csv`). **Status 2026-09-11
  (post-Kelahan re-check): the reference list was, at that check, nine entries
  (Kelahan, Angerhausen, Lesnikowski & Bickel 2026, arXiv:2608.09350,
  added 2026-09-10). Re-checking the primaries against the nine-entry
  list found ONE conflict: V. T. Bickel (then R1 primary) is a
  Kelahan 2026 co-author → demoted to excluded-but-obvious; Anna
  Mittelholz promoted to R1 primary. The remaining primaries
  (Mittelholz, Hemmi, Walker, Su, Kang, Orosei) are not co-authors of
  any of the then-nine references. Update 2026-09-11 (skeptic session 50): three method references added (Garwood 1936; Planchon & Darboux 2002; Wang & Liu 2006) — the list is now TWELVE entries; none of the new co-authors (Garwood; Planchon; Darboux; Wang; Liu) is a current primary, so the exclusion verdict stands.** The excluded obvious names are listed
  per slot above.
- [ ] No reviewer shares an institutional affiliation with the
  LUNARVOID team for the past 5 years.
- [ ] No reviewer is a current collaborator on any active grant or
  manuscript with the LUNARVOID team.
- [ ] Suggested-reviewers count is **not** the same as the
  excluded-reviewers list (the latter must be supplied separately to
  the editor with explicit reasoning).
- [ ] All email addresses verified within 30 days of submission.
- [ ] All expertise keywords are journal-appropriate
  (avoid over-broad terms like "machine learning" or "remote
  sensing" without domain context).

---

*Claim-discipline check:* every suggested expertise area maps to a
specific cited reference; every name maps to a specific real,
Crossref-indexed publication given inline. No affiliation, email, or
publication was invented — fields that could not be verified are
marked `[verify]` rather than guessed. The primaries are all
independent of the Paper 1 reference list; the obvious
cited-reference names are listed explicitly as *excluded* so the
editor can see they were considered and ruled out.

*Search provenance:* Crossref REST API (`api.crossref.org/works`),
queries run 2026-09-04 across the six expertise areas with
`from-pub-date` filters of 2017–2020 depending on slot.
