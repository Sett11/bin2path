"""Batch operations for encoding/decoding multiple items."""

from bin2path.path import Path3D
from bin2path.encode import encode
from bin2path.decode import decode
from typing import List


def batch_encode(numbers: List[int]) -> List[Path3D]:
    """
    Encode multiple numbers into paths.
    
    Args:
        numbers: List of non-negative integers.
        
    Returns:
        List of Path3D objects.
        
    Raises:
        ValueError: If any number is invalid.
    """
    return [encode(n) for n in numbers]


def batch_decode(paths: List[Path3D]) -> List[int]:
    """
    Decode multiple paths back to numbers.
    
    Args:
        paths: List of Path3D objects.
        
    Returns:
        List of original numbers.
        
    Raises:
        ValueError: If any path is invalid.
    """
    return [decode(p) for p in paths]