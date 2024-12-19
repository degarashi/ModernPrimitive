if "bpy" in locals():
    import importlib

    importlib.reload(modern_primitive)  # noqa: F821
    importlib.reload(modifier_select)  # noqa: F821
    importlib.reload(convert)  # noqa: F821
    importlib.reload(cube)  # noqa: F821
    importlib.reload(version)  # noqa: F821
else:
    from .src import modern_primitive
    from .src import modifier_select
    from .src import convert
    from .src import cube
    from .src import version

import bpy  # noqa: F401


def register():
    print("-------------ModernPrimitive::register()--------------")
    modern_primitive.register()
    modifier_select.register()
    convert.register()
    cube.register()
    version.register()


def unregister():
    print("-------------ModernPrimitive::unregister()-----------")
    modern_primitive.unregister()
    modifier_select.unregister()
    convert.unregister()
    cube.unregister()
    version.unregister()
