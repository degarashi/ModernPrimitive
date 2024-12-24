import bpy
import sys
from bpy.types import (
    Mesh,
    Object,
    Context,
    bpy_struct,
    NodeGroup,
    NodesModifier,
    Modifier,
)
from .exception import DGFileNotFound, DGObjectNotFound, DGInvalidVersionNumber
from .constants import (
    Type,
    ASSET_DIR_NAME,
    MODERN_PRIMITIVE_BASE_MESH_NAME,
    MODERN_PRIMITIVE_TAG,
    MODERN_PRIMITIVE_PREFIX,
    get_addon_dir,
)
from mathutils import Vector
from collections.abc import Iterable
from .version import VersionInt, get_primitive_version


def register_class(cls: list[type[bpy_struct]]) -> None:
    for cl in cls:
        bpy.utils.register_class(cl)


def unregister_class(cls: list[type[bpy_struct]]) -> None:
    for cl in cls:
        bpy.utils.unregister_class(cl)


def get_object_just_added(context: Context) -> Object:
    return context.view_layer.objects.selected[0]


def append_object_from_asset(type: Type, context: Context) -> Object:
    obj_name = type.name
    file_path = get_blend_file_path(type, False)
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
    node_group = get_node_group(type, get_primitive_version(type))
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


def get_bound_box(vecs: Iterable[Vector]) -> tuple[Vector, Vector]:
    L = sys.float_info.max
    min_v = Vector((L, L, L))
    max_v = Vector((-L, -L, -L))
    for pt in vecs:
        for i in range(3):
            min_v[i] = min(min_v[i], pt[i])
            max_v[i] = max(max_v[i], pt[i])

    return (min_v, max_v)


def is_modern_primitive(obj: Object) -> bool:
    if obj.type != "MESH":
        return False
    if len(obj.modifiers) == 0:
        return False
    return is_primitive_mod(obj.modifiers[0])


def is_modern_primitive_specific(obj: Object, type: Type) -> bool:
    if not is_modern_primitive(obj):
        return False
    return obj.modifiers[0].name == modifier_name(type)


def update_node_interface(mod: NodesModifier, context: Context) -> bool:
    mod.node_group.interface_update(context)


def get_blend_file_path(type: Type, is_relative: bool) -> str:
    rel_path = f"{ASSET_DIR_NAME}/{type.name.lower()}.blend"
    if is_relative:
        return rel_path
    addon_dir = get_addon_dir()
    return addon_dir / rel_path


def node_group_name_prefix(type: Type) -> str:
    return f"{MODERN_PRIMITIVE_TAG}{type.name}_"


def node_group_name(type: Type, version: VersionInt) -> str:
    return node_group_name_prefix(type) + str(version)


def modifier_name(type: Type) -> str:
    return f"{MODERN_PRIMITIVE_TAG}{type.name}"


def is_primitive_mod(mod: Modifier) -> bool:
    return mod.name.startswith(MODERN_PRIMITIVE_TAG)


def make_primitive_property_name(name: str) -> str:
    return f"{MODERN_PRIMITIVE_PREFIX}_{name}"


def is_primitive_property(name: str) -> bool:
    return name.startswith(MODERN_PRIMITIVE_PREFIX + "_")
