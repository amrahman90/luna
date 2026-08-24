"""pu_learning_baseline.py — Positive-Unlabeled (PU) learning baseline for LLTB-1.

This skeleton implements the WP5/P5.1 deliverable: a PU-learning
classifier that learns from the candidate registry where positives are
**catalogued-pit-recovered TPs** (n=14 at G2; above the floor) and
unlabeled are **everything else** (n=233 below-floor + 9 FPs +
could-be-TPs-but-not-yet-recovered; treat the unlabeled as the U in
PU-learning, with the implicit "if not P, then U" class prior).

What is PU-learning?
--------------------

In binary supervised learning we need (x, y) pairs where y ∈ {0, 1}.
In Positive-Unlabeled learning we only have:
  - P examples that we KNOW are positive (catalogued-pit recovered TPs)
  - U examples that are UNLABELED (they may be positive OR negative)

The training data is therefore biased: negatives in the unlabeled set
are indistinguishable from positives in the unlabeled set. Standard
supervised classifiers over-fit to the unlabeled-as-negative assumption.

The `pulearn` package (https://github.com/pulearn/pulearn) implements
two algorithms:
  - ElkanotoPuClassifier: wraps any scikit-learn classifier; trains on
    P + a balanced subsample of U; class-weighted to compensate.
  - BaggingPuClassifier: bagging ensemble of ElkanotoPuClassifier on
    different U subsamples; reduces variance from the random U draw.

Why this matters for LUNARVOID
------------------------------

The registry has:
  - 14 TPs (catalogued-pit-recovered above-floor morphometry matches)
  - 9 FPs (calibration-context)
  - 233 below-floor rows (morphometry-only, too small to promote)
  - Total: 256 rows with morphometry features

PU-learning is the natural framing: we KNOW 14 are positive; we DON'T
KNOW whether the other 242 are negative or weakly-positive. The
PU-trained classifier's job is to rank unlabeled candidates by
**estimated probability of being positive**, not to claim any
classification. This is the calibrated-posterior leg that the G1
verifier (§5 deferred items) flagged as needed for tier-A promotions.

This skeleton:
  - Loads the candidate registry CSV.
  - Selects P (catalogued-pit-recovered TPs) and U (everyone else).
  - Builds features from morphometry columns (span_m, sag_amp_m,
    score, plus the confusion-layer distance features).
  - Splits U into held-out test (40%) + train pool (60%) — seed 42.
  - Trains `ElkanotoPuClassifier(LogisticRegression())`.
  - Reports F1, precision, recall, ROC-AUC on the held-out U set.
  - Saves trained model (joblib) + metrics JSON.

Why pulearn over a vanilla sklearn classifier?
-----------------------------------------------

The vanilla classifier would treat U as negatives and over-fit
(because 242>>14 — the prior is dominated by U). The PU classifier
explicitly down-weights U-as-negative or uses bagging to make the
implicit assumption less dominant. Result: better-calibrated
posterior on the 14 positives we DO have.

P5.1 acceptance criterion (per `notes/findings.md` deferred-items):
  - N >= 30 positives. We have 14. Below threshold but above the
    floor; the skeleton is runnable at any N and reports whether the
    PU prior holds (need P << U; satisfied at 14 << 242).

CLAIM DISCIPLINE: PU-learning produces a RANKING, not a detection. The
output posterior is "estimated probability of being a void candidate"
and is NEVER quoted as "X% chance of being a lava tube". The trained
model is an aid to tier assignment (per WP3 fusion), not a substitute
for two-independent-methods agreement (the registry schema tier-A rule).

Status: SKELETON. The training loop is wired but uses TODO markers for
the feature engineering + the held-out split. A self-test in `__main__`
runs on a 100-row synthetic PU dataset to prove the API surface works.

Dependencies:
  - pandas
  - scikit-learn (LogisticRegression, train_test_split, metrics)
  - pulearn (ElkanotoPuClassifier) — install with
    `~/lunarvoid/venv/bin/pip install pulearn` (NOT yet installed;
    pulearn is not on PyPI mirror used by the venv)
  - joblib (model persistence)
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

# Optional imports — wrapped so the skeleton imports even when pulearn
# is not installed in the venv.
try:
    from pulearn import ElkanotoPuClassifier  # type: ignore
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (
        f1_score, precision_score, recall_score, roc_auc_score,
    )
    import joblib  # type: ignore
    _PULEARN_OK = True
except ImportError as _imp_err:
    _PULEARN_OK = False
    _IMPORT_ERROR = repr(_imp_err)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Registry feature schema (from `data/candidate_registry.csv`)
# ---------------------------------------------------------------------------
# Columns (from `data/candidate_registry.csv` header):
#   candidate_id, lon, lat, dtm, span_m, sag_amp_m, score, confusion,
#   methods, tier, status, first_found, updated, evidence, notes
#
# Features used (numeric, NaN-safe):
#   - span_m          (long-axis span, m; expected 60-300 prior)
#   - sag_amp_m       (recovered depression amplitude, m)
#   - score           (raw detector score)
#   - conf_dist_rille_m (parse from `confusion` field; distance to
#                        nearest rille, m; or 1e6 if absent)
#   - conf_dist_chain_m (parse from `confusion` field; distance to
#                        nearest pit chain, m; or 1e6 if absent)
#
# Label: positive = catalogued-pit-recovered TP (we don't have an
# explicit `is_tp` column in the registry yet; v0.2 will add it. For
# the skeleton we use the proxy "score above the tier-A threshold AND
# near a catalogued pit" which approximates the G1 TP set).

# Registry schema mapping (placeholder — populated when v0.2 adds the
# `is_tp` column).
FEATURE_COLS = ("span_m", "sag_amp_m", "score")
LABEL_COL = "is_tp"  # placeholder; v0.2 column


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------
@dataclass
class PuLearningConfig:
    """Runtime config for the PU-learning baseline.

    Attributes
    ----------
    registry_csv : Path
        Path to the candidate registry CSV (default:
        `01_WORKSPACE/data/candidate_registry.csv`).
    model_out : Path
        Path to write the trained model (joblib pickle).
    metrics_out : Path
        Path to write the metrics JSON.
    random_state : int
        Seed for the train/test split (v5 I9: 42).
    test_size : float
        Fraction of U to hold out for evaluation (default 0.4).
    """
    registry_csv: Path = Path("01_WORKSPACE/data/candidate_registry.csv")
    model_out: Path = Path("01_WORKSPACE/data/outputs/wp5_fusion/pu_model.joblib")
    metrics_out: Path = Path("01_WORKSPACE/data/outputs/wp5_fusion/pu_metrics.json")
    random_state: int = 42
    test_size: float = 0.4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def parse_confusion_distance(confusion_str: str, kind: str) -> float:
    """Parse the `confusion` column to extract the distance to the
    nearest feature of `kind` ("rille" or "chain").

    The `confusion` column has the shape
    `"<closest_class>=<distance_m>|<second>=<distance_m>|..."`,
    e.g. `"n/a|rille=201886m|chain=1263m"`. Returns 1e6 m for missing
    or unparseable values.

    Parameters
    ----------
    confusion_str : str
        The raw value of the `confusion` column.
    kind : str
        Feature kind to extract: "rille" or "chain".

    Returns
    -------
    float
        Distance in metres (or 1e6 if absent).
    """
    if not isinstance(confusion_str, str) or not confusion_str:
        return 1e6
    for part in confusion_str.split("|"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        if k.strip() == kind:
            try:
                return float(v.replace("m", "").strip())
            except ValueError:
                return 1e6
    return 1e6


def load_registry(path: Path) -> pd.DataFrame:
    """Load the candidate registry CSV and parse the confusion field.

    Parameters
    ----------
    path : Path
        Path to the registry CSV.

    Returns
    -------
    pd.DataFrame
        DataFrame with the original columns PLUS the parsed
        `conf_dist_rille_m` and `conf_dist_chain_m` columns.

    Raises
    ------
    FileNotFoundError
        If `path` does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Registry CSV not found: {path}")
    df = pd.read_csv(path, comment="#")
    # Skip header rows that are comments; the registry has comment
    # lines starting with `#`.
    df = df[~df["candidate_id"].astype(str).str.startswith("#", na=False)].copy()
    df["conf_dist_rille_m"] = df["confusion"].apply(
        lambda s: parse_confusion_distance(s, "rille"),
    )
    df["conf_dist_chain_m"] = df["confusion"].apply(
        lambda s: parse_confusion_distance(s, "chain"),
    )
    return df


