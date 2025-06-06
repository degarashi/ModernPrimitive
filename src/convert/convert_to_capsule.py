from collections.abc import Sequence
from math import pi as PI
from typing import TypeAlias

import bpy.ops
from bpy.types import Context, Object
from mathutils import Vector

from .. import primitive_prop as prop
from ..util.aux_func import get_mpr_modifier, get_object_just_added
from ..aux_node import set_interface_values
from ..constants import MIN_RADIUS, MIN_SIZE, Type
from .common_type import SizeBase
from .convert_to_baseop import (
    BBox,
    ConvertTo_BaseOperator,
    IndexConvOPT,
    vector_conv,
)


class Size(SizeBase):
    radius: float
    height: float  # The height of the cylinder part

    def __init__(self, sz: Vector):
        self.radius = max(MIN_RADIUS, (sz.x + sz.y) / 4)
        self.height = max(MIN_SIZE, sz.z - self.radius * 2)

    @staticmethod
    def build(bbox: BBox, verts: Sequence[Vector], index_conv: IndexConvOPT):
        return Size(vector_conv(bbox.size, index_conv))

    def calc_size(self) -> Vector:
        return Vector(
            (
                self.radius * 2,
                self.radius * 2,
                self.height + self.radius * 2,
            )
        )

    def calc_volume(self) -> float:
        return (4.0 / 3.0) * PI * self.radius**3 + (self.radius**2 * PI * self.height)


class _ConvertToCapsule_Operator(ConvertTo_BaseOperator):
    type = Type.Capsule


class ConvertToCapsule_Operator(_ConvertToCapsule_Operator):
    """Make Modern Capsule From Object"""

    B = _ConvertToCapsule_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()
    SizeType: TypeAlias = Size

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        size = Size.build(bbox, verts, None)

        bpy.ops.mesh.mpr_make_capsule()
        capsule = get_object_just_added(context)
        set_interface_values(
            get_mpr_modifier(capsule.modifiers),
            context,
            (
                (prop.Radius.name, size.radius),
                (prop.Height.name, size.height),
            ),
        )
        return capsule, Vector()
