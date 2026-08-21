---
description: Literature refresh — arXiv MCP search for new lunar lava-tube/skylight/rille work, cross-check Zotero, update prior-art matrix, export BibTeX. Usage /litcheck skylights.
agent: lunar-orchestrator
---

Refresh the prior-art layer for Paper 1. Topic focus: $ARGUMENTS
(defaults: lunar lava tubes, skylights/pits, sinuous rilles, DEM
uncertainty, lunar morphometry).

1. Use the arXiv MCP to search the last 12 months for the topic
   terms (try several phrasings; include "lunar pit", "lava tube",
   "sinuous rille", "skylight", "DEM uncertainty"). PDFs stay under
   `~/lunarvoid/mcp/arxiv` — never copy them into the repo.
2. If the Zotero MCP is connected (Zotero desktop must be running —
   if not, note it and skip): check which new items are already in
   the library; pull BibTeX for the matrix's priority rows into
   `01_WORKSPACE/papers/paper1_resolution_limits/refs.bib`.
3. Dispatch paper-writer to append genuinely-new relevant rows to
   `01_WORKSPACE/notes/prior_art_matrix.csv` + `.md` twin (same
   columns; new priority rows fully populated; mark added-date).
   No deletions.
4. Report: n new rows, n already-known, BibTeX exported y/n, and the
   single most important new finding for Paper 1's positioning.
Note: non-arXiv venues (LPSC abstracts, EPSL...) will not surface via
arXiv — flag that a manual pass may be needed before submission.
