import math
import sys
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

    def __str__(self) -> str:
        return f"MinMax(min={self.min}, max={self.max})"


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


class AABB:
    min_v: Vector
    max_v: Vector

    def __init__(self, minv: Vector, maxv: Vector):
        self.min_v = minv
        self.max_v = maxv

    def __getitem__(self, index: int) -> Vector:
        return (self.min_v, self.max_v)[index]


def calc_aabb(vecs: Iterable[Vector]) -> AABB:
    L = sys.float_info.max
    min_v = Vector((L, L, L))
    max_v = Vector((-L, -L, -L))
    for pt in vecs:
        pt2 = Vector(pt)
        for i in range(3):
            min_v[i] = min(min_v[i], pt2[i])
            max_v[i] = max(max_v[i], pt2[i])

    return AABB(min_v, max_v)


class BBox:
    min: Vector
    max: Vector
    size: Vector
    center: Vector

    def __init__(self, vert: Iterable[Vector]):
        (self.min, self.max) = calc_aabb(vert)
        self.size = self.max - self.min
        self.center = (self.min + self.max) / 2

    def __str__(self) -> str:
        return f"BBox(min={self.min}, max={self.max},\
size={self.size}, center={self.center})"


def calc_sizediff(s0: Vector, s1: Vector) -> float:
    return sum(abs(p[0] - p[1]) for p in zip(s0, s1, strict=False))
