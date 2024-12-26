from bpy.utils import register_class, unregister_class
from bpy.types import Panel, Context
from .modifier_select import FocusModifier_Operator
from .convert import ConvertToCube_Operator
from .cube import DCube_CenterOrigin_Operator
from .constants import MODERN_PRIMITIVE_CATEGORY


class MPR_PT_Main(Panel):
    bl_idname = "MPR_PT_Main"
    bl_label = "Modern Primitive"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = MODERN_PRIMITIVE_CATEGORY

    def draw(self, ctx: Context) -> None:
        layout = self.layout
        layout.operator(FocusModifier_Operator.bl_idname, text="Focus/Unfocus Modifier")

        box = layout.box()
        row = box.row()
        row.label(text="Convert to")
        c = row.operator(ConvertToCube_Operator.bl_idname, text="Cube")
        c.cube_type = "Cube"
        c = row.operator(ConvertToCube_Operator.bl_idname, text="D-Cube")
        c.cube_type = "DeformableCube"

        box = layout.box()
        box.label(text="D-Cube:")
        box.operator(DCube_CenterOrigin_Operator.bl_idname, text="Set origin to Center")


def register() -> None:
    register_class(MPR_PT_Main)


def unregister() -> None:
    unregister_class(MPR_PT_Main)
