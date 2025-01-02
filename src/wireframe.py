import bpy
from bpy.types import Scene, Object, Context
from bpy.app.handlers import persistent
from .aux_func import make_primitive_property_name, is_primitive_mod


class ObjectHold:
    # Entry name to save the original wireframe state
    # (before the wireframe is forcibly displayed by the add-on)
    ENTRY_NAME = make_primitive_property_name("original_wireframe_state")

    def __init__(self):
        self._obj: Object | None = None
        # Is there a state update request from the drawing hook? (on_draw_hook)
        self._draw_hook_called = False

    # Switch target object
    def _set_target(self, obj: Object | None) -> None:
        assert self._obj != obj
        ent_name = self.__class__.ENTRY_NAME

        # Restore wireframe drawing state
        if self._obj is not None:
            if self._obj_is_alive():
                # Restore previously selected objects from propertry
                self._obj.show_wire = self._obj.get(ent_name, False)
                # Delete it as it is no longer used
                del self._obj[ent_name]

        self._obj = obj

        # Set the object to wireframe drawing state
        if obj is not None:
            # Save the wireframe state (we don't just use obj.show_wire,
            #   to deal with when we duplicate or append a primitive)
            obj[ent_name] = obj.get(ent_name, obj.show_wire)
            # Display objects in wireframe
            self._obj.show_wire = True

    # Is the object valid in blender?
    def _obj_is_alive(self) -> bool:
        assert self._obj is not None
        try:
            return bool(self._obj.name) or True
        except ReferenceError:
            return False

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
        return (
            self.__class__._obj_is_eligible(self._obj, act, sel)
            and self._obj_is_alive()
        )

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
        if act is not None:
            if self.__class__._obj_is_eligible(act, act, sel):
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


target_obj = ObjectHold()
handler_deps_update = bpy.app.handlers.depsgraph_update_post
handler_loadpost = bpy.app.handlers.load_post


@persistent
def on_deps(scene: Scene) -> None:
    global target_obj

    context: Context = bpy.context
    if context.mode != "OBJECT":
        return
    target_obj.check_state(context.active_object, context.selected_objects)


def on_draw_hook(self, context: Context):
    global target_obj

    if context.mode != "OBJECT":
        return
    target_obj.on_draw_hook(context)


@persistent
def load_handler(new_file: str):
    on_deps(bpy.context.scene)
    on_draw_hook(None, bpy.context)


def register() -> None:
    handler_deps_update.append(on_deps)
    handler_loadpost.append(load_handler)
    # For detect modifier's active state switching
    bpy.types.TOPBAR_HT_upper_bar.append(on_draw_hook)


def unregister() -> None:
    handler_deps_update.remove(on_deps)
    handler_loadpost.remove(load_handler)
    bpy.types.TOPBAR_HT_upper_bar.remove(on_draw_hook)
