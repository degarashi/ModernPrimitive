from collections.abc import Callable
from typing import Any

import blf
from bpy.types import Area, Context, Region, SpaceView3D
from mathutils import Color

from .blf_aux import set_color as set_color_g


def get_region(context: Context, area_type: str, region_type: str) -> Region | None:
    area: Area | None = None
    for a in context.screen.areas:
        if a.type == area_type:
            area = a
            break
    else:
        return None

    region: Region | None = None
    for r in area.regions:
        if r.type == region_type:
            region = r
            break

    return region


class TextDrawer:
    __text: str
    __handle: Any | None
    __color: Color
    __draw_func: Callable[[Context, int, str, Color], None]

    def __init__(
        self,
        msg: str,
        draw_func: Callable[[Context, int, str, Color], None],
    ):
        self.__text = msg
        self.__handle = None
        self.__color = Color((1, 1, 1))
        self.__draw_func = draw_func

    def is_running(self) -> bool:
        return self.__handle is not None

    def set_text(self, text: str) -> None:
        self.__text = text

    def set_color(self, col: Color) -> None:
        self.__color = col.copy()

    def show(self, context: Context) -> bool:
        if not self.is_running():
            self.__handle = SpaceView3D.draw_handler_add(
                self._draw, (context,), "WINDOW", "POST_PIXEL"
            )
            return True
        return False

    def hide(self, context: Context) -> bool:
        if self.is_running():
            SpaceView3D.draw_handler_remove(self.__handle, "WINDOW")
            self.__handle = None
            return True
        return False

    def switch_draw(self, context: Context) -> None:
        if self.is_running():
            self.hide(context)
        else:
            self.show(context)

    def _draw(self, context: Context) -> None:
        font_id: int = 0
        self.__draw_func(context, font_id, self.__text, self.__color)
