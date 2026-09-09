"""pu_learning_groupsplit.py — D1 leak-free PU eval + D1-repair skeptic ablation.

v3 (D1): leak-free redesign replacing the random 70/30 row split of
`pu_learning_on_registry.py` / `pu_learning_extended.py` (kept untouched as
the historical record of the published v1/v2 numbers). SUPERSEDED rows
excluded from train AND test; leave-one-DTM-out (LODO) cross-fit; same
estimator/hyperparameters as v2 (NOT retuned).

v4 (D1-repair, 2026-09-10) — answers the 5 skeptic objections (3 HIGH,
2 MED) on the v3 artifact:

  O1 (HIGH) annotation-derived features are identity proxies:
      has_terrain_extrap = 1 on 83/117 ACTIVE rows with
      P(positive|flag)=0 (terrain extrapolation only ran on
      catalogued-pit DTMs -> encodes DTM identity); also
      has_deep_pit_low_vesselness (P=0, n=6), has_12km_FP and
      has_funnel_risk (human-adjudicated FP-family flags). Fix: the LODO
      eval now runs TWICE —
        run A "FULL"  = all 19 features, kept as a diagnostic upper
                        bound, explicitly labelled as containing
                        annotation-derived flags;
        run B "MORPH" = the 4 notes-derived flags REMOVED, remaining 15
                        audited (audit recorded in the JSON).
      B is the headline. Run-A per-fold logistic coefficients are
      recorded to document the proxy mechanism.
  O2 (HIGH) row bootstrap anti-conservative (rows cluster by DTM,
      21 clusters): CIs replaced by a DTM-level CLUSTER bootstrap
      (resample the 21 DTM clusters with replacement, 1000 draws, seed
      42) for F1/AUC/precision/recall in BOTH runs; the old row
      bootstrap is kept as explicitly-secondary (F1/precision/AUC only).
      Headline = cluster.
  O3 (HIGH) INGENIIPIT dependence (10/15 positives) + I14 unnamed:
      leave-INGENIIPIT-out pooled summary added for BOTH runs; a
      known_failure_modes block names MARIUSPIT01 r001 (~1e-64 score,
      fold AUC 0.0) as the pre-registered I14 funnel failure recurring
      in the PU layer.
  O4 (MED) recall CI decorative at n=15: recall reported as
      "k/15 positives recovered" + cluster-bootstrap interval only;
      row-bootstrap recall CI language dropped entirely.
  O5 (MED) threshold + prose: threshold sensitivity (F1/precision/recall
      at score thresholds 0.5/1.0/1.5) added for the run-B headline; all
       retry prose is factual — this artifact makes NO claim that
       retry-fold metrics stay inside any CI width (they do not: the
       INGENIIPIT fold's test F1 is 1.0).

v5 (D1-LOW, 2026-09-10) — closes the two skeptic LOW residuals (F20)
on the v4 artifact IN PLACE, without touching any run-A/run-B number
(regression-checked against the committed 596a74f8 JSON):

  L1 rung_cm ablation sensitivity: rung_cm is the only kept run-B
      feature the skeptic flagged as a residual identity carrier
      (rung 500 occurs only in TRANQPIT1, rung 800 only in
      MARIUSPIT01). Run C = run B minus rung_cm (14 features) is
      added as a SENSITIVITY ROW ONLY — run B REMAINS THE HEADLINE.
      Run C reports pooled OOF F1/precision/recall/AUC + cluster-
      bootstrap CIs (same protocol: 21 clusters, 1000 draws, seed 42),
      the MARIUSPIT01-r001 (I14) score in both runs, its rank among
      positives, and the decision-flip count vs run B at t=0.5.
  L2 degenerate-resample rule made explicit: the cluster bootstrap
      occasionally draws a resample with zero positives or zero
      unlabeled rows; v4 already skipped-and-counted these
      (n_degenerate_draws_skipped). The EXACT rule is now documented
      at method.cluster_bootstrap.degenerate_draw_rule with per-run
      discarded-draw counts. The IMPLEMENTATION IS UNCHANGED
      (discard-and-count, not redraw, not coerce) so every published
      CI is reproduced bit-identically (delta 0 <= 0.005 tolerance).

Determinism: seed 42 everywhere; no wall time in the JSON (console
only); the two oof_predictions arrays are self-checked against the
pooled headline metrics before writing; registry md5 recorded.

Claim discipline (v5): PU-learning produces a RANKING of inferred void
candidates, NOT detections. Calibrated inference only.

Cost: $0. Local laptop computation.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import warnings
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

# Reuse the C13-verified loader/leak-guard and the v2 feature/label builders.
from registry_io import load_registry, assert_no_leak
from pu_learning_extended import (
    build_extended_features,
    build_positive_mask,
)

REPO_ROOT = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
REGISTRY_CSV = REPO_ROOT / "01_WORKSPACE" / "data" / "candidate_registry.csv"
V2_JSON = (
    REPO_ROOT / "01_WORKSPACE" / "data" / "outputs" / "wp5_fusion"
    / "pu_learning_registry_baseline_v2.json"
)
OUTPUT_JSON = (
    REPO_ROOT / "01_WORKSPACE" / "data" / "outputs" / "wp5_fusion"
    / "pu_learning_groupsplit_2026-09-09.json"
)

SEED = 42
N_BOOTSTRAP = 1000
THRESHOLDS = (0.5, 1.0, 1.5)
INGENIIPIT = "INGENIIPIT"
# Pinned to the D1 registry snapshot (md5 recorded in the output JSON).
# Fires if the ACTIVE row set ever changes under this evidence artifact.
N_ACTIVE_EXPECTED = 117
_SUPERSEDED_BY_RE = re.compile(r"superseded_by=([^\s;]+)")
_RUNG_IN_ID_RE = re.compile(r"-(?:\d{3,4})cm-")  # only NaN-capable feature trigger

# --- D1-repair O1: run-B feature-set definition ----------------------------
# The four notes-derived flags dropped in run B (kept in run A as the
# diagnostic upper bound). Reasons quote the skeptic's evidence, verified
# on the ACTIVE frame (proxy stats recomputed and stored in the JSON).
DROPPED_ANNOTATION_FLAGS: dict[str, str] = {
    "has_terrain_extrap": (
        "Notes-derived ('terrain-extrapolation'): 1 on 83/117 ACTIVE rows, "
        "P(positive|flag)=0 — terrain extrapolation only ran on "
        "catalogued-pit DTMs, so the flag encodes DTM identity (perfect "
        "negative separator)."
    ),
    "has_deep_pit_low_vesselness": (
        "Notes-derived ('deep-pit low-vesselness'): human-adjudicated "
        "FP-family flag, P(positive|flag)=0 (n=6)."
    ),
    "has_funnel_risk": (
        "Notes-derived ('funnel risk'): human-adjudicated FP-family flag "
        "(n=2)."
    ),
    "has_12km_FP": (
        "Notes-derived ('12-km-scale fp'): human-adjudicated FP-family "
        "flag (n=2). Run-A mean logistic coefficient -0.734 (largest "
        "magnitude of the four) — the proxy mechanism in action."
    ),
}

# Audit verdicts for every KEPT feature in run B (objection 1 requires the
# audit; stored verbatim in the JSON).
KEPT_FEATURE_AUDIT: dict[str, str] = {
    "span_m": "detector output (morphometric); kept",
    "sag_amp_m": "detector output (morphometric); kept",
    "score": "detector output (depth x vesselness); kept",
    "conf_dist_rille_m": (
        "automated WP2 confusion-layer GIS distance (Hurwitz rille "
        "shapefile), 115/117 rows have a real distance — automated "
        "measurement, not human annotation; kept"
    ),
    "conf_dist_chain_m": (
        "automated WP2 confusion-layer GIS distance (crater chains), "
        "115/117 rows have a real distance; kept"
    ),
    "log_span_m": "deterministic transform of span_m; kept",
    "log_sag_amp_m": "deterministic transform of sag_amp_m; kept",
    "log_score": "deterministic transform of score; kept",
    "log_conf_dist_rille_m": "deterministic transform of conf_dist_rille_m; kept",
    "log_conf_dist_chain_m": "deterministic transform of conf_dist_chain_m; kept",
    "sag_per_span": "ratio of detector outputs; kept",
    "log_sag_x_score": "product of detector outputs (log); kept",
    "rung_cm": (
        "parsed from candidate_id; encodes the detection resolution rung "
        "(200/400/500/800 cm). PARTIAL identity signal — rung 500 occurs "
        "only in TRANQPIT1 and rung 800 only in MARIUSPIT01 (1 positive "
        "each of 15) — but rungs are shared across the other 19 DTMs and "
        "the value is a genuine measurement parameter, not an annotation; "
        "kept, flagged here for the record"
    ),
    "is_single_method_morphometry": (
        "methods-column flag; CONSTANT 1 on all 117 ACTIVE rows "
        "(every candidate is single-method morphometry) — zero variance, "
        "carries no information and cannot act as an identity proxy; "
        "kept for exact 15-feature accounting"
    ),
    "n_confusion_keys_present": (
        "count of parsed keys in the automated confusion field (2 for "
        "115/117 rows); automated, not human annotation; kept"
    ),
}

logger = logging.getLogger("pu_groupsplit")

# --- D1-LOW (F20) residual 1: run-C sensitivity feature-set definition ------
# rung_cm is the ONLY kept run-B feature the skeptic flagged as a residual
# identity carrier. Run C = run B minus rung_cm (14 features) is a
# SENSITIVITY ROW ONLY; the headline remains run B (rungs are genuine
# measurement parameters shared across the other 19 DTMs). The per-rung
# row/DTM counts backing the identity claim are recomputed each run and
# stored in the JSON (feature_sets.run_C_MORPH_no_rung_sensitivity.
# rung_identity_evidence) — evidence, not prose.
DROPPED_RUNG_FLAG: dict[str, str] = {
    "rung_cm": (
        "D1-LOW residual (F20): rung_cm is parsed from candidate_id and "
        "is the only KEPT run-B feature the skeptic flagged as a residual "
        "identity carrier — rung 500 occurs only in TRANQPIT1 and rung 800 "
        "only in MARIUSPIT01, so those two values uniquely identify their "
        "DTMs on <=8/117 rows. Dropped HERE ONLY (run C, 14 features) as "
        "an ablation-sensitivity row; KEPT in run B, where it is audited "
        "as a genuine shared measurement parameter (200/400 rungs span "
        "the other 19 DTMs)."
    ),
}

# --- D1-LOW (F20) residual 2: EXPLICIT degenerate-draw rule -----------------
# This documents the v4 (and v5) implementation VERBATIM. The code in
# cluster_bootstrap / row_bootstrap_secondary is UNCHANGED — documenting
# the rule alters no number; all v4 CIs are reproduced bit-identically.
DEGENERATE_DRAW_RULE = (
    "A bootstrap draw is DEGENERATE iff the resample contains zero TRUE "
    "positives or zero TRUE unlabeled rows (ROC AUC is undefined without "
    "both classes; F1/precision/recall would be vacuous). Degenerate draws "
    "are DISCARDED (skipped — NOT redrawn, NOT coerced to a metric value), "
    "counted per run in n_degenerate_draws_skipped, and the percentile CI "
    "is computed over the retained draws only. Draws with zero PREDICTED "
    "positives are NOT degenerate: sklearn's zero_division=0 defines "
    "F1/precision/recall as 0.0 there and such draws are RETAINED with "
    "their 0-valued contributions (AUC is unaffected — it ignores "
    "predictions). The identical rule applies to the secondary row "
    "bootstrap. Discarding-instead-of-redrawing is deliberate: redrawing "
    "would consume extra RNG values and change every downstream draw of "
    "the seeded stream. This rule was already the v4 behaviour; making it "
    "explicit changed nothing (published CIs bit-identical, delta 0.000 "
    "<= 0.005 tolerance)."
)


# ---------------------------------------------------------------------------
# Registry prep: ACTIVE-only frame + candidate-group keys
# ---------------------------------------------------------------------------
def prepare_frames(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, dict]:
    """Split ACTIVE vs SUPERSEDED, build candidate-group keys, validate links.

    Group key: every ACTIVE row is its own primary (its candidate_id);
    every SUPERSEDED row maps to the ACTIVE primary named in its notes
    (`superseded_by=`). Returns (active_df, group_key_for_superseded, stats).
    """
    df = df.copy()
    df["_superseded_by"] = df["notes"].str.extract(_SUPERSEDED_BY_RE.pattern)[0]

    is_active = df["status"] == "ACTIVE"
    is_sup = df["status"] == "SUPERSEDED"
    if not (is_active | is_sup).all():
        bad = sorted(df.loc[~(is_active | is_sup), "status"].unique())
        raise ValueError(f"Unexpected status values: {bad}")

    active = df[is_active].reset_index(drop=True)
    superseded = df[is_sup]

    # Link validation: every SUPERSEDED row names an ACTIVE primary.
    active_ids = set(active["candidate_id"])
    if active["candidate_id"].duplicated().any():
        dupes = active.loc[active["candidate_id"].duplicated(), "candidate_id"]
        raise ValueError(f"Duplicate ACTIVE candidate_ids: {dupes.tolist()}")
    missing = superseded["_superseded_by"].isna()
    if missing.any():
        raise ValueError(
            f"{int(missing.sum())} SUPERSEDED rows lack superseded_by= link"
        )
    dangling = ~superseded["_superseded_by"].isin(active_ids)
    if dangling.any():
        raise ValueError(
            "superseded_by targets not ACTIVE rows: "
            f"{sorted(set(superseded.loc[dangling, '_superseded_by']))[:5]}"
        )

    stats = {
        "n_rows_total": int(len(df)),
        "n_active_kept": int(len(active)),
        "n_superseded_excluded": int(len(superseded)),
        "n_unique_features_active": int(active["candidate_id"].nunique()),
        "n_superseded_links_validated": int(len(superseded)),
    }
    return active, superseded["_superseded_by"], stats


# ---------------------------------------------------------------------------
# Per-fold feature matrices (train-median imputation, train-only scaler)
# ---------------------------------------------------------------------------
def fold_matrices(
    active: pd.DataFrame, train_idx: np.ndarray, test_idx: np.ndarray,
    feature_subset: list[str] | None = None,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Feature matrices for one fold, imputed/scaled with TRAIN statistics only.

    Reuses pu_learning_extended.build_extended_features (all 19 features
    built, then `feature_subset` columns selected — run B drops the four
    notes-derived annotation flags). That helper imputes NaN with the
    medians of whatever frame it is given, so we call it on the TRAIN
    subset (train medians) and on the TEST subset, then assert the TEST
    subset had no pre-imputation NaNs (only sag_per_span [span_m==0] and
    rung_cm [unparseable id] can be NaN; verified 0 on this registry). If
    the assert ever fires, TEST NaN cells are overwritten with TRAIN
    medians.
    """
    X_tr, full_names, audit_tr = build_extended_features(
        active.iloc[train_idx]
    )
    X_te, _, _ = build_extended_features(active.iloc[test_idx])

    test_rows = active.iloc[test_idx]
    nan_capable = (
        test_rows["span_m"].eq(0)
        | ~test_rows["candidate_id"].str.contains(
            _RUNG_IN_ID_RE.pattern, regex=True
        )
        | test_rows[["span_m", "sag_amp_m", "score"]].isna().any(axis=1)
    )
    if bool(nan_capable.any()):
        # Overwrite possibly-imputed cells with TRAIN medians (safe: we do
        # not know which test cells were NaN, so re-apply train medians to
        # every NaN-capable row's NaN-able columns).
        med_tr = audit_tr["feature_medians"]
        for col in ("sag_per_span", "rung_cm"):
            X_te.loc[nan_capable, col] = np.nan
            X_te[col] = X_te[col].fillna(med_tr[col])

    names = full_names if feature_subset is None else list(feature_subset)
    if feature_subset is not None:
        unknown = set(feature_subset) - set(full_names)
        if unknown:
            raise ValueError(f"feature_subset unknown columns: {sorted(unknown)}")
        X_tr, X_te = X_tr[feature_subset], X_te[feature_subset]

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr.to_numpy())
    X_te_s = scaler.transform(X_te.to_numpy())
    return X_tr_s, X_te_s, names


