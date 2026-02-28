"""WCAG 2.1 accessibility calculations for luminance and contrast ratio.

Implements the relative luminance and contrast ratio formulas from
the W3C Web Content Accessibility Guidelines (WCAG) 2.1.
"""

from __future__ import annotations


def _linearize(channel: int) -> float:
    """Convert an sRGB 0-255 channel to linear-light value."""
    v = channel / 255.0
    if v <= 0.04045:
        return v / 12.92
    return ((v + 0.055) / 1.055) ** 2.4


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
