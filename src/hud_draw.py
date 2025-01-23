import bpy
import blf
from typing import Any, cast, Iterable
from mathutils import Vector, Matrix, Color
from bpy.types import Operator, Context, SpaceView3D, Object, Modifier, Scene
from bpy.utils import register_class, unregister_class
from .aux_func import (
    is_modern_primitive,
    type_from_modifier_name,
    get_addon_preferences,
)
from .constants import Type, MODERN_PRIMITIVE_PREFIX
from .aux_node import get_interface_values
from .exception import DGUnknownType
from . import primitive_prop as P
from bpy.props import BoolProperty


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


def proc_cube(mod: Modifier, d: Drawer) -> None:
    input = (
        P.SizeX.name,
        P.SizeY.name,
        P.SizeZ.name,
        P.DivisionX.name,
        P.DivisionY.name,
        P.DivisionZ.name,
        P.GlobalDivision.name,
    )
    out = get_interface_values(mod, input)
    size_x = out[P.SizeX.name]
    size_y = out[P.SizeY.name]
    size_z = out[P.SizeZ.name]
    div_x = out[P.DivisionX.name]
    div_y = out[P.DivisionY.name]
    div_z = out[P.DivisionZ.name]

    d.draw_text_at_2(
        d.color_x,
        Vector((size_x, 0, 0)),
        d.div_text(div_x),
        Vector((1, 0, 0)),
        d.unit_dist(size_x),
    )
    d.draw_text_at_2(
        d.color_y,
        Vector((0, size_y, 0)),
        d.div_text(div_y),
        Vector((0, 1, 0)),
        d.unit_dist(size_y),
    )
    d.draw_text_at_2(
        d.color_z,
        Vector((0, 0, size_z)),
        d.div_text(div_z),
        Vector((0, 0, 1)),
        d.unit_dist(size_z),
    )
    d.draw_text_at(
        d.color_secondary,
        Vector((-size_x, -size_y, size_z)),
        f"{out[P.GlobalDivision.name]:.2f}",
    )


