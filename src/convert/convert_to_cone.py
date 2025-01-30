from .convert_to_baseop import ConvertTo_BaseOperator, BBox
from ..constants import Type, MIN_RADIUS
from bpy.types import Object, Context
from ..aux_func import get_object_just_added, get_real_vertices, mul_vert_mat
from mathutils import Vector, Matrix
from ..aux_node import set_interface_values
from .. import primitive_prop as prop

import bpy.ops


class _ConvertToCone_Operator(ConvertTo_BaseOperator):
    type = Type.Cone


class ConvertToCone_Operator(_ConvertToCone_Operator):
    """Make Modern Cone From Object"""

    B = _ConvertToCone_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    def _handle_proc(
        self, context: Context, obj: Object, bbox: BBox, mat: Matrix
    ) -> tuple[Object, Vector]:
        # Divide into upper half and lower half in the z-axis direction
        top_r: float = MIN_RADIUS
        bottom_r: float = MIN_RADIUS

        verts = mul_vert_mat(get_real_vertices(context, obj), mat)
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
            cone.modifiers[0],
            context,
            (
                (prop.TopRadius.name, top_r),
                (prop.BottomRadius.name, bottom_r),
                (prop.Height.name, bbox.size.z),
            ),
        )
        return cone, Vector((0, 0, -bbox.size.z / 2))
