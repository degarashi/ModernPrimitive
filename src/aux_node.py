from bpy.types import (
    NodeGroup,
    NodeGroupInput,
    NodesModifier,
    Context,
)
from typing import Any, Iterable, Callable


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


def get_interface_value(mod: NodesModifier, name: str) -> Any:
    sock_name = find_interface_name(mod.node_group, name)
    return mod[sock_name]


def get_interface_values(mod: NodesModifier, data: Iterable[str]) -> dict[str, Any]:
    ret: dict[str, Any] = {}
    for d in data:
        ret[d] = get_interface_value(mod, d)
    return ret


def modify_interface_value(
    mod: NodesModifier, ent: str, proc: Callable[[Any], Any]
) -> None:
    value = proc(get_interface_value(mod, ent))
    set_interface_value(mod, (ent, value))


def swap_interface_value(mod: NodesModifier, ent0: str, ent1: str) -> None:
    val0 = get_interface_value(mod, ent0)
    val1 = get_interface_value(mod, ent1)
    set_interface_value(mod, (ent1, val0))
    set_interface_value(mod, (ent0, val1))


def update_node_interface(mod: NodesModifier, context: Context) -> bool:
    mod.node_group.interface_update(context)
