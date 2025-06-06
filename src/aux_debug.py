from collections.abc import Iterable

from mathutils import Vector


def print_vertices(verts: Iterable[Vector]) -> None:
    for v in verts:
        print(v)
