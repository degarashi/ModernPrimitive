from collections.abc import Iterable

from mathutils import Color

DEFAULT_FONT_ID: int = 0


def set_color(blf, color: Color) -> None:
    blf.color(DEFAULT_FONT_ID, color.r, color.g, color.b, 1.0)


def set_position(blf, vec: Iterable[float]) -> None:
    blf.position(DEFAULT_FONT_ID, vec[0], vec[1], 0)


def draw(blf, txt: str) -> None:
    blf.draw(DEFAULT_FONT_ID, txt)


def set_position_draw(blf, vec: Iterable[float], txt: str) -> None:
    set_position(blf, vec)
    draw(blf, txt)
