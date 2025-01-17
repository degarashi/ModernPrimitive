from .constants import Type, MODERN_PRIMITIVE_PREFIX
from .aux_func import node_group_name


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


class Primitive_Cube(Primitive):
    type = Type.Cube


class Primitive_Cone(Primitive):
    type = Type.Cone


class Primitive_Grid(Primitive):
    type = Type.Grid


class Primitive_Torus(Primitive):
    type = Type.Torus


class Primitive_Cylinder(Primitive):
    type = Type.Cylinder


class Primitive_UVSphere(Primitive):
    type = Type.UVSphere


class Primitive_ICOSphere(Primitive):
    type = Type.ICOSphere


class Primitive_Tube(Primitive):
    type = Type.Tube


class Primitive_Gear(Primitive):
    type = Type.Gear


class Primitive_Spring(Primitive):
    type = Type.Spring


class Primitive_DeformableCube(Primitive):
    type = Type.DeformableCube


class Primitive_Capsule(Primitive):
    type = Type.Capsule


class Primitive_QuadSphere(Primitive):
    type = Type.QuadSphere
