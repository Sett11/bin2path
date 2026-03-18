"""Serialize and deserialize Path3D objects."""

import json
from bin2path.path import Path3D, PathMetadata


def serialize(path: Path3D) -> dict:
    """
    Serialize a Path3D object to a dictionary (JSON-compatible).
    
    Args:
        path: Path3D object.
        
    Returns:
        Dictionary representation.
    """
    return {
        "vertices": path.vertices,
        "edges": path.edges,
        "metadata": {
            "original_number": path.metadata.original_number,
            "bits_length": path.metadata.bits_length,
            "first_one_pos": path.metadata.first_one_pos,
            "step_positions": path.metadata.step_positions,
            "start_direction": path.metadata.start_direction,
        },
    }


def deserialize(data: dict) -> Path3D:
    """
    Deserialize a dictionary to a Path3D object.
    
    Args:
        data: Dictionary with 'vertices', 'edges', 'metadata' keys.
        
    Returns:
        Path3D object.
        
    Raises:
        ValueError: If data is invalid.
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    
    if "vertices" not in data or "edges" not in data or "metadata" not in data:
        raise ValueError("Data must contain 'vertices', 'edges', and 'metadata'")
    
    vertices = data["vertices"]
    edges = data["edges"]
    metadata = data["metadata"]
    
    # Validate structure
    if not isinstance(vertices, list) or not isinstance(edges, list):
        raise ValueError("Vertices and edges must be lists")
    
    # Convert to tuples
    vertices = [tuple(v) for v in vertices]
    edges = [tuple(e) for e in edges]
    
    path_metadata = PathMetadata(
        original_number=metadata.get("original_number", 0),
        bits_length=metadata.get("bits_length", 0),
        first_one_pos=metadata.get("first_one_pos", 0),
        step_positions=metadata.get("step_positions", []),
        start_direction=tuple(metadata.get("start_direction", (1, 0, 0))),
    )
    
    return Path3D(vertices=vertices, edges=edges, metadata=path_metadata)


def to_json(path: Path3D, indent: int = 2) -> str:
    """
    Convert Path3D to JSON string.
    
    Args:
        path: Path3D object.
        indent: JSON indentation level.
        
    Returns:
        JSON string.
    """
    return json.dumps(serialize(path), indent=indent)


def from_json(json_str: str) -> Path3D:
    """
    Parse JSON string to Path3D.
    
    Args:
        json_str: JSON string.
        
    Returns:
        Path3D object.
    """
    data = json.loads(json_str)
    return deserialize(data)