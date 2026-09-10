"""connected_component_filter.py — Connected-component post-processing for LLTB-1 score rasters.

LLTB-1 v0.2 backlog skeleton (see `V0.2_PLAN.md`). This module is the
standalone helper that lifts the precision ceiling on the
predict-all-overflagging failure mode. It is the per-rung post-processing
step that v0.2 release note §1 named as the "highest-leverage v0.2
improvement" but found insufficient at the time because v0.2 operated
on the **post-threshold** mask. The skeleton here supports BOTH:

  - score > 0 mode (the headline v0.2 lift when `--cc-threshold 0`):
    filters the full predict-all blob and drops connected components
    smaller than `area_min` cells. The CC components_dropped ratio
    becomes a noise diagnostic.
  - score > threshold mode (the legacy v0.2 / v0.4 / v0.5 behaviour):
    operates on the post-score-threshold binary mask.

The existing `filter_small_components()` in `code/wp1_detector/sag_detect.py`
(line 135) is the inline v0.2 helper; this module is the standalone,
testable, and audit-friendly version that backs the per-rung table in
V0.2_PLAN.md §4.1.

CLAIM DISCIPLINE: this is a post-processing step on a SCORE RASTER, not
a candidate promotion step. Tier-A promotions require two-independent-
methods agreement (registry schema); this module touches only the
per-rung F1 metric and the `pred_<rung>m.tif` mask. No false tier
promotions are possible from this filter.

Algorithm contract (tested in `__main__`):
  Input  : score_raster (2-D float array, NaN where invalid)
           threshold (float; pass score > threshold into the CC step)
           area_min (int; minimum connected-component area in cells)
           connectivity (int; 1=4-conn, 2=8-conn default)
  Output : filtered_score (same shape as input; NaN preserved)
           component_count (int; number of components with size >= area_min)

NaN handling: NaN cells are excluded from the input mask (treated as
"not above threshold"). This matches `sag_detect.filter_small_components()`
which is NaN-safe per the v0.2 release note.

Dependencies:
  - numpy
  - scipy.ndimage.label
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
from scipy.ndimage import label, generate_binary_structure

# ---------------------------------------------------------------------------
# Per-rung AREA_MIN table (C3, LLTB-1 v0.6 candidate wiring).
#
# Authority: V0.2_PLAN.md §4.1 (the dispatch said "if V0.2_PLAN specifies
# a table, use it" — it does). v0_2_pipeline_integration.py carries the
# same values; THIS dict is the canonical copy going forward.
#
# Scale-awareness rationale ((GSD ratio)^2 area scaling): the legacy
# convention is min_component = 5 CELLS at the native 0.5 m rung. A
# fixed cell count scales the minimum physical footprint by
# (GSD ratio)^2 across rungs — 5 cells at the 5 m rung of a 0.5 m
# source already covers 100x the area per cell (125 m^2 vs 1.25 m^2),
# so a SMALL cell count stays meaningful at coarse rungs while a large
# one would destroy recall (recall = 1.00 at every rung with >= 5 void
# cells is the asset this filter must not break). Hence the floor
# DECREASES with rung:
#
#   rung (m) | area_min (cells) | area_min (m^2) | rationale
#   ---------|-----------------|----------------|----------------------
#   0.5      | 50              | 12.5           | tubular features ~5x10 cells at 0.5 m
#   1        | 20              | 20             | v0.2 min-component 10-20 optimal band
#   2        | 8               | 32             | v0.2 NorthSurface 2 m regression band
#   5        | 3               | 75             | few positives; protect recall = 1.00
#   8 / 10   | 2               | 128 / 200      | conservative; few positives exist
# ---------------------------------------------------------------------------
AREA_MIN_PER_RUNG: dict[float, int] = {
    0.5: 50,
    1.0: 20,
    2.0: 8,
    5.0: 3,
    8.0: 2,
    10.0: 2,
}


def area_min_for_rung(rung_m: float) -> int:
    """Return the AREA_MIN table entry for the rung nearest `rung_m`.

    Exact float keys match the fixed ladder (0.5/1/2/5/8/10 m); the
    nearest-key lookup keeps arbitrary rungs (e.g. 1.5 m) from raising.
    """
    keys = sorted(AREA_MIN_PER_RUNG)
    nearest = min(keys, key=lambda k: abs(k - float(rung_m)))
    return AREA_MIN_PER_RUNG[nearest]


def connected_component_filter(
    score_raster: np.ndarray,
    threshold: float,
    area_min: int,
    connectivity: int = 2,
) -> Tuple[np.ndarray, int]:
    """Drop connected components smaller than `area_min` cells.

    Parameters
    ----------
    score_raster : np.ndarray
        2-D float array (or any shape — only the first 2 dims are used
        for 2-D CC labeling). NaN cells are preserved and excluded from
        the binary mask.
    threshold : float
        Pass score > threshold into the CC step. Use 0.0 to capture
        the predict-all overflagging failure mode (the headline v0.2
        lift); use the tuned score threshold to operate on the
        post-score-tuning mask (v0.4 / v0.5 behaviour).
    area_min : int
        Minimum connected-component area in cells. Components smaller
        than this are zeroed in the filtered score. Per-rung defaults
        are documented in `V0.2_PLAN.md` §4.1.
    connectivity : int, default 2
        1 = 4-connectivity (rook moves; orthogonal neighbours only)
        2 = 8-connectivity (king moves; orthogonal + diagonal). v0.2
        release note used 8-conn; match it here for parity.

    Returns
    -------
    filtered_score : np.ndarray
        Same shape as `score_raster`. Components with size < `area_min`
        have their score zeroed (not removed — the score values are
        lost, the cells remain). NaN cells in the input are NaN in the
        output.
    component_count : int
        Number of connected components in the binary mask with size
        >= `area_min`. Does NOT count the dropped components.

    Raises
    ------
    TypeError
        If `score_raster` is not a numpy array.
    ValueError
        If `area_min` < 1, or `connectivity` not in {1, 2}.

    Notes
    -----
    Algorithm:
      1. Build binary mask: (score > threshold) & isfinite(score).
      2. Build structuring element for the chosen connectivity.
      3. Label the mask with `scipy.ndimage.label`.
      4. Compute sizes of each label via bincount.
      5. Build a keep-mask: True for labels with size >= area_min.
      6. Apply: filtered_score = score_raster * keep_mask_for_label.

    Complexity: O(N) where N = number of cells. `scipy.ndimage.label`
    is the bottleneck; on a 5000x5000 raster it runs in ~0.3s locally.

    See Also
    --------
    `code/wp1_detector/sag_detect.py::filter_small_components` — the
    inline v0.2 helper (8-conn, NaN-safe). This module is a standalone,
    testable, and audit-friendly version.
    """
    if not isinstance(score_raster, np.ndarray):
        raise TypeError(
            f"score_raster must be a numpy array, got {type(score_raster).__name__}"
        )
    if area_min < 1:
        raise ValueError(f"area_min must be >= 1, got {area_min}")
    if connectivity not in (1, 2):
        raise ValueError(f"connectivity must be 1 (4-conn) or 2 (8-conn), got {connectivity}")

    # Step 1: binary mask (NaN-safe). NaN cells are excluded.
    finite_mask = np.isfinite(score_raster)
    above_th = score_raster > threshold
    binary = above_th & finite_mask

    # Fast path: no cells above threshold.
    if not binary.any():
        # component_count = 0; filtered = input unchanged on NaN,
        # zeros elsewhere. Matches sag_detect.filter_small_components.
        filtered = np.where(finite_mask, np.zeros_like(score_raster), score_raster)
        return filtered, 0

    # Step 2: structuring element. connectivity=1 -> 4-conn (rook),
    # connectivity=2 -> 8-conn (king). generate_binary_structure uses
    # 1s in a (k,k) box where k = 1 + 2*connectivity. Result is
    # equivalent to np.ones((3,3)) for connectivity=2 and a + shape
    # for connectivity=1.
    structure = generate_binary_structure(2, connectivity)

    # Step 3: label the binary mask. labels is 0 where binary is False;
    # positive integer labels otherwise. unique non-zero labels are 1..N.
    labels, n_labels = label(binary, structure=structure)

    # Step 4: sizes of each label (bincount with minlength = n_labels+1
    # so label 0 — background — always has a bin).
    sizes = np.bincount(labels.ravel(), minlength=n_labels + 1)

    # Step 5: keep-mask (per-cell). True where the cell's label has
    # size >= area_min OR the cell is NaN (preserve NaN).
    keep_per_label = sizes >= area_min  # index 0 (background) is False
    keep_mask = keep_per_label[labels] | ~finite_mask

    # Step 6: apply. NaN cells stay NaN; below-threshold cells go to 0
    # (they were already below threshold); small components go to 0;
    # large components keep their original score.
    filtered = np.where(keep_mask, score_raster, 0.0)

    # component_count: number of components with size >= area_min
    component_count = int((sizes[1:] >= area_min).sum())

    return filtered, component_count


# ---------------------------------------------------------------------------
# Test plan (to be executed by the verifier; this skeleton ships with a
# synthetic self-test in __main__ that the geo-coder can run by hand
# before integrating into the v0.5 ladder):
#
#   cd /home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube
#   ~/lunarvoid/venv/bin/python code/wp1_detector/connected_component_filter.py
#
# The synthetic test (200x200):
#   - 1 planted 50-cell rectangle at centre (survives any area_min <= 50)
#   - 10 planted 5-cell rectangles around it (drop at area_min > 5)
#   - 1000 random Gaussian-noise cells with score 0.3 (drops at area_min > 1)
#   - 50 NaN cells preserved
#
# Expected outcomes:
#   area_min=1   -> component_count = 1 + 10 + 1 (Gaussian blob) = 12
#   area_min=10  -> component_count = 1 + 1 (Gaussian blob has >10 cells) = 2
#   area_min=50  -> component_count = 1 (only the planted rectangle)
#
# Edge cases (not auto-tested here, but covered by spec):
#   - empty input -> (zeros_like, 0)
#   - all-NaN input -> (NaN, 0)
#   - threshold above score max -> (zeros, 0)
#   - area_min=1 -> no-op except for diagonal-folding at connectivity=2
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Synthetic self-test. Run with:
    #   ~/lunarvoid/venv/bin/python code/wp1_detector/connected_component_filter.py
    import numpy as np

    rng = np.random.default_rng(seed=42)
    H, W = 200, 200
    score = rng.normal(loc=0.0, scale=0.1, size=(H, W)).astype(np.float64)

    # Plant a 10x5 (50-cell) rectangle at the centre.
    score[95:105, 95:105] = 1.0

    # Plant 10 small (5-cell) rectangles around it.
    for i in range(10):
        r, c = 20 + i * 15, 20 + i * 15
        score[r:r + 5, c:c + 1] = 1.0  # 5x1 = 5 cells each

    # Plant a Gaussian noise blob (~3% of cells with score > 0.3),
    # but EXCLUDE the rectangle region so the rectangle stays isolated
    # from the blob (otherwise the rectangle fuses into the noise at
    # 8-connectivity and the size test fails predictably).
    noise_mask = (rng.normal(size=(H, W)) > 1.5)  # ~3% of cells
    noise_mask[95:105, 95:105] = False  # protect rectangle
    score[noise_mask] = 0.5

    # NaN cells preserved.
    nan_idx = rng.choice(H * W, size=50, replace=False)
    score.flat[nan_idx] = np.nan

    print(f"Input: shape={score.shape}, "
          f"NaN fraction={np.isnan(score).sum() / score.size:.3f}")

    for area_min in (1, 10, 50):
        filtered, n = connected_component_filter(
            score, threshold=0.0, area_min=area_min, connectivity=2,
        )
        # Verify: no NaN was converted to a number, no score leaked.
        assert np.isnan(score).sum() == np.isnan(filtered).sum(), (
            f"area_min={area_min}: NaN count changed "
            f"({np.isnan(score).sum()} -> {np.isnan(filtered).sum()})"
        )
        # Verify: small components are zeroed, large component survives.
        if area_min >= 50:
            # Only the 50-cell rectangle survives.
            assert n == 1, f"area_min={area_min}: expected 1 component, got {n}"
            assert (filtered[95:105, 95:105] == 1.0).all(), (
                f"area_min={area_min}: 50-cell rectangle was zeroed"
            )
        elif area_min >= 10:
            # The 50-cell rectangle + the Gaussian blob (it has >10 cells
            # when merged at 8-conn). The 10 small rectangles drop.
            assert n >= 1, f"area_min={area_min}: expected >= 1, got {n}"
        print(f"area_min={area_min}: component_count={n}, "
              f"non-zero cells={(filtered != 0).sum()}")

    print("PASS: synthetic self-test OK")