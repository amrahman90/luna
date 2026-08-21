"""Task 12.1: register Indian Tunnel cave cloud -> surface-cloud frame.

Pipeline (all scipy; Open3D unavailable in venv — documented):
  1. load npz clouds, sentinel/robust z filtering (io_analog)
  2. voxel downsample: 0.15 m for ICP
  3. coarse seed from coarse_search.json (yaw + translation + dz)
  4. trimmed point-to-plane ICP, I1 parameters:
     overlap 90%, adjust-scale OFF (rigid), RMS-change stop 1e-7,
     correspondence cap 2.0 -> 0.25 m
  5. residuals: NN RMSE identity / coarse / final on a dense sample
  6. outputs (repo): registration_report.json, validation PNGs
     outputs (~/lunarvoid): registered cloud npz (0.05 m voxel)

Usage: register_cave.py [--ref NorthSurface|Collapse3]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code" / "wp1_analog"))
from coarse_search import CAVE, REFS, Z_TRIM  # noqa: E402
from icp import icp, rmse_to  # noqa: E402
from io_analog import load_xyz, voxel_downsample  # noqa: E402

OUT = REPO / "data" / "outputs" / "wp1_analog" / "registration"
VOID = Path.home() / "lunarvoid" / "data" / "outputs" / "wp1_analog"
VOID.mkdir(parents=True, exist_ok=True)

VOX_ICP = 0.15
VOX_SAVE = 0.05
ICP_SRC_CAP = 2_500_000
ICP_REF_CAP = 2_500_000
SEED = 42


def coarse_T(deg, dx, dy, dz, mx, my):
    """4x4 pose identical to coarse_search.py's candidate transform.

    coarse_search: x' = (x-mx)c + (y-my)s + dx ; y' = -(x-mx)s + (y-my)c + dy
    i.e. T = Tpost @ Rz @ Tpre with Rz = [[c,s,0],[-s,c,0],[0,0,1]].
    """
    th = np.deg2rad(deg)
    c, s = np.cos(th), np.sin(th)
    Tpre = np.eye(4)
    Tpre[:3, 3] = [-mx, -my, 0.0]
    Rz = np.eye(4)
    Rz[:3, :3] = np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])
    Tpost = np.eye(4)
    Tpost[:3, 3] = [dx, dy, dz]
    return Tpost @ Rz @ Tpre


def pose_stats(P, T, dst_tree, radius):
    cur = P @ T[:3, :3].T + T[:3, 3]
    d, _ = dst_tree.query(cur, k=1, workers=-1)
    m = d < radius
    rms = float(np.sqrt(np.mean(d[m] ** 2))) if m.any() else float("nan")
    med = float(np.median(d[m])) if m.any() else float("nan")
    return rms, med, int(m.sum()), float(m.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="NorthSurface", choices=list(REFS))
    args = ap.parse_args()

    with open(OUT / "coarse_search.json") as f:
        cands = json.load(f)["top10_per_ref"][args.ref]
    best = cands[0]
    print(f"[seed] {args.ref}: yaw {best['deg']} deg d=({best['dx']},{best['dy']},{best['dz']}) "
          f"inlier frac {best['inliers']/best.get('n', 1):.3f}" if 'n' in best else
          f"[seed] {args.ref}: yaw {best['deg']} deg d=({best['dx']},{best['dy']},{best['dz']})",
          flush=True)

    print("[load] cave npz ...", flush=True)
    t0 = time.time()
    cx, cy, cz = load_xyz(CAVE)
    print(f"[load] cave {len(cx):,} pts ({time.time()-t0:.0f}s)", flush=True)
    rx, ry, rz = load_xyz(REFS[args.ref])
    keep = np.abs(rz) < Z_TRIM
    rx, ry, rz = rx[keep], ry[keep], rz[keep]
    print(f"[load] {args.ref} {len(rx):,} pts after z-trim ±{Z_TRIM} m", flush=True)

    # ---------- ICP clouds ----------
    sx, sy, sz = voxel_downsample(cx, cy, cz, VOX_ICP)
    src = np.column_stack([sx, sy, sz])
    r = rng = np.random.default_rng(SEED)
    if len(src) > ICP_SRC_CAP:
        src = src[r.choice(len(src), size=ICP_SRC_CAP, replace=False)]
    txx, tyy, tzz = voxel_downsample(rx, ry, rz, VOX_ICP)
    dst = np.column_stack([txx, tyy, tzz])
    if len(dst) > ICP_REF_CAP:
        dst = dst[r.choice(len(dst), size=ICP_REF_CAP, replace=False)]
    print(f"[icp-prep] src {len(src):,} dst {len(dst):,} @ {VOX_ICP} m voxel", flush=True)

    # NOTE: coarse dx,dy were computed with the cave centroid of the
    # coarse-search cloud; rebuild that centroid deterministically.
    mx_c, my_c = float(np.mean(cx)), float(np.mean(np.asarray(cy)))  # full-cloud centroid
    # coarse_search used a 6M random subsample centroid — negligible
    # difference at 0.5 m grid resolution; ICP cap 2 m absorbs it.

    T_id = np.eye(4)
    T0 = coarse_T(best["deg"], best["dx"], best["dy"], best["dz"], mx_c, my_c)

    from scipy.spatial import cKDTree

    dst_tree = cKDTree(dst)
    rms_i, med_i, n_i, f_i = pose_stats(src, T_id, dst_tree, 2.0)
    rms_c, med_c, n_c, f_c = pose_stats(src, T0, dst_tree, 2.0)
    print(f"[residual] identity: rms {rms_i:.3f} med {med_i:.3f} inliers<2m {n_i:,} ({f_i:.2%})")
    print(f"[residual] coarse  : rms {rms_c:.3f} med {med_c:.3f} inliers<2m {n_c:,} ({f_c:.2%})", flush=True)

    print("[icp] running trimmed point-to-plane ...", flush=True)
    t0 = time.time()
    T, rep = icp(src, dst, T0, max_corr_start=2.0, max_corr_end=0.25,
                 iters=100, rms_eps=1e-7, overlap_frac=0.90,
                 subsample=None, verbose=True)
    print(f"[icp] done in {time.time()-t0:.0f}s, iters {rep['iters_run']}, "
          f"final trimmed rms {rep['rmse_final_m']:.4f} m", flush=True)

    # ---------- final residuals on dense independent samples ----------
    dense_sx, dense_sy, dense_sz = voxel_downsample(cx, cy, cz, 0.10)
    dense_src = np.column_stack([dense_sx, dense_sy, dense_sz])
    rms_f, med_f, n_f, f_f = pose_stats(dense_src, T, dst_tree, 2.0)
    rms_f1, med_f1, n_f1, f_f1 = pose_stats(dense_src, T, dst_tree, 1.0)
    rms_f05, med_f05, n_f05, f_f05 = pose_stats(dense_src, T, dst_tree, 0.5)
    print(f"[residual] final(dense 0.10 m voxel, {len(dense_src):,} pts):")
    print(f"           <2.0 m: rms {rms_f:.4f} med {med_f:.4f} inliers {n_f:,} ({f_f:.2%})")
    print(f"           <1.0 m: rms {rms_f1:.4f} med {med_f1:.4f} inliers {n_f1:,} ({f_f1:.2%})")
    print(f"           <0.5 m: rms {rms_f05:.4f} med {med_f05:.4f} inliers {n_f05:,} ({f_f05:.2%})", flush=True)

    yaw_total = np.degrees(np.arctan2(T[1, 0], T[0, 0]))
    report = {
        "reference": args.ref,
        "reference_npz": str(REFS[args.ref]),
        "source_npz": str(CAVE),
        "method": "scipy trimmed point-to-plane ICP (open3d not in venv); "
                  "coarse yaw+FFT-occupancy seed; I1 params: overlap 90%, "
                  "rigid only (adjust-scale OFF), rms_eps 1e-7, cap 2.0->0.25 m",
        "coarse_seed": best,
        "voxel_icp_m": VOX_ICP,
        "n_src_icp": len(src),
        "n_dst_icp": len(dst),
        "residuals": {
            "identity": {"rms2m": rms_i, "med2m": med_i, "inliers": n_i, "frac": f_i},
            "coarse": {"rms2m": rms_c, "med2m": med_c, "inliers": n_c, "frac": f_c},
            "final": {
                "rms_lt_2m": rms_f, "med_lt_2m": med_f, "inliers_lt_2m": n_f, "frac_lt_2m": f_f,
                "rms_lt_1m": rms_f1, "med_lt_1m": med_f1, "inliers_lt_1m": n_f1, "frac_lt_1m": f_f1,
                "rms_lt_0p5m": rms_f05, "med_lt_0p5m": med_f05, "inliers_lt_0p5m": n_f05,
                "frac_lt_0p5m": f_f05,
            },
        },
        "icp": {k: v for k, v in rep.items() if k != "rmse_trimmed_history"},
        "history_head": rep["rmse_trimmed_history"][:5],
        "history_tail": rep["rmse_trimmed_history"][-5:],
        "net_yaw_deg": float(yaw_total),
        "transform": T.tolist(),
        "transform_convention": "p_ref = T[:3,:3] @ p_cave + T[:3,3] (cave -> surface frame)",
        "seed": SEED,
    }
    with open(OUT / "registration_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("wrote", OUT / "registration_report.json")

    # ---------- save registered cloud (0.05 m voxel) ----------
    print("[save] registered cloud ...", flush=True)
    vx, vy, vz = voxel_downsample(cx, cy, cz, VOX_SAVE)
    P = np.column_stack([vx, vy, vz])
    Q = P @ T[:3, :3].T + T[:3, 3]
    out_npz = VOID / f"indian_tunnel_cave_registered_to_{args.ref}.npz"
    np.savez_compressed(out_npz, x=Q[:, 0].astype(np.float32),
                        y=Q[:, 1].astype(np.float32), z=Q[:, 2].astype(np.float32))
    print(f"wrote {out_npz} ({len(Q):,} pts @ {VOX_SAVE} m voxel)", flush=True)

    # ---------- validation figure ----------
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].scatter(rx[:: max(1, len(rx) // 300_000)], ry[:: max(1, len(rx) // 300_000)],
                    s=0.2, c="k", label=f"{args.ref} cloud", rasterized=True)
    axes[0].scatter(Q[:, 0][:: max(1, len(Q) // 500_000)], Q[:, 1][:: max(1, len(Q) // 500_000)],
                    s=0.1, c="tab:red", alpha=0.5, label="cave (registered)", rasterized=True)
    axes[0].set_aspect("equal"); axes[0].legend(markerscale=20)
    axes[0].set_title("plan view: registered cave over reference")
    axes[1].scatter(rx[:: max(1, len(rx) // 300_000)], rz[:: max(1, len(rx) // 300_000)],
                    s=0.2, c="k", rasterized=True)
    axes[1].scatter(Q[:, 0][:: max(1, len(Q) // 500_000)], Q[:, 2][:: max(1, len(Q) // 500_000)],
                    s=0.1, c="tab:red", alpha=0.5, rasterized=True)
    axes[1].set_aspect("equal"); axes[1].set_title("side view (x-z)")
    axes[2].scatter(ry[:: max(1, len(rx) // 300_000)], rz[:: max(1, len(rx) // 300_000)],
                    s=0.2, c="k", rasterized=True)
    axes[2].scatter(Q[:, 1][:: max(1, len(Q) // 500_000)], Q[:, 2][:: max(1, len(Q) // 500_000)],
                    s=0.1, c="tab:red", alpha=0.5, rasterized=True)
    axes[2].set_aspect("equal"); axes[2].set_title("side view (y-z)")
    for ax in axes:
        ax.set_xlabel("x (m)" if ax is axes[0] or ax is axes[1] else "y (m)")
    axes[0].set_ylabel("y (m)"); axes[1].set_ylabel("z (m)"); axes[2].set_ylabel("z (m)")
    fig.tight_layout()
    fig.savefig(OUT / "registration_validation.png", dpi=110)
    print("wrote", OUT / "registration_validation.png")


if __name__ == "__main__":
    main()
