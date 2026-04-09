from collections.abc import Iterable
from typing import Any

import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    PointerProperty,
)
from bpy.types import Context, Material, Node, Object, PropertyGroup, Scene
from mathutils import Vector

from .util.aux_func import material_name
from .version import VersionInt

GRID_MATERIAL_NAME = "GridMaterial"


class MaterialValue:
    name: str

    def __init__(self, p_name: str) -> None:
        self.name = p_name

    def to_property(self, update_cb: Any) -> Any:
        raise NotImplementedError()


class MaterialValueInt(MaterialValue):
    default_value: int
    min_value: int
    max_value: int

    def __init__(
        self,
        p_name: str,
        default_value: int = 0,
        min_value: int = 0,
        max_value: int = 100,
    ) -> None:
        super().__init__(p_name)
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value

    def to_property(self, update_cb: Any) -> Any:
        return IntProperty(
            name=self.name,
            default=self.default_value,
            min=self.min_value,
            max=self.max_value,
            update=update_cb,
        )


class MaterialValueFloat(MaterialValue):
    default_value: float
    min_value: float
    max_value: float

    def __init__(
        self,
        p_name: str,
        default_value: float = 0.0,
        min_value: float = 0.0,
        max_value: float = 1.0,
    ) -> None:
        super().__init__(p_name)
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value

    def to_property(self, update_cb: Any) -> Any:
        return FloatProperty(
            name=self.name,
            default=self.default_value,
            min=self.min_value,
            max=self.max_value,
            update=update_cb,
        )


class MaterialValueBool(MaterialValue):
    default_value: bool

    def __init__(self, p_name: str, default_value: bool = False) -> None:
        super().__init__(p_name)
        self.default_value = default_value

    def to_property(self, update_cb: Any) -> Any:
        return BoolProperty(
            name=self.name,
            default=self.default_value,
            update=update_cb,
        )


class MaterialValueColor(MaterialValue):
    default_value: Vector

    def __init__(self, p_name: str, default_value: Vector | None = None) -> None:
        super().__init__(p_name)
        if default_value is None:
            self.default_value = Vector((1.0, 1.0, 1.0, 1.0))
        else:
            self.default_value = default_value

    def to_property(self, update_cb: Any) -> Any:
        return FloatVectorProperty(
            name=self.name,
            subtype="COLOR",
            default=self.default_value,
            size=4,
            min=0.0,
            max=1.0,
            update=update_cb,
        )


MATERIAL_PARAMS: dict[str, MaterialValue] = {
    "Param_Sub_LineWidth": MaterialValueFloat("Sub Line Width", 0.5, 0.001, 100.0),
    "Param_Sub_GridDensity": MaterialValueInt("Sub Grid Density", 4, 1, 100),
    "Param_Sub_CoplanarIntensity": MaterialValueFloat(
        "Sub Grid Coplanar Intensity", 0.03, 0.0, 1.0
    ),
    "Param_Main_LineWidth": MaterialValueFloat("Main Line Width", 1.0, 0.001, 100.0),
    "Param_Main_GridDensity": MaterialValueInt("Main Grid Density", 1, 1, 100),
    "Param_Main_CoplanarIntensity": MaterialValueFloat(
        "Main Grid Coplanar Intensity", 0.03, 0.0, 1.0
    ),
    "Param_Density": MaterialValueFloat("Grid Density (Global)", 1.0, 0.001, 100.0),
    "Param_LineWidth": MaterialValueFloat("Line Width (Global)", 0.01, 0.001, 1.0),
    "Param_SubGridVisibility": MaterialValueFloat("Sub Grid Visibility", 0.75, 0.0, 1.0),
    "Param_BGColor": MaterialValueColor("BG Color", Vector((0.005, 0.003, 0.5, 1.0))),
    "Param_GridColor": MaterialValueColor("Grid Color", Vector((1.0, 1.0, 1.0, 1.0))),
    "Param_GlobalTransform": MaterialValueBool("Global Transform", False),
}


