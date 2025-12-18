from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..gizmo_info import GizmoInfo, GizmoInfoAr
from ..util.aux_node import get_interface_values
from .drawer import Drawer

CAPSULE_GIZMO_INDEX = {
    P.DivisionCircle: 0,
    P.DivisionCap: 1,
    P.DivisionSide: 2,
    P.Height: 3,
    P.Radius: 4,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr, is_snap_capable: bool) -> None:
    # If the required shape is not maintained due to vertices being merged, etc.
    # exit without drawing anything
    if len(gizmo_info) < len(CAPSULE_GIZMO_INDEX):
        return

    CAP = PR.Primitive_Capsule
    out = get_interface_values(mod, CAP.get_param_names())

    snap_flag: list[bool]
    try:
        snap_flag = get_interface_values(mod, CAP.get_snap_param_names())
    except KeyError:
        snap_flag = CAP.get_empty_snap_params()

    radius = out[P.Radius.name]

    def gz(p: P.Prop) -> GizmoInfo:
        return gizmo_info[CAPSULE_GIZMO_INDEX[p]]

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
    d.draw_text_at(
        d.color.primary,
        gz(P.DivisionCircle).position,
        div_text(P.DivisionCircle, P.SnapCircleDivision),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height).position,
        None,
        Vector((0, 0, 1)),
        unit_text(P.Height, P.SnapHeight),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.Radius).position,
        None,
        Vector((1, 0, 0)),
        unit_text(P.Radius, P.SnapRadius),
    )
    d.draw_text_at(
        d.color.x,
        gz(P.DivisionSide).position,
        div_text(P.DivisionSide, P.SnapSideDivision),
    )
    d.draw_text_at(
        d.color.y,
        gz(P.DivisionCap).position + Vector((1, 0, 1)).normalized() * radius,
        div_text(P.DivisionCap, P.SnapCapDivision),
    )
