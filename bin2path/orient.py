"""Orientation (local frame) utilities for bin2path.

We interpret symbolic steps L/R/U/D as *relative* moves based on a current
orientation defined by two orthonormal axis-aligned vectors:
- forward: where "R" moves (go forward)
- up: local up direction (used as yaw axis)

Right vector is computed as cross(forward, up) (right-hand rule).

Step semantics (each step includes the move):
- R: move forward
- L: yaw left  (rotate forward 90° around up), then move forward
- U: pitch up  (rotate forward 90° around right), then move forward
- D: pitch down(rotate forward 90° around right), then move forward
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

Vec3 = Tuple[int, int, int]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    ax, ay, az = a
    bx, by, bz = b
    return (ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)


def _neg(v: Vec3) -> Vec3:
    return (-v[0], -v[1], -v[2])


def apply_step(sym: str, forward: Vec3, up: Vec3) -> tuple[Vec3, Vec3, Vec3]:
    """Apply a symbolic step and return (delta, new_forward, new_up)."""
    if sym not in ("L", "R", "U", "D"):
        raise ValueError(f"Invalid direction symbol {sym}")

    right = _cross(forward, up)

    if sym == "R":
        new_forward = forward
        new_up = up
        delta = new_forward
        return delta, new_forward, new_up

    if sym == "L":
        # yaw left around up: forward -> -right
        new_forward = _neg(right)
        new_up = up
        delta = new_forward
        return delta, new_forward, new_up

    if sym == "U":
        # pitch up around right: forward -> up, up -> -forward
        new_forward = up
        new_up = _neg(forward)
        delta = new_forward
        return delta, new_forward, new_up

    # sym == "D"
    # pitch down around right: forward -> -up, up -> forward
    new_forward = _neg(up)
    new_up = forward
    delta = new_forward
    return delta, new_forward, new_up


def infer_dirs_from_path(vertices: Iterable[Vec3], edges: Iterable[tuple[int, int]]) -> List[str]:
    """Infer L/R/U/D symbols from a path using the local-frame rules."""
    verts = list(vertices)
    eds = list(edges)
    if not verts:
        return []
    if not eds:
        return []

    forward: Vec3 = (0, 0, 1)
    up: Vec3 = (0, 1, 0)

    dirs: List[str] = []
    for from_idx, to_idx in eds:
        fv = verts[from_idx]
        tv = verts[to_idx]
        vec: Vec3 = (tv[0] - fv[0], tv[1] - fv[1], tv[2] - fv[2])

        right = _cross(forward, up)
        candidates: Dict[str, Vec3] = {
            "R": forward,
            "L": _neg(right),
            "U": up,
            "D": _neg(up),
        }

        sym = None
        for k, v in candidates.items():
            if vec == v:
                sym = k
                break
        if sym is None:
            raise ValueError(f"Unknown step vector {vec}, cannot infer direction symbol")

        dirs.append(sym)
        _, forward, up = apply_step(sym, forward, up)

    return dirs

