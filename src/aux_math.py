import math
from math import isclose as m_isclose
from mathutils import Vector, Quaternion


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
