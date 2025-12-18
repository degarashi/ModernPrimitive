from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

CUBE_GIZMO_INDEX = {
    P.SizeX: 0,
    P.SizeY: 1,
    P.SizeZ: 2,
    P.DivisionX: 3,
    P.DivisionY: 4,
    P.DivisionZ: 5,
    P.GlobalDivision: 6,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr, is_snap_capable: bool) -> None:
    # If the required shape is not maintained due to vertices being merged, etc.
    # exit without drawing anything
    if len(gizmo_info) < len(CUBE_GIZMO_INDEX):
        return

    CUBE = PR.Primitive_Cube
    out = get_interface_values(mod, CUBE.get_param_names())

    snap_flag: list[bool]
    try:
        snap_flag = get_interface_values(mod, CUBE.get_snap_param_names())
    except KeyError:
        snap_flag = CUBE.get_empty_snap_params()

    size = out[P.Size.name]
    div_x = out[P.DivisionX.name]
    div_y = out[P.DivisionY.name]
    div_z = out[P.DivisionZ.name]
    div_g = out[P.GlobalDivision.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CUBE_GIZMO_INDEX[p]]

    def div_text(val: int, prop: P.Prop, prop_snap: P.Prop) -> str:
        return d.format_div_or_adjusted(
            val, int(gz(prop).actual_value), is_snap_capable and snap_flag[prop_snap.name]
        )

    def unit_text(val: float, prop: P.Prop, prop_snap: P.Prop) -> str:
        return d.format_unit_or_adjusted_dist(
            val, gz(prop).actual_value, is_snap_capable and snap_flag[prop_snap.name]
        )

    # --------------------------- draw texts ---------------------------
    d.draw_text_at_2(
        d.color.x,
        gz(P.SizeX).position,
        div_text(div_x, P.DivisionX, P.SnapDivision),
        Vector((1, 0, 0)),
        unit_text(size[0], P.SizeX, P.SnapSize),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.SizeY).position,
        div_text(div_y, P.DivisionY, P.SnapDivision),
        Vector((0, 1, 0)),
        unit_text(size[1], P.SizeY, P.SnapSize),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.SizeZ).position,
        div_text(div_z, P.DivisionZ, P.SnapDivision),
        Vector((0, 0, 1)),
        unit_text(size[2], P.SizeZ, P.SnapSize),
    )
    d.draw_text_at(
        d.color.secondary,
        gz(P.GlobalDivision).position - Vector((size[0], size[1], 0)) / 4,
        f"{div_g:.2f}",
    )