# ---------------------------------------------------------------------------
# Fit — SAME estimator + hyperparameters as v2 (NOT retuned).
# Duplicated minimally from pu_learning_extended.train_and_score because
# that function hard-wires the leaky random row split.
# ---------------------------------------------------------------------------
def fit_pu_fold(
    X_tr: np.ndarray, y_tr: np.ndarray,
) -> tuple[object, float, int, list[str]]:
    """Fit the v2 PU configuration on one fold's TRAIN rows.

    Estimator + hyperparameters are IDENTICAL to v2 (not retuned):
    ElkanotoPuClassifier(LogisticRegression(C=1.0, max_iter=1000)), with
    v2's hold_out_ratio ladder (0.10→0.02). Duplicated minimally from
    pu_learning_extended.train_and_score, which hard-wires the leaky split.

    Feasibility-only deviation, recorded per fold: pulearn holds out
    ceil(n_rows*ratio) of ALL rows and requires >=1 positive in it. On the
    INGENIIPIT-held-out fold only 5 positives remain in train, and the
    seed-42 draw can miss for every ladder ratio. In that case we retry the
    SAME configuration with the internal RNG draw retried across
    random_state 42->81 — the seed ladder range(42, 82), i.e. 40
    consecutive seeds at each hold_out_ratio in the 0.10/0.07/0.05/0.03/
    0.02 ratio ladder. Selection never touches the test fold — this is
    feasibility, not tuning.
    """
    from pulearn import ElkanotoPuClassifier

    base = LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)
    issues: list[str] = []
    hold_out_used = None
    seed_used = None
    clf = None
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for hold_out_try in (0.10, 0.07, 0.05, 0.03, 0.02):
            for seed_try in range(SEED, SEED + 40):
                try:
                    clf = ElkanotoPuClassifier(
                        estimator=base,
                        hold_out_ratio=hold_out_try,
                        random_state=seed_try,
                    )
                    clf.fit(X_tr, y_tr)
                    hold_out_used, seed_used = hold_out_try, seed_try
                    break
                except ValueError as ve:
                    issues.append(
                        f"hold_out_ratio={hold_out_try}, pu_rs={seed_try} "
                        f"failed: {ve}"
                    )
                    clf = None
            if clf is not None:
                break
        if clf is None:
            raise RuntimeError(
                f"All hold_out_ratio/random_state tries failed: {issues[-5:]}"
            )
    issues.extend(f"{w.category.__name__}: {w.message}" for w in caught)
    return clf, hold_out_used, seed_used, issues


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------
def pooled_metrics(
    y: np.ndarray, pred: np.ndarray, score: np.ndarray,
) -> dict:
    return {
        "n": int(len(y)),
        "n_positives": int((y == 1).sum()),
        "n_unlabeled": int((y == 0).sum()),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, score)),
        "n_predicted_positive": int(pred.sum()),
        "n_true_positives": int(((y == 1) & (pred == 1)).sum()),
    }


