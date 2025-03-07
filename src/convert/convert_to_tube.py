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


class _ConvertToTube_Operator(ConvertTo_BaseOperator):
    type = Type.Tube


class ConvertToTube_Operator(_ConvertToTube_Operator):
    """Make Modern Tube From Object"""

    B = _ConvertToTube_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
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
        return tube, Vector()
