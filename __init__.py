if "bpy" in locals():
    import importlib

    importlib.reload(modern_primitive)  # noqa: F821
else:
    from . import modern_primitive

import bpy # noqa: F401


def register():
    print("-------------ModernPrimitive::register()--------------")
    modern_primitive.register()


def unregister():
    print("-------------ModernPrimitive::unregister()-----------")
    modern_primitive.unregister()
