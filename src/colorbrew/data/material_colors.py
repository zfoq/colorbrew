"""Material Design v2 color palette loaded from packaged JSON data."""

from __future__ import annotations

from colorbrew.data.resources import load_palette_json

MATERIAL_COLORS: dict[str, str] = load_palette_json("material")

__all__ = ["MATERIAL_COLORS"]
