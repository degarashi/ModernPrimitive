import bpy
import sys
from typing import cast
from bpy.types import (
    Object,
    Context,
    bpy_struct,
    NodeGroup,
    NodesModifier,
    Modifier,
    AddonPreferences,
    Mesh,
    MeshVertex,
)
from .exception import (
    DGFileNotFound,
    DGObjectNotFound,
    DGInvalidVersionNumber,
    DGUnknownType,
)
from .constants import (
    Type,
    ASSET_DIR_NAME,
    MODERN_PRIMITIVE_TAG,
    MODERN_PRIMITIVE_PREFIX,
    get_addon_dir,
    get_addon_name,
)
from mathutils import Vector, Matrix
from collections.abc import Iterable
from .version import VersionInt, get_primitive_version


# Is the object valid in blender?
def obj_is_alive(obj: Object) -> bool:
    assert obj is not None
    try:
        return bool(obj.name) or True
    except ReferenceError:
        return False


class BackupSelection:
    def __init__(self, context: Context, deselect_all: bool = False):
        self._bkup_active = context.active_object
        self._bkup_sel = context.selected_objects.copy()
        if deselect_all:
            for s in self._bkup_sel:
                s.select_set(False)

    def restore(self, context: Context) -> None:
        context.view_layer.objects.active = self._bkup_active
        for s in self._bkup_sel:
            if obj_is_alive(s):
                s.select_set(True)


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


def share_node_group_if_exists(type: Type, obj: Object) -> None:
    node_group = get_node_group(type, get_primitive_version(type))
    if node_group is not None:
        mod = obj.modifiers[modifier_name(type)]
        if mod.node_group == node_group:
            return

        to_delete = mod.node_group
        mod.node_group = node_group
        bpy.data.node_groups.remove(to_delete)


def load_primitive_from_asset(type: Type, context: Context, set_rot: bool) -> Object:
    obj = append_object_from_asset(type, context)
    # This line may not be necessary,
    # but sometimes it doesn't work well unless you do this...?
    context.view_layer.objects.active = None
    context.view_layer.objects.active = obj
    # share duplicate resources
    share_node_group_if_exists(type, obj)
    # move to 3d-cursor's position and rotation
    cur = context.scene.cursor
    obj.location = cur.location
    if set_rot:
        obj.rotation_euler = cur.rotation_euler
    return obj


class AABB:
    def __init__(self, minv: Vector, maxv: Vector):
        self.min_v = minv
        self.max_v = maxv

    def __getitem__(self, index: int) -> Vector:
        return (self.min_v, self.max_v)[index]


def calc_aabb(vecs: Iterable[Vector]) -> AABB:
    L = sys.float_info.max
    min_v = Vector((L, L, L))
    max_v = Vector((-L, -L, -L))
    for pt in vecs:
        pt = Vector(pt)
        for i in range(3):
            min_v[i] = min(min_v[i], pt[i])
            max_v[i] = max(max_v[i], pt[i])

    return AABB(min_v, max_v)


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


def type_from_modifier_name(name: str) -> Type:
    if name.startswith(MODERN_PRIMITIVE_TAG):
        name_s = name[len(MODERN_PRIMITIVE_TAG) :]
        return Type[name_s]
    raise DGUnknownType()


def modifier_name(type: Type) -> str:
    return f"{MODERN_PRIMITIVE_TAG}{type.name}"


def is_primitive_mod(mod: Modifier) -> bool:
    return mod.name.startswith(MODERN_PRIMITIVE_TAG)


def make_primitive_property_name(name: str) -> str:
    return f"{MODERN_PRIMITIVE_PREFIX}_{name}"


def is_primitive_property(name: str) -> bool:
    return name.startswith(MODERN_PRIMITIVE_PREFIX + "_")


# Return active and selected objects
def get_target_object(context: Context) -> Object | None:
    obj = context.view_layer.objects.active
    if obj is not None and is_modern_primitive(obj):
        sel = context.selected_objects
        if obj in sel:
            return obj
    return None


# Return the selected modern primitive
def get_selected_primitive(context: Context) -> list[Object]:
    ret: list[Object] = []
    sel = context.selected_objects
    for obj in sel:
        if is_modern_primitive(obj):
            ret.append(obj)
    return ret


def get_addon_preferences(context: Context) -> AddonPreferences:
    return context.preferences.addons[get_addon_name()].preferences


def copy_rotation(dst: Object, src: Object) -> None:
    dst.rotation_mode = src.rotation_mode
    dst.rotation_axis_angle = src.rotation_axis_angle
    dst.rotation_quaternion = src.rotation_quaternion
    dst.rotation_euler = src.rotation_euler


def get_evaluated_mesh(context: Context, obj: Object) -> Mesh:
    depsgraph = context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh: Mesh = eval_obj.to_mesh()
    return mesh


# Acquire vertices of the applied modifier, etc.
def get_evaluated_vertices(context: Context, obj: Object) -> list[Vector]:
    mesh = get_evaluated_mesh(context, obj)
    verts: list[Vector] = [v.co for v in cast(MeshVertex, mesh.vertices)]
    return verts


def mul_vert_mat(verts: Iterable[Vector], mat: Matrix) -> list[Vector]:
    return [(mat @ v).to_3d() for v in verts]
