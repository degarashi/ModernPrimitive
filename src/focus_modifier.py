from typing import ClassVar, NamedTuple, cast

import bpy
from bpy.props import BoolProperty
from bpy.types import (
    Context,
    KeyMap,
    KeyMapItem,
    Modifier,
    Object,
    ObjectModifiers,
    Operator,
)

from .aux_func import (
    is_modern_primitive,
    is_primitive_mod,
    make_primitive_property_name,
    is_mpr_enabled,
)
from .constants import MODERN_PRIMITIVE_PREFIX
from .key import KeyAssign
from .modern_primitive import VIEW3D_MT_mesh_modern_prim


def save_other_modifier_state(mods: ObjectModifiers) -> dict[str, bool]:
    # {"modifier-name": viewstate(bool), ...}
    ret: dict[str, bool] = {}
    for mod in mods:
        if not is_primitive_mod(mod):
            ret[mod.name] = mod.show_viewport
    return ret


def restore_other_modifier_state(mods: ObjectModifiers, data: dict[str, bool]) -> None:
    for mod in mods:
        if not is_primitive_mod(mod) and mod.name in data:
            mod.show_viewport = data[mod.name]


def is_other_modifier_state_valid(mods: ObjectModifiers, data: dict[str, bool]) -> bool:
    if len(mods) != (len(data) + 1):
        return False
    found_pmod: bool = False
    for mod in mods:
        if is_primitive_mod(mod):
            found_pmod = True
        elif mod.name not in data:
            return False
    return found_pmod


class FocusModifier_Operator(Operator):
    """
    focus to ModernPrimitive modifier only(save other modifier's state)
    if already focused, then restore other modifier's state
    """

    ENTRY_NAME = make_primitive_property_name("original_modifier_viewstate")

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_focus_modifier"
    bl_label = "Focus/Unfocus ModernPrimitive Modifier"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    disable_others: BoolProperty(name="Disable Others", default=True)

    @staticmethod
    def _can_process(obj: Object) -> bool:
        return is_mpr_enabled(obj.modifiers)

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        obj = context.view_layer.objects.active
        return obj is not None and is_modern_primitive(obj) and cls._can_process(obj)

    def _is_already_focused(self, obj: Object) -> bool:
        for mod in obj.modifiers:
            if is_primitive_mod(mod):
                if not mod.show_viewport or not mod.is_active:
                    return False
            elif mod.show_viewport:
                return False
        return True

    def _focus_modifier(self, obj: Object) -> None:
        focus_modern_modifier(obj.modifiers)
        if self.disable_others:
            # save other modifier's viewport state
            obj[self.__class__.ENTRY_NAME] = save_other_modifier_state(obj.modifiers)
            disable_other_mods(obj.modifiers)

    def _unfocus_modifier(self, obj: Object) -> None:
        if self.disable_others:
            ENTRY_NAME = self.__class__.ENTRY_NAME
            if ENTRY_NAME in obj:
                entry = obj[ENTRY_NAME]
                if is_other_modifier_state_valid(obj.modifiers, entry):
                    restore_other_modifier_state(obj.modifiers, entry)
                del obj[ENTRY_NAME]

    def execute(self, context: Context | None) -> set[str]:
        obj = cast(Object, context.view_layer.objects.active)
        if self._is_already_focused(obj):
            self._unfocus_modifier(obj)
        else:
            self._focus_modifier(obj)
        return {"FINISHED"}


def find_modern_mod(mods: ObjectModifiers) -> Modifier | None:
    for mod in mods:
        if is_primitive_mod(mod):
            return mod
    return None


def focus_modern_modifier(mods: ObjectModifiers) -> None:
    mod = find_modern_mod(mods)
    if mod is not None:
        mod.is_active = True


def disable_other_mods(mods: ObjectModifiers) -> None:
    for mod in mods:
        mod.show_viewport = is_primitive_mod(mod)


addon_keymaps: list[tuple[KeyMap, KeyMapItem]] = []


def menu_func(self, context: Context) -> None:
    layout = self.layout

    OPS = FocusModifier_Operator
    op = layout.operator(OPS.bl_idname, text=OPS.bl_label)
    op.disable_others = True
    layout.separator()


MENU_TARGET = bpy.types.VIEW3D_MT_select_object


class KeymapAt(NamedTuple):
    name: str
    space_type: str


KEY_ASSIGN_MAP: dict[KeymapAt, list[KeyAssign]] = {
    KeymapAt("3D View", "VIEW_3D"): [
        KeyAssign(
            FocusModifier_Operator.bl_idname,
            "X",
            "PRESS",
            True,
            True,
            False,
        ),
        KeyAssign(
            "wm.call_menu",
            "M",
            "PRESS",
            True,
            False,
            True,
            prop={"name": VIEW3D_MT_mesh_modern_prim.bl_idname},
        ),
    ]
}


def register() -> None:
    bpy.utils.register_class(FocusModifier_Operator)
    MENU_TARGET.append(menu_func)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        for at, as_l in KEY_ASSIGN_MAP.items():
            km = kc.keymaps.new(name=at.name, space_type=at.space_type)
            for a in as_l:
                kmi = a.register(km)
                addon_keymaps.append((km, kmi))


def unregister() -> None:
    bpy.utils.unregister_class(FocusModifier_Operator)
    MENU_TARGET.remove(menu_func)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
