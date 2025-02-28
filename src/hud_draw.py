import bpy
import blf
from typing import Any, cast, Iterable
from mathutils import Vector, Matrix, Color
from bpy.types import Operator, Context, SpaceView3D, Object, Modifier, Mesh
from bpy.utils import register_class, unregister_class
from .aux_func import (
    is_modern_primitive,
    type_from_modifier_name,
    get_addon_preferences,
    get_evaluated_mesh,
)
from .constants import Type, MODERN_PRIMITIVE_PREFIX
from .aux_node import get_interface_values
from .exception import DGUnknownType
from . import primitive_prop as P
from bpy.props import BoolProperty
from . import primitive as PR


def make_color256(r: int, g: int, b: int) -> Color:
    return Color((r / 255.0, g / 255.0, b / 255.0))


FONT_ID: int = 0
units = bpy.utils.units


def set_color(blf, color: Color) -> None:
    blf.color(FONT_ID, color.r, color.g, color.b, 1.0)


def set_position(blf, vec: Iterable[float]) -> None:
    blf.position(FONT_ID, vec[0], vec[1], 0)


def draw(blf, txt: str) -> None:
    blf.draw(FONT_ID, txt)


def set_position_draw(blf, vec: Iterable[float], txt: str) -> None:
    set_position(blf, vec)
    draw(blf, txt)


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
    COLOR_WHITE = make_color256(255, 255, 255)
    COLOR_X = make_color256(253, 54, 83)
    COLOR_Y = make_color256(138, 219, 0)
    COLOR_Z = make_color256(44, 143, 255)
    COLOR_PRIMARY = make_color256(245, 241, 77)
    COLOR_SECONDARY = make_color256(99, 255, 255)

    def __init__(self, blf: Any, context: Context, m_world: Matrix):
        reg = context.region
        reg3d = context.region_data

        self.__blf = blf
        self.__pref = context.preferences.view

        # テーマ設定を読んで色を反映
        cls = Drawer
        self.color_white = cls.COLOR_WHITE
        self.color_x = cls.COLOR_X
        self.color_y = cls.COLOR_Y
        self.color_z = cls.COLOR_Z
        self.color_primary = cls.COLOR_PRIMARY
        self.color_secondary = cls.COLOR_SECONDARY
        try:
            ui_theme = context.preferences.themes[0].user_interface
            self.color_x = ui_theme.axis_x
            self.color_y = ui_theme.axis_y
            self.color_z = ui_theme.axis_z
            self.color_primary = ui_theme.gizmo_primary
            self.color_secondary = ui_theme.gizmo_secondary
        except IndexError:
            pass

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
        set_color(blf, Drawer.COLOR_WHITE)
        self.__dim = Vector(blf.dimensions(FONT_ID, "A"))
        self.__dim.y += 4

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.__blf.disable(FONT_ID, blf.SHADOW)

    def gizmo_depend_worldpos(
        self,
        orig_pos: Vector,
        dir: Vector,
    ) -> Vector:
        # 描画元位置
        ori_p = perspec(self.__m_pers, orig_pos.to_4d())

        view_ori = Vector((0, 0, 1, 1))
        p_ori = perspec(self.__m_window, view_ori)
        win_ori = to_win(self.__window_size, p_ori)
        view_diff = Vector((1, 0, 1, 1))
        p_diff = perspec(self.__m_window, view_diff)
        win_diff = to_win(self.__window_size, p_diff)
        ratio = abs(win_diff.x - win_ori.x)
        ratio *= 0.008

        # ギズモ中心位置のZ距離
        gizmo_dist = ori_p.z

        AXIS_LEN = 4.0
        ui_ratio = self.__pref.gizmo_size / 100.0 * self.__pref.ui_scale
        move_dist = AXIS_LEN * gizmo_dist / 6 / ratio * ui_ratio
        return dir * move_dist + orig_pos

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
        set_position_draw(
            blf, (60, 10), f"Scale: {scale.x:.2f} {scale.y:.2f} {scale.z:.2f}"
        )


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


