"""Task 12.2: ENTRANCE-TRENCH + SKYLIGHT MASK for Indian Tunnel on the
ladder DTM grid (NOT roofed-void ground truth; in-window roofed-void
cells = 5 / 1.25 m2 — see NOTES_task12_registration_mask.md guardrails).

Takes the registered cave cloud (register_cave.py output) and rasterises
its ground-projected occupancy onto the EXACT grid of the LLTB-1 ladder
reference DTM (IndianTunnel_NorthSurface master_0.5m.tif: 131x250 cells
@ 0.5 m, local scanner metric frame, CRS None by construction —
degrade.py grid). This is the "vertical projection of the surveyed void
onto the surface DTM" (roadmap Task 12 verification).

Outputs (repo): entrance_trench_skylight_mask.tif,
entrance_trench_skylight_mask_preview.png,
entrance_trench_skylight_mask_footprint.geojson,
entrance_trench_skylight_mask_stats.json
(in data/outputs/wp1_analog/void_mask/; renamed from void_mask_gt.* on
2026-08-22 after skeptic review).

Method notes:
- occupancy = cells containing >=1 registered cave point (0.05 m voxel
  cloud), then binary closing 3x3 (heals <=1-cell scan shadows) and
  removal of connected components < 5 cells (speckle). Raw and cleaned
  counts both reported.
- open-vs-roofed split per cell: cave points reaching within 0.5 m of
  the DTM surface => open (entrance/skylight) cell, else roofed void.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.features import shapes
from scipy import ndimage

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "code" / "wp1_analog"))

MASTER = Path.home() / "lunarvoid/data/lltb1/IndianTunnel_NorthSurface/lltb1/ladder/master_0.5m.tif"
REG = Path.home() / "lunarvoid/data/outputs/wp1_analog/indian_tunnel_cave_registered_to_NorthSurface.npz"
OUTDIR = REPO / "data" / "outputs" / "wp1_analog" / "void_mask"
OUTDIR.mkdir(parents=True, exist_ok=True)
CELL_AREA = 0.25  # 0.5 m * 0.5 m
SEED = 42


def main():
    with rasterio.open(MASTER) as src:
        profile = src.profile.copy()
        Z = src.read(1)
        tr = src.transform
        W, H = src.width, src.height
    valid_dtm = np.isfinite(Z)
    print(f"[grid] master {W}x{H} @ 0.5 m; valid DTM cells {valid_dtm.sum():,} "
          f"({valid_dtm.mean():.1%})", flush=True)

    d = np.load(REG)
    x, y, z = np.asarray(d["x"], float), np.asarray(d["y"], float), np.asarray(d["z"], float)
    print(f"[cloud] registered cave {len(x):,} pts", flush=True)

    # array-space indexing, IDENTICAL to degrade.py cloud_to_master_grid:
    # row = (y - y_min)/s with row 0 at y_min (south). The master GeoTIFF's
    # from_bounds transform is north-up, so rasters in this project are
    # stored south-to-north; we keep that convention for cell-for-cell
    # comparability with all ladder/sag artifacts.
    x_min = tr.c
    y_min = tr.f - H * 0.5
    cols_f = (x - x_min) / 0.5
    rows_f = (y - y_min) / 0.5
    inb = (cols_f >= 0) & (cols_f < W) & (rows_f >= 0) & (rows_f < H)
    rI = np.clip(rows_f[inb], 0, H - 1).astype(int)
    cI = np.clip(cols_f[inb], 0, W - 1).astype(int)
    zI = z[inb]
    print(f"[cloud] inside DTM extent: {inb.sum():,} pts ({inb.mean():.1%})", flush=True)
    print(f"[grid] row convention: row 0 = y_min ({y_min:.2f}); inherited from "
          "degrade.py fill (see registration/notes)", flush=True)

    # occupancy
    occ = np.zeros((H, W), dtype=bool)
    occ[rI, cI] = True
    raw_cells = int(occ.sum())

    # cleanup: closing then drop speckle components
    closed = ndimage.binary_closing(occ, structure=np.ones((3, 3)))
    lab, nlab = ndimage.label(closed)
    if nlab:
        sizes = ndimage.sum(closed, lab, range(1, nlab + 1))
        keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 5])
    else:
        keep = closed
    mask = keep

    # per-cell cave z stats for open/roofed classification
    # (np.maximum.at into a NaN-init array stays NaN — accumulate in
    # +/-inf and NaN-mask untouched cells; same bug class as degrade.py)
    order = np.lexsort((cI, rI))
    rr, cc, zz = rI[order], cI[order], zI[order]
    zmax_cells = np.full((H, W), -np.inf)
    zmin_cells = np.full((H, W), np.inf)
    zcnt_cells = np.zeros((H, W), dtype=np.int32)
    np.maximum.at(zmax_cells, (rr, cc), zz)
    np.minimum.at(zmin_cells, (rr, cc), zz)
    np.add.at(zcnt_cells, (rr, cc), 1)
    touched = zcnt_cells > 0
    zmax_cells = np.where(touched, zmax_cells, np.nan)
    zmin_cells = np.where(touched, zmin_cells, np.nan)

    # interior (sub-surface-band) ceiling: the registered cloud contains a
    # mapped surface layer along the corridor, so zmax alone cannot tell
    # roofed from open. Interior points = strictly below Z-0.5.
    with np.errstate(invalid="ignore"):
        band = zz > Z[rr, cc] - 0.5  # points in/above the surface band
    zmax_int = np.full((H, W), -np.inf)
    np.maximum.at(zmax_int, (rr[~band], cc[~band]), zz[~band])
    has_int = np.zeros((H, W), dtype=bool)
    has_int[rr[~band], cc[~band]] = True
    zmax_int = np.where(has_int, zmax_int, np.nan)

    # open cell: no interior points (collapse floor / entrance ramp) or
    # interior ceiling within 1 m of the DTM (roof thinner than 1 m)
    with np.errstate(invalid="ignore"):
        roof_depth = Z - zmax_int  # NaN where no interior points
        open_cells = mask & valid_dtm & (~has_int | (roof_depth < 1.0))
    roofed_cells = mask & valid_dtm & ~open_cells
    # depth of void floor below DTM (all mask cells with DTM)
    with np.errstate(invalid="ignore"):
        floor_depth = Z - zmin_cells

    # corridor metrics via PCA of mask cell centres
    ys, xs = np.nonzero(mask)
    pts = np.column_stack([xs + 0.5, ys + 0.5])  # cell centres in px
    c = pts.mean(0)
    u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
    axis = vt[0]  # major axis (px)
    s_proj = (pts - c) @ axis * 0.5  # metres along corridor
    length_m = float(s_proj.max() - s_proj.min() + 0.5)
    # width per 1 m corridor slice
    bins = np.arange(np.floor(s_proj.min()), np.ceil(s_proj.max()) + 1, 1.0)
    wsum = np.histogram(s_proj, bins=bins)[0] * CELL_AREA / 1.0
    wpos = wsum > 0

    stats = {
        "grid": {
            "source": str(MASTER),
            "width": W, "height": H, "res_m": 0.5,
            "transform": [tr.a, tr.b, tr.c, tr.d, tr.e, tr.f],
            "crs": None,
            "crs_note": "local scanner metric frame (ENU, metres); dataset has no "
                        "georeferencing — see registration_report.json",
            "valid_dtm_cells": int(valid_dtm.sum()),
        },
        "mask": {
            "raw_occupancy_cells": raw_cells,
            "cleaned_cells": int(mask.sum()),
            "closing": "binary 3x3", "min_component_cells": 5,
            "area_m2": float(mask.sum() * CELL_AREA),
            "raw_area_m2": float(raw_cells * CELL_AREA),
            "pct_of_dtm_extent": float(mask.sum() / (W * H)),
            "pct_of_valid_dtm": float((mask & valid_dtm).sum() / valid_dtm.sum()),
            "cells_also_valid_dtm": int((mask & valid_dtm).sum()),
            "open_cells_entrance_skylight": int(open_cells.sum()),
            "roofed_void_cells": int(roofed_cells.sum()),
            "open_area_m2": float(open_cells.sum() * CELL_AREA),
            "roofed_area_m2": float(roofed_cells.sum() * CELL_AREA),
            "roof_depth_m_p50": float(np.nanmedian(roof_depth[roofed_cells])) if roofed_cells.any() else None,
            "roof_depth_m_p90": float(np.nanquantile(roof_depth[roofed_cells], 0.9)) if roofed_cells.any() else None,
            "floor_depth_m_p50": float(np.nanmedian(floor_depth[mask & valid_dtm])),
            "floor_depth_m_p90": float(np.nanquantile(floor_depth[mask & valid_dtm], 0.9)),
            "floor_depth_m_max": float(np.nanmax(floor_depth[mask & valid_dtm])),
            "corridor_length_m": length_m,
            "corridor_axis_deg_in_grid": float(np.degrees(np.arctan2(axis[1], axis[0]))),
            "corridor_width_m_mean": float(wsum[wpos].mean()),
            "corridor_width_m_median": float(np.median(wsum[wpos])),
            "corridor_width_m_p90": float(np.quantile(wsum[wpos], 0.9)),
            "corridor_width_m_max": float(wsum[wpos].max()),
            "n_open_clusters": int(ndimage.label(open_cells)[1]),
        },
        "cloud": {"registered_npz": str(REG), "n_points": int(len(x)),
                  "n_inside_extent": int(inb.sum())},
        "seed": SEED,
    }

    # ---- corridor-overlap sanity check vs ladder sag-depth raster ----
    sag_p = (Path.home() / "lunarvoid/data/lltb1/IndianTunnel_NorthSurface/lltb1/sag/"
             "depth_1m.tif")
    if sag_p.exists():
        import rasterio as rio
        with rio.open(sag_p) as s2:
            D = s2.read(1)
            D = np.where(D < -1000, np.nan, D)  # -9999 nodata
            f2 = 1.0 / 2.0  # 1 m rung cells are 2x the 0.5 m mask cells
            rrS = (rows_f[inb] * f2).astype(int)
            ccS = (cols_f[inb] * f2).astype(int)
        inS = (rrS < D.shape[0]) & (ccS < D.shape[1])
        dvals_mask_cells = D[rrS[inS], ccS[inS]]
        dvals_mask_cells = dvals_mask_cells[np.isfinite(dvals_mask_cells)]
        dvals_all = D[np.isfinite(D)]
        stats["corridor_overlap_check"] = {
            "sag_raster": str(sag_p),
            "n_valid_sag_cells": int(dvals_all.size),
            "median_sag_depth_in_mask_cells_m": float(np.nanmedian(dvals_mask_cells)) if dvals_mask_cells.size else None,
            "median_sag_depth_in_raster_m": float(np.nanmedian(dvals_all)),
            "frac_zero_sag_in_mask_cells": float((dvals_mask_cells == 0).mean()) if dvals_mask_cells.size else None,
            "frac_zero_sag_in_raster": float((dvals_all == 0).mean()),
            "note": "P-D depression depth is 0 on terrain that drains; the "
                    "in-window corridor is an OPEN entrance trench (see "
                    "open_cells stats) which drains out the entrance, so a "
                    "zero median here is expected and NOT evidence against "
                    "the registration. Deep closed sags would only appear "
                    "over the roofed tube, which lies outside this DTM "
                    "window.",
        }

    # ---- write mask GeoTIFF (byte 0/1, exact master profile) ----
    prof = profile.copy()
    prof.update(dtype="uint8", count=1, nodata=255, compress="deflate")
    # NOTE: master rows run y ascending via from_bounds; profile transform is
    # already north-up negative — identical grid, just write the array as-is.
    mask_tif = OUTDIR / "entrance_trench_skylight_mask.tif"
    with rasterio.open(mask_tif, "w", **prof) as dst:
        dst.write(mask.astype(np.uint8), 1)

    # ---- footprint polygon GeoJSON ----
    geoms = list(shapes(mask.astype(np.uint8), mask=mask, transform=tr))
    feats = [{
        "type": "Feature",
        "properties": {"kind": "void_footprint", "cells": int(mask.sum()),
                        "area_m2": stats["mask"]["area_m2"],
                        "crs_note": stats["grid"]["crs_note"],
                        "registered_from": "indian_tunnel_cave_registered_to_NorthSurface.npz"},
        "geometry": g,
    } for g, v in geoms if v == 1]
    gj = {"type": "FeatureCollection", "features": feats}
    with open(OUTDIR / "entrance_trench_skylight_mask_footprint.geojson", "w") as f:
        json.dump(gj, f)

    with open(OUTDIR / "entrance_trench_skylight_mask_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    # ---- preview PNG ----
    fig, axes = plt.subplots(1, 2, figsize=(16, 9))
    hs_data = np.where(valid_dtm, Z, np.nan)
    ls = matplotlib.colors.LightSource(azdeg=315, altdeg=45)
    hs = ls.hillshade(np.nan_to_num(hs_data, nan=np.nanmean(hs_data)), dy=0.5, dx=0.5)
    ext = [tr.c, tr.c + W * 0.5, y_min, tr.f]  # row 0 = y_min -> origin lower
    ax = axes[0]
    ax.imshow(hs, cmap="gray", extent=ext, origin="lower")
    ax.contour(np.where(mask, 1.0, 0.0), levels=[0.5], colors="red",
               extent=ext, origin="lower", linewidths=1.2)
    if open_cells.any():
        ax.contour(np.where(open_cells, 1.0, 0.0), levels=[0.5], colors="yellow",
                   extent=ext, origin="lower", linewidths=0.8, linestyles=":")
    ax.set_title("Indian Tunnel cave-cloud footprint on NorthSurface DTM (0.5 m)\n"
                 "red = entrance-trench + skylight mask, yellow dotted = open (entrance/skylight) cells")
    ax.set_xlabel("x (m, site frame)"); ax.set_ylabel("y (m, site frame)")
    ax2 = axes[1]
    ax2.imshow(mask.astype(np.uint8), cmap="gray_r", origin="lower", extent=ext)
    ax2.set_title(f"mask cells {mask.sum():,} = {stats['mask']['area_m2']:.0f} m² "
                  f"({stats['mask']['pct_of_valid_dtm']:.1%} of valid DTM)")
    ax2.set_xlabel("x (m)"); ax2.set_ylabel("y (m)")
    fig.tight_layout()
    png = OUTDIR / "entrance_trench_skylight_mask_preview.png"
    fig.savefig(png, dpi=120)

    from PIL import Image
    with Image.open(png) as im:
        print(f"[png] {png.name} {im.size}", flush=True)

    print(json.dumps(stats["mask"], indent=2))
    print("wrote:", mask_tif, OUTDIR / "entrance_trench_skylight_mask_footprint.geojson",
          OUTDIR / "entrance_trench_skylight_mask_stats.json", png, sep="\n  ")


if __name__ == "__main__":
    main()
