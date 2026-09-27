# LUNARVOID — Comprehensive End-to-End Roadmap

> **Authoritative consolidation of all plans, roadmaps, gate reports,
> papers, portal phases, and aspirations as of 2026-09-18.**
>
> **Supersedes (as the live top-level roadmap):**
> `plans/2026-08-19_ZEROCOST_Roadmap.md` (zero-cost execution sequence),
> `plans/2026-08-21_R1_Roadmap_draft.md` (draft, never committed),
> `plans/2026-09-12_R3_Status_Report.md` (terminal status at HEAD `c5be2a2`).
>
> **Does NOT supersede (still authoritative in their domain):**
> `00_SOURCE_ORIGINALS/LUNARVOID_Master_Plan_v5_Full_Synthesis.txt`
> (research thesis + evidence hierarchy + cost model),
> `luna-web/docs/ROADMAP.md` (portal phase ledger; same author intent as
> below but lives in the submodule).
>
> **Status:** LUNARVOID research has reached natural completion point
> (R3 §11 terminal). LUNARVOID Portal Phase 4 COMPLETE, not yet
> published. All remaining work is user-gated, paper-submission, or
> future-aspirational. This roadmap is the canonical map of every
> aspect, interest, and thing we want to do — past, present, future.
>
> **Convention:** prefixes — `[✓]` done, `[~]` in-progress/deferred, `[ ]` open.

---

## 0. ONE-LINE THESIS

> **We do not detect lava tubes. We infer them, with error bars.**

LUNARVOID calibrates morphometric + geophysical + thermal evidence into
FP-bounded candidate tiers (FP per 10⁴ km²), anchored in a $0/$800
frugal-compute record, an LROC NAC-DTM + Diviner + GRAIL pipeline, and
a terrestrial-analog LLTB-1 benchmark. The public surface is a
production-quality React portal; the underlying science is reproducible
byte-identically from this repository.

---

## 1. THE TWO PILLARS

```
┌────────────────────────────────────────────────────────────────────┐
│  PILLAR A — LUNARVOID RESEARCH                          $0 / $800  │
│  Calibrated multi-evidence inference of lunar lava tubes           │
│  Drives: gates G0′ / G1 / G2 / G3; Papers 1 + 2; registry; budget │
│  Output: candidate registry (278 rows, tier C, FP 3.74/10⁴ km²)   │
├────────────────────────────────────────────────────────────────────┤
│  PILLAR B — LUNARVOID PORTAL (luna-web)                  ~$0       │
│  Public research-program portal (React 19 + Vite 8 + R3F)          │
│  Drives: 5-tab SPA, deploy to https://ahnaf181419.github.io/luna-web/
│  State: Phase 4 COMPLETE (17/17 plans, 67 tests); NOT YET PUSHED  │
└────────────────────────────────────────────────────────────────────┘
```

Both pillars share:
- **Thesis** ("inferences, not detections", FP per 10⁴ km²).
- **Frugal compute** ($0 spent across 62 research sessions; portal runs on local + GH Pages).
- **Data discipline** (no LROC mirroring; fetch by product ID; NASA analog research-only).
- **Claim discipline** (verifier + skeptic on every paper-claim + gate).
- **Reproducibility** (byte-identical test pins, frozen registry md5, versioned commits).
- **Author identity** `Ahnaf181419 <muhammad.ahnaf.sarker@gmail.com>` (normalised via `.mailmap`).

The repo holds BOTH: research artifacts in `01_WORKSPACE/` (read-only
provenance in `00_SOURCE_ORIGINALS/`); portal source in `luna-web/`
(submodule). Remote is `https://github.com/amrahman90/luna.git`. The
original LUNARVOID work (sessions 1–66) is preserved on
`backup/pre-cost-rewrite-original` branch (tip `78a4662`); the current
master has been refactored to add the portal.

---

## 2. PILLAR A — LUNARVOID RESEARCH ROADMAP

### 2.1 Phase history (DONE — see R3 terminal report)

| Phase | Period | Output | Gate | Status |
|---|---|---|---|---|
| **M0** Planning | 2026-08-19 | v5 master plan, 3 prior iterations, 6 source docs, feasibility/novelty/dataset assessment | — | [✓] COMPLETE |
| **Z0** WP0 zero-cost | 2026-08-19/21 | Prior-art matrix (30 rows), Tier-0 env, 7/8 pit recovery (Planchon-Darboux), I2 kriging, noise floor, scope map v1.1 | **G0′** FINAL-PASS | [✓] |
| **Z1** WP1 LLTB-1 | 2026-08-21/22 | LLTB-1 v0.5 (Indian Tunnel analog), ladder rungs, VCI + sag detector, per-DTM floors N=10/649 | **G1** FINAL-PASS | [✓] |
| **Z2** WP2 sag search | 2026-08-22/23 | Confusion layer (Hurwitz + LU5M812TGT), sag search over N=21 DTMs, registry 44→278 rows | **G2** FINAL-PASS | [✓] |
| **Z3** WP3 fusion CPU | 2026-08-23 | GRAIL gradients, Diviner thermal N=7, fusion prototype (LR + PU baselines), Bayesian likelihood math | **G2.5** DEMONSTRATION | [✓] |
| **Phase 6** Tier-1 rental + G2 close | BLOCKED | Cycles 3–5 (308 DTMs) + 30 random-mare survey | **G2 FINAL** | [~] BLOCKED on P6.0 credentials |

