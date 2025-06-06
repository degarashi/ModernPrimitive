from types import ModuleType

from . import object_panel

MODULES: tuple[ModuleType, ...] = (object_panel,)


def register() -> None:
    for module in MODULES:
        module.register()


def unregister() -> None:
    for module in MODULES:
        module.unregister()
