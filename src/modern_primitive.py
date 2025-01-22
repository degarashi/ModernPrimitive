import bpy
from . import aux_func
from bpy.types import Context, Menu, bpy_struct
from . import make_primitive as dg_ops
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
            dg_ops.make_operator_to_layout(context, layout, ops)


def menu_func(self, context: Context) -> None:
    layout = self.layout
    layout.menu(VIEW3D_MT_mesh_modern_prim.bl_idname, icon="PACKAGE")
    layout.separator()


MENU_TARGET = bpy.types.VIEW3D_MT_mesh_add
MENUS: list[type[bpy_struct]] = [
    VIEW3D_MT_mesh_modern_prim,
]


def gizmo_props(self, context: Context):
    layout = self.layout
    layout.separator()
    layout.label(text="Modern Primitive")
    layout.prop(context.window_manager, "show_gizmo_values")


def update_show_gizmo_values(self, context: Context) -> None:
    should_show = context.window_manager.show_gizmo_values
    bpy.ops.ui.mpr_show_hud(show=should_show)


def register() -> None:
    aux_func.register_class(MENUS)
    dg_ops.register()
    MENU_TARGET.prepend(menu_func)

    bpy.types.WindowManager.show_gizmo_values = bpy.props.BoolProperty(
        name="Show Gizmo Values", default=True, update=update_show_gizmo_values
    )
    bpy.types.VIEW3D_PT_gizmo_display.append(gizmo_props)


def unregister() -> None:
    aux_func.unregister_class(MENUS)
    dg_ops.unregister()
    MENU_TARGET.remove(menu_func)

    bpy.types.VIEW3D_PT_gizmo_display.remove(gizmo_props)
    del bpy.types.WindowManager.show_gizmo_values
