from collections.abc import Sequence

import bpy.ops
from bpy.types import Context, Object
from mathutils import Vector

from .. import primitive_prop as prop
from ..aux_func import get_mpr_modifier, get_object_just_added
from ..aux_node import set_interface_values
from ..constants import MIN_RADIUS, Type
from .convert_to_baseop import BBox, ConvertTo_BaseOperator


class _ConvertToCone_Operator(ConvertTo_BaseOperator):
    type = Type.Cone


class ConvertToCone_Operator(_ConvertToCone_Operator):
    """Make Modern Cone From Object"""

    B = _ConvertToCone_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        # Divide into upper half and lower half in the z-axis direction
        top_r: float = MIN_RADIUS
        bottom_r: float = MIN_RADIUS

        for v in verts:
            if v.z >= bbox.center.z:
                # Get the top half vertices
                #   and find out how far they are from the center
                top_r = max(top_r, (v.xy - bbox.center.xy).length)
            else:
                # Get the vertices in the bottom half
                #   and find out how far they are from the center
                bottom_r = max(bottom_r, (v.xy - bbox.center.xy).length)

        bpy.ops.mesh.mpr_make_cone()
        cone = get_object_just_added(context)
        set_interface_values(
            get_mpr_modifier(cone.modifiers),
            context,
            (
                (prop.TopRadius.name, top_r),
                (prop.BottomRadius.name, bottom_r),
                (prop.Height.name, bbox.size.z),
            ),
        )
        return cone, Vector()
