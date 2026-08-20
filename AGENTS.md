# AGENTS.md — Project Rules for LUNARVOID (Lunar Lava Tube Research)

These rules apply to every agent session in this project, automatically.
They were set by the user on 2026-08-19 and are permanent until the user
explicitly changes them.

## Directory layout

```
Lunar_LavaTube/
├── AGENTS.md                <- this rules file
├── opencode.json            <- hard permission enforcement of the rules below
├── 00_SOURCE_ORIGINALS/     <- READ-ONLY archive (never touch)
└── 01_WORKSPACE/            <- ALL new and future work goes here
    ├── plans/               <- new plan versions, roadmaps, gate reports
    ├── notes/               <- working notes, literature/prior-art matrix
    ├── code/                <- scripts, pipelines (WP0+ deliverables)
    ├── data/                <- dataset indexes, download manifests (never raw mirrors)
    ├── papers/              <- paper drafts, figures, submission material
    └── admin/               <- budgets, logs, infrastructure records
```

## Rules (non-negotiable)

1. **`00_SOURCE_ORIGINALS/` is a read-only archive.** NEVER create, edit,
   move, rename, or delete any file inside it. Reading/referencing it is
   encouraged — that is its purpose. This is also enforced by edit/write
   permission denial in `opencode.json`.

2. **Every new file goes in `01_WORKSPACE/`** (in the appropriate
   subfolder). Never place new documents, scripts, or scratch files in the
   project root. The project root stays clean: rules file, config, the two
   folders — nothing else.

3. **`AGENTS.md` is the rules file.** Modify it ONLY when the user
   explicitly requests a rule change. Do not add, soften, or remove rules
   on your own initiative.

4. **Source of truth:** `00_SOURCE_ORIGINALS/LUNARVOID_Master_Plan_v5_Full_Synthesis.txt`
   is the authoritative master plan. Any newer plan versions live in
   `01_WORKSPACE/plans/` and must state which version they supersede.

## Project context (read before working)

- Project: LUNARVOID — calibrated multi-evidence inference of lunar lava
  tubes from orbital morphometry + geophysics, anchored in terrestrial
  analogs. Core thesis: "We do not detect lava tubes. We infer them, with
  error bars."
- Key documents (all in `00_SOURCE_ORIGINALS/`): the v5 master plan
  (authoritative), v3/v4 plan iterations, v1 research plan, feasibility &
  novelty analysis, dataset assessment, VPS/infrastructure guide.
- Plan status: ~M0 (planning complete, execution not started). First steps
  are WP0: prior-art matrix, Tier-0 environment, index-layer intersection
  scope map, one reproduced NAC DTM at Mare Tranquillitatis Pit.
- Budget discipline: total compute ceiling ~$800 over 30 months; Tier-0
  first, GPU hourly only, Tier-1 bursts only.
- Data discipline: never mirror LROC archives (fetch by product ID only);
  NASA analog dataset is research/academic use only; ISRO acknowledgement
  mandatory. Audit licences before any redistribution.
- Claim discipline: calibrated inference, never verified detection; report
  FP per 10^4 km^2; nothing subsurface on the Moon is verifiable today
  except the radar-evidenced Tranquillitatis conduit.
