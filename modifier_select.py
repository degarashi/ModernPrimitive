import bpy
from typing import cast
from bpy.types import Context, Object, Operator, Modifier
from .constants import MODERN_PRIMITIVE_TAG


class SelectModifier_Operator(Operator):
    bl_idname = "object.select_modernprimitive_modifier"
    bl_label = "Select ModernPrimitive Modifier"

    def execute(self, context: Context | None) -> set[str]:
        obj = context.view_layer.objects.active
        if obj is not None:
            select_modern_modifier(obj)
        return {"FINISHED"}


def select_modern_modifier(obj: Object) -> None:
    if obj is not None and obj.type == "MESH":
        obj = cast(Object, obj)
        target: Modifier | None = None
        for mod in obj.modifiers:
            if mod.name.startswith(MODERN_PRIMITIVE_TAG):
                target = mod
                break
        if target is not None:
            target.is_active = True


def register() -> None:
    bpy.utils.register_class(SelectModifier_Operator)


def unregister() -> None:
    bpy.utils.unregister_class(SelectModifier_Operator)