**Frozen scientific numbers (HEAD `c5be2a2` / R3):**
- Registry: 278 rows = 117 ACTIVE + 161 SUPERSEDED; md5 `a60fb52152e33f37e9052434ad026a6e`.
- FP (row): **3.74 [1.71, 7.10] per 10⁴ km²** (calibration-context, NOT survey).
- FP (unique): 2.08 [0.67, 4.85] per 10⁴ km².
- v1 PU: P 0.9000 / R 0.8182 / AUC 0.8968; PU v5 run B: F1 0.824 / AUC 0.930.
- Above-floor decomp: 45 = 14 TP + 9 FP + 21 ring + 1 funnel.
- Test suite: **124 passed** (verifier scripts v02 21/21, v03 15/15, v04 11/11).
- Spend: **$0 / $150 cycle cap / $800 master-plan ceiling**.

### 2.2 Work-package map (v5 master plan)

```
WP0 [✓]            WP1 [✓]             WP2 [✓]             WP3 [✓]
Tier-0 env +       LLTB-1 analog       Sag search over     CPU fusion
prior-art +         benchmark +         good-tier mare      prototype +
primitive +         detector ladder     DTMs + confusion    PU baselines +
kriging (I2) +                          layer               hierarchical

WP4 [~]            WP5 [ ]             WP6 [~]             WP7 [ ]           WP8 [ ]
Multi-             Hierarchical        Stereo pipeline     Mission concept   Long-tail
illumination       Bayesian fusion     (NAC repro on        (LunarLeaper     science
stacking +         + tier A/B          rental)             handoff)          deliverables
photometric-       promotion           + 308 DTMs
stereo                                 + 30 random-mare
```

### 2.3 Phase 6 (TIER-1) — the only funded work block in queue

Per ZEROCOST §8 T1 trigger APPROVED 2026-08-22 (cost ceiling $150):

| Sub-step | Action | Status |
|---|---|---|
| **P6.0** | HETZNER CREDENTIALS — needs user API key OR root pwd + provider choice | [ ] USER-GATED |
| **P6.1** | Hetzner AX52-NVMe rental (~$55/mo) + spec to `admin/budget.md` | [ ] |
| **P6.2** | ISIS3 + ASP install on rental (~30 min; reuse local snapshot `~/lunarvoid/isis/`+`asp/` if viable) | [ ] |
| **P6.3** | NAC EDR fetch for 308 target DTMs (PDS / LROC WMS; reuse `code/wp8_stereo/`) | [ ] |
| **P6.4** | ASP parallel_stereo × 6 concurrent (~3 days; checkpoint+resume; 308 DTMs = 30 mare + 278 catalogued pits) | [ ] |
| **P6.5** | DTM quality gate: ≥2/3 must pass RMS < 2 m vs TRANQPIT1/MARIUSPIT01 reference | [ ] |
| **P6.6** | `rsync` DTMs back to local (`~/lunarvoid/data/outputs/<SITE>/NAC_DTM_<SITE>.TIF`; 308 × ~100 MB ≈ 30 GB) | [ ] |
| **P6.7** | Re-run P3.1a (per_dtm_floors) + P3.1c (transfer_apply) at new N; verify per-DTM floors match N=10 calibration | [ ] |
| **P6.8** | G2 gate report (paper-writer + verifier + skeptic); **USER GATE — human G2 FINAL decision** | [ ] |

### 2.4 User-gated queue (R3 §11 + RESUME.md §3 — DO NOT auto-start)

| ID | Item | Status | Block |
|---|---|---|---|
| R3-a | Commit `plans/2026-08-21_R1_Roadmap_draft.md` (untracked; lineage note ready) | [ ] | User ok |
| R3-b | Authorise NAC fetch pipeline (Tier-0, HIGH-OPEN-METADATA-CHAIN verified; would deliver first WP0 reproduction since cycle 2 close) | [ ] | User ok |
| R3-c | Authorise D3 LOO reopen (frozen science will move; required for Paper 1 §5.4 transfer-generalisation claim) | [ ] | User ok |
| R3-d | E3 Zenodo deposit (`data/zenodo_deposit_v1.0/` 10/10 CHECKSUMS; CC-BY-4.0/MIT confirm; creator list; token) | [ ] | User ok |
| R3-e | Journal submission Paper 1 v2.1 / Paper 2 v3.3 (verifier PASS-with-notes; user owns portal + editor list) | [ ] | User ok |
| Phase 6 | Hetzner AX52 rental (~$55/mo) + Cycles 3-5 | [ ] | P6.0 credentials |
| NAC pipeline | Step 19.1/19.2 + IMG-byte-signature fetch (Tier-0 budget) | [ ] | R3-b |
| D2 visual verdicts | FECUNPIT 3 + TRANQPIT1 3 + INGENIIPIT 21 candidates (user-completed 2026-08-28 but format not saved) | [ ] | User files |
| CI activation | `.github/workflows/` at root + `admin/ci/ci.yml` + README staged | [ ] | User ok |
| Zotero attaches | Kelahan 2026 (arXiv:2608.09350), Watson & Baldini 2024 (*Icarus* 411:115952), ESSA/Le Corre 2025, Moonstone 2607.03644, Mars-Bench 2510.24010, StereoLunar 2510.18172 | [ ] | Local Zotero must be running |
| E2 skill decision | vault-mirror / conventions-skill exposure (per session 43 finding) | [ ] | User ok |
| Laurier/ASU audit | External prior-art matrix audit item | [ ] | User ok |
| Repo restructure | Choose A/B/C/D/E (clean / +gitignore / named-folder / two-repo / user plan) | [ ] | User pick |

