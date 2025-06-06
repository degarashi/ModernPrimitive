from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

CAPSULE_GIZMO_POS = {
    P.DivisionCircle: 0,
    P.DivisionCap: 1,
    P.DivisionSide: 2,
    P.Height: 3,
    P.Radius: 4,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Capsule.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    div_cap = out[P.DivisionCap.name]
    div_side = out[P.DivisionSide.name]
    height = out[P.Height.name]
    radius = out[P.Radius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CAPSULE_GIZMO_POS[p]].position

    d.draw_text_at(
        d.color.primary,
        gz(P.DivisionCircle),
        d.div_text(div_circle),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(d.color.x, gz(P.Radius), None, Vector((1, 0, 0)), d.unit_dist(radius))
    d.draw_text_at(
        d.color.x,
        gz(P.DivisionSide),
        d.div_text(div_side),
    )
    d.draw_text_at(
        d.color.y,
        gz(P.DivisionCap) + Vector((1, 0, 1)).normalized() * radius,
        d.div_text(div_cap),
    )
