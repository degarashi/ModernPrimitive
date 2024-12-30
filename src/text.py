import blf
from bpy.types import SpaceView3D, Context, Region, Area


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
    def __init__(self, msg: str):
        self._text = msg
        self._handle = None

    def is_running(self) -> bool:
        return self._handle is not None

    def set_text(self, text: str) -> None:
        self._text = text

    def show(self, context: Context) -> bool:
        if not self.is_running():
            self._handle = SpaceView3D.draw_handler_add(
                self._draw, (context,), "WINDOW", "POST_PIXEL"
            )
            return True
        return False

    def hide(self, context: Context) -> bool:
        if self.is_running():
            SpaceView3D.draw_handler_remove(self._handle, "WINDOW")
            self._handle = None
            return True
        return False

    def switch_draw(self, context: Context) -> None:
        if self.is_running():
            self.hide(context)
        else:
            self.show(context)

    def _draw(self, context: Context) -> None:
        region = get_region(context, "VIEW_3D", "WINDOW")
        if region is not None:
            font_id: int = 0
            blf.enable(font_id, blf.WORD_WRAP)
            blf.word_wrap(font_id, 1024)
            blf.enable(font_id, blf.SHADOW)
            blf.shadow_offset(font_id, 1, -1)

            blf.color(font_id, 1, 0.15, 0.15, 1)
            blf.size(font_id, 20)
            w, h = blf.dimensions(font_id, self._text)
            blf.position(font_id, region.width / 2 - w / 2, region.height - 120, 0)
            blf.draw(font_id, self._text)

            blf.disable(font_id, blf.WORD_WRAP)
            blf.disable(font_id, blf.SHADOW)
