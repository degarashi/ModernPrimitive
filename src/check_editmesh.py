import bpy
from bpy.types import Scene, Context
from bpy.app.handlers import persistent
from .aux_func import is_modern_primitive
from .text import TextDrawer

textdraw_warning = TextDrawer("Warning: Editing ModernPrimitive's Basemesh")


# Active Object または SelectedObjectsにModernPrimitiveが含まれている
def has_primitive_mesh(context: Context) -> bool:
    objs = context.selected_objects[:]
    act = context.active_object
    if act is not None:
        objs.append(act)

    for obj in objs:
        if is_modern_primitive(obj):
            return True


@persistent
def check_editmesh(scene: Scene):
    context = bpy.context
    if context.mode == "EDIT_MESH":
        if has_primitive_mesh(context):
            if textdraw_warning.show(context):
                context.area.tag_redraw()
            return
    if textdraw_warning.hide(context):
        context.area.tag_redraw()


@persistent
def load_handler(new_file: str):
    check_editmesh(bpy.context.scene)


handler_depsh_update = bpy.app.handlers.depsgraph_update_post
handler_loadpost = bpy.app.handlers.load_post


def register() -> None:
    handler_depsh_update.append(check_editmesh)
    handler_loadpost.append(load_handler)


def unregister() -> None:
    # if textdrawer is draweing something, hide it now
    textdraw_warning.hide(bpy.context)

    handler_depsh_update.remove(check_editmesh)
    handler_loadpost.remove(load_handler)
