from typing import ClassVar

import bmesh
import bpy.utils
from bpy.types import Context, Object, Operator
from mathutils import Vector

from .aux_func import is_modern_primitive_specific, is_mpr_enabled
from .aux_math import MinMax
from .aux_node import get_interface_value, set_interface_value
from .constants import MODERN_PRIMITIVE_PREFIX, Type
from .primitive_prop import get_max, get_min


class Equalize_DCube_Operator(Operator):
    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_dcube_origin_center"
    bl_label = "Set DeformableCube Origin to Center"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if len(context.selected_objects) == 0:
            return False
        for obj in context.selected_objects:
            if not is_modern_primitive_specific(obj, Type.DeformableCube) or not is_mpr_enabled(
                obj.modifiers
            ):
                return False
        return True

    @staticmethod
    def _make_single_vertex(context: Context, obj: Object, pos: Vector) -> None:
        """Replaces the meshes that an object has at a single vertex with specified coordinates"""
        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        mesh = bmesh.from_edit_mesh(obj.data)
        bmesh.ops.delete(mesh, geom=mesh.verts[:], context="VERTS")
        mesh.verts.new(pos)
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode="OBJECT")

    @staticmethod
    def _make_centered(obj: Object, context: Context) -> None:
        bb = MinMax.from_obj_bb(obj)

        # Equalize the modifier values
        mod = obj.modifiers[0]
        for i in range(3):
            min_name = get_min(i).name
            max_name = get_max(i).name
            # min = minus-value
            min_v = get_interface_value(mod, min_name)
            max_v = get_interface_value(mod, max_name)
            width = (min_v + max_v) / 2
            set_interface_value(mod, (min_name, width))
            set_interface_value(mod, (max_name, width))

        mod.node_group.interface_update(context)
        __class__._make_single_vertex(context, obj, bb.average)

    def execute(self, context: Context | None) -> set[str]:
        # preserve active object
        act_obj = context.active_object
        for obj in context.selected_objects:
            self._make_centered(obj, context)
        # restore active obejct
        context.view_layer.objects.active = act_obj
        return {"FINISHED"}


MENU_TARGET = bpy.types.VIEW3D_MT_object


def menu_func(self, context: Context) -> None:
    layout = self.layout
    layout.operator(Equalize_DCube_Operator.bl_idname, icon="CUBE")


def register() -> None:
    bpy.utils.register_class(Equalize_DCube_Operator)
    MENU_TARGET.append(menu_func)


def unregister() -> None:
    bpy.utils.unregister_class(Equalize_DCube_Operator)
    MENU_TARGET.remove(menu_func)
