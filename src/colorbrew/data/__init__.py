"""Color palette data and optional stdlib-only palette loading helpers."""

from colorbrew.data.api import get_palette, refresh_palette
from colorbrew.data.material_colors import MATERIAL_COLORS
from colorbrew.data.named_colors import NAMED_COLORS
from colorbrew.data.registry import (
    SystemRecord,
    get_system,
    list_palettes,
    list_systems,
    register_system,
    resolve_name,
)
from colorbrew.data.tailwind_colors import TAILWIND_COLORS


__all__ = [
    "SystemRecord",
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
