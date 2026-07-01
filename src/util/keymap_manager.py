import contextlib
import bpy


class KeymapManager:
    """Manages keymap registration, unregistration, and lookup for Blender addons."""

    def __init__(self, hotkey_defs):
        self.hotkey_defs = hotkey_defs
        self.addon_keymaps = []

    def get_hotkey_entry_item(self, km, kmi_name, kmi_value, handled_kmi):
        """Finds and returns a specific KeyMapItem by its idname and optional property name."""
        for km_item in km.keymap_items:
            if km_item in handled_kmi:
                continue
            if km_item.idname == kmi_name and (
                kmi_value is None or (
                    "name" in km_item.properties and km_item.properties.name == kmi_value
                )
            ):
                return km_item
        return None

    def register(self, keymap_name="3D View", space_type="VIEW_3D"):
        """Registers all hotkeys defined in hotkey_defs."""
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if not kc:
            return

        km = kc.keymaps.new(name=keymap_name, space_type=space_type)

        for spec in self.hotkey_defs:
            kmi = km.keymap_items.new(
                spec["idname"],
                spec["type"],
                "PRESS",
                ctrl=spec.get("ctrl", False),
                shift=spec.get("shift", False),
                alt=spec.get("alt", False)
            )
            properties = spec.get("properties")
            if properties:
                for key, val in properties.items():
                    setattr(kmi.properties, key, val)
            self.addon_keymaps.append((km, kmi))

    def unregister(self):
        """Unregisters all added hotkeys."""
        for km, kmi in self.addon_keymaps:
            with contextlib.suppress(Exception):
                km.keymap_items.remove(kmi)
        self.addon_keymaps.clear()
