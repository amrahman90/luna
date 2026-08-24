# Graphical Abstract Plan — Paper 1 ("LLTB-1 calibrated benchmark")

**Status:** PLAN ONLY — do **NOT** generate the graphic yet.
**Target journal:** *Remote Sensing of Environment* (primary).
**Constraint:** RSE graphical abstract is **required**, ≤1 page,
visually conveys the scope of the work.

---

## 1. Layout sketch (1-page, 4-panel grid)

```
+--------------------------------------------------------------+
|  HEADER BAND (full width, ~10% of page)                       |
|  Title (compressed): "Detectability limits for lava-tube     |
|  roof signatures in orbital topography"                       |
|  Sub: "LLTB-1 calibrated analog benchmark + lunar extension" |
+--------------------------+-----------------------------------+
|                          |                                   |
|   PANEL A (top-left)     |   PANEL B (top-right)             |
|   45% width × 45% height |   55% width × 45% height          |
|                          |                                   |
|   Analog benchmark       |   Lunar pipeline                  |
|   (LLTB-1 setup)         |   (Cycles 1-2 extension)          |
|                          |                                   |
+--------------------------+-----------------------------------+
|                          |                                   |
|   PANEL C (bottom-left)  |   PANEL D (bottom-right)          |
|   45% width × 45% height |   55% width × 45% height          |
|                          |                                   |
|   Headline number        |   Honest limitations             |
|   + callout boxes        |   + claim-discipline caveats      |
|                          |                                   |
+--------------------------+-----------------------------------+
```

### Panel A — Analog benchmark setup (LLTB-1)

- **Content:** IndianTunnel NorthSurface cliff/overhang point-cloud
  thumbnail (or a representative 0.5 m degraded rung crop)
  showing the source-of-truth site (cave interior visible through
  trench/skylights).
- **Arrow:** to a "degradation ladder" 5-row strip showing
  0.5 / 1 / 2 / 5 / 10 m rungs as nested boxes (frangi/vesselness
  scale 30–300 m fused).
- **Caption:** "6 analog sites × 5 GSD rungs = 30 (site × GSD)
  cells; ladder from Fieg / IndianTunnel_Collapse3 / NorthSurface /
  Kingsbowl / IndianTunnel_cave_10x / Sheepridge (NASA Pits and Caves,
  Wong 2014)."
- **Source fig:** `figs/fig_ladder_sensor_preview.png` (0.5 m panels
  baseline).

### Panel B — Lunar pipeline (Cycles 1-2 extension)

- **Content:** Block diagram (left-to-right): NAC DTM
  → Planchon-Darboux fill → depression-depth × Frangi-vesselness
  (sigmas 30/60/100/150/200/300 m) → per-rung threshold (I9) →
  local-maxima (5-cell) → registry row.
- **Numbers overlay:** "N = 21 processed DTMs", "278 tier-C rows",
  "84 score rasters", "$0 spent (local Tier-1 plan)".
- **Caption:** "Calibration frozen at TRANQPIT1
  (md5 `2597002375206aba3119c240c373ad62`); Cycles 1-2 (2026-08-23)
  closed TYCHOPK + 3 deferred DTMs at 4+5 m rungs."
- **Source fig:** synthesise (no direct existing artifact covers all
  pipeline stages at a glance).

### Panel C — Headline number (callout box)

- **Number:** **3.74 [1.71, 7.10] per 10⁴ km²**
- **Tag-line (small caps, BELOW the number, NOT replacing it):**
  "aggregate lunar FP, calibration-context, NOT survey"
- **Sub-callouts (3 small boxes stacked):**
  - "n_fp = 9, n_tp = 14, n_above_local_floor = 45"
  - "24,062.96 km² denominator (N = 21)"
  - "Poisson-exact (Garwood) 95% CI"
- **Source:** `transfer_summary.json` `aggregate` block; `main.md`
  §4.2 Table 1a (line 262).

### Panel D — Honest limitations (caveats)

- **Three red-bordered bullet callouts (small):**
  1. "Lunar FP per 10⁴ km² stays **NOT MEASURED** at survey scale;
     aggregate is calibration-context only (FECUNPIT 6 + TRANQPIT1 3
     FPs at 2 sites with catalogued pits)."
  2. "Tranquillitatis radar conduit (Carrer 2024) = the **only**
     instrumented subsurface structure on the Moon.",
  3. "30 random-mare sites deferred — no LROC NAC DTMs exist for
     those footprints (226 of 278 registry rows lack NAC coverage).
     Kaguya/SP/Chang'e DTMs out of scope for Paper 1."
- **Bottom strip:** "All CRediT roles → LUNARVOID team
  (single-author manuscript). Code & registry open at LUNARVOID repo."

---

## 2. Suggested source figures from `figs/`

| Panel | Use | File |
|---|---|---|
| A | site thumbnail / degraded rung | `figs/fig_ladder_sensor_preview.png` |
| A | ladder overview | `figs/fig_ladder_hapke_grid.png` |
| A | registration validation anchor | `figs/fig_analog_registration_validation.png` |
| B | depth-check anchor | `figs/fig_wp0_transqpit1_depth_check.png` |
| B | kriging-correction anchor | `figs/fig_wp0_kriging_tranqpit1.png` |
| C | no direct fig — text-only callout |
| D | pit-recovery anchor | `figs/fig_wp0_pit_recovery.png` |
| D | noise-floor anchor | `figs/fig_wp0_noise_floor_panels.png` |

