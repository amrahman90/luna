# E3 licence audit — Zenodo deposit preparation (PRE-UPLOAD, user-gated)

**Date:** 2026-09-12 · **Author:** archivist (E3 prep dispatch)
**Scope:** What may be redistributed in the planned versioned-DOI Zenodo
deposit promised by Paper 2 v3.1 (§ Data availability, "Planned versioned
release (E3)"), and under what terms. Upload itself is user-gated
(Zenodo token/decision pending). This memo discharges the licence-audit
obligation the paper states as a precondition.

---

## 1. Pit-atlas provenance — the ASU web-vs-PDS question, resolved

Paper 2 (Data availability) flags: "PDS *archive* products are public
domain, but LROC/ASU *web*-product terms differ from the PDS archive
(MANIFEST licence note) — because the registry's labels are
Pit-Atlas-derived, an explicit ASU-terms audit of the label source is
required before the E3 deposit redistributes them."

**Resolution.** The "pit atlas" consumed by this project is **not** the
ASU/LROC interactive web atlas (`lroc.im-ldi.com/atlases/pits`, a browse
product under ASU web terms). It is the machine-readable
**`LUNAR_PIT_LOCATIONS` shapefile (278 pits)** fetched from the **PDS
LROC RDR archive**:

- URL: `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/EXTRAS/SHAPEFILE/LUNAR_PIT_LOCATIONS/LUNAR_PIT_LOCATIONS_180.ZIP`
- MANIFEST row (Index layers, 2026-08-19): SHA-256
  `b0d2e0123026979fae5b2865049900e7bcc3b2767ca31a36413423fdcae365bb`,
  licence **"PDS public domain"**.
- MANIFEST note (line 302) — "LROC *web* products (quickmap, previews):
  ASU terms differ from PDS archive" — applies to quickmap/previews we
  did **not** ingest; no pipeline step scraped the ASU web atlas.

PDS products are U.S. Government works — public domain, no
redistribution restriction; customary acknowledgement requested.
**Catalogue citation (mandatory-attribution-by-courtesy, no legal
barrier):**

- Wagner, R. V. & Robinson, M. S. (2021), *LPSC 52*, Abstract #2530 —
  the pit catalogue itself (per dataset assessment ref [6]).
- Wagner & Robinson (2014), Icarus — PitScan lineage (ref [5]/[7] of
  `00_SOURCE_ORIGINALS/Lunar_LavaTube_Detection_Dataset_Assessment.txt`).
- Wagner & Robinson (2022), JGR Planets, doi:10.1029/2022JE007328 — pit
  interior morphology (not ingested; context cite only).

**Verdict:** atlas-derived label strings in our deposit are derived from
a public-domain PDS product; the ASU web-terms caveat does **not**
attach to them. Redistribute with the W&R 2021 citation + LROC/PDS
acknowledgement in the deposit README.

## 2. Per-artifact audit table

Legend — "our layer": what LUNARVOID added on top of the source.

| Artifact (deposit path) | Source data | Source licence | Our layer | Redistributable? | Recommended licence |
|---|---|---|---|---|---|
| `candidate_registry.csv` — measurement columns (`candidate_id, lon, lat, dtm, span_m, sag_amp_m, score`) | Values computed by LUNARVOID code (G2-frozen sag pipeline, LLTB-1 lineage) from LROC NAC DTMs | NAC DTMs: **PDS public domain** (MANIFEST DTM rows, all SHA-256'd) | the derived numbers themselves (no DTM pixels copied) | **YES** — derived measurements from public-domain inputs | CC-BY-4.0 `[USER]` |
| `candidate_registry.csv` — annotation columns (`methods, tier, status, first_found, updated, evidence, notes` = TP/FP/ring/funnel labels, `superseded_by` links, failure-mode flags) | none (ours) | n/a | entirely ours (skeptic-audited) | **YES** | CC-BY-4.0 `[USER]` |
| `candidate_registry.csv` — atlas-derived strings (notes referencing catalogued pits: ring-artefact labels, TP-by-100 m-match, "nearest catalogued pit" distances) | PDS `LUNAR_PIT_LOCATIONS` shapefile (§1) | **PDS public domain** | match labels computed by our spatial join (≥30 m atlas-accuracy rule) | **YES** — cite Wagner & Robinson 2021 + LROC/PDS acknowledgement | CC-BY-4.0 `[USER]` |
| `candidate_registry.csv` — `confusion` field (`rille=\|chain=\|ridge=\|graben=` + distance) | distances to nearest feature, computed by `code/wp2_sag/confusion_layer.py` from: Hurwitz 2013 sinuous-rille shapefile; LU5M812TGT crater catalogue (chains + near-pit rims); graben class = 0 cells in v0.1 (dropped, C15-3) | Hurwitz: **no explicit licence** (MANIFEST: "cite Hurwitz, Head & Hiesinger 2013, PSS 79-80"); LU5M812TGT: **CC-BY-4.0** (Zenodo, doi:10.5281/zenodo.13990480) | scalar distances = computed geometric facts; underlying shapefiles/catalogue NOT included in deposit | **YES** — facts, not expression; citation obligations attach: Hurwitz et al. 2013 + La Grassa et al. (LU5M812TGT) | CC-BY-4.0 `[USER]` |
| `METHODS.md` (wp2_sag/transfer methods log, 943 lines) | internal audit record of our own code edits | n/a | ours | **YES** | CC-BY-4.0 `[USER]` |
| `PROVENANCE_INDEX.md` (output-artifact provenance sidecar, 186 lines) | generated from our outputs by our `build_provenance_index.py` | n/a | ours | **YES** | CC-BY-4.0 `[USER]` |
| `pu_learning_groupsplit.py` (1489 lines) | ours (D1 leak-free PU eval; no third-party code embedded) | n/a | ours | **YES** | **MIT** `[USER]` |
| `unique_accounting.py` (506 lines) | ours (A2a unique-feature re-accounting) | n/a | ours | **YES** | **MIT** `[USER]` |
| `repair_registry_v1.py` (335 lines) | ours (B1 registry parse/dedupe repair) | n/a | ours | **YES** | **MIT** `[USER]` |
| `build_provenance_index.py` (262 lines) | ours (B4 sidecar generator) | n/a | ours | **YES** | **MIT** `[USER]` |
| `transfer_summary.json` (1964 lines) | per-DTM transfer results from PDS DTMs + our code; label matches vs PDS atlas | PDS public domain (inputs) | our results | **YES** | CC-BY-4.0 `[USER]` |
| `unique_accounting_2026-09-07.json` (1892 lines) | registry (above) + our code | see registry rows | our results | **YES** | CC-BY-4.0 `[USER]` |
| `pu_learning_groupsplit_2026-09-09.json` (5848 lines) | registry features (above) + our code | see registry rows | our results | **YES** | CC-BY-4.0 `[USER]` |

Net: **every deposit-eligible artifact is redistributable.** No deposit
file carries ASU web terms, NASA analog-dataset (research/academic-only)
material, or ISRO-gated data. The mixed-licence reality (data CC-BY-4.0 /
code MIT) is normal for Zenodo; the record-level licence field should
carry CC-BY-4.0 with the scripts' MIT stated in the README.

## 3. Exclusions (confirmed NOT in the deposit)

- Anything under `00_SOURCE_ORIGINALS/` (read-only archive; master plan
  and prior-plan versions are ours to cite, not to re-publish here).
- Raw rasters / LROC archives — never mirrored (fetch-by-product-ID
  discipline); DTMs stay out.
- Analog LiDAR vault (`~/lunarvoid/data/lltb1/`, NASA Planetary Pits and
  Caves, **research/academic use only** — hard no-redistribution).
- The vault, the R1 roadmap draft (untracked), the R1 draft paper.
- Any `[USER]`-flagged unresolved item (§5) — none currently blocks
  file inclusion; they block *upload*, which is user-gated anyway.

## 4. ADR D6 trigger note (scripts-not-package)

ADR D6 (decisions/D6) defers packaging until: (1) first external user,
(2) **Zenodo release with a `pip install`-able citation target**, or
(3) CI that can't tolerate CWD-sensitive imports. **A code-inclusive
E3 deposit fires this trigger set**: it is a Zenodo code release, i.e.
the first external-facing code artifact. Per ADJ-1 (v2 audit plan),
the scripts-form release was judged acceptable — plain runnable
scripts with the documented `PYTHONPATH=01_WORKSPACE/code` invocation
convention — so **packaging remains optional**: v1.0 ships
scripts-as-is, no `pyproject.toml` added, and D6 stands with trigger
(2) now engaged in its scripts-release form. Optional `[USER]`: amend
D6's trigger-2 wording to "Zenodo code release (pip-installable OR
scripts form)" for precision, or record this memo as the engagement
note.

## 5. `[USER]` decisions needed before upload

1. Confirm **CC-BY-4.0** for registry/docs/JSONs and **MIT** for the 4
   scripts (recommendation above).
2. Confirm **creator list + affiliations** for `zenodo_metadata.json`
   (currently placeholder "LUNARVOID team").
3. Zenodo token + upload go/no-go (the gate this prep respects).
4. (Optional) D6 wording amendment (§4).
5. (Minor) Confirm citation line for the confusion layer: Hurwitz et
   al. 2013 + La Grassa et al. LU5M812TGT — recommended text is in the
   deposit README.

## 6. Staging note (permission gap)

The dispatch approved a staging dir `data/zenodo_deposit_v1.0/`, but
`opencode.json` edit rules currently allow archivist writes only under
`admin/**`, `notes/**`, `plans/**`, `data/MANIFEST.md`, and the
knowledge/vault dirs — no zenodo path. The package is therefore staged
at **`01_WORKSPACE/admin/zenodo_deposit_v1.0_staging/`** (archivist's
allowed area), structured exactly as the final deposit; moving it to
`01_WORKSPACE/data/zenodo_deposit_v1.0/` is a one-step `mv` once the
permission is added (or performed by the user). No bookkeeping commit
made in this dispatch (E3 prep only; upload user-gated).
