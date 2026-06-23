import bpy
from typing import ClassVar

from bpy.props import StringProperty
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

from .constants import MODERN_PRIMITIVE_PREFIX

HOTKEY_DEFS = [
    {
        "label": "Main Menu",
        "idname": "wm.call_menu",
        "prop_name": f"VIEW3D_MT_{MODERN_PRIMITIVE_PREFIX}_append",
        "type": "M",
        "ctrl": True,
        "shift": True,
        "alt": False,
    },
    {
        "label": "Focus Modifier",
        "idname": f"object.{MODERN_PRIMITIVE_PREFIX}_focus_modifier",
        "prop_name": None,
        "type": "X",
        "ctrl": True,
        "shift": False,
        "alt": True,
    },
    {
        "label": "Modal Edit",
        "idname": "object.mpr_modal_edit",
        "prop_name": None,
        "type": "C",
        "ctrl": True,
        "shift": True,
        "alt": False,
    },
]


from .util import keymap_helper


def get_hotkey_entry_item(km, kmi_idname, properties_name=None):
    return keymap_helper.get_hotkey_entry_item(km, kmi_idname, properties_name)


def remove_hotkey():
    keymap_helper.remove_hotkeys(HOTKEY_DEFS)


def add_hotkey():
    keymap_helper.add_hotkeys(HOTKEY_DEFS)


def restore_individual_hotkey(label: str):
    keymap_helper.restore_individual_hotkey(label, HOTKEY_DEFS)


class USERPREF_OT_mpr_restore_hotkeys(Operator):
    bl_idname = f"userpref.{MODERN_PRIMITIVE_PREFIX}_restore_hotkeys"
    bl_label = "Restore Default Hotkeys"
    bl_options: ClassVar[set[str]] = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        add_hotkey()
        return {"FINISHED"}


class USERPREF_OT_mpr_restore_individual_hotkey(Operator):
    bl_idname = f"userpref.{MODERN_PRIMITIVE_PREFIX}_restore_individual_hotkey"
    bl_label = "Restore Shortcut"
    bl_options: ClassVar[set[str]] = {"REGISTER", "INTERNAL"}

    target_shortcut: StringProperty(name="Target Shortcut")

    def execute(self, context):
        if self.target_shortcut:
            restore_individual_hotkey(self.target_shortcut)
        return {"FINISHED"}


def register():
    register_class(USERPREF_OT_mpr_restore_hotkeys)
    register_class(USERPREF_OT_mpr_restore_individual_hotkey)
    add_hotkey()


def unregister():
    remove_hotkey()
    unregister_class(USERPREF_OT_mpr_restore_hotkeys)
    unregister_class(USERPREF_OT_mpr_restore_individual_hotkey)
