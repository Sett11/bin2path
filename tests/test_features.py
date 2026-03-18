"""Test features function."""

import pytest
from bin2path import encode, features


def test_features_basic():
    """Test basic feature extraction."""
    path = encode(42)
    f = features(path)
    
    assert "path_length" in f
    assert "turns" in f
    assert "direct_distance" in f
    assert "center_x" in f
    assert "original_number" in f
    assert f["original_number"] == 42
    assert f["bits_length"] == 6


def test_features_path_length():
    """Test path length is correct."""
    path = encode(42)  # 6 bits -> 6 actions -> 6 edges
    f = features(path)
    assert f["path_length"] == len(path.edges)


def test_features_turns():
    """Test turn count."""
    path = encode(1)  # Only 1 bit = 1, no turn
    f = features(path)
    assert f["turns"] == 0


def test_features_direction_histogram():
    """Test direction histogram."""
    path = encode(1)
    f = features(path)
    assert "direction_histogram" in f
    hist = f["direction_histogram"]
    assert "+Z" in hist
    assert hist["+Z"] == 1  # One step in +Z (start forward direction)


def test_features_self_intersections():
    """Test self-intersection detection."""
    path = encode(1)
    f = features(path)
    assert f["self_intersections"] == 0


def test_features_displacement():
    """Test displacement calculation."""
    path = encode(42)
    f = features(path)
    
    start = path.vertices[0]
    end = path.vertices[-1]
    
    assert f["displacement_x"] == end[0] - start[0]
    assert f["displacement_y"] == end[1] - start[1]
    assert f["displacement_z"] == end[2] - start[2]


def test_features_straightness():
    """Test straightness ratio."""
    path = encode(1)  # Straight line - single edge
    f = features(path)
    assert f["straightness"] == 1.0


def test_features_zero_path():
    """Features should be well-defined for the trivial 0-path."""
    path = encode(0)
    f = features(path)
    assert f["path_length"] == 0
    assert f["turns"] == 1  # bits_length(0) is 1, edges is 0
    assert f["direct_distance"] == 0.0
    assert f["straightness"] == 0
    assert f["self_intersections"] == 0