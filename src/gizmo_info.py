from typing import NamedTuple, TypeAlias, Any, TypeVar
from collections.abc import Callable
from mathutils import Vector
from bpy.types import Mesh
from .exception import DGException


class GizmoInfo(NamedTuple):
    position: Vector
    normal: Vector
    type: int


T = TypeVar("T")
GizmoInfoAr: TypeAlias = list[GizmoInfo]


class DGGizmoInfoCantLoaded(DGException):
    pass


def get_gizmo_info(mesh: Mesh) -> GizmoInfoAr | None:
    MAX_ATTRIBUTES = 20
    try:

        def load(name: str, reader: Callable) -> list[Any]:
            ret: list[T] = []
            # If the required information is not provided, return None
            attr = mesh.attributes[name]
            if attr.domain != "POINT":
                return None

            for i, data in enumerate(attr.data):
                ret.append(reader(data))
                if i == MAX_ATTRIBUTES - 1:
                    break
            return ret

        giz_pos = load("Gizmo Position", lambda x: x.vector.copy())
        giz_type = load("Gizmo Type", lambda x: x.value)
        giz_normal = load("Gizmo Normal", lambda x: x.vector.copy())

        if len(giz_pos) == len(giz_type) == len(giz_normal):
            ret: GizmoInfoAr = []
            for i in range(len(giz_pos)):
                ret.append(GizmoInfo(giz_pos[i], giz_normal[i], giz_type[i]))
            return ret
        raise DGGizmoInfoCantLoaded("invalid length")  # noqa: TRY003
    except KeyError as e:
        print(e)
        raise DGGizmoInfoCantLoaded("no key") from e  # noqa: TRY003
    raise DGGizmoInfoCantLoaded("unknown error")  # noqa: TRY003
