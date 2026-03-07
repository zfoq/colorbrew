"""WCAG 2.1 accessibility calculations for luminance and contrast ratio.

Implements the relative luminance and contrast ratio formulas from
the W3C Web Content Accessibility Guidelines (WCAG) 2.1.
"""

from __future__ import annotations

from typing import Literal

from colorbrew.conversion.converters import hsl_to_rgb, rgb_to_hsl
from colorbrew.conversion.gamma import linearize as _linearize


def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate WCAG relative luminance of an RGB color.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Luminance as a float between 0.0 (black) and 1.0 (white).
    """
    return (
        0.2126 * _linearize(r)
        + 0.7152 * _linearize(g)
        + 0.0722 * _linearize(b)
    )


def is_light(r: int, g: int, b: int) -> bool:
    """Check if a color is perceptually light.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        True if the WCAG relative luminance exceeds 0.5.
    """
    return relative_luminance(r, g, b) > 0.5


def is_dark(r: int, g: int, b: int) -> bool:
    """Check if a color is perceptually dark.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        True if the WCAG relative luminance is 0.5 or below.
    """
    return relative_luminance(r, g, b) <= 0.5


def contrast_ratio(
    rgb1: tuple[int, int, int], rgb2: tuple[int, int, int]
) -> float:
    """Calculate WCAG contrast ratio between two colors.

    Args:
        rgb1: First color as (r, g, b).
        rgb2: Second color as (r, g, b).

    Returns:
        Contrast ratio as a float between 1.0 and 21.0.
    """
    l1 = relative_luminance(*rgb1)
    l2 = relative_luminance(*rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def meets_aa(
    rgb1: tuple[int, int, int],
    rgb2: tuple[int, int, int],
    large: bool = False,
) -> bool:
    """Check if two colors meet WCAG AA contrast requirements.

    Args:
        rgb1: First color as (r, g, b).
        rgb2: Second color as (r, g, b).
        large: True for large text (threshold 3.0 instead of 4.5).

    Returns:
        True if the contrast ratio meets the AA threshold.
    """
    ratio = contrast_ratio(rgb1, rgb2)
    threshold = 3.0 if large else 4.5
    return ratio >= threshold


def meets_aaa(
    rgb1: tuple[int, int, int],
    rgb2: tuple[int, int, int],
    large: bool = False,
) -> bool:
    """Check if two colors meet WCAG AAA contrast requirements.

    Args:
        rgb1: First color as (r, g, b).
        rgb2: Second color as (r, g, b).
        large: True for large text (threshold 4.5 instead of 7.0).

    Returns:
        True if the contrast ratio meets the AAA threshold.
    """
    ratio = contrast_ratio(rgb1, rgb2)
    threshold = 4.5 if large else 7.0
    return ratio >= threshold


def suggest_text_color(
    r: int, g: int, b: int,
) -> tuple[int, int, int]:
    """Suggest black or white text for readability on a given background.

    Returns whichever of black ``(0, 0, 0)`` or white ``(255, 255, 255)``
    produces the higher WCAG contrast ratio against the background.

    Args:
        r: Red channel of the background (0-255).
        g: Green channel of the background (0-255).
        b: Blue channel of the background (0-255).

    Returns:
        ``(0, 0, 0)`` or ``(255, 255, 255)``.
    """
    lum = relative_luminance(r, g, b)
    # Contrast with white: (1.05) / (lum + 0.05)
    # Contrast with black: (lum + 0.05) / (0.05)
    # White wins when (1.05) / (lum + 0.05) > (lum + 0.05) / 0.05
    # Simplifies to: (lum + 0.05)^2 < 1.05 * 0.05
    if (lum + 0.05) ** 2 < 1.05 * 0.05:
        return (255, 255, 255)
    return (0, 0, 0)


def find_accessible_color(
    rgb: tuple[int, int, int],
    target: tuple[int, int, int],
    level: Literal["aa", "aaa"] = "aa",
    large: bool = False,
) -> tuple[int, int, int]:
    """Find the closest color to *target* that meets contrast requirements.

    Adjusts the lightness of *target* in HSL space (toward black or white)
    until the WCAG contrast threshold against *rgb* is met. If *target*
    already meets the requirement, it is returned unchanged.

    Uses binary search over the lightness range for efficiency.

    Args:
        rgb: The fixed background color as (r, g, b).
        target: The desired foreground color as (r, g, b).
        level: ``"aa"`` (4.5:1 / 3:1) or ``"aaa"`` (7:1 / 4.5:1).
        large: True for large text (lower thresholds).

    Returns:
        An accessible RGB tuple close to *target*.
    """
    if level == "aaa":
        threshold = 4.5 if large else 7.0
    else:
        threshold = 3.0 if large else 4.5

    if contrast_ratio(rgb, target) >= threshold:
        return target

    h, s, lit = rgb_to_hsl(*target)
    bg_lum = relative_luminance(*rgb)

    # Binary search: if background is dark, search lighter; otherwise darker
    if bg_lum <= 0.5:
        lo, hi = lit, 100
    else:
        lo, hi = 0, lit

    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = hsl_to_rgb(h, s, mid)
        if contrast_ratio(rgb, candidate) >= threshold:
            best = candidate
            # Try to stay closer to the original lightness
            if bg_lum <= 0.5:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if bg_lum <= 0.5:
                lo = mid + 1
            else:
                hi = mid - 1

    if best is not None:
        return best

    # Fallback: return black or white
    return suggest_text_color(*rgb)
