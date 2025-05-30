from enum import Enum, auto
from pathlib import Path
from typing import ClassVar


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
    Capsule = auto()
    QuadSphere = auto()


MODERN_PRIMITIVE_TAG = "[ModernPrimitive]"
# used by property-name, operator-id...
MODERN_PRIMITIVE_PREFIX = "mpr"
MODERN_PRIMITIVE_CATEGORY = "MPR"
ASSET_DIR_NAME = "assets"

MIN_SIZE = 1e-5
MIN_RADIUS = 1e-5


def get_addon_dir() -> Path:
    return Path(__file__).parent.parent


def get_assets_dir() -> Path:
    return get_addon_dir() / ASSET_DIR_NAME


class Variables:
    _ADDON_NAME: ClassVar[str | None] = None


def get_addon_name() -> str:
    if Variables._ADDON_NAME is None:
        a_name = __package__.split(".")
        a_name.pop()
        Variables._ADDON_NAME = ".".join(a_name)
    return Variables._ADDON_NAME
