from bpy.types import bpy_struct, Context, Operator
from bpy.types import NodeGroup, NodeGroupInput, NodesModifier
import bpy.utils
from typing import cast, Any, Iterable
from .aux_func import bbox, get_object_just_added
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
)


class OperatorBase(Operator):
    bl_options = {"REGISTER", "UNDO"}

    def handle_primitive(self, context: Context) -> set[str]:
        try:
            aux_func.load_primitive_from_asset(self.type, context)
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


def find_group_input(node_group: NodeGroup) -> NodeGroupInput:
    for node in node_group.nodes:
        if node.type == "GROUP_INPUT":
            return node
    raise KeyError("Group Input")


def find_interface_name(node_group: NodeGroup, name: str) -> str:
    gi = find_group_input(node_group)
    for o in gi.outputs:
        if o.name == name:
            return o.identifier
    raise KeyError(name)


def set_interface_value(mod: NodesModifier, data: tuple[str, Any]) -> None:
    sock_name = find_interface_name(mod.node_group, data[0])
    mod[sock_name] = data[1]


def set_interface_values(
    mod: NodesModifier, context: Context, data: Iterable[tuple[str, Any]]
) -> None:
    for d in data:
        set_interface_value(mod, d)
    mod.node_group.interface_update(context)


class ConvertToCube_Operator(Operator):
    """Make Modern Cube From Object"""

    bl_idname = "mesh.convert_to_modern_cube"
    bl_label = "Convert object to ModernCube"

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        context = cast(Context, context)
        obj = context.view_layer.objects.active
        return obj is not None and obj.type == "MESH"

    def execute(self, context: Context | None) -> set[str]:
        from_obj = context.view_layer.objects.active
        (b_min, b_max) = bbox(from_obj.bound_box)
        center = (b_min + b_max) / 2

        bpy.ops.mesh.make_modern_cube()
        cube = get_object_just_added(context)

        set_interface_values(
            cube.modifiers[0],
            context,
            (
                ("SizeX", (b_max.x - b_min.x) / 2),
                ("SizeY", (b_max.y - b_min.y) / 2),
                ("SizeZ", (b_max.z - b_min.z) / 2),
            ),
        )
        cube.matrix_world = from_obj.matrix_world
        cube.location = from_obj.matrix_world @ center

        return {"FINISHED"}


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
]


def register() -> None:
    aux_func.register_class(OPS)
    bpy.utils.register_class(ConvertToCube_Operator)


def unregister() -> None:
    aux_func.unregister_class(OPS)
    bpy.utils.unregister_class(ConvertToCube_Operator)
