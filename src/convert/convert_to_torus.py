from bpy.types import Context, Object
from .convert_to_baseop import ConvertTo_BaseOperator, BBox
from ..constants import Type, MIN_RADIUS
from ..aux_func import (
    get_object_just_added,
)
from ..aux_node import set_interface_values
from .. import primitive_prop as prop
import bpy.ops
from mathutils import Vector
from typing import Sequence


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
            torus.modifiers[0],
            context,
            (
                (prop.RingRadius.name, ring_radius),
                (prop.Radius.name, radius),
            ),
        )
        return torus, Vector()
