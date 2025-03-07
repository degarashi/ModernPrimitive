from collections.abc import Sequence

import bpy.ops
from bpy.types import Context, Object
from mathutils import Vector

from .. import primitive_prop as prop
from ..aux_func import (
    get_object_just_added,
)
from ..aux_node import set_interface_values
from ..constants import Type
from .convert_to_baseop import BBox, ConvertTo_BaseOperator


class _ConvertToCylinder_Operator(ConvertTo_BaseOperator):
    type = Type.Cylinder


class ConvertToCylinder_Operator(_ConvertToCylinder_Operator):
    """Make Modern Cylinder From Object"""

    B = _ConvertToCylinder_Operator
    bl_idname = B.get_bl_idname()
    bl_label = B.get_bl_label()

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        bpy.ops.mesh.mpr_make_cylinder()
        cy = get_object_just_added(context)

        radius = (bbox.size.x + bbox.size.y) / 4
        height = bbox.size.z

        set_interface_values(
            cy.modifiers[0],
            context,
            (
                (prop.Radius.name, radius),
                (prop.Height.name, height),
            ),
        )
        return cy, Vector()
