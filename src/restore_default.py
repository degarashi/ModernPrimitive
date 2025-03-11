from typing import Any, ClassVar

import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Context, Object, Operator
from bpy.utils import register_class, unregister_class

from . import primitive as P
from .aux_func import (
    get_blend_file_path,
    get_mpr_modifier,
    get_selected_primitive,
    type_from_modifier_name,
)
from .aux_node import get_interface_values, set_interface_values
from .constants import MODERN_PRIMITIVE_PREFIX, Type
from .primitive_prop import Prop, PropType, prop_from_name

reset_list = (
    ("All", "All", "Around XYZ axis"),
    ("Width", "Width", "Around XY axis"),
    ("Height", "Height", "Around Z axis"),
)


class RestoreDefault_Operator(Operator):
    """Restore primitive parameteres to default"""

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_restore_default"
    bl_label = "Restore Primitive Paramteres To Default"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    reset_size: BoolProperty(name="Reset Size", default=True)
    reset_size_mode: EnumProperty(name="Size Mode", items=reset_list, default="All")
    reset_division: BoolProperty(name="Reset Division", default=True)
    reset_division_mode: EnumProperty(
        name="Division Mode", items=reset_list, default="All"
    )
    reset_other: BoolProperty(name="Other", default=True)

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        return len(get_selected_primitive(context)) > 0

    def draw(self, context: Context):
        layout = self.layout

        layout.prop(self, "reset_size")
        if self.reset_size:
            layout.prop(self, "reset_size_mode")

        layout.prop(self, "reset_division")
        if self.reset_division:
            layout.prop(self, "reset_division_mode")

        layout.prop(self, "reset_other")

    def execute(self, context: Context) -> set[str]:
        sel = get_selected_primitive(context)
        for obj in sel:
            mod = get_mpr_modifier(obj.modifiers)
            typ = type_from_modifier_name(mod.name)
            def_val = get_default_value(typ)

            params: list[tuple[str, Any]] = []
            for k, v in def_val.items():
                valid = False
                if k.has_tag(PropType.Size) and self.reset_size:
                    match self.reset_size_mode:
                        case "All":
                            valid = True
                        case "Width":
                            valid |= k.has_tag(PropType.Width)
                        case "Height":
                            valid |= k.has_tag(PropType.Height)

                if k.has_tag(PropType.Division) and self.reset_division:
                    match self.reset_division_mode:
                        case "All":
                            valid = True
                        case "Width":
                            valid |= k.has_tag(PropType.Width)
                        case "Height":
                            valid |= k.has_tag(PropType.Height)

                if k.has_tag(PropType.Other) and self.reset_other:
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
        param_values = get_interface_values(get_mpr_modifier(obj.modifiers), param_names)
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
