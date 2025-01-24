import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Operator, Context, Object
from bpy.props import BoolProperty
from typing import Any
from .constants import MODERN_PRIMITIVE_PREFIX, Type
from . import primitive as P
from .primitive_prop import Prop, prop_from_name
from .aux_func import (
    type_from_modifier_name,
    get_selected_primitive,
    get_blend_file_path,
)
from .aux_node import get_interface_values, set_interface_values
from .primitive_prop import PropType


class RestoreDefault_Operator(Operator):
    """Restore primitive parameteres to default"""

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_restore_default"
    bl_label = "Restore Primitive Paramteres To Default"
    bl_options = {"REGISTER", "UNDO"}

    reset_size: BoolProperty(name="Reset Size", default=True)
    reset_division: BoolProperty(name="Reset Division", default=True)

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        return len(get_selected_primitive(context)) > 0

    def execute(self, context: Context) -> set[str]:
        sel = get_selected_primitive(context)
        for obj in sel:
            mod = obj.modifiers[0]
            typ = type_from_modifier_name(mod.name)
            def_val = get_default_value(typ)

            params: list[tuple[str, Any]] = []
            for k, v in def_val.items():
                valid = False
                if self.reset_size and k.has_tag(PropType.Size):
                    valid = True
                if self.reset_division and k.has_tag(PropType.Division):
                    valid = True
                if valid:
                    params.append((k.name, v))
            set_interface_values(mod, context, params)

        return {"FINISHED"}


_default_value: dict[Type, dict[Prop, Any]] = {}


def get_default_value(typ: Type) -> dict[Prop, Any]:
    if typ not in _default_value:
        path = get_blend_file_path(typ, False)
        with bpy.data.libraries.load(str(path)) as (data_from, data_to):
            data_to.objects = [str(typ.name)]

        obj: Object = data_to.objects[0]

        param_names = P.TYPE_TO_PRIMITIVE[typ].get_param_names()

        result: dict[Prop, Any] = {}
        param_values = get_interface_values(obj.modifiers[0], param_names)
        for k, v in param_values.items():
            result[prop_from_name(k)] = v

        # I'm done with it so I'll delete it now
        bpy.data.objects.remove(obj)

        _default_value[typ] = result

    return _default_value[typ]


def register() -> None:
    register_class(RestoreDefault_Operator)


def unregister() -> None:
    unregister_class(RestoreDefault_Operator)
