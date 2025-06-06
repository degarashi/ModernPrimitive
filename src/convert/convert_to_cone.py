from collections.abc import Sequence
from math import pi as PI
from typing import TypeAlias

import bpy.ops
from bpy.types import Context, Object
from mathutils import Vector

from .. import primitive_prop as prop
from ..util.aux_func import get_mpr_modifier, get_object_just_added
from ..aux_node import set_interface_values
from ..constants import MIN_RADIUS, Type
from .common_type import SizeBase
from .convert_to_baseop import BBox, ConvertTo_BaseOperator, IndexConvOPT, index_to_mat


class Size(SizeBase):
    top_r: float
    bottom_r: float
    height: float

    def __init__(self, bb_size: Vector, bb_center: Vector, verts: Sequence[Vector]):
        # Divide into upper half and lower half in the z-axis direction
        top_r: float = MIN_RADIUS
        bottom_r: float = MIN_RADIUS

        for v in verts:
            if v.z >= bb_center.z:
                # Get the top half vertices
                #   and find out how far they are from the center
                top_r = max(top_r, (v.xy - bb_center.xy).length)
            else:
                # Get the vertices in the bottom half
                #   and find out how far they are from the center
                bottom_r = max(bottom_r, (v.xy - bb_center.xy).length)
        self.top_r = top_r
        self.bottom_r = bottom_r
        self.height = bb_size.z

    @staticmethod
    def build(bbox: BBox, verts: Sequence[Vector], index_conv: IndexConvOPT):
        # TODO: Inefficient implementation, so I'll do something later
        mat = index_to_mat(index_conv)
        verts = tuple(mat @ v for v in verts)
        bbox = BBox(verts)
        return Size(bbox.size, bbox.center, verts)

    def calc_size(self) -> Vector:
        f_size = max(self.top_r, self.bottom_r) * 2
        return Vector((f_size, f_size, self.height))

    def calc_volume(self) -> float:
        return (
            PI
            * self.height
            * ((self.bottom_r**2) + self.bottom_r * self.top_r + (self.top_r**2))
            / 3
        )


class _ConvertToCone_Operator(ConvertTo_BaseOperator):
    type = Type.Cone


class ConvertToCone_Operator(_ConvertToCone_Operator):
    """Make Modern Cone From Object"""

    B = _ConvertToCone_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()
    SizeType: TypeAlias = Size

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        size = Size.build(bbox, verts, None)

        bpy.ops.mesh.mpr_make_cone()
        cone = get_object_just_added(context)
        set_interface_values(
            get_mpr_modifier(cone.modifiers),
            context,
            (
                (prop.TopRadius.name, size.top_r),
                (prop.BottomRadius.name, size.bottom_r),
                (prop.Height.name, size.height),
            ),
        )
        return cone, Vector()
