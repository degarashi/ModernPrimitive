from mathutils import Color
from bpy.types import Preferences


def make_color256(r: int, g: int, b: int) -> Color:
    return Color((r / 255.0, g / 255.0, b / 255.0))


class HUDColor:
    white: Color
    x: Color
    y: Color
    z: Color
    primary: Color
    secondary: Color

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
        self.white = cls.WHITE
        self.x = cls.X
        self.y = cls.Y
        self.z = cls.Z
        self.primary = cls.PRIMARY
        self.secondary = cls.SECONDARY

        try:
            ui_theme = pref.themes[0].user_interface
            self.x = ui_theme.axis_x
            self.y = ui_theme.axis_y
            self.z = ui_theme.axis_z
            self.primary = ui_theme.gizmo_primary
            self.secondary = ui_theme.gizmo_secondary
        except IndexError:
            pass
