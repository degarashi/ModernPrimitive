from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

DCUBE_GIZMO_POS = {
    P.MinX: 0,
    P.MaxX: 1,
    P.MinY: 2,
    P.MaxY: 3,
    P.MinZ: 4,
    P.MaxZ: 5,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_DeformableCube.get_param_names())
    min_x = out[P.MinX.name]
    max_x = out[P.MaxX.name]
    min_y = out[P.MinY.name]
    max_y = out[P.MaxY.name]
    min_z = out[P.MinZ.name]
    max_z = out[P.MaxZ.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[DCUBE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.x,
        gz(P.MinX),
        None,
        Vector((-1, 0, 0)),
        d.unit_dist(min_x),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.MaxX),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(max_x),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.MinY),
        None,
        Vector((0, -1, 0)),
        d.unit_dist(min_y),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.MaxY),
        None,
        Vector((0, 1, 0)),
        d.unit_dist(max_y),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.MinZ),
        None,
        Vector((0, 0, -1)),
        d.unit_dist(min_z),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.MaxZ),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(max_z),
    )
