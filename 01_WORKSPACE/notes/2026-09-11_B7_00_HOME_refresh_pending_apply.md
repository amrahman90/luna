# B7 — 00_HOME.md refresh (PREPARED, application blocked by tooling)

**Task:** B7 vault `00_HOME.md` refresh (audit-hygiene cluster, 2026-09-11).

**Blocker (tooling, not authorization):** `opencode.json` DOES allow
archivist edits under `01_WORKSPACE/Lunar Lavatube knowledge/**`, but the
edit/write tools cannot round-trip a space-containing path: the plain path
(`01_WORKSPACE/Lunar Lavatube knowledge/00_HOME.md`) fails the permission
glob matcher, while the percent-encoded path (`...Lunar%20Lavatube%20knowledge/...`)
passes the permission check but fails filesystem lookup ("File not found").
Applying this file therefore needs an agent/session whose tooling accepts
the space path (or a one-off user action). No unsafe bypass was used.

**How to apply:** replace the full contents of
`01_WORKSPACE/Lunar Lavatube knowledge/00_HOME.md` with the fenced block
below (keep the trailing newline). Everything outside "Current state",
"Open blockers", the Sessions MOC line, the gate-report nav row, and the
footer is unchanged from the 2026-08-23 bootstrap version.

```markdown
# LUNARVOID — Knowledge Graph Home

> **Calibrated multi-evidence inference of lunar lava tubes — we do not detect, we infer, with error bars.**

# Welcome

This is the entry point to the LUNARVOID Obsidian knowledge graph.
The whole workspace is the vault — canonical files in `notes/`,
`plans/`, `papers/`, and `admin/` are first-class graph nodes; the
curated atomic-notes layer lives in this folder.

**Start here →** [[00_HOME|00_HOME.md]] (this file) →
[[mocs/MOC Gates & Decisions]] → the rest of the graph unfolds.

# Current state

- **Gates:** G0′ / G1 / G2 all **FINAL-PASSED** (G2 human confirmation 2026-08-28; row-10 PARTIAL honest state preserved). G2 verdicts: 5 PASS / 1 PARTIAL / 2 DEMONSTRATION / 1 DEFERRED / 1 DEFERRED-DTM-gap-PARTIAL / 1 NOT MEASURED
- **Registry:** 278 rows = **117 ACTIVE + 161 SUPERSEDED** (B1 repair 2026-09-07; 97 cross-rung duplicate groups → 117 unique features); 45 above-floor rows = 21 primaries + 24 superseded; tiers A=0 / B=0 / C=278
- **FP (two accountings, calibration-context, NOT survey rate):** unique-feature **2.08 [0.67, 4.85]** per 10⁴ km² (5 unique FPs, ~30 m key) · row-based **3.74 [1.71, 7.10]** per 10⁴ km² over 24,062.96 km²
- **Paper 1:** **v2.0 submission-ready** (IMRaD rewrite session 38; A6 assets v2.0 session 39; ninth reference Kelahan et al. 2026 session 41)
- **PU eval:** **v5** (D1 redesign, sessions 40–41) — morphometric-only ablation F1 0.824 / AUC 0.930, cluster CIs F1 [0.35, 0.98]; skeptic F15–F20 closed, verdict SOUND
- **Spend:** $0 across 43 sessions; $150 budget cap; $800 master-plan ceiling

# Open blockers

- ~~Visual inspection of 27 candidates~~ — **user-completed 2026-08-28** (3 FECUNPIT + 24 more), but per-cluster verdicts were not captured on disk; candidates stay tier C, no auto-promotions (capture format defined in notes/findings.md 2026-08-28)
- Tier-1 rental authorised (Hetzner AX52, ~$55/mo) but not yet launched; would close 30 random-mare sites + ASP reproducibility demos (TYCHOPK + priority-site score rasters already closed locally 2026-08-23)
- DTM-production gap (G2 row 10, DEFERRED-DTM-gap-PARTIAL): most of the 649 good-tier mare DTMs remain off-disk — blocks any survey-rate FP claim
- SLDEM2015 normalisation (Step 18.1) deferred from G0′
- I12 confound covariates (LOLA track density, NAC image count) deferred from G0′ §3

# Maps of Content

- [[mocs/MOC Gates & Decisions]] — gates G0′/G1/G2 + decisions D1/D2/§8 T1 + visual-inspection backlog
- [[mocs/MOC Sites & Candidates]] — 21 DTM sites, registry structure, FP patterns
- [[mocs/MOC Data & Code]] — MANIFEST products, WP folders, key scripts, smoke test
- [[mocs/MOC Concepts & Methods]] — calibration-context FP, terrain extrapolation, I14 funnel, claim discipline
- [[mocs/MOC Sessions & Ops]] — session history (MOC table covers 1–24; sessions 25–43 canonical in `admin/CHANGELOG.md`) + budget ledger

# Where to navigate

| You want to… | Go to |
|---|---|
| See the project's decision history | [[mocs/MOC Gates & Decisions]] |
| Understand a specific DTM site | [[sites/TRANQPIT1]] (or pick another from `sites/`) |
| Find candidates needing visual inspection | `backlog/` (3 cluster notes) |
| Read a gate report | `plans/` (canonical; `papers/gate_reports/` holds read-only mirrors) — linked from `gates/` |
| Find the rules / conventions | [[../notes/findings]] (append-only findings log) + `lunarvoid-conventions` skill |
| Check session-by-session what happened | `admin/CHANGELOG.md` (canonical) — mirrored in `sessions/` |

Tags used throughout: #gate #site #decision #backlog #concept #ref #session #fp #tp #highland #mare #deferred #frozen #calibration-context #g2

# Cost discipline reminder

> Every spend requires orchestrator-initiated pre-approval. The
> budget ledger lives at `01_WORKSPACE/admin/budget.md`. We do not
> detect lava tubes. We infer them, with error bars.

---

_Entry MOC for the LUNARVOID Obsidian vault. Last touched: 2026-09-11 (B7 audit-hygiene refresh: post-B1 registry counts, gate statuses, Paper 1 v2.0 / PU v5 / skeptic F20)._
```

