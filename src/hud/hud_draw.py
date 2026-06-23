from collections.abc import Callable
from typing import ClassVar, cast, TypeAlias

import blf
import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty
from bpy.types import Context, Depsgraph, NodesModifier, Object, Operator, Scene, SpaceView3D
from bpy.utils import register_class, unregister_class

from ..constants import MODERN_PRIMITIVE_PREFIX, Type
from ..exception import DGUnknownType
from ..store_gizmoinfo import get_gizmo_info
from ..util.aux_func import (
    get_addon_preferences,
    get_mpr_modifier,
    is_modern_primitive,
    type_from_modifier_name,
)
from ..version import SNAPPING_CAPABLE, TypeAndVersion
from . import (
    capsule,
    cone,
    cube,
    cylinder,
    dcube,
    gear,
    grid,
    icosphere,
    quadsphere,
    spring,
    torus,
    tube,
    uvsphere,
)
from .drawer import Drawer
from ..gizmo_info import GizmoInfoAr

HudProc: TypeAlias = Callable[[NodesModifier, Drawer, GizmoInfoAr, bool], None]
PROCS: dict[Type, HudProc] = {
    Type.Capsule: capsule.draw_hud,
    Type.Cone: cone.draw_hud,
    Type.Cube: cube.draw_hud,
    Type.Cylinder: cylinder.draw_hud,
    Type.DeformableCube: dcube.draw_hud,
    Type.Gear: gear.draw_hud,
    Type.Grid: grid.draw_hud,
    Type.ICOSphere: icosphere.draw_hud,
    Type.QuadSphere: quadsphere.draw_hud,
    Type.Spring: spring.draw_hud,
    Type.Torus: torus.draw_hud,
    Type.Tube: tube.draw_hud,
    Type.UVSphere: uvsphere.draw_hud,
}


def is_primitive_selected(obj: Object | None) -> bool:
    if obj is None or not is_modern_primitive(obj):
        return False
    mod = get_mpr_modifier(obj.modifiers)
    return mod.show_viewport and mod.is_active


class MPR_Hud(Operator):
    bl_idname = f"ui.{MODERN_PRIMITIVE_PREFIX}_show_hud"
    bl_label = "Show/Hide MPR HUD"
    bl_description = "Show/Hide ModernPrimitive HUD"
    bl_options: ClassVar[set[str]] = set()

    _handle = None
    show: BoolProperty(name="Show HUD", default=True)

    @classmethod
    def is_running(cls) -> bool:
        return cls._handle is not None

    @classmethod
    def _handle_add(cls, context: Context) -> None:
        if not cls.is_running():
            cls._handle = SpaceView3D.draw_handler_add(
                cls._draw, (), "WINDOW", "POST_PIXEL"
            )

    @classmethod
    def _handle_remove(cls, context: Context) -> None:
        if cls.is_running():
            SpaceView3D.draw_handler_remove(cls._handle, "WINDOW")
            cls._handle = None

    @classmethod
    def cleanup(cls) -> None:
        cls._handle_remove(bpy.context)

    @classmethod
    def _draw(cls) -> None:
        try:
            context = bpy.context
            # Do not display in any other than object mode
            if context.mode != "OBJECT":
                return

            obj = context.active_object
            if not is_primitive_selected(obj) or obj not in context.selected_objects:
                return

            space = cast(SpaceView3D, context.space_data)
            # Do not display if gizmo display is turned off
            if not (space.show_gizmo and space.show_gizmo_modifier):
                return

            try:
                typ = type_from_modifier_name(get_mpr_modifier(obj.modifiers).name)
                if typ not in PROCS:
                    return

                reg3d = context.region_data
                show_hud = True

                gizmo_info = get_gizmo_info()
                if gizmo_info is None:
                    return

                QUADVIEW_NUM = 4
                # In quad view mode,
                # scale values are not displayed except for the upper-right view
                if (
                    len(space.region_quadviews) == QUADVIEW_NUM
                    and space.region_quadviews[-1] != reg3d
                ):
                    show_hud = False
                prefs = get_addon_preferences(context)
                with Drawer(blf, context, obj.matrix_world, prefs.show_world_space_value) as drawer:
                    if show_hud:
                        drawer.show_hud(obj.scale)

                    mod = get_mpr_modifier(obj.modifiers)
                    typ_ver = TypeAndVersion.get_type_and_version(mod.node_group.name)
                    if typ_ver is None:
                        return
                    is_snap_capable = typ_ver.version >= SNAPPING_CAPABLE
                    PROCS[typ](mod, drawer, gizmo_info, is_snap_capable)

            except DGUnknownType:
                pass
        except Exception:
            pass

    def execute(self, context: Context) -> set[str]:
        cls = MPR_Hud
        if self.show:
            cls._handle_add(context)
        else:
            cls._handle_remove(context)
        return {"FINISHED"}


