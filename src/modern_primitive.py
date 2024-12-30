import bpy
from bpy.types import Context, Menu, bpy_struct
from . import operator as dg_ops
from .constants import MODERN_PRIMITIVE_PREFIX


class VIEW3D_MT_mesh_modern_prim(Menu):
    bl_idname = f"VIEW3D_MT_{MODERN_PRIMITIVE_PREFIX}_append"
    bl_label = "Modern Primitive"

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        return context.mode == "OBJECT"

    def draw(self, context: Context | None) -> None:
        layout = self.layout
        layout.operator_context = "INVOKE_REGION_WIN"

        for ops in dg_ops.OPS:
            layout.operator(
                ops.bl_idname, text=str(ops.menu_text), icon=str(ops.menu_icon)
            )  # pyright: ignore[reportAttributeAccessIssue]


def menu_func(self, context: Context) -> None:
    layout = self.layout
    layout.menu(VIEW3D_MT_mesh_modern_prim.bl_idname, icon="PACKAGE")
    layout.separator()


MENU_TARGET = bpy.types.VIEW3D_MT_mesh_add

MENUS: list[type[bpy_struct]] = [
    VIEW3D_MT_mesh_modern_prim,
]

from . import aux_func


def register() -> None:
    aux_func.register_class(MENUS)
    dg_ops.register()
    MENU_TARGET.prepend(menu_func)


def unregister() -> None:
    aux_func.unregister_class(MENUS)
    dg_ops.unregister()
    MENU_TARGET.remove(menu_func)
