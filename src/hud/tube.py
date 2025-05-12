from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

TUBE_GIZMO_POS = {
    P.DivisionCircle: 0,
    P.Height: 1,
    P.DivisionSide: 2,
    P.OuterRadius: 3,
    P.InnerRadius: 4,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Tube.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    height = out[P.Height.name]
    div_side = out[P.DivisionSide.name]
    outer_radius = out[P.OuterRadius.name]
    inner_radius = out[P.InnerRadius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[TUBE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        d.div_text(div_circle),
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.InnerRadius),
        None,
        Vector((1, 1, 0)).normalized(),
        d.unit_dist(inner_radius),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.OuterRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(outer_radius),
    )
    d.draw_text_at(d.color.secondary, gz(P.DivisionSide), d.div_text(div_side))
