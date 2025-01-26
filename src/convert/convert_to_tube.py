from bpy.types import Context, Object
from .convert_to_baseop import ConvertTo_BaseOperator, BBox
from ..constants import Type, MIN_RADIUS, MIN_SIZE
from ..aux_func import (
    get_object_just_added,
)
from ..aux_node import set_interface_values
from .. import primitive_prop as prop
import bpy.ops
from mathutils import Matrix, Vector


class _ConvertToTube_Operator(ConvertTo_BaseOperator):
    type = Type.Tube


class ConvertToTube_Operator(_ConvertToTube_Operator):
    """Make Modern Tube From Object"""

    B = _ConvertToTube_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    def _handle_proc(self, context: Context, obj: Object, bbox: BBox) -> Object:
        bpy.ops.mesh.mpr_make_tube()
        tube = get_object_just_added(context)

        height = max(MIN_SIZE, bbox.size.z)
        outer_radius = max(MIN_RADIUS, (bbox.size.x + bbox.size.y) / 4)
        inner_radius = outer_radius / 2
        set_interface_values(
            tube.modifiers[0],
            context,
            (
                (prop.Height.name, height),
                (prop.OuterRadius.name, outer_radius),
                (prop.InnerRadius.name, inner_radius),
            ),
        )
        tube.matrix_world = obj.matrix_world @ Matrix.Translation(
            bbox.center + Vector((0, 0, -height / 2))
        )
        return tube
