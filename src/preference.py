import bpy
import rna_keymap_ui
from bpy.props import BoolProperty
from bpy.types import AddonPreferences, Context, UILayout
from bpy.utils import register_class, unregister_class

from .constants import get_addon_name
from .util.keymap_manager import KeymapManager

HOTKEY_DEFS = [
    {
        "idname": "wm.call_menu",
        "type": "M",
        "ctrl": True,
        "shift": True,
        "alt": False,
        "properties": {"name": "VIEW3D_MT_mpr_append"},
    },
    {
        "idname": "object.mpr_focus_modifier",
        "type": "X",
        "ctrl": True,
        "shift": False,
        "alt": True,
    },
    {"idname": "object.mpr_modal_edit", "type": "C", "ctrl": True, "shift": True, "alt": False},
]

keymap_manager = KeymapManager(HOTKEY_DEFS)


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
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        if not kc:
            return

        box = layout.box()
        col = box.column()
        col.label(text="Setup Keymap")

        km_tree = {}
        for _km, _kmi in keymap_manager.addon_keymaps:
            if _km.name not in km_tree:
                km_tree[_km.name] = []
            km_tree[_km.name].append(
                (_kmi.idname, _kmi.properties.name if "name" in _kmi.properties else None)
            )

        handled_kmi = set()
        for km_name, kmi_items in km_tree.items():
            km = kc.keymaps.get(km_name)
            if km:
                col.context_pointer_set("keymap", km)
                col.separator()
                row = col.row(align=True)
                row.label(text=km_name)

                if km.is_user_modified:
                    subrow = row.row()
                    subrow.alignment = "RIGHT"
                    subrow.operator("preferences.keymap_restore", text="Restore")

                for kmi_node in kmi_items:
                    kmi = keymap_manager.get_hotkey_entry_item(km, kmi_node[0], kmi_node[1], handled_kmi)
                    col.separator()

                    if kmi:
                        handled_kmi.add(kmi)
                        rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
                    else:
                        row = col.row(align=True)
                        row.separator(factor=2.0)
                        row.label(
                            text=f"Keymap item for '{kmi_node[0]}' in '{km_name}' not found",
                            icon="ERROR",
                        )

    def draw(self, ctx: Context) -> None:
        self.__box_create(self.layout)
        self.__box_gizmo(self.layout)
        self.__box_shortcuts(self.layout)


def register() -> None:
    register_class(Preference)
    keymap_manager.register()


def unregister() -> None:
    unregister_class(Preference)
    keymap_manager.unregister()
