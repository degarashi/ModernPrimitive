from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer, ZERO

GEAR_GIZMO_INDEX = {
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


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr, is_snap_capable: bool) -> None:
    # If the required shape is not maintained due to vertices being merged, etc.
    # exit without drawing anything
    if len(gizmo_info) < len(GEAR_GIZMO_INDEX):
        return

    GEAR = PR.Primitive_Gear

    out = get_interface_values(mod, GEAR.get_param_names())

    snap_flag: list[bool]
    try:
        snap_flag = get_interface_values(mod, GEAR.get_snap_param_names())
    except KeyError:
        snap_flag = GEAR.get_empty_snap_params()

    outer_radius = out[P.OuterRadius.name]
    twist = out[P.Twist.name]
    fillet_radius = out[P.FilletRadius.name]

    def gz(p: P.Prop):
        return gizmo_info[GEAR_GIZMO_INDEX[p]]

    def div_text(prop: P.Prop, prop_snap: P.Prop) -> str:
        return d.format_div_or_adjusted(
            int(out[prop.name]),
            int(gz(prop).actual_value),
            is_snap_capable and snap_flag[prop_snap.name],
        )

    def unit_text(prop: P.Prop, prop_snap: P.Prop) -> str:
        return d.format_unit_or_adjusted_dist(
            out[prop.name],
            gz(prop).actual_value,
            is_snap_capable and snap_flag[prop_snap.name],
        )

    # --------------------------- draw texts ---------------------------
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height).position,
        None,
        Vector((0, 0, 1)),
        unit_text(P.Height, P.SnapHeight),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.InnerCircleRadius).position,
        div_text(P.InnerCircleDivision, P.SnapInnerCircleDivision),
        Vector((1, -1, 0)).normalized(),
        unit_text(P.InnerCircleRadius, P.SnapInnerCircleRadius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.OuterRadius).position,
        None,
        Vector((1, 0, 0)),
        unit_text(P.OuterRadius, P.SnapOuterRadius),
    )
    d.draw_text_at(
        d.color.primary,
        Vector((0, -outer_radius, 0)) + gz(P.NumBlades).position,
        div_text(P.NumBlades, P.SnapNumBlades),
    )
    d.draw_text_at(
        d.color.y,
        gz(P.FilletRadius).position + Vector((0, -outer_radius * 1.25, 0)),
        f"{fillet_radius:.2f}",
    )
    d.draw_text_at(
        d.color.z,
        gz(P.FilletCount).position + Vector((0, -outer_radius * 1.25 * 1.3, 0)),
        div_text(P.FilletCount, P.SnapFilletCount),
    )
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.InnerRadius).position,
        None,
        Vector((1, 1, 0)).normalized(),
        unit_text(P.InnerRadius, P.SnapInnerRadius),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.Twist).position,
        None,
        Vector((0, 1, 0)),
        f"{twist:.2f}",
        ZERO,
        Vector((0.5, 2.0)),
    )
