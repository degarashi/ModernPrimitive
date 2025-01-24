import bpy
from bpy.types import (
    Object,
    Operator,
    Context,
)
from typing import cast
from ..aux_func import (
    get_bound_box,
    get_object_just_added,
    is_modern_primitive,
)
from bpy.props import BoolProperty, EnumProperty
from ..aux_node import set_interface_values
from ..constants import MODERN_PRIMITIVE_PREFIX
from .. import primitive_prop as prop


class ConvertToCube_Operator(Operator):
    """Make Modern Cube From Object"""

    bl_idname = f"mesh.{MODERN_PRIMITIVE_PREFIX}_convert_to_cube"
    bl_label = "Convert object to ModernCube"
    bl_options = {"REGISTER", "UNDO"}

    keep_original: BoolProperty(name="Keep Original", default=False)
    cube_type: EnumProperty(
        name="Cube Type",
        default="Cube",
        items=[
            ("Cube", "Cube", "Make Normal Cube"),
            ("DeformableCube", "Deformable Cube", "Make Deformable Cube"),
        ],
    )

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

    def _make_cube(self, context: Context, from_obj: Object) -> None:
        # bound_box update
        if is_modern_primitive(from_obj):
            bpy.ops.object.mode_set(mode="OBJECT")
        from_obj.data.update()
        (b_min, b_max) = get_bound_box(from_obj.bound_box)
        center = (b_min + b_max) / 2

        if self.cube_type == "Cube":
            bpy.ops.mesh.mpr_make_cube()
        else:
            bpy.ops.mesh.mpr_make_deformablecube()

        cube = get_object_just_added(context)
        cube.matrix_world = from_obj.matrix_world

        if self.cube_type == "Cube":
            set_interface_values(
                cube.modifiers[0],
                context,
                (
                    (prop.SizeX.name, (b_max.x - b_min.x) / 2),
                    (prop.SizeY.name, (b_max.y - b_min.y) / 2),
                    (prop.SizeZ.name, (b_max.z - b_min.z) / 2),
                ),
            )
            cube.location = from_obj.matrix_world @ center
        else:
            set_interface_values(
                cube.modifiers[0],
                context,
                (
                    (prop.MinX.name, -b_min.x),
                    (prop.MaxX.name, b_max.x),
                    (prop.MinY.name, -b_min.y),
                    (prop.MaxY.name, b_max.y),
                    (prop.MinZ.name, -b_min.z),
                    (prop.MaxZ.name, b_max.z),
                ),
            )
        cube.name = from_obj.name + "_converted"

    def execute(self, context: Context | None) -> set[str]:
        sel = context.selected_objects.copy()
        for obj in sel:
            self._make_cube(context, obj)
        if not self.keep_original:
            for obj in sel:
                bpy.data.objects.remove(obj)
        return {"FINISHED"}


MENU_TARGET = bpy.types.VIEW3D_MT_object_convert


def menu_func(self, context: Context) -> None:
    layout = self.layout
    layout.operator(ConvertToCube_Operator.bl_idname, text="Modern Cube", icon="CUBE")


def register() -> None:
    bpy.utils.register_class(ConvertToCube_Operator)
    MENU_TARGET.append(menu_func)


def unregister() -> None:
    MENU_TARGET.remove(menu_func)
    bpy.utils.unregister_class(ConvertToCube_Operator)
