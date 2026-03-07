"""Input parsing and normalization for color values.

Converts user-provided strings (hex, CSS functions, named colors) and
integer arguments into validated RGB tuples. Supports both legacy
comma-separated CSS syntax and modern CSS Color Level 4 space-separated
syntax.
"""

from __future__ import annotations

import re

from colorbrew.conversion.converters import hex_to_rgb, hex_to_rgba, hsl_to_rgb
from colorbrew.conversion.css_output import validate_alpha
from colorbrew.data.named_colors import NAMED_COLORS
from colorbrew.exceptions import ColorParseError, ColorValueError

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

# Legacy comma-separated: rgb(52, 152, 219) / rgba(52, 152, 219, 0.8)
_RGB_FUNC_RE = re.compile(
    r"^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})"
    r"(?:\s*,\s*([01]?\.?\d*))?\s*\)$"
)
# Modern space-separated: rgb(52 152 219) / rgb(52 152 219 / 0.8)
_RGB_MODERN_RE = re.compile(
    r"^rgba?\(\s*(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})"
    r"(?:\s*/\s*([01]?\.?\d*%?))?\s*\)$"
)
# Legacy: hsl(204, 70%, 53%) / hsla(204, 70%, 53%, 0.8)
_HSL_FUNC_RE = re.compile(
    r"^hsla?\(\s*(\d{1,3})\s*,\s*(\d{1,3})%?\s*,\s*(\d{1,3})%?"
    r"(?:\s*,\s*([01]?\.?\d*))?\s*\)$"
)
# Modern: hsl(204deg 70% 53%) / hsl(204 70% 53% / 0.8)
_HSL_MODERN_RE = re.compile(
    r"^hsla?\(\s*(\d{1,3})(?:deg)?\s+(\d{1,3})%?\s+(\d{1,3})%?"
    r"(?:\s*/\s*([01]?\.?\d*%?))?\s*\)$"
)


def parse_string(value: str) -> tuple[int, int, int]:
    """Parse a color string into an RGB tuple, discarding any alpha.

    Convenience wrapper around ``parse_string_with_alpha``.

    Args:
        value: Color string to parse.

    Returns:
        Validated RGB tuple (r, g, b) with values 0-255.

    Raises:
        ColorParseError: If the string cannot be parsed.
    """
    rgb, _alpha = parse_string_with_alpha(value)
    return rgb


def _parse_alpha(raw: str | None) -> float:
    """Parse an optional alpha string to a float 0.0-1.0."""
    if raw is None or raw == "":
        return 1.0
    if raw.endswith("%"):
        val = float(raw[:-1]) / 100.0
    else:
        val = float(raw)
    validate_alpha(val)
    return val


def parse_string_with_alpha(value: str) -> tuple[tuple[int, int, int], float]:
    """Parse a color string into an RGB tuple and alpha value.

    Accepts all formats supported by ``parse_string``. If no alpha is
    specified, defaults to 1.0.

    Args:
        value: Color string to parse.

    Returns:
        Tuple of (RGB tuple, alpha float).

    Raises:
        ColorParseError: If the string cannot be parsed.
    """
    value = value.strip()

    # Try hex (3/4/6/8 digit)
    m = _HEX_RE.match(value)
    if m:
        return hex_to_rgba(value)

    # Try rgb/rgba — legacy comma-separated
    rm = _RGB_FUNC_RE.match(value)
    if rm:
        r, g, b = int(rm.group(1)), int(rm.group(2)), int(rm.group(3))
        _validate_rgb(r, g, b)
        alpha = _parse_alpha(rm.group(4))
        return ((r, g, b), alpha)

    # Try rgb/rgba — modern space-separated
    rm = _RGB_MODERN_RE.match(value)
    if rm:
        r, g, b = int(rm.group(1)), int(rm.group(2)), int(rm.group(3))
        _validate_rgb(r, g, b)
        alpha = _parse_alpha(rm.group(4))
        return ((r, g, b), alpha)

    # Try hsl/hsla — legacy comma-separated
    hm = _HSL_FUNC_RE.match(value)
    if hm:
        h, s, lit = int(hm.group(1)), int(hm.group(2)), int(hm.group(3))
        _validate_hsl(h, s, lit)
        alpha = _parse_alpha(hm.group(4))
        return (hsl_to_rgb(h, s, lit), alpha)

    # Try hsl/hsla — modern space-separated
    hm = _HSL_MODERN_RE.match(value)
    if hm:
        h, s, lit = int(hm.group(1)), int(hm.group(2)), int(hm.group(3))
        _validate_hsl(h, s, lit)
        alpha = _parse_alpha(hm.group(4))
        return (hsl_to_rgb(h, s, lit), alpha)

    # Try named color
    name = value.lower()
    if name in NAMED_COLORS:
        return (hex_to_rgb(NAMED_COLORS[name]), 1.0)

    raise ColorParseError(f"Cannot parse color string: {value!r}")


def parse_rgb_args(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Validate and return an RGB tuple from three integer arguments.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Validated RGB tuple.

    Raises:
        ColorValueError: If any value is outside 0-255.
    """
    _validate_rgb(r, g, b)
    return (r, g, b)


def _validate_rgb(r: int, g: int, b: int) -> None:
    """Raise ``ColorValueError`` if any channel is outside 0-255."""
    for name, val in (("r", r), ("g", g), ("b", b)):
        if not isinstance(val, int) or isinstance(val, bool):
            raise ColorValueError(
                f"{name} must be an integer, got {type(val).__name__}"
            )
        if val < 0 or val > 255:
            raise ColorValueError(
                f"{name} must be 0-255, got {val}"
            )


def _validate_hsl(h: int, s: int, lit: int) -> None:
    """Raise ``ColorValueError`` if HSL values are out of range."""
    if h < 0 or h > 360:
        raise ColorValueError(f"Hue must be 0-360, got {h}")
    if s < 0 or s > 100:
        raise ColorValueError(f"Saturation must be 0-100, got {s}")
    if lit < 0 or lit > 100:
        raise ColorValueError(f"Lightness must be 0-100, got {lit}")
