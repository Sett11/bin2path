"""Extract features from a path for clustering."""

from bin2path.path import Path3D
import numpy as np


def features(path: Path3D) -> dict:
    """
    Extract features from a 3D path for clustering.
    
    Args:
        path: A Path3D object.
        
    Returns:
        Dictionary with feature values.
    """
    vertices = np.array(path.vertices)
    edges = path.edges
    
    # Basic metrics
    num_vertices = len(vertices)
    num_edges = len(edges)
    
    # Path length (number of steps)
    path_length = num_edges
    
    # Calculate turn count from edges
    turns = _count_turns(path)
    
    # Center of mass
    center = vertices.mean(axis=0)
    
    # Bounding box
    min_coords = vertices.min(axis=0)
    max_coords = vertices.max(axis=0)
    bbox_size = max_coords - min_coords
    
    # Start and end points
    start = path.vertices[0]
    end = path.vertices[-1]
    displacement = (
        end[0] - start[0],
        end[1] - start[1],
        end[2] - start[2],
    )
    direct_distance = np.linalg.norm(displacement)
    
    # Direction histogram
    dir_histogram = _direction_histogram(path)
    
    # Self-intersections (simplified check)
    self_intersections = _count_self_intersections(path)
    
    # Straight segment lengths histogram
    straight_segments = _straight_segment_lengths(path)
    
    return {
        "path_length": path_length,
        "turns": turns,
        "vertices_count": num_vertices,
        "center_x": float(center[0]),
        "center_y": float(center[1]),
        "center_z": float(center[2]),
        "bbox_x": float(bbox_size[0]),
        "bbox_y": float(bbox_size[1]),
        "bbox_z": float(bbox_size[2]),
        "displacement_x": displacement[0],
        "displacement_y": displacement[1],
        "displacement_z": displacement[2],
        "direct_distance": direct_distance,
        "straightness": direct_distance / num_edges if num_edges > 0 else 0,
        "direction_histogram": dir_histogram,
        "self_intersections": self_intersections,
        "straight_segments": straight_segments,
        "original_number": path.metadata.original_number,
        "bits_length": path.metadata.bits_length,
    }


def _count_turns(path: Path3D) -> int:
    """Count the number of direction changes (bits = 0)."""
    # Turns = total bits - number of steps (edges) = bits_length - num_edges
    # Это количество битов которые были 0
    return path.metadata.bits_length - len(path.edges)


def _direction_histogram(path: Path3D) -> dict:
    """Count steps in each of 6 directions."""
    histogram = {"+X": 0, "-X": 0, "+Y": 0, "-Y": 0, "+Z": 0, "-Z": 0}
    
    for from_idx, to_idx in path.edges:
        from_v = path.vertices[from_idx]
        to_v = path.vertices[to_idx]
        dx = to_v[0] - from_v[0]
        dy = to_v[1] - from_v[1]
        dz = to_v[2] - from_v[2]
        
        if dx == 1:
            histogram["+X"] += 1
        elif dx == -1:
            histogram["-X"] += 1
        elif dy == 1:
            histogram["+Y"] += 1
        elif dy == -1:
            histogram["-Y"] += 1
        elif dz == 1:
            histogram["+Z"] += 1
        elif dz == -1:
            histogram["-Z"] += 1
    
    return histogram


def _count_self_intersections(path: Path3D) -> int:
    """Count vertex revisits (simple intersection check)."""
    seen = {}
    intersections = 0
    
    for i, v in enumerate(path.vertices):
        if v in seen:
            intersections += 1
        else:
            seen[v] = i
    
    return intersections


def _straight_segment_lengths(path: Path3D) -> dict:
    """Histogram of straight segment lengths along any single axis."""
    lengths: list[int] = []
    current_length = 0
    current_dir: tuple[int, int, int] | None = None

    for from_idx, to_idx in path.edges:
        from_v = path.vertices[from_idx]
        to_v = path.vertices[to_idx]
        edge_dir = (to_v[0] - from_v[0], to_v[1] - from_v[1], to_v[2] - from_v[2])

        if current_dir is None or edge_dir == current_dir:
            current_length += 1
            current_dir = edge_dir
        else:
            if current_length > 0:
                lengths.append(current_length)
            current_length = 1
            current_dir = edge_dir

    if current_length > 0:
        lengths.append(current_length)

    hist: dict[int, int] = {}
    for l in lengths:
        hist[l] = hist.get(l, 0) + 1

    return hist