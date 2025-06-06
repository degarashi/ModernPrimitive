from bpy.types import Operator, Context
from bpy.utils import register_class, unregister_class
from .constants import MODERN_PRIMITIVE_PREFIX
from .util.aux_func import get_active_and_selected_primitive
from .wireframe import ENTRY_NAME as Wireframe_EntryName


class SwitchWireframe(Operator):
    """Toggle the native wireframe display of an object, independent of the add-on's automatic wireframe display feature"""  # noqa: E501

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_switch_wireframe"
    bl_label = "Switch wireframe"

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        return get_active_and_selected_primitive(context) is not None

    def execute(self, context: Context | None) -> set[str]:
        obj = context.view_layer.objects.active
        # object's wireframe is automatically displayed by the add-on function,
        # so it is not correct to simply invert the "show_wire" flag.

        ent_name = Wireframe_EntryName
        try:
            # The original state value is stored in the property object hold.entry name
            original_state: bool = obj[ent_name]
            # Store the flag inverted
            obj[ent_name] = not original_state
        except KeyError:
            # If the original value does not exist for some reason,
            # consider it was False
            obj[ent_name] = True

        self.report({"INFO"}, f"Wireframe display mode changed to {obj[ent_name]}")
        return {"FINISHED"}


def register() -> None:
    register_class(SwitchWireframe)


def unregister() -> None:
    unregister_class(SwitchWireframe)
