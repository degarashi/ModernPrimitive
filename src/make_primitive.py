import math
from collections.abc import Iterable
from typing import ClassVar

import bpy.ops
from bpy.props import BoolProperty, FloatProperty
from bpy.types import Context, Operator, SpaceView3D, UILayout, bpy_struct
from mathutils import Vector

from .aux_func import (
    get_addon_preferences,
    get_mpr_modifier,
    get_view3d_pos,
    load_primitive_from_asset,
    register_class,
    unregister_class,
)
from .aux_node import set_interface_value
from .aux_other import classproperty
from .exception import DGFileNotFound, DGObjectNotFound
from .primitive import (
    Primitive_Capsule,
    Primitive_Cone,
    Primitive_Cube,
    Primitive_Cylinder,
    Primitive_DeformableCube,
    Primitive_Gear,
    Primitive_Grid,
    Primitive_ICOSphere,
    Primitive_QuadSphere,
    Primitive_Spring,
    Primitive_Torus,
    Primitive_Tube,
    Primitive_UVSphere,
)


class OperatorBase(Operator):
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}
    set_cursor_rot: BoolProperty(name="Set Cursor's Rotation", default=False)
    appropriate_size: BoolProperty(
        name="Appropriate Size",
        default=False,
        description="Initialize primitive to appropriate size",
    )
    smooth: BoolProperty(name="Smooth Shading", default=False)
    smooth_angle_deg: FloatProperty(name="Smooth Angle", default=45.0, min=0.0, max=180.0)

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        if type(context.space_data) is not SpaceView3D:
            return False
        if context.space_data.type != "VIEW_3D":
            return False
        return context.mode == "OBJECT"

    def handle_primitive(self, context: Context) -> set[str]:
        try:
            obj = load_primitive_from_asset(self.type, context, self.set_cursor_rot)
        except (DGFileNotFound, DGObjectNotFound) as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        if self.appropriate_size:
            # Adjust the scaling value depending on the distance from the viewpoint
            view_loc = get_view3d_pos(context.space_data.region_3d)
            cur_loc = context.scene.cursor.location
            distance = (view_loc - cur_loc).length

            # TODO: The scaling constant and minimum value are hard-coded,
            #   so we will do something about it later.
            size = max(1e-5, distance / 10)
            obj.scale = Vector([size] * 3)

        mod = get_mpr_modifier(obj.modifiers)
        # Apply smooth shading
        set_interface_value(mod, ("Smooth", self.smooth))
        # Apply smooth shading angle
        set_interface_value(mod, ("Smooth Angle", math.radians(self.smooth_angle_deg)))
        # Since the node group value has been changed, update it here
        mod.node_group.interface_update(context)

        if self.appropriate_size:
            bpy.ops.object.mpr_apply_scale(strict=True)

        return {"FINISHED"}

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeCube_Operator(OperatorBase, Primitive_Cube):
    """Make Modern Cube"""

    P = Primitive_Cube
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()


class MakeCone_Operator(OperatorBase, Primitive_Cone):
    """Make Modern Cone"""

    P = Primitive_Cone
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()


class MakeCylinder_Operator(OperatorBase, Primitive_Cylinder):
    """Make Modern Cylinder"""

    P = Primitive_Cylinder
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()


class MakeGrid_Operator(OperatorBase, Primitive_Grid):
    """Make Modern Grid"""

    P = Primitive_Grid
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()


class MakeTorus_Operator(OperatorBase, Primitive_Torus):
    """Make Modern Torus"""

    P = Primitive_Torus
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()


class MakeICOSphere_Operator(OperatorBase, Primitive_ICOSphere):
    """Make Modern Ico Sphere"""

    P = Primitive_ICOSphere
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_text(cls):
        return "Ico Sphere"

    @classproperty
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()


class MakeUVSphere_Operator(OperatorBase, Primitive_UVSphere):
    """Make Modern UV Sphere"""

    P = Primitive_UVSphere
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_text(self):
        return "UV Sphere"

    @classproperty
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()


class MakeTube_Operator(OperatorBase, Primitive_Tube):
    """Make Modern Tube"""

    P = Primitive_Tube
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "SURFACE_NCYLINDER"


class MakeGear_Operator(OperatorBase, Primitive_Gear):
    """Make Modern Gear"""

    P = Primitive_Gear
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "PREFERENCES"


class MakeSpring_Operator(OperatorBase, Primitive_Spring):
    """Make Modern Spring"""

    P = Primitive_Spring
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "MOD_SCREW"


class MakeDeformableCube_Operator(OperatorBase, Primitive_DeformableCube):
    """Make Modern Deformable Cube"""

    P = Primitive_DeformableCube
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "META_CUBE"


class MakeCapsule_Operator(OperatorBase, Primitive_Capsule):
    """Make Modern Capsule"""

    P = Primitive_Capsule
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "MESH_CAPSULE"


class MakeQuadSphere_Operator(OperatorBase, Primitive_QuadSphere):
    """Make Modern QuadSphere"""

    P = Primitive_QuadSphere
    bl_idname = P.get_bl_idname()
    bl_label = P.get_bl_label()

    @classproperty
    def menu_icon(cls):
        return "META_CUBE"


OPS: Iterable[type[bpy_struct]] = (
    MakeCube_Operator,
    MakeDeformableCube_Operator,
    MakeUVSphere_Operator,
    MakeICOSphere_Operator,
    MakeQuadSphere_Operator,
    MakeCone_Operator,
    MakeCylinder_Operator,
    MakeGrid_Operator,
    MakeTorus_Operator,
    MakeTube_Operator,
    MakeGear_Operator,
    MakeSpring_Operator,
    MakeCapsule_Operator,
)

OPS_GROUPS: dict[str, Iterable[type[bpy_struct]]] = {
    "Cube": (
        MakeCube_Operator,
        MakeDeformableCube_Operator,
    ),
    "Sphere": (
        MakeUVSphere_Operator,
        MakeICOSphere_Operator,
        MakeQuadSphere_Operator,
    ),
    "Other": (
        MakeCone_Operator,
        MakeCylinder_Operator,
        MakeGrid_Operator,
        MakeTorus_Operator,
        MakeTube_Operator,
        MakeGear_Operator,
        MakeSpring_Operator,
        MakeCapsule_Operator,
    ),
}


def register() -> None:
    register_class(OPS)


def unregister() -> None:
    unregister_class(OPS)


def make_operator_to_layout(context: Context, layout: UILayout, op: OperatorBase) -> None:
    pref = get_addon_preferences(context)
    p_app_size = pref.make_appropriate_size
    p_cur_rot = pref.make_cursors_rot
    p_smooth = pref.make_smooth_shading

    p = layout.operator(
        op.bl_idname,
        text=op.menu_text,
        icon=op.menu_icon,
    )
    # Read and set default values from preferences
    # Since each default value is false,
    #   OR boolean it with the value of preferences
    p.appropriate_size |= p_app_size
    p.set_cursor_rot |= p_cur_rot
    p.smooth |= p_smooth
