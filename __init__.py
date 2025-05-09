import importlib
import logging
import sys
from types import ModuleType
from typing import TypeAlias

ModuleDict: TypeAlias = dict[str, ModuleType]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODULE_PREFIX = "src"
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


def _load_module(name: str) -> ModuleType:
    full_name: str = f".{MODULE_PREFIX}.{name}"
    try:
        imported_module: ModuleType = importlib.import_module(full_name, package=__package__)
    except ImportError as e:
        logger.error(f"Failed to import module '{full_name}': {e}")
        raise
    sys.modules[full_name] = imported_module
    return imported_module


def _import_modules(mod_names: list[str]) -> ModuleDict:
    modules: ModuleDict = {}
    for name in mod_names:
        modules[name] = _load_module(name)
    return modules


def _reload_modules(mod_names: list[str]) -> ModuleDict:
    modules: ModuleDict = {}
    for name in mod_names:
        if name in sys.modules:
            modules[name] = importlib.reload(sys.modules[name])
        else:
            logger.warning(f"Module '{name}' not found in sys.modules; re-importing.")
            modules[name] = _load_module(name)
    return modules


def _call_if_hasmethod(module: ModuleType, method_name: str) -> None:
    method = getattr(module, method_name, None)
    if method is None:
        logger.warning(
            f'Module "{getattr(module, "__name__", str(module))}" has no method "{method_name}()"'  # noqa: E501
        )
    else:
        method()


def register():
    logger.info("[ModernPrimitive::register()]")
    for module in modules.values():
        _call_if_hasmethod(module, "register")


def unregister():
    logger.info("[ModernPrimitive::unregister()]")
    for module in modules.values():
        _call_if_hasmethod(module, "unregister")


def _should_reload() -> bool:
    return "bpy" in locals()


modules: ModuleDict = (
    _import_modules(MODULE_NAMES) if not _should_reload() else _reload_modules(MODULE_NAMES)
)
