from collections.abc import Sequence
from math import pi as PI
from typing import TypeAlias

import bpy.ops
from bpy.props import EnumProperty
from bpy.types import (
    Context,
    Object,
)
from mathutils import Vector

from .. import primitive_prop as prop
from ..aux_func import get_mpr_modifier, get_object_just_added
from ..aux_node import set_interface_values
from .common_type import SizeBase
from .convert_to_baseop import BBox, ConvertTo_BaseOperator, IndexConvOPT, vector_conv


class Size(SizeBase):
    radius: float

    def __init__(self, sz: Vector):
        self.radius = max(sz.x, sz.y, sz.z) / 2

    @staticmethod
    def build(bbox: BBox, verts: Sequence[Vector], index_conv: IndexConvOPT):
        return Size(vector_conv(bbox.size, index_conv))

    def calc_size(self) -> Vector:
        r2 = self.radius * 2
        return Vector((r2, r2, r2))

    def calc_volume(self) -> float:
        return (4.0 / 3.0) * PI * self.radius**3


class _ConvertToSphere_Operator(ConvertTo_BaseOperator):
    @classmethod
    def get_bl_idname(cls) -> str:
        return "mesh.mpr_convert_to_sphere"

    @classmethod
    def get_bl_label(cls) -> str:
        return "Convert object to Modern Sphere"


class ConvertToSphere_Operator(_ConvertToSphere_Operator):
    """Make Modern UVSphere From Object"""

    B = _ConvertToSphere_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()
    SizeType: TypeAlias = Size

    sphere_type: EnumProperty(
        name="Sphere Type",
        default="UVSphere",
        items=(
            ("UVSphere", "UV Sphere", ""),
            ("ICOSphere", "ICO Sphere", ""),
            ("QuadSphere", "Quad Sphere", ""),
        ),
    )

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        size = Size.build(bbox, verts, None)

        match self.sphere_type:
            case "UVSphere":
                bpy.ops.mesh.mpr_make_uvsphere()
            case "ICOSphere":
                bpy.ops.mesh.mpr_make_icosphere()
            case "QuadSphere":
                bpy.ops.mesh.mpr_make_quadsphere()

        sphere = get_object_just_added(context)

        # I just want the size of Bounding box.
        #   so there is no need to read vertices
        mod = get_mpr_modifier(sphere.modifiers)
        set_interface_values(
            mod,
            context,
            ((prop.Radius.name, size.radius),),
        )
        return sphere, Vector()
