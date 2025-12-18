from collections.abc import Callable

from . import primitive_prop as P
from .util.aux_func import node_group_name
from .util.aux_other import classproperty
from .constants import MODERN_PRIMITIVE_PREFIX, Type


class Primitive:
    param: tuple[P.Prop] = ()

    @classproperty
    def type_name(cls):
        return cls.type.name

    @classmethod
    def get_bl_idname(cls):
        return f"mesh.{MODERN_PRIMITIVE_PREFIX}_make_{cls.type_name.lower()}"

    @classmethod
    def get_bl_label(cls):
        return f"Make Modern {cls.type_name}"

    @classproperty
    def menu_text(cls):
        return cls.type_name

    @classproperty
    def menu_icon(cls):
        return cls.type_name.upper()

    @classproperty
    def nodegroup_name(cls):
        return node_group_name(cls.type)

    @classmethod
    def get_param_names(cls) -> set[str]:
        ret = set()
        for p in cls.param:
            ret.add(p.name)
        return ret

    @classmethod
    def get_snap_param_names(cls) -> list[str]:
        ret = []
        for p in cls.snap_param:
            ret.append(p.name)
        return ret

    @classmethod
    def get_empty_snap_params(cls) -> dict[str, bool]:
        ret = {}
        for p in cls.snap_param:
            ret[p.name] = False
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
    snap_param: tuple[P.Prop] = (
        P.SnapSize,
        P.SnapDivision,
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
    snap_param: tuple[P.Prop] = (
        P.SnapTopRadius,
        P.SnapBottomRadius,
        P.SnapHeight,
        P.SnapSideDivision,
        P.SnapFillDivision,
        P.SnapCircleDivision,
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
    snap_param: tuple[P.Prop] = (
        P.SnapSize,
        P.SnapDivision,
    )


class Primitive_Torus(Primitive):
    type = Type.Torus
    param: tuple[P.Prop] = (
        P.Radius,
        P.RingRadius,
        P.DivisionRing,
        P.DivisionCircle,
    )
    snap_param: tuple[P.Prop] = (
        P.SnapRadius,
        P.SnapRingRadius,
        P.SnapRingDivision,
        P.SnapCircleDivision,
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
    snap_param: tuple[P.Prop] = (
        P.SnapRadius,
        P.SnapHeight,
        P.SnapCircleDivision,
        P.SnapSideDivision,
        P.SnapFillDivision,
    )


class Primitive_UVSphere(Primitive):
    type = Type.UVSphere
    param: tuple[P.Prop] = (
        P.Radius,
        P.DivisionRing,
        P.DivisionCircle,
    )
    snap_param: tuple[P.Prop] = (
        P.SnapRadius,
        P.SnapRingDivision,
        P.SnapCircleDivision,
    )


class Primitive_ICOSphere(Primitive):
    type = Type.ICOSphere
    param: tuple[P.Prop] = (
        P.Radius,
        P.Subdivision,
    )
    snap_param: tuple[P.Prop] = (P.SnapRadius,)


class Primitive_Tube(Primitive):
    type = Type.Tube
    param: tuple[P.Prop] = (
        P.DivisionCircle,
        P.Height,
        P.DivisionSide,
        P.OuterRadius,
        P.InnerRadius,
    )
    snap_param: tuple[P.Prop] = (
        P.SnapCircleDivision,
        P.SnapHeight,
        P.SnapSideDivision,
        P.SnapOuterRadius,
        P.SnapInnerRadius,
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
    snap_param: tuple[P.Prop] = (
        P.SnapNumBlades,
        P.SnapInnerRadius,
        P.SnapOuterRadius,
        P.SnapTwist,
        P.SnapInnerCircleDivision,
        P.SnapInnerCircleRadius,
        P.SnapFilletCount,
        P.SnapFilletRadius,
        P.SnapHeight,
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
    snap_param: tuple[P.Prop] = (
        P.SnapCircleDivision,
        P.SnapRotations,
        P.SnapBottomRadius,
        P.SnapTopRadius,
        P.SnapHeight,
        P.SnapRingDivision,
        P.SnapRingRadius,
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
    snap_param: tuple[P.Prop] = (P.SnapSize,)


class Primitive_Capsule(Primitive):
    type = Type.Capsule
    param: tuple[P.Prop] = (
        P.DivisionCircle,
        P.DivisionCap,
        P.DivisionSide,
        P.Height,
        P.Radius,
    )
    snap_param: tuple[P.Prop] = (
        P.SnapHeight,
        P.SnapRadius,
        P.SnapCircleDivision,
        P.SnapCapDivision,
        P.SnapSideDivision,
    )


class Primitive_QuadSphere(Primitive):
    type = Type.QuadSphere
    param: tuple[P.Prop] = (
        P.Subdivision,
        P.Radius,
    )
    snap_param: tuple[P.Prop] = (P.SnapRadius,)


TYPE_TO_PRIMITIVE: dict[Type, type[Primitive]] = {
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
