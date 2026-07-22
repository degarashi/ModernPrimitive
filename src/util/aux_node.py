from typing import Any
from collections.abc import Callable, Iterable

import bpy

from bpy.types import (
    Context,
    NodeGroup,
    NodeGroupInput,
    NodesModifier,
)
from idprop.types import IDPropertyGroup

_GN_NEW_API = bpy.app.version >= (5, 2, 0)


def find_group_input(node_group: NodeGroup) -> NodeGroupInput:
    for node in node_group.nodes:
        if node.type == "GROUP_INPUT":
            return node
    raise KeyError("Group Input")


def _find_interface_name_new(node_group: NodeGroup, name: str) -> str:
    for item in node_group.interface.items_tree:
        if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name == name:
            return item.identifier
    raise KeyError(name)


def find_interface_name(node_group: NodeGroup, name: str) -> str:
    if _GN_NEW_API:
        return _find_interface_name_new(node_group, name)
    gi = find_group_input(node_group)
    for o in gi.outputs:
        if o.name == name:
            return o.identifier
    raise KeyError(name)


def _enum_group_input_new(node_group: NodeGroup) -> list[str]:
    ret = []
    for item in node_group.interface.items_tree:
        if item.item_type != "SOCKET" or item.in_out != "INPUT":
            continue
        if item.identifier.startswith("_"):
            continue
        if item.bl_socket_idname == "NodeSocketGeometry":
            continue
        ret.append(item.identifier)
    return ret


def _enum_group_input_old(node_group: NodeGroup) -> list[str]:
    ret = []
    gi = find_group_input(node_group)
    for o in gi.outputs:
        if o.identifier.startswith("_") or o.type == "GEOMETRY":
            continue
        ret.append(o.identifier)
    return ret


def _copy_socket_value(dst_inputs, src_inputs, sock_name: str) -> None:
    src_val = src_inputs[sock_name]
    dst_val = dst_inputs[sock_name]
    if isinstance(src_val, IDPropertyGroup) and isinstance(dst_val, IDPropertyGroup):
        dst_val["value"] = src_val["value"]
    else:
        # Blender 5.2+: RNA property → use .value
        dst_inputs[sock_name].value = src_val.value


def copy_geometry_node_params(mod_dst: NodesModifier, mod_src: NodesModifier) -> None:
    enum_fn = _enum_group_input_new if _GN_NEW_API else _enum_group_input_old
    for sock_name in enum_fn(mod_src.node_group):
        if _GN_NEW_API:
            _copy_socket_value(mod_dst.properties.inputs, mod_src.properties.inputs, sock_name)
        else:
            mod_dst[sock_name] = mod_src[sock_name]


def set_interface_value(mod: NodesModifier, data: tuple[str, Any]) -> None:
    sock_name = find_interface_name(mod.node_group, data[0])
    if _GN_NEW_API:
        prop_inputs = mod.properties.inputs
        existing = prop_inputs[sock_name]
        if isinstance(existing, IDPropertyGroup):
            prop_inputs[sock_name]["value"] = data[1]
        else:
            prop_inputs[sock_name].value = data[1]
    else:
        mod[sock_name] = data[1]


def set_interface_values(
    mod: NodesModifier, context: Context, data: Iterable[tuple[str, Any]]
) -> None:
    for d in data:
        set_interface_value(mod, d)
    update_node_interface(mod, context)


def get_interface_value(mod: NodesModifier, name: str) -> Any:
    sock_name = find_interface_name(mod.node_group, name)
    if _GN_NEW_API:
        raw = mod.properties.inputs[sock_name]
        if isinstance(raw, IDPropertyGroup):
            return raw["value"]
        return raw.value
    return mod[sock_name]


def get_interface_values(mod: NodesModifier, data_names: Iterable[str]) -> dict[str, Any]:
    ret: dict[str, Any] = {}
    for d in data_names:
        ret[d] = get_interface_value(mod, d)
    return ret


def modify_interface_value(mod: NodesModifier, ent: str, proc: Callable[[Any], Any]) -> None:
    value = proc(get_interface_value(mod, ent))
    set_interface_value(mod, (ent, value))


def swap_interface_value(mod: NodesModifier, ent0: str, ent1: str) -> None:
    val0 = get_interface_value(mod, ent0)
    val1 = get_interface_value(mod, ent1)
    set_interface_value(mod, (ent1, val0))
    set_interface_value(mod, (ent0, val1))


def update_node_interface(mod: NodesModifier, context: Context) -> bool:
    if _GN_NEW_API:
        # Blender 5.2+: RNA property writes don't auto-trigger depsgraph update
        mod.id_data.update_tag()
        context.view_layer.update()
    else:
        mod.node_group.interface_update(context)
    return True
