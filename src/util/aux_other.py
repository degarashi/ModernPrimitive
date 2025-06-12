from abc import ABC, abstractmethod
from contextlib import contextmanager

import bmesh
from bmesh.types import BMesh
from bpy.types import Mesh, Object


class classproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)


class BMeshWrap(ABC):
    bm: BMesh

    def __init__(self, mesh: Mesh):
        self.bm = self.on_init(mesh)

    @abstractmethod
    def on_init(self, mesh: Mesh) -> BMesh:
        pass

    @abstractmethod
    def on_exit(self, mesh: Mesh) -> None:
        pass

    @abstractmethod
    def on_update(self, mesh: Mesh) -> None:
        pass


class BMW_ObjMode(BMeshWrap):
    def on_init(self, mesh: Mesh) -> BMesh:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        return bm

    def on_exit(self, mesh: Mesh) -> None:
        self.bm.free()

    def on_update(self, mesh: Mesh) -> None:
        self.bm.to_mesh(mesh)


class BMW_EditMode(BMeshWrap):
    def on_init(self, mesh: Mesh) -> BMesh:
        return bmesh.from_edit_mesh(mesh)

    def on_exit(self, mesh: Mesh) -> None:
        pass

    def on_update(self, mesh: Mesh) -> None:
        bmesh.update_edit_mesh(mesh)


# call in OBJECT-mode only
@contextmanager
def make_bmesh(
    mesh: Mesh,
    in_edit_mode: bool = False,
    update_mesh: bool = True,
    recalc_normals: bool = True,
):
    proc: BMeshWrap = BMW_EditMode(mesh) if in_edit_mode else BMW_ObjMode(mesh)

    try:
        yield proc.bm
    finally:
        if recalc_normals:
            proc.bm.normal_update()
        if update_mesh:
            proc.on_update(mesh)
            mesh.update()
        proc.on_exit(mesh)


@contextmanager
def get_tomesh(obj: Object):
    try:
        yield obj.to_mesh()
    finally:
        obj.to_mesh_clear()


@contextmanager
def get_bmesh(
    obj: Object,
    in_edit_mode: bool = False,
    update_mesh: bool = True,
    recalc_normals: bool = True,
):
    with (
        get_tomesh(obj) as mesh,
        make_bmesh(mesh, in_edit_mode, update_mesh, recalc_normals) as bm,
    ):
        yield bm
