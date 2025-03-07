from collections.abc import Iterable
from typing import Any, TypeVar, cast

import blf
import bpy
from bpy.props import BoolProperty
from bpy.types import Context, Modifier, Object, Operator, PreferencesView, SpaceView3D
from bpy.utils import register_class, unregister_class
from mathutils import Color, Matrix, Vector

from . import primitive as PR
from . import primitive_prop as P
from .aux_func import (
    get_addon_preferences,
    get_evaluated_mesh,
    is_modern_primitive,
    type_from_modifier_name,
)
from .aux_node import get_interface_values
from .color import HUDColor
from .constants import MODERN_PRIMITIVE_PREFIX, Type
from .draw_aux import DEFAULT_FONT_ID as FONT_ID
from .draw_aux import set_color, set_position_draw
from .exception import DGUnknownType
from .gizmo_info import GizmoInfoAr, get_gizmo_info

units = bpy.utils.units


def perspec(mat: Matrix, pos: Vector) -> Vector:
    pos = mat @ pos
    pos.x /= pos.w
    pos.y /= pos.w
    pos.z = pos.w
    return pos.xyz


def to_win(window_size: Iterable[int], sc_pos: Vector) -> Vector:
    return Vector(
        (
            (sc_pos.x / 2 + 0.5) * window_size[0],
            (sc_pos.y / 2 + 0.5) * window_size[1],
        )
    )


ONE = Vector((1, 1))
ZERO = Vector((0, 0))
HALF_ONE = ONE / 2


class Drawer:
    color: HUDColor
    __blf: Any
    __pref: PreferencesView
    __window_size: tuple[int, int]
    __m_pers: Matrix
    __m_window: Matrix
    __system: str
    __dim: Vector

    def __init__(self, blf: Any, context: Context, m_world: Matrix):
        reg = context.region
        reg3d = context.region_data

        self.color = HUDColor(context.preferences)
        self.__blf = blf
        self.__pref = context.preferences.view
        self.__window_size = (reg.width, reg.height)
        self.__m_pers = reg3d.perspective_matrix @ m_world
        self.__m_window = reg3d.window_matrix
        self.__system = context.scene.unit_settings.system

    def __enter__(self):
        scale = self.__pref.ui_scale
        blf = self.__blf
        blf.enable(FONT_ID, blf.SHADOW)
        blf.shadow_offset(FONT_ID, 1, -1)
        blf.size(FONT_ID, 15 * scale)
        set_color(blf, HUDColor.WHITE)
        self.__dim = Vector(blf.dimensions(FONT_ID, "A"))
        self.__dim.y += 4

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.__blf.disable(FONT_ID, blf.SHADOW)

    def gizmo_depend_worldpos(
        self,
        orig_pos: Vector,
        dir_v: Vector,
    ) -> Vector:
        # Origin position
        ori_p = perspec(self.__m_pers, orig_pos.to_4d())

        view_ori = Vector((0, 0, 1, 1))
        p_ori = perspec(self.__m_window, view_ori)
        win_ori = to_win(self.__window_size, p_ori)
        view_diff = Vector((1, 0, 1, 1))
        p_diff = perspec(self.__m_window, view_diff)
        win_diff = to_win(self.__window_size, p_diff)
        ratio = abs(win_diff.x - win_ori.x)
        ratio *= 0.008

        # z-distance at the center of Gizmo
        gizmo_dist = ori_p.z

        AXIS_LEN = 4.0
        ui_ratio = self.__pref.gizmo_size / 100.0 * self.__pref.ui_scale
        move_dist = AXIS_LEN * gizmo_dist / 6 / ratio * ui_ratio
        return dir_v * move_dist + orig_pos

    def draw_text_at(
        self,
        color: Color,
        ori_pos: Vector,
        msg: str,
        label_offset_r: Vector = HALF_ONE,
    ) -> None:
        set_color(self.__blf, color)
        ori_w = to_win(self.__window_size, perspec(self.__m_pers, ori_pos.to_4d()))
        set_position_draw(self.__blf, ori_w + self.__dim * label_offset_r, msg)

    def draw_text_at_2(
        self,
        color: Color,
        ori_pos: Vector,
        msg0: str | None,
        lc_dir: Vector,
        msg1: str,
        label_offset0_r: Vector = HALF_ONE,
        label_offset1_r: Vector = HALF_ONE,
    ) -> None:
        if msg0 is not None:
            self.draw_text_at(color, ori_pos, msg0, label_offset0_r)

        set_color(self.__blf, color)
        target_pos = self.gizmo_depend_worldpos(ori_pos, lc_dir)
        set_position_draw(
            self.__blf,
            to_win(self.__window_size, perspec(self.__m_pers, target_pos.to_4d()))
            + self.__dim * label_offset1_r,
            msg1,
        )

    def div_text(self, val: int) -> str:
        return f"[{val}]"

    def unit_dist(self, val: float, prec: int = 3) -> str:
        return units.to_string(
            self.__system,
            units.categories.LENGTH,
            val,
            precision=prec,
        )

    def show_hud(self, scale: Vector) -> None:
        set_position_draw(blf, (50, 30), "ModernPrimitive:")
        set_position_draw(blf, (60, 10), f"Scale: {scale.x:.2f} {scale.y:.2f} {scale.z:.2f}")


