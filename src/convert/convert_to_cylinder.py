from collections.abc import Sequence
from math import pi as PI
from typing import TypeAlias

import bpy.ops
from bpy.types import Context, Object
from mathutils import Vector

from .. import primitive_prop as prop
from ..util.aux_func import (
    get_mpr_modifier,
    get_object_just_added,
)
from ..util.aux_node import set_interface_values
from ..constants import Type
from .common_type import SizeBase
from .convert_to_baseop import BBox, ConvertTo_BaseOperator, IndexConvOPT, vector_conv


class Size(SizeBase):
    radius: float
    height: float

    def __init__(self, sz: Vector):
        self.radius = (sz.x + sz.y) / 4
        self.height = sz.z

    @staticmethod
    def build(bbox: BBox, verts: Sequence[Vector], index_conv: IndexConvOPT):
        return Size(vector_conv(bbox.size, index_conv))

    def calc_size(self) -> Vector:
        f_size = self.radius * 2
        return Vector((f_size, f_size, self.height))

    def calc_volume(self) -> float:
        return self.radius**2 * PI * self.height


class _ConvertToCylinder_Operator(ConvertTo_BaseOperator):
    type = Type.Cylinder


class ConvertToCylinder_Operator(_ConvertToCylinder_Operator):
    """Make Modern Cylinder From Object"""

    B = _ConvertToCylinder_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()
    SizeType: TypeAlias = Size

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        size = Size.build(bbox, verts, None)

        bpy.ops.mesh.mpr_make_cylinder()
        cy = get_object_just_added(context)
        set_interface_values(
            get_mpr_modifier(cy.modifiers),
            context,
            (
                (prop.Radius.name, size.radius),
                (prop.Height.name, size.height),
            ),
        )
        return cy, Vector()
