"""Color temperature classification and Kelvin estimation.

Provides warm/cool/neutral classification based on hue angle and
correlated color temperature (CCT) estimation using McCamy's formula.
"""

from __future__ import annotations

from typing import Literal

from colorbrew.conversion.converters import rgb_to_hsl
from colorbrew.conversion.gamma import SRGB_TO_XYZ, linearize


def classify_temperature(r: int, g: int, b: int) -> Literal["warm", "cool", "neutral"]:
    """Classify a color as warm, cool, or neutral based on hue angle.

    Warm: hue 0-60 or 300-360 (reds, oranges, yellows, magentas).
    Cool: hue 60-300 (greens, cyans, blues, purples).
    Neutral: saturation < 10 (grays).

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        One of ``"warm"``, ``"cool"``, or ``"neutral"``.
    """
    h, s, _ = rgb_to_hsl(r, g, b)

    if s < 10:
        return "neutral"

    if h <= 60 or h >= 300:
        return "warm"

    return "cool"


def estimate_kelvin(r: int, g: int, b: int) -> int:
    """Estimate the correlated color temperature in Kelvin.

    Converts sRGB to CIE XYZ, then to CIE xy chromaticity, and applies
    McCamy's approximation formula for correlated color temperature.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Estimated color temperature in Kelvin (typically 1000-40000).
    """
    # sRGB -> linear RGB
    rn = linearize(r)
    gn = linearize(g)
    bn = linearize(b)

    # Linear RGB -> CIE XYZ (D65 illuminant)
    x = SRGB_TO_XYZ[0][0] * rn + SRGB_TO_XYZ[0][1] * gn + SRGB_TO_XYZ[0][2] * bn
    y = SRGB_TO_XYZ[1][0] * rn + SRGB_TO_XYZ[1][1] * gn + SRGB_TO_XYZ[1][2] * bn
    z = SRGB_TO_XYZ[2][0] * rn + SRGB_TO_XYZ[2][1] * gn + SRGB_TO_XYZ[2][2] * bn

    # CIE xy chromaticity
    total = x + y + z
    if total == 0:
        return 1000  # Black — return minimum

    cx = x / total
    cy = y / total

    # McCamy's formula
    n = (cx - 0.3320) / (0.1858 - cy)
    cct = 449.0 * n**3 + 3525.0 * n**2 + 6823.3 * n + 5520.33

    # Clamp to reasonable range
    return max(1000, min(40000, round(cct)))


