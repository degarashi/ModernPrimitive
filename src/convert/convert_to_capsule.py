from collections.abc import Sequence

import bpy.ops
from bpy.types import Context, Object
from mathutils import Vector

from .. import primitive_prop as prop
from ..aux_func import (
    get_object_just_added,
)
from ..aux_node import set_interface_values
from ..constants import MIN_RADIUS, MIN_SIZE, Type
from .convert_to_baseop import BBox, ConvertTo_BaseOperator


class _ConvertToCapsule_Operator(ConvertTo_BaseOperator):
    type = Type.Capsule


class ConvertToCapsule_Operator(_ConvertToCapsule_Operator):
    """Make Modern Capsule From Object"""

    B = _ConvertToCapsule_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        bpy.ops.mesh.mpr_make_capsule()
        capsule = get_object_just_added(context)

        radius = max(MIN_RADIUS, (bbox.size.x + bbox.size.y) / 4)
        height = max(MIN_SIZE, bbox.size.z - radius*2)
        set_interface_values(
            capsule.modifiers[0],
            context,
            (
                (prop.Radius.name, radius),
                (prop.Height.name, height),
            ),
        )
        return capsule, Vector()
