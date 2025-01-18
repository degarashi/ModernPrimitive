from bpy.utils import register_class, unregister_class
from bpy.types import Panel, Context
from .modifier_select import FocusModifier_Operator
from .convert import ConvertToCube_Operator
from .cube import DCube_CenterOrigin_Operator
from .constants import MODERN_PRIMITIVE_CATEGORY
from .make_primitive import OPS, OperatorBase
from .switch_wireframe import SwitchWireframe
from .aux_func import get_target_object
from .wireframe import ENTRY_NAME
from .apply_scale import ApplyScale_Operator


class MPR_PT_Create(Panel):
    bl_category = "Tool"
    bl_parent_id = "MPR_PT_Main"
    bl_label = "Create"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context) -> None:
        layout = self.layout
        grid = layout.grid_flow(columns=2, row_major=True)

        def add_op(op: OperatorBase) -> None:
            nonlocal grid
            grid.operator(
                op.bl_idname,
                text=op.menu_text,
                icon=op.menu_icon,
            )

        for op in OPS:
            add_op(op)


class MPR_PT_Main(Panel):
    bl_idname = "MPR_PT_Main"
    bl_label = "Modern Primitive"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = MODERN_PRIMITIVE_CATEGORY
    bl_context = ".objectmode"

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

        box = layout.box()
        box.column().label(text="Viewport Display")
        sp = box.split(factor=0.3)
        sp.label(text="Wireframe:")

        obj = get_target_object(ctx)
        view_text = f"{obj[ENTRY_NAME]}" if obj is not None else ""
        sp.label(text=view_text)

        sp.operator(SwitchWireframe.bl_idname, text="Switch")

        box = layout.box()
        box.label(text="Apply")
        row = box.row()
        btn = row.operator(ApplyScale_Operator.bl_idname, text="Scale")
        btn.strict = False
        btn = row.operator(ApplyScale_Operator.bl_idname, text="Scale (Strict Mode)")
        btn.strict = True


def register() -> None:
    register_class(MPR_PT_Main)
    register_class(MPR_PT_Create)


def unregister() -> None:
    unregister_class(MPR_PT_Main)
    unregister_class(MPR_PT_Create)
