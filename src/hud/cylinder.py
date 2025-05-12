from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

CYLINDER_GIZMO_POS = {
    P.Radius: 0,
    P.Height: 1,
    P.DivisionCircle: 2,
    P.DivisionSide: 3,
    P.DivisionFill: 4,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Cylinder.get_param_names())
    radius = out[P.Radius.name]
    height = out[P.Height.name]
    div_circle = out[P.DivisionCircle.name]
    div_side = out[P.DivisionSide.name]
    div_fill = out[P.DivisionFill.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CYLINDER_GIZMO_POS[p]].position

    d.draw_text_at(
        d.color.x,
        gz(P.DivisionSide),
        d.div_text(div_side),
    )

    d.draw_text_at(
        d.color.y,
        Vector((1, 1, 0)).normalized() * radius + gz(P.DivisionCircle),
        d.div_text(div_circle),
    )
    d.draw_text_at(
        d.color.primary,
        Vector((1, 1, 0)).normalized() * radius * 0.7 + gz(P.DivisionFill),
        d.div_text(div_fill),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
