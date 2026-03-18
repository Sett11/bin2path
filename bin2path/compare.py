"""Compare two paths for similarity."""

from bin2path.path import Path3D
from bin2path.features import features
import numpy as np
import math
from typing import Optional


def compare(
    path1: Path3D,
    path2: Path3D,
    method: str = "features",
) -> dict:
    """
    Compare two paths and return similarity metrics.
    
    Args:
        path1: First Path3D object.
        path2: Second Path3D object.
        method: Comparison method - "features", "hausdorff", or "dtw".
        
    Returns:
        Dictionary with similarity metrics.
        
    Raises:
        ValueError: If method is unknown.
    """
    if method == "features":
        return _compare_features(path1, path2)
    elif method == "hausdorff":
        return _compare_hausdorff(path1, path2)
    elif method == "dtw":
        return _compare_dtw(path1, path2)
    else:
        raise ValueError(f"Unknown comparison method: {method}")


def _compare_features(path1: Path3D, path2: Path3D) -> dict:
    """Compare paths using extracted features."""
    f1 = features(path1)
    f2 = features(path2)
    
    # Numeric features to compare
    numeric_keys = [
        "path_length",
        "turns",
        "direct_distance",
        "straightness",
        "self_intersections",
    ]
    
    differences = {}
    for key in numeric_keys:
        diff = abs(f1.get(key, 0) - f2.get(key, 0))
        differences[key] = diff
    
    # Direction histogram comparison (L1 distance)
    hist1 = f1.get("direction_histogram", {})
    hist2 = f2.get("direction_histogram", {})
    hist_diff = sum(abs(hist1.get(k, 0) - hist2.get(k, 0)) for k in set(hist1) | set(hist2))
    
    # Combined similarity score (lower = more similar)
    total_diff = sum(differences.values()) + hist_diff * 0.1
    
    return {
        "method": "features",
        "feature_differences": differences,
        "direction_histogram_diff": hist_diff,
        "total_difference": total_diff,
        "similarity_score": 1.0 / (1.0 + total_diff),
    }


def _compare_hausdorff(path1: Path3D, path2: Path3D) -> dict:
    """Compute Hausdorff distance between path vertex sets."""
    v1 = np.array(path1.vertices)
    v2 = np.array(path2.vertices)

    # Guard against empty vertex sets (defensive: Path3D normally enforces vertices exist)
    if v1.size == 0 and v2.size == 0:
        forward = 0.0
        backward = 0.0
    elif v1.size == 0:
        forward = math.inf
        backward = 0.0
    elif v2.size == 0:
        forward = 0.0
        backward = math.inf
    else:
        # Forward Hausdorff: max distance from any point in v1 to nearest in v2
        forward = max(np.linalg.norm(p - v2, axis=1).min() for p in v1)

        # Backward: max distance from any point in v2 to nearest in v1
        backward = max(np.linalg.norm(p - v1, axis=1).min() for p in v2)
    
    hausdorff = max(forward, backward)
    
    return {
        "method": "hausdorff",
        "forward_hausdorff": float(forward),
        "backward_hausdorff": float(backward),
        "hausdorff_distance": float(hausdorff),
    }


def _compare_dtw(path1: Path3D, path2: Path3D, max_cost: Optional[float] = None) -> dict:
    """Compute Dynamic Time Warping distance between paths."""
    # For 3D paths, use vertex positions as time series
    v1 = np.array(path1.vertices)
    v2 = np.array(path2.vertices)
    
    n, m = len(v1), len(v2)
    
    # DTW matrix
    dtw = np.full((n + 1, m + 1), float("inf"))
    dtw[0, 0] = 0
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = np.linalg.norm(v1[i - 1] - v2[j - 1])
            dtw[i, j] = cost + min(
                dtw[i - 1, j],      # insertion
                dtw[i, j - 1],      # deletion
                dtw[i - 1, j - 1],  # match
            )
    
    dtw_distance = dtw[n, m]
    
    # Normalize by path length
    normalized = dtw_distance / ((n + m) / 2)
    
    return {
        "method": "dtw",
        "dtw_distance": float(dtw_distance),
        "normalized_dtw": float(normalized),
        "path1_length": n,
        "path2_length": m,
    }