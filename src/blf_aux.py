from collections.abc import Iterable
from types import ModuleType

from mathutils import Color

DEFAULT_FONT_ID: int = 0


def set_color(blf: ModuleType, color: Color) -> None:
    blf.color(DEFAULT_FONT_ID, color.r, color.g, color.b, 1.0)


def set_position(blf: ModuleType, vec: Iterable[float]) -> None:
    blf.position(DEFAULT_FONT_ID, vec[0], vec[1], 0)


def draw(blf: ModuleType, txt: str) -> None:
    blf.draw(DEFAULT_FONT_ID, txt)


def set_position_draw(blf: ModuleType, vec: Iterable[float], txt: str) -> None:
    set_position(blf, vec)
    draw(blf, txt)
