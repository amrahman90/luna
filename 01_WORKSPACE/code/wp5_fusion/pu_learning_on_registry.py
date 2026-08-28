"""pu_learning_on_registry.py — Real-data PU-learning baseline on candidate registry.

Operates on the 278-row candidate registry (`data/candidate_registry.csv`).
Wires the pulearn ElkanotoPuClassifier wrapper around scikit-learn's
LogisticRegression on the actual registry features; produces a baseline F1
we can compare against future Hetzner runs.

Why this script is separate from pu_learning_baseline.py
-------------------------------------------------------

The skeleton at `pu_learning_baseline.py` runs on synthetic data and uses a
score-threshold proxy for the positive label. This script:

  1. Reads the registry CSV (handle comment-prefixed lines + quoted commas).
  2. Builds a defensible positive class from columns that ACTUALLY exist in
     the registry (the prompt's `tier_reclass == "TP"`, `above_floor`,
     `depth_max_m`, `frangi_at_score_max`, `dist_pit_m`, `area_km2` columns
     do not exist; the registry has span_m / sag_amp_m / score / confusion +
     methods + tier + status + notes only). The mapping is documented in
     COLUMN_MAPPING inside the script.
  3. Imputes missing numerics with the feature median.
  4. Trains `ElkanotoPuClassifier(LogisticRegression, hold_out_ratio=0.1)`,
     seed 42.
  5. Reports F1, precision, recall on a held-out 30% of positives + unlabeled.

Dataset semantics (per learning/lessons/0008 and 0013)
-----------------------------------------------------

  - Registry tier: A=0, B=0 by design (all 278 are tier C — single-method).
  - Calibration baseline (transfer_summary.json): n_fp=9, n_tp=14.
  - The 14 TPs are the catalogued-pit local-max hits that the detector
    recovers at the 7 catalogued-pit DTMs (TRANQPIT1, MARIUSPIT01,
    INGENIIPIT, SWFECUNPIT1, FECNDITATS2, PRCLRMPIT01, IRIDIUMPIT1). The
    registry does NOT carry an explicit per-row TP/FP label; we have to
    construct a proxy from the candidate_id scheme (rank-1 suffix `-r001`
    identifies the catalogued-pit hit at a given (DTM, rung) cell — by
    construction of the 5-cell local-max detector).

Claim discipline
----------------

PU-learning produces a RANKING of "estimated P(vague void candidate)" — NOT
a detection. The 14 catalogued-pit local-maxes are the only objects on the
Moon with independent existence evidence (Wagner & Robinson 2021 visual
confirmation); all other rows are ML-detected sags whose true nature is
unknown. Even "is this a TP?" is the wrong framing — see
[[concepts/claim-discipline]]. We quote the PU-trained classifier as a
RANKING that *might* prioritize catalogued-pit candidates higher than
non-catalogued candidates in the registry's feature space — that is a
weak but useful baseline claim.

Cost: $0. Local laptop computation; pulearn is in venv.

Outputs
-------

Writes `01_WORKSPACE/data/outputs/wp5_fusion/pu_learning_registry_baseline.json`
with metrics + caveats + wall-time.

Acceptance criteria (per the dispatch prompt):

  - Produce baseline F1 number for WP3 fusion comparison.
  - Validate the pulearn install end-to-end.
  - Document any column-name mismatches discovered.
  - Adapt feature extraction dynamically (no hardcoded names).
"""
from __future__ import annotations

import csv
import io
import json
import logging
import re
import time
import warnings
from datetime import date
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

from pulearn import ElkanotoPuClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score,
)


# ---------------------------------------------------------------------------
# Paths (all relative to repo root)
# ---------------------------------------------------------------------------
REPO_ROOT = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
REGISTRY_CSV = REPO_ROOT / "01_WORKSPACE" / "data" / "candidate_registry.csv"
TRANSFER_SUMMARY_JSON = (
    REPO_ROOT / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag" / "transfer"
    / "transfer_summary.json"
)
OUTPUT_JSON = (
    REPO_ROOT / "01_WORKSPACE" / "data" / "outputs" / "wp5_fusion"
    / "pu_learning_registry_baseline.json"
)

