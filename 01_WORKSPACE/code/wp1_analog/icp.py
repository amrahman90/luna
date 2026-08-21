"""Task 12.1 ICP refinement (scipy implementation; Open3D NOT in venv).

Roadmap I1 parameters honoured:
  - convergence: |dRMSE| < 1e-7 (CloudCompare-style RMS threshold)
  - overlap: keep closest 90% of correspondences (trimmed ICP)
  - adjust-scale OFF: rigid-body only (R in SO(3) + t), no similarity.
  - max correspondence distance shrinks coarse -> 0.25 m (classic ICP
    schedule) so only genuinely shared geometry (entrance/skylight rims
    + collapse floors seen by both scanners) drives the fit.

Point-to-plane variant (reference normals via local PCA, k=20) for the
final pass; point-to-point Kabsch available for robustness comparison.

API:
    T, report = icp(src, dst, T0, iters=100, ...)   # nx3 float arrays
"""
from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree


def _apply(T, P):
    return P @ T[:3, :3].T + T[:3, 3]


def kabsch(src, dst):
    """Rigid (no scale) least-squares R,t mapping src -> dst."""
    cs, cd = src.mean(0), dst.mean(0)
    H = (src - cs).T @ (dst - cd)
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1.0, 1.0, d]) @ U.T
    return R, cd - R @ cs


def estimate_normals(P, k=20):
    tree = cKDTree(P)
    _, idx = tree.query(P, k=k, workers=-1)
    nb = P[idx]  # (n, k, 3)
    nb = nb - nb.mean(axis=1, keepdims=True)
    cov = np.einsum("nki,nkj->nij", nb, nb) / (k - 1)
    w, v = np.linalg.eigh(cov)
    return v[:, :, 0]  # smallest eigenvector


def icp(src, dst, T0, max_corr_start=2.0, max_corr_end=0.25, iters=100,
        rms_eps=1e-7, overlap_frac=0.90, normals_k=20, seed=42,
        subsample=None, verbose=True):
    """Trimmed point-to-plane ICP of src -> dst with initial pose T0.

    Returns (T, report dict). RMSE = root-mean-square of *trimmed*
    correspondence distances (matches CloudCompare's reported RMS).
    """
    rng = np.random.default_rng(seed)
    if subsample is not None and len(src) > subsample:
        src = src[rng.choice(len(src), size=subsample, replace=False)]
    if subsample is not None and len(dst) > subsample:
        dst = dst[rng.choice(len(dst), size=subsample, replace=False)]
    tree = cKDTree(dst)
    normals = estimate_normals(dst, k=normals_k)
    T = T0.copy()
    rms_prev = np.inf
    history = []
    n_inlier_final = 0
    for it in range(iters):
        cap = max_corr_start + (max_corr_end - max_corr_start) * it / max(1, iters - 1)
        cur = _apply(T, src)
        d, j = tree.query(cur, k=1, workers=-1)
        m = d < cap
        if m.sum() < 100:
            if verbose:
                print(f"[icp] iter {it}: only {m.sum()} corr < {cap:.2f} m — stop")
            break
        dm = d[m]
        # trim to best overlap_frac
        kth = max(1, int(np.floor(overlap_frac * len(dm))))
        thr = np.partition(dm, kth - 1)[kth - 1] if kth < len(dm) else dm.max()
        sel = m & (d <= thr)
        P = cur[sel]
        Q = dst[j[sel]]
        N = normals[j[sel]]
        rms = float(np.sqrt(np.mean(d[sel] ** 2)))
        # point-to-plane linearised LS (small-angle 6-vector)
        c = np.einsum("ij,ij->i", Q - P, N)
        A = np.hstack([np.cross(P, N), N])
        sol, *_ = np.linalg.lstsq(A, c, rcond=None)
        wx, wy, wz, tx, ty, tz = sol
        th = np.sqrt(wx * wx + wy * wy + wz * wz)
        if th > 1e-12:
            K = np.array([[0, -wz, wy], [wz, 0, -wx], [-wy, wx, 0]])
            dR = np.eye(3) + K + K @ K * ((1 - np.cos(th)) / (th * th))
        else:
            dR = np.eye(3)
        dT = np.eye(4)
        dT[:3, :3] = dR
        dT[:3, 3] = [tx, ty, tz]
        T = dT @ T
        history.append({"iter": it, "cap_m": cap, "n_corr": int(sel.sum()),
                        "rmse_m": rms, "delta": abs(rms_prev - rms)})
        if verbose and (it % 5 == 0 or it == iters - 1):
            print(f"[icp] iter {it:3d} cap {cap:5.2f} corr {sel.sum():7,} rms {rms:.4f} m "
                  f"d {abs(rms_prev-rms):.2e}")
        if abs(rms_prev - rms) < rms_eps:
            break
        rms_prev = rms
        n_inlier_final = int(sel.sum())
    # final RMSE on the fixed schedule cap
    cur = _apply(T, src)
    d, j = tree.query(cur, k=1, workers=-1)
    m = d < max_corr_end * 2
    rms_final = float(np.sqrt(np.mean(d[m] ** 2))) if m.sum() else float("nan")
    report = {
        "iters_run": len(history),
        "converged_delta_rms": history[-1]["delta"] if history else None,
        "rms_eps": rms_eps,
        "overlap_frac": overlap_frac,
        "final_corr_within_2xcap": int(m.sum()),
        "rmse_final_m": rms_final,
        "rmse_trimmed_history": history,
        "transform": T.tolist(),
        "n_src": len(src),
        "n_dst": len(dst),
    }
    return T, report


def rmse_to(src, dst, T, radius=None):
    """Plain NN RMSE of src (posed by T) against dst; inliers if radius."""
    cur = _apply(T, src)
    d, _ = cKDTree(dst).query(cur, k=1, workers=-1)
    if radius:
        m = d < radius
        return float(np.sqrt(np.mean(d[m] ** 2))) if m.any() else float("nan"), int(m.sum())
    return float(np.sqrt(np.mean(d ** 2))), len(d)
