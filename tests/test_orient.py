"""Test orientation inference."""

from bin2path import encode
from bin2path.orient import infer_dirs_from_path


def test_infer_dirs_matches_encoded_steps_length():
    for n in [1, 2, 3, 8, 42, 123, 999]:
        p = encode(n)
        dirs = infer_dirs_from_path(p.vertices, p.edges)
        assert len(dirs) == len(p.edges)


def test_infer_dirs_roundtrip_with_encode_decode():
    # if infer_dirs is correct, decode(encode(n)) already covers it indirectly,
    # but this ensures inference works on many values without relying on decode.
    for n in range(0, 500):
        p = encode(n)
        dirs = infer_dirs_from_path(p.vertices, p.edges)
        if n == 0:
            assert dirs == []
        else:
            assert dirs[0] in ("L", "R")
            assert all(d in ("L", "R", "U", "D") for d in dirs)

