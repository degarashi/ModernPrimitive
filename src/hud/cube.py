from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

CUBE_GIZMO_POS = {
    P.SizeX: 0,
    P.SizeY: 1,
    P.SizeZ: 2,
    P.DivisionX: 3,
    P.DivisionY: 4,
    P.DivisionZ: 5,
    P.GlobalDivision: 6,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Cube.get_param_names())
    size = out[P.Size.name]
    div_x = out[P.DivisionX.name]
    div_y = out[P.DivisionY.name]
    div_z = out[P.DivisionZ.name]
    div_g = out[P.GlobalDivision.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CUBE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.x,
        gz(P.SizeX),
        d.div_text(div_x),
        Vector((1, 0, 0)),
        d.unit_dist(size[0]),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.SizeY),
        d.div_text(div_y),
        Vector((0, 1, 0)),
        d.unit_dist(size[1]),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.SizeZ),
        d.div_text(div_z),
        Vector((0, 0, 1)),
        d.unit_dist(size[2]),
    )
    d.draw_text_at(
        d.color.secondary,
        gz(P.GlobalDivision) - Vector((size[0], size[1], 0)) / 4,
        f"{div_g:.2f}",
    )
