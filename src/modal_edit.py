from typing import Any, ClassVar

import bpy
from bpy.types import Context, Event, Operator
from idprop.types import IDPropertyArray
from mathutils import Vector

from . import primitive_prop as P
from .primitive import TYPE_TO_PRIMITIVE
from .text import TextDrawer
from .hud.modal_edit_hud import ModalEditHUD
from .util.aux_func import (
    get_active_and_selected_primitive,
    get_mpr_modifier,
    is_modern_primitive,
    type_from_modifier_name,
)
from .util.aux_node import (
    get_interface_value,
    get_interface_values,
    set_interface_value,
    update_node_interface,
)


def expand_idarray(val: Any) -> Any:
    if isinstance(val, IDPropertyArray):
        return val.to_list()
    return val


def get_prop_shortcuts(prop_name: str) -> list[str]:
    name = prop_name.upper()
    keys = []

    # Map of keywords contained in property names and corresponding shortcut keys
    SHORTCUT_MAP: dict[str, str] = {
        "GLOBAL": "G",
        "SIZE": "S",
        "HEIGHT": "H",
        "WIDTH": "W",
        " X": "X",
        " Y": "Y",
        " Z": "Z",
    }

    for keyword, key in SHORTCUT_MAP.items():
        if keyword in name:
            keys.append(key)

    # RADIUS types are evaluated exclusively
    if "RADIUS" in name:
        if "TOP" in name:
            keys.append("T")
        elif "BOTTOM" in name:
            keys.append("B")
        elif "RING" in name:
            keys.append("R")
        elif "OUTER" in name:
            keys.append("O")
        elif "INNER" in name:
            keys.append("I")
        else:
            keys.append("R")

    # DIV types may contain multiple entries, so evaluate each separately
    if "DIV" in name:
        if "SIDE" in name:
            keys.append("S")
        if "FILL" in name:
            keys.append("F")
        if "CIRCLE" in name:
            keys.append("C")
        if "RING" in name:
            keys.append("R")
        if "CAP" in name:
            keys.append("P")

    # If no shortcut is found, use the first character
    if not keys and name:
        keys.append(name[0])
    return keys