def proc_cube(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_Cube.get_param_names())
    size = out[P.Size.name]
    div_x = out[P.DivisionX.name]
    div_y = out[P.DivisionY.name]
    div_z = out[P.DivisionZ.name]
    div_g = out[P.GlobalDivision.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[CUBE_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_x,
        gz(P.SizeX),
        d.div_text(div_x),
        Vector((1, 0, 0)),
        d.unit_dist(size[0]),
    )
    d.draw_text_at_2(
        d.color_y,
        gz(P.SizeY),
        d.div_text(div_y),
        Vector((0, 1, 0)),
        d.unit_dist(size[1]),
    )
    d.draw_text_at_2(
        d.color_z,
        gz(P.SizeZ),
        d.div_text(div_z),
        Vector((0, 0, 1)),
        d.unit_dist(size[2]),
    )
    d.draw_text_at(
        d.color_secondary,
        gz(P.GlobalDivision) - Vector((size[0], size[1], 0))/4,
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


def proc_cone(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_Cone.get_param_names())
    div_side = out[P.DivisionSide.name]
    div_fill = out[P.DivisionFill.name]
    div_circle = out[P.DivisionCircle.name]
    top_radius = out[P.TopRadius.name]
    bottom_radius = out[P.BottomRadius.name]
    height = out[P.Height.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[CONE_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_z,
        gz(P.Height),
        d.div_text(div_fill),
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color_y,
        gz(P.TopRadius),
        d.div_text(div_circle),
        Vector((1, 0, 0)),
        d.unit_dist(top_radius),
    )
    d.draw_text_at_2(
        d.color_primary,
        gz(P.BottomRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(bottom_radius),
    )
    d.draw_text_at(
        d.color_secondary,
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


def proc_cylinder(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_Cylinder.get_param_names())
    radius = out[P.Radius.name]
    height = out[P.Height.name]
    div_circle = out[P.DivisionCircle.name]
    div_side = out[P.DivisionSide.name]
    div_fill = out[P.DivisionFill.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[CYLINDER_GIZMO_POS[p]]

    d.draw_text_at(
        d.color_x,
        gz(P.DivisionSide),
        d.div_text(div_side),
    )

    d.draw_text_at(
        d.color_y,
        Vector((1, 1, 0)).normalized() * radius + gz(P.DivisionCircle),
        d.div_text(div_circle),
    )
    d.draw_text_at(
        d.color_primary,
        Vector((1, 1, 0)).normalized() * radius * 0.7 + gz(P.DivisionFill),
        d.div_text(div_fill),
    )
    d.draw_text_at_2(
        d.color_primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color_primary,
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


def proc_grid(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_Grid.get_param_names())
    size_x = out[P.SizeX.name]
    size_y = out[P.SizeY.name]
    div_x = out[P.DivisionX.name]
    div_y = out[P.DivisionY.name]
    div_g = out[P.GlobalDivision.name]

    def gz(p: str) -> Vector:
        return gizmo_pos[GRID_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_x,
        gz("X"),
        d.div_text(div_x),
        Vector((1, 0, 0)),
        d.unit_dist(size_x),
    )
    d.draw_text_at_2(
        d.color_y,
        gz("Y"),
        d.div_text(div_y),
        Vector((0, 1, 0)),
        d.unit_dist(size_y),
    )
    d.draw_text_at(d.color_z, gz("GDiv"), d.div_text(div_g))


SPHERE_GIZMO_POS = {
    P.Radius: 0,
    P.Subdivision: 1,
}


def proc_icosphere(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_ICOSphere.get_param_names())
    radius = out[P.Radius.name]
    subd = out[P.Subdivision.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[SPHERE_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color_x,
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


def proc_torus(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_Torus.get_param_names())
    radius = out[P.Radius.name]
    ring_radius = out[P.RingRadius.name]
    div_ring = out[P.DivisionRing.name]
    div_circle = out[P.DivisionCircle.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[TORUS_GIZMO_POS[p]]

    d.draw_text_at(d.color_primary, gz(P.DivisionCircle), d.div_text(div_circle))
    d.draw_text_at_2(
        d.color_secondary,
        gz(P.RingRadius),
        d.div_text(div_ring),
        Vector((0, 0, 1)),
        d.unit_dist(ring_radius),
        Vector((2, 0.5)),
    )
    d.draw_text_at_2(
        d.color_primary,
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


def proc_uvsphere(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_UVSphere.get_param_names())
    radius = out[P.Radius.name]
    div_ring = out[P.DivisionRing.name]
    div_circle = out[P.DivisionCircle.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[UV_SPHERE_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_primary,
        gz(P.Radius),
        d.div_text(div_circle),
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at(
        d.color_secondary,
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


def proc_tube(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_Tube.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    height = out[P.Height.name]
    div_side = out[P.DivisionSide.name]
    outer_radius = out[P.OuterRadius.name]
    inner_radius = out[P.InnerRadius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[TUBE_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_primary,
        gz(P.Height),
        d.div_text(div_circle),
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color_y,
        gz(P.InnerRadius),
        None,
        Vector((1, 1, 0)).normalized(),
        d.unit_dist(inner_radius),
    )
    d.draw_text_at_2(
        d.color_x,
        gz(P.OuterRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(outer_radius),
    )
    d.draw_text_at(d.color_secondary, gz(P.DivisionSide), d.div_text(div_side))


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


def proc_gear(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
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
        return gizmo_pos[GEAR_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color_x,
        gz(P.InnerCircleRadius),
        d.div_text(ic_division),
        Vector((1, -1, 0)).normalized(),
        d.unit_dist(ic_radius),
    )
    d.draw_text_at_2(
        d.color_primary,
        gz(P.OuterRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(outer_radius),
    )
    d.draw_text_at(
        d.color_primary,
        Vector((0, -outer_radius, 0)) + gz(P.NumBlades),
        d.div_text(num_blades),
    )
    d.draw_text_at(
        d.color_y,
        gz(P.FilletRadius) + Vector((0, -outer_radius * 1.25, 0)),
        f"{fillet_radius:.2f}",
    )
    d.draw_text_at(
        d.color_z,
        gz(P.FilletCount) + Vector((0, -outer_radius * 1.25 * 1.3, 0)),
        d.div_text(fillet_count),
    )
    d.draw_text_at_2(
        d.color_secondary,
        gz(P.InnerRadius),
        None,
        Vector((1, 1, 0)).normalized(),
        d.unit_dist(inner_radius),
    )
    d.draw_text_at_2(
        d.color_z,
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


def proc_spring(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_Spring.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    rotations = out[P.Rotations.name]
    bottom_radius = out[P.BottomRadius.name]
    top_radius = out[P.TopRadius.name]
    height = out[P.Height.name]
    div_ring = out[P.DivisionRing.name]
    ring_radius = out[P.RingRadius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[SPRING_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_primary,
        gz(P.BottomRadius),
        d.div_text(div_circle),
        Vector((0, 1, 0)),
        d.unit_dist(bottom_radius),
    )
    d.draw_text_at_2(
        d.color_x,
        gz(P.RingRadius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(ring_radius),
    )
    d.draw_text_at_2(
        d.color_secondary,
        gz(P.TopRadius),
        f"{rotations:.2f}",
        Vector((0, 1, 0)),
        d.unit_dist(top_radius),
    )
    d.draw_text_at_2(
        d.color_primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at(d.color_y, gz(P.DivisionRing), d.div_text(div_ring))


def proc_dcube(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_DeformableCube.get_param_names())
    min_x = out[P.MinX.name]
    max_x = out[P.MaxX.name]
    min_y = out[P.MinY.name]
    max_y = out[P.MaxY.name]
    min_z = out[P.MinZ.name]
    max_z = out[P.MaxZ.name]

    center_x = (max_x - min_x) / 2
    center_y = (max_y - min_y) / 2
    center_z = (max_z - min_z) / 2

    d.draw_text_at_2(
        d.color_x,
        Vector((-min_x, center_y, center_z)),
        None,
        Vector((-1, 0, 0)),
        d.unit_dist(min_x),
    )
    d.draw_text_at_2(
        d.color_x,
        Vector((max_x, center_y, center_z)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(max_x),
    )
    d.draw_text_at_2(
        d.color_y,
        Vector((center_x, -min_y, center_z)),
        None,
        Vector((0, -1, 0)),
        d.unit_dist(min_y),
    )
    d.draw_text_at_2(
        d.color_y,
        Vector((center_x, max_y, center_z)),
        None,
        Vector((0, 1, 0)),
        d.unit_dist(max_y),
    )
    d.draw_text_at_2(
        d.color_z,
        Vector((center_x, center_y, -min_z)),
        None,
        Vector((0, 0, -1)),
        d.unit_dist(min_z),
    )
    d.draw_text_at_2(
        d.color_z,
        Vector((center_x, center_y, max_z)),
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


def proc_capsule(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_Capsule.get_param_names())
    div_circle = out[P.DivisionCircle.name]
    div_cap = out[P.DivisionCap.name]
    div_side = out[P.DivisionSide.name]
    height = out[P.Height.name]
    radius = out[P.Radius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[CAPSULE_GIZMO_POS[p]]

    d.draw_text_at(
        d.color_primary,
        gz(P.DivisionCircle),
        d.div_text(div_circle),
    )
    d.draw_text_at_2(
        d.color_primary,
        gz(P.Height),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color_x, gz(P.Radius), None, Vector((1, 0, 0)), d.unit_dist(radius)
    )
    d.draw_text_at(
        d.color_x,
        gz(P.DivisionSide),
        d.div_text(div_side),
    )
    d.draw_text_at(
        d.color_y,
        gz(P.DivisionCap) + Vector((1, 0, 1)).normalized() * radius,
        d.div_text(div_cap),
    )


def proc_quadsphere(mod: Modifier, d: Drawer, gizmo_pos: list[Vector]) -> None:
    out = get_interface_values(mod, PR.Primitive_QuadSphere.get_param_names())
    subd = out[P.Subdivision.name]
    radius = out[P.Radius.name]

    def gz(p: P.Prop) -> Vector:
        return gizmo_pos[SPHERE_GIZMO_POS[p]]

    d.draw_text_at_2(
        d.color_primary,
        gz(P.Radius),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color_secondary,
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
            MAX_ATTRIBUTES = 20
            gizmo_pos: list[Vector] = []
            mesh = get_evaluated_mesh(context, obj)

            try:
                attr = mesh.attributes["Gizmo Position"]
                if attr.domain == "POINT":
                    for i, data in enumerate(attr.data):
                        gizmo_pos.append(data.vector)
                        if i == MAX_ATTRIBUTES - 1:
                            break
            except KeyError:
                pass

            # In quad view mode,
            # scale values are not displayed except for the upper-right view
            if len(space.region_quadviews) == 4:
                if space.region_quadviews[-1] != reg3d:
                    show_hud = False
            with make_drawer(blf, context, obj.matrix_world) as drawer:
                if show_hud:
                    drawer.show_hud(obj.scale)
                PROCS[typ](obj.modifiers[0], drawer, gizmo_pos)

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
