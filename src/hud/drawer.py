from collections.abc import Iterable
from types import ModuleType

import blf
import bpy
from bpy.types import Context, PreferencesView
from mathutils import Color, Matrix, Vector

from ..util.aux_math import make_vec3
from ..blf_aux import DEFAULT_FONT_ID as FONT_ID
from ..blf_aux import set_color, set_position_draw
from ..color import HUDColor

units = bpy.utils.units

ONE = Vector((1, 1))
ZERO = Vector((0, 0))
HALF_ONE = ONE / 2


def tf_posvec(mat: Matrix, pos: Vector) -> Vector:
    """Transform position vector with perspective matrix
    Args:
        mat (Matrix): Perspective matrix
        pos (Vector): Position vector(d=4)

    Returns:
        Vector: transformed vector(d=3)
    """
    pos = mat @ pos
    pos.x /= pos.w
    pos.y /= pos.w
    pos.z = pos.w
    return pos.xyz


def tf_window(window_size: Iterable[int], sc_pos: Vector) -> Vector:
    """
    Args:
        window_size(Iterable[int]): window size(d=2) pixel unit
        sc_pos(Vector): screen-space position vector(d=2)

    Returns:
        Vector: transformed vector
    """
    return Vector(
        (
            (sc_pos.x / 2 + 0.5) * window_size[0],
            (sc_pos.y / 2 + 0.5) * window_size[1],
        )
    )


def tf_w_p(window_size: Iterable[int], p_mat: Matrix, pos: Vector) -> Vector:
    return tf_window(window_size, tf_posvec(p_mat, pos))


class Drawer:
    color: HUDColor
    __blf: ModuleType
    __pref: PreferencesView
    __window_size: tuple[int, int]
    __m_pers: Matrix
    __m_window: Matrix
    __system: str
    __text_dim: Vector
    __scale: Vector
    __unit_scale: float

    def __init__(self, blf: ModuleType, context: Context, m_world: Matrix):
        reg = context.region
        reg3d = context.region_data

        self.color = HUDColor(context.preferences)
        self.__blf = blf
        self.__pref = context.preferences.view
        self.__window_size = (reg.width, reg.height)
        self.__m_pers = reg3d.perspective_matrix @ m_world
        self.__scale = m_world.to_scale()
        self.__m_window = reg3d.window_matrix
        self.__system = context.scene.unit_settings.system
        self.__unit_scale = context.scene.unit_settings.scale_length

        scale = self.__pref.ui_scale
        blf = self.__blf
        blf.enable(FONT_ID, blf.SHADOW)
        blf.shadow_offset(FONT_ID, 1, -1)
        blf.size(FONT_ID, 15 * scale)
        set_color(blf, HUDColor.WHITE)
        self.__text_dim = Vector(blf.dimensions(FONT_ID, "A"))
        self.__text_dim.y += 4

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.__blf.disable(FONT_ID, blf.SHADOW)

    def _gizmo_depend_worldpos(
        self,
        orig_pos: Vector,
        dir_v: Vector,
    ) -> Vector:
        # Origin position
        ori_p = tf_posvec(self.__m_pers, orig_pos.to_4d())

        win_ori = tf_w_p(self.__window_size, self.__m_window, Vector((0, 0, 1, 1)))
        win_x_one = tf_w_p(self.__window_size, self.__m_window, Vector((1, 0, 1, 1)))

        ratio = abs(win_x_one.x - win_ori.x)
        ratio *= 0.008

        # z-distance at the center of Gizmo
        gizmo_dist = ori_p.z

        AXIS_LEN = 4.0
        ui_ratio = self.__pref.gizmo_size / 100.0 * self.__pref.ui_scale
        move_dist = make_vec3(AXIS_LEN * gizmo_dist / 6 / ratio * ui_ratio)
        for i in range(3):
            move_dist[i] /= self.__scale[i]
        return dir_v * move_dist + orig_pos

    def draw_text_at(
        self,
        color: Color,
        ori_pos: Vector,
        msg: str,
        label_offset_r: Vector = HALF_ONE,
    ) -> None:
        set_color(self.__blf, color)
        ori_w = tf_w_p(self.__window_size, self.__m_pers, ori_pos.to_4d())
        set_position_draw(self.__blf, ori_w + self.__text_dim * label_offset_r, msg)

    def draw_text_at_2(  # noqa: PLR0913
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
        target_pos = self._gizmo_depend_worldpos(ori_pos, lc_dir)
        set_position_draw(
            self.__blf,
            tf_w_p(self.__window_size, self.__m_pers, target_pos.to_4d())
            + self.__text_dim * label_offset1_r,
            msg1,
        )

    @staticmethod
    def div_text(val: int) -> str:
        """
        Convert the input division number into display text.

        This function transforms the given division number into a string
        representation for display purposes.

        Args:
            val (int): The division number to be converted.

        Returns:
            str: The formatted text representation of the division number.
        """
        return f"[{val}]"

    def unit_dist(self, val: float, prec: int = 3) -> str:
        # Apply scene unit scale explicitly
        scaled_val = val * self.__unit_scale
        return units.to_string(
            self.__system,
            units.categories.LENGTH,
            scaled_val,
            precision=prec,
        )

    def show_hud(self, scale: Vector) -> None:
        set_position_draw(blf, (50, 30), "ModernPrimitive:")
        set_position_draw(blf, (60, 10), f"Scale: {scale.x:.2f} {scale.y:.2f} {scale.z:.2f}")
