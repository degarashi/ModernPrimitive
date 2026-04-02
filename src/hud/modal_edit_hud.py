import blf
from bpy.types import Context
from mathutils import Color

from ..text import get_region
from ..blf_aux import set_color as set_color_g


class ModalEditHUD:
    """Functor class to draw the HUD for Modern Primitive modal editing."""

    def __call__(self, context: Context, font_id: int, text: str, color: Color) -> None:
        region = get_region(context, "VIEW_3D", "WINDOW")
        if region is None:
            return

        blf.enable(font_id, blf.WORD_WRAP)
        blf.word_wrap(font_id, 1024)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow_offset(font_id, 1, -1)
        blf.size(font_id, 20)

        lines = text.split("\n")
        line_height = 25

        # Margin from the top-left of the screen
        margin_x = 160
        margin_y = 120

        # Start Y coordinate (subtract margin from the top of the region)
        start_y = region.height - margin_y

        # Padding between labels and numeric values (indentation width)
        label_width = 220

        for i, line in enumerate(lines):
            current_y = start_y - (i * line_height)

            # Color detection (Mode lines or active items are orange, others are default)
            if "▶" in line or "Mode:" in line:
                blf.color(font_id, 1.0, 0.5, 0.0, 1.0)
            else:
                set_color_g(blf, color)

            # Separate label and value for clean alignment
            if "|" in line and "Mode:" not in line:
                parts = line.split("|")
                label_part = parts[0].strip()
                value_part = parts[1].strip()

                # Label (left-aligned)
                blf.position(font_id, margin_x, current_y, 0)
                blf.draw(font_id, label_part)

                # Numeric value (left-aligned at fixed offset to prevent jitter)
                blf.position(font_id, margin_x + label_width, current_y, 0)
                blf.draw(font_id, value_part)
            else:
                # Headers, separators, and instruction text are just left-aligned
                blf.position(font_id, margin_x, current_y, 0)
                blf.draw(font_id, line)

        blf.disable(font_id, blf.WORD_WRAP)
        blf.disable(font_id, blf.SHADOW)
