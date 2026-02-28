"""ColorBrew — a lightweight, zero-dependency Python library for colors.

Provides color parsing, format conversion, CSS/HTML output, reverse name
lookup, color manipulation, and blend modes through a single ``Color`` class.
"""

from __future__ import annotations

from colorbrew.color import Color
from colorbrew.converters import hex_to_rgb, hsl_to_rgb, rgb_to_hex, rgb_to_hsl
from colorbrew.exceptions import ColorBrewError, ColorParseError, ColorValueError
from colorbrew.types import NameMatch

__all__ = [
    "Color",
    "ColorBrewError",
    "ColorParseError",
    "ColorValueError",
    "NameMatch",
    "hex_to_rgb",
    "hsl_to_rgb",
    "rgb_to_hex",
    "rgb_to_hsl",
]
