from contextlib import contextmanager

import bmesh
from bpy.types import Mesh


class classproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)


# call in OBJECT-mode only
@contextmanager
def make_bmesh(mesh: Mesh, update_mesh: bool = True, recalc_normals: bool = True):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    try:
        yield bm
    finally:
        if recalc_normals:
            bm.normal_update()
        if update_mesh:
            bm.to_mesh(mesh)
            mesh.update()
        bm.free()
