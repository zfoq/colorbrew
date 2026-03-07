"""Format colors as CSS/HTML-ready strings.

All functions accept primitive types and return formatted strings suitable
for direct use in stylesheets and HTML attributes. Both legacy
comma-separated and modern CSS Color Level 4 space-separated formats
are supported.
"""

from __future__ import annotations

from colorbrew.conversion.converters import rgb_to_hsl
from colorbrew.exceptions import ColorValueError


def validate_alpha(a: float) -> None:
    """Raise ``ColorValueError`` if alpha is outside 0.0-1.0.

    Args:
        a: Alpha value to validate.

    Raises:
        ColorValueError: If alpha is not a number or outside 0.0-1.0.
    """
    if not isinstance(a, (int, float)) or a < 0.0 or a > 1.0:
        raise ColorValueError(f"Alpha must be between 0.0 and 1.0, got {a}")


def to_css_rgb(r: int, g: int, b: int) -> str:
    """Return a CSS ``rgb()`` function string.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        String like ``"rgb(52, 152, 219)"``.
    """
    return f"rgb({r}, {g}, {b})"


def to_css_rgba(r: int, g: int, b: int, a: float) -> str:
    """Return a CSS ``rgba()`` function string.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        a: Alpha value (0.0-1.0).

    Returns:
        String like ``"rgba(52, 152, 219, 0.8)"``.

    Raises:
        ColorValueError: If alpha is outside 0.0-1.0.
    """
    validate_alpha(a)
    return f"rgba({r}, {g}, {b}, {a})"


def to_css_hsl(r: int, g: int, b: int) -> str:
    """Return a CSS ``hsl()`` function string.

    Converts from RGB internally.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        String like ``"hsl(204, 70%, 53%)"``.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    return f"hsl({h}, {s}%, {lit}%)"


def to_css_hsla(r: int, g: int, b: int, a: float) -> str:
    """Return a CSS ``hsla()`` function string.

    Converts from RGB internally.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        a: Alpha value (0.0-1.0).

    Returns:
        String like ``"hsla(204, 70%, 53%, 0.8)"``.

    Raises:
        ColorValueError: If alpha is outside 0.0-1.0.
    """
    validate_alpha(a)
    h, s, lit = rgb_to_hsl(r, g, b)
    return f"hsla({h}, {s}%, {lit}%, {a})"


def to_css_rgb_modern(r: int, g: int, b: int, a: float = 1.0) -> str:
    """Return a modern CSS Color Level 4 ``rgb()`` string.

    Uses space-separated syntax with optional slash alpha:
    ``rgb(52 152 219)`` or ``rgb(52 152 219 / 0.8)``.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        a: Alpha value (0.0-1.0, default 1.0).

    Returns:
        Modern CSS rgb() string.

    Raises:
        ColorValueError: If alpha is outside 0.0-1.0.
    """
    validate_alpha(a)
    if a < 1.0:
        return f"rgb({r} {g} {b} / {a})"
    return f"rgb({r} {g} {b})"


def to_css_hsl_modern(r: int, g: int, b: int, a: float = 1.0) -> str:
    """Return a modern CSS Color Level 4 ``hsl()`` string.

    Uses space-separated syntax with optional slash alpha:
    ``hsl(204 70% 53%)`` or ``hsl(204 70% 53% / 0.8)``.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        a: Alpha value (0.0-1.0, default 1.0).

    Returns:
        Modern CSS hsl() string.

    Raises:
        ColorValueError: If alpha is outside 0.0-1.0.
    """
    validate_alpha(a)
    h, s, lit = rgb_to_hsl(r, g, b)
    if a < 1.0:
        return f"hsl({h} {s}% {lit}% / {a})"
    return f"hsl({h} {s}% {lit}%)"