handler_deps_update = bpy.app.handlers.depsgraph_update_post
handler_loadpost = bpy.app.handlers.load_post
_hud_init_timer = None


class Setting:
    # Display status of gizmo values from preferences
    pref_value: ClassVar[bool | None] = None

    @classmethod
    def _set_window_manager_value(cls, value: bool) -> bool:
        try:
            bpy.context.window_manager.show_gizmo_values = value
            return True
        except Exception:
            try:
                bpy.context.window_manager["show_gizmo_values"] = value
                return True
            except Exception:
                return False

    @classmethod
    def _get_window_manager_value(cls) -> bool | None:
        try:
            return bpy.context.window_manager.show_gizmo_values
        except Exception:
            try:
                return bpy.context.window_manager["show_gizmo_values"]
            except Exception:
                return None

    @classmethod
    def _apply_show_state(cls, should_show: bool) -> None:
        if should_show:
            MPR_Hud._handle_add(bpy.context)
        else:
            MPR_Hud._handle_remove(bpy.context)

    @classmethod
    def _sync_from_window_manager(cls) -> bool:
        should_show = cls._get_window_manager_value()
        if should_show is None:
            return False
        cls.pref_value = should_show
        cls._apply_show_state(should_show)
        return True

    @classmethod
    def _apply_from_pref_value(cls) -> None:
        if cls.pref_value is None:
            should_show: bool = False
            try:
                should_show = get_addon_preferences(bpy.context).show_gizmo_value
            except Exception:
                # Try again later, do not set cls.pref_value yet
                return

            cls.pref_value = should_show
            if not cls._set_window_manager_value(should_show):
                # If setting fails, reset pref_value to try again
                cls.pref_value = None
                return

        if not cls._sync_from_window_manager():
            cls._apply_show_state(cls.pref_value)

    @classmethod
    def on_changed(cls, value: bool) -> None:
        cls.pref_value = value


@persistent
def on_update(scene: Scene, depsgraph: Depsgraph) -> None:
    Setting._apply_from_pref_value()


@persistent
def on_load(*args) -> None:
    Setting._apply_from_pref_value()


def init_hud_deferred() -> float | None:
    try:
        if bpy.context.window_manager is None:
            return 0.1
        Setting._apply_from_pref_value()
        if Setting.pref_value is not None:
            return None
    except Exception:
        pass
    return 0.1


def register() -> None:
    global _hud_init_timer

    register_class(MPR_Hud)

    # Registering handlers
    if on_update not in handler_deps_update:
        handler_deps_update.append(on_update)
    if on_load not in handler_loadpost:
        handler_loadpost.append(on_load)

    # Defer execution to ensure context / window_manager are ready
    _hud_init_timer = bpy.app.timers.register(init_hud_deferred, first_interval=0.1)


def unregister() -> None:
    global _hud_init_timer

    if _hud_init_timer is not None:
        bpy.app.timers.unregister(_hud_init_timer)
        _hud_init_timer = None

    # UnRegistering handlers
    if on_load in handler_loadpost:
        handler_loadpost.remove(on_load)
    if on_update in handler_deps_update:
        handler_deps_update.remove(on_update)

    MPR_Hud.cleanup()
    unregister_class(MPR_Hud)
