"""Core data structures for bin2path."""

from dataclasses import dataclass


@dataclass
class PathMetadata:
    """Metadata for a 3D path."""
    original_number: int
    bits_length: int
    first_one_pos: int = 0  # position of first 1-bit (number of leading zeros)
    step_positions: list[int] = None  # positions of all 1-bits
    # Start forward direction used by the encoding/decoding scheme (defaults to +Z)
    start_direction: tuple[int, int, int] = (0, 0, 1)
    
    def __post_init__(self):
        if self.step_positions is None:
            self.step_positions = []


@dataclass
class Path3D:
    """
    3D path representation.
    
    Attributes:
        vertices: List of (x, y, z) tuples representing path vertices.
        edges: List of (from_idx, to_idx) tuples representing directed edges.
        metadata: Additional metadata about the path.
    """
    vertices: list[tuple[int, int, int]]
    edges: list[tuple[int, int]]
    metadata: PathMetadata
    
    def __post_init__(self):
        if not self.vertices:
            raise ValueError("Path must have at least one vertex")
        if len(self.edges) != len(self.vertices) - 1:
            raise ValueError("Number of edges must be equal to vertices count minus 1")
        if self.metadata.bits_length < len(self.edges):
            raise ValueError(
                "Invalid metadata: bits_length must be >= number of edges "
                f"(bits_length={self.metadata.bits_length}, edges={len(self.edges)})"
            )
    
    @property
    def start(self) -> tuple[int, int, int]:
        """Return the starting vertex."""
        return self.vertices[0] if self.vertices else (0, 0, 0)
    
    @property
    def end(self) -> tuple[int, int, int]:
        """Return the ending vertex."""
        return self.vertices[-1] if self.vertices else (0, 0, 0)
    
    @property
    def num_steps(self) -> int:
        """Return the number of steps (edges) in the path."""
        return len(self.edges)
    
    @property
    def num_turns(self) -> int:
        """
        Return the number of turn bits (0-bits) in the encoding.

        In this scheme, 1-bits produce forward steps (edges), and 0-bits produce turns.
        Since each bit corresponds to one symbolic action, the turn count is:
        turns = bits_length - edges_count
        """
        return self.metadata.bits_length - len(self.edges)