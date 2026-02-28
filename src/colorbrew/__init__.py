"""ColorBrew — a lightweight, zero-dependency Python library for colors.

Provides color parsing, format conversion (hex, RGB, HSL, CMYK, HSV),
CSS/HTML output, reverse name lookup, color manipulation (shade, tint,
tone, gradient), blend modes, palette generation, WCAG accessibility
checking (including is_light/is_dark), color temperature analysis, and
color blindness simulation through a single ``Color`` class.
"""

from __future__ import annotations

from colorbrew.color import Color
from colorbrew.converters import (
    cmyk_to_rgb,
    hex_to_rgb,
    hsl_to_rgb,
    hsv_to_rgb,
    rgb_to_cmyk,
    rgb_to_hex,
    rgb_to_hsl,
    rgb_to_hsv,
)
from colorbrew.exceptions import ColorBrewError, ColorParseError, ColorValueError
from colorbrew.types import NameMatch

__all__ = [
    "Color",
    "ColorBrewError",
    "ColorParseError",
    "ColorValueError",
    "NameMatch",
    "cmyk_to_rgb",
    "hex_to_rgb",
    "hsl_to_rgb",
    "hsv_to_rgb",
    "rgb_to_cmyk",
    "rgb_to_hex",
    "rgb_to_hsl",
    "rgb_to_hsv",
]
