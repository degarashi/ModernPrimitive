from .convert_to_cube import ConvertToCube_Operator
from .convert_to_grid import ConvertToGrid_Operator
from .convert_to_sphere import ConvertToSphere_Operator
from .convert_to_cylinder import ConvertToCylinder_Operator
from .convert_to_cone import ConvertToCone_Operator
from .convert_to_torus import ConvertToTorus_Operator
from .convert_to_tube import ConvertToTube_Operator
from .convert_to_capsule import ConvertToCapsule_Operator
from bpy.utils import register_class, unregister_class

_CLS = (
    ConvertToCube_Operator,
    ConvertToGrid_Operator,
    ConvertToSphere_Operator,
    ConvertToCylinder_Operator,
    ConvertToCone_Operator,
    ConvertToTorus_Operator,
    ConvertToTube_Operator,
    ConvertToCapsule_Operator,
)


def register() -> None:
    for c in _CLS:
        register_class(c)


def unregister() -> None:
    for c in _CLS:
        unregister_class(c)
