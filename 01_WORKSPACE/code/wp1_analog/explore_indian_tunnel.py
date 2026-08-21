"""Task 12 pre-flight: look at the three Indian Tunnel clouds before ICP.

Produces top-down (x-y, z-coloured) and side (x-z) density renders for
  - Indian_NorthSurface_1x (exterior DTM source, ladder reference)
  - Indian_Collapse3      (a skylight/collapse scan, surface frame?)
  - IndianTunnel_full_1x  (cave interior, 10x used for speed here)
plus a frame-consistency check: is Collapse3 already in the NorthSurface
frame? (compare a 0.5 m DTM built from each in the bbox overlap)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code" / "wp1_analog"))
from io_analog import load_xyz, master_grid, voxel_downsample

LLTB1 = Path.home() / "lunarvoid/data/lltb1"
OUT = REPO / "data" / "outputs" / "wp1_analog" / "registration"
OUT.mkdir(parents=True, exist_ok=True)

SITES = {
    "NorthSurface": LLTB1 / "IndianTunnel_surface/Indian_NorthSurface_1x_0p5m.npz",
    "Collapse3": LLTB1 / "IndianTunnel_surface/Indian_Collapse3_0p5m.npz",
    "Cave1x": LLTB1 / "IndianTunnel_cave_1x/IndianTunnel_cave_1x_0p5m.npz",
}

clouds = {}
for name, path in SITES.items():
    cap = 4_000_000 if name == "Cave1x" else None
    x, y, z = load_xyz(path, max_points=cap)  # cap only for plotting speed
    x, y, z = voxel_downsample(x, y, z, 0.10)
    clouds[name] = (x, y, z)
    print(
        f"{name:13s} n={len(x):>10,}  x[{x.min():8.2f},{x.max():8.2f}] "
        f"y[{y.min():8.2f},{y.max():8.2f}] z[{z.min():8.2f},{z.max():8.2f}] "
        f"z_p50={np.median(z):7.2f}",
        flush=True,
    )

fig, axes = plt.subplots(3, 2, figsize=(14, 18))
for i, (name, (x, y, z)) in enumerate(clouds.items()):
    for j, (a, b, la, lb) in enumerate(((x, y, "x (m)", "y (m)"), (x, z, "x (m)", "z (m)"))):
        ax = axes[i, j]
        s = ax.scatter(a, b, c=z, s=0.05, cmap="viridis", rasterized=True)
        ax.set_xlabel(la)
        ax.set_ylabel(lb)
        ax.set_title(f"{name}  ({la} vs {lb})")
        ax.set_aspect("equal")
        plt.colorbar(s, ax=ax, label="z (m)")
fig.suptitle("Indian Tunnel clouds — pre-registration look (0.10 m voxel ds)", y=0.995)
fig.tight_layout()
fig.savefig(OUT / "preflight_clouds.png", dpi=110)
print("wrote", OUT / "preflight_clouds.png")

# --- frame consistency: Collapse3 vs NorthSurface overlap comparison ---
def quick_dtm(x, y, z, spacing=0.5):
    nx, ny, x0, y0 = master_grid(x, y, spacing)
    col = np.clip(((x - x0) / spacing).astype(int), 0, nx - 1)
    row = np.clip(((y - y0) / spacing).astype(int), 0, ny - 1)
    Z = np.full((ny, nx), np.nan)
    cnt = np.zeros((ny, nx), dtype=np.int32)
    np.add.at(Z, (row, col), z.astype(np.float64))
    np.add.at(cnt, (row, col), 1)
    m = cnt > 0
    Z[m] /= cnt[m]
    return Z, x0, y0, spacing


xn, yn, zn = clouds["NorthSurface"]
xc, yc, zc = clouds["Collapse3"]
Zn, x0n, y0n, s = quick_dtm(xn, yn, zn)
nxn, nyn = Zn.shape
col = np.clip(((xc - x0n) / s).astype(int), 0, nxn - 1)
row = np.clip(((yc - y0n) / s).astype(int), 0, nyn - 1)
zn_surf = Zn[row, col]
ok = np.isfinite(zn_surf) & (np.abs(zc - zn_surf) < 50)
if ok.sum() > 100:
    dz = (zc - zn_surf)[ok].astype(np.float64)
    print(
        f"[frame-check] Collapse3 pts falling on NorthSurface grid: {ok.sum():,}; "
        f"dz median {np.median(dz):+.3f} m, MAD {np.median(np.abs(dz - np.median(dz))):.3f} m, "
        f"frac |dz|<0.5 m: {np.mean(np.abs(dz) < 0.5):.3f}"
    )
else:
    print(f"[frame-check] negligible bbox overlap between Collapse3 and NorthSurface ({ok.sum()} pts)")