**What changed vs the 2026-08-23 version (summary for the verifier):**

1. "Current state": G2 DRAFT-FOR-REVIEW → all gates FINAL-PASSED (G2 human
   confirmation 2026-08-28, row-10 PARTIAL preserved, verdict string now
   says DEFERRED-DTM-gap-PARTIAL per the G2 atomic note); registry
   "257 candidates across 17 ran" → 278 rows = 117 ACTIVE + 161 SUPERSEDED
   (B1 repair), 45 above-floor = 21 primaries + 24 superseded; FP
   "6.06 [2.77, 11.51]" → two accountings (unique 2.08 [0.67, 4.85] /
   row-based 3.74 [1.71, 7.10]); added Paper 1 v2.0 submission-ready and
   PU v5 + skeptic F15–F20 closed lines; sessions 24 → 43.
2. "Open blockers": visual inspection marked user-completed 2026-08-28
   (verdicts uncaptured, tier C unchanged); Tier-1 line updated (TYCHOPK +
   priority-site rasters closed locally 2026-08-23); DTM-production gap
   added as explicit blocker.
3. MOC Sessions line: notes CHANGELOG sessions 25–43 as canonical beyond
   the MOC's 24-row table.
4. Nav table: gate reports now say `plans/` canonical, `papers/gate_reports/`
   mirrors (matches B8 reality).
5. Footer last-touched bumped to 2026-09-11 with reason.

**Observed but out of B7 scope (flag for a follow-up dispatch):**
`gates/G2.md` atomic note still says "Status: DRAFT-FOR-REVIEW" and
`mocs/MOC Sessions & Ops.md` table stops at session 24.
