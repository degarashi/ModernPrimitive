import bpy
from typing import Any


def get_addon_keyconfig():
    """Returns the addon key configuration from Blender's window manager."""
    return bpy.context.window_manager.keyconfigs.addon


def get_hotkey_entry_item(
    km: bpy.types.KeyMap, kmi_idname: str, properties_name: str | None = None
) -> bpy.types.KeyMapItem | None:
    """Finds and returns a specific KeyMapItem by its idname and optional property name."""
    for km_item in km.keymap_items:
        if km_item.idname == kmi_idname:
            if properties_name:
                if getattr(km_item.properties, "name", None) == properties_name:
                    return km_item
            else:
                return km_item
    return None


def remove_hotkeys(keymap_defs: list[dict[str, Any]], keymap_name: str = "3D View"):
    """Removes all keymaps defined in the keymap_defs list."""
    kc = get_addon_keyconfig()
    if not kc:
        return
    km = kc.keymaps.get(keymap_name)
    if not km:
        return
    for kmi in list(km.keymap_items):
        for spec in keymap_defs:
            if kmi.idname == spec["idname"]:
                prop_name = spec.get("prop_name")
                if prop_name is None or getattr(kmi.properties, "name", None) == prop_name:
                    km.keymap_items.remove(kmi)
                    break


def add_hotkeys(
    keymap_defs: list[dict[str, Any]], keymap_name: str = "3D View", space_type: str = "VIEW_3D"
):
    """Adds or registers hotkeys based on keymap definitions."""
    remove_hotkeys(keymap_defs, keymap_name=keymap_name)
    kc = get_addon_keyconfig()
    if not kc:
        return
    km = kc.keymaps.new(name=keymap_name, space_type=space_type)

    for spec in keymap_defs:
        kmi = km.keymap_items.new(
            spec["idname"],
            spec["type"],
            "PRESS",
            ctrl=spec.get("ctrl", False),
            shift=spec.get("shift", False),
            alt=spec.get("alt", False),
        )
        prop_name = spec.get("prop_name")
        if prop_name:
            kmi.properties.name = prop_name
        kmi.active = True


def restore_individual_hotkey(
    label: str,
    keymap_defs: list[dict[str, Any]],
    keymap_name: str = "3D View",
    space_type: str = "VIEW_3D",
):
    """Restores a single hotkey definition by its label."""
    kc = get_addon_keyconfig()
    if not kc:
        return
    km = kc.keymaps.new(name=keymap_name, space_type=space_type)

    target_spec = None
    for spec in keymap_defs:
        if spec.get("label") == label:
            target_spec = spec
            break
    if not target_spec:
        return

    for kmi in list(km.keymap_items):
        if kmi.idname == target_spec["idname"]:
            prop_name = target_spec.get("prop_name")
            if prop_name is None or getattr(kmi.properties, "name", None) == prop_name:
                km.keymap_items.remove(kmi)
                break

    kmi = km.keymap_items.new(
        target_spec["idname"],
        target_spec["type"],
        "PRESS",
        ctrl=target_spec.get("ctrl", False),
        shift=target_spec.get("shift", False),
        alt=target_spec.get("alt", False),
    )
    prop_name = target_spec.get("prop_name")
    if prop_name:
        kmi.properties.name = prop_name
    kmi.active = True
