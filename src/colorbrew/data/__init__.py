"""Color palette data and optional stdlib-only palette loading helpers."""

from colorbrew.data.api import get_palette, refresh_palette
from colorbrew.data.loader import (
    MATERIAL_COLORS,
    NAMED_COLORS,
    TAILWIND_COLORS,
)
from colorbrew.data.registry import (
    SystemRecord,
    get_system,
    list_palettes,
    list_systems,
    register_system,
    resolve_name,
)


def __getattr__(name: str):
    if name == "Palette":
        from colorbrew.palette import Palette

        return Palette
    raise AttributeError(name)


__all__ = [
    "SystemRecord",
    "Palette",
    "get_palette",
    "get_system",
    "list_palettes",
    "list_systems",
    "refresh_palette",
    "register_system",
    "resolve_name",
    "MATERIAL_COLORS",
    "NAMED_COLORS",
    "TAILWIND_COLORS",
]
