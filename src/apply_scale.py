from bpy.utils import register_class, unregister_class
from bpy.props import BoolProperty
from bpy.types import Operator, Context, Object, NodesModifier
from typing import Callable, cast, Any
from mathutils import Vector, Quaternion
from .constants import MODERN_PRIMITIVE_PREFIX, Type
from .aux_func import is_modern_primitive
from .aux_node import swap_interface_value, modify_interface_value
from .version import TypeAndVersion, get_primitive_version
from .exception import DGInvalidInput
import math


WarnProc = Callable[[str], None]


def _xyz_scale(obj: Object, mod: NodesModifier, max_index: int) -> None:
    SIZE_ENT = ("SizeX", "SizeY", "SizeZ")

    for i in range(max_index):
        scale_val = abs(obj.scale[i])
        modify_interface_value(mod, SIZE_ENT[i], lambda val, s=scale_val: val * s)


def _isclose(*args) -> bool:
    base = args[0]
    for a in args[1:]:
        if not math.isclose(base, a, rel_tol=1e-6):
            return False
    return True


def _is_uniform(vec: Vector) -> bool:
    return _isclose(*vec)


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
    return _isclose(vec.x, vec.y)


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
    _xyz_scale(obj, mod, 3)


def proc_cone(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    # -- xy scaling --
    _check_xy_same(obj.scale, warn)

    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, "Radius Top", lambda val: val * scale_val)
    modify_interface_value(mod, "Radius Bottom", lambda val: val * scale_val)

    # -- z scaling --
    modify_interface_value(mod, "Height", lambda val: val * abs(obj.scale.z))
    if obj.scale.z < 0:
        _rotate_x180(obj)


def proc_grid(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    _xyz_scale(obj, mod, 2)


def proc_torus(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    if not _is_uniform(obj.scale):
        warn("Object is not uniformly scaled")

    scale_val = _abs_average_vec(obj.scale)
    modify_interface_value(mod, "Radius", lambda val: val * scale_val)
    modify_interface_value(mod, "SecondaryRadius", lambda val: val * scale_val)


def proc_cylinder(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    # -- xy scaling --
    _check_xy_same(obj.scale, warn)

    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, "Radius", lambda val: val * scale_val)

    # -- z scaling --
    scale_val = abs(obj.scale.z)
    modify_interface_value(mod, "Height", lambda val: val * scale_val)
    if obj.scale.z < 0:
        _rotate_x180(obj)


def proc_uvsphere(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    proc_icosphere(obj, mod, warn)


def proc_icosphere(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    # Generate an error if scaling is not uniform
    if not _is_uniform(obj.scale):
        warn("Object is not uniformly scaled")

    scale_val = _abs_average_vec(obj.scale)
    # TODO: The variable name is hard-coded, so do something about it
    modify_interface_value(mod, "Radius", lambda val: val * scale_val)


def proc_tube(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    _check_xy_same(obj.scale, warn)

    # -- xy scaling --
    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, "OuterRadius", lambda val: val * scale_val)
    modify_interface_value(mod, "InnerRadius", lambda val: val * scale_val)

    # -- z scaling --
    scale_val = abs(obj.scale.z)
    modify_interface_value(mod, "Height", lambda val: val * scale_val)
    if obj.scale.z < 0:
        _rotate_x180(obj)


def proc_gear(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    _check_xy_same(obj.scale, warn)

    # -- xy scaling --
    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, "Outer Radius", lambda val: val * scale_val)
    modify_interface_value(mod, "Inner Radius", lambda val: val * scale_val)
    modify_interface_value(mod, "InnerCircle Radius", lambda val: val * scale_val)
    modify_interface_value(mod, "Fillet Radius", lambda val: val * scale_val)

    # -- z scaling --
    scale_val = abs(obj.scale.z)
    modify_interface_value(mod, "Height", lambda val: val * scale_val)


def proc_spring(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    if obj.scale.x < 0 or obj.scale.y < 0 or obj.scale.z < 0:
        raise DGInvalidInput("Negative scaling is not supported")
    if not _is_uniform(obj.scale):
        warn("Object is not uniformly scaled")

    scale_val = _abs_average_vec(obj.scale)
    modify_interface_value(mod, "Start Radius", lambda val: val * scale_val)
    modify_interface_value(mod, "End Radius", lambda val: val * scale_val)
    modify_interface_value(mod, "Ring Radius", lambda val: val * scale_val)
    modify_interface_value(mod, "Height", lambda val: val * scale_val)


def proc_dcube(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    modify_interface_value(mod, "MinX", lambda val: val * abs(obj.scale.x))
    modify_interface_value(mod, "MaxX", lambda val: val * abs(obj.scale.x))
    if obj.scale.x < 0:
        swap_interface_value(mod, "MinX", "MaxX")

    modify_interface_value(mod, "MinY", lambda val: val * abs(obj.scale.y))
    modify_interface_value(mod, "MaxY", lambda val: val * abs(obj.scale.y))
    if obj.scale.y < 0:
        swap_interface_value(mod, "MinY", "MaxY")

    modify_interface_value(mod, "MinZ", lambda val: val * abs(obj.scale.z))
    modify_interface_value(mod, "MaxZ", lambda val: val * abs(obj.scale.z))
    if obj.scale.z < 0:
        swap_interface_value(mod, "MinZ", "MaxZ")


def proc_capsule(obj: Object, mod: NodesModifier, warn: WarnProc) -> None:
    if not _is_uniform(obj.scale):
        warn("Object is not uniformly scaled")

    # -- xy scaling --
    scale_val = _abs_average_xy(obj.scale)
    modify_interface_value(mod, "Radius", lambda val: val * scale_val)

    # -- z scaling --
    scale_val = abs(obj.scale.z)
    modify_interface_value(mod, "Height", lambda val: val * scale_val)


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


def _get_selected_primitive(context: Context) -> list[Object]:
    ret: list[Object] = []
    sel = context.selected_objects
    for obj in sel:
        if is_modern_primitive(obj):
            ret.append(obj)
    return ret


class ApplyScale_Operator(Operator):
    """Apply scaling to ModernPrimitive Object"""

    bl_idname = f"object.{MODERN_PRIMITIVE_PREFIX}_apply_scale"
    bl_label = "Apply scaling to ModernPrimitive"
    bl_options = {"REGISTER", "UNDO"}

    strict: BoolProperty(name="Strict Mode", default=True)

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        return len(_get_selected_primitive(context)) > 0

    def warn(self, msg: str) -> None:
        self.report({"WARNING"}, msg)

    def warn_as_error(self, msg: str) -> None:
        raise DGInvalidInput(msg)

    def execute(self, context: Context | None) -> set[str]:
        warn = self.warn if not self.strict else self.warn_as_error
        objs = _get_selected_primitive(context)
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
                    self.report({"ERROR"}, f"{obj.name}: {str(e)}")

        return {"FINISHED"}


def register() -> None:
    register_class(ApplyScale_Operator)


def unregister() -> None:
    unregister_class(ApplyScale_Operator)
