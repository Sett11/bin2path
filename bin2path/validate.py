"""Validate Path3D objects."""

from bin2path.path import Path3D


def validate(path: Path3D) -> tuple[bool, list[str]]:
    """
    Validate a Path3D object.
    
    Args:
        path: Path3D object to validate.
        
    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    errors = []
    
    # Check vertices exist
    if not path.vertices:
        errors.append("Path must have at least one vertex")
        return False, errors
    
    # Check vertices are valid tuples
    for i, v in enumerate(path.vertices):
        if not isinstance(v, (tuple, list)) or len(v) != 3:
            errors.append(f"Vertex {i} must be a 3D coordinate tuple")
        elif not all(isinstance(c, int) for c in v):
            errors.append(f"Vertex {i} coordinates must be integers")
    
    # Check edges exist
    # Special-case: allow the trivial path for 0 (single vertex, no edges)
    if not path.edges:
        if len(path.vertices) == 1 and path.metadata and path.metadata.bits_length == 1:
            if errors:
                return False, errors
            return True, []
        errors.append("Path must have at least one edge (two vertices), unless it is the trivial 0-path")
        return False, errors
    
    # Check edges are valid
    for i, e in enumerate(path.edges):
        if not isinstance(e, (tuple, list)) or len(e) != 2:
            errors.append(f"Edge {i} must be a tuple of two indices")
            continue
        
        from_idx, to_idx = e
        
        if from_idx < 0 or from_idx >= len(path.vertices):
            errors.append(f"Edge {i}: from_index {from_idx} out of range")
        if to_idx < 0 or to_idx >= len(path.vertices):
            errors.append(f"Edge {i}: to_index {to_idx} out of range")
        
        # Check edge direction is valid (must be one of 6 axis-aligned unit directions)
        if from_idx < len(path.vertices) and to_idx < len(path.vertices):
            from_v = path.vertices[from_idx]
            to_v = path.vertices[to_idx]
            edge_dir = (
                to_v[0] - from_v[0],
                to_v[1] - from_v[1],
                to_v[2] - from_v[2],
            )
            if edge_dir not in {
                (-1, 0, 0),
                (1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1),
            }:
                errors.append(f"Edge {i}: invalid direction {edge_dir}")
    
    # Check edge count matches vertices - 1
    if len(path.edges) != len(path.vertices) - 1:
        errors.append(f"Edges count ({len(path.edges)}) must equal vertices count ({len(path.vertices)}) - 1")
    
    # Check metadata
    if not path.metadata:
        errors.append("Path must have metadata")
    elif path.metadata.bits_length <= 0:
        errors.append("bits_length must be positive")
    
    # Check path is connected (simple check)
    for i in range(len(path.edges) - 1):
        if path.edges[i][1] != path.edges[i + 1][0]:
            errors.append(f"Path is not continuous at edge {i}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def is_valid(path: Path3D) -> bool:
    """
    Quick validation check.
    
    Args:
        path: Path3D object.
        
    Returns:
        True if valid, False otherwise.
    """
    return validate(path)[0]