### 2.5 Aspirational science horizons (post-G2, post-paper)

These are NOT in the v5 plan but are natural extensions that the user
may want to pursue after the first two papers land. Each is HIGH-cost
or HIGH-time and would warrant its own gate.

- **A.H1** — **Cross-body transfer learning** (Mars→Moon, Moon→Mars via
  MGC3 + Cushing 2015/2017). Deferred to Paper 3. Needs N ≥ 30 lunar
  positives; would follow the PU-learning baseline. Free Colab/Kaggle
  GPU ceilings suffice for DL pretraining.
- **A.H2** — **Diviner 3D thermal inversion**. Powell 2023 GHRM is
  128 ppd (~237 m/px). At sub-pixel pit scale, the thermal leg of the
  multi-evidence stack is unresolved. A re-derivation at higher
  resolution (e.g., via custom 0.5×0.5° binning of the LRO L-L-DL-RADR
  product) could lift the 2/7 coverage gap to site-wide.
- **A.H3** — **GRAIL Bouguer tier-A promotion**. v5 WP3 includes a
  physics screen (60-300 m span prior + depth-to-width). With 308 new
  DTMs from Phase 6, the morphometry + gravity cross-check becomes
  feasible for tier A (two-independent-methods) for the first time.
- **A.H4** — **NAC fetch pipeline → tier A from visual inspection**.
  With the NAC IMG byte-signature fetch pipeline (R3-b), every catalogued
  pit gets a NAC pair at the user's desk; tier A promotion via
  human-confirmed tube-shape morphology. This is the only path to a
  *detection* claim and would replace R3-c's frozen-science caveat.
- **A.H5** — **Miniaturised PBR moon for portal** (already DONE
  in-session 2026-09-14). Procedural normal + roughness from LROC
  color basemap. Listed here for completeness; zero remaining work.
- **A.H6** — **Polar pit survey extension**. Lunar pits in the polar
  PSRs are scientifically interesting for water-ice stability; v5
  scope is equatorial mare only. Requires permanently-shadowed NAC
  pairs (different illumination constraints).
- **A.H7** — **Open-data release of the candidate registry as a
  machine-readable API**. Beyond Zenodo (R3-d): serve the 278-row
  registry as a JSON API on the portal so other researchers can pull
  the FP-bounded candidates and recompute tiers. Couples to A.H5
  (visual inspection promotes/demotes rows).

---

## 3. PILLAR B — LUNARVOID PORTAL ROADMAP

### 3.1 Phase history (DONE — see `luna-web/docs/ROADMAP.md`)

| Phase | Period | Output | Status |
|---|---|---|---|
| **Phase 0** Pre-2026-09 | Original app: Cinematic Research Showcase, own UI | [✓] SUPERSEDED |
| **Phase 1** 2026-09-12 | Portal migration (lunarvoid-explorer → LUNARVOID Portal): 46 shadcn primitives, R3F globe + cutaway, 5-tab layout, deploy pipeline | [✓] commit `05e66e1` |
| **Phase 2** 2026-09-13 | Design overhaul: "Planetary cartography & sonar workbench"; overlay-collision + responsive fixes | [✓] commits `af73770` + `6f6856b` |
| **Phase 3** 2026-09-13 | Audit: 4 parallel `improve` agents, 9 categories, 19 findings + 4 directions → 17 self-contained plans | [✓] |
| **Phase 4** 2026-09-13 | Hardening & Growth: 17 plans, 67 tests, lint/typecheck/format/build all 0; **NOT YET PUSHED to `main`** | [✓] COMPLETE, awaiting deploy |

### 3.2 Phase 5 (PROPOSED — from portal ROADMAP §"Phase 5 Recommended next")

Ordered by leverage (each needs a design pass before implementation):

