"""ColorBrew — a lightweight, zero-dependency Python library for colors.

Provides color parsing, format conversion (hex, RGB, HSL, CMYK, HSV),
CSS/HTML output, reverse name lookup (CSS, Tailwind CSS, Material Design),
color manipulation (shade, tint, tone, gradient), blend modes, palette
generation, WCAG accessibility checking (including is_light/is_dark),
color temperature analysis, color blindness simulation, and perceptual
color distance (CIE76 and CIEDE2000) through a single ``Color`` class.
"""

from __future__ import annotations

from colorbrew.analysis.delta_e import delta_e_76, delta_e_2000, rgb_to_lab
from colorbrew.color import Color
from colorbrew.conversion.converters import (
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
from colorbrew.types import BlendMode, ColorVisionDeficiency, DistanceMethod, NameMatch

__all__ = [
    "BlendMode",
    "Color",
    "ColorBrewError",
    "ColorParseError",
    "ColorValueError",
    "ColorVisionDeficiency",
    "DistanceMethod",
    "NameMatch",
    "cmyk_to_rgb",
    "delta_e_76",
    "delta_e_2000",
    "hex_to_rgb",
    "hsl_to_rgb",
    "hsv_to_rgb",
    "rgb_to_cmyk",
    "rgb_to_hex",
    "rgb_to_hsl",
    "rgb_to_hsv",
    "rgb_to_lab",
]
