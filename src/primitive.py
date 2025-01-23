from .constants import Type, MODERN_PRIMITIVE_PREFIX
from .aux_func import node_group_name
from . import primitive_prop as P


class Primitive:
    @classmethod
    @property
    def type_name(cls):
        return cls.type.name

    @classmethod
    @property
    def bl_idname(cls):
        return f"mesh.{MODERN_PRIMITIVE_PREFIX}_make_{cls.type_name.lower()}"

    @classmethod
    @property
    def bl_label(cls):
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


class Primitive_Cube(Primitive):
    type = Type.Cube
    param: tuple[P.Prop] = (
        P.SizeX,
        P.SizeY,
        P.SizeZ,
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
        P.Centered,
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
        P.Centered,
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
