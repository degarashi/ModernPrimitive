import importlib
import logging
from types import ModuleType
from typing import TypeAlias

__all__ = ["register", "unregister"]

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
    "hud.hud_draw",
    "restore_default",
    "convert",
    "apply_mesh",
    "reset_origin",
]


def _make_fullname(name: str) -> str:
    return f".{MODULE_PREFIX}.{name}"


def _import_modules(mod_names: list[str]) -> ModuleDict:
    logger.info("Begin importing submodules...")

    def load_module(name: str) -> ModuleType:
        full_name = _make_fullname(name)
        try:
            imported_module: ModuleType = importlib.import_module(
                full_name, package=__package__
            )
        except ImportError as e:
            logger.error(f"Failed to import module '{full_name}': {e}")
            raise
        return imported_module

    modules: ModuleDict = {}
    for name in mod_names:
        logger.info(f"Importing submodule '{name}'")
        modules[name] = load_module(name)
    logger.info("Importing submodule Done!")
    return modules


def _reload_modules(modules: ModuleDict) -> ModuleDict:
    logger.info("Begin reloading submodules...")
    ret: ModuleDict = {}
    for name, mod in modules.items():
        logger.info(f"Reloading submodule '{name}'")
        ret[name] = importlib.reload(mod)
    logger.info("Reloading submodule Done!")
    return ret


def _call_if_hasmethod(module: ModuleType, method_name: str) -> None:
    method = getattr(module, method_name, None)

    if method is None or not callable(method):

        def get_module_name() -> str:
            return getattr(module, "__name__", str(module))

        logger.warning(f'Module "{get_module_name()}" has no method "{method_name}()"')
    else:
        method()


modules: ModuleDict
_should_reload = "bpy" in locals()
import bpy  # noqa: E402, F401


def register():
    global modules  # noqa: PLW0603

    logger.info("=========== register() ===========")
    modules = _import_modules(MODULE_NAMES) if not _should_reload else _reload_modules(modules)

    for module in modules.values():
        _call_if_hasmethod(module, "register")


def unregister():
    global modules  # noqa: PLW0602

    logger.info("=========== unregister() ===========")
    for module in modules.values():
        _call_if_hasmethod(module, "unregister")
