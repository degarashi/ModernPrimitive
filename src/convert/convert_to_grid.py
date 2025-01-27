from bpy.types import (
    Context,
    Object,
)
from .convert_to_baseop import ConvertTo_BaseOperator, BBox
import bpy.ops
from ..aux_func import (
    get_object_just_added,
)
from ..aux_node import set_interface_values
from .. import primitive_prop as prop
from ..constants import Type
from mathutils import Matrix


class _ConvertToGrid_Operator(ConvertTo_BaseOperator):
    type = Type.Grid


class ConvertToGrid_Operator(_ConvertToGrid_Operator):
    """Make Modern Grid From Object"""

    B = _ConvertToGrid_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    def _handle_proc(self, context: Context, obj: Object, bbox: BBox) -> Object:
        # I just want the size on the XY plane, so I can use a bounding box

        bpy.ops.mesh.mpr_make_grid()
        grid = get_object_just_added(context)
        mod = grid.modifiers[0]
        set_interface_values(
            mod,
            context,
            (
                (prop.SizeX.name, bbox.size.x / 2),
                (prop.SizeY.name, bbox.size.y / 2),
            ),
        )

        t, r, s = obj.matrix_world.decompose()
        t = obj.matrix_world @ bbox.center
        grid.matrix_world = Matrix.LocRotScale(t, r, s)

        return grid
