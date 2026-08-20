"""Z3 hierarchical fusion prototype (Task 21) — CPU-feasible v0.1.

A simple hierarchical logistic-regression stack of evidence layers at
the LLTB-1 ground-truth cells. The point is to demonstrate that the
*fusion* (multi-layer weighted combination) beats any single-stream
baseline on calibrated metrics — the v5 Gate G3 claim, run on a
held-out cell split.

Features (per v5 Section 3 evidence hierarchy):
  - depth_m  (Planchon-Darboux, master 0.5 m DTM)
  - frangi   (vesselness 30-300 m)
  - vci      (height-binned Shannon evenness, optional)
  - grail    (GRAIL gradient magnitude at 0.25 deg — bucketised)
  - diviner  (placeholder, same as grail for v0.1)

Target: void vs background, defined by the LLTB-1 ground-truth mask.

Model: scikit-learn LogisticRegression with class_weight='balanced',
split 50/50 cell-stratified, report P/R/F1 + ROC-AUC + Brier score
(calibration).

CLI:
  fusion.py --npz path/to/analog.npz --grail-dir 01_WORKSPACE/data/outputs/wp3_fusion
            --depth path/to/depth.tif --frangi path/to/frangi.tif
            --outdir 01_WORKSPACE/data/outputs/wp3_fusion/result
            [--vci path/to/vci.tif]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import Affine
from scipy.ndimage import zoom
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss, f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split

# ---- feature engineering helpers (duplicated from sag_detect) ----------


def cloud_ground_truth(x, y, z, pixel: float, threshold_depth: float = 1.0):
    """Boolean raster of cells containing a point >threshold_depth BELOW
    the local surface envelope (= 'this cell is above a void').

    Surface envelope = nan-robust 50th-percentile over a 21x21 cell
    window (~5-10x the largest expected void cell). Robust against
    flat mare panels with sparse outliers.
    """
    finite = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[finite], y[finite], z[finite]
    x_min, y_min = x.min(), y.min()
    x_max, y_max = x.max(), y.max()
    nx = max(1, int(np.ceil((x_max - x_min) / pixel)))
    ny = max(1, int(np.ceil((y_max - y_min) / pixel)))
    col = np.clip(((x - x_min) / pixel).astype(int), 0, nx - 1)
    row = np.clip(((y - y_min) / pixel).astype(int), 0, ny - 1)
    flat = row * nx + col
    sums = np.bincount(flat, weights=z, minlength=ny * nx)
    cnts = np.bincount(flat, minlength=ny * nx)
    zmin = np.full(ny * nx, np.inf)
    np.minimum.at(zmin, flat, z)
    zmin = zmin.reshape(ny, nx)
    zmin[cnts.reshape(ny, nx) == 0] = np.nan
    from scipy.ndimage import generic_filter
    def nan_pct(arr):
        v = arr[np.isfinite(arr)]
        return np.percentile(v, 50) if len(v) else np.nan
    env = generic_filter(np.where(np.isfinite(zmin), zmin, np.nan),
                         nan_pct, size=21, mode="nearest")
    void_above = (env - zmin) > threshold_depth
    void_above &= np.isfinite(zmin) & np.isfinite(env)
    return void_above, (x_min, y_min, nx, ny, pixel)


def f1_at_threshold(scores: np.ndarray, truth: np.ndarray, thr: float):
    pred = scores >= thr
    tp = int((pred & truth).sum())
    fp = int((pred & ~truth).sum())
    fn = int((~pred & truth).sum())
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"thr": float(thr), "tp": tp, "fp": fp, "fn": fn,
            "precision": prec, "recall": rec, "f1": f1}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--npz", type=Path, required=True)
    p.add_argument("--depth", type=Path, required=True)
    p.add_argument("--frangi", type=Path, required=True)
    p.add_argument("--vci", type=Path, default=None)
    p.add_argument("--grail-dir", type=Path, default=None)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--grid-spacing", type=float, default=0.5)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    data = np.load(args.npz)
    x, y, z = data["x"], data["y"], data["z"]
    gt, gt_geo = cloud_ground_truth(x, y, z, args.grid_spacing)
    x_min, y_min, nx, ny, px = gt_geo
    print(f"[gt ] {ny}x{nx}, void cells = {gt.sum()}", flush=True)

    def load_band(path, target_shape):
        if path is None:
            return np.zeros(target_shape, dtype=np.float32)
        with rasterio.open(path) as s:
            arr = s.read(1).astype(np.float32)
            nodata = s.nodata
        if nodata is not None:
            arr = np.where(arr == nodata, np.nan, arr)
        if arr.shape != target_shape:
            sh, sw = target_shape
            oh, ow = arr.shape
            arr = zoom(arr, (sh / oh, sw / ow), order=1)
        return arr

    depth = load_band(args.depth, (ny, nx))
    frangi = load_band(args.frangi, (ny, nx))
    vci = load_band(args.vci, (ny, nx)) if args.vci else None
    # GRAIL: same lonlat frame as the cloud (local); for the analog
    # site, this is approximate; v0.1 uses a uniform placeholder
    # that simply adds a low-frequency signal.
    grail = np.zeros((ny, nx), dtype=np.float32)
    if args.grail_dir:
        # if the dir has a gmag .tif overlapping, use it; else zero
        candidates = sorted(args.grail_dir.glob("grail_gmag_*.tif"))
        if candidates:
            grail = load_band(candidates[0], (ny, nx))
    # Diviner placeholder
    diviner = np.zeros((ny, nx), dtype=np.float32)

    # flatten
    valid = np.isfinite(depth) & np.isfinite(frangi)
    if vci is not None and vci.any():
        valid &= np.isfinite(vci)
    if grail.any():
        valid &= np.isfinite(grail)
    flat_idx = np.argwhere(valid)
    n = len(flat_idx)
    if n < 100:
        raise SystemExit(f"too few valid cells: {n}")
    X = np.column_stack([
        depth[flat_idx[:, 0], flat_idx[:, 1]],
        frangi[flat_idx[:, 0], flat_idx[:, 1]],
        vci[flat_idx[:, 0], flat_idx[:, 1]] if vci is not None and vci.any() else np.zeros(n),
        grail[flat_idx[:, 0], flat_idx[:, 1]] if grail.any() else np.zeros(n),
        diviner[flat_idx[:, 0], flat_idx[:, 1]],
    ])
    y = gt[flat_idx[:, 0], flat_idx[:, 1]].astype(int)
    print(f"[data] {n} cells, {y.sum()} positives ({y.mean():.2%})", flush=True)
    # normalise features (z-score)
    Xn = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)

    Xtr, Xte, ytr, yte = train_test_split(
        Xn, y, test_size=0.5, random_state=args.seed, stratify=y
    )
    # baselines: each single feature as a 1-D logistic
    rows = []
    for i, name in enumerate(["depth", "frangi", "vci", "grail", "diviner"]):
        m = LogisticRegression(class_weight="balanced", max_iter=200).fit(Xtr[:, [i]], ytr)
        p = m.predict_proba(Xte[:, [i]])[:, 1]
        rows.append({
            "feature": name,
            "auc": float(roc_auc_score(yte, p)),
            "f1": float(f1_score(yte, (p > 0.5).astype(int), zero_division=0)),
            "precision": float(precision_score(yte, (p > 0.5).astype(int), zero_division=0)),
            "recall": float(recall_score(yte, (p > 0.5).astype(int), zero_division=0)),
            "brier": float(brier_score_loss(yte, p)),
        })
    # full model: all 5 features
    m = LogisticRegression(class_weight="balanced", max_iter=200).fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    rows.append({
        "feature": "FUSION (all 5)",
        "auc": float(roc_auc_score(yte, p)),
        "f1": float(f1_score(yte, (p > 0.5).astype(int), zero_division=0)),
        "precision": float(precision_score(yte, (p > 0.5).astype(int), zero_division=0)),
        "recall": float(recall_score(yte, (p > 0.5).astype(int), zero_division=0)),
        "brier": float(brier_score_loss(yte, p)),
    })
    df = pd.DataFrame(rows)
    df.to_csv(args.outdir / "fusion_metrics.csv", index=False)
    print(df.to_string(index=False))
    # figure: ROC + calibration
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    from sklearn.metrics import roc_curve
    for i, name in enumerate(["depth", "frangi", "vci", "grail", "diviner", "FUSION"]):
        if name == "FUSION":
            xx = Xte; pm = m.predict_proba(xx)[:, 1]
        else:
            mm = LogisticRegression(class_weight="balanced", max_iter=200).fit(Xtr[:, [i]], ytr)
            pm = mm.predict_proba(Xte[:, [i]])[:, 1]
        fpr, tpr, _ = roc_curve(yte, pm)
        ax[0].plot(fpr, tpr, label=name, lw=2 if name == "FUSION" else 1)
    ax[0].plot([0, 1], [0, 1], "k--", lw=0.5)
    ax[0].set_xlabel("FPR"); ax[0].set_ylabel("TPR"); ax[0].set_title("ROC (test split)")
    ax[0].legend(fontsize=8)
    # calibration: bin predicted probs and plot mean predicted vs mean observed
    bins = np.linspace(0, 1, 11)
    bin_centres = 0.5 * (bins[1:] + bins[:-1])
    obs = []
    prd = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m_ = (p >= lo) & (p < hi)
        if m_.any():
            obs.append(yte[m_].mean())
            prd.append(p[m_].mean())
    ax[1].plot([0, 1], [0, 1], "k--", lw=0.5)
    ax[1].scatter(prd, obs, color="#1f78b4", s=40)
    ax[1].set_xlabel("mean predicted P(void)"); ax[1].set_ylabel("observed rate")
    ax[1].set_title("Calibration (10-bin reliability)")
    fig.suptitle(f"Z3 fusion prototype — {args.npz.name}")
    fig.tight_layout()
    fig.savefig(args.outdir / "fusion_eval.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[out] figure -> {args.outdir / 'fusion_eval.png'}")

    with open(args.outdir / "fusion_summary.json", "w") as f:
        json.dump({
            "n_cells": int(n),
            "n_pos": int(y.sum()),
            "features": ["depth", "frangi", "vci", "grail", "diviner"],
            "metrics": rows,
        }, f, indent=2)


if __name__ == "__main__":
    main()
