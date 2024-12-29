from .constants import Type, MODERN_PRIMITIVE_PREFIX
from .aux_func import node_group_name


class PrimitiveInfo:
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


class PrimitiveInfo_Cube(PrimitiveInfo):
    type = Type.Cube


class PrimitiveInfo_Cone(PrimitiveInfo):
    type = Type.Cone


class PrimitiveInfo_Grid(PrimitiveInfo):
    type = Type.Grid


class PrimitiveInfo_Torus(PrimitiveInfo):
    type = Type.Torus


class PrimitiveInfo_Cylinder(PrimitiveInfo):
    type = Type.Cylinder


class PrimitiveInfo_UVSphere(PrimitiveInfo):
    type = Type.UVSphere


class PrimitiveInfo_ICOSphere(PrimitiveInfo):
    type = Type.ICOSphere


class PrimitiveInfo_Tube(PrimitiveInfo):
    type = Type.Tube


class PrimitiveInfo_Gear(PrimitiveInfo):
    type = Type.Gear


class PrimitiveInfo_Spring(PrimitiveInfo):
    type = Type.Spring


class PrimitiveInfo_DeformableCube(PrimitiveInfo):
    type = Type.DeformableCube


class PrimitiveInfo_Capsule(PrimitiveInfo):
    type = Type.Capsule


class PrimitiveInfo_QuadSphere(PrimitiveInfo):
    type = Type.QuadSphere
