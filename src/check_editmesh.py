from collections.abc import Iterable

import bpy
from bpy.app.handlers import persistent
from bpy.types import Context, Object, Scene

from .aux_func import is_modern_primitive
from .color import HUDColor
from .text import TextDrawer

textdraw_warning = TextDrawer("")


def make_warning_message(objs: Iterable[Object]) -> str:
    ret = "Editing ModernPrimitive's Mesh"
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
        hud_color = HUDColor(context.preferences)
        pm = get_primitive_mesh(context)
        if len(pm) > 0:
            textdraw_warning.set_text(make_warning_message(pm))
            textdraw_warning.set_color(hud_color.white)
            if textdraw_warning.show(context) and context.area is not None:
                context.area.tag_redraw()
            return
    if textdraw_warning.hide(context) and context.area is not None:
        context.area.tag_redraw()


@persistent
def load_handler(new_file: str):
    check_editmesh(bpy.context.scene)


handler_deps_update = bpy.app.handlers.depsgraph_update_post
handler_loadpost = bpy.app.handlers.load_post


def register() -> None:
    handler_deps_update.append(check_editmesh)
    handler_loadpost.append(load_handler)


def unregister() -> None:
    # if textdrawer is draweing something, hide it now
    textdraw_warning.hide(bpy.context)

    handler_deps_update.remove(check_editmesh)
    handler_loadpost.remove(load_handler)