| # | Item | Effort | Leverage |
|---|---|---|---|
| 1 | **Zenodo + DOI closure** — link the G3 export (plan 014) to a DOI; complete "open artifact" story | Small | High (credibility) |
| 2 | **Self-host fonts** via `@fontsource` — removes last 3rd-party runtime call | Small | Med (privacy) |
| 3 | **E2E smoke (Playwright)** — codify the 5-tab live checklist in CI | Med | High (regression guard) |
| 4 | **Coverage expansion** — grow synthetic atlas from 12 → 21 sites / 245 unpublished candidates | Med | Med (narrative) |
| 5 | **Content reconciliation** — resolve candidateCount 190 vs CATALOG_SIZE 257; G1 "17 targets" vs C1-1 "21 sites" | Small | High (honesty) |
| 6 | **Photorealistic PBR moon** (DONE in-session 2026-09-14 — procedural normal/roughness) | — | [✓] COMPLETE |
| 7 | **Optional NASA moon basemap** (DONE in-session 2026-09-13 — LROC WAC color map at `public/moon/ldam_4k.jpg`) | — | [✓] COMPLETE |

### 3.3 Portal deployment roadmap

| Sub-step | Action | Status |
|---|---|---|
| Publish | `cd luna-web && git push origin main` → triggers `.github/workflows/deploy.yml` validate → deploy | [ ] USER-GATED |
| Verify live | Open https://ahnaf181419.github.io/luna-web/ in real browser; 5-tab smoke | [ ] |
| First deploy of Phase 4 batch | Currently on branch (no Phase 4 commit on `main`); needs the 17 commits 826e98b→06432ca pushed | [ ] |
| Subsequent deploys | `main` auto-deploys on every push; CI gates lint/typecheck/test/format/build | [✓] |

### 3.4 Portal aspirational horizons

- **P.H1** — **Real-time tier upgrades**: when R3-c (D3 LOO) or A.H4 (visual
  inspection) promotes a registry row, the portal reflects it on next
  data refresh (currently `PROGRAM_RECORD` is hand-pinned).
- **P.H2** — **Multi-locale**: i18n of the manifesto + epistemic thesis
  for non-English-speaking lunar-science audiences (ISRO acknowledgement
  motivates Hindi/Bengali at minimum).
- **P.H3** — **Embeddable widget**: a `<lunarvoid-globe>` custom element
  that other mission-concept pages (LunarLeaper handoff) can embed with
  one script tag.
- **P.H4** — **API surface**: see A.H7 — portal serves the registry as
  JSON. Couples Pillar A and Pillar B.
- **P.H5** — **Interactive analog comparator**: side-by-side Indian
  Tunnel ↔ MARIUSPIT01 DTM with the same detector overlay, so users can
  visually compare ladder-rung outputs.
- **P.H6** — **Mission concept handoff page**: when A.H7 / LunarLeaper
  2025 matures, a dedicated "next mission" tab appears.

---

## 4. REPO STRUCTURE & META

### 4.1 Current layout

```
Lunar_LavaTube/                                         <- repo root (this dir)
├── AGENTS.md                                           <- project rules (rule 5: no commit w/o perm)
├── opencode.json                                       <- permission enforcement
├── .mailmap                                            <- author normalisation
├── .gitignore                                          <- per-machine + outputs + sandbox
├── .gitmodules                                         <- luna-web path + url
├── LICENSE                                             <- MIT (c) 2026 Ahnaf Shafin
├── 00_SOURCE_ORIGINALS/                                <- READ-ONLY archive (5 lunar plans + VPS guide)
├── 01_WORKSPACE/                                       <- ALL new work (admin, code, data, learning, notes, papers, plans)
│   ├── plans/                                          <- roadmap + gate reports + status
│   ├── notes/                                          <- findings (append-only), prior-art matrix, RESUME
│   ├── code/                                           <- LLTB-1, WP0-8 modules, tests, tools
│   ├── data/                                           <- candidate registry, MANIFEST, outputs, Zenodo deposit
│   ├── papers/                                         <- paper1 (12 refs), paper2 (18 refs), gate_reports/
│   ├── learning/                                       <- Obsidian vault: MOCs, NOTES, RESOURCES, MISSION
│   ├── Lunar Lavatube knowledge/                       <- gitignored Obsidian vault
│   ├── admin/                                          <- CHANGELOG, budget, CI, git-hooks, hetzner kit
│   └── README.md                                       <- workspace guide
├── luna-web/                                           <- SUBMODULE (HEAD 4afa59a, main)
│   ├── AGENTS.md                                       <- portal rules (pin react 19.2.8, ui/ vendored)
│   ├── README.md, LICENSE, components.json
│   ├── docs/                                           <- ROADMAP, audit, architecture
│   ├── plans/                                          <- 17 improvement plans
│   ├── src/                                            <- React 19 + Vite 8 + R3F + oklch tokens
│   ├── public/                                         <- third-party assets
│   ├── dist/                                           <- production build (NOT in repo; generated)
│   ├── package.json, vite.config.ts, vitest.config.ts
│   └── index.html
├── .opencode/                                          <- gitignored: agents (orchestrator, geo-coder, verifier, etc.)
├── .playwright-mcp/                                    <- gitignored
└── .pytest_cache/                                      <- gitignored
```

### 4.2 Repo state (date 2026-09-18)

