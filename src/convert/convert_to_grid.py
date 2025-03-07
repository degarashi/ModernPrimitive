from collections.abc import Sequence

import bpy.ops
from bpy.types import (
    Context,
    Object,
)
from mathutils import Vector

from .. import primitive_prop as prop
from ..aux_func import (
    get_object_just_added,
)
from ..aux_node import set_interface_values
from ..constants import Type
from .convert_to_baseop import BBox, ConvertTo_BaseOperator


class _ConvertToGrid_Operator(ConvertTo_BaseOperator):
    type = Type.Grid


class ConvertToGrid_Operator(_ConvertToGrid_Operator):
    """Make Modern Grid From Object"""

    B = _ConvertToGrid_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        # I just want the size on the XY plane, so I can use a bounding box

        bpy.ops.mesh.mpr_make_grid()
        grid = get_object_just_added(context)
        mod = grid.modifiers[0]
        set_interface_values(
            mod,
            context,
            (
                (prop.SizeX.name, bbox.size.x),
                (prop.SizeY.name, bbox.size.y),
            ),
        )
        return grid, Vector()
