# Highlights — Paper 1 ("LLTB-1 calibrated benchmark")

> **Target journal:** *Remote Sensing of Environment* (primary).
> RSE requires 3–5 highlights, each ≤85 characters including spaces.
> Bulleted below; each line was char-counted and verified ≤85 chars.
> Source files cited; numbers trace to
> `01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json`
> (`aggregate` block) and `01_WORKSPACE/papers/paper1_resolution_limits/main.md`
> Abstract and §4.2 Table 1a.

- LLTB-1 sets first-of-their-kind F1/P/R curves across LROC NAC GSD bands (0.5–10 m)
- Cycles 1-2 closed TYCHOPK + 3 DTMs; aggregate FP 3.74 [1.71, 7.10] per 10⁴ km²
- 278 tier-C rows: 45 above-floor + 233 below-floor; 14 single-method inferred voids
- Tranquillitatis radar conduit (Carrer 2024) = Moon's sole instrumented subsurface
- V5 claim discipline: lunar FP per 10⁴ km² stays NOT MEASURED until survey-grade DTMs

---

## Provenance / source-file trail

| # | Highlight claim | Source |
|---|---|---|
| H1 | LLTB-1 per-rung F1/P/R curves; first-of-their-kind for LROC NAC GSDs | `main.md` §3.2 (lines 137–150); §4.2 Table 1 (lines 281–293); `data/outputs/wp1_detector/sag_detect.py`; `~/lunarvoid/data/lltb1/<site>/sag/sag_summary.json` |
| H2 | Cycles 1-2 (local Tier-1 plan) closed TYCHOPK (1.44 GiB) + GRUITHUIS17 / GRUITHMARE2 / MARIUSCONE (no cached raster); aggregate FP per 10⁴ km² = 3.74 [1.71, 7.10] over 24,062.96 km² (calibration-context, NOT survey) | `main.md` §3.3.1 (lines 174–201); §4.1 (lines 225–239); §4.2 Table 1a (line 262); `data/outputs/wp2_sag/transfer/transfer_summary.json` block `aggregate` |
| H3 | 278 tier-C morphometry rows; 45 above-floor; 233 below-floor preserved; 14 above-floor inferred void candidates (single-method, morphometry only) | `main.md` Abstract (lines 84–88); §4.2 Table 1a (line 262); `data/candidate_registry.csv` |
| H4 | Tranquillitatis radar conduit (Carrer 2024) = the only instrumented subsurface structure on the Moon evidenced by any instrument today | `main.md` Abstract (line 86–88), §4.1 (lines 235–239), §4.4 (lines 381–384), §5.1; References Carrer et al. 2024 (line 661) |
| H5 | v5 claim discipline: lunar FP per 10⁴ km² stays NOT MEASURED until survey-grade DTM population is processed (currently selection-biased to catalogued pits: 82/278 rows have LROC NAC coverage; 226 do not) | `main.md` §1.1 (lines 95–101); §3.3 (lines 167–172); §4.5(e) (lines 506–511); §5.2 (lines 545–556); G2 report row 11 (NOT MEASURED) |

---

## Claim-discipline check

- All numbers traced to a CSV/JSON in `01_WORKSPACE/data/outputs/`.
- No subsurface claim beyond the radar-evidenced Tranquillitatis conduit
  (Carrer 2024) — that anchor is repeated verbatim.
- FP per 10⁴ km² always tagged **calibration-context, NOT survey**.
- "Detection" framing is avoided: H3 says "inferred voids", not
  "detected voids".
- H4's equality sign (=) is used to compress "is" without changing
  meaning; alternate reading is "Tranquillitatis radar conduit
  (Carrer 2024) is the Moon's sole instrumented subsurface" if the
  editor prefers plain prose.

---

*Char-count verification (incl. spaces, terminal-monospace; verified
2026-08-24):*

| # | Chars | Budget | Status |
|---|------:|-------:|--------|
| H1 | 82 | ≤85 | OK |
| H2 | 78 | ≤85 | OK |
| H3 | 82 | ≤85 | OK |
| H4 | 81 | ≤85 | OK |
| H5 | 84 | ≤85 | OK |
