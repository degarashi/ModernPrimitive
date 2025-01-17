from enum import Enum
from typing import NamedTuple


class Prop(NamedTuple):
    name: str
    type: type


SizeX = Prop("Size X", float)
SizeY = Prop("Size Y", float)
SizeZ = Prop("Size Z", float)

MinX = Prop("Min X", float)
MinY = Prop("Min Y", float)
MinZ = Prop("Min Z", float)
MaxX = Prop("Max X", float)
MaxY = Prop("Max Y", float)
MaxZ = Prop("Max Z", float)


def get_min(index: int) -> Prop:
    return (MinX, MinY, MinZ)[index]


def get_max(index: int) -> Prop:
    return (MaxX, MaxY, MaxZ)[index]


Height = Prop("Height", float)

Radius = Prop("Radius", float)
TopRadius = Prop("Top Radius", float)
BottomRadius = Prop("Bottom Radius", float)
RingRadius = Prop("Ring Radius", float)
OuterRadius = Prop("Outer Radius", float)
InnerRadius = Prop("Inner Radius", float)

DivisionX = Prop("Division X", float)
DivisionY = Prop("Division Y", float)
DivisionZ = Prop("Division Z", float)
DivisionCircle = Prop("Div Circle", int)
DivisionSide = Prop("Div Side", int)
DivisionFill = Prop("Div Fill", int)
DivisionRing = Prop("Div Ring", int)
DivisionCap = Prop("Div Cap", int)
GlobalDivision = Prop("Global Division", float)

Fill = Prop("Fill", bool)
Centered = Prop("Centered", bool)

Smooth = Prop("Smooth", bool)
SmoothAngle = Prop("Smooth Angle", float)
Subdivision = Prop("Subdivision", int)

UVType = Prop("UV Type", Enum)
UVName = Prop("UV Name", str)

NumBlades = Prop("Num Blades", int)
Twist = Prop("Twist", float)

FilletCount = Prop("Fillet Count", int)
FilletRadius = Prop("Fillet Radius", float)

InnerCircleRadius = Prop("InnerCircle Radius", float)
InnerCircleDivision = Prop("InnerCircle Division", int)

Rotations = Prop("Rotations", float)
