from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer
from .icosphere import SPHERE_GIZMO_POS


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_QuadSphere.get_param_names())
    subd = out[P.Subdivision.name]
    radius = out[P.Radius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[SPHERE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.Subdivision),
        None,
        Vector((1, 0, 1)),
        d.div_text(subd),
    )
