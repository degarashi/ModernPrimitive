from contextlib import contextmanager

import bmesh
from bpy.types import Mesh, Object


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


@contextmanager
def get_tomesh(obj: Object):
    try:
        yield obj.to_mesh()
    finally:
        obj.to_mesh_clear()


@contextmanager
def get_bmesh(obj: Object, update_mesh: bool = True, recalc_normals: bool = True):
    with get_tomesh(obj) as mesh, make_bmesh(mesh, update_mesh, recalc_normals) as bm:
        yield bm
