"""pu_learning_extended.py — Extended PU-learning baseline using more registry features.

This is the v2 extension of `pu_learning_on_registry.py` (v1 baseline, F1 0.857
on 5 features). Goal: expose MORE signal to the classifier without direct label
leakage. Adds derived transforms, candidate_id-derived features, and notes-
parsed flags.

Feature audit (registry has 16 columns; see Part A of dispatch):
    Numeric columns:        lon, lat, span_m, sag_amp_m, score
    String columns:         candidate_id, dtm, confusion, methods, tier,
                             status, first_found, updated, evidence, notes

We deliberately EXCLUDE features that leak the positive-class definition:
    - `dtm`             — positive def includes "dtm ∈ CATALOGUED_PIT_DTMS"
    - `lon`, `lat`      — would identify which DTM
    - `has_ring_artifact` (notes flag) — directly in positive def
    - `is_rank1` or `rank_n` — "candidate_id ends in -r001" is in positive def

New features added (Part B of dispatch):
    Log transforms:     log_span_m, log_sag_amp_m, log_score,
                         log_conf_dist_rille_m, log_conf_dist_chain_m
    Ratios / products:  sag_per_span (depth-to-diameter),
                         sag_x_score (project score formula = depth × vesselness)
    ID-derived:         rung_cm (200/400/500/800 — detector cell size)
    Notes flags:        has_below_local_floor, has_terrain_extrap,
                         has_deep_pit_low_vesselness, has_funnel_risk,
                         has_12km_FP
    Methods flag:       is_single_method_morphometry
    Misc:               n_confusion_keys_present (1 or 2 = rille+chain parsed)

Total features: 5 (existing) + 14 (new) = 19.

Claim discipline (per v5): PU-learning produces a RANKING, not a detection.
The 34 positives are a defensible proxy for catalogued-pit local-max hits;
everything else is ML-detected sags with unknown ground truth.

Cost: $0. Local laptop computation.
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
from sklearn.preprocessing import StandardScaler


REPO_ROOT = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
REGISTRY_CSV = REPO_ROOT / "01_WORKSPACE" / "data" / "candidate_registry.csv"
V1_BASELINE_JSON = (
    REPO_ROOT / "01_WORKSPACE" / "data" / "outputs" / "wp5_fusion"
    / "pu_learning_registry_baseline.json"
)
V2_OUTPUT_JSON = (
    REPO_ROOT / "01_WORKSPACE" / "data" / "outputs" / "wp5_fusion"
    / "pu_learning_registry_baseline_v2.json"
)
COMPARISON_JSON = (
    REPO_ROOT / "01_WORKSPACE" / "data" / "outputs" / "wp5_fusion"
    / "pu_learning_comparison.json"
)

# Same catalogued-pit DTM set as v1.
CATALOGUED_PIT_DTMS = frozenset({
    "TRANQPIT1", "MARIUSPIT01", "INGENIIPIT", "SWFECUNPIT1",
    "FECNDITATS2", "PRCLRMPIT01", "IRIDIUMPIT1",
})
CALIBRATION_FP = 9
CALIBRATION_TP = 14

logger = logging.getLogger("pu_registry_v2")


# ---------------------------------------------------------------------------
# Registry reader (reuses v1's logic — must match its column coercion)
# ---------------------------------------------------------------------------
def load_registry(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Registry CSV not found: {path}")

    with open(path) as f:
        lines = f.readlines()

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
# Confusion parser (same as v1)
# ---------------------------------------------------------------------------
_CONFUSION_RE = re.compile(r"(rille|chain|ridge|graben|bg)=(\d+(?:\.\d+)?)m")


def parse_confusion(confusion_str: str, kind: str) -> float:
    if not isinstance(confusion_str, str):
        return 1e6
    for m in _CONFUSION_RE.finditer(confusion_str):
        if m.group(1) == kind:
            try:
                return float(m.group(2))
            except ValueError:
                return 1e6
    return 1e6


def count_confusion_keys(confusion_str: str) -> int:
    """How many rille/chain/ridge/graben/bg distances are present?"""
    if not isinstance(confusion_str, str):
        return 0
    return sum(1 for _ in _CONFUSION_RE.finditer(confusion_str))


# ---------------------------------------------------------------------------
# ID parsers
# ---------------------------------------------------------------------------
_RUNG_RE = re.compile(r"-(\d{3,4})cm-")


def parse_rung_cm(cid: str):
    m = _RUNG_RE.search(cid)
    return int(m.group(1)) if m else np.nan


# ---------------------------------------------------------------------------
# Numeric column audit
# ---------------------------------------------------------------------------
def audit_numeric_columns(df: pd.DataFrame) -> dict:
    """Part A deliverable: every numeric column with name, dtype, %non-null, range."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    audit = []
    for col in numeric_cols:
        s = df[col]
        audit.append({
            "name": col,
            "dtype": str(s.dtype),
            "n_total": int(len(s)),
            "n_non_null": int(s.notna().sum()),
            "pct_non_null": round(100.0 * s.notna().sum() / max(len(s), 1), 2),
            "min": float(s.min()) if s.notna().any() else None,
            "max": float(s.max()) if s.notna().any() else None,
            "median": float(s.median()) if s.notna().any() else None,
        })
    return {
        "all_numeric_columns": numeric_cols,
        "per_column": audit,
        "note": (
            "lon/lat and dtm are excluded from the feature matrix because "
            "they trivially identify the catalogued-pit DTMs used in the "
            "positive-class definition. candidate_id, methods, tier, "
            "status, notes, confusion are object/string columns that we "
            "parse or one-hot encode below."
        ),
    }


