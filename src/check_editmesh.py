import bpy
from typing import Iterable
from bpy.types import Scene, Context, Object
from bpy.app.handlers import persistent
from .aux_func import is_modern_primitive
from .text import TextDrawer

textdraw_warning = TextDrawer("")


def make_warning_message(objs: Iterable[Object]) -> str:
    ret = "Warning: Editing ModernPrimitive's Basemesh"
    for obj in objs:
        ret += "\n"
        ret += f"[{obj.name}]"

    return ret


# get ModernPrimitive from Active object and Selected object
def get_primitive_mesh(context: Context) -> set[Object]:
    ret: set[Object] = set()
    objs = context.selected_objects[:]
    act = context.active_object
    if act is not None:
        objs.append(act)

    for obj in objs:
        if is_modern_primitive(obj):
            ret.add(obj)

    return ret


@persistent
def check_editmesh(scene: Scene):
    context = bpy.context
    if context.mode == "EDIT_MESH":
        pm = get_primitive_mesh(context)
        if len(pm) > 0:
            textdraw_warning.set_text(make_warning_message(pm))
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
