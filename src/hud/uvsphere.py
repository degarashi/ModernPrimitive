from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

UV_SPHERE_GIZMO_POS = {
    P.Radius: 0,
    P.DivisionRing: 1,
    P.DivisionCircle: 2,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_UVSphere.get_param_names())
    radius = out[P.Radius.name]
    div_ring = out[P.DivisionRing.name]
    div_circle = out[P.DivisionCircle.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[UV_SPHERE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        d.div_text(div_circle),
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at(
        d.color.secondary,
        gz(P.DivisionCircle) + Vector((0, 0, radius)),
        d.div_text(div_ring),
    )
