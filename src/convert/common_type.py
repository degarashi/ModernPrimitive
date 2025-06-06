from collections.abc import Sequence
from typing import TypeAlias

from mathutils import Vector

from ..aux_math import BBox

IndexConv: TypeAlias = tuple[int, int, int]
IndexConvOPT: TypeAlias = IndexConv | None


class SizeBase:
    @staticmethod
    def build(bbox: BBox, verts: Sequence[Vector], index_conv: IndexConvOPT):
        pass

    def calc_size(self) -> Vector:
        raise NotImplementedError("This method should be implemented by subclass")

    def calc_volume(self) -> float:
        raise NotImplementedError("This method should be implemented by subclass")
