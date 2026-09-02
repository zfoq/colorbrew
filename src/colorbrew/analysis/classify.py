"""Perceptual color classification using OKLCH.

Maps a color to a family, tone, and chroma bucket based on its OKLCH
coordinates.  Low-chroma colors are reported as ``neutral`` so that grays
and near-grays are not assigned an arbitrary hue family.
"""

from __future__ import annotations

from colorbrew.conversion.oklab import rgb_to_oklch
from colorbrew.types import ColorClass

# Hue boundaries are chosen against the OKLCH color wheel so that the
# canonical sRGB primaries and secondaries fall in the expected families.
_HUE_FAMILIES: tuple[tuple[float, float, str], ...] = (
    (340.0, 360.0, "red"),
    (0.0, 35.0, "red"),
    (35.0, 90.0, "orange"),
    (90.0, 125.0, "yellow"),
    (125.0, 170.0, "green"),
    (170.0, 220.0, "cyan"),
    (220.0, 280.0, "blue"),
    (280.0, 320.0, "purple"),
    (320.0, 340.0, "magenta"),
)

# OKLCH lightness ranges used for tone labels.
_LIGHTNESS_TONES: tuple[tuple[float, str], ...] = (
    (0.30, "dark"),
    (0.75, "medium"),
    (1.00, "light"),
)

# OKLCH chroma ranges used for chroma buckets.
_CHROMA_BUCKETS: tuple[tuple[float, str], ...] = (
    (0.05, "low"),
    (0.20, "medium"),
    (float("inf"), "high"),
)

_NEUTRAL_CHROMA_THRESHOLD = 0.05


def _pick_family(hue: float, chroma: float) -> str:
    """Return the hue family for a color, or ``neutral`` when chroma is very low."""
    if chroma < _NEUTRAL_CHROMA_THRESHOLD:
        return "neutral"

    for lower, upper, name in _HUE_FAMILIES:
        if lower <= hue < upper:
            return name

    # Should never happen because the intervals cover 0-360, but keep a fallback.
    return "neutral"


def _pick_tone(lightness: float) -> str:
    """Return the tone bucket for a lightness value."""
    for threshold, tone in _LIGHTNESS_TONES:
        if lightness < threshold:
            return tone
    return "light"


def _pick_chroma_bucket(chroma: float) -> str:
    """Return the chroma bucket for a chroma value."""
    for threshold, bucket in _CHROMA_BUCKETS:
        if chroma < threshold:
            return bucket
    return "high"


def classify_color(r: int, g: int, b: int) -> ColorClass:
    """Classify an sRGB color into perceptual OKLCH buckets.

    The returned ``ColorClass`` contains:

    - ``family``: one of ``red``, ``orange``, ``yellow``, ``green``,
      ``cyan``, ``blue``, ``purple``, ``magenta``, or ``neutral`` for
      very low-chroma colors.
    - ``tone``: ``dark``, ``medium``, or ``light`` based on OKLCH lightness.
    - ``chroma``: ``low``, ``medium``, or ``high`` based on OKLCH chroma.
    - ``lightness``: the OKLCH ``L`` value (0-1).
    - ``hue``: the OKLCH ``h`` value in degrees (0-360).

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        A ``ColorClass`` describing the color's perceptual buckets.
    """
    lightness, chroma, hue = rgb_to_oklch(r, g, b)

    return ColorClass(
        family=_pick_family(hue, chroma),
        tone=_pick_tone(lightness),
        chroma=_pick_chroma_bucket(chroma),
        lightness=lightness,
        hue=hue,
    )


__all__ = ["classify_color"]
