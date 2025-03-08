def import_modules(mod_name: list[str]):
    import importlib.util

    modules = {}
    for name in mod_name:
        modules[name] = importlib.import_module(f".src.{name}", package=__package__)
    return modules


def reload_modules(mod_name: list[str]):
    import importlib

    modules = {}
    for name in mod_name:
        modules[name] = importlib.reload(globals()[name])
    return modules


MODULE_NAMES: list[str] = [
    "modern_primitive",
    "focus_modifier",
    "equalize_dcube_size",
    "version",
    "panel",
    "check_editmesh",
    "wireframe",
    "switch_wireframe",
    "apply_scale",
    "preference",
    "hud_draw",
    "restore_default",
    "convert",
    "apply_mesh",
    "reset_origin",
]

modules = (
    import_modules(MODULE_NAMES)
    if "bpy" not in locals()
    else reload_modules(MODULE_NAMES)
)


import bpy  # noqa: F401, E402


def register():
    print("-------------ModernPrimitive::register()--------------")
    for module in modules.values():
        module.register()


def unregister():
    print("-------------ModernPrimitive::unregister()-----------")
    for module in modules.values():
        module.unregister()
