from enum import Enum, auto
from .exception import DGInvalidVersionNumber
import re


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
    Cylinder = VersionInt(1)
    UVSphere = VersionInt(0)
    ICOSphere = VersionInt(0)
    Tube = VersionInt(1)
    Gear = VersionInt(0)


MODERN_PRIMITIVE_TAG = "[ModernPrimitive]"
MODERN_PRIMITIVE_BASE_MESH_NAME = f"{MODERN_PRIMITIVE_TAG}BaseMesh"


def node_group_name_prefix(type: Type) -> str:
    return f"{MODERN_PRIMITIVE_TAG}{type.name}_"


def node_group_name(type: Type, version: VersionInt) -> str:
    return node_group_name_prefix(type) + str(version)


def modifier_name(type: Type) -> str:
    return f"{MODERN_PRIMITIVE_TAG}{type.name}"
