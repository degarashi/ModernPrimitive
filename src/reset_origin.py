from contextlib import suppress
from typing import ClassVar

from bpy.types import Context, Object, Operator
from bpy.utils import register_class, unregister_class
from mathutils import Vector

from .util.aux_func import get_mpr_modifier, get_selected_primitive
from .aux_math import MinMax
from .aux_node import get_interface_value
from .constants import MODERN_PRIMITIVE_PREFIX
from .primitive_prop import CornerRatio


class ResetOrigin_Operator(Operator):
    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_reset_origin"
    bl_label = "Reset origin to Pivot position"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        return len(get_selected_primitive(context)) > 0

    @classmethod
    def proc_obj(cls, obj: Object) -> None:
        box = MinMax.from_obj_bb(obj)

        # Pivot座標を取得
        mod = get_mpr_modifier(obj.modifiers)
        diff = Vector()
        with suppress(KeyError):
            pivot = Vector(val for val in get_interface_value(mod, CornerRatio.name))
            diff = pivot * (box.size / 2)

        center = box.average + diff
        obj.location = obj.matrix_world @ center

        mesh = obj.data
        offset = -center
        # Inverse offset vertices
        for v in mesh.vertices:
            v.co += offset
        mesh.update()

    def execute(self, context: Context | None) -> set[str]:
        sel = get_selected_primitive(context)
        cls = self.__class__
        for obj in sel:
            cls.proc_obj(obj)

        return {"FINISHED"}


def register() -> None:
    register_class(ResetOrigin_Operator)


def unregister() -> None:
    unregister_class(ResetOrigin_Operator)
