"""
bin2path - Transform numbers into 3D geometric paths.

A library for converting natural numbers into 3D geometric shapes (spatial
polyline on an integer lattice). Each bit of the binary representation
is mapped to a symbolic step sequence (L/R/U/D) using a cellular-automaton rule.
Symbols are then interpreted as local (orientation-dependent) 3D moves, so the
resulting path is not constrained to a plane.

Usage:
    import bin2path
    
    path = bin2path.encode(42)
    number = bin2path.decode(path)
    bin2path.visualize(path)
    features = bin2path.features(path)
"""

from bin2path.path import Path3D, PathMetadata
from bin2path.encode import encode
from bin2path.decode import decode
from bin2path.features import features
from bin2path.visualize import visualize
from bin2path.serialize import serialize, deserialize, to_json, from_json
from bin2path.compare import compare
from bin2path.validate import validate, is_valid
from bin2path.batch import batch_encode, batch_decode

__version__ = "0.1.0"
__author__ = "bin2path"

__all__ = [
    "Path3D",
    "PathMetadata",
    "encode",
    "decode",
    "features",
    "visualize",
    "serialize",
    "deserialize",
    "to_json",
    "from_json",
    "compare",
    "validate",
    "is_valid",
    "batch_encode",
    "batch_decode",
]