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
    return Path(__file__).parent


def get_assets_dir() -> Path:
    return get_addon_dir() / ASSET_DIR_NAME
