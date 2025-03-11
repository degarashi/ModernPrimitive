from typing import Sequence

import bpy.ops
from bpy.types import Context, Object
from mathutils import Vector

from .. import primitive_prop as prop
from ..aux_func import (
    get_mpr_modifier,
    get_object_just_added,
)
from ..aux_node import set_interface_values
from ..constants import MIN_RADIUS, Type
from .convert_to_baseop import BBox, ConvertTo_BaseOperator


class _ConvertToTorus_Operator(ConvertTo_BaseOperator):
    type = Type.Torus


class ConvertToTorus_Operator(_ConvertToTorus_Operator):
    """Make Modern Torus From Object"""

    B = _ConvertToTorus_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        bpy.ops.mesh.mpr_make_torus()
        torus = get_object_just_added(context)

        ring_radius = max(MIN_RADIUS, bbox.size.z / 2)
        radius = max(MIN_RADIUS, (bbox.size.x + bbox.size.y) / 4 - ring_radius)
        set_interface_values(
            get_mpr_modifier(torus.modifiers),
            context,
            (
                (prop.RingRadius.name, ring_radius),
                (prop.Radius.name, radius),
            ),
        )
        return torus, Vector()
