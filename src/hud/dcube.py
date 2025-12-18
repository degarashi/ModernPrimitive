from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

DCUBE_GIZMO_INDEX = {
    P.MinX: 0,
    P.MaxX: 1,
    P.MinY: 2,
    P.MaxY: 3,
    P.MinZ: 4,
    P.MaxZ: 5,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr, is_snap_capable: bool) -> None:
    # If the required shape is not maintained due to vertices being merged, etc.
    # exit without drawing anything
    if len(gizmo_info) < len(DCUBE_GIZMO_INDEX):
        return

    DCUBE = PR.Primitive_DeformableCube
    out = get_interface_values(mod, DCUBE.get_param_names())

    snap_flag: list[bool]
    try:
        snap_flag = get_interface_values(mod, DCUBE.get_snap_param_names())
    except KeyError:
        snap_flag = DCUBE.get_empty_snap_params()

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[DCUBE_GIZMO_INDEX[p]]

    def unit_text(prop: P.Prop, prop_snap: P.Prop) -> str:
        return d.format_unit_or_adjusted_dist(
            out[prop.name],
            gz(prop).actual_value,
            is_snap_capable and snap_flag[prop_snap.name],
        )

    # --------------------------- draw texts ---------------------------
    d.draw_text_at_2(
        d.color.x,
        gz(P.MinX).position,
        None,
        Vector((-1, 0, 0)),
        unit_text(P.MinX, P.SnapSize),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.MaxX).position,
        None,
        Vector((1, 0, 0)),
        unit_text(P.MaxX, P.SnapSize),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.MinY).position,
        None,
        Vector((0, -1, 0)),
        unit_text(P.MinY, P.SnapSize),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.MaxY).position,
        None,
        Vector((0, 1, 0)),
        unit_text(P.MaxY, P.SnapSize),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.MinZ).position,
        None,
        Vector((0, 0, -1)),
        unit_text(P.MinZ, P.SnapSize),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.MaxZ).position,
        None,
        Vector((0, 0, 1)),
        unit_text(P.MaxZ, P.SnapSize),
    )
