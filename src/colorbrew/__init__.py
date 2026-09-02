"""ColorBrew — a lightweight, zero-dependency Python library for colors.

Provides color parsing, format conversion (hex, RGB, HSL, CMYK, HSV),
CSS/HTML output, reverse name lookup (CSS, Tailwind CSS, Material Design),
color manipulation (shade, tint, tone, gradient), blend modes, palette
generation, WCAG accessibility checking (including is_light/is_dark),
color temperature analysis and approximation, color blindness simulation,
and perceptual color distance (CIE76 and CIEDE2000) through a single
``Color`` class.
"""

from __future__ import annotations

from importlib.metadata import version as _version

from colorbrew.analysis.delta_e import delta_e_76, delta_e_2000, lab_to_rgb, rgb_to_lab
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
from colorbrew.data import (
    get_system,
    list_palettes,
    list_systems,
    register_system,
    resolve_name,
)
from colorbrew.data.registry import get_palette
from colorbrew.exceptions import (
    ColorBrewError,
    ColorParseError,
    ColorValueError,
    PaletteError,
)
from colorbrew.palette import Palette, Theme
from colorbrew.settings import Settings, configure, settings_context
from colorbrew.types import ColorClass, NameMatch, WcagReport

__version__ = _version("colorbrew")

__all__ = [
    "Color",
    "ColorBrewError",
    "ColorClass",
    "ColorParseError",
    "ColorValueError",
    "NameMatch",
    "Palette",
    "PaletteError",
    "Settings",
    "Theme",
    "WcagReport",
    "cmyk_to_rgb",
    "configure",
    "delta_e_76",
    "delta_e_2000",
    "get_palette",
    "get_system",
    "hex_to_rgb",
    "hsl_to_rgb",
    "hsv_to_rgb",
    "lab_to_rgb",
    "list_palettes",
    "list_systems",
    "register_system",
    "resolve_name",
    "rgb_to_cmyk",
    "rgb_to_hex",
    "rgb_to_hsl",
    "rgb_to_hsv",
    "rgb_to_lab",
    "settings_context",
]