| Metric | Value |
|---|---|
| HEAD | `c9e31ed` (pushed to `origin/master`) |
| Working tree | dirty: `AGENTS.md` modified (rule 5 added today) |
| Submodule | `luna-web` at `4afa59a` (`main`) |
| Backup branch | `backup/pre-cost-rewrite-original` at `78a4662` (full original LUNARVOID history, sessions 1–66) |
| Remote | `https://github.com/amrahman90/luna.git` |
| Author | `Ahnaf181419 <muhammad.ahnaf.sarker@gmail.com>` (normalised via `.mailmap`) |
| Recent commits | `069cd20` bump luna-web → `0516cad` author amend → `37a881b` add .mailmap → `c9e31ed` move luna-web to root |

### 4.3 Repo restructure decision (PENDING — see 5 chat messages earlier)

Five options presented; user has not chosen:
- **A** Minimal: just commit + stop. (Current state.)
- **B** Document + .gitignore sweep: AGENTS.md update, LICENSE consolidated, per-machine dirs confirmed gitignored.
- **C** Named-folder rename: `01_WORKSPACE/` → `research/`, new `portal/` for luna-web parent.
- **D** Two-repo split: extract luna-web to its own repo; research-only in Lunar_LavaTube.
- **E** User's plan (TBD).

### 4.4 Branch strategy

| Branch | Purpose | State |
|---|---|---|
| `master` | Current "live" — research remnants + portal submodule | [✓] at `c9e31ed`, pushed |
| `backup/pre-cost-rewrite-original` | Full pre-portal LUNARVOID history (sessions 1–66) | [✓] at `78a4662`, archived |
| `remotes/origin/master` | GitHub mirror | [✓] at `c9e31ed` |

---

## 5. CROSS-CUTTING CONCERNS

### 5.1 Discipline (from `AGENTS.md` + `luna-web/AGENTS.md`)

- **$0 spend** unless an §8 trigger fires AND user approves.
- **No commits without permission** (rule 5, set 2026-09-18). Every `git commit`, `git commit --amend`, `git tag`, etc. requires explicit, on-message user instruction. Overrides the prior archivist per-task commit step.
- **`00_SOURCE_ORIGINALS/` is read-only** for ALL agents (permission-enforced).
- **`01_WORKSPACE/` holds ALL new work** (root stays clean — `AGENTS.md`, config, two folders, plus LICENSE + .mailmap + .gitmodules post-portal-move; the luna-web/ at root is an explicit exception).
- **Claim discipline**: inference, not detection; FP per 10⁴ km²; Wilson 95% CI.
- **Data discipline**: never mirror LROC archives; NASA analog = research-only; ISRO acknowledgement mandatory; audit licences before redistribution.
- **Test discipline**: smoke pins byte-identical (F1 0.39160839160839167 / 0.0 / 0.8 per rung; fusion AUC 0.990; e2e Fieg F1 0.029746281714785657).

### 5.2 Skills (the agentic layer)

- **`lunarvoid-protocol`** — task lifecycle (orchestrator → geo-coder → verifier → skeptic → archivist → paper-writer); stop conditions; bookkeeping.
- **`lunarvoid-conventions`** — env paths, Planchon-Darboux mandate, lunar DTM geodesy, PDS/Zenodo patterns, statistics & claim discipline, licence rules.

### 5.3 MCP tools in use

| Server | Purpose | Status |
|---|---|---|
| `arxiv` | Paper search + download + semantic search | ✓ enabled (storage `~/lunarvoid/mcp/arxiv`) |
| `zotero` | Library search + metadata + full-text | ✓ enabled (local Zotero required) |

### 5.4 Agents in `.opencode/agent/`

| Agent | Role |
|---|---|
| `lunar-orchestrator` (primary) | Drives the roadmap, dispatches subagents, applies rule 5 (no commits) |
| `geo-coder` | WP0-WP8 implementation, runs research code |
| `verifier` | Re-runs checks, audits numbers + manifest + claim language (edit-denied) |
| `skeptic` | Adversarial scientific reviewer (model-diverse second opinion) |
| `archivist` | Bookkeeping (CHANGELOG, MANIFEST, roadmap ticks, single per-task commit) — **now user-gated for commits** |
| `paper-writer` | Paper drafts + gate reports + figure narration |
| `explore` | Fast codebase exploration (limited thoroughness) |

### 5.5 Budget ledger (live)

| Date | Item | Cost USD |
|---|---|---|
| 2026-08-19 → 2026-09-13 | 62 sessions of research + portal hardening | **$0.00** |
| — | **Cumulative total** | **$0.00** |
| — | **Phase-6 rental ceiling (user-set 2026-08-22)** | **$150.00** |
| — | **Master-plan ceiling (v5)** | **$800.00** |

Pending charges (require user approval per §8):
- Hetzner AX52 (~$55/mo, G2 trigger) — Phase 6 P6.1.
- Tycho-recompute cycles (gated by G2).

---

## 6. PHASING & DEPENDENCIES

### 6.1 Master timeline (gantt-ish)

