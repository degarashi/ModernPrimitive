from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..gizmo_info import GizmoInfo, GizmoInfoAr
from ..util.aux_node import get_interface_values
from .drawer import Drawer

# Mapping of properties to gizmo positions
SPHERE_GIZMO_INDEX = {
    P.Radius: 0,
    P.Subdivision: 1,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr, is_snap_capable: bool) -> None:
    # If the required shape is not maintained due to vertices being merged, etc.
    # exit without drawing anything
    if len(gizmo_info) < len(SPHERE_GIZMO_INDEX):
        return

    # Retrieve interface values from modifier
    ICO = PR.Primitive_ICOSphere
    out = get_interface_values(mod, ICO.get_param_names())

    snap_flag: list[bool]
    try:
        snap_flag = get_interface_values(mod, ICO.get_snap_param_names())
    except KeyError:
        snap_flag = ICO.get_empty_snap_params()

    subd = out[P.Subdivision.name]  # Subdivision value

    # Function to get gizmo position for a property
    def gz(p: P.Prop) -> GizmoInfo:
        return gizmo_info[SPHERE_GIZMO_INDEX[p]]

    def unit_text(prop: P.Prop, prop_snap: P.Prop) -> str:
        return d.format_unit_or_adjusted_dist(
            out[prop.name],
            gz(prop).actual_value,
            is_snap_capable and snap_flag[prop_snap.name],
        )

    # --------------------------- draw texts ---------------------------
    # Draw radius text at gizmo position
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius).position,
        None,
        Vector((1, 0, 0)),
        unit_text(P.Radius, P.SnapRadius),
    )
    # Draw subdivision text at gizmo position
    d.draw_text_at_2(
        d.color.x,
        gz(P.Subdivision).position,
        None,
        Vector((1, 0, 1)).normalized() * 1.4,
        d.div_text(subd),
    )
