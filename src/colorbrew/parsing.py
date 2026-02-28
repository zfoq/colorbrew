"""Input parsing and normalization for color values.

Converts user-provided strings (hex, CSS functions, named colors) and
integer arguments into validated RGB tuples.
"""

from __future__ import annotations

import re

from colorbrew.converters import hex_to_rgb, hsl_to_rgb
from colorbrew.exceptions import ColorParseError, ColorValueError
from colorbrew.named_colors import NAMED_COLORS

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGB_FUNC_RE = re.compile(
    r"^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$"
)
_HSL_FUNC_RE = re.compile(
    r"^hsl\(\s*(\d{1,3})\s*,\s*(\d{1,3})%?\s*,\s*(\d{1,3})%?\s*\)$"
)


def parse_string(value: str) -> tuple[int, int, int]:
    """Parse a color string into an RGB tuple.

    Accepts hex strings, CSS ``rgb()`` / ``hsl()`` function strings, and
    CSS named color strings (case-insensitive).

    Args:
        value: Color string to parse.

    Returns:
        Validated RGB tuple (r, g, b) with values 0-255.

    Raises:
        ColorParseError: If the string cannot be parsed as any known format.
    """
    value = value.strip()

    # Try hex
    if _HEX_RE.match(value):
        return hex_to_rgb(value)

    # Try rgb() function
    m = _RGB_FUNC_RE.match(value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        _validate_rgb(r, g, b)
        return (r, g, b)

    # Try hsl() function
    m = _HSL_FUNC_RE.match(value)
    if m:
        h, s, lit = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return hsl_to_rgb(h, s, lit)

    # Try named color
    name = value.lower()
    if name in NAMED_COLORS:
        return hex_to_rgb(NAMED_COLORS[name])

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
