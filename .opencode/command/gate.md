---
description: Compile a gate report (G0' zero-cost gate etc.) from task outputs via paper-writer, then verify + commit via the standard cycle.
agent: lunar-orchestrator
---

Compile a gate report. Target gate: $ARGUMENTS (default: G0' — the
zero-cost portion of Gate G0, roadmap Task 10).

1. Gather the inputs the gate needs (for G0': Task 4 recovery table,
   Task 5 kriging metrics, Task 6 noise-floor stats + sag-band
   verdict, Task 7/9 confusion+scope layers, Task 8 log/verdict,
   scope-map v1.1 ranking). Paths are in the CHANGELOG entries.
2. Dispatch paper-writer to draft
   `01_WORKSPACE/plans/<date>_GATE_<name>_report.md`: criteria vs
   measured numbers table, pass/fail per criterion, what remains for
   the full (paid) gate, and the explicit "what we can now claim"
   paragraph under claim discipline.
3. Dispatch verifier to check every number in the report against its
   source CSV/JSON.
4. Dispatch skeptic to attack the gate report's methodology and
   claims (alternative explanations, base-rate honesty, claim
   language). Address objections or downgrade claims before step 5;
   do NOT commit over an unaddressed UNSOUND verdict.
5. Dispatch archivist to commit.
Stop and surface to the user if any gate criterion fails, the skeptic
returns UNSOUND, or a decision needs a human.
