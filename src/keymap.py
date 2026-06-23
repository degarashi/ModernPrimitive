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


def _get_kc():
    return bpy.context.window_manager.keyconfigs.addon


def get_hotkey_entry_item(km, kmi_idname, properties_name=None):
    for km_item in km.keymap_items:
        if km_item.idname == kmi_idname:
            if properties_name:
                if getattr(km_item.properties, "name", None) == properties_name:
                    return km_item
            else:
                return km_item
    return None


def remove_hotkey():
    kc = _get_kc()
    if not kc:
        return
    km = kc.keymaps.get("3D View")
    if not km:
        return
    for kmi in list(km.keymap_items):
        for spec in HOTKEY_DEFS:
            if kmi.idname == spec["idname"]:
                prop_name = spec["prop_name"]
                if prop_name is None or getattr(kmi.properties, "name", None) == prop_name:
                    km.keymap_items.remove(kmi)
                    break


def add_hotkey():
    remove_hotkey()

    kc = _get_kc()
    if not kc:
        return
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    for spec in HOTKEY_DEFS:
        kmi = km.keymap_items.new(
            spec["idname"],
            spec["type"],
            "PRESS",
            ctrl=spec["ctrl"],
            shift=spec["shift"],
            alt=spec["alt"],
        )
        if spec["prop_name"]:
            kmi.properties.name = spec["prop_name"]
        kmi.active = True


def restore_individual_hotkey(label: str):
    kc = _get_kc()
    if not kc:
        return
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    target_spec = None
    for spec in HOTKEY_DEFS:
        if spec["label"] == label:
            target_spec = spec
            break
    if not target_spec:
        return

    for kmi in list(km.keymap_items):
        if kmi.idname == target_spec["idname"]:
            prop_name = target_spec["prop_name"]
            if prop_name is None or getattr(kmi.properties, "name", None) == prop_name:
                km.keymap_items.remove(kmi)
                break

    kmi = km.keymap_items.new(
        target_spec["idname"],
        target_spec["type"],
        "PRESS",
        ctrl=target_spec["ctrl"],
        shift=target_spec["shift"],
        alt=target_spec["alt"],
    )
    if target_spec["prop_name"]:
        kmi.properties.name = target_spec["prop_name"]
    kmi.active = True


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
