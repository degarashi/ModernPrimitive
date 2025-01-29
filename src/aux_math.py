from math import isclose as m_isclose
from mathutils import Vector


def is_close(*args) -> bool:
    base = args[0]
    for a in args[1:]:
        if not m_isclose(base, a, rel_tol=1e-6):
            return False
    return True


def is_uniform(vec: Vector) -> bool:
    return is_close(*vec)
