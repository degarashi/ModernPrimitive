from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

CONE_GIZMO_POS = {
    P.DivisionSide: 0,
    P.DivisionFill: 1,
    P.DivisionCircle: 2,
    P.TopRadius: 3,
    P.BottomRadius: 4,
    P.Height: 5,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Cone.get_param_names())
    div_side = out[P.DivisionSide.name]
    div_fill = out[P.DivisionFill.name]
    div_circle = out[P.DivisionCircle.name]
    top_radius = out[P.TopRadius.name]
    bottom_radius = out[P.BottomRadius.name]
    height = out[P.Height.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CONE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.z,
        gz(P.Height),
        d.div_text(div_fill),
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.TopRadius),
        d.div_text(div_circle),
        Vector((1, 0, 0)),
        d.unit_dist(top_radius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.BottomRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(bottom_radius),
    )
    d.draw_text_at(
        d.color.secondary,
        gz(P.DivisionSide),
        d.div_text(div_side),
    )