def get_highest_version_in_names(
    names: Iterable[str], base_name: str
) -> tuple[VersionInt, str]:
    """Search for the latest version starting with the specified base name.
    The search is performed from a list of names.
    """
    highest_ver = VersionInt(0)
    target_name = ""

    for name in names:
        if name.startswith(base_name):
            try:
                ver = VersionInt.get_version_from_string(name)
                if ver >= highest_ver:
                    highest_ver, target_name = ver, name
            except Exception:
                continue
    return highest_ver, target_name


def get_grid_material_from_data() -> Material | None:
    """Search for the material with the latest version in the current data."""
    base_name = material_name(GRID_MATERIAL_NAME)
    _, target_name = get_highest_version_in_names(
        (mat.name for mat in bpy.data.materials), base_name
    )

    if not target_name:
        return None

    return bpy.data.materials.get(target_name)


def get_grid_material_slot(obj: Object | None) -> Any:
    """Get the first material slot that contains a GridMaterial."""
    if not obj or obj.type != "MESH":
        return None
    base_name = material_name(GRID_MATERIAL_NAME)
    for slot in obj.material_slots:
        if slot.material and slot.material.name.startswith(base_name):
            return slot
    return None


def has_grid_material(obj: Object | None) -> bool:
    """Check if GridMaterial is applied to the object."""
    return get_grid_material_slot(obj) is not None


def _update_node_value(node: Node, settings: Any) -> None:
    """Update values of Value/Color nodes with appropriate names."""
    if node.type in {"VALUE", "RGB"} and node.name in MATERIAL_PARAMS:
        val = getattr(settings, node.name)
        node.outputs[0].default_value = val


def sync_settings_to_material(mat: Material | None, settings: Any) -> None:
    """Update material node values based on current settings."""
    if not mat or not mat.use_nodes:
        return

    for node in mat.node_tree.nodes:
        _update_node_value(node, settings)


def update_grid_material(self, _context: Context) -> None:
    """Callback function called when N-panel properties are changed."""
    if not hasattr(self, "id_data"):
        return

    owner = self.id_data
    if isinstance(owner, bpy.types.Material):
        # Update only this material
        sync_settings_to_material(owner, self)
    elif isinstance(owner, bpy.types.Scene):
        # Scene-level settings act as defaults for newly applied materials.
        # We don't automatically update existing materials here to avoid
        # unintentionally overriding "unique" material instances.
        pass


def mpr_grid_prop(key: str) -> Any:
    """Helper function to generate Blender properties from MATERIAL_PARAMS."""
    return MATERIAL_PARAMS[key].to_property(update_grid_material)


class MPR_GridMaterialSettings(PropertyGroup):
    """Property group class to hold material settings."""

    Param_BGColor: mpr_grid_prop("Param_BGColor")
    Param_GridColor: mpr_grid_prop("Param_GridColor")
    Param_Sub_LineWidth: mpr_grid_prop("Param_Sub_LineWidth")
    Param_Sub_GridDensity: mpr_grid_prop("Param_Sub_GridDensity")
    Param_Sub_CoplanarIntensity: mpr_grid_prop("Param_Sub_CoplanarIntensity")
    Param_Main_GridDensity: mpr_grid_prop("Param_Main_GridDensity")
    Param_Main_CoplanarIntensity: mpr_grid_prop("Param_Main_CoplanarIntensity")
    Param_Main_LineWidth: mpr_grid_prop("Param_Main_LineWidth")
    Param_Density: mpr_grid_prop("Param_Density")
    Param_LineWidth: mpr_grid_prop("Param_LineWidth")
    Param_SubGridVisibility: mpr_grid_prop("Param_SubGridVisibility")
    Param_GlobalTransform: mpr_grid_prop("Param_GlobalTransform")


def register() -> None:
    """Register classes and define custom properties."""
    bpy.utils.register_class(MPR_GridMaterialSettings)
    Scene.mpr_grid_material_settings = PointerProperty(type=MPR_GridMaterialSettings)
    Material.mpr_grid_material_settings = PointerProperty(type=MPR_GridMaterialSettings)


def unregister() -> None:
    """Remove custom properties and unregister classes."""
    del Scene.mpr_grid_material_settings
    del Material.mpr_grid_material_settings
    bpy.utils.unregister_class(MPR_GridMaterialSettings)
