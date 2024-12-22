from enum import Enum, auto
from pathlib import Path


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


MODERN_PRIMITIVE_TAG = "[ModernPrimitive]"
MODERN_PRIMITIVE_BASE_MESH_NAME = f"{MODERN_PRIMITIVE_TAG}BaseMesh"
MODERN_PRIMITIVE_PROPERTY_PREFIX = "mpr"
ASSET_DIR_NAME = "assets"


def get_addon_dir() -> Path:
    return Path(__file__).parent.parent


def get_assets_dir() -> Path:
    return get_addon_dir() / ASSET_DIR_NAME


_ADDON_NAME: str | None = None


def get_addon_name() -> str:
    global _ADDON_NAME
    if _ADDON_NAME is None:
        a_name = __package__.split(".")
        a_name.pop()
        _ADDON_NAME = ".".join(a_name)
    return _ADDON_NAME
