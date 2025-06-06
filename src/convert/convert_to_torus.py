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
from ..aux_node import set_interface_values
from ..constants import MIN_RADIUS, Type
from .common_type import SizeBase
from .convert_to_baseop import BBox, ConvertTo_BaseOperator, IndexConvOPT, vector_conv


class Size(SizeBase):
    ring_radius: float
    radius: float

    def __init__(self, sz: Vector):
        self.ring_radius = max(MIN_RADIUS, sz.z / 2)
        self.radius = max(MIN_RADIUS, (sz.x + sz.y) / 4 - self.ring_radius)

    @staticmethod
    def build(bbox: BBox, verts: Sequence[Vector], index_conv: IndexConvOPT):
        return Size(vector_conv(bbox.size, index_conv))

    def calc_size(self) -> Vector:
        f_size = (self.radius + self.ring_radius) * 2
        return Vector((f_size, f_size, self.ring_radius * 2))

    def calc_volume(self) -> float:
        return 2 * PI**2 * self.radius * self.ring_radius


class _ConvertToTorus_Operator(ConvertTo_BaseOperator):
    type = Type.Torus


class ConvertToTorus_Operator(_ConvertToTorus_Operator):
    """Make Modern Torus From Object"""

    B = _ConvertToTorus_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()
    SizeType: TypeAlias = Size

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        size = Size.build(bbox, verts, None)

        bpy.ops.mesh.mpr_make_torus()
        torus = get_object_just_added(context)
        set_interface_values(
            get_mpr_modifier(torus.modifiers),
            context,
            (
                (prop.RingRadius.name, size.ring_radius),
                (prop.Radius.name, size.radius),
            ),
        )
        return torus, Vector()
