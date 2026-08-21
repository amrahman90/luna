---
description: Run the pipeline smoke test and compare against known-good values. Direct execution, no subagents.
agent: lunar-orchestrator
---

Run the smoke test directly and interpret it:

```
~/lunarvoid/venv/bin/python 01_WORKSPACE/code/smoke_test.py
```

Known-good (session-2 baseline): synthetic 200×200 cloud with 4 m
void → 156 void cells (0.4%); per-rung F1 ≈ 0.39 (0.5 m) / 0 (2 m,
threshold collapse — expected) / 0.80 (5 m); fusion AUC ≈ 0.990.
Report PASS/FAIL per value, and if anything regressed, identify the
likely module (recent CHANGELOG entries) and propose the fix — but do
not implement it without the user's go (or dispatch geo-coder if the
user says go).

$ARGUMENTS
