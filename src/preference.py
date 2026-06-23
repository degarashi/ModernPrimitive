import bpy
import rna_keymap_ui
from bpy.props import BoolProperty
from bpy.types import AddonPreferences, Context, UILayout
from bpy.utils import register_class, unregister_class

from . import keymap
from .constants import get_addon_name, MODERN_PRIMITIVE_PREFIX


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
    show_world_space_value: BoolProperty(
        name="Show World-Space Values",
        description="Display world-space values alongside local values when object scale is not 1.0",  # noqa: E501
        default=False,
    )
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
        box.prop(self, "show_world_space_value", text="Show World-Space Values")

    def __box_shortcuts(self, layout: UILayout) -> None:
        box = layout.box()
        box.label(text="Shortcuts")

        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        km = kc.keymaps.get("3D View") if kc else None

        hotkeys = [
            ("wm.call_menu", f"VIEW3D_MT_{MODERN_PRIMITIVE_PREFIX}_append", "Main Menu"),
            (f"object.{MODERN_PRIMITIVE_PREFIX}_focus_modifier", None, "Focus Modifier"),
            ("object.mpr_modal_edit", None, "Modal Edit"),
        ]

        missing_count = 0
        total_count = len(hotkeys)

        if km:
            for kmi_idname, prop_name, label in hotkeys:
                kmi = keymap.get_hotkey_entry_item(km, kmi_idname, prop_name)
                row = box.row()
                row.label(text=label)

                if kmi:
                    sub = row.row()
                    sub.context_pointer_set("keymap", km)
                    rna_keymap_ui.draw_kmi([], kc, km, kmi, sub, 0)

                    op = row.operator(
                        keymap.USERPREF_OT_mpr_restore_individual_hotkey.bl_idname,
                        text="",
                        icon="FILE_REFRESH",
                    )
                    op.target_shortcut = label
                else:
                    missing_count += 1
                    row.label(text="Missing", icon="ERROR")
                    op = row.operator(
                        keymap.USERPREF_OT_mpr_restore_individual_hotkey.bl_idname,
                        text="Add",
                        icon="ADD",
                    )
                    op.target_shortcut = label
        else:
            missing_count = total_count

        if missing_count > 0:
            row = box.row()
            row.label(text=f"Missing {missing_count} of {total_count} shortcuts!", icon="ERROR")

        row = box.row()
        if missing_count == total_count:
            row.operator(
                keymap.USERPREF_OT_mpr_restore_hotkeys.bl_idname,
                text="Add Default Hotkeys",
                icon="ADD",
            )
        else:
            row.operator(
                keymap.USERPREF_OT_mpr_restore_hotkeys.bl_idname,
                text="Restore Default Hotkeys",
                icon="FILE_REFRESH",
            )

    def draw(self, ctx: Context) -> None:
        self.__box_create(self.layout)
        self.__box_gizmo(self.layout)
        self.__box_shortcuts(self.layout)


def register() -> None:
    register_class(Preference)


def unregister() -> None:
    unregister_class(Preference)
