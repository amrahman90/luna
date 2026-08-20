"""End-to-end smoke test of the LLTB-1 + Z2 + Z3 code path on a
SYNTHETIC analog point cloud (a low-resolution but realistic-looking
synthetic ground surface with a single buried void footprint).

This is NOT a real result — it exists to verify the modules wire up
correctly. Run after any major module change.

Usage:
  python -m smoke_test                          # uses defaults
  python -m smoke_test --rungs 0.5 2 5          # change rungs
  python -m smoke_test --outdir /tmp/smoke      # redirect outputs
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def make_synthetic_cloud(n_xy: int = 200, grid_spacing: float = 0.25,
                         void_radius: float = 4.0,
                         void_depth: float = 5.0,
                         rng_seed: int = 42) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return (x, y, z, void_mask) for a synthetic flat-mare surface
    with a single circular void footprint (cells where z drops by
    void_depth inside void_radius of the centre).

    The void is "underground" — the z value AT the void is depth
    below the surrounding flat ground, mimicking a cave interior.
    """
    rng = np.random.default_rng(rng_seed)
    # grid in metres, centred at origin
    half = (n_xy - 1) * grid_spacing / 2.0
    x = np.linspace(-half, half, n_xy)
    y = np.linspace(-half, half, n_xy)
    XX, YY = np.meshgrid(x, y)
    X = XX.ravel(); Y = YY.ravel()
    # ground: flat with small noise
    z = 0.1 * rng.standard_normal(len(X))
    # void: circular footprint centred at origin
    R = np.sqrt(X**2 + Y**2)
    void_mask = R <= void_radius
    z[void_mask] = -void_depth + 0.05 * rng.standard_normal(void_mask.sum())
    # add some surface noise everywhere
    z += 0.05 * rng.standard_normal(len(X))
    return X.astype(np.float64), Y.astype(np.float64), z.astype(np.float64), void_mask


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--outdir", type=Path, default=Path("/tmp/ll_smoke"))
    p.add_argument("--rungs", type=float, nargs="+", default=[0.5, 2, 5])
    p.add_argument("--grid-spacing", type=float, default=0.25)
    p.add_argument("--n-xy", type=int, default=200)
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    print(f"== smoke test: synthetic cloud {args.n_xy}x{args.n_xy} at {args.grid_spacing} m ==")
    x, y, z, void_mask_pts = make_synthetic_cloud(args.n_xy, args.grid_spacing)
    npz = args.outdir / "synthetic_cloud.npz"
    np.savez_compressed(npz, x=x, y=y, z=z)
    print(f"[npz] {len(x):,} points -> {npz}")
    print(f"[syn] void footprint covers {void_mask_pts.sum()} points "
          f"({void_mask_pts.mean():.1%})")

    # ---- degradation ladder ---------------------------------------------
    print(f"\n== degradation ladder == rungs {args.rungs}")
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code"))
    from wp1_ladder.degrade import degradation_ladder
    ladder_dir = args.outdir / "ladder"
    ladder_summary = degradation_ladder(npz, ladder_dir, args.rungs, args.grid_spacing, "average")

    # ---- VCI ------------------------------------------------------------
    print("\n== VCI ==")
    from wp1_detector.vci import vci_raster, local_maxima
    VCI, n_col, geo = vci_raster(x, y, z, args.grid_spacing, 0.5, 30.0, args.grid_spacing)
    print(f"[vci] raster {VCI.shape}, max VCI = {VCI.max():.3f}, "
          f"n_cells > 0.4 = {(VCI >= 0.4).sum()}")

    # ---- sag detect per rung -------------------------------------------
    print("\n== sag detect ==")
    from wp1_detector.sag_detect import (
        cloud_ground_truth, frangi_vesselness, sink_fill_planchon,
        f1_at_threshold, tune_threshold, write_geotiff,
    )
    from rasterio.transform import Affine
    from whitebox import WhiteboxTools
    import rasterio

    gt, gt_geo = cloud_ground_truth(x, y, z, args.grid_spacing, threshold_depth=1.0)
    n_void = int(gt.sum())
    print(f"[gt ] void cells = {n_void} ({n_void / gt.size:.1%})")
    x_min, y_min, nx, ny, px = gt_geo
    transform = Affine(px, 0.0, x_min, 0.0, px, y_min)

    wbt = WhiteboxTools(); wbt.verbose = False
    rung_rows = []
    sag_dir = args.outdir / "sag"
    sag_dir.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff", "dtype": "float32", "nodata": -9999.0,
        "width": nx, "height": ny, "count": 1,
        "transform": transform, "crs": "EPSG:32631",
        "compress": "deflate", "BIGTIFF": "IF_SAFER",
    }
    for r in args.rungs:
        print(f"  -- rung {r} m --")
        # bin cloud to this rung
        nxr = max(1, int(np.ceil((x.max() - x.min()) / r)))
        nyr = max(1, int(np.ceil((y.max() - y.min()) / r)))
        col = np.clip(((x - x.min()) / r).astype(int), 0, nxr - 1)
        row = np.clip(((y - y.min()) / r).astype(int), 0, nyr - 1)
        flat = row * nxr + col
        sums = np.bincount(flat, weights=z, minlength=nyr * nxr)
        cnts = np.bincount(flat, minlength=nyr * nxr)
        ok = cnts > 0
        Z = np.full(nyr * nxr, np.nan); Z[ok] = sums[ok] / cnts[ok]
        Zr = Z.reshape(nyr, nxr)
        Zr[np.isnan(Zr)] = float(np.nanmean(Zr))
        # write DTM, sink-fill, then compute score
        dtm_tif = sag_dir / f"dtm_{r:g}m.tif"
        with rasterio.open(dtm_tif, "w", **profile | {"width": nxr, "height": nyr,
                                                     "transform": Affine(r, 0, x.min(), 0, r, y.min())}) as dst:
            dst.write(Zr.astype(np.float32), 1)
        fill_tif = sag_dir / f"filled_{r:g}m.tif"
        sink_fill_planchon(wbt, dtm_tif, fill_tif)
        with rasterio.open(fill_tif) as fs, rasterio.open(dtm_tif) as ds:
            fill = fs.read(1).astype(np.float32)
            Zr = ds.read(1).astype(np.float32)
        depth = np.maximum(fill - Zr, 0).astype(np.float32)
        F = frangi_vesselness(Zr, r).astype(np.float32)
        score = (depth * F).astype(np.float32)
        # ground truth resampled
        from scipy.ndimage import zoom
        if (nxr, nyr) != (nx, ny):
            truth_r = zoom(gt.astype(np.float32), (nyr / ny, nxr / nx), order=0).astype(bool)
        else:
            truth_r = gt
        # 50/50 split
        rng = np.random.default_rng(42)
        ev = np.argwhere(np.isfinite(score))
        perm = rng.permutation(len(ev))
        n_cal = len(ev) // 2
        cal = ev[perm[:n_cal]]; test = ev[perm[n_cal:]]
        cal_mask = np.zeros_like(score, dtype=bool); cal_mask[cal[:, 0], cal[:, 1]] = True
        test_mask = np.zeros_like(score, dtype=bool); test_mask[test[:, 0], test[:, 1]] = True
        thr, f1_cal = tune_threshold(score[cal_mask], truth_r[cal_mask])
        m_tst = f1_at_threshold(score[test_mask], truth_r[test_mask], thr)
        cell_area_km2 = (r * r) / 1e6
        n_cells_test = int(test_mask.sum())
        fp_per_1e4km2 = m_tst["fp"] * 1e4 / (n_cells_test * cell_area_km2) if n_cells_test else float("nan")
        print(f"     thr={thr:.3g}, F1_cal={f1_cal:.3f}, F1_test={m_tst['f1']:.3f}, "
              f"P={m_tst['precision']:.3f}, R={m_tst['recall']:.3f}, "
              f"FP/10^4km^2={fp_per_1e4km2:.1f}")
        rung_rows.append({
            "res_m": r, "f1_test": m_tst["f1"], "precision_test": m_tst["precision"],
            "recall_test": m_tst["recall"], "fp_per_1e4km2": fp_per_1e4km2,
            "n_void_cells": int(truth_r.sum()),
        })

    # ---- fusion (Z3.2) --------------------------------------------------
    print("\n== fusion (Z3.2) ==")
    from wp3_fusion.fusion import cloud_ground_truth, f1_at_threshold
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import train_test_split
    # use the 0.5 m rung as features
    r = 0.5
    nxr = max(1, int(np.ceil((x.max() - x.min()) / r)))
    nyr = max(1, int(np.ceil((y.max() - y.min()) / r)))
    col = np.clip(((x - x.min()) / r).astype(int), 0, nxr - 1)
    row = np.clip(((y - y.min()) / r).astype(int), 0, nyr - 1)
    flat = row * nxr + col
    sums = np.bincount(flat, weights=z, minlength=nyr * nxr)
    cnts = np.bincount(flat, minlength=nyr * nxr)
    ok = cnts > 0
    Z = np.full(nyr * nxr, np.nan); Z[ok] = sums[ok] / cnts[ok]
    Zr = Z.reshape(nyr, nxr)
    Zr[np.isnan(Zr)] = float(np.nanmean(Zr))
    depth_f = np.maximum(sink_fill_planchon(wbt, sag_dir / f"dtm_{r:g}m.tif",
                                            sag_dir / f"filled_{r:g}m.tif") if False else Zr, 0)  # placeholder
    # Re-derive the r=0.5 depth properly:
    fill_tif = sag_dir / f"filled_{r:g}m.tif"
    with rasterio.open(fill_tif) as fs, rasterio.open(sag_dir / f"dtm_{r:g}m.tif") as ds:
        depth_f = np.maximum(fs.read(1) - ds.read(1), 0).astype(np.float32)
    F_f = frangi_vesselness(Zr, r).astype(np.float32)
    # features per cell: depth, frangi, plus zero grail/diviner
    feats = np.column_stack([depth_f.ravel(), F_f.ravel(),
                              np.zeros(nxr * nyr), np.zeros(nxr * nyr),
                              np.zeros(nxr * nyr)])
    truth = zoom(gt.astype(np.float32), (nyr / ny, nxr / nx), order=0).astype(bool).ravel()
    finite = np.isfinite(feats).all(axis=1)
    X = feats[finite]; yv = truth[finite].astype(int)
    Xn = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
    Xtr, Xte, ytr, yte = train_test_split(Xn, yv, test_size=0.5, random_state=42, stratify=yv)
    print(f"[data] {X.shape[0]} cells, {yv.sum()} positives ({yv.mean():.1%})")
    for i, name in enumerate(["depth", "frangi", "grail", "diviner", "extra"]):
        m = LogisticRegression(class_weight="balanced", max_iter=200).fit(Xtr[:, [i]], ytr)
        p = m.predict_proba(Xte[:, [i]])[:, 1]
        print(f"  {name:8s}: AUC={roc_auc_score(yte, p):.3f}, "
              f"F1={f1_at_threshold(p, yte, 0.5)['f1']:.3f}")
    m = LogisticRegression(class_weight="balanced", max_iter=200).fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    print(f"  FUSION : AUC={roc_auc_score(yte, p):.3f}, "
          f"F1={f1_at_threshold(p, yte, 0.5)['f1']:.3f}")

    print(f"\n[done] smoke test outputs in {args.outdir}")
    summary = {
        "rungs": rung_rows,
        "synthetic_n_points": int(len(x)),
        "synthetic_void_frac": float(void_mask_pts.mean()),
        "outdir": str(args.outdir),
    }
    with open(args.outdir / "smoke_summary.json", "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
