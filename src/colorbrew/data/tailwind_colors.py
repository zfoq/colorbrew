"""Tailwind CSS v3 color palette loaded from packaged JSON data."""

from __future__ import annotations

from colorbrew.data.resources import load_palette_json

TAILWIND_COLORS: dict[str, str] = load_palette_json("tailwind")

__all__ = ["TAILWIND_COLORS"]