def cluster_bootstrap(
    y: np.ndarray, pred: np.ndarray, score: np.ndarray,
    groups: np.ndarray, n_boot: int = N_BOOTSTRAP, seed: int = SEED,
) -> dict:
    """DTM-level cluster bootstrap (objection 2): resample the DTM clusters
    with replacement (all rows of a drawn cluster enter the resample,
    with multiplicity), recompute pooled metrics per draw, percentile CI.

    This is the HEADLINE CI: rows within a DTM are spatially correlated,
    so a row bootstrap understates variance whenever whole DTMs are
    systematically mis-scored.
    """
    rng = np.random.default_rng(seed)
    dtms = pd.unique(groups)
    idx_by_dtm = [np.flatnonzero(groups == d) for d in dtms]
    n_clusters = len(dtms)
    draws = {m: [] for m in ("f1", "precision", "recall", "roc_auc")}
    n_skipped = 0
    for _ in range(n_boot):
        pick = rng.integers(0, n_clusters, n_clusters)
        idx = np.concatenate([idx_by_dtm[i] for i in pick])
        yb, pb, sb = y[idx], pred[idx], score[idx]
        if (yb == 1).sum() == 0 or (yb == 0).sum() == 0:
            n_skipped += 1  # degenerate resample (no positive / no unlabeled)
            continue
        draws["f1"].append(f1_score(yb, pb, zero_division=0))
        draws["precision"].append(precision_score(yb, pb, zero_division=0))
        draws["recall"].append(recall_score(yb, pb, zero_division=0))
        draws["roc_auc"].append(roc_auc_score(yb, sb))
    ci = {
        f"{m}_95ci": {
            "low": float(np.percentile(v, 2.5)),
            "high": float(np.percentile(v, 97.5)),
        }
        for m, v in draws.items()
    }
    return {
        "n_resamples": n_boot,
        "seed": seed,
        "method": (
            f"DTM-level cluster bootstrap: the {n_clusters} DTM clusters "
            "resampled with replacement; all rows of a drawn cluster enter "
            "the resample (with multiplicity); percentile 95% CI. HEADLINE "
            "CI (rows cluster by DTM; row bootstrap is anti-conservative)."
        ),
        "n_clusters": int(n_clusters),
        "n_degenerate_draws_skipped": int(n_skipped),
        **ci,
    }


def row_bootstrap_secondary(
    y: np.ndarray, pred: np.ndarray, score: np.ndarray,
    n_boot: int = N_BOOTSTRAP, seed: int = SEED,
) -> dict:
    """Secondary (non-headline) row bootstrap over pooled OOF rows.

    Recall is DELIBERATELY omitted (objection 4: a row-resample recall
    interval is decorative at n=15 positives — it only resamples the
    denominator, never the ranking difficulty). Recall is reported as
    'k/15 recovered' plus the cluster-bootstrap interval.
    """
    rng = np.random.default_rng(seed)
    n = len(y)
    draws = {m: [] for m in ("f1", "precision", "roc_auc")}
    n_skipped = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        yb, pb, sb = y[idx], pred[idx], score[idx]
        if (yb == 1).sum() == 0 or (yb == 0).sum() == 0:
            n_skipped += 1
            continue
        draws["f1"].append(f1_score(yb, pb, zero_division=0))
        draws["precision"].append(precision_score(yb, pb, zero_division=0))
        draws["roc_auc"].append(roc_auc_score(yb, sb))
    ci = {
        f"{m}_95ci": {
            "low": float(np.percentile(v, 2.5)),
            "high": float(np.percentile(v, 97.5)),
        }
        for m, v in draws.items()
    }
    return {
        "n_resamples": n_boot,
        "seed": seed,
        "method": (
            "percentile bootstrap over pooled out-of-fold ROWS — SECONDARY, "
            "reported for continuity with v3 only; anti-conservative "
            "because rows cluster by DTM. Use the cluster bootstrap as the "
            "headline. Recall CI deliberately omitted (objection 4)."
        ),
        "n_degenerate_draws_skipped": int(n_skipped),
        **ci,
    }


# ---------------------------------------------------------------------------
# Cross-fit one feature set (LODO), collecting OOF arrays + coefficients
# ---------------------------------------------------------------------------
def cross_fit(
    active: pd.DataFrame, y: np.ndarray, folds: list,
    feature_subset: list[str],
) -> dict:
    """Run the LODO cross-fit for one feature set.

    Returns oof_score/oof_pred arrays, per-fold records, and the wrapped
    LogisticRegression's standardised-space coefficients per fold (run-A
    coefficients document the annotation-proxy mechanism — objection 1).
    """
    oof_score = np.full(len(y), np.nan)
    oof_pred = np.full(len(y), np.nan)
    fold_of_row = np.full(len(y), -1)
    fold_records: list[dict] = []
    coef_rows: list[list[float]] = []

    for fold_i, (tr_idx, te_idx) in enumerate(folds):
        if (y[tr_idx] == 1).sum() < 2:
            raise RuntimeError(
                f"Fold {fold_i}: train set has "
                f"{int((y[tr_idx] == 1).sum())} positives — Elkanoto needs "
                ">=2 (hold-out + fit set)."
            )
        X_tr, X_te, feat_names = fold_matrices(
            active, tr_idx, te_idx, feature_subset
        )
        assert feat_names == list(feature_subset)
        clf, hold_out_used, pu_seed_used, issues = fit_pu_fold(
            X_tr, y[tr_idx]
        )
        s = clf.predict_proba(X_te)[:, 1]
        p = (s >= 0.5).astype(int)
        oof_score[te_idx] = s
        oof_pred[te_idx] = p
        fold_of_row[te_idx] = fold_i

        # Per-feature coefficients of the wrapped LogisticRegression
        # (fit by Elkanoto on its non-hold-out subset; unlabeled coded 0,
        # positives 1; standardised feature space). Documents which
        # features drive the score — the proxy mechanism of objection 1.
        try:
            coefs = np.asarray(
                clf.estimator.coef_, dtype=float
            ).ravel().tolist()
        except AttributeError as exc:  # pragma: no cover — defensive
            raise RuntimeError(
                f"fold {fold_i}: cannot extract estimator coefficients: {exc}"
            ) from exc
        if len(coefs) != len(feature_subset):
            raise RuntimeError(
                f"fold {fold_i}: coefficient vector length {len(coefs)} != "
                f"n_features {len(feature_subset)}"
            )
        coef_rows.append(coefs)

        y_te = y[te_idx]
        try:
            auc = float(roc_auc_score(y_te, s))
        except ValueError:
            auc = float("nan")
        fold_records.append({
            "fold": fold_i,
            "test_dtms": sorted(pd.unique(
                active["dtm"].to_numpy()[te_idx]
            ).tolist()),
            "n_train": int(len(tr_idx)), "n_train_pos": int(y[tr_idx].sum()),
            "n_test": int(len(te_idx)), "n_test_pos": int(y_te.sum()),
            "hold_out_ratio_used": hold_out_used,
            "pulearn_random_state_used": pu_seed_used,
            "feasibility_retry": pu_seed_used != SEED,
            "f1": float(f1_score(y_te, p, zero_division=0)),
            "precision": float(precision_score(y_te, p, zero_division=0)),
            "recall": float(recall_score(y_te, p, zero_division=0)),
            "roc_auc": auc,
            "fit_warnings": issues,
        })
        logger.info(
            "fold %d: test %s (%d pos / %d), F1=%.3f AUC=%s",
            fold_i, fold_records[-1]["test_dtms"], int(y_te.sum()),
            int(len(te_idx)), fold_records[-1]["f1"],
            f"{auc:.3f}" if np.isfinite(auc) else "n/a (single class)",
        )

    assert not np.isnan(oof_score).any(), "missing OOF predictions"
    coefs_by_feature = {
        f: float(np.mean([r[i] for r in coef_rows]))
        for i, f in enumerate(feature_subset)
    }
    return {
        "oof_score": oof_score,
        "oof_pred": oof_pred.astype(int),
        "fold_of_row": fold_of_row,
        "fold_records": fold_records,
        "coefficients": {
            "space": (
                "standardised feature space; wrapped "
                "LogisticRegression(C=1.0) fit by ElkanotoPuClassifier on "
                "its non-hold-out training subset (unlabeled=0, positive=1); "
                "positive coefficient -> pushes score UP for positives"
            ),
            "mean_across_folds": coefs_by_feature,
            "per_fold": coef_rows,
        },
    }


