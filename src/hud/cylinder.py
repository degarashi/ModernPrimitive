from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

CYLINDER_GIZMO_INDEX = {
    P.Radius: 0,
    P.Height: 1,
    P.DivisionCircle: 2,
    P.DivisionSide: 3,
    P.DivisionFill: 4,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr, is_snap_capable: bool) -> None:
    # If the required shape is not maintained due to vertices being merged, etc.
    # exit without drawing anything
    if len(gizmo_info) < len(CYLINDER_GIZMO_INDEX):
        return

    CYL = PR.Primitive_Cylinder
    out = get_interface_values(mod, CYL.get_param_names())

    snap_flag: list[bool]
    try:
        snap_flag = get_interface_values(mod, CYL.get_snap_param_names())
    except KeyError:
        snap_flag = CYL.get_empty_snap_params()

    radius = out[P.Radius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CYLINDER_GIZMO_INDEX[p]]

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
        d.color.x,
        gz(P.DivisionSide).position,
        div_text(P.DivisionSide, P.SnapSideDivision),
    )

    d.draw_text_at(
        d.color.y,
        Vector((1, 1, 0)).normalized() * radius + gz(P.DivisionCircle).position,
        div_text(P.DivisionCircle, P.SnapCircleDivision),
    )
    d.draw_text_at(
        d.color.primary,
        Vector((1, 1, 0)).normalized() * radius * 0.7 + gz(P.DivisionFill).position,
        div_text(P.DivisionFill, P.SnapFillDivision),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius).position,
        None,
        Vector((1, 0, 0)),
        unit_text(P.Radius, P.SnapRadius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height).position,
        None,
        Vector((0, 0, 1)),
        unit_text(P.Height, P.SnapHeight),
    )
