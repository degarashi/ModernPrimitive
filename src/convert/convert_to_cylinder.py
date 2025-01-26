from bpy.types import Context, Object
from .convert_to_baseop import ConvertTo_BaseOperator, BBox
from ..constants import Type
from ..aux_func import (
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

    def _handle_proc(self, context: Context, obj: Object, bbox: BBox) -> Object:
        bpy.ops.mesh.mpr_make_cylinder()
        cy = get_object_just_added(context)
        set_interface_values(
            cy.modifiers[0],
            context,
            (
                (prop.Radius.name, (bbox.size.x + bbox.size.y) / 4),
                (prop.Height.name, (bbox.size.z)),
            ),
        )
        cy.matrix_world = obj.matrix_world @ Matrix.Translation(
            bbox.center + Vector((0, 0, -bbox.size.z / 2))
        )
        return cy
