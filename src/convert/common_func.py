import sys
from collections.abc import Sequence
from typing import cast

from mathutils import Vector

from ..util.aux_math import BBox, calc_sizediff
from .common_type import IndexConv, SizeBase

# Try three patterns and use the one with the most matching volume.
INDEX: tuple[IndexConv] = (
    (0, 1, 2),
    (1, 2, 0),
    (2, 0, 1),
)

SIZE_DIFF_COEFF = 10.0
VOLUME_DIFF_COEFF = 1.0


def vector_conv(source: Vector, index_conv=None) -> Vector:
    if index_conv is None:
        return source.copy()
    return Vector(source[index_conv[i]] for i in range(3))


def calc_fittest_axis(
    primitive_size: type[SizeBase],
    bbox: BBox,
    verts: Sequence[Vector],
    target_vol: float,
) -> IndexConv:
    best_diff: float = sys.float_info.max
    result: IndexConv = INDEX[0]
    for idx_conv in INDEX:
        size = cast(SizeBase, primitive_size.build(bbox, verts, idx_conv))
        vol_diff = abs(size.calc_volume() - target_vol)
        sz_diff = calc_sizediff(size.calc_size(), vector_conv(bbox.size, idx_conv))
        diff = vol_diff * VOLUME_DIFF_COEFF + sz_diff * SIZE_DIFF_COEFF
        if best_diff > diff:
            best_diff = diff
            result = idx_conv

    return result
