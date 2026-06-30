# Modern Primitive
A Blender add-on for non-destructive modeling, providing 13 procedural primitives based on Geometry Nodes with interactive gizmos and a streamlined workflow.

<img src="./doc_images/main_image_0.jpg" alt="Modern Primitive Main Image" /><br>
<div><video controls src="https://github.com/user-attachments/assets/af1c5da9-1dcc-49d4-870b-7e9b7e9eb598" muted="false"></video></div>

## Features

### 13 Procedural Primitives
All primitives are built with Geometry Nodes, allowing for non-destructive editing at any time.
- **Cube / Deformable Cube**
- **UV Sphere / Ico Sphere / Quad Sphere**
- **Cylinder / Cone / Capsule / Tube**
- **Torus / Gear / Spring / Grid**

### Interactive Workflow
- **In-Viewport Gizmos**: Adjust parameters like radius, height, and divisions directly in the 3D view.
- **HUD (Heads-Up Display)**: Real-time display of parameter values and snapping information. Optionally show world-space values alongside local values when the object has non-uniform scale (configurable in Preferences → HUD, **disabled by default**).
<img src="./doc_images/world_space_scale_hud.jpg" alt="World-Space HUD Display" width="75%" />
- **Modal Edit (`Ctrl + Shift + C`)**: Enter a modal mode to adjust parameters using keyboard shortcuts (e.g., `S` for Size, `H` for Height, `W` for Smooth), numeric input, and mouse wheel.
<img src="./doc_images/modal_edit.jpg" alt="Modal Edit" width="50%" />
<img src="./doc_images/modal_edit2.jpg" alt="Modal Edit Smooth" width="50%" />
- **Focus Modifier (`Ctrl + Alt + X`)**: Instantly select and focus the Modern Primitive modifier for quick adjustments.
- **Snapping**: Precise control over primitive parameters with snapping support.

### Advanced Tools
- **Convert to Primitive**: Convert existing meshes into Modern Primitives. Reuses the original object to maintain Boolean relationships, materials, and modifiers.
- **Extract to Primitive**: Select polygons in Edit Mode and convert them into a new Modern Primitive object. Supports multi-region selection.
- **Origin Manipulation**: Move the object origin freely (using Blender's "Affect Only Origins") and reset it to the default position via the N-panel.
- **UV Generation**: Supports `Simple` and `Evenly` (texel density preserving) UV mapping. (Requires specifying the UV name in a Shader Attribute node, default is "UVMap")
- **Grid Material**: A procedural grid material for layout and UV checking. Parameters such as color, density, and line width can be adjusted directly from the MPR panel.
<img src="./doc_images/grid_material.jpg" alt="Grid Material" width="75%" />
- **Apply Mesh**: Bake the procedural shape to a static mesh while optionally keeping the modifier for reference.
- **Apply Scale**: Synchronize gizmos with the object's scale.

## Requirement
- **Blender 4.3 or later**

## Usage

### 1. Creation
Add a Modern Primitive via the **Add Menu**:
`Shift + A` -> `Mesh` -> `Modern Primitive` -> (Select Shape)

You can also use the **MPR tab** in the N-panel for quick access.

<img src="./doc_images/menu0.png" alt="Add Menu" width="50%" />

### 2. Adjustment
- **Modifier Properties**: Fine-tune all parameters in the Modifier tab.
- **Gizmos**: Use the interactive handles in the viewport.
- **N-Panel [MPR]**: Access extra tools like "Apply Mesh", "Restore Defaults", "Conversion" tools, and Grid Material settings.

<img src="./doc_images/mpr_panel.jpg" alt="N-Panel" width="75%" />

### 3. Shortcut
- **`Ctrl + Alt + X`**: Focus the Modern Primitive modifier. Pressing it again will unfocus/toggle.
- **`Ctrl + Shift + C`**: Start Modal Edit.

Keybindings can be viewed and restored from the **Preferences** panel.

<img src="./doc_images/shortcut_key_2.jpg" alt="Shortcut Key Preferences" width="75%" />

## Gallery
<img src="./doc_images/usage_cube_1.jpg" alt="" width="24%" /> <img src="./doc_images/usage_cone_1.jpg" alt="" width="24%" /> <img src="./doc_images/usage_cylinder_2.jpg" alt="" width="24%" /> <img src="./doc_images/usage_grid_1.jpg" alt="" width="24%" />
<img src="./doc_images/usage_icosphere_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_torus_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_uvsphere_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_tube_2.jpg" alt="" width="24%" />
<img src="./doc_images/usage_gear_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_spring_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_deformable_cube_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_capsule_0.jpg" alt="" width="24%" />

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for full history.

## Author
Degarashi ([@degarashi](https://github.com/degarashi))
ps://github.com/degarashi))
