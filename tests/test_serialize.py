"""Test serialize and validate functions."""

import pytest
import json
from bin2path import encode, serialize, deserialize, to_json, from_json, validate, is_valid


def test_serialize_basic():
    """Test basic serialization."""
    path = encode(42)
    data = serialize(path)
    
    assert "vertices" in data
    assert "edges" in data
    assert "metadata" in data
    assert data["metadata"]["original_number"] == 42


def test_deserialize_basic():
    """Test basic deserialization."""
    path = encode(42)
    data = serialize(path)
    restored = deserialize(data)
    
    assert restored.metadata.original_number == 42
    assert restored.metadata.bits_length == 6
    assert len(restored.vertices) == len(path.vertices)


def test_roundtrip():
    """Test serialize -> deserialize roundtrip."""
    original = encode(999)
    data = serialize(original)
    restored = deserialize(data)
    
    assert restored.metadata.original_number == original.metadata.original_number
    assert restored.metadata.bits_length == original.metadata.bits_length


def test_to_json():
    """Test JSON string conversion."""
    path = encode(123)
    json_str = to_json(path)
    
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["metadata"]["original_number"] == 123


def test_from_json():
    """Test JSON string parsing."""
    path = encode(123)
    json_str = to_json(path)
    restored = from_json(json_str)
    
    assert restored.metadata.original_number == 123


def test_validate_valid_path():
    """Test validation of valid path."""
    path = encode(42)
    is_valid_result, errors = validate(path)
    
    assert is_valid_result is True
    assert len(errors) == 0


def test_validate_trivial_zero_path():
    """The trivial path for 0 (single vertex, no edges) should be valid."""
    path = encode(0)
    is_valid_result, errors = validate(path)
    assert is_valid_result is True
    assert errors == []


def test_is_valid():
    """Test quick validation function."""
    path = encode(42)
    assert is_valid(path) is True


def test_validate_invalid():
    """Test validation of invalid path."""
    from bin2path import Path3D, PathMetadata
    
    # Empty vertices - raises when creating Path3D
    with pytest.raises(ValueError):
        Path3D([], [], PathMetadata(0, 0))