from bpy.types import (
    Context,
    Object,
)
from .convert_to_baseop import ConvertTo_BaseOperator
import bpy.ops

from ..aux_func import get_bound_box, get_object_just_added, copy_rotation
from .. import primitive_prop as prop
from ..aux_node import set_interface_values
from bpy.props import EnumProperty


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

    def _handle_proc(self, context: Context, obj: Object) -> Object:
        match(self.sphere_type):
            case "UVSphere":
                bpy.ops.mesh.mpr_make_uvsphere()
            case "ICOSphere":
                bpy.ops.mesh.mpr_make_icosphere()
            case "QuadSphere":
                bpy.ops.mesh.mpr_make_quadsphere()

        sphere = get_object_just_added(context)

        # I just want the size of Bounding box.
        #   so there is no need to read vertices
        (b_min, b_max) = get_bound_box(obj.bound_box)
        b_diff = b_max - b_min
        mod = sphere.modifiers[0]
        set_interface_values(
            mod, context, ((prop.Radius.name, max(b_diff.x, b_diff.y, b_diff.z) / 2),)
        )

        center = (b_min + b_max) / 2
        center = obj.matrix_world @ center
        sphere.location = center
        copy_rotation(sphere, obj)
        sphere.scale = obj.scale
        return sphere
