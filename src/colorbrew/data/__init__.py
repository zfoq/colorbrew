"""Color palette data and optional stdlib-only palette loading helpers."""

from colorbrew.data.api import (
    get_palette,
    get_palette_entries,
    list_palettes,
    refresh_palette,
)
from colorbrew.data.material_colors import MATERIAL_COLORS
from colorbrew.data.models import Palette
from colorbrew.data.named_colors import NAMED_COLORS
from colorbrew.data.tailwind_colors import TAILWIND_COLORS

__all__ = [
    "get_palette",
    "get_palette_entries",
    "list_palettes",
    "refresh_palette",
    "Palette",
    "MATERIAL_COLORS",
    "NAMED_COLORS",
    "TAILWIND_COLORS",
]
