if "bpy" in locals():
    import importlib

    importlib.reload(modern_primitive)  # noqa: F821
    importlib.reload(modifier_select)  # noqa: F821
    importlib.reload(convert)  # noqa: F821
    importlib.reload(cube)  # noqa: F821
else:
    from . import modern_primitive
    from . import modifier_select
    from . import convert
    from . import cube

import bpy  # noqa: F401


def register():
    print("-------------ModernPrimitive::register()--------------")
    modern_primitive.register()
    modifier_select.register()
    convert.register()
    cube.register()


def unregister():
    print("-------------ModernPrimitive::unregister()-----------")
    modern_primitive.unregister()
    modifier_select.unregister()
    convert.unregister()
    cube.unregister()
