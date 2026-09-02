"""CSS named colors loaded from packaged JSON data."""

from __future__ import annotations

from colorbrew.data.resources import load_palette_json

NAMED_COLORS: dict[str, str] = load_palette_json("named")

__all__ = ["NAMED_COLORS"]
