# bin2path

Transform numbers into 3D geometric paths.

A Python library for converting natural numbers into 3D geometric shapes (spatial polylines on an integer lattice).  
We use a **cellular-automaton scheme** that produces a sequence of symbolic steps `L/R/U/D`, and then interpret these steps as **local** (orientation-dependent) moves in 3D.

## Concept

Each number is represented as a 3D path on an integer lattice via a **discrete step rule**:

- We work with the binary representation **MSB → LSB** (left-to-right bits).
- Each bit is mapped to one of 4 **symbols**: `L/R/U/D`.
- Each symbol is then interpreted as a **relative 3D move** based on the current orientation (`forward/up/right`), so the path is not constrained to a plane.

### Bits → symbols (cellular automaton)

- **First bit**:
  - `0` → first step `L`
  - `1` → first step `R`
- **Each next bit** (only previous step matters):
  - if bit = `0`:
    - if previous step was `L` → current step `D`
    - otherwise → `L`
  - if bit = `1`:
    - if previous step was `R` → current step `U`
    - otherwise → `R`

### Symbols → 3D steps (local orientation)

We maintain a local frame:

- `forward` (where “go forward” points)
- `up` (local up)
- `right = cross(forward, up)`

Initial frame:

- `forward = (0, 0, 1)` (along +Z)
- `up      = (0, 1, 0)` (along +Y)

Step semantics (rotate if needed, then move 1 unit along the new `forward`):

- `R`: move forward
- `L`: yaw left around `up`, then move forward
- `U`: pitch up around `right`, then move forward
- `D`: pitch down around `right`, then move forward

So the path is built from `(0,0,0)` by applying these steps.

The representation is:
- **Unique**: Different numbers produce different paths
- **Reversible**: You can decode the path back to the original number
- **Deterministic**: Same number always produces same path

## Installation

```bash
pip install bin2path
```

Or from source:

```bash
git clone https://github.com/Sett11/bin2path.git
cd bin2path
pip install -e .
```

## Quick Start

```python
import bin2path

# Encode a number to 3D path
path = bin2path.encode(42)

# Get path data
print(path.vertices)    # list of (x,y,z)
print(path.edges)       # list of (from_idx, to_idx)

# Decode back to number
number = bin2path.decode(path)  # 42

# Visualize
bin2path.visualize(path)

# Extract features for clustering / analysis
f = bin2path.features(path)
print(f['path_length'])   # number of steps
print(f['turns'])         # number of direction changes (zeros)
print(f['straightness'])  # ratio of direct to path distance
```

### Example: 8 = 1000

```python
import bin2path

print(bin2path.encode(8).vertices)
# [(0, 0, 0), (0, 0, 1), (1, 0, 1), (1, -1, 1), (1, -1, 0)]
```

## API Reference

### Core Functions

- `encode(number: int) -> Path3D` — Convert number to 3D path
- `decode(path: Path3D) -> int` — Convert path back to number
- `features(path: Path3D) -> dict` — Extract features for clustering
- `visualize(path: Path3D, **kwargs)` — Render 3D visualization
- `serialize(path) -> dict` — Convert to JSON-serializable dict
- `deserialize(data) -> Path3D` — Restore from dict
- `to_json(path) -> str` — Convert to JSON string
- `from_json(json_str) -> Path3D` — Parse JSON string
- `compare(path1, path2) -> dict` — Compare similarity between paths
- `validate(path) -> (bool, list[str])` — Validate path correctness
- `is_valid(path) -> bool` — Quick validity check
- `batch_encode(numbers) -> list[Path3D]` — Encode multiple numbers
- `batch_decode(paths) -> list[int]` — Decode multiple paths

### Path3D Structure

```python
@dataclass
class Path3D:
    vertices: list[tuple[int, int, int]]  # [(x,y,z), ...]
    edges: list[tuple[int, int]]          # [(from_idx, to_idx), ...]
    metadata: PathMetadata                 # additional info

@dataclass
class PathMetadata:
    original_number: int          # original input number
    bits_length: int             # length of binary representation
    first_one_pos: int          # position of first 1-bit (MSB index)
    step_positions: list[int]   # positions of all 1-bits (MSB indices)
    start_direction: tuple      # starting forward direction (defaults to +Z)
```

### Features

The `features()` function returns a dictionary with:

- `path_length`: Number of edges/steps
- `turns`: Approximate number of bit-0 transitions (`bits_length - len(edges)`)
- `direct_distance`: Straight-line distance from start to end
- `straightness`: Ratio of direct distance to path length
- `center_x`, `center_y`, `center_z`: Center of mass coordinates
- `bbox_x`, `bbox_y`, `bbox_z`: Bounding box dimensions
- `displacement_x`, `displacement_y`, `displacement_z`: Total displacement
- `direction_histogram`: Count of steps in ±X/±Y/±Z directions
- `self_intersections`: Number of vertex revisits

## Examples

### Roundtrip Test

```python
import bin2path

test_numbers = [0, 1, 2, 42, 100, 12345, 2**10, 999999]
for n in test_numbers:
    path = bin2path.encode(n)
    decoded = bin2path.decode(path)
    assert decoded == n  # Always True!
```

### Visualization Options

```python
import bin2path

path = bin2path.encode(42)

# Basic visualization
bin2path.visualize(path)

# Custom appearance
bin2path.visualize(
    path,
    figsize=(10, 8),
    vertex_color="red",
    edge_color="blue",
    edge_linewidth=3,
    vertex_size=50,
)

# Save to file
bin2path.visualize(path, save_path="my_path.png")

# Different viewing angle
bin2path.visualize(path, azim=45, elev=30)
```

## Requirements

- Python >= 3.10
- matplotlib >= 3.7.0
- numpy >= 1.24.0

## License

MIT License

## See Also

See [`plan.md`](plan.md) for the detailed specification of the scheme (including the local-orientation rules).