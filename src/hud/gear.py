from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

GEAR_GIZMO_POS = {
    P.NumBlades: 0,
    P.InnerRadius: 1,
    P.OuterRadius: 2,
    P.Twist: 3,
    P.InnerCircleDivision: 4,
    P.InnerCircleRadius: 5,
    P.FilletCount: 6,
    P.FilletRadius: 7,
    P.Height: 8,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Gear.get_param_names())
    num_blades = out[P.NumBlades.name]
    inner_radius = out[P.InnerRadius.name]
    outer_radius = out[P.OuterRadius.name]
    twist = out[P.Twist.name]
    ic_division = out[P.InnerCircleDivision.name]
    ic_radius = out[P.InnerCircleRadius.name]
    fillet_count = out[P.FilletCount.name]
    fillet_radius = out[P.FilletRadius.name]
    height = out[P.Height.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[GEAR_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.InnerCircleRadius),
        d.div_text(ic_division),
        Vector((1, -1, 0)).normalized(),
        d.unit_dist(ic_radius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.OuterRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(outer_radius),
    )
    d.draw_text_at(
        d.color.primary,
        Vector((0, -outer_radius, 0)) + gz(P.NumBlades),
        d.div_text(num_blades),
    )
    d.draw_text_at(
        d.color.y,
        gz(P.FilletRadius) + Vector((0, -outer_radius * 1.25, 0)),
        f"{fillet_radius:.2f}",
    )
    d.draw_text_at(
        d.color.z,
        gz(P.FilletCount) + Vector((0, -outer_radius * 1.25 * 1.3, 0)),
        d.div_text(fillet_count),
    )
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.InnerRadius),
        None,
        Vector((1, 1, 0)).normalized(),
        d.unit_dist(inner_radius),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.Twist),
        None,
        Vector((0, 1, 0)),
        f"{twist:.2f}",
        ZERO,
        Vector((0.5, 2.0)),
    )