The graphical abstract will **NOT** reproduce any fig verbatim; it
will reuse visual language (colormap, axis style, scale bar) from the
above to stay visually consistent with the manuscript.

---

## 3. Typography and color guidance

- **Typeface:** serif (Computer Modern / STIX Two Math if LaTeX
  output; otherwise a free DejaVu Serif). Numerical callouts use
  sans-serif (DejaVu Sans) at large size.
- **Color palette — subdued, data-faithful, NO decorative effects:**
  - Background: white or very-light grey (#F7F7F7).
  - Pipeline / arrow color: dark slate (#2E4053).
  - Mare DTM elevation colormap: viridis (`cividis` for color-blind
    safety) — consistent with main manuscript figs.
  - Highlight / callout (headline number 3.74): muted ochre
    (#B7791F) — *not* alarm red, *not* bright green; subdued.
  - Caveat / limitation bullets: muted brick (#9B2C2C) — present but
    not screaming.
  - Reference grid lines: light grey (#D1D5DB).
- **NO** gradients on text; **NO** drop shadows; **NO** glow effects;
  **NO** 3D bevels. RSE style guide penalises chart-junk.
- **Numerical callout typography:** the "3.74" must be ≥48 pt at
  intended print size (RSE column width ≈ 8.5 cm; the number should
  read clearly at thumbnail).

---

## 4. Key text elements (verbatim strings)

These are the **load-bearing** text strings to embed in the graphic.
They are claim-disciplined and trace to the manuscript.

- Title: "Detectability limits for lava-tube roof signatures in
  orbital topography"
- Subtitle: "LLTB-1 calibrated analog benchmark + lunar extension
  (Cycles 1-2 close, 2026-08-23)"
- Headline number (Panel C): **"3.74 [1.71, 7.10] per 10⁴ km²"**
- Headline tag-line (Panel C, small caps): "aggregate lunar FP,
  calibration-context, NOT survey"
- Limitation 1 (Panel D): "Lunar FP per 10⁴ km² stays NOT MEASURED
  at survey scale; aggregate is calibration-context only."
- Limitation 2 (Panel D): "Tranquillitatis radar conduit (Carrer
  2024) is the only instrumented subsurface structure on the Moon."
- Limitation 3 (Panel D): "30 random-mare sites deferred — no LROC
  NAC DTMs for those footprints; 226 of 278 tier-C rows lack NAC
  coverage."
- Footer: "LUNARVOID team · single-author manuscript · code & registry
  open at LUNARVOID repo."

---

## 5. Tools

**Recommendation:** **matplotlib (Agg backend) + Pillow** —
already used throughout the paper for the manuscript figures (see
`code/wp1_ladder/`, `code/wp2_sag/`); same font + colormap choices
give visual continuity. Render at 300 DPI for print, 150 DPI for
screen preview.

**Why not other tools:**
- TikZ: would require rebuilding the entire pipeline and gives
  LaTeX-native output but the per-panel raster inserts are awkward.
- Inkscape / SVG: more flexibility, but breaks the matplotlib visual
  continuity and adds a toolchain.
- plotly: interactive output is wasted on a static journal figure.

**Snippet (skeleton):**

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
fig = plt.figure(figsize=(8.5, 11), dpi=300)
gs = GridSpec(3, 2, height_ratios=[1, 5, 5], hspace=0.4, wspace=0.3)
# header, panel A, panel B, panel C, panel D + footer
fig.savefig('graphical_abstract.pdf', bbox_inches='tight')
```

---

## 6. Estimated generation time

**~2 hours** total:
- Layout + typography pass: 30 min
- Source-figure preparation (extract relevant thumbnail crops with
  consistent colormap): 30 min
- matplotlib assembly (4 panels + header + footer + 3 callout
  boxes): 45 min
- Visual review + iteration (headline-number legibility; panel
  contrast against RSE column-width preview): 15 min

---

## 7. Caveat — do NOT generate yet

The user explicitly requested the **plan** first, before any visual
generation. After plan approval, the actual generation step lives in
the paper-writer's next session and must be reviewed against RSE's
graphical-abstract guidelines before submission.

When generation runs:
- Save canonical output as
  `01_WORKSPACE/papers/paper1_resolution_limits/figs/graphical_abstract.pdf`
  (vector) + `..._preview.png` (300 DPI raster for review).
- Cite the PDF in the manuscript §Graphical abstract caption.
- Update `figs/README.md` with a 1-line entry.
- Commit after the headline-number callout is verified against
  `transfer_summary.json` `aggregate.fp_per_1e4_km2` and
  `aggregate.fp_ci95_low` / `aggregate.fp_ci95_high` — do not hard-code.

---

*Claim-discipline check:* no number in this plan is invented; all
trace to `data/outputs/...` artifacts. "Detection" framing avoided.
"Calibration-context, NOT survey" appears twice. Tranquillitatis radar
conduit (Carrer 2024) anchor repeated.
