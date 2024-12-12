import bpy
from pathlib import Path
from bpy.types import Mesh, Object, Context, bpy_struct, NodeGroup
from .primitive import Type
from .constants import MODERN_PRIMITIVE_BASE_MESH_NAME, VersionInt, get_blend_file_name
from .exception import DGFileNotFound, DGObjectNotFound, DGInvalidVersionNumber
from .constants import modifier_name, node_group_name_prefix, NodeGroupCurVersion


def register_class(cls: list[type[bpy_struct]]) -> None:
    for cl in cls:
        bpy.utils.register_class(cl)


def unregister_class(cls: list[type[bpy_struct]]) -> None:
    for cl in cls:
        bpy.utils.unregister_class(cl)


def get_object_just_added(context: Context) -> Object:
    return context.view_layer.objects.selected[0]


def append_object_from_asset(type: Type, context: Context) -> Object:
    addon_dir = Path(__file__).parent
    obj_name = type.name
    file_name = get_blend_file_name(type)
    file_path = addon_dir / file_name
    if not file_path.exists():
        raise DGFileNotFound(file_path)

    bpy.ops.wm.append(
        filepath=str(file_path / "Object" / obj_name),
        directory=str(file_path / "Object"),
        filename=obj_name,
    )
    try:
        return get_object_just_added(context)
    except IndexError as e:
        # ロードできてない
        raise DGObjectNotFound(obj_name, file_path) from e


def show_error_message(msg: str, title: str = "Error") -> None:
    bpy.context.window_manager.popup_menu(
        lambda self, context: self.layout.label(text=msg),
        title=title,
        icon="ERROR",
    )


def get_node_group(type: Type, minimum_version: VersionInt) -> NodeGroup | None:
    prefix: str = node_group_name_prefix(type)
    matched: NodeGroup | None = None

    for ng in bpy.data.node_groups:
        if ng.name.startswith(prefix):
            try:
                ver: VersionInt = VersionInt.get_version_from_string(ng.name)
                if ver >= minimum_version:
                    matched = ng
            except DGInvalidVersionNumber:
                pass

    return matched


def get_base_mesh() -> Mesh | None:
    return bpy.data.meshes.get(MODERN_PRIMITIVE_BASE_MESH_NAME, None)


def share_node_group_if_exists(type: Type, obj: Object) -> None:
    node_group = get_node_group(type, NodeGroupCurVersion[type.name].value)
    if node_group is not None:
        mod = obj.modifiers[modifier_name(type)]
        if mod.node_group == node_group:
            return

        to_delete = mod.node_group
        mod.node_group = node_group
        bpy.data.node_groups.remove(to_delete)


def share_basemesh_if_exists(obj: Object) -> None:
    mesh = get_base_mesh()
    if mesh == obj.data:
        return
    if mesh is not None:
        to_delete = obj.data
        obj.data = mesh
        bpy.data.meshes.remove(to_delete)


def load_primitive_from_asset(type: Type, context: Context) -> Object:
    obj = append_object_from_asset(type, context)
    # ダブッたリソースを共有
    share_node_group_if_exists(type, obj)
    share_basemesh_if_exists(obj)
    # カーソル位置へ移動
    obj.location = context.scene.cursor.location
    return obj
