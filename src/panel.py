from bpy.types import Context, Panel
from bpy.utils import register_class, unregister_class

from .apply_mesh import ApplyMesh_Operator
from .apply_scale import ApplyScale_Operator
from .aux_func import get_active_and_selected_primitive
from .constants import MODERN_PRIMITIVE_CATEGORY
from .convert import (
    ConvertToCapsule_Operator,
    ConvertToCone_Operator,
    ConvertToCube_Operator,
    ConvertToCylinder_Operator,
    ConvertToGrid_Operator,
    ConvertToSphere_Operator,
    ConvertToTorus_Operator,
    ConvertToTube_Operator,
)
from .cube import DCube_CenterOrigin_Operator
from .make_primitive import OPS_GROUPS, make_operator_to_layout
from .modifier_select import FocusModifier_Operator
from .restore_default import RestoreDefault_Operator
from .switch_wireframe import SwitchWireframe
from .wireframe import ENTRY_NAME


class MPR_PT_Create(Panel):
    bl_category = "Tool"
    bl_parent_id = "MPR_PT_Main"
    bl_label = "Create"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context) -> None:
        layout = self.layout

        first: bool = True
        for _, ops in OPS_GROUPS.items():
            if first:
                first = False
            else:
                layout.separator()
            grid = layout.grid_flow(columns=2, row_major=True)
            for op in ops:
                make_operator_to_layout(context, grid, op)


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
        box.label(text="Convert to:")
        box.label(text="(SHIFT: Keep Original Object)")
        grid = box.grid_flow(columns=3, row_major=True)
        c = grid.operator(ConvertToCube_Operator.bl_idname, text="Cube")
        c.cube_type = "Cube"
        c = grid.operator(ConvertToCube_Operator.bl_idname, text="D-Cube")
        c.cube_type = "DeformableCube"
        grid.operator(ConvertToGrid_Operator.bl_idname, text="Grid")

        s = grid.operator(ConvertToSphere_Operator.bl_idname, text="UV Sphere")
        s.sphere_type = "UVSphere"
        s = grid.operator(ConvertToSphere_Operator.bl_idname, text="ICO Sphere")
        s.sphere_type = "ICOSphere"
        s = grid.operator(ConvertToSphere_Operator.bl_idname, text="Quad Sphere")
        s.sphere_type = "QuadSphere"
        grid.operator(ConvertToCylinder_Operator.bl_idname, text="Cylinder")
        grid.operator(ConvertToCone_Operator.bl_idname, text="Cone")
        grid.operator(ConvertToTorus_Operator.bl_idname, text="Torus")
        grid.operator(ConvertToTube_Operator.bl_idname, text="Tube")
        grid.operator(ConvertToCapsule_Operator.bl_idname, text="Capsule")

        box = layout.box()
        box.label(text="D-Cube:")
        box.operator(DCube_CenterOrigin_Operator.bl_idname, text="Set origin to Center")

        box = layout.box()
        box.label(text="Apply Mesh")
        box.operator(ApplyMesh_Operator.bl_idname, text="Apply MPR-Modifier to Mesh")

        box = layout.box()
        box.column().label(text="Viewport Display")
        sp = box.split(factor=0.3)
        sp.label(text="Wireframe:")

        obj = get_active_and_selected_primitive(ctx)
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

        box = layout.box()
        box.label(text="Restore Default")
        row = box.row()
        btn = row.operator(RestoreDefault_Operator.bl_idname, text="All")
        btn.reset_size = True
        btn.reset_size_mode = "All"
        btn.reset_division = True
        btn.reset_division_mode = "All"
        btn.reset_other = True

        btn = row.operator(RestoreDefault_Operator.bl_idname, text="Size")
        btn.reset_size = True
        btn.reset_size_mode = "All"
        btn.reset_division = False
        btn.reset_other = False

        btn = row.operator(RestoreDefault_Operator.bl_idname, text="Division")
        btn.reset_size = False
        btn.reset_division = True
        btn.reset_division_mode = "All"
        btn.reset_other = False


def register() -> None:
    register_class(MPR_PT_Main)
    register_class(MPR_PT_Create)


def unregister() -> None:
    unregister_class(MPR_PT_Main)
    unregister_class(MPR_PT_Create)
