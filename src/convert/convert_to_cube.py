from collections.abc import Sequence

import bpy.ops
from bpy.props import EnumProperty
from bpy.types import (
    Context,
    Object,
)
from mathutils import Vector

from .. import primitive_prop as prop
from ..aux_func import (
    get_mpr_modifier,
    get_object_just_added,
)
from ..aux_node import set_interface_values
from ..constants import Type
from .convert_to_baseop import BBox, ConvertTo_BaseOperator


class _ConvertToCube_Operator(ConvertTo_BaseOperator):
    type = Type.Cube


class ConvertToCube_Operator(_ConvertToCube_Operator):
    """Make Modern Cube From Object"""

    B = _ConvertToCube_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()

    cube_type: EnumProperty(
        name="Cube Type",
        default="Cube",
        items=[
            ("Cube", "Cube", "Make Normal Cube"),
            ("DeformableCube", "Deformable Cube", "Make Deformable Cube"),
        ],
    )

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        if self.cube_type == "Cube":
            bpy.ops.mesh.mpr_make_cube()
        else:
            bpy.ops.mesh.mpr_make_deformablecube()

        cube = get_object_just_added(context)
        if self.cube_type == "Cube":
            set_interface_values(
                get_mpr_modifier(cube.modifiers),
                context,
                (
                    (prop.Size.name, bbox.size),
                ),
            )
        else:
            set_interface_values(
                get_mpr_modifier(cube.modifiers),
                context,
                (
                    (prop.MinX.name, bbox.size.x / 2),
                    (prop.MaxX.name, bbox.size.x / 2),
                    (prop.MinY.name, bbox.size.y / 2),
                    (prop.MaxY.name, bbox.size.y / 2),
                    (prop.MinZ.name, bbox.size.z / 2),
                    (prop.MaxZ.name, bbox.size.z / 2),
                ),
            )
        return cube, Vector()


MENU_TARGET = bpy.types.VIEW3D_MT_object_convert


def menu_func(self, context: Context) -> None:
    layout = self.layout
    layout.operator(ConvertToCube_Operator.bl_idname, text="Modern Cube", icon="CUBE")


def register() -> None:
    MENU_TARGET.append(menu_func)


def unregister() -> None:
    MENU_TARGET.remove(menu_func)
