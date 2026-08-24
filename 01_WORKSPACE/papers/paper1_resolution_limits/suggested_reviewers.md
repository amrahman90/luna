# Suggested Reviewers — Paper 1 ("LLTB-1 calibrated benchmark")

**Status:** TEMPLATE — placeholder fields, not actual names.
**Target journal:** *Remote Sensing of Environment* (primary).
**Format:** RSE-style table; each row has bracketed placeholders for
the user to fill in real names against the expertise-area rationale.

---

## Important caveat

> The author of this template (LUNARVOID paper-writer agent) does
> **not** have current knowledge of specific individuals in the
> research groups named below. The expertise-area mapping is anchored
> in the references cited in Paper 1 (Le Corre 2025 ESSA; Mueller
> 2026; Reichenzeller 2026; Carrer 2024; Blair 2017; Chwala 2024;
> Theinat 2020; Wagner & Robinson 2021; Wong 2014) and in their
> `notes/prior_art_matrix.csv` rows. The user should fill in real
> names from these groups and verify each candidate's current
> affiliation, recent publications, and any conflict-of-interest
> signals before submission.

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
4. **Lava tube stability** — Blair 2017; Chwala 2024; Theinat 2020 —
   the 60–300 m lunar tube-width band that anchors the vesselness
   scale selection.
5. **Radar sounder** — Carrer 2024 Mini-RF S-band imaging of the
   Tranquillitatis conduit; the only instrumented subsurface
   evidence on the Moon to date.

A balanced 4–6 reviewer slate should cover at least areas 1, 2, and
4; area 5 strengthens the radar-anchor discussion; area 3 covers the
methodological inheritance.

---

## Reviewer suggestions (template; user fills in)

### R1 — Lunar pit / planetary cave detection (direct competitor)

| Field | Value |
|---|---|
| **Name** | [Name] |
| **Affiliation** | [Lab / University] (e.g., applied planetary
  remote-sensing group that published on lunar pit detection) |
| **Email** | [corresponding-email@institution] |
| **Expertise (1 sentence)** | Lunar pit detection using deep
  learning on LROC NAC imagery; published the ESSA pipeline
  (Le Corre 2025) and prior lunar pit catalogs. |
| **Why qualified (1 sentence)** | Most-cited direct competitor
  to LLTB-1; reviewer can audit the ESSA-vs-LLTB-1 positioning
  (Cover Letter §2; Refs R8/R9) and the v5 claim-discipline
  framing around detection vs inference. |
| **Conflict-of-interest note** | No known conflict; verify before
  submission. If ESSA is the same first author (Le Corre), flag
  as direct competitor and consider whether the editor would
  consider this a competitive conflict. |

### R2 — LROC NAC pit catalog / morphometry

| Field | Value |
|---|---|
| **Name** | [Name] |
| **Affiliation** | [Lab / University] (Wagner & Robinson
  group, Arizona State University / LROC team) |
| **Email** | [corresponding-email@institution] |
| **Expertise (1 sentence)** | LROC NAC pit catalogs and
  lunar surface morphometry; the primary label-set authority
  (Wagner & Robinson 2021). |
| **Why qualified (1 sentence)** | Can verify the 278-row tier-C
  registry bookkeeping against the ~281 catalogued-pit population
  and the ~20 tube-relevant subset (Abstract lines 84–88; §1.1
  line 95; G2 §3 row 3). |
| **Conflict-of-interest note** | No known conflict; verify before
  submission. Confirm independence from LLTB-1 author group. |

### R3 — Photogrammetry / point-cloud kriging (UAV domain)

| Field | Value |
|---|---|
| **Name** | [Name] |
| **Affiliation** | [Lab / University] (Mueller group,
  UAV-photogrammetry + kriged systematic-error correction) |
| **Email** | [corresponding-email@institution] |
| **Expertise (1 sentence)** | Kriged distortion correction
  after ICP registration on snow-covered UAV photogrammetric
  point clouds (Mueller 2026). |
| **Why qualified (1 sentence)** | Can audit the I1–I7 inherited
  components (kriged I2 correction; zero-change noise-floor
  protocol; ICP parameters; §3.3.1 line 199; §4.5(e) line 506)
  and the calibration-freeze reproducibility claim
  (`calibration_transqpit1.json` md5 unchanged). |
| **Conflict-of-interest note** | No known conflict; verify before
  submission. If Mueller is the first author of one of the
  inherited-component papers, this is methodologically desirable
  but should be flagged as not-a-blind-reviewer for that section. |

### R4 — Forest / VCI / UAV-LiDAR (VCI inheritance)

| Field | Value |
|---|---|
| **Name** | [Name] |
| **Affiliation** | [Lab / University] (Reichenzeller group,
  UAV-LiDAR forest plots) |
| **Email** | [corresponding-email@institution] |
| **Expertise (1 sentence)** | Vertical Complexity Index for
  overstory tree detection in UAV-LiDAR and SfM forest plots
  (Reichenzeller 2026). |
| **Why qualified (1 sentence)** | Can audit the I8–I15 inherited
  components (VCI overhang detector; per-rung threshold re-tuning;
  inspect-every-apparent-FP discipline; stratified detectability
  template; I12 confound covariates; sensitivity heatmap;
  pre-registered funnel-pit failure prediction; calibrate-once-
  transfer-unchanged with declared matching radius; §4.4 lines
  337–384). |
| **Conflict-of-interest note** | No known conflict; verify before
  submission. If Reichenzeller is the first author of the
  inherited-component paper, flag as methodologically desirable
  but not a blind reviewer for that section. |

### R5 — Lava tube stability (mechanics)

| Field | Value |
|---|---|
| **Name** | [Name] |
| **Affiliation** | [Lab / University] (Blair / Chwala /
  Theinat group; lunar tube-stability modelling) |
| **Email** | [corresponding-email@institution] |
| **Expertise (1 sentence)** | Lava tube roof stability and
  maximum stable span modelling (Blair 2017; Chwala 2024;
  Theinat 2020). |
| **Why qualified (1 sentence)** | Can audit the 60–300 m
  vesselness-scale selection (§3.3 line 158; §4.5(e) line 496;
  §5.1 line 525) against the published stability bounds and
  comment on whether the physical-scale priors are defensible
  across the Blair/Theinat/Chwala triangle. |
| **Conflict-of-interest note** | No known conflict; verify before
  submission. |

### R6 — Radar sounder (Tranquillitatis anchor)

| Field | Value |
|---|---|
| **Name** | [Name] |
| **Affiliation** | [Lab / University] (Carrer / Mini-RF
  team or related; LRO Mini-RF S-band) |
| **Email** | [corresponding-email@institution] |
| **Expertise (1 sentence)** | LRO Mini-RF S-band imaging of
  lunar subsurface conduits (Carrer 2024). |
| **Why qualified (1 sentence)** | Can verify the
  Tranquillitatis-radar-conduit claim as the **only instrumented
  subsurface structure on the Moon** (Abstract lines 86–88; §4.1
  line 239; §4.4 line 381; §6 line 615; Cover Letter paragraph 2)
  and the v5 claim-discipline anchor that treats every other
  claim as calibrated inference. |
| **Conflict-of-interest note** | No known conflict; verify before
  submission. If Carrer is the first author, flag as
  methodologically desirable but not a blind reviewer for that
  section. |

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
  (R8/R9 in `notes/prior_art_matrix.csv`); the references section
  was assembled 2026-08-23 and is the authoritative exclusion list.
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
specific cited reference; the user fills in names without any
fabricated affiliations.
