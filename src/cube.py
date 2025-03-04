import bpy.utils
from bpy.types import Context, Object, Operator
from mathutils import Vector

from .aux_func import is_modern_primitive_specific
from .aux_node import get_interface_value, set_interface_value
from .constants import MODERN_PRIMITIVE_PREFIX, Type
from .primitive_prop import get_max, get_min


class DCube_CenterOrigin_Operator(Operator):
    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_dcube_origin_center"
    bl_label = "Set DeformableCube Origin to Center"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if len(context.selected_objects) == 0:
            return False
        for obj in context.selected_objects:
            if not is_modern_primitive_specific(obj, Type.DeformableCube):
                return False
        return True

    @staticmethod
    def _make_centered(obj: Object, context: Context) -> None:
        # use no mesh data (modifier only)

        mod = obj.modifiers[0]
        center = Vector()
        for i in range(3):
            min_name = get_min(i).name
            max_name = get_max(i).name
            # min = minus-value
            min_v = get_interface_value(mod, min_name)
            max_v = get_interface_value(mod, max_name)
            center[i] = (-min_v + max_v) / 2
            width = (min_v + max_v) / 2
            set_interface_value(mod, (min_name, width))
            set_interface_value(mod, (max_name, width))
        center = obj.matrix_world @ center

        node_group = mod.node_group
        node_group.interface_update(context)
        obj.location = center

    def execute(self, context: Context | None) -> set[str]:
        for obj in context.selected_objects:
            self._make_centered(obj, context)
        return {"FINISHED"}


MENU_TARGET = bpy.types.VIEW3D_MT_object


def menu_func(self, context: Context) -> None:
    layout = self.layout
    layout.operator(DCube_CenterOrigin_Operator.bl_idname, icon="CUBE")


def register() -> None:
    bpy.utils.register_class(DCube_CenterOrigin_Operator)
    MENU_TARGET.append(menu_func)


def unregister() -> None:
    bpy.utils.unregister_class(DCube_CenterOrigin_Operator)
    MENU_TARGET.remove(menu_func)