# ---------------------------------------------------------------------------
# Feature engineering (extended)
# ---------------------------------------------------------------------------
def build_extended_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], dict]:
    """Build the v2 feature matrix.

    Returns (X, feature_names, audit_dict).
    """
    work = df.copy()

    # --- 5 v1 features (re-parsed to keep this script self-contained) ---
    work["conf_dist_rille_m"] = work["confusion"].apply(
        lambda s: parse_confusion(s, "rille")
    )
    work["conf_dist_chain_m"] = work["confusion"].apply(
        lambda s: parse_confusion(s, "chain")
    )

    # --- Log transforms (helpers + for the confusion distances) ---
    # Use log1p on span/sag/score (all >=0). For confusion distances use
    # log1p of the raw value (1e6 = "no constraint" caps the log at ~13.8).
    work["log_span_m"] = np.log1p(work["span_m"].clip(lower=0))
    work["log_sag_amp_m"] = np.log1p(work["sag_amp_m"].clip(lower=0))
    work["log_score"] = np.log1p(work["score"].clip(lower=0))
    work["log_conf_dist_rille_m"] = np.log1p(work["conf_dist_rille_m"].clip(lower=0))
    work["log_conf_dist_chain_m"] = np.log1p(work["conf_dist_chain_m"].clip(lower=0))

    # --- Ratios / products ---
    # depth-to-diameter ratio (sag per span). Use span_m as a proxy for diameter.
    work["sag_per_span"] = work["sag_amp_m"] / work["span_m"].replace(0, np.nan)
    # Per the project's documented score formula: depth × vesselness.
    # score = depth × vesselness, so sag_amp_m × score is approximately
    # sag_amp_m^2 × vesselness. We log-transform to keep the dynamic range
    # sane; this is a derived signal that emphasizes cells where both
    # depth AND vesselness are large.
    work["log_sag_x_score"] = np.log1p(
        (work["sag_amp_m"] * work["score"]).clip(lower=0)
    )

    # --- ID-derived (rung; NOT rank — rank is in the positive def) ---
    work["rung_cm"] = work["candidate_id"].apply(parse_rung_cm)

    # --- Notes-derived binary flags ---
    # We DELIBERATELY exclude two notes patterns that overlap with the
    # positive-class definition:
    #   - "ring artifact" → directly in positive def
    #   - "below-local-floor" → NOT in the positive label, but the
    #     positive-class construction EXCLUDES all rows with this flag
    #     (the `above_floor` filter applied before train/test split).
    #     Every positive has has_below_local_floor=0 by construction;
    #     adding the feature would let the classifier trivially predict
    #     "below-floor → not positive" with no morphometric signal.
    notes_lower = work["notes"].str.lower()
    work["has_terrain_extrap"] = notes_lower.str.contains(
        "terrain-extrapolation", regex=False
    ).astype(int)
    work["has_deep_pit_low_vesselness"] = notes_lower.str.contains(
        "deep-pit low-vesselness", regex=False
    ).astype(int)
    work["has_funnel_risk"] = notes_lower.str.contains(
        "funnel risk", regex=False
    ).astype(int)
    work["has_12km_FP"] = notes_lower.str.contains(
        "12-km-scale fp", regex=False
    ).astype(int)

    # --- methods-derived ---
    work["is_single_method_morphometry"] = (
        work["methods"].str.strip() == "morphometry"
    ).astype(int)

    # --- Confusion richness (1=rille or chain only, 2=both parsed) ---
    work["n_confusion_keys_present"] = work["confusion"].apply(count_confusion_keys)

    # --- Final feature list ---
    feature_names = [
        # v1 features
        "span_m", "sag_amp_m", "score",
        "conf_dist_rille_m", "conf_dist_chain_m",
        # log transforms
        "log_span_m", "log_sag_amp_m", "log_score",
        "log_conf_dist_rille_m", "log_conf_dist_chain_m",
        # ratios/products
        "sag_per_span", "log_sag_x_score",
        # ID-derived
        "rung_cm",
        # notes flags (NOT ring_artifact or below-local-floor — leakage
        # via the above_floor filter on the positive class)
        "has_terrain_extrap",
        "has_deep_pit_low_vesselness", "has_funnel_risk", "has_12km_FP",
        # methods flag
        "is_single_method_morphometry",
        # misc
        "n_confusion_keys_present",
    ]

    X = work[feature_names].apply(pd.to_numeric, errors="coerce").astype(float)
    medians = X.median(numeric_only=True)
    n_nan_pre = int(X.isna().any(axis=1).sum())
    X = X.fillna(medians)

    feature_audit = {
        "n_features_v2": len(feature_names),
        "n_features_v1": 5,
        "n_new_features": len(feature_names) - 5,
        "new_feature_names": [f for f in feature_names
                              if f not in {"span_m", "sag_amp_m", "score",
                                           "conf_dist_rille_m", "conf_dist_chain_m"}],
        "excluded_to_avoid_leakage": [
            "dtm (used in positive def: CATALOGUED_PIT_DTMS membership)",
            "lon, lat (would identify DTM)",
            "has_ring_artifact (in positive def: notes contain 'ring artifact')",
            "has_below_local_floor (every positive is above_floor=True by the "
            "construction filter; feature would be tautological)",
            "is_rank1 / rank_n (in positive def: candidate_id ends in '-r001')",
        ],
        "imputation": "median per feature",
        "feature_medians": {k: float(v) for k, v in medians.to_dict().items()},
        "n_rows_with_nan_pre_imputation": n_nan_pre,
    }
    return X, feature_names, feature_audit


