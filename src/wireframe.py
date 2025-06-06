from typing import ClassVar

import bpy
from bpy.app.handlers import persistent
from bpy.types import Context, Object, Scene

from .util.aux_func import is_primitive_mod, make_primitive_property_name, obj_is_alive

# Entry name to save the original wireframe state
# (before the wireframe is forcibly displayed by the add-on)
ENTRY_NAME = make_primitive_property_name("original_wireframe_state")


class ObjectHold:
    def __init__(self):
        self._obj: Object | None = None
        # Is there a state update request from the drawing hook? (on_draw_hook)
        self._draw_hook_called = False

    # Switch target object
    def _set_target(self, obj: Object | None) -> None:
        assert self._obj != obj
        ent_name = ENTRY_NAME

        # Restore wireframe drawing state
        if self._obj is not None and obj_is_alive(self._obj):
            try:
                # Restore previously selected objects from propertry
                self._obj.show_wire = self._obj[ent_name]
                # Delete it as it is no longer used
                del self._obj[ent_name]
            except KeyError:
                self._obj.show_wire = False

        self._obj = obj

        # Set the object to wireframe drawing state
        if obj is not None:
            # Save the wireframe state (we don't just use obj.show_wire,
            #   to deal with when we duplicate or append a primitive)
            obj[ent_name] = obj.get(ent_name, obj.show_wire)
            # Display objects in wireframe
            self._obj.show_wire = True

    # Determine whether the object is eligible for wireframe display
    @staticmethod
    def _obj_is_eligible(obj: Object, act: Object | None, sel: list[Object]) -> bool:
        assert obj is not None
        # Check: target is active object and selected
        if obj == act and obj in sel:
            # has the modern primitive modifier and it is selected
            for mod in obj.modifiers:
                if is_primitive_mod(mod):
                    return mod.show_viewport and mod.is_active
        return False

    # Determine whether the object should show wireframe
    def _obj_is_still_eligible(self, act: Object | None, sel: list[Object]) -> bool:
        assert self._obj is not None
        return self.__class__._obj_is_eligible(self._obj, act, sel) and obj_is_alive(self._obj)

    def check_state(self, act: Object | None, sel: list[Object]) -> None:
        # Determine whether the currently selected object is still valid
        if self._obj is not None:
            if not self._obj_is_still_eligible(act, sel):
                # Since the target is invalid, set it to none once
                self._set_target(None)

            else:
                # still valid
                return

        assert self._obj is None

        # If there is a new target(eligible) object, set it here
        if act is not None and self.__class__._obj_is_eligible(act, act, sel):
            self._set_target(act)
            return

    def _on_draw_hook_async(self) -> None:
        self._draw_hook_called = False
        ctx = bpy.context
        self.check_state(ctx.active_object, ctx.selected_objects)

    def on_draw_hook(self, context: Context) -> None:
        # We want to judge the wireframe display,
        #   but since we can't change the display state of the object here.
        # We have to process it again using the application timer.

        # Provide some grace time to reduce the frequency of callbacks
        if not self._draw_hook_called:
            self._draw_hook_called = True
            bpy.app.timers.register(self._on_draw_hook_async, first_interval=0.1)


class LocalValue:
    target_obj: ClassVar[ObjectHold] = ObjectHold()


@persistent
def on_deps(scene: Scene) -> None:
    context: Context = bpy.context
    if context.mode != "OBJECT":
        return
    LocalValue.target_obj.check_state(context.active_object, context.selected_objects)


def on_draw_hook(self, context: Context):
    if context.mode != "OBJECT":
        return
    LocalValue.target_obj.on_draw_hook(context)


@persistent
def load_handler(new_file: str):
    on_deps(bpy.context.scene)
    on_draw_hook(None, bpy.context)


handler_deps_update = bpy.app.handlers.depsgraph_update_post
handler_loadpost = bpy.app.handlers.load_post


def register() -> None:
    if on_deps not in handler_deps_update:
        handler_deps_update.append(on_deps)
    if load_handler not in handler_loadpost:
        handler_loadpost.append(load_handler)
    # For detect modifier's active state switching
    bpy.types.TOPBAR_HT_upper_bar.append(on_draw_hook)


def unregister() -> None:
    if on_deps in handler_deps_update:
        handler_deps_update.remove(on_deps)
    if load_handler in handler_loadpost:
        handler_loadpost.remove(load_handler)
    bpy.types.TOPBAR_HT_upper_bar.remove(on_draw_hook)
