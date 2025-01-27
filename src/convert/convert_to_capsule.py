from bpy.types import Context, Object
from .convert_to_baseop import ConvertTo_BaseOperator, BBox
from ..constants import Type, MIN_RADIUS, MIN_SIZE
from ..aux_func import (
    get_object_just_added,
)
from ..aux_node import set_interface_values
from .. import primitive_prop as prop
import bpy.ops
from mathutils import Matrix


class _ConvertToCapsule_Operator(ConvertTo_BaseOperator):
    type = Type.Capsule


class ConvertToCapsule_Operator(_ConvertToCapsule_Operator):
    """Make Modern Capsule From Object"""

    B = _ConvertToCapsule_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    def _handle_proc(self, context: Context, obj: Object, bbox: BBox) -> Object:
        bpy.ops.mesh.mpr_make_capsule()
        capsule = get_object_just_added(context)

        radius = max(MIN_RADIUS, (bbox.size.x + bbox.size.y) / 4)
        height = max(MIN_SIZE, bbox.size.z / 2 - radius)
        set_interface_values(
            capsule.modifiers[0],
            context,
            (
                (prop.Radius.name, radius),
                (prop.Height.name, height),
            ),
        )
        capsule.matrix_world = obj.matrix_world @ Matrix.Translation(bbox.center)
        return capsule
