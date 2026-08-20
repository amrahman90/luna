"""WP0 scope map: intersect Lunar Pit Atlas (mare/highland subset) with published NAC DTM footprints.

Outputs CSV tables + a global overview figure. Answers: which tube-relevant
pits already sit inside a quality-acceptable published DTM, which have buildable
stereo, and where the coverage gaps are. See LUNARVOID Master Plan v5 WP0.
"""

from pathlib import Path

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

DATA_DIR = Path.home() / "lunarvoid" / "data" / "index_layers"
OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "outputs" / "wp0_scope_map"
FIG_DIR = Path(__file__).resolve().parents[2] / "plans" / "figures"
DTM_SHP = DATA_DIR / "nac_dtms" / "NAC_DTMS_180.SHP"
PIT_SHP = DATA_DIR / "pit_atlas" / "LUNAR_PIT_LOCATIONS_180.SHP"

RELEVANT_TERRAIN = ["Mare", "Highland"]


def load_layers():
    dtms = gpd.read_file(DTM_SHP)
    pits = gpd.read_file(PIT_SHP)
    for col in ["resolution", "relat_le", "triang_rms", "cov_sqkm", "lola_rms"]:
        dtms[col] = pd.to_numeric(dtms[col], errors="coerce")
    return dtms, pits


