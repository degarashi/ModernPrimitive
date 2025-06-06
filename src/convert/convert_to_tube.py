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
from ..constants import MIN_RADIUS, MIN_SIZE, Type
from .common_type import SizeBase
from .convert_to_baseop import BBox, ConvertTo_BaseOperator, IndexConvOPT, vector_conv


class Size(SizeBase):
    height: float
    outer_radius: float
    inner_radius: float

    def __init__(self, sz: Vector):
        self.height = max(MIN_SIZE, sz.z)
        self.outer_radius = max(MIN_RADIUS, (sz.x + sz.y) / 4)
        self.inner_radius = self.outer_radius / 2

    @staticmethod
    def build(bbox: BBox, verts: Sequence[Vector], index_conv: IndexConvOPT):
        return Size(vector_conv(bbox.size, index_conv))

    def calc_size(self) -> Vector:
        f_size = self.outer_radius * 2
        return Vector((f_size, f_size, self.height))

    def calc_volume(self) -> float:
        return (self.outer_radius**2 - self.inner_radius**2) * PI * self.height


class _ConvertToTube_Operator(ConvertTo_BaseOperator):
    type = Type.Tube


class ConvertToTube_Operator(_ConvertToTube_Operator):
    """Make Modern Tube From Object"""

    B = _ConvertToTube_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()
    SizeType: TypeAlias = Size

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        size = Size.build(bbox, verts, None)

        bpy.ops.mesh.mpr_make_tube()
        tube = get_object_just_added(context)
        set_interface_values(
            get_mpr_modifier(tube.modifiers),
            context,
            (
                (prop.Height.name, size.height),
                (prop.OuterRadius.name, size.outer_radius),
                (prop.InnerRadius.name, size.inner_radius),
            ),
        )
        return tube, Vector()
