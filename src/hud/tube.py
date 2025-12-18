from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..gizmo_info import GizmoInfo, GizmoInfoAr
from ..util.aux_node import get_interface_values
from .drawer import Drawer

TUBE_GIZMO_INDEX = {
    P.DivisionCircle: 0,
    P.Height: 1,
    P.DivisionSide: 2,
    P.OuterRadius: 3,
    P.InnerRadius: 4,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr, is_snap_capable: bool) -> None:
    # If the required shape is not maintained due to vertices being merged, etc.
    # exit without drawing anything
    if len(gizmo_info) < len(TUBE_GIZMO_INDEX):
        return

    TUBE = PR.Primitive_Tube
    out = get_interface_values(mod, TUBE.get_param_names())

    snap_flag: list[bool]
    try:
        snap_flag = get_interface_values(mod, TUBE.get_snap_param_names())
    except KeyError:
        snap_flag = TUBE.get_empty_snap_params()

    def gz(p: P.Prop) -> GizmoInfo:
        return gizmo_info[TUBE_GIZMO_INDEX[p]]

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
        div_text(P.DivisionCircle, P.SnapCircleDivision),
        Vector((0, 0, 1)),
        unit_text(P.Height, P.SnapHeight),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.InnerRadius).position,
        None,
        Vector((1, 1, 0)).normalized(),
        unit_text(P.InnerRadius, P.SnapInnerRadius),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.OuterRadius).position,
        None,
        Vector((1, 0, 0)),
        unit_text(P.OuterRadius, P.SnapOuterRadius),
    )
    d.draw_text_at(
        d.color.secondary,
        gz(P.DivisionSide).position,
        div_text(P.DivisionSide, P.SnapSideDivision),
    )
