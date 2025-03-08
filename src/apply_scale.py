import math
from collections.abc import Callable
from typing import Any, ClassVar, cast

from bpy.props import BoolProperty
from bpy.types import Context, NodesModifier, Object, Operator
from bpy.utils import register_class, unregister_class
from mathutils import Quaternion, Vector

from . import primitive_prop as prop
from .aux_func import get_selected_primitive
from .aux_math import is_close, is_uniform
from .aux_node import (
    get_interface_value,
    modify_interface_value,
    set_interface_value,
    swap_interface_value,
)
from .constants import MODERN_PRIMITIVE_PREFIX, Type
from .exception import DGInvalidInput
from .version import TypeAndVersion, get_primitive_version

WarnProc = Callable[[str], None]


def _xyz_scale(obj: Object, mod: NodesModifier, max_index: int) -> None:
    SIZE_ENT = (prop.SizeX.name, prop.SizeY.name, prop.SizeZ.name)

    for i in range(max_index):
        scale_val = abs(obj.scale[i])
        modify_interface_value(mod, SIZE_ENT[i], lambda val, s=scale_val: val * s)


def _abs_sum(*args) -> Any:
    s = abs(args[0])
    for a in args[1:]:
        s += abs(a)
    return s


def _abs_average(*args) -> Any:
    return _abs_sum(*args) / len(args)


def _abs_average_xy(vec: Vector) -> float:
    return _abs_average(vec.x, vec.y)


def _abs_average_vec(vec: Vector) -> float:
    return _abs_average(*vec)


def _is_xy_same(vec: Vector) -> bool:
    return is_close(vec.x, vec.y)


def _rotate_x180(obj: Object) -> None:
    rot_mode = obj.rotation_mode
    obj.rotation_mode = "QUATERNION"

    rot_x180 = Quaternion(Vector((1, 0, 0)), math.radians(180))
    obj.rotation_quaternion = obj.rotation_quaternion @ rot_x180

    obj.rotation_mode = rot_mode


def _check_xy_same(vec: Vector, warn: WarnProc) -> None:
    if not _is_xy_same(vec):
        warn(f"Object XY scale is not equal: ({vec.x:.8f}, {vec.y:.8f})")
    elif vec.x < 0:
        warn("Negative XY scaling can change shape")


