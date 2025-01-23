from enum import Enum, auto
from typing import NamedTuple


class PropType(Enum):
    # related to size
    Size = auto()
    # related to number of divisions
    Division = auto()

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


def get_min(index: int) -> Prop:
    return (MinX, MinY, MinZ)[index]


def get_max(index: int) -> Prop:
    return (MaxX, MaxY, MaxZ)[index]


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

DivisionX = Prop("Division X", float, {PT.Division, PT.Width})
DivisionY = Prop("Division Y", float, {PT.Division, PT.Width})
DivisionZ = Prop("Division Z", float, {PT.Division, PT.Height})
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
Twist = Prop("Twist", float, {})

FilletCount = Prop("Fillet Count", int, {})
FilletRadius = Prop("Fillet Radius", float, {})

InnerCircleRadius = Prop("InnerCircle Radius", float, {PT.Size})
InnerCircleDivision = Prop("InnerCircle Division", int, {PT.Division})

Rotations = Prop("Rotations", float, {})
