"""Decode a 3D path back into a number (L/R/U/D scheme with local orientation)."""

from bin2path.path import Path3D
from bin2path.encode import _decode_bits_from_dirs  # type: ignore
from bin2path.orient import infer_dirs_from_path


def decode(path: Path3D) -> int:
    """
    Decode a 3D path back into the original number.

    Steps:
    1) edges -> L/R/U/D using local-frame inference
    2) dirs -> bits via _decode_bits_from_dirs
    3) bits (MSB->LSB) -> integer
    """
    if not path.vertices:
        raise ValueError("Path must have at least one vertex")

    if len(path.edges) == 0:
        return 0

    if len(path.edges) != len(path.vertices) - 1:
        raise ValueError("Invalid path: edges count mismatch")

    dirs = infer_dirs_from_path(path.vertices, path.edges)

    bits = _decode_bits_from_dirs(dirs)

    n = 0
    for b in bits:
        n = (n << 1) | b
    return n