```
2026-08-19  ─┬─ M0 ─┬─ Z0 ───┬─ Z1 ───┬─ Z2 ───┬─ Z3 ───┐
              │       │         │         │         │         │
              │ v5    │ G0′     │ G1      │ G2      │ G2.5    │ USER-GATE
              │ plan  │ FINAL   │ FINAL   │ FINAL   │ DEMO    │ (paper submit,
              │ done  │ PASS    │ PASS    │ PASS    │ fusion  │  Zenodo,
              │       │         │         │         │         │  Phase 6)
              ├───────┴─────────┴─────────┴─────────┴─────────┤
              │                                                   │
2026-09 ──────┤ Portal Phases 1-4 (17 plans, 67 tests) [✓]     │
              │                                                   │
              │ Portal Phase 5 (proposed)                        │
              │  • Zenodo DOI (P5.1)                             │
              │  • Self-host fonts (P5.2)                        │
              │  • E2E smoke (P5.3)                               │
              │  • Content reconcile (P5.5)                       │
              │                                                   │
              ├───────────────────────────────────────────────────┤
2026-09-18    │ Comprehensive roadmap (THIS DOC) [✓]            │
              │ Repo restructure decision (A-E) [ ]              │
              │ .mailmap + author normalise [✓]                  │
              │ Rule 5 (no commit w/o perm) [✓]                  │
              └───────────────────────────────────────────────────┘
```

### 6.2 Cross-pillar dependencies

```
                        ┌────────────────────────────┐
                        │  PILLAR A — RESEARCH        │
                        │  62 sessions, $0 spent,     │
                        │  registry 278 rows,         │
                        │  G0′/G1/G2 FINAL-PASS       │
                        └─────────────┬──────────────┘
                                      │ frozen numbers +
                                      │ figures + claims
                                      ▼
                        ┌────────────────────────────┐
                        │  PILLAR B — PORTAL          │
                        │  React 19 + Vite 8 + R3F    │
                        │  5 tabs, 67 tests, Phase 4  │
                        │  [✓] COMPLETE, NOT PUSHED   │
                        └────────────────────────────┘
                                      │
                                      ▼
                        ┌────────────────────────────┐
                        │  USER-GATED: PUBLISH        │
                        │  push main → GH Pages       │
                        │  + link DOI from P5.1       │
                        │  + journal submissions      │
                        └────────────────────────────┘
```

### 6.3 Phase 6 (TIER-1) gate-trigger cascade

```
P6.0 [credentials] → P6.1 [rental $55/mo]
   → P6.2 [ISIS3+ASP install]
   → P6.3 [NAC EDR fetch 308 DTMs]
   → P6.4 [ASP parallel_stereo × 6] (3 days)
   → P6.5 [DTM quality gate ≥2/3 PASS]
   → P6.6 [rsync DTMs home]
   → P6.7 [P3.1a + P3.1c re-run at N=308+30]
   → P6.8 [G2 FINAL gate report → USER DECISION]
       → if PASS → freeze registry at N=649 → A.H4 (visual inspection)
                                       → R3-c (D3 LOO reopen)
                                       → R3-e (journal submission w/ new G2 context)
```

---

## 7. STOP CONDITIONS (HALT loop and report)

Per `AGENTS.md` + `lunarvoid-protocol`:

- An **§8 cost trigger** would be required (paid GPU, VPS, rental).
- A **gate decision** (G0′/G1/...) needs a human judgement.
- **Verifier FAIL ×3** on one task.
- A **licence / rule conflict**.
- Any need to **write outside `01_WORKSPACE/` or `~/lunarvoid/`**.
- **T5**: cannot reproduce a published v0.x headline number within ±5%.
- **The user interrupts**.
- **No commits without explicit user permission** (rule 5, 2026-09-18).

---

## 8. VERIFICATION & RESUME PROTOCOL

### 8.1 On any session resume (per RESUME.md §2 — 6 steps)

1. Load skills: `lunarvoid-protocol`, `lunarvoid-conventions`.
2. Acquire lock: `bash ~/lunarvoid/bin/lunarvoid_lock.sh acquire opencode`.
3. Read Obsidian vault `01_WORKSPACE/Lunar Lavatube knowledge/00_HOME.md`.
4. Navigate MOCs (Gates & Decisions; Sites & Candidates; Data & Code; Concepts & Methods; Sessions & Ops).
5. Read `01_WORKSPACE/notes/RESUME.md` (frozen state + user-gated items).
6. Read `admin/CHANGELOG.md` + `notes/findings.md` (when scientific claims touched).

### 8.2 Portal resume (per `luna-web/AGENTS.md`)

1. Run gate: `npm run lint && npm run typecheck && npm test && npm run build`.
2. If all pass: ready to push; ask user before `git push`.
3. If any fail: dispatch verifier + geo-coder cycle to land a fix; never push on red.

### 8.3 Frozen-state verification commands (LUNARVOID)

