"""Format colors as CSS/HTML-ready strings.

All functions accept primitive types and return formatted strings suitable
for direct use in stylesheets and HTML attributes.
"""

from __future__ import annotations

from colorbrew.converters import rgb_to_hsl


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
        ValueError: If alpha is outside 0.0-1.0.
    """
    _validate_alpha(a)
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
        ValueError: If alpha is outside 0.0-1.0.
    """
    _validate_alpha(a)
    h, s, lit = rgb_to_hsl(r, g, b)
    return f"hsla({h}, {s}%, {lit}%, {a})"


def _validate_alpha(a: float) -> None:
    """Raise ``ValueError`` if alpha is outside 0.0-1.0."""
    if not isinstance(a, (int, float)) or a < 0.0 or a > 1.0:
        raise ValueError(f"Alpha must be between 0.0 and 1.0, got {a}")