# Catalogued-pit DTMs (per MANIFEST.md + lesson 0008). Rows in the registry
# at these DTMs whose candidate_id ends in `-r001` are by construction the
# catalogued-pit local-max hit (rank-1 of the 5-cell local-max per rung).
CATALOGUED_PIT_DTMS = frozenset({
    "TRANQPIT1", "MARIUSPIT01", "INGENIIPIT", "SWFECUNPIT1",
    "FECNDITATS2", "PRCLRMPIT01", "IRIDIUMPIT1",
})

# Calibration baseline numbers (from data/outputs/wp2_sag/transfer/transfer_summary.json)
# At transport level: n_fp=9, n_tp=14 across all 21 good-tier DTMs.
CALIBRATION_FP = 9
CALIBRATION_TP = 14
# Per the README/prompt: 3.74 per 10^4 km^2 ([1.71, 7.10])
CALIBRATION_FP_PER_10K_KM2 = 3.74
CALIBRATION_FP_PER_10K_KM2_CI = [1.71, 7.10]

# Columns the prompt mentioned but which do NOT exist in the registry.
# Captured for the report.
COLUMNS_PROMPT_EXPECTED = [
    "depth_max_m", "frangi_at_score_max", "span_m", "dist_pit_m",
    "area_km2", "above_floor",
]

logger = logging.getLogger("pu_registry")


