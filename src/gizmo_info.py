from typing import NamedTuple, TypeAlias, Any, TypeVar
from collections.abc import Callable
from mathutils import Vector, Color
from bpy.types import Mesh
from .exception import DGException
from enum import Enum
from .color import HUDColor


class GizmoType(Enum):
    Linear = 0
    Dial = 1


class GizmoColor(Enum):
    Primary = 0
    Secondary = 1
    X = 2
    Y = 3
    Z = 4


class GizmoInfo(NamedTuple):
    position: Vector
    normal: Vector
    type: GizmoType
    color_type: GizmoColor

    def get_color(self, hud_color: HUDColor) -> Color:
        match self.color_type:
            case GizmoColor.Primary:
                return hud_color.primary
            case GizmoColor.Secondary:
                return hud_color.secondary
            case GizmoColor.X:
                return hud_color.x
            case GizmoColor.Y:
                return hud_color.y
            case GizmoColor.Z:
                return hud_color.z
        return hud_color.white


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

        def get_vec(x):
            return x.vector.copy()

        giz_pos = load("Gizmo Position", get_vec)
        giz_type = load("Gizmo Type", lambda x: GizmoType(x.value))
        giz_normal = load("Gizmo Normal", get_vec)
        giz_color = load("Gizmo Color", lambda x: GizmoColor(x.value))

        if len(giz_pos) == len(giz_type) == len(giz_normal):
            ret: GizmoInfoAr = []
            for i in range(len(giz_pos)):
                ret.append(GizmoInfo(giz_pos[i], giz_normal[i], giz_type[i], giz_color[i]))
            return ret
        raise DGGizmoInfoCantLoaded("invalid length")
    except KeyError as e:
        print(e)
        raise DGGizmoInfoCantLoaded("no key") from e
    raise DGGizmoInfoCantLoaded("unknown error")