# ---------------------------------------------------------------------------
# Positive class construction (identical to v1 for an apples-to-apples compare)
# ---------------------------------------------------------------------------
def build_positive_mask(df: pd.DataFrame) -> Tuple[pd.Series, dict]:
    is_cat_pit_dtm = df["dtm"].isin(CATALOGUED_PIT_DTMS)
    is_rank1 = df["candidate_id"].str.contains(
        r"-r001(?:$|-)", regex=True, na=False
    )
    is_ring = df["notes"].str.contains("ring artifact", case=False, na=False)
    positive = (is_cat_pit_dtm & is_rank1) | is_ring
    above_floor = ~df["notes"].str.contains("below-local-floor", case=False, na=False)
    positive_with_floor = positive & above_floor
    n_pos = int(positive_with_floor.sum())
    n_neg = int((~positive_with_floor).sum())
    mapping = {
        "definition": (
            "positive ← (dtm ∈ CATALOGUED_PIT_DTMS AND candidate_id matches '-r001') "
            "OR (notes contain 'ring artifact'); AND NOT below-local-floor"
        ),
        "n_positive_candidates": n_pos,
        "n_unlabeled": n_neg,
    }
    return positive_with_floor, mapping


# ---------------------------------------------------------------------------
# Train / score
# ---------------------------------------------------------------------------
def train_and_score(
    X: pd.DataFrame, y: np.ndarray, feature_names: List[str],
    test_size: float = 0.30, random_state: int = 42,
) -> Tuple[dict, float, List[Tuple[str, float]]]:
    """Train ElkanotoPuClassifier with standardized features.

    Returns (metrics_dict, wall_seconds, [(feat, coef), ...]).
    """
    X_np = X.to_numpy()

    pos_idx = np.where(y == 1)[0]
    neg_idx = np.where(y == 0)[0]

    pos_train_idx, pos_test_idx = train_test_split(
        pos_idx, test_size=test_size, random_state=random_state,
    )
    neg_train_idx, neg_test_idx = train_test_split(
        neg_idx, test_size=test_size, random_state=random_state,
    )

    train_idx = np.concatenate([pos_train_idx, neg_train_idx])
    test_idx = np.concatenate([pos_test_idx, neg_test_idx])

    X_train_raw, y_train = X_np[train_idx], y[train_idx]
    X_test_raw, y_test = X_np[test_idx], y[test_idx]

    # Standardize (zero-mean, unit-variance) using train-set statistics only.
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test = scaler.transform(X_test_raw)

    base = LogisticRegression(C=1.0, max_iter=1000, random_state=random_state)
    sklearn_warnings: list[str] = []
    hold_out_ratio_used = 0.10
    clf = None

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for hold_out_try in (0.10, 0.07, 0.05, 0.03, 0.02):
            try:
                clf = ElkanotoPuClassifier(
                    estimator=base,
                    hold_out_ratio=hold_out_try,
                    random_state=random_state,
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
            raise RuntimeError("All hold_out_ratio tries failed")
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

    # Feature importances: ElkanotoPuClassifier wraps LogisticRegression;
    # the trained estimator is accessible via clf.estimator_ or similar.
    # pulearn's ElkanotoPuClassifier stores the base estimator accessible
    # via clf.estimator after fit. We pull coef_ from there.
    coef = None
    try:
        # ElkanotoPuClassifier wraps the estimator; coef_ lives on the
        # wrapped sub-estimator. Try clf.estimator first.
        if hasattr(clf, "estimator") and hasattr(clf.estimator, "coef_"):
            coef = clf.estimator.coef_[0]
        elif hasattr(clf, "coef_"):
            coef = clf.coef_[0]
    except Exception as e:
        sklearn_warnings.append(f"could not extract coef_: {e}")

    feat_imp: list[Tuple[str, float]] = []
    if coef is not None:
        coef = np.asarray(coef).flatten()
        if coef.shape[0] == len(feature_names):
            feat_imp = list(zip(feature_names, coef.tolist()))

    metrics = {
        "f1_test": f1,
        "precision_test": prec,
        "recall_test": rec,
        "roc_auc_test": auc,
        "n_test_predicted_positive": int(y_pred_test.sum()),
        "n_test_total": int(len(test_idx)),
        "n_test_positives": int(y_test.sum()),
        "n_test_unlabeled": int((y_test == 0).sum()),
        "n_train_total": int(len(train_idx)),
        "n_train_positives": int(y_train.sum()),
        "n_train_unlabeled": int((y_train == 0).sum()),
        "pulearn_base_estimator": "LogisticRegression(C=1.0, max_iter=1000)",
        "pulearn_hold_out_ratio": hold_out_ratio_used,
        "pulearn_random_state": random_state,
        "test_size_fraction": test_size,
        "scaler": "StandardScaler (zero-mean, unit-variance; train-set stats)",
        "sklearn_warnings": sklearn_warnings,
    }
    return metrics, hold_out_ratio_used, feat_imp


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    t0 = time.perf_counter()
    V2_OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    warnings.filterwarnings("always")

    df = load_registry(REGISTRY_CSV)
    n_total = len(df)

    numeric_audit = audit_numeric_columns(df)
    X, feature_names, feature_audit = build_extended_features(df)
    positive, pos_mapping = build_positive_mask(df)
    y = positive.astype(int).to_numpy()

    logger.info(
        "Registry: n=%d, positives=%d, unlabeled=%d, features=%d",
        n_total, int(y.sum()), int((y == 0).sum()), len(feature_names),
    )

    metrics, hold_out_ratio_used, feat_imp = train_and_score(
        X, y, feature_names, test_size=0.30, random_state=42,
    )

    # Sort features by absolute coefficient (descending) for the report.
    feat_imp_sorted = sorted(feat_imp, key=lambda kv: abs(kv[1]), reverse=True)
    top_5 = [(name, float(coef)) for name, coef in feat_imp_sorted[:5]]

    t1 = time.perf_counter()
    wall = t1 - t0

    out = {
        "date": str(date.today()),
        "version": "v2_extended",
        "n_total_rows": n_total,
        "n_positives_TP": int(y.sum()),
        "n_unlabeled": int((y == 0).sum()),
        "n_features": len(feature_names),
        "feature_names": feature_names,
        "numeric_column_audit": numeric_audit,
        "feature_audit": feature_audit,
        "positive_class_mapping": pos_mapping,
        "metrics": metrics,
        "top_5_features_by_abs_coef": top_5,
        "all_feature_coefficients": [
            {"feature": name, "coef": float(c)} for name, c in feat_imp_sorted
        ],
        "calibration_baseline": {
            "n_fp": CALIBRATION_FP,
            "n_tp": CALIBRATION_TP,
            "source": "01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json",
        },
        "wall_time_seconds": wall,
        "claim_discipline": (
            "PU-learning produces a RANKING of inferred void candidates, NOT "
            "a detection. The 34 positives are a defensible proxy for "
            "catalogued-pit local-max hits; the 244 unlabeled are ML-detected "
            "sags whose true nature is unknown. Calibrated inference only."
        ),
    }
    V2_OUTPUT_JSON.write_text(json.dumps(out, indent=2))
    logger.info("Wrote %s", V2_OUTPUT_JSON)

    # Comparison: v1 vs v2
    v1 = json.loads(V1_BASELINE_JSON.read_text())
    v1_metrics = v1["metrics"]
    delta = {
        "f1": metrics["f1_test"] - v1_metrics["f1_test"],
        "precision": metrics["precision_test"] - v1_metrics["precision_test"],
        "recall": metrics["recall_test"] - v1_metrics["recall_test"],
        "auc": metrics["roc_auc_test"] - v1_metrics["roc_auc_test"],
    }
    comparison = {
        "date": str(date.today()),
        "v1": {
            "f1": v1_metrics["f1_test"],
            "precision": v1_metrics["precision_test"],
            "recall": v1_metrics["recall_test"],
            "auc": v1_metrics["roc_auc_test"],
            "n_features": v1["n_features"],
            "feature_names": v1["feature_names"],
            "wall_time_seconds": v1["wall_time_seconds"],
            "source": V1_BASELINE_JSON.name,
        },
        "v2_extended": {
            "f1": metrics["f1_test"],
            "precision": metrics["precision_test"],
            "recall": metrics["recall_test"],
            "auc": metrics["roc_auc_test"],
            "n_features": len(feature_names),
            "feature_names": feature_names,
            "wall_time_seconds": wall,
            "source": V2_OUTPUT_JSON.name,
        },
        "delta": delta,
        "delta_interpretation": (
            "delta = v2_extended - v1. Positive = v2 is better. "
            "v2 adds 14 new features (log transforms, ratios, ID/notes flags) "
            "with the same positive-class definition."
        ),
        "top_5_features_v2_by_abs_coef": [
            {"feature": name, "coef": coef} for name, coef in top_5
        ],
    }
    COMPARISON_JSON.write_text(json.dumps(comparison, indent=2))
    logger.info("Wrote %s", COMPARISON_JSON)

    # Console summary
    print(f"\n=== v2_extended (n_features={len(feature_names)}) ===")
    print(json.dumps(metrics, indent=2))
    print("\n--- Top 5 features by |coef| ---")
    for name, coef in top_5:
        print(f"  {name:36s}  coef={coef:+.4f}")
    print("\n--- v1 vs v2 delta ---")
    print(json.dumps(delta, indent=2))
    print(f"\nWall time v2: {wall:.3f}s")
    print(f"Wrote {V2_OUTPUT_JSON}")
    print(f"Wrote {COMPARISON_JSON}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    raise SystemExit(main())