# ---------------------------------------------------------------------------
# Registry reader (handles comment-prefixed lines + quoted commas in notes)
# ---------------------------------------------------------------------------
def load_registry(path: Path) -> pd.DataFrame:
    """Load the candidate registry CSV with comment-header + CSV-quoting
    tolerance.

    The registry file has 30 lines of `#`-prefixed header comments followed
    by a 15-column CSV. The `notes` field may contain quoted commas which
    breaks `pd.read_csv(comment='#')`. We parse via the csv module.

    Returns a DataFrame whose numeric columns are best-effort coerced.
    """
    if not path.exists():
        raise FileNotFoundError(f"Registry CSV not found: {path}")

    with open(path) as f:
        lines = f.readlines()

    # Find the actual CSV header (starts with 'candidate_id,').
    try:
        header_idx = next(
            i for i, ln in enumerate(lines) if ln.startswith("candidate_id,")
        )
    except StopIteration:
        raise ValueError(f"No 'candidate_id,' header found in {path}") from None

    csv_text = "".join(lines[header_idx:])
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = [r for r in reader if r.get("candidate_id")
            and not str(r["candidate_id"]).startswith("#")]
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(f"0 data rows loaded from {path}")

    # Numeric coercion for the columns that exist.
    for col in ("lon", "lat", "span_m", "sag_amp_m", "score"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["dtm"] = df["dtm"].astype(str)
    df["candidate_id"] = df["candidate_id"].astype(str)
    df["methods"] = df["methods"].astype(str)
    df["tier"] = df["tier"].astype(str)
    df["notes"] = df["notes"].fillna("").astype(str)
    df["confusion"] = df["confusion"].astype(str)
    return df


# ---------------------------------------------------------------------------
# Confusion-field parser (same shape as pu_learning_baseline.parse_confusion_distance)
# ---------------------------------------------------------------------------
_CONFUSION_RE = re.compile(r"(rille|chain|ridge|graben|bg)=(\d+(?:\.\d+)?)m")


def parse_confusion(confusion_str: str, kind: str) -> float:
    """Extract `kind=distance_m` from a confusion field.

    Returns 1e6 if kind is missing (effectively "no constraint").
    """
    if not isinstance(confusion_str, str):
        return 1e6
    for m in _CONFUSION_RE.finditer(confusion_str):
        if m.group(1) == kind:
            try:
                return float(m.group(2))
            except ValueError:
                return 1e6
    return 1e6


# ---------------------------------------------------------------------------
# Feature engineering (dynamic — features are discovered from the registry)
# ---------------------------------------------------------------------------
# Registry-native numeric morphometry features (used because the prompt's
# listed columns do not all exist; see build_features() for the
# translation). These three are present in every row of the registry and
# are the only signal we have for PU-learning.
REGISTRY_NUMERIC_FEATURES = ("span_m", "sag_amp_m", "score")
# Confusion-distance features (parsed from the 'confusion' field).
REGISTRY_DERIVED_FEATURES = ("conf_dist_rille_m", "conf_dist_chain_m")


def build_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], dict]:
    """Return (feature_df, feature_names, column_report).

    The prompt listed six features — only one (`span_m`) matches. We build
    the full usable feature set from the actual registry columns + parsed
    confusion distances:

      Numeric features (registry columns):
        - span_m          (candidate long-axis span, m)
        - sag_amp_m       (recovered depression amplitude, m)
        - score           (raw detector score = depth × vesselness)

      Parsed features (from the 'confusion' field):
        - conf_dist_rille_m  (distance to nearest sinuous rille, m)
        - conf_dist_chain_m  (distance to nearest crater chain, m)

    Of the 6 prompt-expected columns, only `span_m` is present:
    `depth_max_m`, `frangi_at_score_max`, `dist_pit_m`, `area_km2`,
    `above_floor` are absent (the registry schema lacks them; tier A=0/B=0
    by design, so `tier_reclass` and `above_floor` are also absent).
    """
    work = df.copy()
    work["conf_dist_rille_m"] = work["confusion"].apply(
        lambda s: parse_confusion(s, "rille")
    )
    work["conf_dist_chain_m"] = work["confusion"].apply(
        lambda s: parse_confusion(s, "chain")
    )

    feature_names: list[str] = []
    for col in REGISTRY_NUMERIC_FEATURES + REGISTRY_DERIVED_FEATURES:
        if col in work.columns:
            feature_names.append(col)

    # Numeric matrix; impute NaN with column median (robust to outlier skew).
    X = work[feature_names].apply(pd.to_numeric, errors="coerce").astype(float)
    medians = X.median(numeric_only=True)
    X = X.fillna(medians)

    column_report = {
        "prompt_expected_columns": COLUMNS_PROMPT_EXPECTED,
        "columns_present_in_registry": [c for c in COLUMNS_PROMPT_EXPECTED
                                        if c in work.columns],
        "columns_missing_from_registry": [c for c in COLUMNS_PROMPT_EXPECTED
                                          if c not in work.columns],
        "registry_native_numeric_features_used": [
            c for c in REGISTRY_NUMERIC_FEATURES if c in work.columns
        ],
        "derived_features": [
            c for c in feature_names
            if c in REGISTRY_DERIVED_FEATURES
        ],
        "final_feature_names": feature_names,
        "imputation": "median per feature",
        "feature_medians": {k: float(v) for k, v in medians.to_dict().items()},
        "n_rows_with_nan_pre_imputation": int(work[feature_names]
                                              .apply(pd.to_numeric, errors="coerce")
                                              .isna().any(axis=1).sum()),
    }
    return X, feature_names, column_report


