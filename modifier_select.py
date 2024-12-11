import bpy
from typing import cast
from bpy.types import Context, Object, Operator, Modifier
from bpy.props import BoolProperty
from .constants import is_primitive_mod


class SelectModifier_Operator(Operator):
    bl_idname = "object.select_modernprimitive_modifier"
    bl_label = "Select ModernPrimitive Modifier"
    bl_options = {"REGISTER", "UNDO"}

    disable_others: BoolProperty(default=False)

    def execute(self, context: Context | None) -> set[str]:
        obj = context.view_layer.objects.active
        if obj is not None and obj.type == "MESH":
            obj = cast(Object, obj)
            select_modern_modifier(obj)
            if self.disable_others:
                disable_others(obj)
        return {"FINISHED"}




def select_modern_modifier(obj: Object) -> None:
    target: Modifier | None = None
    for mod in obj.modifiers:
        if is_primitive_mod(mod):
            target = mod
            break
    if target is not None:
        target.is_active = True


def disable_others(obj: Object) -> None:
    for mod in obj.modifiers:
        mod.show_viewport = is_primitive_mod(mod)


addon_keymaps = []


class KeyAssign:
    def __init__(
        self, idname: str, key: str, event: str, ctrl: bool, alt: bool, shift: bool
    ):
        self.idname = idname
        self.key = key
        self.event = event
        self.ctrl = ctrl
        self.alt = alt
        self.shift = shift

    def __getitem__(self, key: int):
        match key:
            case 0:
                return self.idname
            case 1:
                return self.key
            case 2:
                return self.event
            case 3:
                return self.ctrl
            case 4:
                return self.alt
            case 5:
                return self.shift
        raise IndexError


def register() -> None:
    bpy.utils.register_class(SelectModifier_Operator)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        KEY_ASSIGN_LIST: list[KeyAssign] = [
            KeyAssign(
                SelectModifier_Operator.bl_idname, "X", "PRESS", True, True, False
            ),
        ]
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        for idname, key, event, ctrl, alt, shift in KEY_ASSIGN_LIST:
            kmi = km.keymap_items.new(
                idname, key, event, ctrl=ctrl, alt=alt, shift=shift
            )
            addon_keymaps.append((km, kmi))


def unregister() -> None:
    bpy.utils.unregister_class(SelectModifier_Operator)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
