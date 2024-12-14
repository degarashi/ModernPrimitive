from enum import Enum, auto
from .exception import DGInvalidVersionNumber
import re
from bpy.types import Modifier


class Type(Enum):
    Cube = auto()
    Cone = auto()
    Grid = auto()
    Torus = auto()
    Cylinder = auto()
    UVSphere = auto()
    ICOSphere = auto()
    Tube = auto()
    Gear = auto()
    Spring = auto()
    DeformableCube = auto()


class VersionInt:
    MAX_DIGITS = 4
    MAX_NUMBER = pow(10, MAX_DIGITS) - 1
    RE_DIGITS = re.compile(r".*_(\d{4})$")

    def __init__(self, num: int):
        self.num = num
        if num < 0 or num > self.MAX_NUMBER:
            raise DGInvalidVersionNumber(num)

    def __str__(self) -> str:
        return str(self.num).zfill(self.MAX_DIGITS)

    def __eq__(self, other) -> bool:
        return self.num == other.num

    def __ne__(self, other) -> bool:
        return self.num != other.num

    def __ge__(self, other) -> bool:
        return self.num >= other.num

    @classmethod
    def get_version_from_string(cls, v_str: str):
        res = cls.RE_DIGITS.match(v_str)
        if res is not None:
            return VersionInt(int(res.group(1)))
        raise DGInvalidVersionNumber(-1)


class NodeGroupCurVersion(Enum):
    Cube = VersionInt(0)
    Cone = VersionInt(0)
    Grid = VersionInt(0)
    Torus = VersionInt(0)
    Cylinder = VersionInt(2)
    UVSphere = VersionInt(0)
    ICOSphere = VersionInt(0)
    Tube = VersionInt(3)
    Gear = VersionInt(1)
    Spring = VersionInt(0)
    DeformableCube = VersionInt(0)


_MODERN_PRIMITIVE_TAG = "[ModernPrimitive]"
MODERN_PRIMITIVE_BASE_MESH_NAME = f"{_MODERN_PRIMITIVE_TAG}BaseMesh"
_MODERN_PRIMITIVE_PROPERTY_PREFIX = "mpr"


def node_group_name_prefix(type: Type) -> str:
    return f"{_MODERN_PRIMITIVE_TAG}{type.name}_"


def node_group_name(type: Type, version: VersionInt) -> str:
    return node_group_name_prefix(type) + str(version)


def modifier_name(type: Type) -> str:
    return f"{_MODERN_PRIMITIVE_TAG}{type.name}"


def is_primitive_mod(mod: Modifier) -> bool:
    return mod.name.startswith(_MODERN_PRIMITIVE_TAG)


def make_primitive_property_name(name: str) -> str:
    return f"{_MODERN_PRIMITIVE_PROPERTY_PREFIX}_{name}"


def is_primitive_property(name: str) -> bool:
    return name.startswith(_MODERN_PRIMITIVE_PROPERTY_PREFIX + "_")


def get_blend_file_name(type: Type) -> str:
    return f"assets/{type.name.lower()}.blend"
