import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

from .constants import MODERN_PRIMITIVE_PREFIX

HOTKEY_DEFS = [
    ("wm.call_menu", f"VIEW3D_MT_{MODERN_PRIMITIVE_PREFIX}_append"),
    (f"object.{MODERN_PRIMITIVE_PREFIX}_focus_modifier", None),
    ("object.mpr_modal_edit", None),
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
        for idname, prop_name in HOTKEY_DEFS:
            if kmi.idname == idname:
                if prop_name is None or getattr(kmi.properties, "name", None) == prop_name:
                    km.keymap_items.remove(kmi)
                    break


def add_hotkey():
    remove_hotkey()

    kc = _get_kc()
    if not kc:
        return
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    kmi = km.keymap_items.new("wm.call_menu", "M", "PRESS", ctrl=True, shift=True)
    kmi.properties.name = f"VIEW3D_MT_{MODERN_PRIMITIVE_PREFIX}_append"
    kmi.active = True

    kmi = km.keymap_items.new(
        f"object.{MODERN_PRIMITIVE_PREFIX}_focus_modifier", "X", "PRESS", ctrl=True, alt=True
    )
    kmi.active = True

    kmi = km.keymap_items.new("object.mpr_modal_edit", "C", "PRESS", ctrl=True, shift=True)
    kmi.active = True


class USERPREF_OT_mpr_add_hotkey(Operator):
    bl_idname = f"userpref.{MODERN_PRIMITIVE_PREFIX}_add_hotkey"
    bl_label = "Add Hotkey"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        add_hotkey()
        return {"FINISHED"}


def register():
    register_class(USERPREF_OT_mpr_add_hotkey)
    add_hotkey()


def unregister():
    remove_hotkey()
    unregister_class(USERPREF_OT_mpr_add_hotkey)
