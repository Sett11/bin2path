"""Encode a number into a 3D path using the L/R/U/D cellular-automaton scheme."""

from bin2path.path import Path3D, PathMetadata
from bin2path.orient import apply_step, Vec3


def _get_bits_msb(n: int) -> list[int]:
    """Return bits of n in MSB->LSB order."""
    if n == 0:
        return [0]
    bits: list[int] = []
    while n > 0:
        bits.insert(0, n & 1)
        n >>= 1
    return bits


START_FORWARD: Vec3 = (0, 0, 1)
START_UP: Vec3 = (0, 1, 0)


def _encode_dirs(bits: list[int]) -> list[str]:
    """
    Encode bit sequence (MSB first) into sequence of direction symbols L/R/U/D.

    Rules:
    - first bit:
        0 -> L
        1 -> R
    - subsequent bits:
        if bit == 0:
            if previous step == L -> D
            else -> L
        if bit == 1:
            if previous step == R -> U
            else -> R
    """
    if not bits:
        return []

    dirs: list[str] = []

    # first bit
    first = bits[0]
    cur_dir = "L" if first == 0 else "R"
    dirs.append(cur_dir)

    for b in bits[1:]:
        if b == 0:
            if cur_dir == "L":
                cur_dir = "D"
            else:
                cur_dir = "L"
        else:  # b == 1
            if cur_dir == "R":
                cur_dir = "U"
            else:
                cur_dir = "R"
        dirs.append(cur_dir)

    return dirs


def _decode_bits_from_dirs(dirs: list[str]) -> list[int]:
    """
    Inverse of _encode_dirs with simplified rule:
    - first step: L->0, R->1
    - subsequent steps: (L,D)->0, (R,U)->1
    """
    if not dirs:
        return [0]

    bits: list[int] = []

    first = dirs[0]
    if first == "L":
        bits.append(0)
    elif first == "R":
        bits.append(1)
    else:
        raise ValueError(f"Invalid first direction {first}, expected 'L' or 'R'")

    for cur in dirs[1:]:
        if cur in ("L", "D"):
            bits.append(0)
        elif cur in ("R", "U"):
            bits.append(1)
        else:
            raise ValueError(f"Invalid direction symbol {cur}")

    return bits


def encode(number: int) -> Path3D:
    """
    Encode a natural number into a 3D path.

    The binary representation (MSB first) is mapped to a sequence of symbols
    L/R/U/D using the rules above. Symbols are then interpreted as *relative*
    moves using a local orientation frame starting with forward=+Z and up=+Y.
    """
    if not isinstance(number, int):
        raise TypeError(f"Expected integer, got {type(number).__name__}")
    if number < 0:
        raise ValueError("Number must be non-negative")

    bits = _get_bits_msb(number)
    bits_length = len(bits)

    # trivial path for 0: stay at origin
    if number == 0:
        metadata = PathMetadata(
            original_number=0,
            bits_length=1,
            first_one_pos=0,
            step_positions=[],
            start_direction=START_FORWARD,
        )
        return Path3D(vertices=[(0, 0, 0)], edges=[], metadata=metadata)

    dirs = _encode_dirs(bits)

    current_point: Vec3 = (0, 0, 0)
    vertices: list[tuple[int, int, int]] = [current_point]
    edges: list[tuple[int, int]] = []

    forward = START_FORWARD
    up = START_UP

    for d in dirs:
        vec, forward, up = apply_step(d, forward, up)
        new_point = (
            current_point[0] + vec[0],
            current_point[1] + vec[1],
            current_point[2] + vec[2],
        )
        vertices.append(new_point)
        edges.append((len(vertices) - 2, len(vertices) - 1))
        current_point = new_point

    step_positions = [i for i, b in enumerate(bits) if b == 1]

    metadata = PathMetadata(
        original_number=number,
        bits_length=bits_length,
        first_one_pos=step_positions[0] if step_positions else 0,
        step_positions=step_positions,
        start_direction=START_FORWARD,
    )

    return Path3D(vertices=vertices, edges=edges, metadata=metadata)