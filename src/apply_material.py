from pathlib import Path
from typing import ClassVar

import bpy
from bpy.types import Context, Material, Operator

from .material_prop import (
    GRID_MATERIAL_NAME,
    MATERIAL_PARAMS,
    get_grid_material_slot,
    get_highest_version_in_names,
    has_grid_material,
    sync_settings_to_material,
)
from .util.aux_func import (
    append_datablock_from_asset,
    get_blend_file_path,
    material_name,
    register_class,
    unregister_class,
)


class ApplyPrototypeMaterial_Operator(Operator):
    """Apply the latest Prototype Grid Material to selected mesh objects"""

    bl_idname = "object.mpr_apply_prototype_material"
    bl_label = "Apply Prototype Material"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if not context or not context.selected_objects:
            return False
        return any(obj.type == "MESH" for obj in context.selected_objects)

    def _get_highest_version_name(self, blend_file_path: Path, base_name: str) -> str:
        """Find the material name with the highest version
            across current data and asset library."""
        # Search internal data
        highest_ver, target_name = get_highest_version_in_names(
            (mat.name for mat in bpy.data.materials), base_name
        )

        # Search external asset library
        try:
            with bpy.data.libraries.load(str(blend_file_path)) as (data_from, _):
                ext_ver, ext_name = get_highest_version_in_names(data_from.materials, base_name)
                if ext_ver >= highest_ver:
                    target_name = ext_name
        except Exception as e:
            self.report({"ERROR"}, f"Failed to read asset library: {e}")

        return target_name

    def _ensure_material_exists(self, blend_file_path: Path, mat_name: str) -> Material | None:
        """Return the material from data, or try to load it from the asset file if missing."""
        mat = bpy.data.materials.get(mat_name)
        if mat:
            return mat

        try:
            append_datablock_from_asset(blend_file_path, "Material", mat_name)
            return bpy.data.materials.get(mat_name)
        except Exception as e:
            self.report({"ERROR"}, f"Could not load material '{mat_name}': {e}")
            return None

    def execute(self, context: Context | None) -> set[str]:
        if context is None:
            return {"CANCELLED"}

        # Copy selected_objects to ensure the selection is preserved
        selected_objects = list(context.selected_objects)

        # Setup paths and names
        asset_path = Path(get_blend_file_path("__material__", False))
        if not asset_path.exists():
            self.report({"ERROR"}, f"Material asset file missing: {asset_path}")
            return {"CANCELLED"}

        base_name = material_name(GRID_MATERIAL_NAME)
        scene_settings = context.scene.mpr_grid_material_settings

        # Identify the best material (to be used if an object has no grid material)
        target_name = self._get_highest_version_name(asset_path, base_name)
        if not target_name:
            self.report({"ERROR"}, f"No valid material found for base name: {base_name}")
            return {"CANCELLED"}

        # Check if the target material already exists in the scene
        was_in_scene = target_name in bpy.data.materials

        # Load the base prototype material
        prototype_mat = self._ensure_material_exists(asset_path, target_name)
        if not prototype_mat:
            return {"CANCELLED"}

        # Apply to meshes
        selected_meshes = [obj for obj in selected_objects if obj.type == "MESH"]
        updated_materials = set()

        for obj in selected_meshes:
            # Skip objects that already have a grid material
            if has_grid_material(obj):
                continue

            # No existing grid material, so apply the prototype
            if not obj.data.materials:
                obj.data.materials.append(prototype_mat)
            else:
                obj.data.materials[0] = prototype_mat

            # If the prototype material was newly added, we sync it with scene settings
            if not was_in_scene:
                updated_materials.add(prototype_mat)

        # Update all affected materials with scene settings
        for mat in updated_materials:
            mat_settings = mat.mpr_grid_material_settings
            for key in MATERIAL_PARAMS:
                setattr(mat_settings, key, getattr(scene_settings, key))
            sync_settings_to_material(mat, mat_settings)

        # UI Refresh and Notification
        if context.area:
            context.area.tag_redraw()

        self.report({"INFO"}, f"Applied/Updated material on {len(selected_meshes)} object(s).")
        return {"FINISHED"}


class MakeMaterialUnique_Operator(Operator):
    """Make the grid material unique for each selected object"""

    bl_idname = "object.mpr_make_material_unique"
    bl_label = "Make Material Unique"
    bl_options: ClassVar[set[str]] = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context | None) -> bool:
        if not context or not context.selected_objects:
            return False
        return any(has_grid_material(obj) for obj in context.selected_objects)

    def execute(self, context: Context | None) -> set[str]:
        if context is None:
            return {"CANCELLED"}

        selected_meshes = [obj for obj in context.selected_objects if obj.type == "MESH"]
        count = 0
        for obj in selected_meshes:
            # Check for grid material in slots
            slot = get_grid_material_slot(obj)
            if slot:
                # Make material unique
                # If mesh is shared, we should probably make mesh unique too
                # but for now let's focus on the material.
                if obj.data.users > 1:
                    obj.data = obj.data.copy()

                slot.material = slot.material.copy()
                count += 1

        self.report({"INFO"}, f"Made {count} material(s) unique.")
        return {"FINISHED"}


def register() -> None:
    register_class([ApplyPrototypeMaterial_Operator, MakeMaterialUnique_Operator])


def unregister() -> None:
    unregister_class([ApplyPrototypeMaterial_Operator, MakeMaterialUnique_Operator])