def quality_tier(dtms):
    relat_le = dtms["relat_le"]
    triang_rms = dtms["triang_rms"]
    good = (relat_le <= 5.0) & (triang_rms <= 20.0)
    fair = (relat_le <= 10.0) & (triang_rms <= 40.0) & ~good
    return np.select([good, fair], ["good", "fair"], default="poor")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    dtms, pits = load_layers()
    dtms["quality"] = quality_tier(dtms)

    relevant = pits[pits["Terrain"].isin(RELEVANT_TERRAIN)].copy()
    relevant["pit_id"] = relevant.index

    dtm_join = dtms[["DTM_NAME", "sitename", "resolution", "relat_le", "triang_rms",
                     "lola_rms", "cov_sqkm", "completion", "num_stereo", "quality",
                     "url", "geometry"]]

    joined = gpd.sjoin(relevant, dtm_join, how="left", predicate="within")

    join_cols = ["Name", "Terrain", "Type", "Latitude", "Longitude", "InMaxDiam",
                 "Depth", "Overhang", "StereoIDs", "DTM",
                 "DTM_NAME", "sitename", "resolution", "relat_le", "triang_rms",
                 "lola_rms", "cov_sqkm", "num_stereo", "quality", "completion", "url"]
    joined_out = joined[join_cols].copy()
    joined_out.to_csv(OUT_DIR / "relevant_pits_x_dtms.csv", index=False)

    per_pit = joined.groupby("pit_id").agg(
        Name=("Name", "first"),
        Terrain=("Terrain", "first"),
        Latitude=("Latitude", "first"),
        Longitude=("Longitude", "first"),
        n_dtm_overlaps=("DTM_NAME", lambda s: s.notna().sum()),
        best_resolution=("resolution", "min"),
        best_relat_le=("relat_le", "min"),
        best_quality=("quality", lambda s: s.dropna().min() if s.notna().any() else np.nan),
        atlas_dtm_field=("DTM", "first"),
        stereo_ids=("StereoIDs", "first"),
    ).reset_index(drop=True)

    def coverage(row):
        if row["n_dtm_overlaps"] > 0:
            return "HAS_DTM"
        if isinstance(row["stereo_ids"], str) and row["stereo_ids"].strip() not in ("", "N/A"):
            return "STEREO_NO_DTM"
        return "NO_COVERAGE"
    per_pit["coverage_class"] = per_pit.apply(coverage, axis=1)

    per_pit.to_csv(OUT_DIR / "pit_coverage_summary.csv", index=False)

    all_pits_covered = gpd.sjoin(pits, dtm_join[["DTM_NAME", "quality", "geometry"]],
                                 how="left", predicate="within")
    pit_has_dtm = all_pits_covered.groupby(level=0)["index_right"].any()
    pits["has_dtm"] = pit_has_dtm.reindex(pits.index).fillna(False)
    coverage_by_terrain = pits.groupby("Terrain").agg(
        total=("has_dtm", "size"),
        in_dtm=("has_dtm", "sum"),
    )
    coverage_by_terrain["pct"] = 100 * coverage_by_terrain["in_dtm"] / coverage_by_terrain["total"]
    coverage_by_terrain.to_csv(OUT_DIR / "coverage_by_terrain_all_278_pits.csv")

    rille_pat = ("rima|rilles|vallis|prinz|schroter|hadley|sharp|marius.*rille|"
                 "rille.*marius|sinuous")
    rille_dtms = dtms[
        dtms["sitename"].str.contains(rille_pat, case=False, na=False, regex=True)
        | dtms["features"].str.contains(rille_pat, case=False, na=False, regex=True)
    ]
    rille_dtms.drop(columns="geometry").to_csv(OUT_DIR / "rille_related_dtms.csv", index=False)

    fig, ax = plt.subplots(figsize=(14, 7.5))
    colors = {"good": "#2c7bb6", "fair": "#abd9e9", "poor": "#fdae61"}
    for tier, color in colors.items():
        sub = dtms[dtms["quality"] == tier]
        sub.boundary.plot(ax=ax, linewidth=0.5, color=color,
                          label=f"DTM {tier} (n={len(sub)})")
    pits[pits["Terrain"] == "Impact Melt"].plot(
        ax=ax, marker=".", color="grey", markersize=8, alpha=0.5, label="Impact-melt pits (n=257)")
    relevant.plot(ax=ax, marker="*", color="crimson", markersize=160, edgecolor="k",
                  linewidth=0.4, label="Tube-relevant pits (n=21)")
    for _, r in relevant.iterrows():
        ax.annotate(r["Name"], (r.geometry.x, r.geometry.y), fontsize=5.5,
                    xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("Longitude (deg, -180..180)")
    ax.set_ylabel("Latitude (deg)")
    ax.set_title("LUNARVOID WP0 scope map: NAC DTM footprints (through 2026-06-15) vs tube-relevant pits")
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax.set_xlim(-185, 185)
    ax.set_ylim(-90, 95)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "wp0_scope_map_overview.png", dpi=200)

    print(f"DTMs total: {len(dtms)}  quality: {dtms['quality'].value_counts().to_dict()}")
    print(f"Relevant pits: {len(relevant)} (mare={sum(relevant['Terrain']=='Mare')}, "
          f"highland={sum(relevant['Terrain']=='Highland')})")
    print("\nCoverage class counts:")
    print(per_pit["coverage_class"].value_counts().to_string())
    print("\nPits WITH published DTM coverage:")
    print(per_pit[per_pit["coverage_class"] == "HAS_DTM"][
        ["Name", "Terrain", "best_resolution", "best_relat_le", "best_quality",
         "atlas_dtm_field"]].to_string(index=False))
    print("\nPits with stereo but no DTM:")
    stereo_pits = per_pit[per_pit["coverage_class"] == "STEREO_NO_DTM"]
    print(stereo_pits[["Name", "Terrain", "stereo_ids"]].to_string(index=False)
          if len(stereo_pits) else "(none)")
    print("\nNo coverage at all:")
    none_pits = per_pit[per_pit["coverage_class"] == "NO_COVERAGE"]
    print(none_pits[["Name", "Terrain"]].to_string(index=False) if len(none_pits) else "(none)")
    print("\nAtlas 'DTM' field vs spatial-join agreement (relevant pits):")
    agree = per_pit.apply(
        lambda r: (isinstance(r["atlas_dtm_field"], str)
                   and r["n_dtm_overlaps"] > 0)
        or (not isinstance(r["atlas_dtm_field"], str) and r["n_dtm_overlaps"] == 0),
        axis=1)
    print(f"  agreement: {agree.sum()}/{len(per_pit)}")
    mism = per_pit[~agree]
    if len(mism):
        print(mism[["Name", "atlas_dtm_field", "n_dtm_overlaps"]].to_string(index=False))
    print(f"\nCoverage of all 278 pits by terrain:")
    print(coverage_by_terrain.to_string())
    print(f"\nRille-related DTM products: {len(rille_dtms)}")
    print(f"\nOutputs written to {OUT_DIR} and {FIG_DIR}")


if __name__ == "__main__":
    main()