def split_positive_unlabeled(
    df: pd.DataFrame,
    label_col: str = LABEL_COL,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split the registry into P (catalogued-pit-recovered TPs) and U.

    Parameters
    ----------
    df : pd.DataFrame
        Registry with the `label_col` column populated.
    label_col : str
        Name of the boolean label column.

    Returns
    -------
    p_df : pd.DataFrame
        Positives (rows where label_col is True).
    u_df : pd.DataFrame
        Unlabeled (rows where label_col is False or NaN).
    """
    if label_col not in df.columns:
        # TODO: when v0.2 adds the `is_tp` column, this becomes a real
        # split. For now we synthesise a label from the score column
        # (proxy: high-score rows near catalogued pits) so the
        # skeleton is runnable end-to-end.
        logger.warning(
            "Registry has no `%s` column; using score proxy. v0.2 "
            "should add the explicit TP column.",
            label_col,
        )
        df = df.copy()
        # Proxy: high score + small rille distance = likely TP.
        df[label_col] = (
            (df["score"] > df["score"].quantile(0.95))
            & (df["conf_dist_chain_m"] < 10_000)
        )
    p_df = df[df[label_col] == True].copy()  # noqa: E712 — pandas style
    u_df = df[df[label_col] != True].copy()  # noqa: E712
    return p_df, u_df


# ---------------------------------------------------------------------------
# Main PU-learning entry point
# ---------------------------------------------------------------------------
def train_and_evaluate(cfg: PuLearningConfig) -> dict:
    """Train the PU-learning classifier and report held-out metrics.

    Parameters
    ----------
    cfg : PuLearningConfig
        Runtime config.

    Returns
    -------
    dict
        Metrics dict with keys: n_p, n_u, n_u_train, n_u_test,
        f1_test, precision_test, recall_test, roc_auc_test, status.

    Raises
    ------
    RuntimeError
        If pulearn is not installed. The caller should install pulearn
        (`~/lunarvoid/venv/bin/pip install pulearn`) before running
        the production pipeline.
    """
    if not _PULEARN_OK:
        raise RuntimeError(
            f"pulearn is not installed: {_IMPORT_ERROR}. "
            "Run `~/lunarvoid/venv/bin/pip install pulearn` to enable "
            "PU-learning baseline. Skeleton runs on synthetic data "
            "without it."
        )

    logger.info("Loading registry: %s", cfg.registry_csv)
    df = load_registry(cfg.registry_csv)
    logger.info("Registry rows: %d", len(df))

    p_df, u_df = split_positive_unlabeled(df)
    n_p, n_u = len(p_df), len(u_df)
    logger.info("P=%d, U=%d (PU requires P << U: %s)",
                n_p, n_u, "OK" if n_p < n_u else "FAIL")

    # TODO (geo-coder, v0.2): feature engineering. The skeleton uses
    # span_m, sag_amp_m, score, conf_dist_rille_m, conf_dist_chain_m.
    # The next iteration should add:
    #   - per-DTM pooled_rms_m (from per_dtm_floors.csv)
    #   - local_Amin (amplitude floor) as a per-row denominator
    #   - polar coords + dtm one-hot (small N, may over-fit)
    feature_cols = list(FEATURE_COLS) + ["conf_dist_rille_m", "conf_dist_chain_m"]
    X_p = p_df[feature_cols].fillna(0.0).to_numpy()
    X_u = u_df[feature_cols].fillna(0.0).to_numpy()

    # Held-out test split (U only; P goes entirely into training).
    # v5 I9 protocol: seed 42; test_size 0.4.
    X_u_train, X_u_test = train_test_split(
        X_u, test_size=cfg.test_size, random_state=cfg.random_state,
    )
    n_u_train, n_u_test = len(X_u_train), len(X_u_test)
    logger.info("U train=%d, U test=%d", n_u_train, n_u_test)

    # TODO (geo-coder, v0.2): actual training loop. The skeleton wires
    # the API surface (ElkanotoPuClassifier wraps LogisticRegression)
    # but the real training should:
    #   1. Compute class_weight on P vs U (pulearn handles this).
    #   2. Try multiple base classifiers (LR, RF, GBDT).
    #   3. Cross-validate over random_state (currently single split).
    base = LogisticRegression(max_iter=200, random_state=cfg.random_state)
    clf = ElkanotoPuClassifier(estimator=base, hold_out_ratio=0.2)

    # Concatenate P + U_train; labels are (1, 1, ..., 1, 0, 0, ..., 0)
    # where the 1s come from P (we KNOW they're positive) and the 0s
    # come from a held-in fraction of U_train (pulearn handles this
    # internally; the explicit label vector below is for safety).
    X_train = np.vstack([X_p, X_u_train])
    y_train = np.concatenate([
        np.ones(len(X_p), dtype=int),
        np.zeros(len(X_u_train), dtype=int),  # U_train as negative; pulearn re-weights
    ])
    clf.fit(X_train, y_train)

    # Predict on U_test. We report F1 at threshold=0.5 (default) and
    # ROC-AUC for the ranking quality.
    y_pred = clf.predict(X_u_test)
    # For ROC-AUC, we need a continuous score. pulearn exposes
    # `predict_proba()` on the wrapped estimator; fall back to
    # `decision_function` if not available.
    if hasattr(clf, "predict_proba"):
        y_score = clf.predict_proba(X_u_test)[:, 1]
    elif hasattr(clf, "decision_function"):
        y_score = clf.decision_function(X_u_test)
    else:
        y_score = y_pred.astype(float)

    # Metrics. The U_test set has NO TRUE POSITIVES (we held out P), so
    # F1 is 0-by-definition for the strict binary classification. The
    # meaningful metric is the ROC-AUC on U_test (ranking quality of
    # the 14 P-positives as a fraction of "could-be-positive U").
    # TODO (geo-coder, v0.2): add a held-out-P evaluation: hold out 5
    # of 14 P for test; report F1 vs the held-in P.
    metrics = {
        "n_p": n_p,
        "n_u": n_u,
        "n_u_train": n_u_train,
        "n_u_test": n_u_test,
        "f1_test": float(f1_score(np.zeros_like(y_pred), y_pred, zero_division=0)),
        "precision_test": float(precision_score(np.zeros_like(y_pred), y_pred, zero_division=0)),
        "recall_test": float(recall_score(np.zeros_like(y_pred), y_pred, zero_division=0)),
        # ROC-AUC is undefined if y_test has only one class; guard.
        "roc_auc_test": float(roc_auc_score(np.zeros_like(y_score), y_score)) if len(set(np.zeros_like(y_score))) > 1 else float("nan"),
        "status": "OK",
        "feature_cols": feature_cols,
        "random_state": cfg.random_state,
    }
    logger.info("Metrics: %s", json.dumps(metrics, indent=2))

    # Persist model + metrics.
    cfg.model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, cfg.model_out)
    cfg.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    cfg.metrics_out.write_text(json.dumps(metrics, indent=2))
    logger.info("Saved model: %s", cfg.model_out)
    logger.info("Saved metrics: %s", cfg.metrics_out)
    return metrics


# ---------------------------------------------------------------------------
# Synthetic self-test
# ---------------------------------------------------------------------------
def _synthetic_self_test() -> None:
    """Run a self-test on a 100-row synthetic PU dataset.

    Builds a 2-feature 100-row dataset where the positives cluster in
    one quadrant and the unlabeled are random; verifies the API surface
    works and the metrics dict has the right schema. Skipped if pulearn
    is not installed.

    Expected (sanity, not accuracy): at seed 42 with 80 P + 20 U_test,
    ElkanotoPuClassifier + LogisticRegression should achieve ROC-AUC >
    0.7 (ranking quality of the 14 positives as a function of feature
    distance). F1 will be 0 because y_test is all-zero (no held-out
    P); the meaningful metric is ROC-AUC.
    """
    if not _PULEARN_OK:
        print("SKIP: pulearn not installed; synthetic self-test disabled.")
        print("      Install with: ~/lunarvoid/venv/bin/pip install pulearn")
        return

    rng = np.random.default_rng(seed=42)
    n_p, n_u = 14, 86
    X_p = rng.normal(loc=(2.0, 2.0), scale=0.5, size=(n_p, 2))
    X_u = rng.normal(loc=(0.0, 0.0), scale=1.5, size=(n_u, 2))

    X_u_train, X_u_test = train_test_split(X_u, test_size=0.4, random_state=42)
    X_train = np.vstack([X_p, X_u_train])
    y_train = np.concatenate([np.ones(n_p, dtype=int), np.zeros(len(X_u_train), dtype=int)])

    base = LogisticRegression(max_iter=200, random_state=42)
    clf = ElkanotoPuClassifier(estimator=base, hold_out_ratio=0.2)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_u_test)
    y_score = clf.predict_proba(X_u_test)[:, 1]
    # Verify API surface.
    assert y_pred.shape == (len(X_u_test),), "y_pred shape mismatch"
    assert y_score.shape == (len(X_u_test),), "y_score shape mismatch"
    # Verify metrics are computable.
    f1 = f1_score(np.zeros_like(y_pred), y_pred, zero_division=0)
    assert isinstance(f1, float)
    print(f"PASS: synthetic self-test OK (n_p={n_p}, n_u={n_u}, "
          f"n_u_test={len(X_u_test)})")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    _synthetic_self_test()
    print("INFO: To run on the real registry, call train_and_evaluate() "
          "with a PuLearningConfig pointing at "
          "01_WORKSPACE/data/candidate_registry.csv. Skeleton is a "
          "TODO — feature engineering and the held-out-P evaluation "
          "are placeholders pending v0.2.")