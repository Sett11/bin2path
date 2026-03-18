"""Test decode function."""

import pytest
import random
from bin2path import encode, decode


def test_decode_0():
    """Test decoding of path for 0."""
    path = encode(0)
    number = decode(path)
    assert number == 0


def test_decode_1():
    """Test decoding of path for 1."""
    path = encode(1)
    number = decode(path)
    assert number == 1


def test_decode_2():
    """Test decoding of path for 2."""
    path = encode(2)
    number = decode(path)
    assert number == 2


def test_decode_42():
    """Test decoding of path for 42."""
    path = encode(42)
    number = decode(path)
    assert number == 42


def test_decode_roundtrip_small():
    """Test roundtrip for small numbers."""
    for i in range(100):
        path = encode(i)
        number = decode(path)
        assert number == i, f"Roundtrip failed for {i}"


def test_decode_roundtrip_powers():
    """Test roundtrip for powers of 2."""
    for i in range(20):
        n = 2 ** i
        path = encode(n)
        number = decode(path)
        assert number == n


def test_decode_roundtrip_random():
    """Test roundtrip for random large numbers."""
    test_numbers = [
        12345,
        999999,
        2**15,
        2**50,
        2**100,
    ]
    for n in test_numbers:
        path = encode(n)
        number = decode(path)
        assert number == n


def test_decode_roundtrip_wide_range():
    """Stronger property-style test: many numbers across a wide range."""
    # dense small range
    for n in range(0, 50_000):
        assert decode(encode(n)) == n

    # some random larger numbers
    rng = random.Random(123456)
    samples = [rng.randrange(0, 10**18) for _ in range(500)]
    for n in samples:
        assert decode(encode(n)) == n


def test_decode_invalid_path():
    """Test that invalid paths raise error."""
    from bin2path import Path3D, PathMetadata
    
    # Empty path - raises when creating Path3D
    with pytest.raises(ValueError):
        Path3D([], [], PathMetadata(0, 0))
    
    # Single vertex with edge - raises when creating Path3D
    with pytest.raises(ValueError):
        Path3D(
            vertices=[(0, 0, 0)],
            edges=[(0, 0)],  # Invalid - points to itself
            metadata=PathMetadata(0, 1),
        )