from bpy.types import (
    Operator,
    Context,
)
from ..constants import MODERN_PRIMITIVE_PREFIX
from typing import cast
from bpy.props import BoolProperty
import bpy
from ..aux_func import is_modern_primitive
from ..apply_scale import ApplyScale_Operator


class ConvertTo_BaseOperator(Operator):
    @classmethod
    @property
    def type_name(cls):
        return cls.type.name

    @classmethod
    @property
    def bl_idname(cls):
        return f"mesh.{MODERN_PRIMITIVE_PREFIX}_convert_to_{cls.type_name.lower()}"

    @classmethod
    @property
    def bl_label(cls):
        return f"Convert object to Modern{cls.type_name}"

    bl_options = {"REGISTER", "UNDO"}
    keep_original: BoolProperty(name="Keep Original", default=False)
    apply_scale: BoolProperty(name="Apply Scaling", default=True)

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        context = cast(Context, context)

        sel = context.selected_objects
        if len(sel) == 0:
            return False
        for obj in sel:
            if obj is None or obj.type != "MESH":
                return False
        return True

    def execute(self, context: Context | None) -> set[str]:
        sel = context.selected_objects.copy()
        for obj in sel:
            # bound_box update
            if is_modern_primitive(obj):
                bpy.ops.object.mode_set(mode="OBJECT")
            obj.data.update()

            new_obj = self._handle_proc(context, obj)
            new_obj.name = obj.name + "_converted"
            if self.apply_scale:
                bpy.ops.object.mpr_apply_scale(strict=False)

        if not self.keep_original:
            for obj in sel:
                bpy.data.objects.remove(obj)
        return {"FINISHED"}
