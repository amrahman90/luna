"""Task 12.1 coarse registration search: cave cloud -> surface frame.

The three Indian Tunnel scans each live in their own scanner-local frame
(no common site frame; preflight showed 0 XY overlap between Collapse3
and NorthSurface points, i.e. arbitrary yaw). We search a yaw-only
rotation (both scanners were z-levelled) + XY translation, seeded by
FFT cross-correlation of 0.5 m XY occupancy bitmaps, and scored by the
number of cave points with a 3D nearest neighbour < 1.0 m in the
reference cloud (shared entrance/skylight geometry). Best seed feeds the
ICP refinement (register_cave.py).

Importable: CAVE, REFS, Z_TRIM, VOXEL, SEED, fft_shift_candidates,
occupancy. Running as a script executes the search and writes
coarse_search.json (+ PNG).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
from scipy.spatial import cKDTree

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code" / "wp1_analog"))
from io_analog import load_xyz, voxel_downsample

LLTB1 = Path.home() / "lunarvoid/data/lltb1"
OUT = REPO / "data" / "outputs" / "wp1_analog" / "registration"

CAVE = LLTB1 / "IndianTunnel_cave_1x/IndianTunnel_cave_1x_0p5m.npz"
REFS = {
    "NorthSurface": LLTB1 / "IndianTunnel_surface/Indian_NorthSurface_1x_0p5m.npz",
    "Collapse3": LLTB1 / "IndianTunnel_surface/Indian_Collapse3_0p5m.npz",
}
Z_TRIM = 30.0  # NorthSurface has 39 junk points beyond +-30 m; real terrain ~[-15,5]
VOXEL = 0.20
SEARCH_SUBSAMPLE = 250_000
NN_R = 1.0
SEED = 42


def occupancy(x, y, res, x0, y0, nx, ny):
    g = np.zeros((ny, nx), dtype=np.float32)
    col = np.clip(((x - x0) / res).astype(int), 0, nx - 1)
    row = np.clip(((y - y0) / res).astype(int), 0, ny - 1)
    g[row, col] = 1.0
    return g


def fft_shift_candidates(A, B, res, k=3):
    """Top-k (dx, dy) shifts (metres) maximizing overlap(A shifted, B)."""
    ny, nx = A.shape
    FA = np.fft.rfft2(A, s=(2 * ny, 2 * nx))
    FB = np.fft.rfft2(B, s=(2 * ny, 2 * nx))
    corr = np.fft.irfft2(FA * np.conj(FB), s=(2 * ny, 2 * nx))
    flat = corr.ravel()
    top = np.argpartition(flat, -k)[-k:]
    out = []
    for t in top:
        iy, ix = np.unravel_index(t, corr.shape)
        dy = iy * res if iy < ny else (iy - 2 * ny) * res
        dx = ix * res if ix < nx else (ix - 2 * nx) * res
        out.append((float(dx), float(dy), float(flat[t])))
    return sorted(out, key=lambda v: -v[2])


def inlier_score(pts, tree, radius=NN_R):
    d, _ = tree.query(pts, k=1, workers=-1)
    return int((d < radius).sum()), d


def search_ref(cs, P, rx, ry, rz):
    """Yaw sweep against one reference cloud. Returns candidate list."""
    tree = cKDTree(P)
    res = 0.5
    x0r, y0r = rx.min(), ry.min()
    nx = int(np.ceil((rx.max() - x0r) / res)) + 2
    ny = int(np.ceil((ry.max() - y0r) / res)) + 2
    mx = cs[:, 0].mean()
    my = cs[:, 1].mean()
    cands = []
    for deg in range(0, 360, 2):
        th = np.deg2rad(deg)
        ct, st = np.cos(th), np.sin(th)
        dxr = (cs[:, 0] - mx) * ct + (cs[:, 1] - my) * st
        dyr = -(cs[:, 0] - mx) * st + (cs[:, 1] - my) * ct
        ux0 = min(dxr.min(), x0r)
        uy0 = min(dyr.min(), y0r)
        unx = int(np.ceil((max(dxr.max(), rx.max()) - ux0) / res)) + 2
        uny = int(np.ceil((max(dyr.max(), ry.max()) - uy0) / res)) + 2
        A = occupancy(dxr, dyr, res, ux0, uy0, unx, uny)
        Bp = occupancy(rx, ry, res, ux0, uy0, unx, uny)
        for dx, dy, _ in fft_shift_candidates(A, Bp, res, k=2):
            sx = dxr + dx
            sy = dyr + dy
            sz = cs[:, 2]
            n0, _ = inlier_score(np.column_stack([sx, sy, sz]), tree)
            if n0 > 200:
                d, j = tree.query(np.column_stack([sx, sy, sz]), k=1, workers=-1)
                m = d < NN_R
                if m.sum() > 100:
                    dz = float(np.median(P[j[m], 2] - sz[m]))
                    n1, _ = inlier_score(np.column_stack([sx, sy, sz + dz]), tree)
                    cands.append({"deg": deg, "dx": dx, "dy": dy, "dz": dz,
                                  "inliers_xy": n0, "inliers": n1})
                else:
                    cands.append({"deg": deg, "dx": dx, "dy": dy, "dz": 0.0,
                                  "inliers_xy": n0, "inliers": n0})
            else:
                cands.append({"deg": deg, "dx": dx, "dy": dy, "dz": 0.0,
                              "inliers_xy": n0, "inliers": n0})
    cands.sort(key=lambda c: -c["inliers"])
    return cands


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    print("[load] cave ...", flush=True)
    cx, cy, cz = load_xyz(CAVE, max_points=6_000_000, seed=SEED)
    cx, cy, cz = voxel_downsample(cx, cy, cz, VOXEL)
    cidx = rng.choice(len(cx), size=min(SEARCH_SUBSAMPLE, len(cx)), replace=False)
    cs = np.column_stack([cx[cidx], cy[cidx], cz[cidx]])
    print(f"[load] cave {len(cx):,} pts (voxel {VOXEL} m), search subset {len(cs):,}", flush=True)

    results = {}
    for name, path in REFS.items():
        x, y, z = load_xyz(path)
        keep = np.abs(z) < Z_TRIM
        x, y, z = x[keep], y[keep], z[keep]
        x, y, z = voxel_downsample(x, y, z, VOXEL)
        P = np.column_stack([x, y, z])
        print(f"[load] {name}: {len(x):,} pts", flush=True)
        t0 = time.time()
        cands = search_ref(cs, P, x, y, z)
        results[name] = cands[:10]
        best = cands[0]
        print(
            f"[{name}] best: yaw {best['deg']} deg, d=({best['dx']:.1f},{best['dy']:.1f},{best['dz']:.2f}) "
            f"inliers {best['inliers']:,}/{len(cs):,} = {best['inliers']/len(cs):.3%} "
            f"({time.time()-t0:.0f}s)",
            flush=True,
        )

    with open(OUT / "coarse_search.json", "w") as f:
        json.dump({"seed": SEED, "voxel_m": VOXEL, "search_subsample": len(cs),
                   "nn_radius_m": NN_R, "top10_per_ref": results}, f, indent=2)
    print("wrote", OUT / "coarse_search.json")


if __name__ == "__main__":
    main()
