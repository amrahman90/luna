# Highlights — Paper 1 ("LLTB-1 calibrated benchmark")

> **Target journal:** *Remote Sensing of Environment* (primary).
> RSE requires 3–5 highlights, each ≤85 characters including spaces.
> Bulleted below; each line char-counted (Unicode code points; en-dash,
> superscripts ⁴/² count as one character) and verified ≤85 chars.
> Numbers trace to `01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json`
> (`aggregate` block), `data/candidate_registry.csv`, and
> `main.md` Abstract and §4.2 Table 2.

- LLTB-1 sets first-of-their-kind F1/P/R curves across LROC NAC GSD bands (0.5–10 m)
- Calibration-context row-based FP rate 3.74 [1.71, 7.10] per 10⁴ km², 24,062.96 km²
- 278 tier-C rows: 45 above-floor + 233 below-floor; 14 re-detections of known pits
- Tranquillitatis radar conduit (Carrer 2024) = Moon's sole instrumented subsurface
- Survey-grade lunar FP rate stays not measured; reported rate is calibration-context

---

## Provenance / source-file trail

| # | Highlight claim | Source |
|---|---|---|
| H1 | LLTB-1 per-rung F1/P/R curves; first-of-their-kind for the LROC NAC GSD band (0.5–10 m rungs) | `main.md` §1.3 contribution 2; §4.1 Table 1; `data/outputs/wp1_detector/sag_detect.py`; `~/lunarvoid/data/lltb1/<site>/sag/sag_summary.json` |
| H2 | Row-based calibration-context aggregate FP per 10⁴ km² = 3.74 [Poisson-exact 95% CI 1.71, 7.10] over 24,062.96 km² of 21 pit-associated DTMs (NOT survey) | `main.md` §4.2 Table 2 (aggregate row); `data/outputs/wp2_sag/transfer/transfer_summary.json` block `aggregate` |
| H3 | 278 tier-C morphometry rows; 45 above-floor; 233 below-floor preserved; all 14 above-floor true positives are re-detections of catalogued pits — zero novel candidates | `main.md` Abstract; §4.2; §5.2; `data/candidate_registry.csv` |
| H4 | Tranquillitatis radar conduit (Carrer 2024) = the only instrumented subsurface structure on the Moon evidenced by any instrument today | `main.md` Abstract; §1.1; §6 closing; References: Carrer et al. 2024 |
| H5 | Survey-grade lunar FP per 10⁴ km² stays NOT MEASURED; reported rate is calibration-context only (21 pit-associated DTMs; 30 random-mare control footprints have no NAC DTMs — atlas-level coverage gap) | `main.md` §2.2; §3.5; §5.4; §4.6 closing sentence; G2 report row 11 (NOT MEASURED) |

---

## Claim-discipline check

- All numbers traced to a CSV/JSON in `01_WORKSPACE/data/outputs/` or to
  `data/candidate_registry.csv`.
- No subsurface claim beyond the radar-evidenced Tranquillitatis conduit
  (Carrer 2024) — that anchor is repeated verbatim (H4).
- FP per 10⁴ km² always tagged **calibration-context, NOT survey**; H2 also
  marks the **row-based** definition (registry rows, not deduplicated
  features — 278 rows → 117 unique features; §5.4).
- "Detection" framing is avoided: H3 says **re-detections of known pits**
  (all 14 above-floor true positives re-find catalogued pits; zero novel
  candidates), never "inferred voids" or "detected voids".
- No coverage-fraction claim: the incorrect "82/278 rows have NAC coverage;
  226 do not" statement was removed from `main.md` §2.2 and §5.4 (post-A1
  fix); all 278 rows derive from the 21 processed DTMs, and the remaining
  coverage gap is atlas-level (~281 catalogued pits), stated as a scope
  limitation.

---

*Char-count verification (incl. spaces, Unicode code points; verified
2026-09-07 against the five bullet lines above):*

| # | Chars | Budget | Status |
|---|------:|-------:|--------|
| H1 | 83 | ≤85 | OK |
| H2 | 83 | ≤85 | OK |
| H3 | 82 | ≤85 | OK |
| H4 | 82 | ≤85 | OK |
| H5 | 84 | ≤85 | OK |
