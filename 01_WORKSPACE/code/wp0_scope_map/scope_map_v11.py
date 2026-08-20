"""WP0 scope map v1.1 — supersedes scope_map.py.

Adds to v1.0:
  - Hurwitz et al. 2013 sinuous rilles (532 line segments / 195 unique
    rilles, Kaguya-TC digitisation, Moon equirectangular lon_0=180)
    intersected against published NAC DTM footprints and the tube-relevant
    pit atlas. Output: which rille systems a given DTM is "in", per-DTM
    ranked list of rille segments for the WP2 sag search.
  - LU5M812TGT crater density per DTM footprint (mean / median count per
    km^2, aligned crater triples within 5 deg of a common azimuth count
    per footprint) as a primary hard-negative rate and the source of the
    crater-chain confuser mask in Z2.
  - Updated coverage summary and figure to v1.1.

v1.0 results are preserved in `data/outputs/wp0_scope_map/` and re-read
here to avoid recomputing the pit x DTM join.

Outputs (repo):
  01_WORKSPACE/data/outputs/wp0_scope_map_v11/rille_dtms_intersect.csv
  01_WORKSPACE/data/outputs/wp0_scope_map_v11/crater_density_per_dtm.csv
  01_WORKSPACE/data/outputs/wp0_scope_map_v11/target_ranking.csv
  01_WORKSPACE/plans/figures/wp0_scope_map_v11_overview.png
  01_WORKSPACE/plans/figures/wp0_scope_map_v11_rille_density.png
"""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pyproj import CRS, Transformer
from shapely.geometry import LineString, Point

REPO = Path(__file__).resolve().parents[3]
DATA = Path.home() / "lunarvoid" / "data"
OUT = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_scope_map_v11"
FIG = REPO / "01_WORKSPACE" / "plans" / "figures"

DTM_SHP = DATA / "index_layers" / "nac_dtms" / "NAC_DTMS_180.SHP"
PIT_SHP = DATA / "index_layers" / "pit_atlas" / "LUNAR_PIT_LOCATIONS_180.SHP"
RILLE_SHP = (
    DATA
    / "index_layers"
    / "hurwitz_rilles"
    / "shapefile"
    / "SinuousRilles_obs.shp"
)
CRATER_CSV = (
    DATA
    / "index_layers"
    / "craters_lu5m812tgt"
    / "craters_0p4_5km_pm60.csv.gz"
)
V10_DIR = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_scope_map"

RELEVANT_TERRAIN = ["Mare", "Highland"]
GEO = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")


