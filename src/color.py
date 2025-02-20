from mathutils import Color
from bpy.types import Preferences


def make_color256(r: int, g: int, b: int) -> Color:
    return Color((r / 255.0, g / 255.0, b / 255.0))


class HUDColor:
    __white: Color
    __x: Color
    __y: Color
    __z: Color
    __primary: Color
    __secondary: Color

    @property
    def white(self):
        return self.__white

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def z(self):
        return self.__z

    @property
    def primary(self):
        return self.__primary

    @property
    def secondary(self):
        return self.__secondary

    # --- Default Color ---
    WHITE = make_color256(255, 255, 255)
    X = make_color256(253, 54, 83)
    Y = make_color256(138, 219, 0)
    Z = make_color256(44, 143, 255)
    PRIMARY = make_color256(245, 241, 77)
    SECONDARY = make_color256(99, 255, 255)

    def __init__(self, pref: Preferences):
        cls = self.__class__

        # Read the theme settings to reflect the color
        self.__white = cls.WHITE
        self.__x = cls.X
        self.__y = cls.Y
        self.__z = cls.Z
        self.__primary = cls.PRIMARY
        self.__secondary = cls.SECONDARY

        try:
            ui_theme = pref.themes[0].user_interface
            self.__x = ui_theme.axis_x
            self.__y = ui_theme.axis_y
            self.__z = ui_theme.axis_z
            self.__primary = ui_theme.gizmo_primary
            self.__secondary = ui_theme.gizmo_secondary
        except IndexError:
            pass