```bash
REPO=/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube
cd $REPO

# Suite (expect 124 passed)
PYTHONPATH=01_WORKSPACE/code ~/lunarvoid/venv/bin/python -m pytest 01_WORKSPACE/code/tests/ -x -q

# Registry md5 (expect a60fb52152e33f37e9052434ad026a6e)
md5sum 01_WORKSPACE/data/candidate_registry.csv

# Sidecar sha256 (expect 1c884a1ee965c9a3bbbc1b34531509a4a676ae8e9f10ed45280a7b0ef7fb498e)
sha256sum 01_WORKSPACE/data/candidate_registry_flags.csv

# Zenodo CHECKSUMS (expect 10/10 OK)
( cd 01_WORKSPACE/data/zenodo_deposit_v1.0 && sha256sum -c CHECKSUMS.sha256 )

# Verifier scripts
~/lunarvoid/venv/bin/python 01_WORKSPACE/admin/verification_evidence/scripts/verify_v02_f32dir_and_filter.py
~/lunarvoid/venv/bin/python 01_WORKSPACE/admin/verification_evidence/scripts/verify_v03_slope_mask.py
~/lunarvoid/venv/bin/python 01_WORKSPACE/admin/verification_evidence/scripts/verify_v04_tune_slope.py
```

### 8.4 Portal gate commands

```bash
cd /home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube/luna-web
npm run lint && npm run typecheck && npm test && npm run build
# → 0 / 0 / 67 passed / ✓
```

---

## 9. RECENT DECISIONS & DEVIATIONS

| Date | Decision / Deviation | Owner |
|---|---|---|
| 2026-08-19 | Authoritative plan: v5 master plan; everything else is subordinate | user + orchestrator |
| 2026-08-21 | G0′ FINAL-PASS via D1 (Task 8 local ASP = "not viable") | user decision |
| 2026-08-22 | G1 FINAL-PASS + §8 T1 trigger APPROVED + $150 cycle cap | user decision |
| 2026-08-22 | Multi-illumination azimuth test deferred (becomes free w/ P4.2 stacking) | orchestrator decision |
| 2026-08-22 | PU baselines deferred (n=5 too small; need ≥30 for stable F1) | orchestrator decision |
| 2026-08-22 | Physics screen + tier-A promotion deferred (only Z2 active; 7/7) | orchestrator decision |
| 2026-08-22 | MGC3 cross-body pretraining deferred to Paper 2 | orchestrator decision |
| 2026-08-23 | P3.1c N=21 expansion (registry 44→278; FP 6.06→3.74 per 10⁴ km²) | orchestrator decision |
| 2026-09-04 | Project audit v2 (17 plans derived; cross-checked vs source) | orchestrator decision |
| 2026-09-12 | R3 status report = terminal; no more R-numbered reports planned | orchestrator decision |
| 2026-09-12 | Paper 1 v2.1 + Paper 2 v3.3 = submission-ready; awaiting journal submission | user gate |
| 2026-09-13 | Portal Phase 4 COMPLETE; 17/17 plans, 67/67 tests, 0/0 lint/typecheck | orchestrator decision |
| 2026-09-13 | Photorealistic PBR moon (procedural normal+roughness) DONE in-session | orchestrator decision |
| 2026-09-14 | NASA moon basemap commit DONE in-session | orchestrator decision |
| 2026-09-18 | Rule 5 added: **no commits without explicit user permission** | user instruction |
| 2026-09-18 | `.mailmap` normalises author identity | orchestrator decision |
| 2026-09-18 | `luna-web/` moved from `01_WORKSPACE/` to repo root (submodule path edit) | user instruction |

---

## 10. RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Phase 6 rental exceeds $55/mo (idle cost) | Low | $150 cap reached early | Spot pricing + checkpoint+resume; per-task cost tracking in `admin/budget.md` |
| NAC fetch pipeline (R3-b) breaks WMS endpoints | Med | Blocks R3-c + A.H4 | Cache HTML pages; sha256 them; manual screenshot fallback |
| Paper 1/2 desk-rejected for "inference not detection" framing | Low | 6-week resubmit cycle | "to our knowledge" + honest-numbers pattern + skeptic PASS-with-notes on both; carve-out for Tranquillitatis Carrer 2024 |
| Portal push breaks GH Pages (base path mismatch) | Low | Site offline | `vite.config.ts` `base: '/luna-web/'` verified in 67-test suite; preview before push |
| Per-DTM noise floor scaling (N=308 from P6.7) breaks FP CI | Med | Frozen science moves; requires re-paper | Wilson 95% CI; transparent re-accounting; gate-decision protocol (skeptics on demand) |
| `00_SOURCE_ORIGINALS/` accidentally edited | Low | Corruption of authoritative plan | `opencode.json` permission deny + bash deny patterns + git tracked + read-only enforcement |
| Zotero / arxiv MCP unavailable | Low | Cannot search literature | Local Zotero as fallback; arXiv direct URL fetch |
| Laurier/ASU pit database audit conflict | Low | Prior-art matrix drift | Decision pending (user-gated); deferral acceptable |
| User forgets rule 5 and asks for autonomous commit | Med | Rule violation | Hard-coded orchestrator rule; subagents prompt-explicit; ask before every commit |
| luna-web submodule drifts from parent `luna` repo | Low | Deploy pipeline stale | Parent bump script (`git submodule update --remote`); CI gates |

---

## 11. IMMEDIATE NEXT STEPS (sorted by user-decision)

