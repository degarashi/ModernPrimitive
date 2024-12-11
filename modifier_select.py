import bpy
from typing import cast, Dict
from bpy.types import Context, Object, Operator, Modifier, ObjectModifiers
from bpy.props import BoolProperty
from .constants import is_primitive_mod, make_primitive_property_name


def save_other_modifier_state(mods: ObjectModifiers) -> Dict[str, bool]:
    # {"modifier-name": viewstate(bool), ...}
    ret: Dict[str, bool] = {}
    for mod in mods:
        if not is_primitive_mod(mod):
            ret[mod.name] = mod.show_viewport
    return ret


def restore_other_modifier_state(mods: ObjectModifiers, data: Dict[str, bool]) -> None:
    for mod in mods:
        if not is_primitive_mod(mod):
            if mod.name in data:
                mod.show_viewport = data[mod.name]


def is_other_modifier_state_valid(mods: ObjectModifiers, data: Dict[str, bool]) -> bool:
    if len(mods) != (len(data) + 1):
        return False
    found_pmod: bool = False
    for mod in mods:
        if is_primitive_mod(mod):
            found_pmod = True
        else:
            if mod.name not in data:
                return False
    return found_pmod


class SelectModifier_Operator(Operator):
    """
    focus to ModernPrimitive modifier only(save other modifier's state)
    if already focused, then restore other modifier's state
    """

    ENTRY_NAME = make_primitive_property_name("original_modifier_viewstate")

    bl_idname = "object.select_modernprimitive_modifier"
    bl_label = "Select ModernPrimitive Modifier"
    bl_options = {"REGISTER", "UNDO"}

    disable_others: BoolProperty(default=True)

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        obj = context.view_layer.objects.active
        return obj is not None and obj.type == "MESH"

    def _is_already_selected(self, obj: Object) -> bool:
        for mod in obj.modifiers:
            if is_primitive_mod(mod):
                if not mod.show_viewport or not mod.is_active:
                    return False
            else:
                if mod.show_viewport:
                    return False
        return True

    def _select_modifier(self, obj: Object) -> None:
        select_modern_modifier(obj.modifiers)
        if self.disable_others:
            # save other modifier's viewport state
            obj[self.__class__.ENTRY_NAME] = save_other_modifier_state(obj.modifiers)
            disable_other_mods(obj.modifiers)

    def _unselect_modifier(self, obj: Object) -> None:
        if self.disable_others:
            ENTRY_NAME = self.__class__.ENTRY_NAME
            if ENTRY_NAME in obj:
                entry = obj[ENTRY_NAME]
                if is_other_modifier_state_valid(obj.modifiers, entry):
                    restore_other_modifier_state(obj.modifiers, entry)
                del obj[ENTRY_NAME]

    def execute(self, context: Context | None) -> set[str]:
        obj = cast(Object, context.view_layer.objects.active)
        if self._is_already_selected(obj):
            self._unselect_modifier(obj)
        else:
            self._select_modifier(obj)
        return {"FINISHED"}


def find_modern_mod(mods: ObjectModifiers) -> Modifier | None:
    for mod in mods:
        if is_primitive_mod(mod):
            return mod
    return None


def select_modern_modifier(mods: ObjectModifiers) -> None:
    mod = find_modern_mod(mods)
    if mod is not None:
        mod.is_active = True


def disable_other_mods(mods: ObjectModifiers) -> None:
    for mod in mods:
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
