# LUNARVOID — project overview (for cold outreach)

*One-pager, ~2-minute read. Send as PDF or paste as email body.*

**One-line thesis:** *We do not detect lava tubes. We infer them, with error bars.*

**LUNARVOID — calibrated inference of lunar lava-tube candidates from orbital morphometry + geophysics, anchored in a terrestrial-analog benchmark and a public research portal.**

## What I built

LUNARVOID is a 62-session solo research program that builds a calibrated multi-evidence framework for inferring candidate subsurface voids on the Moon, never detecting them. Frozen state (repo `Ahnaf181419/luna`):

- **Registry:** 278 rows (md5-pinned) over 24,063 km²; FP = **3.74 [1.71, 7.10] per 10⁴ km²** (Wilson 95% CI).
- **WP0.5 forward model (freshest):** three-regime analytical model + 2,880-row parameter sweep tying elastic flexure to NAC DTM detection floors; verified at seven anchors within ±5%. Result: intact basalt flexure is **3–5 orders of magnitude below the 4 m floor**; only near-collapse (d ≥ 0.6, L ≥ 300 m) is detectable. (`01_WORKSPACE/code/wp0_5_deflection/`.)
- **LLTB-1 analog benchmark:** detector-ladder benchmark on the Indian Tunnel analog; seven sites, byte-identical; best F1 0.362 (cliff edge).
- **LUNARVOID Portal:** five-tab public research surface (React 19 + Vite 8 + R3F); 67 tests green; not yet deployed.
- **Reproducibility:** 124 tests passing byte-identically; v02/v03/v04 verifier scripts PASS 21/21, 15/15, 11/11.

## What I'd want to discuss

I'm applying to European PhD programs (Sept 2027 intake; deadlines Dec 2026 / Jan 2027) and your group's recent work on **[Topic A — PLACEHOLDER; e.g., "PU learning under class-prior shift" / "conformal calibration of scientific ML" / "multi-modal fusion for earth observation"]** seems to align with the methodological questions LUNARVOID has surfaced. A few specific framings I'd value your view on:

1. **PU + conformal wrapping around a physics-informed forward model.** The WP0.5 result tells me *where* detection is plausible. Could a conformal wrapper around a PU-trained classifier give tiered inferences with per-tier coverage guarantees that survive physical-completeness tests, not only i.i.d. ones?
2. **Multi-modal fusion under 4-orders-of-magnitude scale gap.** LUNARVOID's fusion stack combines point samples, orbital rasters (~0.5 m), regional mosaics (~100 m), and global gravity (~300 m). The calibration discipline I want for this is general; I'd like to compare notes on how it is handled in your setting.

A brief reply would be welcome — a pointer to the most relevant paper from your group, a comment on whether this kind of test-bed would fit a prospective PhD project, or a redirect to a closer colleague.

## What I've shipped recently

The roof-deformation forward model (WP0.5), two weeks old: `01_WORKSPACE/code/wp0_5_deflection/{deflection_model.py, sweep.py, make_figure.py}`, plus the 2,880-row sweep CSV and the four-panel figure at `01_WORKSPACE/data/outputs/wp0_5_deflection/`. This closes the F1 critical finding ("the roof-sag amplitude was never estimated") and re-frames the targeting criterion for the rest of the project.

## What I want next

A PhD program whose methodological interest matches one of the framings above; an advisor who values reproducibility and open benchmarks as first-class research outputs. Not a request to be supervised by you specifically — just a question whether the framing fits.

## Links

- **Repo:** `github.com/amrahman90/luna` — full code, data, sweep CSVs, portal source
- **Roadmap:** `01_WORKSPACE/plans/2026-09-18_COMPREHENSIVE_Roadmap.md` (authoritative)
- **Portal (pending deploy):** `ahnaf181419.github.io/luna-web/`
- **arXiv preprint (planned):** "The Detectable Signal of Lunar Lava Tubes: A Three-Regime Roof-Deformation Forward Model"
- **Zenodo deposit:** staged at `01_WORKSPACE/data/zenodo_deposit_v1.0/` (10/10 CHECKSUMS verified; awaiting licence-confirmation step)
- **Author:** Ahnaf Shafin — `muhammad.ahnaf.sarker@gmail.com` (solo project, no PI)

---

*Honest state of play: paper is draft, not submitted; Zenodo deposit is staged, not yet executed; portal is built, not yet pushed. This is the calibration discipline applied to my own outreach.*