| # | Action | Decision needed |
|---|---|---|
| 1 | **Pick repo restructure option** (A minimal / B +gitignore / C named-folder / D two-repo / E user plan) | User pick |
| 2 | **Push portal to GH Pages** (publish Phase 4) | User: yes/no |
| 3 | **Commit R1 draft** (`plans/2026-08-21_R1_Roadmap_draft.md` untracked) | User: yes/no |
| 4 | **Start Phase 6** (Hetzner rental + Cycles 3-5) | User: provide API key / root pwd |
| 5 | **Start NAC fetch pipeline** (R3-b) | User: yes/no |
| 6 | **Submit Paper 1 / Paper 2** to journals | User: pick journal + portal + editor list |
| 7 | **Deposit Zenodo** (E3) | User: pick licence, confirm creators, paste token |
| 8 | **Reopen D3 LOO** (frozen-science moves) | User: yes/no |
| 9 | **Save D2 visual verdicts** (45 above-floor candidates) | User: paste verdicts |
| 10 | **Activate CI** at repo root | User: yes/no |
| 11 | **Commit this comprehensive roadmap** | User: yes/no (rule 5) |
| 12 | **Start E2E smoke (Playwright)** (portal P5.3) | User: yes/no |
| 13 | **Start self-host fonts** (portal P5.2) | User: yes/no |
| 14 | **Start Zenodo DOI link** (portal P5.1) | User: yes/no |

---

## 12. WHAT THIS ROADMAP DOES NOT COVER (and where to find it)

| Topic | Reference |
|---|---|
| Detailed LLTB-1 ladder rungs | `01_WORKSPACE/code/wp1_ladder/degrade.py` + `plans/2026-08-21_LLTB1_v0.5.1_release_note.md` |
| Paper 1 main body | `01_WORKSPACE/papers/paper1_resolution_limits/main.md` (56 KB) |
| Paper 2 inference framework | `01_WORKSPACE/papers/paper2_inference_main.md` (87 KB) |
| Gate verdicts | `01_WORKSPACE/plans/2026-08-21_GATE_G0prime_report_v1.1.md` + `2026-08-22_GATE_G1_report_v1.0.md` + `2026-08-23_GATE_G2_report_v1.0.md` |
| 17 portal improvement plans | `luna-web/plans/` (see `luna-web/plans/README.md`) |
| Detailed portal architecture | `luna-web/docs/architecture_and_design_plan.md` |
| Portal audit | `luna-web/docs/project_audit_2026-09-16.md` |
| Findings log | `01_WORKSPACE/notes/findings.md` (1,400+ lines, append-only) |
| CHANGELOG | `01_WORKSPACE/admin/CHANGELOG.md` (1,451 lines) |
| Prior-art matrix | `01_WORKSPACE/notes/prior_art_matrix.md` + `.csv` (30 rows) |
| VPS rental guide | `00_SOURCE_ORIGINALS/VPS_Setup_Guide_Lunar_Photogrammetry.txt` |
| Hetzner kit (DO-NOT-RUN) | `01_WORKSPACE/admin/hetzner_rental_kit/` (12 files) |

---

## 13. VERSION LINEAGE NOTE

- **v5 master plan** = `00_SOURCE_ORIGINALS/LUNARVOID_Master_Plan_v5_Full_Synthesis.txt` (authoritative research thesis; never superseded).
- **ZEROCOST roadmap** = `01_WORKSPACE/plans/2026-08-19_ZEROCOST_Roadmap.md` (executable sequence; superseded by THIS document as the top-level roadmap).
- **R1** = `01_WORKSPACE/plans/2026-08-21_R1_Roadmap_draft.md` (untracked; never committed; lineage note ready).
- **R2** = `01_WORKSPACE/plans/2026-09-12_R2_Status_Report.md` (sessions 47 snapshot, 71 lines).
- **R3** = `01_WORKSPACE/plans/2026-09-12_R3_Status_Report.md` (terminal at HEAD `c5be2a2`, 151 lines).
- **THIS DOCUMENT** = `01_WORKSPACE/plans/2026-09-18_COMPREHENSIVE_Roadmap.md` (top-level roadmap as of 2026-09-18; supersedes ZEROCOST + R3 as the live top-level; preserves v5 + R3 numbers verbatim).
- **Luna-web ROADMAP** = `luna-web/docs/ROADMAP.md` (170 lines; lives in submodule; same author intent as Phase 4-5 sections above).

---

## 14. END-OF-ROADMAP

The autonomous engineering program has reached a natural completion
point on Pillar A (R3 §11) and Phase 4 on Pillar B. All frozen-science,
all paper-claim integrity, all v2-plan engineering boxes are done. The
remaining work is user-gated (paper submission, Zenodo, Phase 6 rental,
NAC fetch, visual verdicts, CI activation), repo-decision (restructure
option A-E), or future-aspirational (A.H1-A.H7 / P.H1-P.H6). The
budget holds at $0; the cost ceiling is $150 per cycle and $800 total.

When the user is ready to act on any of these, the orchestrator will
respect rule 5 (no commits without explicit permission) and stop to
ask before every state-changing Git operation.
