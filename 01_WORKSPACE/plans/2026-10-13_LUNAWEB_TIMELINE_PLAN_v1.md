# LUNAWEB Portal — 22-Step Build Timeline (Gates/Journey Section Expansion) · Plan v1

Date: 2026-10-13
Status: EXECUTED (this file is the record)
Supersedes: nothing (extends the 2026-10-05 portal content refresh v1)

## Why this matters

The portal's Gates & Journey tab summarized the program in 5 milestone
cards. The full story — 22 steps from scaffolding to preprint, including
the honest failures (illumination collapse, stereo quality FAIL, the
fabricated "passed" literal, leak-inflated early ML numbers) — is the
strongest possible evidence for the epistemic thesis the portal sells.
Faculty and cold-email recipients now see the complete arc, not just the
highlights.

User decisions (2026-10-13, this session):
- Scope: ALL 22 rows, lightly reworded for public tone.
- Dates: NONE — step numbers carry the chronology.
- Placement: expand the existing Journey block (replace the 5-card grid).

## What shipped (luna-web, 3 files)

1. `src/lib/lunarvoid-data.ts` — new `TimelineStep` interface +
   `TIMELINE` export (22 entries, real-record stratum; provenance comment
   cites `admin/CHANGELOG.md` sessions 1–70). Milestone flags on steps
   08 (first lunar results), 13 (deep audit), 15 (statistics made
   honest), 19 (the physics test), 21 (paper + PDFs + portal).
2. `src/components/sections/GatesJourneySection.tsx` — `JOURNEY` 5-card
   grid deleted; `TIMELINE` rendered as a semantic `<ol>`: mono
   step-number cells (32 px; milestone cells in success tokens
   `border-success/50 bg-success/15 text-success`), neutral 1 px spine
   between steps, title + body in the exact typography of the cards
   replaced. Header gains the tagline "The complete build record — every
   step, including the failures." Frozen stats, WP0.5 panel + figure,
   gates accordion, and budget ledger UNTOUCHED.
3. `src/lib/__tests__/program-record.test.ts` — new `describe('TIMELINE')`
   (5 tests): length/order/uniqueness; dateless guard (ISO-date regex
   across all fields); claim-discipline guard (no detection language);
   milestone-set pin {08,13,15,19,21}; content spot-pins (44 /
   Tranquillitatis / 2,880-row / "far too little for orbit to see" /
   10,610 / $0).

## Copy discipline (row 22 rewrite note)

Row 22 ("Bookkeeping — rewrote commit dates at your request; push
pending" in the internal version) was rewritten for the public surface to:
"Session bookkeeping closed; total program spend: $0 of the $800 lifetime
ceiling. The complete build record — including the failures — stands as
the evidence base for the calibrated-inference thesis." Internal git
operations are not portal content. All other rows track the internal
22-row table the user approved, in third-person public tone.

## Number provenance

Every number in TIMELINE traces to frozen evidence already pinned by the
portal test suite (33 refs, 44 candidates, 278 entries, 35 lessons, 28
raw images, 2,880-row sweep, 10,610-word preprint, $0/$800). No frozen
field of PROGRAM_RECORD / WP05_RECORD / GATES / BUDGET_LEDGER changed.

## Verification evidence

- Gate: `npm run format && lint && typecheck && test && build` — ALL PASS;
  tests 74 → **79/79** (+5 TIMELINE pins); lint 0 errors (7 pre-existing
  warnings in untouched files); build 1.73 s, chunk profile unchanged.
- Browser (Playwright, dev server): gates tab renders the full `<ol>`;
  22 step titles; 5 milestone cells; list terminates at "Final close-out".
- Programmatic layout check at 390 px mobile: NO horizontal overflow;
  number cells (32 px) aligned with titles; first step below header.
- Screenshots: `01_WORKSPACE/plans/figures/timeline-desktop.png`,
  `timeline-mobile.png` (model could not visually inspect; DOM/a11y-tree
  verification used instead).
- Console: 1 error — the documented pre-existing R3F OrbitControls
  tab-switch teardown race (luna-web AGENTS.md "known and cosmetic"),
  unrelated to this change.

## Review chain

Orchestrator direct (luna-web is outside geo-coder edit scope — session-70
routing precedent): implementation + full gate + browser verification
above. Design skill (impeccable) consulted; identity-preservation rule
applied — no new aesthetic, existing tokens only, and the numbered
vertical timeline chosen over a 22-card grid (card-grid anti-pattern).

## User actions (NOT performed by agents)

- Push luna-web main → GH Actions auto-deploys; live check: Gates & Ledger
  tab → 22-step timeline under "The 70-session autonomous research program".
- Push parent master whenever ready (stacks on the unpushed Oct-5-era
  commits; push order independent of luna-web).

## Deferred

- TIMELINE not embedded in the registry JSON export (`registry-export.ts`)
  — the export serves the candidate working set; timeline is narrative.
  Add on request.
- `/impeccable init` (PRODUCT.md) for luna-web — separate housekeeping
  session if wanted.
