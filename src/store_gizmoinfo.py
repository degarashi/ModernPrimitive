from typing import ClassVar

import bpy
from bpy.app.handlers import persistent
from bpy.types import Depsgraph, Mesh, Scene

from .aux_func import is_modern_primitive
from .gizmo_info import GizmoInfoAr, get_gizmo_info as _get_gizmo_info


class LocalValue:
    gizmo_info: ClassVar[GizmoInfoAr | None] = None


def get_gizmo_info() -> GizmoInfoAr | None:
    return LocalValue.gizmo_info


@persistent
def store_gizmoinfo_handler(scene: Scene, depsgraph: Depsgraph):
    LocalValue.gizmo_info = None

    active_obj = bpy.context.active_object
    if not active_obj:
        return

    evaluated_obj = active_obj.evaluated_get(depsgraph)
    if not evaluated_obj or not is_modern_primitive(evaluated_obj):
        return

    if evaluated_obj.type == "MESH":
        evaluated_mesh: Mesh | None = evaluated_obj.data
        if evaluated_mesh:
            LocalValue.gizmo_info = _get_gizmo_info(evaluated_mesh)
            return


@persistent
def onload_handler(new_file: str):
    store_gizmoinfo_handler(bpy.context.scene, bpy.context.evaluated_depsgraph_get())


handler_deps_update = bpy.app.handlers.depsgraph_update_post
handler_loadpost = bpy.app.handlers.load_post


def register() -> None:
    if store_gizmoinfo_handler not in handler_deps_update:
        handler_deps_update.append(store_gizmoinfo_handler)
    if onload_handler not in handler_loadpost:
        handler_loadpost.append(onload_handler)


def unregister() -> None:
    if store_gizmoinfo_handler in handler_deps_update:
        handler_deps_update.remove(store_gizmoinfo_handler)
    if onload_handler in handler_loadpost:
        handler_loadpost.remove(onload_handler)
