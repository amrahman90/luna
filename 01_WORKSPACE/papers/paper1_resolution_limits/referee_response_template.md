# Referee-Response Template — Paper 1 v2.0 ("LLTB-1 calibrated benchmark")

**Status:** Regenerated 2026-09-09 (task A6a) to track Paper 1 **v2.0**
(`main.md`, commits `84f63ab` + `2449926`). This version supersedes the
v1.0-era template wholesale: the old stubs cited a registry-coverage
scope claim that was refuted and removed during the v2.0 IMRaD rewrite,
and turned registry rows and re-detections into candidate counts. Do not
resurrect v1.0 stub text; every response starts from Section 0 below.

**Use:** paste into a structured rebuttal document, one Sections A–C
block per referee comment. Section D is the fixed rebuttal structure for
every comment. Section E holds pre-drafted skeletons for the six
objections we anticipate; expand the `[...]` placeholders with
referee-specific text when the decision letter arrives.

---

## 0. Frozen v2.0 claim table (single source for every number quoted)

Any number in a response must come from this table verbatim — do not
paraphrase, re-round, or refresh from memory.

| # | Claim | v2.0 value | Manuscript anchor | Output artifact |
|---|---|---|---|---|
| 1 | Manuscript | IMRaD; 297 lines / 8,281 words; 8 references | whole manuscript | — |
| 2 | Analog scope | **four field sites / six map instances** (three instances sample the same trench-hosted tube; site-level independence = 4, not 6) | §2.1, §5.4 | — |
| 3 | Lunar scope | **21 DTM instances, 24,062.96 km²**; pit-associated by construction → *calibration-context, not survey* | §2.2, Table 2 | `data/outputs/wp2_sag/transfer/transfer_summary.json` |
| 4 | Registry | 278 morphometry rows → **117 unique features**; 45 above-floor rows = 14 TP + 9 FP + 21 ring + 1 funnel; **21 unique above-floor** | §2.2, §4.2, §5.4 | `data/candidate_registry.csv` |
| 5 | FP rate — frozen anchor | **row-based 3.74 [1.71, 7.10] per 10⁴ km²**, Garwood (Poisson-exact) 95% CI | Abstract, §4.2 Table 2, §6 | `transfer_summary.json` (`aggregate`) |
| 6 | FP rate — companion | **unique-feature 2.08 [0.67, 4.85] per 10⁴ km²** (30 m grouping key; stable 30–60 m; row-based regression reproduces 3.74 [1.71, 7.10]) | §5.4 pointer; companion data paper | `data/outputs/wp2_sag/unique_accounting_2026-09-07.json` |
| 7 | Outcome | **14 re-detections of catalogued pits; zero novel above-floor candidates** — the paper claims no new candidates | Abstract, §4.2, §5.2, §6 | `candidate_registry.csv` |
| 8 | Matching | 100 m radius (frozen-calibration convention); one borderline row at **138.1 m** disclosed (reclassifies as TP under 150 m) | §3.3 | — |
| 9 | TRANQPIT1 FPs | 3 FP rows = **two spatial structures** (pair co-located at 16.5 m + third at 132.8 m) | §4.2 | `unique_accounting_2026-09-07.json` |
| 10 | Detector | **LLTB-1 v0.5**; connected-component filter v0.2 validated standalone but NOT applied to frozen results | §3.2, Data availability | — |
| 11 | Validation honesty | leave-one-site-out **not performed**; four field sites; all per-rung results are within-site detectability, not transfer | §3.3, §5.4 | — |
| 12 | Data availability | registry + per-rung/per-arm summaries + methods + code available from authors / repository-on-request; analog dataset not redistributed (research/academic use) | Data availability | — |

**Banned v1.0-era phrasings (refuted or misleading — never reuse):**
- The refuted registry-coverage split ("82-of-226"-style NAC-coverage
  claim) in any form.
- Any phrasing that turns the 278 registry rows, or the 14 true
  positives, into a *candidate* count. Correct forms: "278 morphometry
  rows (117 unique features)"; "14 re-detections of catalogued pits";
  "zero novel above-floor candidates".
- "Detected a lava tube" or any detection framing of lunar subsurface
  structure. Only the Tranquillitatis radar conduit (Carrer et al.,
  2024) is instrument-evidenced.

---

## 1. Header (fill at receipt of decision letter)

- **Manuscript title:** Detectability limits for lava tube roof
  signatures in orbital topography: the LLTB-1 calibrated benchmark
- **Manuscript ID / submission round:** [fill]
- **Target journal:** *Remote Sensing of Environment* (primary) /
  *ISPRS Journal of Photogrammetry and Remote Sensing* (secondary)
