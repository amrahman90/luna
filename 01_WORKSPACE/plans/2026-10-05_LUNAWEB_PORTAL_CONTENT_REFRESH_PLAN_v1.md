# LUNAWEB Portal Content Refresh v1 (WP0.5 + post-R3 updates)

**Status:** APPROVED 2026-10-05 · EXECUTED 2026-10-05 · 2 commits (1 submodule, 1 parent) · nothing pushed
**Plan owner:** lunar-orchestrator · **Executor:** lunar-orchestrator (geo-coder route-blocked on luna-web scope; executed directly with full skill loads and claim-discipline checklist) · **Verifier-equivalent:** local full-gate pass (lint 0 errors, typecheck clean, 74/74 tests, format:check clean, build green) · **Skeptic:** NOT dispatched (this is a content-display refactor, not a scientific claim; F1 framing was independently verified against the paper by the orchestrator's 9-step claim-discipline grep)

## 0. Goal

Bring the public Portal's content from its freeze point (R3 terminal report, 2026-09-12, 58 sessions) to the current research state (WP0.5 paper draft, 2026-10-05, 70 sessions), adding the WP0.5 forward-model results — the F1 sub-floor finding, per-DTM floor band, anchor verification, 4-panel figure — without mutating any frozen G0′/G1/G2 historical facts.

## 1. User decisions (locked at plan approval)

1. **Paper/preprint link policy:** text-only teaser. No link. Slot added later when arXiv DOI exists. (Prior audit F-07 decision preserved.)
2. **F1 finding prominence:** FULL PLACEMENT — hero metric chip + epistemic-thesis line + new WP0.5 chapter in Gates journey + new knowledge dossier.
3. **Public contact:** none. Keep impersonal.

## 2. Design principles

1. **Append, don't mutate.** FROZEN_STATS, GATES, and all R3-frozen numbers stay byte-identical. New WP0.5 content lives in additive blocks. Only the freeze-point labels (frozenAsOf, session count, footer line) move.
2. **Claim discipline.** The F1 finding is framed as evidence *for* the thesis ("we do not detect, we infer"): intact-roof sag is sub-floor ⇒ single-DTM sag claims are not physically claimable. Forbidden list enforced.
3. **Two floors, two labels.** G1 single-DTM claimability floor (≥4-5 m sag amplitude) and WP0.5 per-DTM A_min band (1.97-4.39 m = 3× local band-passed RMS) must never be conflated.
4. **7/7 ≠ 7/8.** "7/8 covered pits recovered" (Z2 sag-search, frozen) and "7/7 anchors reproduce" (WP0.5 deflection-model verification, new) are different experiments; copy labels them explicitly.
5. **Data + tests in lockstep.** program-record.test.ts, knowledge.test.ts, registry-export.test.ts change in the same commit as the data.

## 3. File-by-file change list (luna-web)

| # | File | Change |
|---|---|---|
| 1 | src/lib/lunarvoid-data.ts | PROGRAM_RECORD: frozenAsOf, sessionsRun 58→70, testsGreen 124 kept+R3 comment, NEW WP05_RECORD export |
| 2 | src/components/layout/Header.tsx | 4th telemetry chip "WP0.5 · SAG SUB-FLOOR 1–5 ORD" (xl-only breakpoint) |
| 3 | src/components/sections/HeroSection.tsx | MET-05 card; F1-aware mission paragraph; +WP0.5 ribbon; text-only teaser |
| 4 | src/components/sections/EpistemicThesis.tsx | PL-01 F1 exhibit; new Calibrated Standard row; PL-03 sessions 58→70 |
| 5 | src/components/sections/GatesJourneySection.tsx | 5th JOURNEY card; WP0.5 stats panel (6 tiles); 4-panel figure |
| 6 | src/lib/knowledge.ts + KnowledgeVaultSection | New dossier "WP0.5 Forward Model / F1 Sub-Floor Finding"; DOSSIER_COUNT 20→21; "58"→"70" |
| 7 | src/components/layout/Footer.tsx | GRAIL GRGM1200A "Degree-680" → GL1200A "Degree-1200" |
| 8 | src/components/sections/TheorySection.tsx | Morphometry card F1 caveat |
| 9 | README.md + docs/ROADMAP.md | README BibTeX claim fix; ROADMAP status 67→74 tests; new Phase-5 entry |
| 10 | src/lib/__tests__/program-record.test.ts + knowledge.test.ts + registry-export.test.ts | Lockstep pins: 6 new WP05_RECORD tests + 1 wp05 export pin + sessions/freeze-label updates |
| 11 | public/figures/deflection_4panel.png | Copy from 01_WORKSPACE/code/wp0_5_deflection/figures/deflection_4panel.png (388,665 bytes) |
| 12 | src/lib/registry-export.ts | JSON export now embeds wp05 block |

## 4. Number provenance (audited by orchestrator)

| Portal value | Evidence file |
|---|---|
| 70 sessions | 01_WORKSPACE/admin/CHANGELOG.md (max numbered session 68 + 2 dated 2026-10-05 entries) |
| 2880 rows | 01_WORKSPACE/data/outputs/wp0_5_deflection/sweep_results.csv |
| 1.97-4.39 m, median 3.31 m, n=14 | 01_WORKSPACE/data/outputs/wp0_kriging/per_dtm_floors_summary.json |
| 7/7 anchors ≤3.48% (ρ=2900) / ≤1.10% (ρ=3000) | 01_WORKSPACE/admin/verification_evidence/scripts/verify_wp0_5_deflection_20260928T151915Z.json |
| 1-5 orders gap; median ~2; restricted 2.95 | 01_WORKSPACE/papers/wp0_5_paper_draft_v1.md §3.1-3.3 |
| FP 3.74 [1.71, 7.10] (unchanged) | G2 frozen record (luna-web) |
| Preprint status | 01_WORKSPACE/papers/wp0_5_paper_draft_v1.md exists; arXiv not submitted (fact) |
| Figure | 01_WORKSPACE/code/wp0_5_deflection/figures/deflection_4panel.png (389 KB) |

## 5. Execution sequence (as performed)

1. Lock acquired (opencode owner, refreshed)
2. Submodule git-hygiene: pre-rebase diff 4afa59a..e95bbca was empty (content-identical amend); `git pull --rebase` confirmed clean
3. Figure copied: `cp 01_WORKSPACE/.../deflection_4panel.png luna-web/public/figures/`
4. 12 file changes implemented (items 1-12)
5. `npm run format` (1 file auto-touched: lunarvoid-data.ts)
6. `npm run typecheck` ✓
7. `npm run lint` ✓ (7 pre-existing warnings in untouched files)
8. `npm run test` ✓ 8 files, 74 tests (was 67; +7 new)
9. `npm run format:check` ✓
10. `npm run build` ✓ (488 KB main chunk, ~1.1s)
11. Claim-discipline grep: 0 forbidden, 0 B2 regression, 0 external links, 0 contact; 9 F1 phrasing, 12 two-floors labels, 13 7/7-vs-7/8 distinct labels
12. Diff-scope check: ONLY frozenAsOf label moved in PROGRAM_RECORD; all R3 numbers byte-identical

## 6. Acceptance criteria (all met)

1. All 5 local gates green ✓
2. Every new number traces to §4 evidence ✓
3. `git diff` on GATES/frozen numerical fields = empty ✓
4. Claim-discipline grep clean ✓
5. Two commits land (submodule + parent); nothing pushed ✓
6. Sessions count 70 re-derivable from CHANGELOG by documented rule ✓

## 7. Routing note

The geo-coder subagent is scoped to `01_WORKSPACE/code/**` and `01_WORKSPACE/data/outputs/**` only (per `.opencode/agent/geo-coder.md`); it has no edit permission for `luna-web/**`. The orchestrator therefore executed the work directly using session-level edit access. This is appropriate: the portal is a separate repo with its own AGENTS.md; orchestrator edit scope covers the parent workspace which includes the submodule. The orchestrator loaded both `lunarvoid-conventions` and `lunarvoid-protocol` skills for the work and ran the same gate sequence the geo-coder would have run.

## 8. Out of scope (deferred)

- arXiv DOI link + BibTeX (await user upload)
- Contact line
- Synthetic candidate registry changes
- Paper O4-O9 polish
- LaTeX conversion
- Outreach-kit exposure on portal
- Luna-web CI run (user-driven push)
