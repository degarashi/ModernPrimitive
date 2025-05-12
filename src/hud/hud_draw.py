from typing import Any, ClassVar, cast

import blf
import bpy
from bpy.props import BoolProperty
from bpy.types import Context, Object, Operator, SpaceView3D
from bpy.utils import register_class, unregister_class

from ..aux_func import (
    get_addon_preferences,
    get_evaluated_mesh,
    get_mpr_modifier,
    is_modern_primitive,
    type_from_modifier_name,
)
from ..constants import MODERN_PRIMITIVE_PREFIX, Type
from ..exception import DGUnknownType
from ..gizmo_info import get_gizmo_info
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

PROCS: dict[Type, Any] = {
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

    __handle = None
    show: BoolProperty(name="Show HUD", default=True)

    @classmethod
    def is_running(cls) -> bool:
        return cls.__handle is not None

    @classmethod
    def __handle_add(cls, context: Context) -> None:
        if not cls.is_running():
            cls.__handle = SpaceView3D.draw_handler_add(
                cls.__draw, (context,), "WINDOW", "POST_PIXEL"
            )

    @classmethod
    def __handle_remove(cls, context: Context) -> None:
        if cls.is_running():
            SpaceView3D.draw_handler_remove(cls.__handle, "WINDOW")
            cls.__handle = None

    @classmethod
    def cleanup(cls) -> None:
        cls.__handle_remove(bpy.context)

    @classmethod
    def __draw(cls, context: Context) -> None:
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

            # ------ Get Gizmo Positions ------
            mesh = get_evaluated_mesh(context, obj)
            gizmo_info = get_gizmo_info(mesh)

            QUADVIEW_NUM = 4
            # In quad view mode,
            # scale values are not displayed except for the upper-right view
            if (
                len(space.region_quadviews) == QUADVIEW_NUM
                and space.region_quadviews[-1] != reg3d
            ):
                show_hud = False
            with Drawer(blf, context, obj.matrix_world) as drawer:
                if show_hud:
                    drawer.show_hud(obj.scale)
                PROCS[typ](get_mpr_modifier(obj.modifiers), drawer, gizmo_info)

        except DGUnknownType:
            pass

    def execute(self, context: Context) -> set[str]:
        cls = MPR_Hud
        if self.show:
            cls.__handle_add(context)
        else:
            cls.__handle_remove(context)
        return {"FINISHED"}

    # Display status of gizmo values from preferences
    show_value_flag: ClassVar[bool | None] = None


# Set the gizmo value only once for the first time
def init_gizmo_value_show() -> None:
    # Enabled by default for now
    bpy.ops.ui.mpr_show_hud(show=True)

    # Do nothing if the flag value is not set due to some mistake
    if MPR_Hud.show_value_flag is None:
        pass
    else:
        # Set gizmo value display according to preferences value
        bpy.ops.ui.mpr_show_hud(show=MPR_Hud.show_value_flag)

        # Set the flag value to the window manager property value
        bpy.context.window_manager.show_gizmo_values = MPR_Hud.show_value_flag


def register() -> None:
    # show-gizmo flag from preferences
    MPR_Hud.show_value_flag = get_addon_preferences(bpy.context).show_gizmo_value

    register_class(MPR_Hud)
    # This means not calling the operator now,
    # but after initialization is complete, but there may be a better way.
    bpy.app.timers.register(init_gizmo_value_show, first_interval=0)


def unregister() -> None:
    MPR_Hud.cleanup()
    unregister_class(MPR_Hud)