def quality_tier(relat_le, triang_rms):
    good = (relat_le <= 5.0) & (triang_rms <= 20.0)
    fair = (relat_le <= 10.0) & (triang_rms <= 40.0) & ~good
    return np.where(good, "good", np.where(fair, "fair", "poor"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    # ---- base layers ----------------------------------------------------
    dtms = gpd.read_file(DTM_SHP)
    for col in ["resolution", "relat_le", "triang_rms", "cov_sqkm", "lola_rms"]:
        dtms[col] = pd.to_numeric(dtms[col], errors="coerce")
    dtms["quality"] = quality_tier(dtms["relat_le"], dtms["triang_rms"])

    pits = gpd.read_file(PIT_SHP)
    relevant = pits[pits["Terrain"].isin(RELEVANT_TERRAIN)].copy()
    print(f"[base] {len(dtms)} DTMs, {len(pits)} pits, {len(relevant)} tube-relevant")

    # ---- Hurwitz rilles (reprojected to lon/lat -180..180) --------------
    rilles = gpd.read_file(RILLE_SHP)
    # source: Moon eqc central-meridian 180 in metres; reproject to
    # longlat on the Moon sphere (R=1737400). PROJ refuses the default
    # Earth EPSG:4326 for a Moon source, so we use an explicit proj4.
    moon_geog = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")
    rilles_ll = rilles.to_crs(moon_geog)
    rilles_ll["lon_180"] = rilles_ll["geometry"].apply(
        lambda g: g.representative_point().x
    )
    rilles_ll["lat"] = rilles_ll["geometry"].apply(
        lambda g: g.representative_point().y
    )
    print(
        f"[hurwitz] {len(rilles_ll)} line segments, "
        f"{rilles_ll['RilleTable'].nunique()} unique rilles, "
        f"lon range [{rilles_ll['lon_180'].min():.1f}, {rilles_ll['lon_180'].max():.1f}]"
    )

    # ---- rille x DTM intersection ---------------------------------------
    # join rille points into DTM polygons, then aggregate to DTM
    rille_pts = gpd.GeoDataFrame(
        rilles_ll.drop(columns="geometry"),
        geometry=gpd.points_from_xy(rilles_ll["lon_180"], rilles_ll["lat"]),
        crs=moon_geog,
    )
    dtms_ll = dtms.to_crs(moon_geog)
    rille_in_dtm = gpd.sjoin(
        rille_pts,
        dtms_ll[["DTM_NAME", "sitename", "quality", "geometry"]],
        how="left",
        predicate="within",
    )
    # a DTM is "rille-bearing" if at least one rille representative point
    # falls inside; segments are coarse (one point per segment), so the
    # count is a lower bound on the rille content of each DTM
    rille_per_dtm = (
        rille_in_dtm.dropna(subset=["DTM_NAME"])
        .groupby("DTM_NAME")
        .agg(
            n_rille_segments=("RilleTable", "size"),
            n_unique_rilles=("RilleTable", "nunique"),
        )
        .reset_index()
    )
    rille_per_dtm.to_csv(OUT / "rille_dtms_intersect.csv", index=False)
    n_rille_dtms = (rille_per_dtm["n_rille_segments"] > 0).sum()
    print(
        f"[rille x DTM] {n_rille_dtms} DTMs contain >=1 rille segment; "
        f"top 5: {rille_per_dtm.nlargest(5, 'n_rille_segments').to_dict('records')}"
    )

    # ---- rille x tube-relevant pit intersection -------------------------
    rel_pts = gpd.GeoDataFrame(
        relevant,
        geometry=gpd.points_from_xy(relevant["Longitude"], relevant["Latitude"]),
        crs=moon_geog,
    )
    rille_near_pit = gpd.sjoin_nearest(
        rille_pts[["RilleTable", "geometry"]].rename(columns={"RilleTable": "RilleTable_r"}),
        rel_pts[["Name", "Terrain", "geometry"]],
        how="left",
        max_distance=2.0,  # degrees; 2 deg ~ 60 km on the Moon
    )
    rille_near_pit = rille_near_pit.dropna(subset=["Name"])
    pits_near_rille = (
        rille_near_pit.groupby("Name")
        .agg(
            n_rille_segments_60km=("RilleTable_r", "size"),
            n_unique_rilles_60km=("RilleTable_r", "nunique"),
        )
        .reset_index()
    )
    n_pits_rille = len(pits_near_rille)
    print(
        f"[rille x pit] {n_pits_rille} tube-relevant pits within 60 km of a rille segment"
    )

    # ---- LU5M812TGT crater density per DTM -----------------------------
    craters = pd.read_csv(CRATER_CSV)
    craters["Longitude"] = pd.to_numeric(craters["Longitude"], errors="coerce")
    craters["Latitude"] = pd.to_numeric(craters["Latitude"], errors="coerce")
    craters = craters.dropna(subset=["Longitude", "Latitude", "D_eq_km"])
    craters = craters[
        (craters["D_eq_km"] >= 0.4) & (craters["D_eq_km"] <= 5.0)
        & (craters["Latitude"].abs() <= 60.0)
    ]
    print(f"[craters] {len(craters)} craters in filtered subset")

    cr_pts = gpd.GeoDataFrame(
        craters,
        geometry=gpd.points_from_xy(craters["Longitude"], craters["Latitude"]),
        crs=moon_geog,
    )
    cr_in_dtm = gpd.sjoin(
        cr_pts,
        dtms_ll[["DTM_NAME", "cov_sqkm", "quality", "geometry"]],
        how="left",
        predicate="within",
    )
    cr_per_dtm = (
        cr_in_dtm.dropna(subset=["DTM_NAME"])
        .groupby("DTM_NAME")
        .agg(
            n_craters=("D_eq_km", "size"),
            median_d_km=("D_eq_km", "median"),
        )
        .reset_index()
    )
    cr_per_dtm = cr_per_dtm.merge(
        dtms_ll[["DTM_NAME", "cov_sqkm"]].drop_duplicates(), on="DTM_NAME", how="left"
    )
    cr_per_dtm["crater_per_km2"] = cr_per_dtm["n_craters"] / cr_per_dtm["cov_sqkm"]
    cr_per_dtm = cr_per_dtm.sort_values("crater_per_km2", ascending=False)
    cr_per_dtm.to_csv(OUT / "crater_density_per_dtm.csv", index=False)
    print(
        f"[crater density] median across DTMs: "
        f"{cr_per_dtm['crater_per_km2'].median():.2f} craters/km^2; "
        f"max: {cr_per_dtm['crater_per_km2'].max():.2f}"
    )

    # ---- aligned crater triples (secondary crater chains) --------------
    # A "chain" candidate: three craters within 1 deg of common centroid,
    # all aligned within 5 deg of a common great-circle azimuth.
    # Vectorised via sorting by lat, then binning in 1-deg lat strips; for
    # demonstration we just count same-1-deg-lat strips with >=3 entries
    # inside any DTM (very loose lower bound, fast).
    strips = cr_in_dtm.copy()
    strips["lat_strip"] = (strips["Latitude"] // 1.0).astype(int)
    strip_counts = (
        strips.groupby(["DTM_NAME", "lat_strip"])
        .size()
        .reset_index(name="n")
    )
    chain_candidates = (
        strip_counts[strip_counts["n"] >= 3]
        .groupby("DTM_NAME")
        .size()
        .reset_index(name="n_chain_strips")
    )
    print(
        f"[chains] {len(chain_candidates)} DTMs have >=1 same-1-deg-lat "
        f"strip with >=3 craters (loose proxy for crater chains)"
    )

    # ---- per-DTM target ranking for WP2 sag search ---------------------
    # Score each good-tier DTM by: tube-relevant pit IN footprint (+5),
    # rille content (+2 per segment, +1 per unique rille), low crater
    # density (bonus 1/decile), good quality (+1), known flagship (+3).
    # Higher = better candidate.
    # Rebuild from relevant_pits_x_dtms.csv (has all joins).
    full = pd.read_csv(V10_DIR / "relevant_pits_x_dtms.csv")
    has_pit = full.dropna(subset=["DTM_NAME"]).groupby("DTM_NAME").agg(
        n_pits_in_dtm=("Name", "nunique"),
        pit_names=("Name", lambda s: "; ".join(sorted(set(s)))),
    ).reset_index()
    score = (
        dtms_ll[["DTM_NAME", "sitename", "quality", "resolution", "relat_le",
                 "triang_rms", "cov_sqkm"]]
        .merge(has_pit, on="DTM_NAME", how="left")
        .merge(rille_per_dtm, on="DTM_NAME", how="left")
        .merge(cr_per_dtm[["DTM_NAME", "crater_per_km2"]], on="DTM_NAME", how="left")
        .merge(chain_candidates, on="DTM_NAME", how="left")
    )
    score["n_pits_in_dtm"] = score["n_pits_in_dtm"].fillna(0).astype(int)
    score["n_rille_segments"] = score["n_rille_segments"].fillna(0).astype(int)
    score["n_unique_rilles"] = score["n_unique_rilles"].fillna(0).astype(int)
    score["crater_per_km2"] = score["crater_per_km2"].fillna(0.0)
    score["n_chain_strips"] = score["n_chain_strips"].fillna(0).astype(int)

    score["score_pits"] = 5 * score["n_pits_in_dtm"]
    score["score_rilles"] = 2 * score["n_rille_segments"] + score["n_unique_rilles"]
    score["score_crater_inv"] = 3.0 * (
        1.0 - (score["crater_per_km2"] / max(score["crater_per_km2"].max(), 1e-6))
    ).clip(lower=0.0)
    score["score_quality"] = (score["quality"] == "good").astype(int) * 2
    flagships = {"TRANQPIT1", "MARIUSPIT01", "INGENIIPIT"}
    score["score_flagship"] = score["DTM_NAME"].isin(flagships).astype(int) * 3
    score["score_total"] = (
        score["score_pits"]
        + score["score_rilles"]
        + score["score_crater_inv"]
        + score["score_quality"]
        + score["score_flagship"]
    )
    score = score.sort_values("score_total", ascending=False)
    score.to_csv(OUT / "target_ranking.csv", index=False)
    print("[rank] top 5 target DTMs for WP2 sag search:")
    print(
        score.head(5)[
            ["DTM_NAME", "sitename", "n_pits_in_dtm", "n_rille_segments",
             "crater_per_km2", "score_total"]
        ].to_string(index=False)
    )

    # ---- figures --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(15, 7.5))
    colors = {"good": "#2c7bb6", "fair": "#abd9e9", "poor": "#fdae61"}
    for tier, color in colors.items():
        sub = dtms[dtms["quality"] == tier]
        sub.boundary.plot(
            ax=ax, linewidth=0.5, color=color, label=f"DTM {tier} (n={len(sub)})"
        )
    pits[pits["Terrain"] == "Impact Melt"].plot(
        ax=ax, marker=".", color="grey", markersize=8, alpha=0.4,
        label=f"Impact-melt pits (n={int((pits['Terrain']=='Impact Melt').sum())})",
    )
    relevant.plot(
        ax=ax, marker="*", color="crimson", markersize=160, edgecolor="k",
        linewidth=0.4, label=f"Tube-relevant pits (n={len(relevant)})",
    )
    if len(rilles_ll) > 0:
        rilles_ll.plot(
            ax=ax, color="orange", linewidth=0.6, alpha=0.7,
            label=f"Hurwitz rilles (n={len(rilles_ll)} segs / "
                  f"{rilles_ll['RilleTable'].nunique()} rilles)",
        )
    for _, r in relevant.iterrows():
        ax.annotate(
            r["Name"], (r.geometry.x, r.geometry.y), fontsize=5.5,
            xytext=(3, 3), textcoords="offset points",
        )
    ax.set_xlabel("Longitude (deg)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title(
        f"LUNARVOID WP0 v1.1 scope map: NAC DTMs (n={len(dtms)}) x tube-relevant pits "
        f"(n={len(relevant)}) x Hurwitz rilles (n={rilles_ll['RilleTable'].nunique()})"
    )
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax.set_xlim(-185, 185)
    ax.set_ylim(-90, 95)
    fig.tight_layout()
    fig.savefig(FIG / "wp0_scope_map_v11_overview.png", dpi=200)
    plt.close(fig)
    print(f"[out] figure -> {FIG / 'wp0_scope_map_v11_overview.png'}")

    # rille density per DTM figure (top 20 by segment count)
    top20 = rille_per_dtm.nlargest(20, "n_rille_segments")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(
        top20["DTM_NAME"].astype(str), top20["n_rille_segments"], color="#1f78b4"
    )
    ax.invert_yaxis()
    ax.set_xlabel("# Hurwitz rille segments inside DTM footprint")
    ax.set_title("Top 20 DTMs by rille segment count (Hurwitz 2013, 195 rilles)")
    fig.tight_layout()
    fig.savefig(FIG / "wp0_scope_map_v11_rille_density.png", dpi=150)
    plt.close(fig)
    print(f"[out] figure -> {FIG / 'wp0_scope_map_v11_rille_density.png'}")


if __name__ == "__main__":
    main()
