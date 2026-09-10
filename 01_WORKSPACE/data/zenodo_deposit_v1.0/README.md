# LUNARVOID annotated test-bed registry + evaluation protocol — Zenodo deposit v1.0.0 (STAGED, NOT YET UPLOADED)

## What this is

This is the versioned release promised as deliverable **E3** by Paper 2
(v3.1-draft, "An annotated test-bed registry and leakage-corrected
evaluation protocol for lunar void-candidate inference from meter-scale
orbital terrain data"). Framing per the D4 reframe: an **annotated
test-bed registry + leakage-corrected evaluation protocol + honest
baselines** — calibration-context, *not* a survey catalogue, and
explicitly *not* a claim of lava-tube detection. "Benchmark" is the
forward-looking, community-adoption goal; until then this is a test-bed.

Contents in numbers (frozen 2026-08-23 G2 transfer + 2026-09-07/09
re-accountings): 278 candidate rows over 21 LROC NAC DTMs
(24,062.96 km², pit-associated/pit-rich sites); 161 SUPERSEDED
duplicate rows with explicit `superseded_by` links (117 unique
features); row labels 14 TP / 9 FP / 21 ring / 1 funnel among 45
above-floor rows + 233 explicitly not-inferable below-floor rows;
unique-feature accounting 6 TP / 5 FP / 9 ring / 1 funnel of 21. FP
rates (calibration-context, never survey rates): row-based 3.74
[Poisson-exact Garwood 95% CI 1.71, 7.10], unique-feature 2.08
[0.67, 4.85] per 10⁴ km². Leakage-corrected PU-learning baseline:
leave-one-DTM-out pooled out-of-fold F1 0.824 [DTM-cluster bootstrap
95% CI 0.35, 0.98], AUC 0.930 [0.49, 1.00].

The deposited registry snapshot is the one identified in Paper 2 by
md5 `a60fb52152e33f37e9052434ad026a6e` (sha-256 in CHECKSUMS.sha256).

## Version

v1.0.0 (first public staging; corresponds to the frozen G2 registry +
D1 group-split evaluation, 2026-09-09).

## Structure

```
deposit/
├── candidate_registry.csv                  # THE registry: 32-line header/schema
│                                           #   + provenance line + 278 data rows
├── METHODS.md                              # WP2 sag-detector transfer methods log
│                                           #   (calibration freeze, audit table)
├── PROVENANCE_INDEX.md                     # per-output provenance sidecar
│                                           #   (sha-256, producer, inputs, status)
├── pu_learning_groupsplit.py               # D1 leak-free PU eval (LODO folds,
│                                           #   duplicate exclusion, cluster
│                                           #   bootstrap, identity-proxy ablation)
├── unique_accounting.py                    # A2a unique-feature FP re-accounting
│                                           #   (30 m atlas-accuracy grouping)
├── repair_registry_v1.py                   # B1 registry parse/dedupe repair tool
├── build_provenance_index.py               # B4 provenance sidecar generator
├── transfer_summary.json                   # frozen G2 per-DTM transfer results
├── unique_accounting_2026-09-07.json       # frozen unique-feature accounting
└── pu_learning_groupsplit_2026-09-09.json  # frozen D1 evaluation (run A/B)
```

## Regenerating the derived artifacts

Scripts are plain runnable scripts (no package; ADR D6). Canonical
invocation convention — `PYTHONPATH` prefix pointing at the code root,
project venv python, run from the repository root (`01_WORKSPACE/` as
CWD):

```bash
PYTHONPATH=01_WORKSPACE/code /home/frostflux/lunarvoid/venv/bin/python \
  01_WORKSPACE/code/tools/repair_registry_v1.py            # argparse: --registry/--backup/--report (defaults = repo paths)

PYTHONPATH=01_WORKSPACE/code /home/frostflux/lunarvoid/venv/bin/python \
  01_WORKSPACE/code/wp2_sag/transfer/unique_accounting.py  # fixed paths, deterministic re-count

PYTHONPATH=01_WORKSPACE/code /home/frostflux/lunarvoid/venv/bin/python \
  01_WORKSPACE/code/wp5_fusion/pu_learning_groupsplit.py   # fixed paths, seeds fixed at 42

PYTHONPATH=01_WORKSPACE/code /home/frostflux/lunarvoid/venv/bin/python \
  01_WORKSPACE/code/tools/build_provenance_index.py        # regenerates PROVENANCE_INDEX.md
```

Dependencies: see the repository's `code/setup/requirements.txt` freeze
(geopandas, rasterio, scikit-learn, pulearn, numpy, ...). Underlying
LROC NAC DTMs are **not** redistributed (fetch by product ID from the
PDS LROC RDR archive; SHA-256s in the project MANIFEST) —
`transfer_summary.json` cannot be regenerated without them.

## Licence — PENDING USER CONFIRMATION

- Registry, methods/provenance docs, summary JSONs: **CC-BY-4.0**
  (recommended; `[USER]` confirm).
- The four `.py` scripts: **MIT** (recommended; `[USER]` confirm).
- Record-level Zenodo licence field: cc-by-4.0 with the scripts' MIT
  stated here (mixed licence; standard practice).
- All derived values trace to PDS public-domain inputs (LROC NAC DTMs;
  LROC `LUNAR_PIT_LOCATIONS` pit atlas). No ASU web-product terms
  attach (PDS archive product only — see the project licence-audit
  memo, `notes/2026-09-12_E3_licence_audit.md`). NASA analog LiDAR
  (research/academic use only) is NOT included and was not used for
  these artifacts.

## Required citations / acknowledgements (carried with the data)

- Lunar Pit Atlas catalogue: **Wagner, R. V. & Robinson, M. S.
  (2021), LPSC 52, Abstract #2530**; data via NASA LRO LROC PDS
  archive (public domain).
- NAC DTMs: NASA LRO LROC team, PDS RDR archive.
- Confusion-layer distances: **Hurwitz, D. M., Head, J. W. & Hiesinger,
  H. (2013), PSS 79-80, 1-38** (sinuous rilles); **La Grassa et al.
  2024/2025** LU5M812TGT crater catalogue (CC-BY-4.0,
  doi:10.5281/zenodo.13990480).
- Detector lineage: LLTB-1 **v0.5.1** (release note 2026-09-11; CC
  filter `--cc-filter {off,on,auto}`, default off — registry rows were
  produced by the frozen G2 v0.5-parity pipeline).

## Citation of this deposit

DOI will be minted on deposit (Zenodo, versioned). Until then:

> LUNARVOID team (2026): An annotated test-bed registry and
> leakage-corrected evaluation protocol for lunar void-candidate
> inference from meter-scale orbital terrain data, v1.0.0, Zenodo,
> DOI pending.
