"""Test batch operations."""

import pytest
from bin2path import batch_encode, batch_decode


def test_batch_encode():
    """Test batch encoding."""
    numbers = [1, 2, 42, 100]
    paths = batch_encode(numbers)
    
    assert len(paths) == 4
    assert paths[0].metadata.original_number == 1
    assert paths[1].metadata.original_number == 2
    assert paths[2].metadata.original_number == 42
    assert paths[3].metadata.original_number == 100


def test_batch_decode():
    """Test batch decoding."""
    from bin2path import encode
    
    numbers = [1, 2, 42, 100]
    paths = batch_encode(numbers)
    decoded = batch_decode(paths)
    
    assert decoded == numbers


def test_batch_roundtrip():
    """Test batch roundtrip."""
    import random
    
    numbers = [random.randint(0, 10000) for _ in range(100)]
    paths = batch_encode(numbers)
    decoded = batch_decode(paths)
    
    assert decoded == numbers