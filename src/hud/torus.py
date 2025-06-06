from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

TORUS_GIZMO_POS = {
    P.Radius: 0,
    P.RingRadius: 1,
    P.DivisionRing: 2,
    P.DivisionCircle: 3,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Torus.get_param_names())
    radius = out[P.Radius.name]
    ring_radius = out[P.RingRadius.name]
    div_ring = out[P.DivisionRing.name]
    div_circle = out[P.DivisionCircle.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[TORUS_GIZMO_POS[p]].position

    d.draw_text_at(d.color.primary, gz(P.DivisionCircle), d.div_text(div_circle))
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.RingRadius),
        d.div_text(div_ring),
        Vector((0, 0, 1)),
        d.unit_dist(ring_radius),
        Vector((2, 0.5)),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
