# Task 4 (Z0.3) — 8-pit depression-depth sweep notes

Date: 2026-08-19. Sweep of the Task-3 Planchon-Darboux primitive across
all 8 tube-relevant pits with published NAC DTMs. Engine, geodesy and
wrap handling per `01_WORKSPACE/code/wp0_primitive/sweep_pits.py`;
results in `data/outputs/wp0_primitive/pit_recovery_table.csv`.

**Acceptance: 7/8 pass at >=50% of catalogued depth (threshold >=6/8). MET.**

## Failure 1 of 1 — Marius Hills Pit (MARIUSPIT01)

Recovered 14.6 m vs 40 m catalogued (frac 0.36, FAIL). The pit interior
is 98% photogrammetrically valid (NoData fraction only 0.02 within
200 m — this pit's floor was imaged under favorable illumination), so
this is NOT the Task-3 NoData-drain failure: the Planchon-Darboux fill
genuinely ponds only 14.6 m before spilling. The pit sits incised into
Rille A in the Marius Hills; its rim has a low spill point into the
rille channel, so the sink drains sideways at a shallow level — the
pre-registered v5 I14 funnel/open-drainage failure mode. The deepest
fill anywhere within 1 km of the pit is still 14.6 m (at the pit
itself), ruling out an offset-coordinate explanation.

## Overshoot cases (informational, not failures)

Sinus Iridum (frac 2.32), Mare Ingenii (1.60), M. Tranquillitatis
(1.24), N. Procellarum 2 (1.14), N. Procellarum 1 (1.15), C. M.
Fecunditatis (1.19) all recover MORE than the catalogued depth.
Mechanism per Task 3: sink-fill depth measures fill-to-spill of the
valid-pixel floor, which can exceed rim-to-floor catalogue depth when
the spill point is a local rim high. Sinus Iridum's 2.3x overshoot is
the largest and flags either a conservative catalogue value (16 m for a
66 m-diameter pit) or a compound sink; the pit pixel itself is valid
(27.3 m at pixel), so geometry, not data gaps, drives it.

## CRS note for future DTM ingestion

IRIDIUMPIT1 (and FECNDITATS2) store x in an UNWRAPPED projected frame
(lon_0=0, x ~ +7.05e6 m = ~331 degE), which no +/-360 input-longitude
shift can reach because pyproj wraps all longitudes to [-180,180].
`sweep_pits.pit_to_pixel` therefore also shifts x post-transform by
whole 360-degree turns (2*pi*R*cos(lat_ts)). Products with lon_0=180
(TRANQPIT1, MARIUSPIT01, INGENIIPIT, SWFECUNPIT1, PRCLRMPIT01) resolve
via the plain lon+360 input wrap.
