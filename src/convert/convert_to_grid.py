from collections.abc import Sequence
from typing import TypeAlias

import bpy.ops
from bpy.types import (
    Context,
    Object,
)
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

GRID_THICKNESS = 1e-8


class Size(SizeBase):
    width: float
    height: float

    def __init__(self, sz: Vector):
        self.width = sz.x
        self.height = sz.y

    @staticmethod
    def build(bbox: BBox, verts: Sequence[Vector], index_conv: IndexConvOPT):
        return Size(vector_conv(bbox.size, index_conv))

    def calc_size(self) -> Vector:
        return Vector((self.width, self.height, GRID_THICKNESS))

    def calc_volume(self) -> float:
        return self.width * self.height * GRID_THICKNESS


class _ConvertToGrid_Operator(ConvertTo_BaseOperator):
    type = Type.Grid


class ConvertToGrid_Operator(_ConvertToGrid_Operator):
    """Make Modern Grid From Object"""

    B = _ConvertToGrid_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()
    SizeType: TypeAlias = Size

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        # I just want the size on the XY plane, so I can use a bounding box
        size = Size.build(bbox, verts, None)

        bpy.ops.mesh.mpr_make_grid()
        grid = get_object_just_added(context)
        mod = get_mpr_modifier(grid.modifiers)
        set_interface_values(
            mod,
            context,
            (
                (prop.SizeX.name, size.width),
                (prop.SizeY.name, size.height),
            ),
        )
        return grid, Vector()
