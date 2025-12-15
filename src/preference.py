from bpy.props import BoolProperty
from bpy.types import AddonPreferences, Context, UILayout
from bpy.utils import register_class, unregister_class

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

    # --- N-Panel Option ---
    show_npanel: BoolProperty(
        name="Show N-Panel",
        description="Toggle N-Panel visibility",
        default=True,
    )
    # ------

    def __box_create(self, layout: UILayout) -> None:
        box = layout.box()
        box.label(text="Make option (Default)")
        box.prop(self, "make_cursors_rot")
        box.prop(self, "make_appropriate_size")
        box.prop(self, "make_smooth_shading")
        box.prop(self, "show_npanel")

    def __box_gizmo(self, layout: UILayout) -> None:
        box = layout.box()
        box.label(text="HUD")
        box.prop(self, "show_gizmo_value", text="Show Gizmo Value (Initial state)")

    def draw(self, ctx: Context) -> None:
        self.__box_create(self.layout)
        self.__box_gizmo(self.layout)


def register() -> None:
    register_class(Preference)


def unregister() -> None:
    unregister_class(Preference)