def proc_cube(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    sc = Vector(
        (
            abs(obj.scale[0]),
            abs(obj.scale[1]),
            abs(obj.scale[2]),
        )
    )
    vec = get_interface_value(mod, prop.Size.name)
    for i in range(3):
        vec[i] *= sc[i]
    set_interface_value(mod, (prop.Size.name, vec))


def proc_cone(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    # -- xy scaling --
    _check_xy_same(obj.scale, warn)

    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, prop.TopRadius.name, lambda val: val * scale_val)
    modify_interface_value(mod, prop.BottomRadius.name, lambda val: val * scale_val)

    # -- z scaling --
    modify_interface_value(mod, prop.Height.name, lambda val: val * abs(obj.scale.z))
    if obj.scale.z < 0:
        _rotate_x180(obj)


def proc_grid(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    _xyz_scale(obj, mod, 2)


def proc_torus(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    if not is_uniform(obj.scale):
        warn("Object is not uniformly scaled")

    scale_val = _abs_average_vec(obj.scale)
    modify_interface_value(mod, prop.Radius.name, lambda val: val * scale_val)
    modify_interface_value(mod, prop.RingRadius.name, lambda val: val * scale_val)


def proc_cylinder(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    # -- xy scaling --
    _check_xy_same(obj.scale, warn)

    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, prop.Radius.name, lambda val: val * scale_val)

    # -- z scaling --
    scale_val = abs(obj.scale.z)
    modify_interface_value(mod, prop.Height.name, lambda val: val * scale_val)
    if obj.scale.z < 0:
        _rotate_x180(obj)


def proc_uvsphere(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    proc_icosphere(obj, mod, warn)


def proc_icosphere(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    # Generate an error if scaling is not uniform
    if not is_uniform(obj.scale):
        warn("Object is not uniformly scaled")

    scale_val = _abs_average_vec(obj.scale)
    modify_interface_value(mod, prop.Radius.name, lambda val: val * scale_val)


def proc_tube(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    _check_xy_same(obj.scale, warn)

    # -- xy scaling --
    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, prop.OuterRadius.name, lambda val: val * scale_val)
    modify_interface_value(mod, prop.InnerRadius.name, lambda val: val * scale_val)

    # -- z scaling --
    scale_val = abs(obj.scale.z)
    modify_interface_value(mod, prop.Height.name, lambda val: val * scale_val)
    if obj.scale.z < 0:
        _rotate_x180(obj)


def proc_gear(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    _check_xy_same(obj.scale, warn)

    # -- xy scaling --
    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, prop.OuterRadius.name, lambda val: val * scale_val)
    modify_interface_value(mod, prop.InnerRadius.name, lambda val: val * scale_val)
    modify_interface_value(
        mod, prop.InnerCircleRadius.name, lambda val: val * scale_val
    )
    modify_interface_value(mod, prop.FilletRadius.name, lambda val: val * scale_val)

    # -- z scaling --
    scale_val = abs(obj.scale.z)
    modify_interface_value(mod, prop.Height.name, lambda val: val * scale_val)


def proc_spring(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    if obj.scale.x < 0 or obj.scale.y < 0 or obj.scale.z < 0:
        raise DGInvalidInput("Negative scaling is not supported")
    if not is_uniform(obj.scale):
        warn("Object is not uniformly scaled")

    scale_val = _abs_average_vec(obj.scale)
    modify_interface_value(mod, prop.BottomRadius.name, lambda val: val * scale_val)
    modify_interface_value(mod, prop.TopRadius.name, lambda val: val * scale_val)
    modify_interface_value(mod, prop.RingRadius.name, lambda val: val * scale_val)
    modify_interface_value(mod, prop.Height.name, lambda val: val * scale_val)


def proc_dcube(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    modify_interface_value(mod, prop.MinX.name, lambda val: val * abs(obj.scale.x))
    modify_interface_value(mod, prop.MaxX.name, lambda val: val * abs(obj.scale.x))
    if obj.scale.x < 0:
        swap_interface_value(mod, prop.MinX.name, prop.MaxX.name)

    modify_interface_value(mod, prop.MinY.name, lambda val: val * abs(obj.scale.y))
    modify_interface_value(mod, prop.MaxY.name, lambda val: val * abs(obj.scale.y))
    if obj.scale.y < 0:
        swap_interface_value(mod, prop.MinY.name, prop.MaxY.name)

    modify_interface_value(mod, prop.MinZ.name, lambda val: val * abs(obj.scale.z))
    modify_interface_value(mod, prop.MaxZ.name, lambda val: val * abs(obj.scale.z))
    if obj.scale.z < 0:
        swap_interface_value(mod, prop.MinZ.name, prop.MaxZ.name)


def proc_capsule(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    if not is_uniform(obj.scale):
        warn("Object is not uniformly scaled")

    # -- xy scaling --
    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, prop.Radius.name, lambda val: val * scale_val)

    # -- z scaling --
    scale_val = abs(obj.scale.z)
    modify_interface_value(mod, prop.Height.name, lambda val: val * scale_val)


def proc_quadsphere(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    proc_icosphere(obj, mod, warn)


apply_proc = Callable[[Object, NodesModifier, WarnProc], None]
PROC_MAP: dict[Type, apply_proc] = {
    Type.Cube: proc_cube,
    Type.Cone: proc_cone,
    Type.Grid: proc_grid,
    Type.Torus: proc_torus,
    Type.Cylinder: proc_cylinder,
    Type.UVSphere: proc_uvsphere,
    Type.ICOSphere: proc_icosphere,
    Type.Tube: proc_tube,
    Type.Gear: proc_gear,
    Type.Spring: proc_spring,
    Type.DeformableCube: proc_dcube,
    Type.Capsule: proc_capsule,
    Type.QuadSphere: proc_quadsphere,
}


class ApplyScale_Operator(Operator):
    """Apply scaling to ModernPrimitive Object"""

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_apply_scale"
    bl_label = "Apply scaling to ModernPrimitive"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    strict: BoolProperty(name="Strict Mode", default=True)

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        return len(get_selected_primitive(context)) > 0

    def warn(self, msg: str) -> None:
        self.report({"WARNING"}, msg)

    def warn_as_error(self, msg: str) -> None:
        raise DGInvalidInput(msg)

    def execute(self, context: Context | None) -> set[str]:
        warn = self.warn if not self.strict else self.warn_as_error
        objs = get_selected_primitive(context)
        for obj in objs:
            typ_ver = TypeAndVersion.get_type_and_version(
                obj.modifiers[0].node_group.name
            )
            if typ_ver is None:
                self.report({"WARNING"}, f"unknown primitive type: {obj.name}")
            else:
                # For now, make sure it doesn't work unless it's the latest version
                if get_primitive_version(typ_ver.type) > typ_ver.version:
                    self.report(
                        {"ERROR"},
                        """Primitive version is not up to date
(Unfortunately, there is no way to update automatically at this time,
 so please convert it manually.)""",
                    )
                    continue

                # is_modern_primitive() assumes modifier number 0,
                # so do that here as well
                mod = obj.modifiers[0]
                mod = cast(NodesModifier, mod)
                try:
                    PROC_MAP[typ_ver.type](obj, mod, warn)
                    # Since the node group value has been changed, update it here
                    mod.node_group.interface_update(context)
                    # reset scale value
                    obj.scale = Vector((1, 1, 1))
                except DGInvalidInput as e:
                    # An error has occurred, notify the contents
                    self.report({"ERROR"}, f"{obj.name}: {e!s}")

        return {"FINISHED"}


def register() -> None:
    register_class(ApplyScale_Operator)


def unregister() -> None:
    unregister_class(ApplyScale_Operator)
