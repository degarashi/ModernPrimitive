from collections.abc import Sequence

import bpy.ops
from bpy.props import EnumProperty
from bpy.types import (
    Context,
    Object,
)
from mathutils import Vector

from .. import primitive_prop as prop
from ..aux_func import get_object_just_added
from ..aux_node import set_interface_values
from .convert_to_baseop import BBox, ConvertTo_BaseOperator


class _ConvertToSphere_Operator(ConvertTo_BaseOperator):
    @classmethod
    @property
    def bl_idname(cls) -> str:
        return "mesh.mpr_convert_to_sphere"

    @classmethod
    @property
    def bl_label(cls) -> str:
        return "Convert object to Modern Sphere"


class ConvertToSphere_Operator(_ConvertToSphere_Operator):
    """Make Modern UVSphere From Object"""

    B = _ConvertToSphere_Operator
    bl_idname = B.bl_idname
    bl_label = B.bl_label

    sphere_type: EnumProperty(
        name="Sphere Type",
        default="UVSphere",
        items=(
            ("UVSphere", "UV Sphere", ""),
            ("ICOSphere", "ICO Sphere", ""),
            ("QuadSphere", "Quad Sphere", ""),
        ),
    )

    def _handle_proc(
        self, context: Context, bbox: BBox, verts: Sequence[Vector]
    ) -> tuple[Object, Vector]:
        match self.sphere_type:
            case "UVSphere":
                bpy.ops.mesh.mpr_make_uvsphere()
            case "ICOSphere":
                bpy.ops.mesh.mpr_make_icosphere()
            case "QuadSphere":
                bpy.ops.mesh.mpr_make_quadsphere()

        sphere = get_object_just_added(context)

        # I just want the size of Bounding box.
        #   so there is no need to read vertices
        mod = sphere.modifiers[0]
        set_interface_values(
            mod,
            context,
            ((prop.Radius.name, max(bbox.size.x, bbox.size.y, bbox.size.z) / 2),),
        )
        return sphere, Vector()
