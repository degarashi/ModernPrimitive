from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

SPRING_GIZMO_POS = {
    P.DivisionCircle: 0,
    P.Rotations: 1,
    P.BottomRadius: 2,
    P.TopRadius: 3,
    P.Height: 4,
    P.DivisionRing: 5,
    P.RingRadius: 6,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Spring.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    rotations = out[P.Rotations.name]
    bottom_radius = out[P.BottomRadius.name]
    top_radius = out[P.TopRadius.name]
    height = out[P.Height.name]
    div_ring = out[P.DivisionRing.name]
    ring_radius = out[P.RingRadius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[SPRING_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.BottomRadius),
        d.div_text(div_circle),
        Vector((0, 1, 0)),
        d.unit_dist(bottom_radius),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.RingRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(ring_radius),
    )
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.TopRadius),
        f"{rotations:.2f}",
        Vector((0, 1, 0)),
        d.unit_dist(top_radius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at(d.color.y, gz(P.DivisionRing), d.div_text(div_ring))