def proc_cone(mod: Modifier, d: Drawer) -> None:
    input = (
        P.DivisionSide.name,
        P.DivisionFill.name,
        P.DivisionCircle.name,
        P.TopRadius.name,
        P.BottomRadius.name,
        P.Height.name,
    )
    out = get_interface_values(mod, input)
    div_side = out[P.DivisionSide.name]
    div_fill = out[P.DivisionFill.name]
    div_circle = out[P.DivisionCircle.name]
    top_radius = out[P.TopRadius.name]
    bottom_radius = out[P.BottomRadius.name]
    height = out[P.Height.name]

    d.draw_text_at_2(
        d.color_z,
        Vector((0, 0, height)),
        d.div_text(div_fill),
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color_y,
        Vector((top_radius, 0, height)),
        d.div_text(div_circle),
        Vector((1, 0, 0)),
        d.unit_dist(top_radius),
    )
    d.draw_text_at_2(
        d.color_primary,
        Vector((bottom_radius, 0, 0)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(bottom_radius),
    )
    d.draw_text_at(
        d.color_secondary,
        (Vector((0, bottom_radius, 0)) + Vector((0, top_radius, height))) / 2,
        d.div_text(div_side),
    )


def proc_cylinder(mod: Modifier, d: Drawer) -> None:
    input = (
        P.Radius.name,
        P.Height.name,
        P.DivisionCircle.name,
        P.DivisionSide.name,
        P.DivisionFill.name,
        P.Centered.name,
    )
    out = get_interface_values(mod, input)
    radius = out[P.Radius.name]
    height = out[P.Height.name]
    div_circle = out[P.DivisionCircle.name]
    div_side = out[P.DivisionSide.name]
    div_fill = out[P.DivisionFill.name]
    centered = out[P.Centered.name]
    h_center = 0 if centered else height / 2

    d.draw_text_at(d.color_x, Vector((radius, 0, h_center)), d.div_text(div_side))

    d.draw_text_at(
        d.color_y,
        Vector((1, 1, 0)).normalized() * radius + Vector((0, 0, height)),
        d.div_text(div_circle),
    )
    d.draw_text_at(
        d.color_primary,
        Vector((1, 1, 0)).normalized() * radius * 0.7 + Vector((0, 0, height)),
        d.div_text(div_fill),
    )
    d.draw_text_at_2(
        d.color_primary,
        Vector((radius, 0, h_center)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color_primary,
        Vector((0, 0, height)),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )


def proc_grid(mod: Modifier, d: Drawer) -> None:
    input = (
        P.SizeX.name,
        P.SizeY.name,
        P.DivisionX.name,
        P.DivisionY.name,
        P.GlobalDivision.name,
    )
    out = get_interface_values(mod, input)
    size_x = out[P.SizeX.name]
    size_y = out[P.SizeY.name]
    div_x = out[P.DivisionX.name]
    div_y = out[P.DivisionY.name]
    div_g = out[P.GlobalDivision.name]
    d.draw_text_at_2(
        d.color_x,
        Vector((size_x, 0, 0)),
        d.div_text(div_x),
        Vector((1, 0, 0)),
        d.unit_dist(size_x),
    )
    d.draw_text_at_2(
        d.color_y,
        Vector((0, size_y, 0)),
        d.div_text(div_y),
        Vector((0, 1, 0)),
        d.unit_dist(size_y),
    )
    d.draw_text_at(d.color_z, Vector((0, 0, 0)), d.div_text(div_g))


def proc_icosphere(mod: Modifier, d: Drawer) -> None:
    input = (
        P.Radius.name,
        P.Subdivision.name,
    )
    out = get_interface_values(mod, input)
    radius = out[P.Radius.name]
    subd = out[P.Subdivision.name]
    d.draw_text_at_2(
        d.color_primary,
        Vector((radius, 0, 0)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color_x,
        Vector((radius, 0, 0)),
        None,
        Vector((1, 0, 1)).normalized() * 1.4,
        d.div_text(subd),
    )


def proc_torus(mod: Modifier, d: Drawer) -> None:
    input = (
        P.Radius.name,
        P.RingRadius.name,
        P.DivisionRing.name,
        P.DivisionCircle.name,
    )
    out = get_interface_values(mod, input)
    radius = out[P.Radius.name]
    ring_radius = out[P.RingRadius.name]
    div_ring = out[P.DivisionRing.name]
    div_circle = out[P.DivisionCircle.name]
    d.draw_text_at(d.color_primary, ZERO, d.div_text(div_circle))
    d.draw_text_at_2(
        d.color_secondary,
        Vector((radius, 0, ring_radius)),
        d.div_text(div_ring),
        Vector((0, 0, 1)),
        d.unit_dist(ring_radius),
        Vector((2, 0.5)),
    )
    d.draw_text_at_2(
        d.color_primary,
        Vector((radius + ring_radius, 0, 0)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )


def proc_uvsphere(mod: Modifier, d: Drawer) -> None:
    input = (P.Radius.name, P.DivisionRing.name, P.DivisionCircle.name)
    out = get_interface_values(mod, input)
    radius = out[P.Radius.name]
    div_ring = out[P.DivisionRing.name]
    div_circle = out[P.DivisionCircle.name]

    d.draw_text_at_2(
        d.color_primary,
        Vector((radius, 0, 0)),
        d.div_text(div_circle),
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at(d.color_secondary, Vector((0, 0, radius)), d.div_text(div_ring))


def proc_tube(mod: Modifier, d: Drawer) -> None:
    input = (
        P.DivisionCircle.name,
        P.Height.name,
        P.DivisionSide.name,
        P.OuterRadius.name,
        P.InnerRadius.name,
        P.Centered.name,
    )
    out = get_interface_values(mod, input)
    div_circle = out[P.DivisionCircle.name]
    height = out[P.Height.name]
    div_side = out[P.DivisionSide.name]
    outer_radius = out[P.OuterRadius.name]
    inner_radius = out[P.InnerRadius.name]
    centered = out[P.Centered.name]

    h_center = height / 2 if not centered else 0

    d.draw_text_at_2(
        d.color_primary,
        Vector((0, 0, height)),
        d.div_text(div_circle),
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color_y,
        Vector((1, 1, 0)).normalized() * inner_radius + Vector((0, 0, h_center)),
        None,
        Vector((1, 1, 0)).normalized(),
        d.unit_dist(inner_radius),
    )
    d.draw_text_at_2(
        d.color_x,
        Vector((outer_radius, 0, h_center)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(outer_radius),
    )
    d.draw_text_at(
        d.color_secondary, Vector((outer_radius, 0, h_center)), d.div_text(div_side)
    )


def proc_gear(mod: Modifier, d: Drawer) -> None:
    input = (
        P.NumBlades.name,
        P.InnerRadius.name,
        P.OuterRadius.name,
        P.Twist.name,
        P.InnerCircleDivision.name,
        P.InnerCircleRadius.name,
        P.FilletCount.name,
        P.FilletRadius.name,
        P.Height.name,
    )
    out = get_interface_values(mod, input)
    num_blades = out[P.NumBlades.name]
    inner_radius = out[P.InnerRadius.name]
    outer_radius = out[P.OuterRadius.name]
    twist = out[P.Twist.name]
    ic_division = out[P.InnerCircleDivision.name]
    ic_radius = out[P.InnerCircleRadius.name]
    fillet_count = out[P.FilletCount.name]
    fillet_radius = out[P.FilletRadius.name]
    height = out[P.Height.name]

    d.draw_text_at_2(
        d.color_primary,
        Vector((0, 0, height)),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color_x,
        Vector((1, -1, 0)).normalized() * ic_radius + Vector((0, 0, height)),
        d.div_text(ic_division),
        Vector((1, -1, 0)).normalized(),
        d.unit_dist(ic_radius),
    )
    d.draw_text_at_2(
        d.color_primary,
        Vector((outer_radius, 0, height)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(outer_radius),
    )
    d.draw_text_at(
        d.color_primary,
        Vector((0, -outer_radius, 0)) + Vector((0, 0, height)),
        d.div_text(num_blades),
    )
    d.draw_text_at(
        d.color_y, Vector((0, -outer_radius * 1.25, 0)), f"{fillet_radius:.2f}"
    )
    d.draw_text_at(
        d.color_z, Vector((0, -outer_radius * 1.25 * 1.3, 0)), d.div_text(fillet_count)
    )
    d.draw_text_at_2(
        d.color_secondary,
        Vector((1, 1, 0)).normalized() * inner_radius,
        None,
        Vector((1, 1, 0)).normalized(),
        d.unit_dist(inner_radius),
    )
    d.draw_text_at_2(
        d.color_z,
        Vector((outer_radius, 0, 0)),
        None,
        Vector((0, 1, 0)),
        f"{twist:.2f}",
        ZERO,
        Vector((0.5, 2.0)),
    )


def proc_spring(mod: Modifier, d: Drawer) -> None:
    input = (
        P.DivisionCircle.name,
        P.Rotations.name,
        P.BottomRadius.name,
        P.TopRadius.name,
        P.Height.name,
        P.DivisionRing.name,
        P.RingRadius.name,
    )
    out = get_interface_values(mod, input)
    div_circle = out[P.DivisionCircle.name]
    rotations = out[P.Rotations.name]
    bottom_radius = out[P.BottomRadius.name]
    top_radius = out[P.TopRadius.name]
    height = out[P.Height.name]
    div_ring = out[P.DivisionRing.name]
    ring_radius = out[P.RingRadius.name]

    d.draw_text_at_2(
        d.color_primary,
        Vector((0, bottom_radius, 0)),
        d.div_text(div_circle),
        Vector((0, 1, 0)),
        d.unit_dist(bottom_radius),
    )
    d.draw_text_at_2(
        d.color_x,
        Vector((bottom_radius + ring_radius, 0, 0)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(ring_radius),
    )
    d.draw_text_at_2(
        d.color_secondary,
        Vector((0, top_radius, height)),
        f"{rotations:.2f}",
        Vector((0, 1, 0)),
        d.unit_dist(top_radius),
    )
    d.draw_text_at_2(
        d.color_primary,
        Vector((0, 0, height)),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at(
        d.color_y, Vector((bottom_radius, 0, ring_radius)), d.div_text(div_ring)
    )


def proc_dcube(mod: Modifier, d: Drawer) -> None:
    input = (
        P.MinX.name,
        P.MaxX.name,
        P.MinY.name,
        P.MaxY.name,
        P.MinZ.name,
        P.MaxZ.name,
    )
    out = get_interface_values(mod, input)
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


def proc_capsule(mod: Modifier, d: Drawer) -> None:
    input = (
        P.DivisionCircle.name,
        P.DivisionCap.name,
        P.DivisionSide.name,
        P.Height.name,
        P.Radius.name,
    )
    out = get_interface_values(mod, input)
    div_circle = out[P.DivisionCircle.name]
    div_cap = out[P.DivisionCap.name]
    div_side = out[P.DivisionSide.name]
    height = out[P.Height.name]
    radius = out[P.Radius.name]

    d.draw_text_at(
        d.color_primary,
        Vector((1, 1, 0)).normalized() * radius + Vector((0, 0, height)),
        d.div_text(div_circle),
    )
    d.draw_text_at_2(
        d.color_primary,
        Vector((0, 0, height + radius)),
        None,
        Vector((0, 0, 1)),
        d.unit_dist(height),
    )
    d.draw_text_at_2(
        d.color_x, Vector((radius, 0, 0)), None, Vector((1, 0, 0)), d.unit_dist(radius)
    )
    d.draw_text_at(
        d.color_x,
        Vector((0, 1, 1)).normalized() * height * 0.8 + Vector((radius, 0, 0)),
        d.div_text(div_side),
    )
    d.draw_text_at(
        d.color_y,
        Vector((1, 0, 1)).normalized() * radius + Vector((0, 0, height)),
        d.div_text(div_cap),
    )


def proc_quadsphere(mod: Modifier, d: Drawer) -> None:
    input = (P.Subdivision.name, P.Radius.name)
    out = get_interface_values(mod, input)
    subd = out[P.Subdivision.name]
    radius = out[P.Radius.name]

    d.draw_text_at_2(
        d.color_primary,
        Vector((radius, 0, 0)),
        None,
        Vector((1, 0, 0)),
        d.unit_dist(radius),
    )
    d.draw_text_at_2(
        d.color_secondary,
        Vector((1, 0, 1)).normalized() * radius,
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

            # In quad view mode,
            # scale values are not displayed except for the upper-right view
            if len(space.region_quadviews) == 4:
                if space.region_quadviews[-1] != reg3d:
                    show_hud = False
            with make_drawer(blf, context, obj.matrix_world) as drawer:
                if show_hud:
                    drawer.show_hud(obj.scale)
                PROCS[typ](obj.modifiers[0], drawer)

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
