from bpy.types import (
    NodeGroup,
    NodeGroupInput,
    NodesModifier,
    Context,
)
from typing import Any, Iterable


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

