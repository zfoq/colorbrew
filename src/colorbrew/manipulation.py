"""Color adjustment functions: lighten, darken, saturate, mix, and more.

All functions take RGB tuples, convert to HSL internally when needed,
apply the adjustment, and convert back to RGB.
"""

from __future__ import annotations

from colorbrew.converters import hsl_to_rgb, rgb_to_hsl


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a value to the given range."""
    return max(lo, min(hi, value))


def lighten(r: int, g: int, b: int, amount: int = 10) -> tuple[int, int, int]:
    """Increase HSL lightness by the given amount.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        amount: Percentage points to add to lightness (0-100).

    Returns:
        New RGB tuple with increased lightness.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    new_l = round(_clamp(lit + amount, 0, 100))
    return hsl_to_rgb(h, s, new_l)


def darken(r: int, g: int, b: int, amount: int = 10) -> tuple[int, int, int]:
    """Decrease HSL lightness by the given amount.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        amount: Percentage points to subtract from lightness (0-100).

    Returns:
        New RGB tuple with decreased lightness.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    new_l = round(_clamp(lit - amount, 0, 100))
    return hsl_to_rgb(h, s, new_l)


def saturate(r: int, g: int, b: int, amount: int = 10) -> tuple[int, int, int]:
    """Increase HSL saturation by the given amount.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        amount: Percentage points to add to saturation (0-100).

    Returns:
        New RGB tuple with increased saturation.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    new_s = round(_clamp(s + amount, 0, 100))
    return hsl_to_rgb(h, new_s, lit)


def desaturate(r: int, g: int, b: int, amount: int = 10) -> tuple[int, int, int]:
    """Decrease HSL saturation by the given amount.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        amount: Percentage points to subtract from saturation (0-100).

    Returns:
        New RGB tuple with decreased saturation.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    new_s = round(_clamp(s - amount, 0, 100))
    return hsl_to_rgb(h, new_s, lit)


def rotate_hue(r: int, g: int, b: int, degrees: int) -> tuple[int, int, int]:
    """Shift the hue by the given number of degrees.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        degrees: Degrees to rotate (wraps at 360).

    Returns:
        New RGB tuple with shifted hue.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    new_h = (h + degrees) % 360
    return hsl_to_rgb(new_h, s, lit)


def invert(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Return the RGB inverse (255 minus each channel)."""
    return (255 - r, 255 - g, 255 - b)


def grayscale(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Remove all saturation, producing a gray of equal lightness."""
    h, _s, lit = rgb_to_hsl(r, g, b)
    return hsl_to_rgb(h, 0, lit)


def mix(
    rgb1: tuple[int, int, int],
    rgb2: tuple[int, int, int],
    weight: float = 0.5,
) -> tuple[int, int, int]:
    """Blend two colors by linear interpolation in RGB space.

    A weight of 0.0 returns ``rgb1``; a weight of 1.0 returns ``rgb2``.

    Args:
        rgb1: First color as (r, g, b).
        rgb2: Second color as (r, g, b).
        weight: Blend weight toward ``rgb2`` (0.0-1.0).

    Returns:
        New RGB tuple representing the blended color.
    """
    w = _clamp(weight, 0.0, 1.0)
    return (
        round(rgb1[0] + (rgb2[0] - rgb1[0]) * w),
        round(rgb1[1] + (rgb2[1] - rgb1[1]) * w),
        round(rgb1[2] + (rgb2[2] - rgb1[2]) * w),
    )