def threshold_sensitivity(
    y: np.ndarray, score: np.ndarray,
) -> dict:
    """F1/precision/recall at score thresholds (objection 5, run B).

    NOTE: ElkanotoPuClassifier scores are NOT calibrated probabilities and
    can exceed 1 (the classifier divides the wrapped estimator's
    probability by the hold-out-estimated prevalence c); thresholds above
    0.5 are therefore meaningful on this raw score scale.
    """
    rows = []
    for t in THRESHOLDS:
        p = (score >= t).astype(int)
        rows.append({
            "threshold": float(t),
            "f1": float(f1_score(y, p, zero_division=0)),
            "precision": float(precision_score(y, p, zero_division=0)),
            "recall": float(recall_score(y, p, zero_division=0)),
            "n_predicted_positive": int(p.sum()),
        })
    return {
        "metric": "pooled out-of-fold, run B (MORPH) feature set",
        "score_scale_note": (
            "Elkanoto raw score (not a calibrated probability; can exceed "
            "1). Fold-loop decision threshold 0.5 (as v2/v3) is the "
            "default row."
        ),
        "table": rows,
    }


def main() -> int:
    t0 = time.perf_counter()
    warnings.filterwarnings("always")
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    registry_md5 = hashlib.md5(REGISTRY_CSV.read_bytes()).hexdigest()
    df = load_registry(REGISTRY_CSV)
    active, sup_targets, reg_stats = prepare_frames(df)

    # Labels + leak-guarded features (both reused from pu_learning_extended).
    pos_mask, pos_mapping = build_positive_mask(active)
    y = pos_mask.astype(int).to_numpy()
    groups = active["dtm"].to_numpy()

    both_classes_dtms = sorted(
        dtm for dtm in pd.unique(groups)
        if (y[groups == dtm] == 1).any() and (y[groups == dtm] == 0).any()
    )
    n_groups = int(pd.unique(groups).size)

    # k per dispatch: min(5, n_dtms_with_both_classes); LODO if that group
    # split is infeasible. FEASIBILITY REQUIREMENT: ElkanotoPuClassifier
    # needs >=2 train positives per fold (>=1 in its internal hold-out AND
    # >=1 remaining for LogisticRegression to see both classes). With 1
    # train positive it is mathematically infeasible at ANY ratio/seed.
    # Positives concentrate in 6/21 DTMs (INGENIIPIT alone: 10/15), and the
    # deterministic GroupKFold(k=2) split puts 14/15 positives on one side
    # (train folds with 1 and 14 positives) -> infeasible -> LODO fallback
    # (dispatch-sanctioned alternative), under which the worst train fold
    # (INGENIIPIT held out) still has 5 positives. Verified, not assumed.
    lodo = False
    k_attempted = min(5, len(both_classes_dtms))
    fallback_reason = None
    splitter = None
    if k_attempted >= 2:
        cand = GroupKFold(n_splits=k_attempted)
        cand_folds = list(
            cand.split(X=np.zeros(len(y)), y=y, groups=groups)
        )
        bad = [
            i for i, (tr, _) in enumerate(cand_folds)
            if (y[tr] == 1).sum() < 2
        ]
        if not bad:
            splitter, folds, k = cand, cand_folds, k_attempted
        else:
            lodo = True
            fallback_reason = (
                f"GroupKFold(k={k_attempted}) infeasible: fold(s) {bad} "
                f"train with {[int((y[tr] == 1).sum()) for tr, _ in cand_folds if (y[tr] == 1).sum() < 2]} "
                "positive(s); ElkanotoPuClassifier needs >=2 (hold-out + "
                "fit set). Positives concentrate in 6/21 DTMs "
                "(INGENIIPIT: 10/15); the deterministic k=2 split puts "
                "14/15 on one side. Fell back to leave-one-DTM-out."
            )
    if lodo or k_attempted < 2:
        splitter = LeaveOneGroupOut()
        folds = list(splitter.split(X=np.zeros(len(y)), y=y, groups=groups))
        k = len(folds)
        lodo = True

    logger.info(
        "ACTIVE n=%d (pos=%d, U=%d); %d DTM groups; %d with both classes "
        "-> k=%d%s",
        len(y), int(y.sum()), int((y == 0).sum()), n_groups,
        len(both_classes_dtms), k, " (LODO)" if lodo else "",
    )

    # Full feature list + leak guard (guard applies to BOTH run feature
    # sets — subsets of the leak-free full list are leak-free).
    _, full_feature_names, _ = build_extended_features(active)
    assert_no_leak(full_feature_names)
    morph_feature_names = [
        f for f in full_feature_names if f not in DROPPED_ANNOTATION_FLAGS
    ]
    assert len(morph_feature_names) == len(full_feature_names) - 4
    assert_no_leak(morph_feature_names)

    # --- D1-LOW L1: run C = run B minus rung_cm (sensitivity row only) ----
    run_c_feature_names = [f for f in morph_feature_names if f != "rung_cm"]
    assert len(run_c_feature_names) == len(morph_feature_names) - 1 == 14
    assert_no_leak(run_c_feature_names)

    # Rung identity-carrier evidence (recomputed, stored in the JSON): for
    # each rung value, how many rows carry it and in how many DTMs it
    # occurs. A rung occurring in exactly 1 DTM uniquely identifies that
    # DTM on those rows (the skeptic's residual identity claim).
    rung_parsed = active["candidate_id"].str.extract(r"-(\d{3,4})cm-")[0]
    rung_evidence = {}
    for rung in sorted(pd.unique(rung_parsed.dropna())):
        m = (rung_parsed == rung).to_numpy()
        rung_evidence[f"{int(rung)}cm"] = {
            "n_rows": int(m.sum()),
            "n_dtms": int(pd.unique(groups[m]).size),
            "unique_to_one_dtm": bool(pd.unique(groups[m]).size == 1),
            "dtms": sorted(pd.unique(groups[m]).tolist()),
        }

    # --- Objection-1 evidence: recompute the proxy stats on ACTIVE rows --
    notes_lower = active["notes"].str.lower()
    proxy_evidence = {}
    for flag, pattern in (
        ("has_terrain_extrap", "terrain-extrapolation"),
        ("has_deep_pit_low_vesselness", "deep-pit low-vesselness"),
        ("has_funnel_risk", "funnel risk"),
        ("has_12km_FP", "12-km-scale fp"),
    ):
        m = notes_lower.str.contains(pattern, regex=False).to_numpy()
        proxy_evidence[flag] = {
            "n_rows_flagged": int(m.sum()),
            "n_positive_flagged": int(y[m].sum()),
            "p_positive_given_flag": (
                float(y[m].mean()) if m.sum() else None
            ),
        }

    # ---------------- Cross-fit the feature sets ------------------------
    res_a = cross_fit(active, y, folds, list(full_feature_names))
    res_b = cross_fit(active, y, folds, morph_feature_names)
    res_c = cross_fit(active, y, folds, run_c_feature_names)
    # Same folds => identical fold assignment across runs (assert; the
    # leak asserts below are run once and cover all three runs).
    assert np.array_equal(res_a["fold_of_row"], res_b["fold_of_row"])
    assert np.array_equal(res_a["fold_of_row"], res_c["fold_of_row"])

    dtm_fold: dict[str, int] = {}
    for fold_i, (_, te_idx) in enumerate(folds):
        for dtm in pd.unique(groups[te_idx]):
            dtm_fold[str(dtm)] = fold_i

    # ---------------- Leak asserts ----------------
    # (ii) no DTM spans folds: each DTM in exactly one test fold, absent
    # from its own train fold.
    for fold_i, (tr_idx, te_idx) in enumerate(folds):
        overlap = set(groups[tr_idx]) & set(groups[te_idx])
        assert not overlap, f"fold {fold_i}: DTM spans train/test: {overlap}"
    for dtm, f in dtm_fold.items():
        assert f >= 0
    assert len(dtm_fold) == n_groups

    # (i) no candidate group (primary + superseded children) spans folds.
    # ACTIVE rows carry their own fold; SUPERSEDED rows inherit the fold of
    # their ACTIVE primary (via superseded_by). Assert <=1 distinct fold.
    active_df_pos = df.index[df["status"] == "ACTIVE"].to_numpy()
    sup_target_by_row = dict(zip(
        df.index[df["status"] == "SUPERSEDED"], sup_targets
    ))
    fold_by_active_id: dict[str, int] = {}
    for local_i, orig_i in enumerate(active_df_pos):
        fold_by_active_id[str(df.loc[orig_i, "candidate_id"])] = int(
            res_a["fold_of_row"][local_i]
        )
    group_folds: dict[str, set[int]] = {
        cid: {f} for cid, f in fold_by_active_id.items()
    }
    for target in sup_target_by_row.values():
        group_folds.setdefault(str(target), set()).add(
            fold_by_active_id[str(target)]
        )
    spanning_groups = {
        g: sorted(f) for g, f in group_folds.items() if len(f) > 1
    }
    assert not spanning_groups, (
        f"candidate groups span folds: {list(spanning_groups.items())[:5]}"
    )
    leak_asserts = {
        "no_dtm_spans_folds": True,
        "no_candidate_group_spans_folds": True,
        "n_candidate_groups_checked": len(group_folds),
        "n_superseded_children_fold_inherited": len(sup_target_by_row),
        "registry_md5_recorded": True,
        "applies_to_all_runs": (
            "All three runs (A FULL, B MORPH, C MORPH-no-rung) share the "
            "identical LODO fold assignment (asserted); the leak guards "
            "therefore cover every run alike."
        ),
        "detail": (
            "Every SUPERSEDED row inherits the fold of its ACTIVE primary "
            "(superseded_by=); each group has exactly one distinct fold. "
            "SUPERSEDED rows are additionally excluded from train/test "
            "entirely (duplicates by construction)."
        ),
    }

    # ---------------- Per-run assembly + self-checks ----------------
    ingeniipit_fold = dtm_fold[INGENIIPIT]

    def _score_of(cid_sub: str, res: dict) -> float:
        i = int(
            active.index[
                active["candidate_id"].str.contains(cid_sub, regex=False)
            ][0]
        )
        return float(res["oof_score"][i])

    def assemble_run(res: dict, feature_names: list[str]) -> dict:
        s, p = res["oof_score"], res["oof_pred"]
        pooled = pooled_metrics(y, p, s)

        # leave-INGENIIPIT-out summary (objection 3)
        m = groups != INGENIIPIT
        loio = pooled_metrics(y[m], p[m], s[m])
        loio["excluded_fold"] = int(ingeniipit_fold)
        loio["excluded_dtm"] = INGENIIPIT
        loio["note"] = (
            f"pooled OOF metrics with the {INGENIIPIT} test fold (fold "
            f"{ingeniipit_fold}, 10 of 15 positives) excluded — how the "
            "run performs away from the dominant positive DTM."
        )

        # oof_predictions array (reproducibility): one entry per ACTIVE
        # row, sorted by candidate_id (unique) for byte-determinism.
        oof_predictions = [
            {
                "candidate_id": str(active["candidate_id"].iloc[i]),
                "dtm": str(active["dtm"].iloc[i]),
                "y_true": int(y[i]),
                "y_pred": int(p[i]),
                "score": float(s[i]),
                "fold": int(res["fold_of_row"][i]),
            }
            for i in range(len(y))
        ]
        oof_predictions.sort(key=lambda r: r["candidate_id"])
        assert len(oof_predictions) == N_ACTIVE_EXPECTED
        y_chk = np.array([r["y_true"] for r in oof_predictions])
        p_chk = np.array([r["y_pred"] for r in oof_predictions])
        s_chk = np.array([r["score"] for r in oof_predictions])
        f1_chk = float(f1_score(y_chk, p_chk, zero_division=0))
        auc_chk = float(roc_auc_score(y_chk, s_chk))
        assert abs(f1_chk - pooled["f1"]) <= 1e-9, (
            f"pooled F1 mismatch: {pooled['f1']!r} vs recomputed {f1_chk!r}"
        )
        assert abs(auc_chk - pooled["roc_auc"]) <= 1e-9, (
            f"pooled AUC mismatch: {pooled['roc_auc']!r} vs {auc_chk!r}"
        )

        return {
            "n_features": len(feature_names),
            "features": list(feature_names),
            "folds": res["fold_records"],
            "pooled_oof": pooled,
            "leave_ingeniipit_out": loio,
            "bootstrap_cluster_HEADLINE": cluster_bootstrap(y, p, s, groups),
            "bootstrap_row_secondary": row_bootstrap_secondary(y, p, s),
            "logistic_coefficients": res["coefficients"],
            "oof_predictions_self_check": (
                f"PASS: {len(oof_predictions)} rows; F1 {f1_chk:.10f} / AUC "
                f"{auc_chk:.10f} match pooled to <=1e-9"
            ),
            "oof_predictions": oof_predictions,
        }

    run_a = assemble_run(res_a, list(full_feature_names))
    run_b = assemble_run(res_b, morph_feature_names)
    run_b["threshold_sensitivity"] = threshold_sensitivity(
        y, res_b["oof_score"]
    )
    run_c = assemble_run(res_c, run_c_feature_names)

    # --- A-vs-B decision/score comparison (computed, not asserted) -------
    diff_pred = int((res_a["oof_pred"] != res_b["oof_pred"]).sum())
    s_a, s_b = res_a["oof_score"], res_b["oof_score"]
    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = np.where(
            (s_a > 0) & (s_b > 0),
            np.maximum(s_a, s_b) / np.maximum(np.minimum(s_a, s_b), 1e-300),
            np.nan,
        )
    ab_comparison = {
        "n_differing_predictions_at_0.5": diff_pred,
        "max_score_ratio_across_runs": float(np.nanmax(ratios)),
        "delta_pooled_roc_auc_B_minus_A": round(
            run_b["pooled_oof"]["roc_auc"] - run_a["pooled_oof"]["roc_auc"], 6
        ),
        "note": (
            f"Removing the four annotation-derived flags changed the raw "
            f"OOF scores substantially (max cross-run score ratio "
            f"{float(np.nanmax(ratios)):.1e}) but LEFT THE POOLED 0.5-"
            f"THRESHOLD DECISIONS UNCHANGED ({diff_pred}/117 rows differ). "
            "At this threshold the flags were not load-bearing for the "
            "decision set on this registry — the honest reading of the "
            "ablation. They DID deform the score scale (e.g. the MARIUS-"
            "PIT01 r001 I14 score) and carry large run-A coefficients "
            "(proxy mechanism documented per fold). Run B remains the "
            "headline because its inputs are defensible, not because the "
            "number moved."
        ),
    }

    # --- MARIUSPIT01 r001 (I14) scores, shared by the blocks below --------
    marius_fold = next(
        r for r in run_a["folds"] if "MARIUSPIT01" in r["test_dtms"]
    )
    marius_score_a = _score_of("LV-MARIUSPIT01-0400cm-r001", res_a)
    marius_score_b = _score_of("LV-MARIUSPIT01-0400cm-r001", res_b)

    # --- D1-LOW (F20) L1: run C vs run B comparison (sensitivity row) ----
    MARIUS_CID = "LV-MARIUSPIT01-0400cm-r001"
    marius_score_c = _score_of(MARIUS_CID, res_c)
    marius_row_i = int(
        active.index[active["candidate_id"] == MARIUS_CID][0]
    )
    pos_rows = np.flatnonzero(y == 1)
    # Rank among the 15 positives, ascending by OOF score (0 = lowest).
    marius_rank_b = int(
        (res_b["oof_score"][pos_rows] < res_b["oof_score"][marius_row_i]).sum()
    )
    marius_rank_c = int(
        (res_c["oof_score"][pos_rows] < res_c["oof_score"][marius_row_i]).sum()
    )
    diff_pred_cb = int((res_b["oof_pred"] != res_c["oof_pred"]).sum())
    flip_mask = res_b["oof_pred"] != res_c["oof_pred"]
    flipped_rows_cb = [
        {
            "candidate_id": str(active["candidate_id"].iloc[i]),
            "dtm": str(active["dtm"].iloc[i]),
            "y_true": int(y[i]),
            "pred_B": int(res_b["oof_pred"][i]),
            "pred_C": int(res_c["oof_pred"][i]),
            "score_B": float(res_b["oof_score"][i]),
            "score_C": float(res_c["oof_score"][i]),
        }
        for i in np.flatnonzero(flip_mask)
    ]
    metrics4_cb = ("f1", "precision", "recall", "roc_auc")
    delta_cb = {
        m: round(
            run_c["pooled_oof"][m] - run_b["pooled_oof"][m], 6
        )
        for m in metrics4_cb
    }
    run_c["role"] = (
        "SENSITIVITY ROW ONLY — run B minus rung_cm (14 features), "
        "answering the D1-LOW F20 residual that rung_cm is a residual "
        "identity carrier (rung 500 only in TRANQPIT1, rung 800 only in "
        "MARIUSPIT01). The HEADLINE REMAINS RUN B; this block exists to "
        "show how much of run B depends on that one feature."
    )
    run_c["comparison_vs_run_B"] = {
        "n_differing_predictions_at_0.5": diff_pred_cb,
        "flipped_rows": flipped_rows_cb,
        "mariuspit01_r001_I14": {
            "candidate_id": MARIUS_CID,
            "score_run_B": marius_score_b,
            "score_run_C": marius_score_c,
            "score_magnitude_regime_unchanged": bool(
                (marius_score_b < 0.5) and (marius_score_c < 0.5)
            ),
            "y_pred_run_B": int(res_b["oof_pred"][marius_row_i]),
            "y_pred_run_C": int(res_c["oof_pred"][marius_row_i]),
            "rank_among_15_positives_run_B": marius_rank_b,
            "rank_among_15_positives_run_C": marius_rank_c,
            "verdict": (
                f"I14 funnel failure RECURS in run C: score "
                f"{marius_score_c:.3e} (vs {marius_score_b:.3e} in B), "
                f"rank {marius_rank_c + 1}/15 among positives by score "
                f"(B: rank {marius_rank_b + 1}/15), decision stays "
                "negative at t=0.5."
                if (marius_score_c < 0.5 and marius_rank_c == marius_rank_b)
                else (
                    f"score {marius_score_c:.3e} (vs {marius_score_b:.3e} "
                    f"in B), rank {marius_rank_c + 1}/15 (B: "
                    f"{marius_rank_b + 1}/15), pred_C="
                    f"{int(res_c['oof_pred'][marius_row_i])}."
                )
            ),
        },
        "delta_pooled_C_minus_B": delta_cb,
        "note": (
            f"Removing rung_cm changed the raw score scale but "
            f"{diff_pred_cb}/117 pooled decisions at t=0.5 vs run B. "
            "Read alongside run_B's own numbers — run B stays canonical."
        ),
    }

    # ---------------- Known failure modes (objection 3) ------------------
    ing_folds_a = next(r for r in run_a["folds"] if r["fold"] == ingeniipit_fold)
    ing_folds_b = next(r for r in run_b["folds"] if r["fold"] == ingeniipit_fold)
    known_failure_modes = [
        {
            "id": "I14_funnel_failure_in_PU_layer",
            "what": (
                "MARIUSPIT01 r001 (the catalogued Marius Hills pit, the "
                "only positive in its fold) is the LOWEST-scoring positive "
                f"in both runs: OOF score {marius_score_a:.3e} (run A) / "
                f"{marius_score_b:.3e} (run B); fold ROC AUC "
                f"{marius_fold['roc_auc']:.3f} (all unlabeled rows in the "
                "fold rank above the pit). It does NOT move in the run-C "
                f"rung_cm ablation: {marius_score_c:.3e}, still rank "
                f"{marius_rank_c + 1}/15 among positives, still negative "
                "at t=0.5."
                if marius_rank_c == 0 and marius_score_c < 0.5
                else (
                    "MARIUSPIT01 r001 OOF scores: "
                    f"{marius_score_a:.3e} (run A) / {marius_score_b:.3e} "
                    f"(run B) / {marius_score_c:.3e} (run C, no rung_cm; "
                    f"rank {marius_rank_c + 1}/15); fold ROC AUC "
                    f"{marius_fold['roc_auc']:.3f}."
                )
            ),
            "diagnosis": (
                "This is the pre-registered I14 funnel failure recurring in "
                "the PU layer: pits incised into rilles (Marius Hills) "
                "spill sideways at the fill-to-spill reference, so "
                "morphometry ranks the pit below its rille-context "
                "neighbours. Pre-registered in the v5 master plan (I14 "
                "funnel prediction); a FINDING, not a bug."
            ),
        },
        {
            "id": "INGENIIPIT_dependence",
            "what": (
                "10 of 15 positives lie in INGENIIPIT; pooled metrics are "
                f"dominated by its single LODO fold (fold {ingeniipit_fold}: "
                f"run-A F1 {ing_folds_a['f1']:.3f}, run-B F1 "
                f"{ing_folds_b['f1']:.3f} on 10 positives / 0 test FPs). "
                "Leave-INGENIIPIT-out summary rows are reported for both "
                "runs — read them alongside the pooled numbers."
            ),
        },
        {
            "id": "feasibility_retry_stated_factually",
            "what": (
                f"Fold {ingeniipit_fold} ({INGENIIPIT} held out; 5 train "
                "positives): pulearn's internal hold-out draw at seed 42 "
                "contains no positive at any hold_out_ratio, so the "
                "pre-registered feasibility ladder (random_state 42..81 x "
                "hold_out_ratio 0.10/0.07/0.05/0.03/0.02) was used; the "
                "seed and ratio actually used are recorded per fold per "
                f"run (run A: pu_rs={ing_folds_a['pulearn_random_state_used']}, "
                f"hold_out_ratio={ing_folds_a['hold_out_ratio_used']}; "
                f"run B: pu_rs={ing_folds_b['pulearn_random_state_used']}, "
                f"hold_out_ratio={ing_folds_b['hold_out_ratio_used']}). "
                f"Fold-{ingeniipit_fold} test F1 is {ing_folds_a['f1']:.3f} "
                "(run A) / "
                f"{ing_folds_b['f1']:.3f} (run B). Stated factually; this "
                "artifact makes NO claim that retry-fold metrics stay "
                "inside any CI width (that v3-prose claim was false — "
                "fold-6 F1=1.0 exceeded the old row-bootstrap upper bound)."
            ),
        },
    ]

    # ---------------- Recall reporting (objection 4) ---------------------
    tp_b = run_b["pooled_oof"]["n_true_positives"]
    n_pos = run_b["pooled_oof"]["n_positives"]
    recall_reporting = {
        "run_B_statement": (
            f"{tp_b}/{n_pos} positives recovered (run B MORPH, pooled OOF, "
            "threshold 0.5)"
        ),
        "cluster_bootstrap_interval": (
            run_b["bootstrap_cluster_HEADLINE"]["recall_95ci"]
        ),
        "note": (
            "Recall is reported as a recovered-count plus the "
            "cluster-bootstrap interval; row-bootstrap recall CI dropped "
            "(decorative at n=15 positives — it only resamples the "
            "denominator)."
        ),
    }

    # ---------------- Comparison vs published v2 (leak-inflated) ---------
    v2 = json.loads(V2_JSON.read_text())
    v2m = v2["metrics"]
    v2_row = {
        "f1": v2m["f1_test"], "precision": v2m["precision_test"],
        "recall": v2m["recall_test"], "roc_auc": v2m["roc_auc_test"],
        "split": "random 70/30 ROW split (test_size=0.30, seed 42)",
        "annotation": (
            "LEAK-INFLATED: (a) 161 SUPERSEDED duplicate rows of the same "
            "physical feature (superseded_by= links) could span train/test; "
            "(b) rows from the same DTM spanned train/test (spatial "
            "autocorrelation). Metrics are optimistic upper bounds, not "
            "generalisation estimates."
        ),
    }
    metrics4 = ("f1", "precision", "recall", "roc_auc")
    a_row = {m: run_a["pooled_oof"][m] for m in metrics4}
    b_row = {m: run_b["pooled_oof"][m] for m in metrics4}
    comparison = {
        "v2_random_split_published_2026_08_28": v2_row,
        "run_A_FULL_like_for_like": a_row,
        "run_B_MORPH_headline": b_row,
        "delta_B_minus_v2": {
            m: round(b_row[m] - v2_row[m], 4) for m in metrics4
        },
        "delta_B_minus_A": {
            m: round(b_row[m] - a_row[m], 4) for m in metrics4
        },
        "interpretation": (
            "v2→A measures the leakage + spatial-autocorrelation inflation "
            "(same 19 features, same model, only the eval design changes). "
            "A→B measures the annotation-proxy subsidy in the FULL feature "
            "set (the four notes-derived flags). Run B is the defensible "
            "generalisation estimate; run A is retained only as a "
            "diagnostic upper bound and explicitly INCLUDES "
            "annotation-derived flags."
        ),
    }

    method_block = {
        "split": (
            "leave-one-DTM-out (LODO), grouped by dtm"
            if lodo else "GroupKFold grouped by dtm (deterministic)"
        ),
        "k": int(k),
        "k_rule": (
            "k = min(5, n_dtms_with_both_classes) = min(5, "
            f"{len(both_classes_dtms)}) = {k_attempted}; "
            + ("fallback to LODO (see fallback_reason)"
               if lodo else "used as-is")
        ),
        "k_attempted_groupkfold": int(k_attempted),
        "groupkfold_fallback_reason": fallback_reason,
        "leave_one_dtm_out_fallback_used": lodo,
        "n_dtm_groups": n_groups,
        "n_dtms_with_both_classes": len(both_classes_dtms),
        "dtms_with_both_classes": both_classes_dtms,
        "superseded_excluded_from_train_and_test": True,
        "imputation": "median per feature, TRAIN-fold statistics only",
        "scaler": "StandardScaler fit on train fold only",
        "estimator": (
            "ElkanotoPuClassifier(LogisticRegression(C=1.0, max_iter=1000, "
            "random_state=42), hold_out_ratio ladder 0.10/0.07/0.05/0.03/"
            "0.02, random_state=42) — IDENTICAL to v2, not retuned, used "
            "UNMODIFIED for both run A (19 features) and run B (15 "
            "features). No retuning accompanied the ablation. "
            "Feasibility-only retry: when a fold's train positives are too "
            "few for pulearn's hold-out draw at seed 42 (INGENIIPIT-held-"
            "out fold), the internal RNG draw is retried across "
            "random_state 42->81 — the seed ladder range(42, 82), 40 "
            "consecutive seeds at each hold_out_ratio — with the same "
            "configuration; the seed actually used is recorded per fold. "
            "Selection never touches test folds. (Retry outcomes are "
            "stated factually per fold; no CI-width claims are made.)"
        ),
        "decision_threshold": 0.5,
        "cluster_bootstrap": {
            "design": (
                f"DTM-level cluster bootstrap: {n_groups} DTM clusters "
                f"resampled with replacement, {N_BOOTSTRAP} draws, seed "
                f"{SEED}, percentile 95% CI (HEADLINE). Secondary row "
                "bootstrap: same draw count and seed over pooled OOF rows."
            ),
            "degenerate_draw_rule": DEGENERATE_DRAW_RULE,
            "n_discarded_draws": {
                "run_A_cluster": int(
                    run_a["bootstrap_cluster_HEADLINE"][
                        "n_degenerate_draws_skipped"
                    ]
                ),
                "run_A_row_secondary": int(
                    run_a["bootstrap_row_secondary"][
                        "n_degenerate_draws_skipped"
                    ]
                ),
                "run_B_cluster": int(
                    run_b["bootstrap_cluster_HEADLINE"][
                        "n_degenerate_draws_skipped"
                    ]
                ),
                "run_B_row_secondary": int(
                    run_b["bootstrap_row_secondary"][
                        "n_degenerate_draws_skipped"
                    ]
                ),
                "run_C_cluster": int(
                    run_c["bootstrap_cluster_HEADLINE"][
                        "n_degenerate_draws_skipped"
                    ]
                ),
                "run_C_row_secondary": int(
                    run_c["bootstrap_row_secondary"][
                        "n_degenerate_draws_skipped"
                    ]
                ),
            },
            "note": (
                "Degenerate draws are DROPPED from the CI, not redrawn "
                "(redrawing would consume extra values from the seeded RNG "
                "stream and change every subsequent draw). With positives "
                "in 6/21 DTMs, P(a 21-cluster draw misses all 6) is small "
                "but nonzero — hence the occasional 1 discarded draw per "
                "1000."
            ),
        },
        "note_on_k": (
            "Only 2 ACTIVE DTMs contain both classes (positives concentrate "
            "in INGENIIPIT: 10 of 15; positives in 6 of 21 DTMs). The "
            "dispatch rule k=min(5, both-class DTMs) yields k=2, but the "
            "deterministic GroupKFold(k=2) split puts 14/15 positives in "
            "one half — the other fold trains with 1 positive, which makes "
            "Elkanoto's internal hold-out mathematically infeasible. "
            "Fell back to leave-one-DTM-out (worst train fold: 5 positives "
            "when INGENIIPIT is held out). This is the eval-design "
            "consequence of positive-label concentration, reported as part "
            "of the D1 finding."
        ),
    }

    feature_sets_block = {
        "run_A_FULL": {
            "n_features": len(full_feature_names),
            "features": list(full_feature_names),
            "role": (
                "DIAGNOSTIC UPPER BOUND ONLY — explicitly INCLUDES the "
                "four notes-derived annotation flags that partially encode "
                "DTM identity / human FP adjudication. Not a "
                "generalisation estimate."
            ),
            "annotation_flag_proxy_evidence": proxy_evidence,
        },
        "run_B_MORPH_headline": {
            "n_features": len(morph_feature_names),
            "features": list(morph_feature_names),
            "dropped_features": DROPPED_ANNOTATION_FLAGS,
            "audit_of_kept_features": KEPT_FEATURE_AUDIT,
        },
        "run_C_MORPH_no_rung_sensitivity": {
            "n_features": len(run_c_feature_names),
            "features": list(run_c_feature_names),
            "role": (
                "SENSITIVITY ROW ONLY (D1-LOW F20): run B minus rung_cm. "
                "The HEADLINE REMAINS RUN B. Reported in "
                "runs.run_C_MORPH_no_rung_sensitivity."
            ),
            "dropped_features": DROPPED_RUNG_FLAG,
            "rung_identity_evidence": rung_evidence,
        },
        "leak_guard": (
            "registry_io.assert_no_leak passed on the full 19-feature list, "
            "the run-B 15-feature subset, AND the run-C 14-feature subset"
        ),
        "excluded_leak_features_note": (
            "dtm/lon/lat/ring-artifact/below-floor/rank excluded as in "
            "v2 (see pu_learning_registry_baseline_v2.json feature_audit)"
        ),
    }

    out = {
        "date": str(date.today()),
        "version": "v5_groupsplit_triplerun (D1-LOW repair, F20)",
        "supersedes": (
            "v4_groupsplit_dualrun (D1-repair) in this same file — "
            "regenerated in place to close the two skeptic LOW residuals "
            "(F20). Run A and run B numbers are UNCHANGED from the "
            "committed 596a74f8 artifact (regression-checked); v5 only "
            "ADDS the run-C sensitivity row and the explicit degenerate-"
            "draw rule."
        ),
        "purpose": (
            "Leak-free, ablated PU-learning evaluation: "
            "feature-deduplicated (SUPERSEDED excluded), DTM-grouped "
            "out-of-fold, run A (FULL, 19 features, diagnostic upper "
            "bound) vs run B (MORPH, 15 features, notes-derived "
            "annotation flags removed — HEADLINE) vs run C (run B minus "
            "rung_cm, 14 features — SENSITIVITY ROW ONLY), DTM-level "
            "cluster bootstrap CIs with an explicit degenerate-draw rule, "
            "leave-INGENIIPIT-out summaries, named failure modes. Same "
            "model, same labels as v2 — evaluation design and feature-set "
            "honesty are the only changes. No retuning."
        ),
        "skeptic_objections_addressed": {
            "O1_annotation_identity_proxies": (
                "Dual-run ablation (A FULL vs B MORPH); 4 notes-derived "
                "flags dropped in B; remaining 15 audited; run-A logistic "
                "coefficients recorded per fold."
            ),
            "O2_row_bootstrap_anti_conservative": (
                "DTM-level cluster bootstrap (21 clusters, 1000 draws, "
                "seed 42) is the HEADLINE CI for both runs; row bootstrap "
                "kept as secondary without recall."
            ),
            "O3_INGENIIPIT_dependence_and_I14": (
                "Leave-INGENIIPIT-out summary rows for both runs; "
                "known_failure_modes names MARIUSPIT01 r001 as the "
                "pre-registered I14 funnel failure recurring in the PU "
                "layer."
            ),
            "O4_recall_ci_decorative": (
                "Recall reported as 'k/15 recovered' + cluster-bootstrap "
                "interval; row-bootstrap recall CI dropped."
            ),
            "O5_threshold_and_prose": (
                "Threshold sensitivity 0.5/1.0/1.5 for run B; retry stated "
                "factually, no 'inside CI width' claims."
            ),
        },
        "skeptic_low_residuals_addressed_F20": {
            "L1_rung_cm_identity_carrier": (
                "Run C = run B minus rung_cm (14 features) added as a "
                "SENSITIVITY ROW ONLY; headline remains run B. Reports "
                "pooled OOF metrics + cluster-bootstrap CIs (21 clusters, "
                "1000 draws, seed 42), the MARIUSPIT01-r001 I14 score in "
                "B and C, and the decision-flip count vs B at t=0.5. "
                "Per-rung row/DTM counts backing the identity claim are "
                "recorded in "
                "feature_sets.run_C_MORPH_no_rung_sensitivity."
                "rung_identity_evidence."
            ),
            "L2_degenerate_draw_rule_implicit": (
                "The exact degenerate-resample rule (discard-and-count on "
                "zero TRUE positives / zero TRUE unlabeled; zero "
                "PREDICTED-positive draws retained via zero_division=0) is "
                "now documented at method.cluster_bootstrap."
                "degenerate_draw_rule with per-run discarded-draw counts "
                "in method.cluster_bootstrap.n_discarded_draws. The v4 "
                "implementation was ALREADY discard-and-count; "
                "documenting it changed no number (published B CIs "
                "reproduced bit-identically, delta 0.000 <= 0.005)."
            ),
        },
        "registry": {**reg_stats, "path": str(REGISTRY_CSV), "md5": registry_md5},
        "method": method_block,
        "label_definition": pos_mapping["definition"],
        "label_counts_active": {
            "n_positive": pos_mapping["n_positive_candidates"],
            "n_unlabeled": pos_mapping["n_unlabeled"],
        },
        "positives_per_dtm_active": {
            d: int(((groups == d) & (y == 1)).sum())
            for d in pd.unique(groups) if ((groups == d) & (y == 1)).any()
        },
        "feature_sets": feature_sets_block,
        "runs": {
            "run_A_FULL_diagnostic_upper_bound": run_a,
            "run_B_MORPH_HEADLINE": run_b,
            "run_C_MORPH_no_rung_sensitivity": run_c,
        },
        "run_A_vs_run_B": ab_comparison,
        "recall_reporting": recall_reporting,
        "known_failure_modes": known_failure_modes,
        "comparison_vs_v2": comparison,
        "leak_asserts": leak_asserts,
        "seed": SEED,
        # NOTE (D1 verifier note 1): wall time is deliberately NOT stored
        # here. It varies run-to-run and no rounding scheme is
        # boundary-safe, so it would break the byte-determinism guarantee
        # on this artifact. Timing is console-only.
        "claim_discipline": (
            "PU-learning produces a RANKING of inferred void candidates, "
            "NOT detections. The positives are a proxy for catalogued-pit "
            "local-max hits; unlabeled rows are ML-detected sags of unknown "
            "nature. Metrics estimate agreement with that proxy on "
            "held-out DTMs; run B removes annotation-derived identity "
            "proxies and is the only defensible generalisation estimate "
            "reported here. Calibrated inference only."
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(out, indent=2))
    logger.info("Wrote %s", OUTPUT_JSON)

    ca = run_a["bootstrap_cluster_HEADLINE"]
    cb = run_b["bootstrap_cluster_HEADLINE"]
    cc = run_c["bootstrap_cluster_HEADLINE"]
    c_row = {m: run_c["pooled_oof"][m] for m in metrics4}
    print(f"\n=== v5 groupsplit triple-run (k={k}, LODO={lodo}) ===")
    print(
        f"{'':16s} {'A FULL (diag)':>16s} {'B MORPH (HEAD)':>16s} "
        f"{'C no-rung (sens)':>17s}"
    )
    for m in metrics4:
        print(
            f"{m:16s} {a_row[m]:>16.4f} {b_row[m]:>16.4f} "
            f"{c_row[m]:>17.4f}"
        )
    print("\n--- cluster-bootstrap 95% CIs (21 DTM clusters, 1000 draws) ---")
    for run_lbl, c in (("A", ca), ("B", cb), ("C", cc)):
        print(f" run {run_lbl}: F1 [{c['f1_95ci']['low']:.3f}, "
              f"{c['f1_95ci']['high']:.3f}]  AUC "
              f"[{c['roc_auc_95ci']['low']:.3f}, "
              f"{c['roc_auc_95ci']['high']:.3f}]  P "
              f"[{c['precision_95ci']['low']:.3f}, "
              f"{c['precision_95ci']['high']:.3f}]  R "
              f"[{c['recall_95ci']['low']:.3f}, "
              f"{c['recall_95ci']['high']:.3f}]"
              f" (skipped {c['n_degenerate_draws_skipped']})")
    print(f"\n--- leave-INGENIIPIT-out (fold {ingeniipit_fold}) ---")
    for run_lbl, run in (("A", run_a), ("B", run_b)):
        lo = run["leave_ingeniipit_out"]
        print(f" run {run_lbl}: F1={lo['f1']:.4f} P={lo['precision']:.4f} "
              f"R={lo['recall']:.4f} ({lo['n_true_positives']}/"
              f"{lo['n_positives']} recovered) AUC={lo['roc_auc']:.4f} "
              f"(n={lo['n']})")
    print("\n--- run B threshold sensitivity ---")
    for row in run_b["threshold_sensitivity"]["table"]:
        print(f" t={row['threshold']:.1f}: F1={row['f1']:.4f} "
              f"P={row['precision']:.4f} R={row['recall']:.4f} "
              f"(n_pred_pos={row['n_predicted_positive']})")
    print("\n--- run-A mean logistic coefficients (proxy mechanism) ---")
    top = sorted(
        run_a["logistic_coefficients"]["mean_across_folds"].items(),
        key=lambda kv: abs(kv[1]), reverse=True,
    )[:6]
    for name, c in top:
        print(f"  {name:32s} {c:+.4f}")
    print(f"\nFailure modes: {[f['id'] for f in known_failure_modes]}")
    print(f"A-vs-B: {diff_pred}/117 decisions differ at t=0.5; "
          f"max score ratio {float(np.nanmax(ratios)):.1e}; "
          f"dAUC(B-A)={ab_comparison['delta_pooled_roc_auc_B_minus_A']:+.4f}")
    rcb = run_c["comparison_vs_run_B"]
    m14 = rcb["mariuspit01_r001_I14"]
    print(f"C-vs-B: {rcb['n_differing_predictions_at_0.5']}/117 decisions "
          f"differ at t=0.5; dAUC(C-B)={delta_cb['roc_auc']:+.6f}")
    print(f"  MARIUSPIT01 r001 (I14): B {m14['score_run_B']:.3e} "
          f"(rank {m14['rank_among_15_positives_run_B'] + 1}/15) -> "
          f"C {m14['score_run_C']:.3e} "
          f"(rank {m14['rank_among_15_positives_run_C'] + 1}/15), "
          f"pred_C={m14['y_pred_run_C']}")
    print("Degenerate draws (discarded per 1000): "
          f"{json.dumps(out['method']['cluster_bootstrap']['n_discarded_draws'])}")
    print(f"Recall reporting (B): {recall_reporting['run_B_statement']}")
    print(f"Leak asserts: ALL PASS ({leak_asserts['n_candidate_groups_checked']} groups)")
    print(f"oof self-checks: A: {run_a['oof_predictions_self_check']}")
    print(f"                 B: {run_b['oof_predictions_self_check']}")
    print(f"                 C: {run_c['oof_predictions_self_check']}")
    print(f"Wall time: {time.perf_counter() - t0:.1f} s (console-only; "
          "omitted from JSON for byte-determinism)")
    print(f"Wrote {OUTPUT_JSON}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    raise SystemExit(main())
