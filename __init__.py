if "bpy" in locals():
    import importlib

    importlib.reload(modern_primitive)  # noqa: F821
    importlib.reload(modifier_select)  # noqa: F821
    importlib.reload(convert_to_cube)  # noqa: F821
    importlib.reload(cube)  # noqa: F821
    importlib.reload(version)  # noqa: F821
    importlib.reload(panel)  # noqa: F821
    importlib.reload(check_editmesh)  # noqa: F821
    importlib.reload(wireframe)  # noqa: F821
    importlib.reload(switch_wireframe) # noqa: F821
    importlib.reload(apply_scale) # noqa: F821
    importlib.reload(preference) # noqa: F821
    importlib.reload(hud_draw) # noqa: F821
    importlib.reload(restore_default)  # noqa: F821
else:
    from .src import modern_primitive
    from .src import modifier_select
    from .src.convert import convert_to_cube
    from .src import cube
    from .src import version
    from .src import panel
    from .src import check_editmesh
    from .src import wireframe
    from .src import switch_wireframe
    from .src import apply_scale
    from .src import preference
    from .src import hud_draw
    from .src import restore_default

import bpy  # noqa: F401


def register():
    print("-------------ModernPrimitive::register()--------------")
    modern_primitive.register()
    modifier_select.register()
    convert_to_cube.register()
    cube.register()
    version.register()
    panel.register()
    check_editmesh.register()
    wireframe.register()
    switch_wireframe.register()
    apply_scale.register()
    preference.register()
    hud_draw.register()
    restore_default.register()


def unregister():
    print("-------------ModernPrimitive::unregister()-----------")
    modern_primitive.unregister()
    modifier_select.unregister()
    convert_to_cube.unregister()
    cube.unregister()
    version.unregister()
    panel.unregister()
    check_editmesh.unregister()
    wireframe.unregister()
    switch_wireframe.unregister()
    apply_scale.unregister()
    preference.unregister()
    hud_draw.unregister()
    restore_default.unregister()
