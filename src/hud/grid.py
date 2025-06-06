from bpy.types import Modifier
from mathutils import Vector

from .. import primitive as PR
from .. import primitive_prop as P
from ..util.aux_node import get_interface_values
from ..gizmo_info import GizmoInfoAr
from .drawer import Drawer

GRID_GIZMO_POS = {
    "X": 0,
    "Y": 1,
    "GDiv": 2,
}


def draw_hud(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Grid.get_param_names())
    size_x = out[P.SizeX.name]
    size_y = out[P.SizeY.name]
    div_x = out[P.DivisionX.name]
    div_y = out[P.DivisionY.name]
    div_g = out[P.GlobalDivision.name]

    def gz(p: str) -> Vector:
        return gizmo_info[GRID_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.x,
        gz("X"),
        d.div_text(div_x),
        Vector((1, 0, 0)),
        d.unit_dist(size_x),
    )
    d.draw_text_at_2(
        d.color.y,
        gz("Y"),
        d.div_text(div_y),
        Vector((0, 1, 0)),
        d.unit_dist(size_y),
    )
    d.draw_text_at(d.color.z, gz("GDiv"), d.div_text(div_g))