class MPR_OT_modal_edit(Operator):
    """Modal operator to edit Modern Primitive properties"""

    _obj: bpy.types.Object | None
    _mod: bpy.types.Modifier | None
    _params: set[str] | None
    _initial_values: dict[str, any] | None
    _input_str: str
    _mode: str
    _text_drawer: TextDrawer | None

    _modes: list[str]
    """List of all available editing modes."""
    _mode_to_prop: dict[str, tuple[P.Prop, int | None]]
    """Mapping from mode name to (Property, ComponentIndex)."""
    _key_to_modes: dict[str, list[str]]
    """Mapping from keyboard key to a list of modes to cycle through."""
    _primitive_name: str
    """Name of the primitive being edited (for display)."""

    bl_idname = "object.mpr_modal_edit"
    bl_label = "Modal Edit Modern Primitive"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    def __init__(self):
        self._obj = None
        self._mod = None
        self._params = None
        self._initial_values = None
        self._input_str = ""
        self._mode = ""
        self._text_drawer = None
        self._modes = []
        self._mode_to_prop = {}
        self._key_to_modes = {}
        self._primitive_name = ""

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if context is None:
            return False
        obj = get_active_and_selected_primitive(context)
        return obj is not None and is_modern_primitive(obj)

    def _init_modes(self, primitive_class: type):
        self._modes = []
        self._mode_to_prop = {}
        self._key_to_modes = {}

        for prop in primitive_class.get_params():
            prop_modes = []
            if prop.type == Vector:
                # All components
                name_all = prop.name
                prop_modes.append(name_all)
                self._mode_to_prop[name_all] = (prop, None)

                # Individual components
                for i, axis in enumerate(["X", "Y", "Z"]):
                    name_comp = "{0} {1}".format(prop.name, axis)
                    prop_modes.append(name_comp)
                    self._mode_to_prop[name_comp] = (prop, i)
            else:
                prop_modes.append(prop.name)
                self._mode_to_prop[prop.name] = (prop, None)

            self._modes.extend(prop_modes)

            # Assign keys
            keys = get_prop_shortcuts(prop.name)
            for k in keys:
                if k not in self._key_to_modes:
                    self._key_to_modes[k] = []
                self._key_to_modes[k].extend(prop_modes)

        if self._modes:
            self._mode = self._modes[0]

    def modal(self, context: Context, event: Event) -> set[str]:
        context.area.tag_redraw()

        # Confirm with Enter key or left click
        if event.type in {"RET", "NUMPAD_ENTER"} or (
            event.type == "LEFTMOUSE" and event.value == "PRESS"
        ):
            self.finish(context)
            return {"FINISHED"}

        # Cancel with Escape key or right click
        if event.type in {"ESC"} or (event.type == "RIGHTMOUSE" and event.value == "PRESS"):
            self.cancel(context)
            return {"CANCELLED"}

        # Mouse wheel handling
        if event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            if event.shift:
                if event.type == "WHEELDOWNMOUSE":
                    current_idx = self._modes.index(self._mode)
                    self._mode = self._modes[(current_idx + 1) % len(self._modes)]
                elif event.type == "WHEELUPMOUSE":
                    current_idx = self._modes.index(self._mode)
                    self._mode = self._modes[(current_idx - 1) % len(self._modes)]

                self._input_str = ""
                self._update_text()
                return {"RUNNING_MODAL"}
            return {"PASS_THROUGH"}

        # Switch items with Tab key (reverse order with Shift+Tab)
        if event.type == "TAB" and event.value == "PRESS":
            current_idx = self._modes.index(self._mode)
            if event.shift:
                self._mode = self._modes[(current_idx - 1) % len(self._modes)]
            else:
                self._mode = self._modes[(current_idx + 1) % len(self._modes)]

            self._input_str = ""
            self._update_text()
            return {"RUNNING_MODAL"}

        if event.type in {"MIDDLEMOUSE", "TRACKPADPAN", "TRACKPADZOOM"}:
            return {"PASS_THROUGH"}

        if event.value == "PRESS":
            # Handle numeric input
            if event.ascii.isdigit() or event.ascii in {".", "-"}:
                self._input_str += event.ascii
                self._update_value(context)

            # Backspace behavior
            elif event.type == "BACK_SPACE":
                if len(self._input_str) > 0:
                    self._input_str = self._input_str[:-1]
                    self._update_value(context)
                else:
                    # 💡 If Backspace is pressed with no text input, reset to default (value at start of editing)
                    self._reset_current_property(context)

            # Handle mode switching via keyboard
            else:
                key = event.type
                if key in self._key_to_modes:
                    target_modes = self._key_to_modes[key]
                    if self._mode in target_modes:
                        idx = target_modes.index(self._mode)
                        self._mode = target_modes[(idx + 1) % len(target_modes)]
                    else:
                        self._mode = target_modes[0]
                    self._input_str = ""

        self._update_text()
        return {"RUNNING_MODAL"}

    def invoke(self, context: Context, event: Event) -> set[str]:
        self._obj = get_active_and_selected_primitive(context)
        self._mod = get_mpr_modifier(self._obj.modifiers)

        type_c = type_from_modifier_name(self._mod.name)
        primitive_class = TYPE_TO_PRIMITIVE[type_c]
        self._primitive_name = primitive_class.type_name
        self._params = primitive_class.get_param_names()

        # Initialize modes dynamically from primitive parameters
        self._init_modes(primitive_class)

        # Save initial values for cancellation
        self._initial_values = get_interface_values(self._mod, self._params)
        for val in self._initial_values:
            self._initial_values[val] = expand_idarray(self._initial_values[val])

        self._input_str = ""

        self._text_drawer = TextDrawer("", draw_func=ModalEditHUD())
        self._text_drawer.show(context)
        self._update_text()

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def finish(self, context: Context) -> None:
        if self._text_drawer:
            self._text_drawer.hide(context)

    def cancel(self, context: Context) -> None:
        if self._initial_values:
            for name, val in self._initial_values.items():
                set_interface_value(self._mod, (name, val))
            update_node_interface(self._mod, context)
            context.view_layer.update()

        if self._text_drawer:
            self._text_drawer.hide(context)

    def _reset_current_property(self, context: Context) -> None:
        """💡 Reset the currently selected property to its value at the start of editing"""
        if not self._initial_values:
            return

        prop, idx = self._mode_to_prop[self._mode]
        initial_val = self._initial_values.get(prop.name)

        if initial_val is None:
            return

        if prop.type == Vector:
            if idx is None:
                # Reset all axes
                set_interface_value(self._mod, (prop.name, tuple(initial_val)))
            else:
                # Reset only the selected single axis
                current_val = list(expand_idarray(get_interface_value(self._mod, prop.name)))
                current_val[idx] = initial_val[idx]
                set_interface_value(self._mod, (prop.name, tuple(current_val)))
        else:
            # Reset int or float
            set_interface_value(self._mod, (prop.name, initial_val))

        update_node_interface(self._mod, context)

    def _update_value(self, context: Context) -> None:
        if not self._input_str or self._input_str in {"-", "."}:
            return

        try:
            val = float(self._input_str)
        except ValueError:
            return

        prop, idx = self._mode_to_prop[self._mode]

        if prop.type == Vector:
            current_val = list(expand_idarray(get_interface_value(self._mod, prop.name)))
            if idx is None:
                new_val = [max(0.001, val)] * 3
            else:
                current_val[idx] = max(0.001, val)
                new_val = current_val
            set_interface_value(self._mod, (prop.name, tuple(new_val)))

        elif prop.type == int:
            val_int = int(val)
            val_int = max(1, min(100, val_int))
            set_interface_value(self._mod, (prop.name, val_int))

        elif prop.type == float:
            if "DIV" in prop.name.upper():
                val = max(0.001, min(100.0, val))
            else:
                val = max(0.001, val)
            set_interface_value(self._mod, (prop.name, val))

        update_node_interface(self._mod, context)

    def _update_text(self) -> None:
        vals = get_interface_values(self._mod, self._params)
        msg = "MPR Modal Edit ({0})\n".format(self._primitive_name)
        current_input = self._input_str if self._input_str else "-"
        msg += "Mode: {0} | Input: {1}\n".format(self._mode, current_input)
        msg += "---------------------------------\n"

        # Dynamically build property list for display
        displayed_props = set()
        for mode_name in self._modes:
            prop, idx = self._mode_to_prop[mode_name]
            if prop.name in displayed_props and idx is None:
                continue

            prefix = "▶ " if self._mode == mode_name else "  "
            val = vals[prop.name]

            # 💡 Get initial value
            init_val = self._initial_values.get(prop.name) if self._initial_values else None

            if prop.type == Vector:
                vec = expand_idarray(val)
                init_vec = expand_idarray(init_val) if init_val is not None else vec

                if idx is None:
                    msg += "{0}{1} (All) | {2:.3f}, {3:.3f}, {4:.3f} ({5:.3f}, {6:.3f}, {7:.3f})\n".format(
                        prefix,
                        prop.name,
                        vec[0],
                        vec[1],
                        vec[2],
                        init_vec[0],
                        init_vec[1],
                        init_vec[2],
                    )
                else:
                    axis_name = ["X", "Y", "Z"][idx]
                    msg += "{0}  {1} {2} | {3:.3f} ({4:.3f})\n".format(
                        prefix, prop.name, axis_name, vec[idx], init_vec[idx]
                    )
            elif prop.type == int:
                init_i = init_val if init_val is not None else val
                msg += "{0}{1} | {2} ({3})\n".format(prefix, prop.name, val, init_i)
            elif prop.type == float:
                init_f = init_val if init_val is not None else val
                msg += "{0}{1} | {2:.3f} ({3:.3f})\n".format(prefix, prop.name, val, init_f)

            if idx is None or idx == 2:
                displayed_props.add(prop.name)

        msg += "---------------------------------\n"
        shortcut_info = " ".join(["[{0}]".format(k) for k in sorted(self._key_to_modes.keys())])
        msg += "{0} [Tab:Next]\n".format(shortcut_info)
        msg += "[L-Click/Enter:Confirm] [R-Click/Esc:Cancel] [BS:Reset]"
        self._text_drawer.set_text(msg)


def draw_menu(self, context):
    layout = self.layout
    layout.operator(MPR_OT_modal_edit.bl_idname, text="Modal Edit (MPR)")


addon_keymaps = []


def _register_keymap() -> None:
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            MPR_OT_modal_edit.bl_idname,
            type="C",
            value="PRESS",
            ctrl=True,
            shift=True,
        )
        addon_keymaps.append((km, kmi))


def _unregister_keymap() -> None:
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register() -> None:
    bpy.utils.register_class(MPR_OT_modal_edit)
    bpy.types.VIEW3D_MT_mesh_add.append(draw_menu)
    _register_keymap()


def unregister() -> None:
    bpy.utils.unregister_class(MPR_OT_modal_edit)
    bpy.types.VIEW3D_MT_mesh_add.remove(draw_menu)
    _unregister_keymap()
