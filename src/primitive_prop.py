from enum import Enum, auto
from typing import NamedTuple
from .exception import DGPropertyNotFound
from mathutils import Vector


class PropType(Enum):
    # related to size
    Size = auto()
    # related to number of divisions
    Division = auto()
    # not Size or Division
    Other = auto()

    # around xy axis
    Width = auto()
    # around z-axis
    Height = auto()
    # related to smooth display
    Smooth = auto()


PT = PropType


class Prop(NamedTuple):
    name: str
    type: type
    prop_type: set[PT]

    def __hash__(self):
        # This is done on the premise that there is no Prop of the same name
        return hash(f"{self.name}")

    def has_tag(self, pt: PropType) -> bool:
        return pt in self.prop_type


def get_min(index: int) -> Prop:
    return (MinX, MinY, MinZ)[index]


def get_max(index: int) -> Prop:
    return (MaxX, MaxY, MaxZ)[index]


Size = Prop("Size", Vector, {PT.Size})
SizeX = Prop("Size X", float, {PT.Size, PT.Width})
SizeY = Prop("Size Y", float, {PT.Size, PT.Width})
SizeZ = Prop("Size Z", float, {PT.Size, PT.Height})

MinX = Prop("Min X", float, {PT.Size, PT.Width})
MinY = Prop("Min Y", float, {PT.Size, PT.Width})
MinZ = Prop("Min Z", float, {PT.Size, PT.Height})
MaxX = Prop("Max X", float, {PT.Size, PT.Width})
MaxY = Prop("Max Y", float, {PT.Size, PT.Width})
MaxZ = Prop("Max Z", float, {PT.Size, PT.Height})

Height = Prop("Height", float, {PT.Size, PT.Height})

Radius = Prop("Radius", float, {PT.Size})
TopRadius = Prop("Top Radius", float, {PT.Size, PT.Width})
BottomRadius = Prop("Bottom Radius", float, {PT.Size, PT.Width})
RingRadius = Prop("Ring Radius", float, {PT.Size})
OuterRadius = Prop("Outer Radius", float, {PT.Size})
InnerRadius = Prop("Inner Radius", float, {PT.Size})

DivisionX = Prop("Division X", int, {PT.Division, PT.Width})
DivisionY = Prop("Division Y", int, {PT.Division, PT.Width})
DivisionZ = Prop("Division Z", int, {PT.Division, PT.Height})
DivisionCircle = Prop("Div Circle", int, {PT.Division, PT.Width})
DivisionSide = Prop("Div Side", int, {PT.Division, PT.Height})
DivisionFill = Prop("Div Fill", int, {PT.Division})
DivisionRing = Prop("Div Ring", int, {PT.Division})
DivisionCap = Prop("Div Cap", int, {PT.Division})
GlobalDivision = Prop("Global Division", float, {PT.Division})

Fill = Prop("Fill", bool, {})
Centered = Prop("Centered", bool, {})

Smooth = Prop("Smooth", bool, {PT.Smooth})
SmoothAngle = Prop("Smooth Angle", float, {PT.Smooth})
Subdivision = Prop("Subdivision", int, {PT.Division})

UVType = Prop("UV Type", Enum, {})
UVName = Prop("UV Name", str, {})

NumBlades = Prop("Num Blades", int, {PT.Division})
Twist = Prop("Twist", float, {PT.Other})

FilletCount = Prop("Fillet Count", int, {PT.Other})
FilletRadius = Prop("Fillet Radius", float, {PT.Other})

InnerCircleRadius = Prop("InnerCircle Radius", float, {PT.Size})
InnerCircleDivision = Prop("InnerCircle Division", int, {PT.Division})

Rotations = Prop("Rotations", float, {PT.Other})

CornerRatio = Prop("Corner Ratio", Vector, {PT.Other})


# -- Snapping Flag --
def _make_snapping_name(name: str) -> str:
    return f"Enable {name} Snapping"


def _make_snapping_prop(name: str) -> Prop:
    return Prop(_make_snapping_name(name), bool, {})


SnapHeight = _make_snapping_prop("Height")
SnapRadius = _make_snapping_prop("Radius")
SnapCircleDivision = _make_snapping_prop("Circle-Division")
SnapCapDivision = _make_snapping_prop("Cap-Division")
SnapSideDivision = _make_snapping_prop("Side-Division")
SnapFillDivision = _make_snapping_prop("Fill-Division")
SnapTopRadius = _make_snapping_prop("Top-Radius")
SnapBottomRadius = _make_snapping_prop("Bottom-Radius")
SnapSize = _make_snapping_prop("Size")
SnapDivision = _make_snapping_prop("Division")
SnapNumBlades = _make_snapping_prop("Num Blades")
SnapInnerRadius = _make_snapping_prop("Inner Radius")
SnapOuterRadius = _make_snapping_prop("Outer Radius")
SnapTwist = _make_snapping_prop("Twist")
SnapInnerCircleDivision = _make_snapping_prop("InnerCircle Division")
SnapInnerCircleRadius = _make_snapping_prop("InnerCircle Radius")
SnapFilletCount = _make_snapping_prop("Fillet Count")
SnapFilletRadius = _make_snapping_prop("Fillet Radius")
SnapRotations = _make_snapping_prop("Rotations")
SnapRingDivision = _make_snapping_prop("Ring-Division")
SnapRingRadius = _make_snapping_prop("Ring Radius")
# ----

PROP_LIST: list[Prop] = [
    Size,
    SizeX,
    SizeY,
    SizeZ,
    MinX,
    MinY,
    MinZ,
    MaxX,
    MaxY,
    MaxZ,
    Height,
    Radius,
    TopRadius,
    BottomRadius,
    RingRadius,
    OuterRadius,
    InnerRadius,
    DivisionX,
    DivisionY,
    DivisionZ,
    DivisionCircle,
    DivisionSide,
    DivisionFill,
    DivisionRing,
    DivisionCap,
    GlobalDivision,
    Fill,
    Centered,
    Smooth,
    SmoothAngle,
    Subdivision,
    UVType,
    UVName,
    NumBlades,
    Twist,
    FilletCount,
    FilletRadius,
    InnerCircleRadius,
    InnerCircleDivision,
    Rotations,
    SnapHeight,
    SnapRadius,
    SnapCircleDivision,
    SnapCapDivision,
    SnapSideDivision,
    SnapFillDivision,
    SnapTopRadius,
    SnapBottomRadius,
    SnapSize,
    SnapDivision,
    SnapNumBlades,
    SnapInnerRadius,
    SnapOuterRadius,
    SnapTwist,
    SnapInnerCircleDivision,
    SnapInnerCircleRadius,
    SnapFilletCount,
    SnapFilletRadius,
    SnapRotations,
    SnapRingDivision,
    SnapRingRadius,
]
PROP_MAP: dict[str, Prop] = {}


def prop_from_name(name: str) -> Prop:
    if len(PROP_MAP) == 0:
        for p in PROP_LIST:
            PROP_MAP[p.name] = p

    if name in PROP_MAP:
        return PROP_MAP[name]

    raise DGPropertyNotFound()
