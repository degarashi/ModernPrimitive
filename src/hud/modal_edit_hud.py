from typing import ClassVar

import blf
from bpy.types import Context
from mathutils import Color

from ..text import get_region
from ..blf_aux import set_color as set_color_g


class ModalEditHUD:
    """Functor class to draw the HUD for Modern Primitive modal editing."""

    WORD_WRAP_WIDTH: ClassVar[int] = 1024
    SHADOW_OFFSET: ClassVar[tuple[int, int]] = (1, -1)
    FONT_SIZE: ClassVar[int] = 16
    LINE_HEIGHT: ClassVar[int] = 22
    MARGIN_X: ClassVar[int] = 60
    MARGIN_Y: ClassVar[int] = 180
    LABEL_WIDTH: ClassVar[int] = 160
    VALUE_WIDTH: ClassVar[int] = 340
    HIGHLIGHT_COLOR: ClassVar[tuple[float, float, float, float]] = (1.0, 0.5, 0.0, 1.0)

    def __call__(self, context: Context, font_id: int, text: str, color: Color) -> None:
        region = get_region(context, "VIEW_3D", "WINDOW")
        if region is None:
            return

        blf.enable(font_id, blf.WORD_WRAP)
        blf.word_wrap(font_id, self.WORD_WRAP_WIDTH)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow_offset(font_id, *self.SHADOW_OFFSET)
        blf.size(font_id, self.FONT_SIZE)

        lines = text.split("\n")

        # Start Y coordinate (subtract margin from the top of the region)
        start_y = region.height - self.MARGIN_Y

        # X coordinate for initial values (fixed position to prevent jittering)
        initial_val_x = self.MARGIN_X + self.LABEL_WIDTH + self.VALUE_WIDTH

        for i, line in enumerate(lines):
            current_y = start_y - (i * self.LINE_HEIGHT)

            # Color detection (Mode lines or active items are orange, others are default)
            if "▶" in line or "Mode:" in line:
                blf.color(font_id, *self.HIGHLIGHT_COLOR)
            else:
                set_color_g(blf, color)

            # Separate label and values for clean alignment
            if "|" in line and "Mode:" not in line:
                parts = line.split("|")

                # --- Label (Left-aligned) ---
                label_part = parts[0].strip()
                blf.position(font_id, self.MARGIN_X, current_y, 0)
                blf.draw(font_id, label_part)

                # --- Current Value (Left-aligned) ---
                if len(parts) > 1:
                    value_part = parts[1].strip()
                    blf.position(font_id, self.MARGIN_X + self.LABEL_WIDTH, current_y, 0)
                    blf.draw(font_id, value_part)

                # --- Initial Value (Right-aligned layout) ---
                if len(parts) > 2:
                    init_part = parts[2].strip()

                    # Get text dimensions and offset from the specified position to the left (right-alignment)
                    text_width, _ = blf.dimensions(font_id, init_part)
                    blf.position(font_id, initial_val_x - text_width, current_y, 0)
                    blf.draw(font_id, init_part)

            else:
                # Headers, separators, and instruction text are just left-aligned
                blf.position(font_id, self.MARGIN_X, current_y, 0)
                blf.draw(font_id, line)

        blf.disable(font_id, blf.WORD_WRAP)
        blf.disable(font_id, blf.SHADOW)
