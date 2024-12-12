import bpy
from bpy.types import (
    Object,
    Operator,
    Context,
    NodeGroup,
    NodeGroupInput,
    NodesModifier,
)
from typing import cast
from .aux_func import get_bound_box, get_object_just_added
from typing import Any, Iterable
from bpy.props import BoolProperty, EnumProperty


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
    bl_options = {"REGISTER", "UNDO"}

    keep_original: BoolProperty(name="Keep Original", default=False)
    cube_type: EnumProperty(
        name="Cube Type",
        default="Cube",
        items=[
            ("Cube", "Cube", "Make Normal Cube"),
            ("DeformableCube", "Deformable Cube", "Make Deformable Cube"),
        ],
    )

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        context = cast(Context, context)

        sel = context.selected_objects
        if len(sel) == 0:
            return False
        for obj in sel:
            if obj is None or obj.type != "MESH":
                return False
        return True

    def _make_cube(self, context: Context, from_obj: Object) -> None:
        (b_min, b_max) = get_bound_box(from_obj.bound_box)
        center = (b_min + b_max) / 2

        if self.cube_type == "Cube":
            bpy.ops.mesh.make_modern_cube()
        else:
            bpy.ops.mesh.make_modern_deformablecube()

        cube = get_object_just_added(context)

        if self.cube_type == "Cube":
            set_interface_values(
                cube.modifiers[0],
                context,
                (
                    ("SizeX", (b_max.x - b_min.x) / 2),
                    ("SizeY", (b_max.y - b_min.y) / 2),
                    ("SizeZ", (b_max.z - b_min.z) / 2),
                ),
            )
        else:
            set_interface_values(
                cube.modifiers[0],
                context,
                (
                    ("MinX", -b_min.x),
                    ("MaxX", b_max.x),
                    ("MinY", -b_min.y),
                    ("MaxY", b_max.y),
                    ("MinZ", -b_min.z),
                    ("MaxZ", b_max.z),
                ),
            )
        cube.matrix_world = from_obj.matrix_world
        cube.location = from_obj.matrix_world @ center
        cube.name = from_obj.name + "_converted"
        print(cube.name_full)

    def execute(self, context: Context | None) -> set[str]:
        sel = context.selected_objects.copy()
        for obj in sel:
            self._make_cube(context, obj)
        if not self.keep_original:
            for obj in sel:
                bpy.data.objects.remove(obj)
        return {"FINISHED"}


MENU_TARGET = bpy.types.VIEW3D_MT_object_convert


def menu_func(self, context: Context) -> None:
    layout = self.layout
    layout.operator(ConvertToCube_Operator.bl_idname, text="Modern Cube", icon="CUBE")


def register() -> None:
    bpy.utils.register_class(ConvertToCube_Operator)
    MENU_TARGET.append(menu_func)


def unregister() -> None:
    MENU_TARGET.remove(menu_func)
    bpy.utils.unregister_class(ConvertToCube_Operator)
