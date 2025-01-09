import bpy
import re
from .exception import DGInvalidVersionNumber, DGUnknownAssetFound, DGNodeGroupNotFound
from .constants import (
    Type,
    MODERN_PRIMITIVE_TAG,
    get_assets_dir,
)
from functools import total_ordering


@total_ordering
class VersionInt:
    MAX_DIGITS = 4
    MAX_NUMBER = pow(10, MAX_DIGITS) - 1
    RE_DIGITS = re.compile(r".*_(\d{4})$")

    def __init__(self, num: int):
        self.num = num
        if num < 0 or num > self.MAX_NUMBER:
            raise DGInvalidVersionNumber(num)

    def __str__(self) -> str:
        return f"Version({str(self.num).zfill(self.MAX_DIGITS)})"

    def __eq__(self, other) -> bool:
        return self.num == other.num

    def __ge__(self, other) -> bool:
        return self.num >= other.num

    # Read MAX_DIGITS of numbers at the end of the string
    @classmethod
    def get_version_from_string(cls, v_str: str):
        res = cls.RE_DIGITS.match(v_str)
        if res is not None:
            return VersionInt(int(res.group(1)))
        raise DGInvalidVersionNumber(-1)


_version_num: list[VersionInt] = []


# A set of primitive type and version number
class TypeAndVersion:
    RE_TYPE_AND_DIGIT = re.compile(r"(\w+)(_.+)$")

    def __init__(self, typ: Type, ver: VersionInt):
        self.type = typ
        self.version = ver

    # Extract the primitive type + version number
    # from the node group name (returns none if it cannot be identified)
    @classmethod
    def get_type_and_version(cls, src: str):
        if src.startswith(MODERN_PRIMITIVE_TAG):
            s_name = src[len(MODERN_PRIMITIVE_TAG) :]
            res = cls.RE_TYPE_AND_DIGIT.match(s_name)
            if res is not None:
                try:
                    return TypeAndVersion(
                        Type[res.group(1)],
                        VersionInt.get_version_from_string(res.group(2)),
                    )
                except DGInvalidVersionNumber:
                    pass
        return None


def register() -> None:
    global _version_num
    _version_num = []


def unregister() -> None:
    pass


# Is the version number of the primitive that comes with the add-on already read?
def _is_version_num_loaded() -> bool:
    global _version_num
    return len(_version_num) > 0


# Read the version number of the primitive that comes with the add-on
def _prepare_version_num() -> None:
    for _i in range(len(Type)):
        _version_num.append(VersionInt(0))

    str_to_type: dict[str, Type] = {}
    for t in Type:
        str_to_type[t.name.lower()] = t

    path = get_assets_dir()
    for p in path.iterdir():
        type_p: Type
        try:
            type_p = str_to_type[p.stem]
        except KeyError as e:
            raise DGUnknownAssetFound(str(p)) from e

        with bpy.data.libraries.load(str(p)) as (data_from, data_to):
            found: bool = False
            # find appropriate mesh name
            for ng_name in data_from.node_groups:
                # read version number from node-group name
                tv = TypeAndVersion.get_type_and_version(ng_name)
                if tv is not None:
                    _version_num[type_p.value - 1] = tv.version
                    found = True
                    break
            if not found:
                raise DGNodeGroupNotFound(type_p.name, str(p))


# Get the version number of the primitive attached to the add-on
def get_primitive_version(type_p: Type) -> VersionInt:
    if not _is_version_num_loaded():
        _prepare_version_num()
    return _version_num[type_p.value - 1]