- **Review round:** [1 / 2 / 3]
- **Date of response:** [YYYY-MM-DD]
- **Corresponding author:** LUNARVOID team — [corresponding.author@…]

---

## 2. Per-comment response scaffold

### Referee #N, Comment M: <one-line summary>

**Section A — Referee comment (verbatim)**

> [Paste verbatim from the referee report. Preserve original emphasis.]

**Section B — Our response**

[Free-text response built on the Section D moves. Quote numbers from the
Section 0 table only. Referee-specific material goes here: ...]

**Section C — Changes made in the manuscript**

- Manuscript location: [§, table, or figure; line numbers at proof stage]
- Before (verbatim): [paste old text]
- After (verbatim): [paste new text]
- Reason: [one sentence. If nothing changed, say so and why — the
  referee may be right but the change is out of scope, or would
  misstate a frozen result.]

---

## 3. Section D — rebuttal structure (use for every comment)

1. **Agree / disagree / partially agree.** State it explicitly, first.
2. **Evidence.** Quote the exact number from the Section 0 table and
   cite its output artifact path (`data/outputs/...`). Do not round
   favourably.
3. **Revision.** Manuscript location + before/after, or an explicit
   no-change statement with reason.
4. **Citation discipline.** New citations go through Zotero and the
   author-year References list (currently 8 entries).

Stylistic rules (project conventions):

- Framing for any lunar claim: **calibrated inference, never verified
  detection**. Write "inferred void candidate at confidence X", never
  "detected a lava tube".
- FP numbers always carry three labels: the accounting definition
  (row-based / unique-feature), the population (calibration-context,
  not survey), and the Garwood 95% CI.
- Limitations stay visible: LOO not performed; four sites; funnel and
  ring failure modes are findings, not shames.

---

## 4. Section E — anticipated objections and response skeletons

> Seeds. Expand with referee-specific `[...]` material when the comment
> arrives. Section/table anchors are to `main.md` v2.0.

### R1. "Single-calibration-context generalisability — thresholds were
tuned in-sample on essentially one trench-hosted tube."

**Skeleton.** We agree on the transfer limitation and state it as such
(§3.3, §5.4): the analog corpus is **four field sites / six map
instances**, three of which sample the same trench-hosted tube, so
site-level independence is four, not six; **leave-one-site-out
validation was not performed**, and every per-rung result is a
within-site detectability result, not a transfer result. Two protections
apply. First, degradation arms never re-tuned thresholds: the
calibration/test split was frozen from the baseline arm before any
degraded arm existed (§3.4). Second, the lunar side does not inherit
analog thresholds at all — every lunar score threshold uses an
amplitude floor anchored on the Mare Tranquillitatis pit calibration
anchor and frozen before any lunar product was evaluated (§3.5, Data
availability). LOO across the four sites is pre-committed before any
transfer-generalisation claim (§5.5). [If the referee requests LOO
within the revision window: state compute plan and whether the four-site
n supports it; do not promise transfer claims.]

### R2. "FP accounting ambiguity — is the rate per row or per physical
feature? Double-counting a depression at two rungs inflates it."

**Skeleton.** Both accountings exist and both are labelled. The frozen
anchor (Table 2, Abstract, §6) is **row-based: 3.74 [1.71, 7.10] per
10⁴ km²** (9 FP rows over 24,062.96 km², Garwood exact CI). The
registry now annotates rung duplicates: **278 rows → 117 unique
features; 45 above-floor rows → 21 unique features** (6 TP + 5 FP +
9 ring + 1 funnel), giving the companion **unique-feature rate 2.08
[0.67, 4.85] per 10⁴ km²** (30 m grouping key, stable across 30–60 m;
the row-based regression reproduces the frozen aggregate to numerical
precision). §5.4 discloses the row-based definition as an
upper-bound-style accounting, with the per-rung table the finest
granularity at which the definition is unambiguous; the full
unique-feature re-accounting table appears in the companion data paper.
Where one number is quoted, it is the row-based frozen anchor, labelled
"row-based". [Offer the both-accountings table as a supplementary
insert if the referee prefers it in this paper.]

### R3. "Zero novel candidates — so the detector found nothing new?"

