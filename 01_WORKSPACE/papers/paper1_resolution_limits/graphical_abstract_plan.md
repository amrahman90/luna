# Graphical Abstract Plan — Paper 1 v2.0 ("LLTB-1 calibrated benchmark")

**Status:** Canonical panel spec for the v2.0 re-render of
`figs/fig_graphical_abstract.png` (1280×720). The PNG is being
re-rendered in parallel (task A6b); the renderer must match the panel
text strings in §3 exactly — this document is the single source for
panel content. Supersedes the v1.0-era plan, whose panel contents
carried refuted scope claims and unlabeled FP counts (see §5,
stale-content warning).

**Target journal:** *Remote Sensing of Environment* (primary).
**Claim discipline:** calibrated inference, never verified detection;
every FP figure carries its accounting definition and Garwood CI.

---

## 1. Layout (1280×720 PNG, 2×2 panel grid)

```
+------------------------------------------------------------------+
|  HEADER BAND (full width, ~90 px)                                 |
|  Title: "Detectability limits for lava tube roof signatures in    |
|  orbital topography"                                             |
|  Sub: "LLTB-1 calibrated benchmark · 21 NAC DTM instances ·      |
|  24,062.96 km²"                                                  |
+-------------------------------+----------------------------------+
|  PANEL A (top-left, ~48% w)    |  PANEL B (top-right, ~52% w)     |
|  Method chain (left→right      |  FP calibration result           |
|  boxes, 4 stages)              |  (headline number + labels)      |
+-------------------------------+----------------------------------+
|  PANEL C (bottom-left, ~48% w) |  PANEL D (bottom-right, ~52% w)  |
|  Outcome (re-detections +      |  Claim framing                   |
|  resolution limit)             |  (calibrated inference + v0.5)   |
+-------------------------------+----------------------------------+
|  FOOTER STRIP (full width, ~40 px): "calibrated inference, never  |
|  verified detection"                                            |
+------------------------------------------------------------------+
```

- Canvas 1280×720 px (matches the committed artifact; do not resize).
- Panels read left→right, top→bottom: method → result → outcome →
  framing.
- No panel mixes configurations: Panel B carries only the lunar
  calibration-context FP result; analog F1 numbers are deliberately
  absent (the graphic has one number to remember, and it is the FP
  rate, not an F1).

## 2. Panel contents

### Panel A — method chain
Four chained boxes, left to right, arrow-connected:
`NAC DTM` → `Planchon–Darboux fill` → `multi-rung sag detection` →
`calibration`. Micro-caption under the chain: "detector: depth ×
vesselness, rungs 0.5–10 m". Visual: reuse manuscript figure language
(colormap, scale-bar style) from `figs/fig_wp0_transqpit1_depth_check.png`
and `figs/fig_ladder_sensor_preview.png`; do not reproduce any figure
verbatim.

### Panel B — FP calibration result (headline)
- Big number: **"3.74 [1.71, 7.10] per 10⁴ km²"**
- Definition label (must sit directly under the number, same weight as
  the number is large): **"row-based"**
- Companion line (small): **"unique-feature: 2.08 [0.67, 4.85]"**
- Population strip: **"21 DTM instances · 24,062.96 km² ·
  calibration-context, not survey"**
- CI tag (small): **"Garwood exact 95% CI"**

### Panel C — outcome
Two stacked statement lines + resolution-limit pair:
- **"14 catalogued pits re-detected"**
- **"zero novel above-floor candidates"**
- Resolution limit (small callout): **"single-DTM limit: sag A ≥ 5 m
  (≥ 4 m at quieter site)"** and **"1–2 m sags → multi-evidence
  stacking"**

### Panel D — claim framing
- Banner phrase: **"Calibrated inference, not detection"**
- Tool line: **"detector: LLTB-1 v0.5"**
- Anchor line (small): **"only instrument-evidenced conduit:
  Tranquillitatis (Carrer 2024)"**

## 3. Exact panel text strings (verbatim; renderer copies these)

