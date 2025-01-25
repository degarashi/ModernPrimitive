from bpy.types import (
    Context,
    Object,
)
from .convert_to_baseop import ConvertTo_BaseOperator
from bpy.utils import register_class, unregister_class
import bpy.ops
from ..aux_func import (
    get_bound_box,
    get_object_just_added,
    copy_rotation,
)
from ..aux_node import set_interface_values
from .. import primitive_prop as prop
from ..constants import Type


class _ConvertToGrid_Operator(ConvertTo_BaseOperator):
    type = Type.Grid


class ConvertToGrid_Operator(_ConvertToGrid_Operator):
    """Make Modern Grid From Object"""

    B = _ConvertToGrid_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    def _handle_proc(self, context: Context, obj: Object) -> Object:
        # I just want the size on the XY plane, so I can use a bounding box

        (b_min, b_max) = get_bound_box(obj.bound_box)
        b_diff = b_max - b_min

        bpy.ops.mesh.mpr_make_grid()
        grid = get_object_just_added(context)
        mod = grid.modifiers[0]
        set_interface_values(
            mod,
            context,
            (
                (prop.SizeX.name, b_diff.x / 2),
                (prop.SizeY.name, b_diff.y / 2),
            ),
        )
        center = (b_min + b_max) / 2
        center = obj.matrix_world @ center
        grid.location = center
        copy_rotation(grid, obj)
        grid.scale = obj.scale
        return grid
