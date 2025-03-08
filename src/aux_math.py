import math
from collections.abc import Iterable
from math import isclose as m_isclose
from sys import float_info
from typing import NamedTuple

from bpy.types import Object
from mathutils import Quaternion, Vector


def make_vec3(val: float) -> Vector:
    return Vector([val] * 3)


class MinMax(NamedTuple):
    min: Vector
    max: Vector

    @property
    def average(self) -> Vector:
        return (self.min + self.max) / 2

    @property
    def size(self) -> Vector:
        return self.max - self.min

    @staticmethod
    def update_obj(obj: Object) -> None:
        if obj.mode != "OBJECT":
            obj.mode = "OBJECT"
            obj.update_from_editmode()

    @staticmethod
    def from_iterable(verts: Iterable[Iterable[float]]):
        min_v = make_vec3(float_info.max)
        max_v = make_vec3(-float_info.max)
        for pos in verts:
            for i in range(3):
                min_v[i] = min(min_v[i], pos[i])
                max_v[i] = max(max_v[i], pos[i])
        return MinMax(min_v, max_v)

    @classmethod
    def from_obj_bb(cls, obj: Object):
        cls.update_obj(obj)
        return MinMax.from_iterable(obj.bound_box)


def is_close(*args) -> bool:
    base = args[0]
    for a in args[1:]:
        if not m_isclose(base, a, rel_tol=1e-6):
            return False
    return True


def is_uniform(vec: Vector) -> bool:
    return is_close(*vec)


def calc_from_to_rotation(from_vec: Vector, to_vec: Vector) -> Quaternion:
    dot = from_vec.dot(to_vec)
    # If the vector is pointing in almost the opposite direction
    if dot < -1 + 1e-10:
        # Choose an appropriate vector perpendicular to from vec and use the axis of rotation.
        THRESHOLD = 0.9
        ortho_vec = Vector((1, 0, 0)) if abs(from_vec.x) < THRESHOLD else Vector((0, 1, 0))
        axis = from_vec.cross(ortho_vec).normalized()
        return Quaternion(axis, math.pi)  # π (180度) 回転

    axis = from_vec.cross(to_vec)
    if math.isclose(axis.length, 0):
        # Already in the same direction
        return Quaternion()

    angle = Vector(from_vec).angle(to_vec)
    return Quaternion(axis, angle)
