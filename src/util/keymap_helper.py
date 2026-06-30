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
    """Removes keymaps matching the operator's idname and prop_name on unregister."""
    kc = get_addon_keyconfig()
    if not kc:
        return
    km = kc.keymaps.get(keymap_name)
    if not km:
        return
    for spec in keymap_defs:
        # Remove all matching items in case there are duplicates
        while True:
            kmi = get_hotkey_entry_item(km, spec["idname"], spec.get("prop_name"))
            if kmi:
                km.keymap_items.remove(kmi)
            else:
                break


def add_hotkeys(
    keymap_defs: list[dict[str, Any]], keymap_name: str = "3D View", space_type: str = "VIEW_3D"
):
    """Adds missing hotkeys without removing existing user customizations."""
    kc = get_addon_keyconfig()
    if not kc:
        return
    km = kc.keymaps.new(name=keymap_name, space_type=space_type)

    for spec in keymap_defs:
        # Skip if a keymap item for this operator already exists
        # (preserving user customizations)
        if get_hotkey_entry_item(km, spec["idname"], spec.get("prop_name")):
            continue

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

    # Remove existing keymap items for this operator before restoring
    while True:
        kmi = get_hotkey_entry_item(km, target_spec["idname"], target_spec.get("prop_name"))
        if kmi:
            km.keymap_items.remove(kmi)
        else:
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
