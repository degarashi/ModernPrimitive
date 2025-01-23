from bpy.types import AddonPreferences, Context
from bpy.utils import register_class, unregister_class
from bpy.props import BoolProperty
from .constants import get_addon_name


class Preference(AddonPreferences):
    bl_idname = get_addon_name()

    # --- Make Option ---
    make_appropriate_size: BoolProperty(
        name="Appropriate Size",
        description="Create primitives with proper scaling by default",
        default=False,
    )
    make_cursors_rot: BoolProperty(name="Set Cursor's Rotation", default=False)
    make_smooth_shading: BoolProperty(name="Smooth Shading", default=False)
    # ------

    # --- Gizmo Option ---
    show_gizmo_value: BoolProperty(name="Show Gizmo Value", default=True)
    # ------

    def draw(self, ctx: Context) -> None:
        layout = self.layout
        box = layout.box()
        box.label(text="Make option (Default)")
        box.prop(self, "make_cursors_rot")
        box.prop(self, "make_appropriate_size")
        box.prop(self, "make_smooth_shading")

        box = layout.box()
        box.label(text="HUD")
        box.prop(self, "show_gizmo_value", text="Show Gizmo Value (Initial state)")


def register() -> None:
    register_class(Preference)


def unregister() -> None:
    unregister_class(Preference)