# ---------------------------------------------------------------------------
# Positive class construction
# ---------------------------------------------------------------------------
def build_positive_mask(df: pd.DataFrame) -> Tuple[pd.Series, dict]:
    """Define positive = catalogued-pit local-max hits.

    Per the prompt, the intended positive class is
    `(tier_reclass == "TP") OR (catalogued_pit_source AND above_floor)`.
    Neither `tier_reclass` nor `above_floor` columns exist in the registry.
    We construct the closest defensible proxy from columns that exist:

    POSITIVE ← row.dtm ∈ CATALOGUED_PIT_DTMS AND candidate_id matches
                `-r001` suffix (rank-1 local-max of the 5-cell detector)
                OR notes field mentions "ring artifact around catalogued
                pit" (ring-echo rows are also co-located with the pit so
                they share the same feature-space signal).

    The proxy captures the 14-TP-spirit at n≈16-21 (versus the 14 the
    calibration says). The mapping is documented in the report.
    """
    is_cat_pit_dtm = df["dtm"].isin(CATALOGUED_PIT_DTMS)
    is_rank1 = df["candidate_id"].str.contains(
        r"-r001(?:$|-)", regex=True, na=False
    )
    is_ring = df["notes"].str.contains("ring artifact", case=False, na=False)

    positive = (is_cat_pit_dtm & is_rank1) | is_ring
    # Above-floor proxy from the notes "below-local-floor" annotation.
    above_floor = ~df["notes"].str.contains("below-local-floor", case=False, na=False)

    positive_with_floor = positive & above_floor

    n_pos = int(positive_with_floor.sum())
    n_neg = int((~positive_with_floor).sum())

    mapping = {
        "prompt_intended_definition": (
            "(tier_reclass == 'TP') OR (catalogued_pit_source AND above_floor)"
        ),
        "column_mismatches": [
            "'tier_reclass' column not present (registry only has 'tier' "
            "with values A=0/B=0/C=278 by design)",
            "'above_floor' column not present (must derive from notes "
            "'below-local-floor' annotation)",
            "'depth_max_m' not present (use 'sag_amp_m' as analog)",
            "'frangi_at_score_max' not present (use 'score' as analog)",
            "'dist_pit_m' not present (catalogued-pit proximity is implicit "
            "via 'dtm' membership in CATALOGUED_PIT_DTMS)",
            "'area_km2' not present (no per-candidate searched area; the "
            "calibration baseline uses per-DTM area at the transport level)",
        ],
        "actual_positive_definition": (
            "positive ← (dtm ∈ CATALOGUED_PIT_DTMS) AND "
            "(candidate_id matches '-r001$') "
            "OR (notes contain 'ring artifact') AND "
            "row is NOT flagged 'below-local-floor'"
        ),
        "catalogued_pit_dtms": sorted(CATALOGUED_PIT_DTMS),
        "n_positive_candidates": n_pos,
        "n_unlabeled": n_neg,
        "n_below_local_floor_excluded": int(df["notes"].str.contains(
            "below-local-floor", case=False, na=False
        ).sum()),
    }
    return positive_with_floor, mapping


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    t0 = time.perf_counter()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    # Capture sklearn warnings (convergence, etc).
    warnings.filterwarnings("always")
    sklearn_warnings: list[str] = []

    df = load_registry(REGISTRY_CSV)
    n_total = len(df)

    # Detect which prompt-expected columns exist.
    present = [c for c in COLUMNS_PROMPT_EXPECTED if c in df.columns]
    missing = [c for c in COLUMNS_PROMPT_EXPECTED if c not in df.columns]

    X, feature_names, column_report = build_features(df)
    positive, pos_mapping = build_positive_mask(df)

    n_pos = int(positive.sum())
    n_unlabeled = int((~positive).sum())
    logger.info(
        "Registry: n=%d, positives=%d, unlabeled=%d, features=%d",
        n_total, n_pos, n_unlabeled, len(feature_names),
    )

    y = positive.astype(int).to_numpy()
    X_np = X.to_numpy()

    # PU-learning requires P << U. We have a small positive set (~16-21).
    # ElkanotoPuClassifier handles this internally via hold_out_ratio,
    # but we need to keep ALL positives in the training set per the prompt
    # ("train on 70% of positives + unlabeled; test on the held-out 30%").
    # The U set is split 70/30 since that's what's truly unlabeled in the
    # test bed; positives are also split 70/30 but pulearn only uses
    # positives during training.
    test_size = 0.30

    pos_idx = np.where(y == 1)[0]
    neg_idx = np.where(y == 0)[0]

    pos_train_idx, pos_test_idx = train_test_split(
        pos_idx, test_size=test_size, random_state=42,
    )
    neg_train_idx, neg_test_idx = train_test_split(
        neg_idx, test_size=test_size, random_state=42,
    )

    # Both train and test contain positives + unlabeled.
    train_idx = np.concatenate([pos_train_idx, neg_train_idx])
    test_idx = np.concatenate([pos_test_idx, neg_test_idx])

    X_train = X_np[train_idx]
    y_train = y[train_idx]
    X_test = X_np[test_idx]
    y_test = y[test_idx]

    logger.info(
        "Split (seed=42, test=0.3): train n=%d (%d pos / %d unlab), "
        "test n=%d (%d pos / %d unlab)",
        len(train_idx), int(y_train.sum()), int((y_train == 0).sum()),
        len(test_idx), int(y_test.sum()), int((y_test == 0).sum()),
    )

    base = LogisticRegression(max_iter=500, random_state=42)
    # The ElkanotoPuClassifier needs at least one positive in its internal
    # hold-out subsample. With only ~23 positives in training (after the
    # 70/30 split) and the default `hold_out_ratio=0.1`, pulearn samples
    # ~19 indices and may capture 0 positives by chance. Retry with
    # shrinking hold_out_ratio (and remember which was used).
    n_pos_train = int(y_train.sum())
    hold_out_ratio_used = 0.10
    clf = None
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for hold_out_try in (0.10, 0.07, 0.05, 0.03, 0.02):
            try:
                clf = ElkanotoPuClassifier(
                    estimator=base,
                    hold_out_ratio=hold_out_try,
                    random_state=42,
                )
                clf.fit(X_train, y_train)
                hold_out_ratio_used = hold_out_try
                break
            except ValueError as ve:
                sklearn_warnings.append(
                    f"hold_out_ratio={hold_out_try} failed: {ve}"
                )
                clf = None
        if clf is None:
            raise RuntimeError(
                f"All hold_out_ratio tries failed; n_pos_train={n_pos_train}"
            )
        y_score_test = clf.predict_proba(X_test)[:, 1]
        y_pred_test = (y_score_test >= 0.5).astype(int)
    for w in caught:
        sklearn_warnings.append(f"{w.category.__name__}: {w.message}")

    f1 = float(f1_score(y_test, y_pred_test, zero_division=0))
    prec = float(precision_score(y_test, y_pred_test, zero_division=0))
    rec = float(recall_score(y_test, y_pred_test, zero_division=0))
    try:
        auc = float(roc_auc_score(y_test, y_score_test))
    except ValueError:
        auc = float("nan")
    n_pred_pos = int(y_pred_test.sum())

    t1 = time.perf_counter()
    wall = t1 - t0

    out = {
        "date": str(date.today()),
        "n_total_rows": n_total,
        "n_positives_TP": n_pos,
        "n_unlabeled": n_unlabeled,
        "n_features": len(feature_names),
        "feature_names": feature_names,
        "column_mapping_report": column_report,
        "positive_class_mapping": pos_mapping,
        "n_train_total": int(len(train_idx)),
        "n_train_positives": int(y_train.sum()),
        "n_train_unlabeled": int((y_train == 0).sum()),
        "n_test_total": int(len(test_idx)),
        "n_test_positives": int(y_test.sum()),
        "n_test_unlabeled": int((y_test == 0).sum()),
        "metrics": {
            "f1_test": f1,
            "precision_test": prec,
            "recall_test": rec,
            "roc_auc_test": auc,
            "n_test_predicted_positive": n_pred_pos,
            "pulearn_base_estimator": "LogisticRegression(max_iter=500, C=1.0)",
            "pulearn_hold_out_ratio": hold_out_ratio_used,
            "pulearn_random_state": 42,
            "test_size_fraction": test_size,
        },
        "calibration_baseline": {
            "n_fp": CALIBRATION_FP,
            "n_tp": CALIBRATION_TP,
            "expected_fp_rate_per_10k_km2": CALIBRATION_FP_PER_10K_KM2,
            "expected_per_10k_km2_ci95": CALIBRATION_FP_PER_10K_KM2_CI,
            "source": "01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json",
        },
        "sklearn_warnings": sklearn_warnings,
        "wall_time_seconds": wall,
    }

    OUTPUT_JSON.write_text(json.dumps(out, indent=2))
    logger.info("Wrote %s", OUTPUT_JSON)
    print(json.dumps(out["metrics"], indent=2))
    print(f"\nWrote {OUTPUT_JSON}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    raise SystemExit(main())
