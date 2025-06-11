from typing import ClassVar

from bpy.types import Context, Panel

from ..apply_mesh import ApplyMesh_Operator
from ..apply_scale import ApplyScale_Operator
from ..constants import MODERN_PRIMITIVE_CATEGORY
from ..convert import (
    ConvertToCapsule_Operator,
    ConvertToCone_Operator,
    ConvertToCube_Operator,
    ConvertToCylinder_Operator,
    ConvertToGrid_Operator,
    ConvertToSphere_Operator,
    ConvertToTorus_Operator,
    ConvertToTube_Operator,
)
from ..equalize_dcube_size import Equalize_DCube_Operator
from ..extract_primitive import ExtractPrimitive_Operator
from ..focus_modifier import FocusModifier_Operator
from ..make_primitive import OPS_GROUPS, make_operator_to_layout
from ..reset_origin import ResetOrigin_Operator
from ..restore_default import RestoreDefault_Operator
from ..switch_wireframe import SwitchWireframe
from ..util.aux_func import (
    get_active_and_selected_primitive,
    is_mpr_enabled,
    register_class,
    unregister_class,
)
from ..wireframe import ENTRY_NAME as Wireframe_EntryName


class MPR_PT_Base(Panel):
    bl_category = "Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options: ClassVar[set[str]] = {"DEFAULT_CLOSED"}


class MPR_PT_Create(MPR_PT_Base):
    bl_idname = "MPR_PT_Create"
    bl_parent_id = "MPR_PT_Main"
    bl_label = "Create"

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


class MPR_PT_Restore(MPR_PT_Base):
    bl_idname = "MPR_PT_Restore"
    bl_parent_id = "MPR_PT_Main"
    bl_label = "Restore"

    def draw(self, context: Context) -> None:
        box_param = self.layout.box()
        box_param.label(text="Parameters")
        row = box_param.row()
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

        box_origin = self.layout.box()
        box_origin.label(text="Origin")
        box_origin.operator(ResetOrigin_Operator.bl_idname, text="Reset")


class MPR_PT_Convert(MPR_PT_Base):
    bl_idname = "MPR_PT_Convert"
    bl_parent_id = "MPR_PT_Main"
    bl_label = "Convert To"

    def draw(self, context: Context) -> None:
        box = self.layout
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


class MPR_PT_Extract(MPR_PT_Base):
    bl_idname = "MPR_PT_Extract"
    bl_parent_id = "MPR_PT_Main"
    bl_label = "Extract (Beta)"

    def draw(self, context: Context) -> None:
        lo = self.layout
        lo.label(text="Extract Polygons to")
        box = lo.box()
        box.label(text="(SHIFT: Keep Original Polygons)")
        grid = box.grid_flow(columns=3, row_major=True)

        idname = ExtractPrimitive_Operator.bl_idname
        b = grid.operator(idname, text="Cube")
        b.primitive_type = "Cube"
        b = grid.operator(idname, text="D-Cube")
        b.primitive_type = "DCube"
        b = grid.operator(idname, text="Grid")
        b.primitive_type = "Grid"
        b = grid.operator(idname, text="UV Sphere")
        b.primitive_type = "UV Sphere"
        b = grid.operator(idname, text="ICO Sphere")
        b.primitive_type = "ICO Sphere"
        b = grid.operator(idname, text="Quad Sphere")
        b.primitive_type = "Quad Sphere"
        b = grid.operator(idname, text="Cylinder")
        b.primitive_type = "Cylinder"
        b = grid.operator(idname, text="Cone")
        b.primitive_type = "Cone"
        b = grid.operator(idname, text="Torus")
        b.primitive_type = "Torus"
        b = grid.operator(idname, text="Tube")
        b.primitive_type = "Tube"
        b = grid.operator(idname, text="Capsule")
        b.primitive_type = "Capsule"

        # Notes
        box2 = box.box()
        box2.label(text="Current Limitations:")
        box2.label(text="- Make sure to select the polygons in Edit Mode")
        box2.label(text="- You can select only one region per object")
        box2.label(text="- You cannot execute the operator directly from Edit Mode")


class MPR_PT_Main(Panel):
    bl_idname = "MPR_PT_Main"
    bl_label = "Modern Primitive"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = MODERN_PRIMITIVE_CATEGORY
    bl_context = "objectmode"

    def __focus_panel(self) -> None:
        layout = self.layout
        layout.operator(FocusModifier_Operator.bl_idname, text="Focus/Unfocus Modifier")

    def __dcube_panel(self) -> None:
        box = self.layout.box()
        box.label(text="D-Cube:")
        box.operator(Equalize_DCube_Operator.bl_idname, text="Equalize Size")

    def __apply_mesh_panel(self) -> None:
        box = self.layout.box()
        box.label(text="Apply Mesh")
        box.operator(ApplyMesh_Operator.bl_idname, text="Apply MPR-Modifier to Mesh")

    def __viewport_display_panel(self, ctx: Context) -> None:
        box = self.layout.box()
        box.column().label(text="Viewport Display")
        sp = box.split(factor=0.3)

        obj = get_active_and_selected_primitive(ctx)
        if obj is not None and is_mpr_enabled(obj.modifiers):
            sp.label(text="Wireframe:")
            view_text = f'{getattr(obj, Wireframe_EntryName, "")}' if obj is not None else ""
            sp.label(text=view_text)
            sp.operator(SwitchWireframe.bl_idname, text="Switch")

    def __apply_panel(self) -> None:
        box = self.layout.box()
        box.label(text="Apply")
        row = box.row()
        btn = row.operator(ApplyScale_Operator.bl_idname, text="Scale")
        btn.strict = False
        btn = row.operator(ApplyScale_Operator.bl_idname, text="Scale (Strict Mode)")
        btn.strict = True

    def draw(self, ctx: Context) -> None:
        self.__focus_panel()
        self.__dcube_panel()
        self.__apply_mesh_panel()
        self.__viewport_display_panel(ctx)
        self.__apply_panel()


CLASS: tuple[type, ...] = (
    MPR_PT_Main,
    MPR_PT_Convert,
    MPR_PT_Create,
    MPR_PT_Restore,
    MPR_PT_Extract,
)


def register() -> None:
    register_class(CLASS)


def unregister() -> None:
    unregister_class(CLASS)
