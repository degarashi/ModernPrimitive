from typing import Dict, Any
from bpy.types import (
    KeyMap,
    KeyMapItem,
)


class KeyAssign:
    def __init__(
        self,
        idname: str,
        key: str,
        event: str,
        ctrl: bool,
        alt: bool,
        shift: bool,
        *,
        prop: Dict[str, Any] | None = None,
    ):
        self._idname = idname
        self._key = key
        self._event = event
        self._ctrl = ctrl
        self._alt = alt
        self._shift = shift
        self._prop = prop

    def register(self, km: KeyMap) -> KeyMapItem:
        kmi = km.keymap_items.new(
            self._idname,
            self._key,
            self._event,
            ctrl=self._ctrl,
            alt=self._alt,
            shift=self._shift,
        )
        if isinstance(self._prop, dict):
            for k, v in self._prop.items():
                setattr(kmi.properties, k, v)
        return kmi
