from typing import ClassVar

import bpy
from bpy.types import Context, Object, Operator
from bpy.utils import register_class, unregister_class

from .constants import MODERN_PRIMITIVE_PREFIX
from .util.aux_func import (
    disable_modifier,
    get_mpr_modifier,
    get_selected_primitive,
    is_mpr_enabled,
)


class ApplyMesh_Base(Operator):
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        if context is None:
            return False
        return len(get_selected_primitive(context)) > 0

    def execute(self, context: Context) -> set[str]:
        sel = get_selected_primitive(context)
        apply_count = 0
        for obj in sel:
            apply_count += 1 if self._apply_mesh(obj, context) else 0
        apply_count_str = str(apply_count) if apply_count > 0 else "no"
        self.report(
            {"INFO"}, f"Apply MPR-Modifier to Mesh: {apply_count_str} object(s) applied."
        )

        return {"FINISHED"}


class ApplyMesh_Operator(ApplyMesh_Base):
    """
    Apply MPR modifier to mesh and disable modifier
    """

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_apply_mesh"
    bl_label = "Apply MPR-Geometry node to Mesh"

    def _apply_mesh(self, obj: Object, context: Context) -> bool:
        # Check if the MPR modifier is enabled on the object
        if not is_mpr_enabled(obj.modifiers):
            return False

        tmp_obj = obj.copy()

        # Copy only modifier 0 (MPR)
        for i in range(len(tmp_obj.modifiers) - 1, 0, -1):
            tmp_obj.modifiers.remove(tmp_obj.modifiers[i])

        context.collection.objects.link(tmp_obj)

        deps = context.evaluated_depsgraph_get()
        eval_obj = tmp_obj.evaluated_get(deps)
        mesh = bpy.data.meshes.new_from_object(eval_obj)

        mesh_name = obj.data.name
        obj.data.name = f"__to_delete_{obj.name}"
        mesh.name = mesh_name
        obj.data = mesh

        mpr_mod = get_mpr_modifier(obj.modifiers)
        disable_modifier(mpr_mod)
        bpy.data.objects.remove(tmp_obj)
        return True


class ApplyAndRemoveMesh_Operator(ApplyMesh_Base):
    """
    Apply MPR modifier to mesh and remove modifier
    """

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_apply_and_remove_mesh"
    bl_label = "Apply and Remove MPR-Geometry node"

    def _apply_mesh(self, obj: Object, context: Context) -> bool:
        if not is_mpr_enabled(obj.modifiers):
            return False

        mpr_mod = get_mpr_modifier(obj.modifiers)
        if not mpr_mod:
            return False

        original_active = context.view_layer.objects.active
        context.view_layer.objects.active = obj

        try:
            bpy.ops.object.modifier_apply(modifier=mpr_mod.name)
            return True
        except Exception as e:
            self.report({"INFO"}, f"Failed to apply modifier: {e}")
            return False
        finally:
            context.view_layer.objects.active = original_active


def register() -> None:
    register_class(ApplyMesh_Operator)
    register_class(ApplyAndRemoveMesh_Operator)


def unregister() -> None:
    unregister_class(ApplyMesh_Operator)
    unregister_class(ApplyAndRemoveMesh_Operator)
