"""Color temperature classification and Kelvin estimation.

Provides warm/cool/neutral classification based on hue angle and
correlated color temperature (CCT) estimation using McCamy's formula.
"""

from __future__ import annotations

from typing import Literal

from colorbrew.converters import rgb_to_hsl


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
    # Normalize to 0-1
    rn = r / 255.0
    gn = g / 255.0
    bn = b / 255.0

    # Linearize sRGB
    rn = _linearize(rn)
    gn = _linearize(gn)
    bn = _linearize(bn)

    # sRGB to CIE XYZ (D65 illuminant)
    x = 0.4124564 * rn + 0.3575761 * gn + 0.1804375 * bn
    y = 0.2126729 * rn + 0.7151522 * gn + 0.0721750 * bn
    z = 0.0193339 * rn + 0.1191920 * gn + 0.9503041 * bn

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


def _linearize(v: float) -> float:
    """Convert an sRGB gamma-encoded value to linear light."""
    if v <= 0.04045:
        return v / 12.92
    return ((v + 0.055) / 1.055) ** 2.4
