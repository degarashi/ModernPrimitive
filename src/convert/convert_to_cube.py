import bpy.ops
from bpy.types import (
    Object,
    Context,
)
from .convert_to_baseop import ConvertTo_BaseOperator, BBox
from ..aux_func import (
    get_object_just_added,
)
from bpy.props import EnumProperty
from ..aux_node import set_interface_values
from .. import primitive_prop as prop
from ..constants import Type


class _ConvertToCube_Operator(ConvertTo_BaseOperator):
    type = Type.Cube


class ConvertToCube_Operator(_ConvertToCube_Operator):
    """Make Modern Cube From Object"""

    B = _ConvertToCube_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    cube_type: EnumProperty(
        name="Cube Type",
        default="Cube",
        items=[
            ("Cube", "Cube", "Make Normal Cube"),
            ("DeformableCube", "Deformable Cube", "Make Deformable Cube"),
        ],
    )

    def _handle_proc(self, context: Context, obj: Object, bbox: BBox) -> Object:
        if self.cube_type == "Cube":
            bpy.ops.mesh.mpr_make_cube()
        else:
            bpy.ops.mesh.mpr_make_deformablecube()

        cube = get_object_just_added(context)
        cube.matrix_world = obj.matrix_world

        if self.cube_type == "Cube":
            set_interface_values(
                cube.modifiers[0],
                context,
                (
                    (prop.SizeX.name, bbox.size.x / 2),
                    (prop.SizeY.name, bbox.size.y / 2),
                    (prop.SizeZ.name, bbox.size.z / 2),
                ),
            )
            cube.location = obj.matrix_world @ bbox.center
        else:
            set_interface_values(
                cube.modifiers[0],
                context,
                (
                    (prop.MinX.name, -bbox.min.x),
                    (prop.MaxX.name, bbox.max.x),
                    (prop.MinY.name, -bbox.min.y),
                    (prop.MaxY.name, bbox.max.y),
                    (prop.MinZ.name, -bbox.min.z),
                    (prop.MaxZ.name, bbox.max.z),
                ),
            )
        return cube


MENU_TARGET = bpy.types.VIEW3D_MT_object_convert


def menu_func(self, context: Context) -> None:
    layout = self.layout
    layout.operator(ConvertToCube_Operator.bl_idname, text="Modern Cube", icon="CUBE")


def register() -> None:
    MENU_TARGET.append(menu_func)


def unregister() -> None:
    MENU_TARGET.remove(menu_func)