**Skeleton.** Correct, and it is the result the paper is built to
report, not a failure of it. Paper 1 is a resolution-limits paper: the
lunar side measures how the frozen chain behaves where pits are known
(calibration-context), and the accounting is explicit — **14 above-floor
true positives, all re-detections of catalogued pits; zero novel
above-floor candidates** (§4.2, §5.2, §6). The informative quantities
are behavioural: the chain re-finds known pits, concentrates its 9 FP
rows at two pit-bearing sites (six at the Fecunditatis cluster,
amplitudes 155/140/34 m; three at Tranquillitatis, forming two spatial
structures — a 16.5 m pair and a third at 132.8 m), and produced
**zero false positives across 9,222.69 km² of added highland and
impact-melt terrain (21 new rows, every one below-floor)** (§4.2). At
the §1.1 base rate (~20 tube-relevant features among ~281 catalogued
pits), a novel single-method morphometric claim would be more likely a
false positive than a discovery; a novel candidate would require an
above-floor score at an uncatalogued location surviving visual
inspection and an independent evidence leg (§5.2). All lunar results
are calibrated inference, never verified detection.
[If the referee asks about the pending visual inspection of the 9 FP
rows: it is disclosed as pending in §5.4; no row can change status
before it.]

### R4. "DTM production gap — your lunar evaluation only covers where
published NAC DTMs already exist; the FP rate cannot be a survey rate."

**Skeleton.** Partially agree, and the paper says so before the referee
can. **All 21 evaluation DTM instances are published LROC NAC PDS
products (public domain), fetched by product ID** — none were produced
by us, so the lunar evaluation is reproducible from the public archive
alone (§2.2, Data availability). The suite is deliberately *not* a
survey sample: it is pit-associated by construction, and **every** lunar
rate is labelled calibration-context, never survey (§3.5, §4.2, §5.4).
The production gap is stated as a scope limitation: the 30 random-mare
control footprints from the project scope map have no existing NAC DTMs
at all; closing them requires alternative-sensor DTMs (Kaguya TC,
Chang'e) or new stereo processing, deferred to the companion data paper
(§2.2, §5.4). The survey-grade FP per 10⁴ km² therefore remains not
measured, and the manuscript states this. [If the referee demands
alternative-sensor closure in revision: out of scope for this paper;
would require a different pipeline — say so plainly.]

### R5. "Statistical rigour — nine false positives cannot support a
rate."

**Skeleton.** The smallness is handled, not hidden. All rates carry
**Poisson-exact (Garwood) 95% CIs**, the appropriate interval for small
FP counts: row-based **3.74 [1.71, 7.10]**, unique-feature **2.08
[0.67, 4.85]** per 10⁴ km². The concentration problem is disclosed
rather than averaged away: the single-site Tranquillitatis rate is
240.41 [49.58, 702.58] per 10⁴ km², and §4.2 states that the aggregate
fell from an earlier 6.06 [2.77, 11.51] to 3.74 **purely by denominator
growth** — the added 9,222.69 km² produced zero new false positives —
an improvement we explicitly refuse to claim as detector improvement.
§5.4 carries the formal limitation: a ±50% precision target on a 1%
FP-rate estimate needs ≈16,000 FP trials, roughly 40× the current
calibration-context population; the power analysis accompanies the
random-mare closure in the companion paper. Noise-floor verdicts rest
on 2 of ~649 mare DTMs with per-panel RMS spanning 0.74–2.05 m and are
labelled floor-sampling results, not survey-wide guarantees (§4.6).
[If the referee asks for bootstrap CIs: Garwood is exact for the
Poisson FP count; bootstrap adds no information at n = 9.]

### R6. "The TP/FP split hinges on a match radius you chose yourself —
the 138.1 m borderline row shows the fragility."

**Skeleton.** Agree that the split is definitional; that is why the
definition is frozen, disclosed, and stress-tested. Matching uses a
**100 m radius** (frozen-calibration convention), consistent with the
~30 m positional accuracy of the atlas labels; §3.3 discloses that one
Fecunditatis FP row lies at **138.1 m** from its nearest catalogued pit
and would reclassify as a true positive under a 150 m tolerance — a
single-row sensitivity we state rather than tune away. Definitional
sensitivity is also why both accountings are reported (R2): row-based
vs unique-feature, with the grouping key (30 m) and its stability band
(30–60 m) on record. At Tranquillitatis the FP geometry is likewise
disclosed at row level: the 3 FP rows are two spatial structures (a
pair co-located at 16.5 m and a third at 132.8 m), so per-row counts
there overstate structure counts — exactly the row-vs-feature
distillation of R2. [If the referee requests a radius-sweep table: the
30–60 m stability band already covers the grouping axis; a match-radius
sweep is a small, non-freezing addition — offer it as a supplement,
never as a re-tuned headline.]

---

*Claim-discipline check for this template: all numbers trace to
`main.md` v2.0 and the artifacts listed in Section 0; no registry-rows-
as-candidates phrasing; no novel-candidate claims; FP figures always
carry accounting definition + population label + Garwood CI.*
