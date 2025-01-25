from bpy.types import Context, Object
from .convert_to_baseop import ConvertTo_BaseOperator
from ..constants import Type
from ..aux_func import (
    get_bound_box,
    get_object_just_added,
)
from ..aux_node import set_interface_values
from .. import primitive_prop as prop
import bpy.ops
from mathutils import Matrix, Vector


class _ConvertToCylinder_Operator(ConvertTo_BaseOperator):
    type = Type.Cylinder


class ConvertToCylinder_Operator(_ConvertToCylinder_Operator):
    """Make Modern Cylinder From Object"""

    B = _ConvertToCylinder_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    def _handle_proc(self, context: Context, obj: Object) -> Object:
        (b_min, b_max) = get_bound_box(obj.bound_box)
        b_diff = b_max - b_min
        b_avg = (b_min + b_max) / 2
        bpy.ops.mesh.mpr_make_cylinder()
        cy = get_object_just_added(context)
        set_interface_values(
            cy.modifiers[0],
            context,
            (
                (prop.Radius.name, (b_diff.x + b_diff.y) / 4),
                (prop.Height.name, (b_diff.z)),
            ),
        )
        cy.matrix_world = obj.matrix_world @ Matrix.Translation(
            b_avg + Vector((0, 0, -b_diff.z / 2))
        )
        return cy
