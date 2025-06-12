from typing import ClassVar

from bpy.types import Context, Panel

from ..constants import MODERN_PRIMITIVE_CATEGORY
from ..extract_primitive import ExtractPrimitive_Operator
from ..util.aux_func import (
    register_class,
    unregister_class,
)


class MPR_PT_EditConvert(Panel):
    bl_idname = "MPR_PT_EditConvert"
    bl_parent_id = "MPR_PT_Edit"
    bl_label = "Convert To Primitive (Selected)"
    bl_category = "Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options: ClassVar[set[str]] = {"DEFAULT_CLOSED"}

    def draw(self, ctx: Context) -> None:
        lo = self.layout
        box = lo.box()
        box.label(text="(SHIFT: Keep Original Mesh)")
        grid = box.grid_flow(columns=3, row_major=True)
        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="Cube")
        op.primitive_type = "Cube"
        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="D-Cube")
        op.primitive_type = "DCube"
        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="Grid")
        op.primitive_type = "Grid"

        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="UV Sphere")
        op.primitive_type = "UV Sphere"
        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="ICO Sphere")
        op.primitive_type = "ICO Sphere"
        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="Quad Sphere")
        op.primitive_type = "Quad Sphere"

        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="Cylinder")
        op.primitive_type = "Cylinder"
        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="Cone")
        op.primitive_type = "Cone"
        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="Torus")
        op.primitive_type = "Torus"

        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="Tube")
        op.primitive_type = "Tube"
        op = grid.operator(ExtractPrimitive_Operator.bl_idname, text="Capsule")
        op.primitive_type = "Capsule"


class MPR_PT_Edit(Panel):
    bl_idname = "MPR_PT_Edit"
    bl_label = "Modern Primitive"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = MODERN_PRIMITIVE_CATEGORY
    bl_context = "mesh_edit"

    def draw(self, ctx: Context) -> None:
        pass


CLASS: tuple[type, ...] = (
    MPR_PT_Edit,
    MPR_PT_EditConvert,
)


def register() -> None:
    register_class(CLASS)


def unregister() -> None:
    unregister_class(CLASS)
