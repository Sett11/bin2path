"""Test encode function."""

import pytest
from bin2path import encode, decode


def test_encode_0():
    """Test encoding of 0."""
    path = encode(0)
    assert path.metadata.original_number == 0
    assert path.metadata.bits_length == 1  # single zero bit
    assert path.vertices == [(0, 0, 0)]
    assert path.edges == []
    assert decode(path) == 0


def test_encode_1():
    """Test encoding of 1."""
    path = encode(1)
    assert path.metadata.original_number == 1
    assert path.metadata.bits_length == 1  # 1 -> [1]
    # one step => two vertices, one edge
    assert len(path.vertices) == 2
    assert len(path.edges) == 1
    assert decode(path) == 1


def test_encode_2():
    """Test encoding of 2."""
    path = encode(2)
    assert path.metadata.original_number == 2
    assert path.metadata.bits_length == 2  # 2 -> [0, 1]
    # two bits => two steps
    assert len(path.edges) == 2
    assert decode(path) == 2


def test_encode_42():
    """Test encoding of 42 - roundtrip only."""
    path = encode(42)
    assert path.metadata.original_number == 42
    assert path.metadata.bits_length == 6  # 42 = 101010
    assert decode(path) == 42


def test_encode_negative():
    """Test that negative numbers raise error."""
    with pytest.raises(ValueError):
        encode(-1)


def test_encode_non_integer():
    """Test that non-integers raise error."""
    with pytest.raises(TypeError):
        encode(3.14)
    with pytest.raises(TypeError):
        encode("42")


def test_encode_large_number():
    """Test encoding a large number."""
    path = encode(2**20)
    assert path.metadata.original_number == 2**20
    assert path.metadata.bits_length == 21