def make_drawer(blf: Any, context: Context, m_world: Matrix) -> Drawer:
    drawer = Drawer(blf, context, m_world)
    return drawer.__enter__()


CUBE_GIZMO_POS = {
    P.SizeX: 0,
    P.SizeY: 1,
    P.SizeZ: 2,
    P.DivisionX: 3,
    P.DivisionY: 4,
    P.DivisionZ: 5,
    P.GlobalDivision: 6,
}


def proc_cube(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
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


CONE_GIZMO_POS = {
    P.DivisionSide: 0,
    P.DivisionFill: 1,
    P.DivisionCircle: 2,
    P.TopRadius: 3,
    P.BottomRadius: 4,
    P.Height: 5,
}


def proc_cone(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Cone.get_param_names())
    div_side = out[P.DivisionSide.name]
    div_fill = out[P.DivisionFill.name]
    div_circle = out[P.DivisionCircle.name]
    top_radius = out[P.TopRadius.name]
    bottom_radius = out[P.BottomRadius.name]
    height = out[P.Height.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CONE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.z,
        gz(P.Height),
        d.div_text(div_fill),
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.TopRadius),
        d.div_text(div_circle),
        Vector((1, 0, 0)),
        d.unit_dist(top_radius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.BottomRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(bottom_radius),
    )
    d.draw_text_at(
        d.color.secondary,
        gz(P.DivisionSide),
        d.div_text(div_side),
    )


CYLINDER_GIZMO_POS = {
    P.Radius: 0,
    P.Height: 1,
    P.DivisionCircle: 2,
    P.DivisionSide: 3,
    P.DivisionFill: 4,
}


def proc_cylinder(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Cylinder.get_param_names())
    radius = out[P.Radius.name]
    height = out[P.Height.name]
    div_circle = out[P.DivisionCircle.name]
    div_side = out[P.DivisionSide.name]
    div_fill = out[P.DivisionFill.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CYLINDER_GIZMO_POS[p]].position

    d.draw_text_at(
        d.color.x,
        gz(P.DivisionSide),
        d.div_text(div_side),
    )

    d.draw_text_at(
        d.color.y,
        Vector((1, 1, 0)).normalized() * radius + gz(P.DivisionCircle),
        d.div_text(div_circle),
    )
    d.draw_text_at(
        d.color.primary,
        Vector((1, 1, 0)).normalized() * radius * 0.7 + gz(P.DivisionFill),
        d.div_text(div_fill),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )


GRID_GIZMO_POS = {
    "X": 0,
    "Y": 1,
    "GDiv": 2,
}


def proc_grid(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
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


SPHERE_GIZMO_POS = {
    P.Radius: 0,
    P.Subdivision: 1,
}


def proc_icosphere(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_ICOSphere.get_param_names())
    radius = out[P.Radius.name]
    subd = out[P.Subdivision.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[SPHERE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.Subdivision),
        None,
        Vector((1, 0, 1)).normalized() * 1.4,
        d.div_text(subd),
    )


TORUS_GIZMO_POS = {
    P.Radius: 0,
    P.RingRadius: 1,
    P.DivisionRing: 2,
    P.DivisionCircle: 3,
}


def proc_torus(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Torus.get_param_names())
    radius = out[P.Radius.name]
    ring_radius = out[P.RingRadius.name]
    div_ring = out[P.DivisionRing.name]
    div_circle = out[P.DivisionCircle.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[TORUS_GIZMO_POS[p]].position

    d.draw_text_at(d.color.primary, gz(P.DivisionCircle), d.div_text(div_circle))
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.RingRadius),
        d.div_text(div_ring),
        Vector((0, 0, 1)),
        d.unit_dist(ring_radius),
        Vector((2, 0.5)),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )


UV_SPHERE_GIZMO_POS = {
    P.Radius: 0,
    P.DivisionRing: 1,
    P.DivisionCircle: 2,
}


def proc_uvsphere(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_UVSphere.get_param_names())
    radius = out[P.Radius.name]
    div_ring = out[P.DivisionRing.name]
    div_circle = out[P.DivisionCircle.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[UV_SPHERE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        d.div_text(div_circle),
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at(
        d.color.secondary,
        gz(P.DivisionCircle) + Vector((0, 0, radius)),
        d.div_text(div_ring),
    )


TUBE_GIZMO_POS = {
    P.DivisionCircle: 0,
    P.Height: 1,
    P.DivisionSide: 2,
    P.OuterRadius: 3,
    P.InnerRadius: 4,
}


def proc_tube(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Tube.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    height = out[P.Height.name]
    div_side = out[P.DivisionSide.name]
    outer_radius = out[P.OuterRadius.name]
    inner_radius = out[P.InnerRadius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[TUBE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        d.div_text(div_circle),
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color.y,
        gz(P.InnerRadius),
        None,
        Vector((1, 1, 0)).normalized(),
        d.unit_dist(inner_radius),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.OuterRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(outer_radius),
    )
    d.draw_text_at(d.color.secondary, gz(P.DivisionSide), d.div_text(div_side))


GEAR_GIZMO_POS = {
    P.NumBlades: 0,
    P.InnerRadius: 1,
    P.OuterRadius: 2,
    P.Twist: 3,
    P.InnerCircleDivision: 4,
    P.InnerCircleRadius: 5,
    P.FilletCount: 6,
    P.FilletRadius: 7,
    P.Height: 8,
}


def proc_gear(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Gear.get_param_names())
    num_blades = out[P.NumBlades.name]
    inner_radius = out[P.InnerRadius.name]
    outer_radius = out[P.OuterRadius.name]
    twist = out[P.Twist.name]
    ic_division = out[P.InnerCircleDivision.name]
    ic_radius = out[P.InnerCircleRadius.name]
    fillet_count = out[P.FilletCount.name]
    fillet_radius = out[P.FilletRadius.name]
    height = out[P.Height.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[GEAR_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.InnerCircleRadius),
        d.div_text(ic_division),
        Vector((1, -1, 0)).normalized(),
        d.unit_dist(ic_radius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.OuterRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(outer_radius),
    )
    d.draw_text_at(
        d.color.primary,
        Vector((0, -outer_radius, 0)) + gz(P.NumBlades),
        d.div_text(num_blades),
    )
    d.draw_text_at(
        d.color.y,
        gz(P.FilletRadius) + Vector((0, -outer_radius * 1.25, 0)),
        f"{fillet_radius:.2f}",
    )
    d.draw_text_at(
        d.color.z,
        gz(P.FilletCount) + Vector((0, -outer_radius * 1.25 * 1.3, 0)),
        d.div_text(fillet_count),
    )
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.InnerRadius),
        None,
        Vector((1, 1, 0)).normalized(),
        d.unit_dist(inner_radius),
    )
    d.draw_text_at_2(
        d.color.z,
        gz(P.Twist),
        None,
        Vector((0, 1, 0)),
        f"{twist:.2f}",
        ZERO,
        Vector((0.5, 2.0)),
    )


SPRING_GIZMO_POS = {
    P.DivisionCircle: 0,
    P.Rotations: 1,
    P.BottomRadius: 2,
    P.TopRadius: 3,
    P.Height: 4,
    P.DivisionRing: 5,
    P.RingRadius: 6,
}


def proc_spring(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Spring.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    rotations = out[P.Rotations.name]
    bottom_radius = out[P.BottomRadius.name]
    top_radius = out[P.TopRadius.name]
    height = out[P.Height.name]
    div_ring = out[P.DivisionRing.name]
    ring_radius = out[P.RingRadius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[SPRING_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.BottomRadius),
        d.div_text(div_circle),
        Vector((0, 1, 0)),
        d.unit_dist(bottom_radius),
    )
    d.draw_text_at_2(
        d.color.x,
        gz(P.RingRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(ring_radius),
    )
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.TopRadius),
        f"{rotations:.2f}",
        Vector((0, 1, 0)),
        d.unit_dist(top_radius),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at(d.color.y, gz(P.DivisionRing), d.div_text(div_ring))


DCUBE_GIZMO_POS = {
    P.MinX: 0,
    P.MaxX: 1,
    P.MinY: 2,
    P.MaxY: 3,
    P.MinZ: 4,
    P.MaxZ: 5,
}


def proc_dcube(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
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


CAPSULE_GIZMO_POS = {
    P.DivisionCircle: 0,
    P.DivisionCap: 1,
    P.DivisionSide: 2,
    P.Height: 3,
    P.Radius: 4,
}


def proc_capsule(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_Capsule.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    div_cap = out[P.DivisionCap.name]
    div_side = out[P.DivisionSide.name]
    height = out[P.Height.name]
    radius = out[P.Radius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[CAPSULE_GIZMO_POS[p]].position

    d.draw_text_at(
        d.color.primary,
        gz(P.DivisionCircle),
        d.div_text(div_circle),
    )
    d.draw_text_at_2(
        d.color.primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(d.color.x, gz(P.Radius), None, Vector((1, 0, 0)), d.unit_dist(radius))
    d.draw_text_at(
        d.color.x,
        gz(P.DivisionSide),
        d.div_text(div_side),
    )
    d.draw_text_at(
        d.color.y,
        gz(P.DivisionCap) + Vector((1, 0, 1)).normalized() * radius,
        d.div_text(div_cap),
    )


def proc_quadsphere(mod: Modifier, d: Drawer, gizmo_info: GizmoInfoAr) -> None:
    out = get_interface_values(mod, PR.Primitive_QuadSphere.get_param_names())
    subd = out[P.Subdivision.name]
    radius = out[P.Radius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_info[SPHERE_GIZMO_POS[p]].position

    d.draw_text_at_2(
        d.color.primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color.secondary,
        gz(P.Subdivision),
        None,
        Vector((1, 0, 1)),
        d.div_text(subd),
    )


PROCS: dict[Type, Any] = {
    Type.Cube: proc_cube,
    Type.Cone: proc_cone,
    Type.Cylinder: proc_cylinder,
    Type.Grid: proc_grid,
    Type.ICOSphere: proc_icosphere,
    Type.Torus: proc_torus,
    Type.UVSphere: proc_uvsphere,
    Type.Tube: proc_tube,
    Type.Gear: proc_gear,
    Type.Spring: proc_spring,
    Type.DeformableCube: proc_dcube,
    Type.Capsule: proc_capsule,
    Type.QuadSphere: proc_quadsphere,
}


def is_primitive_selected(obj: Object | None) -> bool:
    if obj is None or not is_modern_primitive(obj):
        return False
    mod = obj.modifiers[0]
    return mod.show_viewport and mod.is_active


T = TypeVar("T")


class MPR_Hud(Operator):
    bl_idname = f"ui.{MODERN_PRIMITIVE_PREFIX}_show_hud"
    bl_label = "Show/Hide MPR HUD"
    bl_description = "Show/Hide ModernPrimitive HUD"
    bl_options = set()

    __handle = None
    show: BoolProperty(name="Show HUD", default=True)

    @classmethod
    def is_running(cls) -> bool:
        return cls.__handle is not None

    @classmethod
    def __handle_add(cls, context: Context) -> None:
        if not cls.is_running():
            cls.__handle = SpaceView3D.draw_handler_add(
                cls.__draw, (context,), "WINDOW", "POST_PIXEL"
            )

    @classmethod
    def __handle_remove(cls, context: Context) -> None:
        if cls.is_running():
            SpaceView3D.draw_handler_remove(cls.__handle, "WINDOW")
            cls.__handle = None

    @classmethod
    def cleanup(cls) -> None:
        cls.__handle_remove(bpy.context)

    @classmethod
    def __draw(cls, context: Context) -> None:
        # Do not display in any other than object mode
        if context.mode != "OBJECT":
            return

        obj = context.active_object
        if not is_primitive_selected(obj) or obj not in context.selected_objects:
            return

        space = cast(SpaceView3D, context.space_data)
        # Do not display if gizmo display is turned off
        if not (space.show_gizmo and space.show_gizmo_modifier):
            return

        try:
            typ = type_from_modifier_name(obj.modifiers[0].name)
            if typ not in PROCS:
                return

            reg3d = context.region_data
            show_hud = True

            # ------ Get Gizmo Positions ------
            mesh = get_evaluated_mesh(context, obj)
            gizmo_info = get_gizmo_info(mesh)

            # In quad view mode,
            # scale values are not displayed except for the upper-right view
            if len(space.region_quadviews) == 4:
                if space.region_quadviews[-1] != reg3d:
                    show_hud = False
            with make_drawer(blf, context, obj.matrix_world) as drawer:
                if show_hud:
                    drawer.show_hud(obj.scale)
                PROCS[typ](obj.modifiers[0], drawer, gizmo_info)

        except DGUnknownType:
            pass

    def execute(self, context: Context) -> set[str]:
        cls = MPR_Hud
        if self.show:
            cls.__handle_add(context)
        else:
            cls.__handle_remove(context)
        return {"FINISHED"}


# Display status of gizmo values from preferences
show_value_flag = None


# Set the gizmo value only once for the first time
def init_gizmo_value_show() -> None:
    # Enabled by default for now
    bpy.ops.ui.mpr_show_hud(show=True)

    # Do nothing if the flag value is not set due to some mistake
    if show_value_flag is None:
        pass
    else:
        # Set gizmo value display according to preferences value
        bpy.ops.ui.mpr_show_hud(show=show_value_flag)

        # Set the flag value to the window manager property value
        bpy.context.window_manager.show_gizmo_values = show_value_flag


def register() -> None:
    # show-gizmo flag from preferences
    global show_value_flag
    show_value_flag = get_addon_preferences(bpy.context).show_gizmo_value

    register_class(MPR_Hud)
    # This means not calling the operator now,
    # but after initialization is complete, but there may be a better way.
    bpy.app.timers.register(init_gizmo_value_show, first_interval=0)


def unregister() -> None:
    MPR_Hud.cleanup()
    unregister_class(MPR_Hud)
