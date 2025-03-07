from collections.abc import Callable

from . import primitive_prop as P
from .aux_func import node_group_name
from .constants import MODERN_PRIMITIVE_PREFIX, Type


class Primitive:
    @classmethod
    @property
    def type_name(cls):
        return cls.type.name

    @classmethod
    def get_bl_idname(cls):
        return f"mesh.{MODERN_PRIMITIVE_PREFIX}_make_{cls.type_name.lower()}"

    @classmethod
    def get_bl_label(cls):
        return f"Make Modern {cls.type_name}"

    @classmethod
    @property
    def menu_text(cls):
        return cls.type_name

    @classmethod
    @property
    def menu_icon(cls):
        return cls.type_name.upper()

    @classmethod
    @property
    def nodegroup_name(cls):
        return node_group_name(cls.type)

    @classmethod
    def get_param_names(cls) -> tuple[str]:
        ret = set()
        for p in cls.param:
            ret.add(p.name)
        return ret

    @classmethod
    def get_param_if(cls, chk: Callable[[P.Prop], bool]) -> tuple[P.Prop]:
        return tuple(p for p in cls.param if chk(p))

    @classmethod
    def get_params(cls) -> tuple[P.Prop]:
        return cls.param


class Primitive_Cube(Primitive):
    type = Type.Cube
    param: tuple[P.Prop] = (
        P.Size,
        P.DivisionX,
        P.DivisionY,
        P.DivisionZ,
        P.GlobalDivision,
    )


class Primitive_Cone(Primitive):
    type = Type.Cone
    param: tuple[P.Prop] = (
        P.DivisionSide,
        P.DivisionFill,
        P.DivisionCircle,
        P.TopRadius,
        P.BottomRadius,
        P.Height,
    )


class Primitive_Grid(Primitive):
    type = Type.Grid
    param: tuple[P.Prop] = (
        P.SizeX,
        P.SizeY,
        P.DivisionX,
        P.DivisionY,
        P.GlobalDivision,
    )


class Primitive_Torus(Primitive):
    type = Type.Torus
    param: tuple[P.Prop] = (
        P.Radius,
        P.RingRadius,
        P.DivisionRing,
        P.DivisionCircle,
    )


class Primitive_Cylinder(Primitive):
    type = Type.Cylinder
    param: tuple[P.Prop] = (
        P.Radius,
        P.Height,
        P.DivisionCircle,
        P.DivisionSide,
        P.DivisionFill,
    )


class Primitive_UVSphere(Primitive):
    type = Type.UVSphere
    param: tuple[P.Prop] = (P.Radius, P.DivisionRing, P.DivisionCircle)


class Primitive_ICOSphere(Primitive):
    type = Type.ICOSphere
    param: tuple[P.Prop] = (
        P.Radius,
        P.Subdivision,
    )


class Primitive_Tube(Primitive):
    type = Type.Tube
    param: tuple[P.Prop] = (
        P.DivisionCircle,
        P.Height,
        P.DivisionSide,
        P.OuterRadius,
        P.InnerRadius,
    )


class Primitive_Gear(Primitive):
    type = Type.Gear
    param: tuple[P.Prop] = (
        P.NumBlades,
        P.InnerRadius,
        P.OuterRadius,
        P.Twist,
        P.InnerCircleDivision,
        P.InnerCircleRadius,
        P.FilletCount,
        P.FilletRadius,
        P.Height,
    )


class Primitive_Spring(Primitive):
    type = Type.Spring
    param: tuple[P.Prop] = (
        P.DivisionCircle,
        P.Rotations,
        P.BottomRadius,
        P.TopRadius,
        P.Height,
        P.DivisionRing,
        P.RingRadius,
    )


class Primitive_DeformableCube(Primitive):
    type = Type.DeformableCube
    param: tuple[P.Prop] = (
        P.MinX,
        P.MaxX,
        P.MinY,
        P.MaxY,
        P.MinZ,
        P.MaxZ,
    )


class Primitive_Capsule(Primitive):
    type = Type.Capsule
    param: tuple[P.Prop] = (
        P.DivisionCircle,
        P.DivisionCap,
        P.DivisionSide,
        P.Height,
        P.Radius,
    )


class Primitive_QuadSphere(Primitive):
    type = Type.QuadSphere
    param: tuple[P.Prop] = (P.Subdivision, P.Radius)


TYPE_TO_PRIMITIVE: dict[Type, Primitive] = {
    Type.Cube: Primitive_Cube,
    Type.Cone: Primitive_Cone,
    Type.Grid: Primitive_Grid,
    Type.Torus: Primitive_Torus,
    Type.Cylinder: Primitive_Cylinder,
    Type.UVSphere: Primitive_UVSphere,
    Type.ICOSphere: Primitive_ICOSphere,
    Type.Tube: Primitive_Tube,
    Type.Gear: Primitive_Gear,
    Type.Spring: Primitive_Spring,
    Type.DeformableCube: Primitive_DeformableCube,
    Type.Capsule: Primitive_Capsule,
    Type.QuadSphere: Primitive_QuadSphere,
}