| Slot | String |
|---|---|
| Header title | `Detectability limits for lava tube roof signatures in orbital topography` |
| Header sub | `LLTB-1 calibrated benchmark · 21 NAC DTM instances · 24,062.96 km²` |
| A box 1 | `NAC DTM` |
| A box 2 | `Planchon–Darboux fill` |
| A box 3 | `multi-rung sag detection` |
| A box 4 | `calibration` |
| A micro-caption | `detector: depth × vesselness, rungs 0.5–10 m` |
| B headline | `3.74 [1.71, 7.10] per 10⁴ km²` |
| B label | `row-based` |
| B companion | `unique-feature: 2.08 [0.67, 4.85]` |
| B population | `21 DTM instances · 24,062.96 km² · calibration-context, not survey` |
| B CI tag | `Garwood exact 95% CI` |
| C line 1 | `14 catalogued pits re-detected` |
| C line 2 | `zero novel above-floor candidates` |
| C limit 1 | `single-DTM limit: sag A ≥ 5 m (≥ 4 m at quieter site)` |
| C limit 2 | `1–2 m sags → multi-evidence stacking` |
| D banner | `Calibrated inference, not detection` |
| D tool | `detector: LLTB-1 v0.5` |
| D anchor | `only instrument-evidenced conduit: Tranquillitatis (Carrer 2024)` |
| Footer | `calibrated inference, never verified detection` |

Number provenance (do not hard-code in the generator without a
verification pull): row-based rate + area from
`data/outputs/wp2_sag/transfer/transfer_summary.json` (`aggregate`);
unique-feature companion from
`data/outputs/wp2_sag/unique_accounting_2026-09-07.json`
(`unique_b1_key`); resolution-limit strings from `main.md` §4.6
(A ≥ 5 m at both floor-sampling sites; A ≥ 4 m at the quieter site;
1–2 m not single-DTM detectable).

## 4. Typography and color (unchanged guidance from v1 plan)

- Serif for title (DejaVu Serif / STIX); sans (DejaVu Sans) for
  numerical callouts. Headline number ≥ 48 pt at print scale.
- Muted palette: white/very-light-grey background (#F7F7F7); pipeline
  arrows dark slate (#2E4053); headline callout muted ochre (#B7791F);
  limitation/caveat text muted brick (#9B2C2C); grid lines light grey
  (#D1D5DB). Colormap continuity with manuscript figs (viridis/cividis).
- No gradients on text, drop shadows, glow, or 3D bevels.

## 5. Stale-content warning (v1.0-plan content REMOVED — never restore)

The v1.0 plan's panel contents contradicted Paper 1 v2.0. Removed:

1. **The refuted "82-of-226" NAC-coverage scope claim** and the
   limitation text built on it ("226 of 278 registry rows lack NAC
   coverage") — the v2.0 scope is four sites / six map instances
   (analog) and 21 DTM instances / 24,062.96 km² (lunar); all 278
   registry rows derive from the 21 processed DTMs.
2. **Any bare "14-candidate"-style claim.** The 14 are re-detections
   of catalogued pits; the paper claims zero novel candidates. Panel C
   wording above is the only permitted form.
3. **Unlabeled FP counts.** The old headline "aggregate lunar FP,
   calibration-context, NOT survey" carried no accounting definition;
   every FP figure now carries the "row-based" label (with the
   unique-feature companion shown), the population label, and the
   Garwood CI.
4. **"6 analog sites × 5 GSD rungs = 30 cells"** (old Panel A caption)
   — wrong scope; v2.0 states four field sites / six map instances,
   and the graphical abstract no longer shows the analog grid at all.
5. **Internal scaffolding in panel captions**: Cycles 1-2 narrative,
   "$0 spent" budget text, and the calibration-file md5 string —
   stripped from the v2.0 manuscript into Data Availability and out of
   the graphic.
6. **"278 tier-C rows" as a numbers overlay** — registry rows are
   morphometry rows, not candidate objects; the graphic now shows only
   the evaluation extent (21 instances / 24,062.96 km²).

## 6. Verification checklist before commit

1. Strings: renderer output matches §3 exactly (diff the strings).
2. Banned-string grep over the generator script AND this plan: search
   for the three literals listed in §5 items 1–2 plus the rows-as-
   candidates phrasing (the slash form of the coverage split, the bare
   "278" + candidate-noun phrase, and the bare "14" + candidate-noun
   phrase) → all must return nothing. The §5 wording above is
   deliberately hyphenated so this document passes its own check.
3. Numbers: pull both rates from the two JSONs listed in §3 and assert
   equality with the rendered text (use
   `~/lunarvoid/venv/bin/python`).
4. Dimensions: PNG is 1280×720 (`PIL.Image.open(...).size`).
5. Claim discipline: no "detection" framing of subsurface structure
   anywhere in the graphic; the only instrument-evidenced conduit is
   the Tranquillitatis radar conduit.
