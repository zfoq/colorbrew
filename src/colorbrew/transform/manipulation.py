"""Color adjustment functions: lighten, darken, saturate, mix, and more.

All functions take RGB tuples, convert to HSL internally when needed,
apply the adjustment, and convert back to RGB.
"""

from __future__ import annotations

from typing import Literal

from colorbrew.conversion.converters import hsl_to_rgb, rgb_to_hsl


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


def shade(
    r: int, g: int, b: int, amount: float = 0.5
) -> tuple[int, int, int]:
    """Mix a color with black to create a shade.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        amount: Weight toward black (0.0 = original, 1.0 = black).

    Returns:
        New darker RGB tuple.
    """
    return mix((r, g, b), (0, 0, 0), amount)


def tint(
    r: int, g: int, b: int, amount: float = 0.5
) -> tuple[int, int, int]:
    """Mix a color with white to create a tint.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        amount: Weight toward white (0.0 = original, 1.0 = white).

    Returns:
        New lighter RGB tuple.
    """
    return mix((r, g, b), (255, 255, 255), amount)


def tone(
    r: int, g: int, b: int, amount: float = 0.5
) -> tuple[int, int, int]:
    """Mix a color with gray to create a tone.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        amount: Weight toward gray (0.0 = original, 1.0 = gray).

    Returns:
        New muted RGB tuple.
    """
    return mix((r, g, b), (128, 128, 128), amount)


def _mix_lab(
    rgb1: tuple[int, int, int],
    rgb2: tuple[int, int, int],
    weight: float,
) -> tuple[int, int, int]:
    """Blend two colors by linear interpolation in CIE L*a*b* space."""
    from colorbrew.analysis.delta_e import rgb_to_lab
    from colorbrew.conversion.gamma import delinearize

    w = _clamp(weight, 0.0, 1.0)
    l1, a1, b1 = rgb_to_lab(*rgb1)
    l2, a2, b2 = rgb_to_lab(*rgb2)

    # Interpolate in Lab
    ls = l1 + (l2 - l1) * w
    a = a1 + (a2 - a1) * w
    b = b1 + (b2 - b1) * w

    # Lab -> XYZ -> linear RGB -> sRGB
    _XN = 0.95047
    _YN = 1.00000
    _ZN = 1.08883
    _EPSILON = 216 / 24389
    _KAPPA = 24389 / 27

    fy = (ls + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0

    fx3 = fx ** 3
    fz3 = fz ** 3

    xr = fx3 if fx3 > _EPSILON else (116.0 * fx - 16.0) / _KAPPA
    yr = ((ls + 16.0) / 116.0) ** 3 if ls > _KAPPA * _EPSILON else ls / _KAPPA
    zr = fz3 if fz3 > _EPSILON else (116.0 * fz - 16.0) / _KAPPA

    x = xr * _XN
    y = yr * _YN
    z = zr * _ZN

    # XYZ -> linear RGB (inverse of SRGB_TO_XYZ)
    rl = 3.2404542 * x - 1.5371385 * y - 0.4985314 * z
    gl = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
    bl = 0.0556434 * x - 0.2040259 * y + 1.0572252 * z

    return (delinearize(rl), delinearize(gl), delinearize(bl))


def gradient(
    rgb1: tuple[int, int, int],
    rgb2: tuple[int, int, int],
    steps: int = 5,
    space: Literal["rgb", "lab"] = "rgb",
) -> list[tuple[int, int, int]]:
    """Generate a list of colors between two endpoints.

    Args:
        rgb1: Start color as (r, g, b).
        rgb2: End color as (r, g, b).
        steps: Number of colors to generate (minimum 2).
        space: Interpolation color space — ``"rgb"`` or ``"lab"``.

    Returns:
        List of RGB tuples from ``rgb1`` to ``rgb2``.
    """
    if steps < 2:
        return [rgb1]
    interp = _mix_lab if space == "lab" else mix
    return [interp(rgb1, rgb2, i / (steps - 1)) for i in range(steps)]
