# LUNARVOID — Findings Log (append-only)

Scientific memory: WHAT WE LEARNED, each claim with a traceable
evidence link. (The CHANGELOG records process; this records science.)
Append dated sections only — never edit or delete prior entries.
Reviewed by the skeptic agent; mined by paper-writer.

Format per entry:
`- CLAIM (confidence) — evidence: <path> — caveat: <known weakness>`

---

## findings 2026-08-21 (seed — backfilled headline results)

- Mare Tranquillitatis Pit depth recovered at 129.67 m from NAC DTM
  via Planchon-Darboux fill vs 105 m catalogued (fill-to-spill
  overshoot documented) (HIGH) — evidence:
  `data/outputs/wp0_primitive/pit_recovery_table.csv` — caveat:
  NoData fraction inside 200 m recorded per site.
- 7 of 8 covered pits recover ≥50% of catalogued depth; sole failure
  Marius Hills (14.56/40 m) matches the pre-registered v5 I14
  rille-funnel prediction (HIGH) — evidence: same table; notes
  `notes/2026-08-19_task4_sweep_notes.md`.
- Published NAC DTMs are already LOLA-registered at decimetre level:
  kriged I2 correction moves check-point RMSE only 0.373→0.327 m on
  TRANQPIT1 (1.425→0.541 m on MARIUSPIT01); correction is ~100%
  low-frequency (λ>300 m) and preserves pit depth to +0.05% (HIGH) —
  evidence: `data/outputs/wp0_kriging/*_kriging_metrics.csv`,
  `*_summary.json`.
- Sag detectability floor: sag-band (60–300 m) residual RMS
  1.25–1.38 m on flat mare ⇒ only ≥4 m amplitude sags are
  single-DTM detectable; 1–2 m sags require multi-evidence stacking
  (HIGH — this is the G1 answer) — evidence:
  `data/outputs/wp0_kriging/noise_floor_stats.csv`.
- Sag search recovers the catalogued pit within 100 m as top
  candidate on ALL 8 covered DTMs (scores 1.60–21.06; SW Fecunditatis
  lowest as the only highland site) (HIGH) — evidence:
  `data/outputs/wp2_sag/*/sag_search_summary.json`.
- LLTB-1 v0.4: best honest F1 0.362 (IndianTunnel_NorthSurface 1 m,
  tuned slope 45°); recall 1.00 wherever ≥5 void cells; per-site
  slope tuning regresses on IndianTunnel_cave_1x (use fixed 10°)
  (HIGH) — evidence: `admin/verification_evidence/2026-08-21_v04_tune_slope_verification.json`.

## findings 2026-08-21 (skeptic corrections, G0' report v1.1 review)

- CORRECTION — the 2026-08-21 entry above ("Sag search recovers the
  catalogued pit within 100 m as top candidate on ALL 8 covered DTMs
  (HIGH)") is REFUTED: verifier pit-distance measurement shows
  recovery within 100 m on 4/8 runs only (Ingenii 46 m, top of list;
  MTP 45 m at rank 11/29, score 3.72; Procellarum 38–77 m at ranks
  55/189); on the other 4 runs the closest candidate lies 1.2–2.6 km
  away, and each run's global top score lies 5–29 km from the
  catalogued pit (MTP top 21.06, ~12.5 km NNE) (HIGH, that the
  original claim is false) — evidence:
  `papers/gate_reports/G0prime_report_v1.1.md` row 8;
  `admin/verification_evidence/2026-08-21_z2_pit_distance_verification.md`
  (pending filing) — caveat: corrected claim is "detector responds at
  some real pits; ranking uncalibrated and dominated by uncorroborated
  candidates" at MEDIUM confidence (n=8, Wilson 95% CI on 4/8 ≈
  0.18–0.82; FP/10^4 km² NOT MEASURED; only 21/278 catalogued pits are
  tube-relevant, so pit response ≠ tube response).
- CAVEAT — the sag-floor entry above: pooled sag-band RMS 1.245 m
  (TRANQPIT1) / 1.379 m (MARIUSPIT01) ⇒ 3σ = 3.74 / 4.14 m, so
  "A≥4 m single-DTM detectable" holds strictly only at TRANQPIT1
  (4 m < 4.14 m at Marius). Per-panel RMS spans 0.74–2.05 m (Marius
  P3 local 3σ ≈ 6.1 m); floor sampled at only 2 of ~649 mare DTMs.
  Floor should read "≥5 m at both pooled sites (≥4 m at the quieter
  site)" until per-DTM floors exist (MEDIUM) — evidence:
  `data/outputs/wp0_kriging/noise_floor_stats.csv`. The "3× sag-band
  RMS" rule is a PROJECT CONVENTION; no such multiplier appears in
  v5 §4 (grep-verified 2026-08-21) — do not cite v5 for it.
