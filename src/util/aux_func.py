from collections.abc import Iterable
from contextlib import suppress

import bpy
from bpy.types import (
    AddonPreferences,
    Context,
    Modifier,
    NodeGroup,
    NodesModifier,
    Object,
    ObjectModifiers,
    RegionView3D,
    bpy_struct,
)
from mathutils import Matrix, Vector

from ..constants import (
    ASSET_DIR_NAME,
    MODERN_PRIMITIVE_PREFIX,
    MODERN_PRIMITIVE_TAG,
    Type,
    get_addon_dir,
    get_addon_name,
)
from ..exception import (
    DGFileNotFound,
    DGInvalidVersionNumber,
    DGModifierNotFound,
    DGObjectNotFound,
    DGUnknownType,
)
from ..version import VersionInt, get_primitive_version


def get_mpr_modifier(mods: ObjectModifiers) -> NodesModifier:
    # For now, it's fixed at 0 in the modifier list
    mod = mods[0]
    if not is_primitive_mod(mod):
        raise DGModifierNotFound()
    return mod


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


def register_class(cls: Iterable[type[bpy_struct]]) -> None:
    for cl in cls:
        bpy.utils.register_class(cl)


def unregister_class(cls: Iterable[type[bpy_struct]]) -> None:
    for cl in cls:
        bpy.utils.unregister_class(cl)


def get_object_just_added(context: Context) -> Object:
    return context.view_layer.objects.selected[0]


def append_object_from_asset(type_c: Type, context: Context) -> Object:
    obj_name = type_c.name
    file_path = get_blend_file_path(type_c, False)
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
        # Cannot load
        raise DGObjectNotFound(obj_name, file_path) from e


def show_error_message(msg: str, title: str = "Error") -> None:
    bpy.context.window_manager.popup_menu(
        lambda self, context: self.layout.label(text=msg),
        title=title,
        icon="ERROR",
    )


def get_node_group(type_c: Type, minimum_version: VersionInt) -> NodeGroup | None:
    prefix: str = node_group_name_prefix(type_c)
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


def share_node_group_if_exists(type_c: Type, obj: Object) -> None:
    node_group = get_node_group(type_c, get_primitive_version(type_c))
    if node_group is not None:
        mod = obj.modifiers[modifier_name(type_c)]
        if mod.node_group == node_group:
            return

        to_delete = mod.node_group
        mod.node_group = node_group
        bpy.data.node_groups.remove(to_delete)


def load_primitive_from_asset(type_c: Type, context: Context, set_rot: bool) -> Object:
    obj = append_object_from_asset(type_c, context)
    # This line may not be necessary,
    # but sometimes it doesn't work well unless you do this...?
    context.view_layer.objects.active = None
    context.view_layer.objects.active = obj
    # share duplicate resources
    share_node_group_if_exists(type_c, obj)
    # move to 3d-cursor's position and rotation
    cur = context.scene.cursor
    obj.location = cur.location
    if set_rot:
        obj.rotation_euler = cur.rotation_euler
    return obj


def is_modern_primitive(obj: Object) -> bool:
    if obj.type != "MESH" or len(obj.modifiers) == 0:
        return False
    with suppress(DGModifierNotFound):
        return is_primitive_mod(get_mpr_modifier(obj.modifiers))
    return False


def is_modern_primitive_specific(obj: Object, type_c: Type) -> bool:
    if not is_modern_primitive(obj):
        return False
    return get_mpr_modifier(obj.modifiers).name == modifier_name(type_c)


def get_blend_file_path(type_c: Type, is_relative: bool) -> str:
    rel_path = f"{ASSET_DIR_NAME}/{type_c.name.lower()}.blend"
    if is_relative:
        return rel_path
    addon_dir = get_addon_dir()
    return addon_dir / rel_path


def node_group_name_prefix(type_c: Type) -> str:
    return f"{MODERN_PRIMITIVE_TAG}{type_c.name}_"


def node_group_name(type_c: Type, version: VersionInt) -> str:
    return node_group_name_prefix(type_c) + str(version)


def type_from_modifier_name(name: str) -> Type:
    if name.startswith(MODERN_PRIMITIVE_TAG):
        name_s = name[len(MODERN_PRIMITIVE_TAG) :]
        return Type[name_s]
    raise DGUnknownType()


def modifier_name(type_c: Type) -> str:
    return f"{MODERN_PRIMITIVE_TAG}{type_c.name}"


def is_primitive_mod(mod: Modifier) -> bool:
    return mod.name.startswith(MODERN_PRIMITIVE_TAG)


def make_primitive_property_name(name: str) -> str:
    return f"{MODERN_PRIMITIVE_PREFIX}_{name}"


def is_primitive_property(name: str) -> bool:
    return name.startswith(MODERN_PRIMITIVE_PREFIX + "_")


def get_active_and_selected_primitive(context: Context) -> Object | None:
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


def get_evaluated_obj(context: Context, obj: Object) -> Object:
    depsgraph = context.evaluated_depsgraph_get()
    return obj.evaluated_get(depsgraph)


def mul_vert_mat(verts: Iterable[Vector], mat: Matrix) -> list[Vector]:
    return [(mat @ v).to_3d() for v in verts]


def get_category_name_from_operator(typ: Type) -> tuple[str, str]:
    if not hasattr(typ, "bl_idname") or not isinstance(typ.bl_idname, str):
        raise TypeError(f"Expected an Operator type with a string bl_idname, got {typ}")

    CATEGORY_SEGMENTS = 2
    parts = typ.bl_idname.split(".")
    if len(parts) == CATEGORY_SEGMENTS:
        return tuple(parts)
    raise ValueError(f"Invalid bl_idname format: {typ.bl_idname}")


def exec_operator_from_type(typ: Type, *args, **kwargs) -> None:
    category, name = get_category_name_from_operator(typ)
    try:
        operator = getattr(bpy.ops, category)
        op = getattr(operator, name)
        op(*args, **kwargs)
    except AttributeError as e:
        raise ValueError(f"Operator bpy.ops.{category}.{name} not found: {e}") from e
    except Exception as e:  # Catch other potential errors
        raise RuntimeError(f"Error executing operator: {e}") from e


def copy_modifier(from_mod: Modifier, to_mod: ObjectModifiers) -> None:
    new_mod = to_mod.new(name=from_mod.name, type=from_mod.type)
    for attr in dir(from_mod):
        if attr.startswith("__") or attr in {"name", "type"}:
            continue
        # Ignore some properties as they may not be able to be copied
        with suppress(AttributeError):
            setattr(new_mod, attr, getattr(from_mod, attr))


def disable_modifier(mod: Modifier) -> None:
    mod.show_viewport = False
    mod.show_render = False


def is_mpr_enabled(mod: ObjectModifiers) -> bool:
    return mod[0].show_viewport


def get_view3d_pos(region: RegionView3D) -> Vector:
    # view matrix
    v_mat = region.view_matrix
    # The position of the viewpoint can be obtained as a position vector
    #   of the inverse matrix of the view matrix
    return v_mat.inverted().translation
