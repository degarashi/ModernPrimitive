from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..gizmo_info import GizmoInfo, GizmoInfoAr
from ..util.aux_node import get_interface_values
from .drawer import Drawer

GRID_GIZMO_INDEX = {
    P.SizeX: 0,
    P.SizeY: 1,
    P.GlobalDivision: 2,
    P.DivisionX: 3,
    P.DivisionY: 4,
}
# Minimum vertices for HUD display
CAN_SHOW_HUD_VERTEX = 3
# Minimum vertices for division value display
CAN_SHOW_DIVISION_VERTEX = 5


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr, is_snap_capable: bool) -> None:
    # If the required shape is not maintained due to vertices being merged, etc.
    # exit without drawing anything
    if len(gizmo_info) < CAN_SHOW_HUD_VERTEX:
        return

    show_actual_division = len(gizmo_info) >= CAN_SHOW_DIVISION_VERTEX

    # Interface values retrieval
    GRID = PR.Primitive_Grid
    out = get_interface_values(mod, GRID.get_param_names())

    snap_flag: list[bool]
    try:
        snap_flag = get_interface_values(mod, GRID.get_snap_param_names())
    except KeyError:
        snap_flag = GRID.get_empty_snap_params()

    div_x = out[P.DivisionX.name]
    div_y = out[P.DivisionY.name]
    div_g = out[P.GlobalDivision.name]

    # Gizmo accessor
    def gz(prop: P.Prop) -> GizmoInfo:
        return gizmo_info[GRID_GIZMO_INDEX[prop]]

    # Unit text formatting
    def unit_text(prop: P.Prop, prop_snap: P.Prop) -> str:
        return d.format_unit_or_adjusted_dist(
            out[prop.name],
            gz(prop).actual_value,
            is_snap_capable and snap_flag[prop_snap.name],
        )

    # --------------------------- draw texts ---------------------------
    # Draw X axis text
    d.draw_text_at_2(
        d.color.x,
        gz(P.SizeX).position,
        d.format_div_or_adjusted(
            div_x,
            int(gz(P.DivisionX).actual_value) if show_actual_division else "1",
            is_snap_capable and snap_flag[P.SnapDivision.name],
        ),
        Vector((1, 0, 0)),
        unit_text(P.SizeX, P.SnapSize),
    )
    # Draw Y axis text
    d.draw_text_at_2(
        d.color.y,
        gz(P.SizeY).position,
        d.format_div_or_adjusted(
            div_y,
            int(gz(P.DivisionY).actual_value) if show_actual_division else "1",
            is_snap_capable and snap_flag[P.SnapDivision.name],
        ),
        Vector((0, 1, 0)),
        unit_text(P.SizeY, P.SnapSize),
    )
    # Draw global division text
    d.draw_text_at(
        d.color.z,
        gz(P.GlobalDivision).position,
        d.div_text(div_g),
    )
