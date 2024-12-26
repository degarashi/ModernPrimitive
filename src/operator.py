from bpy.types import bpy_struct, Context, Operator
from bpy.props import BoolProperty
from . import aux_func
from .exception import DGFileNotFound, DGObjectNotFound
from .primitive import (
    PrimitiveInfo_Cube,
    PrimitiveInfo_Cone,
    PrimitiveInfo_Grid,
    PrimitiveInfo_Cylinder,
    PrimitiveInfo_ICOSphere,
    PrimitiveInfo_UVSphere,
    PrimitiveInfo_Torus,
    PrimitiveInfo_Tube,
    PrimitiveInfo_Gear,
    PrimitiveInfo_Spring,
    PrimitiveInfo_DeformableCube,
    PrimitiveInfo_Capsule,
)


class OperatorBase(Operator):
    bl_options = {"REGISTER", "UNDO"}
    set_cursor_rot: BoolProperty(name="Set Cursor's Rotation", default=False)

    def handle_primitive(self, context: Context) -> set[str]:
        try:
            aux_func.load_primitive_from_asset(self.type, context, self.set_cursor_rot)
        except (DGFileNotFound, DGObjectNotFound) as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        return {"FINISHED"}


class MakeCube_Operator(OperatorBase, PrimitiveInfo_Cube):
    """Make Modern Cube"""

    P = PrimitiveInfo_Cube
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeCone_Operator(OperatorBase, PrimitiveInfo_Cone):
    """Make Modern Cone"""

    P = PrimitiveInfo_Cone
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeCylinder_Operator(OperatorBase, PrimitiveInfo_Cylinder):
    """Make Modern Cylinder"""

    P = PrimitiveInfo_Cylinder
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeGrid_Operator(OperatorBase, PrimitiveInfo_Grid):
    """Make Modern Grid"""

    P = PrimitiveInfo_Grid
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeTorus_Operator(OperatorBase, PrimitiveInfo_Torus):
    """Make Modern Torus"""

    P = PrimitiveInfo_Torus
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeICOSphere_Operator(OperatorBase, PrimitiveInfo_ICOSphere):
    """Make Modern Ico Sphere"""

    P = PrimitiveInfo_ICOSphere
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_text(cls):
        return "Ico Sphere"

    @classmethod
    @property
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeUVSphere_Operator(OperatorBase, PrimitiveInfo_UVSphere):
    """Make Modern UV Sphere"""

    P = PrimitiveInfo_UVSphere
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_text(self):
        return "UV Sphere"

    @classmethod
    @property
    def menu_icon(cls):
        return "MESH_" + cls.type_name.upper()

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeTube_Operator(OperatorBase, PrimitiveInfo_Tube):
    """Make Modern Tube"""

    P = PrimitiveInfo_Tube
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_icon(cls):
        return "SURFACE_NCYLINDER"

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeGear_Operator(OperatorBase, PrimitiveInfo_Gear):
    """Make Modern Gear"""

    P = PrimitiveInfo_Gear
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_icon(cls):
        return "PREFERENCES"

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeSpring_Operator(OperatorBase, PrimitiveInfo_Spring):
    """Make Modern Spring"""

    P = PrimitiveInfo_Spring
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_icon(cls):
        return "MOD_SCREW"

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeDeformableCube_Operator(OperatorBase, PrimitiveInfo_DeformableCube):
    """Make Modern Deformable Cube"""

    P = PrimitiveInfo_DeformableCube
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_icon(cls):
        return "META_CUBE"

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


class MakeCapsule_Operator(OperatorBase, PrimitiveInfo_Capsule):
    """Make Modern Capsule"""

    P = PrimitiveInfo_Capsule
    bl_idname = P.bl_idname
    bl_label = P.bl_label

    @classmethod
    @property
    def menu_icon(cls):
        return "MESH_CAPSULE"

    def execute(self, context: Context | None) -> set[str]:
        return self.handle_primitive(context)


OPS: list[type[bpy_struct]] = [
    MakeCube_Operator,
    MakeCone_Operator,
    MakeCylinder_Operator,
    MakeGrid_Operator,
    MakeICOSphere_Operator,
    MakeTorus_Operator,
    MakeUVSphere_Operator,
    MakeTube_Operator,
    MakeGear_Operator,
    MakeSpring_Operator,
    MakeDeformableCube_Operator,
    MakeCapsule_Operator,
]


def register() -> None:
    aux_func.register_class(OPS)


def unregister() -> None:
    aux_func.unregister_class(OPS)
