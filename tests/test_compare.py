"""Test compare function."""

import pytest

from bin2path import compare, encode


def test_compare_features_identity():
    """Same path should have perfect similarity score in features method."""
    p = encode(42)
    result = compare(p, p, method="features")
    assert result["method"] == "features"
    assert result["total_difference"] == 0
    assert result["similarity_score"] == 1.0


def test_compare_hausdorff_identity():
    p = encode(123)
    result = compare(p, p, method="hausdorff")
    assert result["method"] == "hausdorff"
    assert result["hausdorff_distance"] == 0.0


def test_compare_dtw_identity():
    p = encode(999)
    result = compare(p, p, method="dtw")
    assert result["method"] == "dtw"
    assert result["dtw_distance"] == 0.0
    assert result["normalized_dtw"] == 0.0


def test_compare_unknown_method():
    p = encode(1)
    with pytest.raises(ValueError):
        compare(p, p, method="unknown")

