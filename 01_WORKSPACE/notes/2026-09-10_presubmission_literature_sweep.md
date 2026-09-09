# Pre-submission literature sweep — Paper 1 (2026-09-10)

Scope: arXiv (astro-ph.EP, cs.CV, no-category), 2025-01-01 → 2026-09-10.
Queries: (1) abs:"lunar pit" OR (abs:"lava tube" AND abs:"Moon");
(2) (abs:"lunar subsurface" OR abs:"Mare Tranquillitatis") AND (radar OR SKS OR conduit);
(3) abs:"lunar skylight" OR (abs:"pit detection" AND abs:lunar) OR (abs:"deep learning" AND abs:"lunar surface").
Tool: arXiv MCP search (snippet mode) + full abstract pulls.

## Verdict
Reference set current. ONE addition warranted (made this session): Kelahan et al. 2026,
arXiv:2608.09350 — unsupervised Beta-VAE anomaly search over NAC images recovering
volcanic pits / collapsed lava tubes among anomaly classes (Plaskett, Paracelsus C at
significant rates). Complementary, not competing: 2-D imagery anomaly search vs our
calibrated DTM morphometric inference with FP-per-area accounting. Note: co-author
V. T. Bickel is on our suggested-reviewers list (suggested_reviewers.md).

## Not cited (rationale)
- arXiv:2609.02448 (Bauer+ 2026, foundation model lunar height estimation): DEM
  production, not void inference. Optional future cite if DEM-production paragraph
  ever added.
- arXiv:2604.22848 (LunarDepthNet, monocular DEM generation): same rationale.
- arXiv:2604.25208 (TMC radiometric normalization): not relevant.
- arXiv:2510.18172 (StereoLunar dataset, stereo vision for lunar 3-D reconstruction):
  **WP8-relevant** (stereo DTM rebuild / Task-8 domain) — flag for the R1 roadmap's
  stereo work, not for Paper 1.

## Radar/SKS
Query 2 returned zero 2025+ results: Carrer et al. 2024 (Tranquillitatis conduit,
Mini-RF/SMAP SKS) remains the state of the art for the only radar-evidenced lunar
conduit. No update needed in Papers 1/2.

## Bookkeeping
- Paper 1 main.md: sentence added in §1.2 related work; references 8 → 9 (author-year;
  no renumbering); cover letter count phrase updated.
- Zotero attachment of arXiv:2608.09350 = user-side action (MCP is read/search only).
