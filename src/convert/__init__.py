from .convert_to_cube import ConvertToCube_Operator
from bpy.utils import register_class, unregister_class


def register() -> None:
    register_class(ConvertToCube_Operator)


def unregister() -> None:
    unregister_class(ConvertToCube_Operator)
