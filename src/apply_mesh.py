from typing import ClassVar

import bpy
from bpy.types import Context, Object, Operator
from bpy.utils import register_class, unregister_class

from .aux_func import disable_modifier, get_selected_primitive, is_mpr_enabled
from .constants import MODERN_PRIMITIVE_PREFIX


class ApplyMesh_Operator(Operator):
    """
    Apply MPR modifier to mesh and disable modifier
    """

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_apply_mesh"
    bl_label = "Apply MPR-Geometry node to Mesh"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        return len(get_selected_primitive(context)) > 0

    @staticmethod
    def __apply_mesh(obj: Object, context: Context) -> bool:
        if not is_mpr_enabled(obj.modifiers):
            return False
        new_obj = obj.copy()

        # Copy only modifier 0 (MPR)
        for i in range(len(new_obj.modifiers)-1, 0, -1):
            new_obj.modifiers.remove(new_obj.modifiers[i])

        context.collection.objects.link(new_obj)

        deps = context.evaluated_depsgraph_get()
        eval_obj = new_obj.evaluated_get(deps)
        mesh = bpy.data.meshes.new_from_object(eval_obj)

        mesh_name = obj.data.name
        obj.data.name = f"__to_delete_{obj.name}"
        mesh.name = mesh_name
        obj.data = mesh

        mpr_mod = obj.modifiers[0]
        disable_modifier(mpr_mod)
        bpy.data.objects.remove(new_obj)
        return True

    def execute(self, context: Context | None) -> set[str]:
        sel = get_selected_primitive(context)
        apply_count = 0
        for obj in sel:
            apply_count += 1 if self.__class__.__apply_mesh(obj, context) else 0
        apply_count_str = str(apply_count) if apply_count > 0 else "no"
        self.report(
            {"INFO"}, f"Apply MPR-Modifier to Mesh: {apply_count_str} object(s) applied."
        )

        return {"FINISHED"}


def register() -> None:
    register_class(ApplyMesh_Operator)


def unregister() -> None:
    unregister_class(ApplyMesh_Operator)
