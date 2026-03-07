"""sRGB gamma linearization/delinearization and shared color space constants.

Provides the canonical sRGB transfer functions and the D65 sRGB-to-XYZ
transformation matrix used across multiple modules.
"""

from __future__ import annotations


def linearize(channel: int) -> float:
    """Convert an sRGB 0-255 channel to a linear-light 0.0-1.0 value.

    Args:
        channel: sRGB channel value (0-255).

    Returns:
        Linear-light value between 0.0 and 1.0.
    """
    v = channel / 255.0
    if v <= 0.04045:
        return v / 12.92
    return ((v + 0.055) / 1.055) ** 2.4


def delinearize(v: float) -> int:
    """Convert a linear-light 0.0-1.0 value back to an sRGB 0-255 integer.

    Args:
        v: Linear-light value (0.0-1.0).

    Returns:
        sRGB channel value (0-255), clamped.
    """
    if v <= 0.0031308:
        out = v * 12.92
    else:
        out = 1.055 * (v ** (1.0 / 2.4)) - 0.055
    return round(max(0.0, min(1.0, out)) * 255)


# sRGB to CIE XYZ transformation matrix (D65 illuminant, 2-degree observer).
# Each row is (X, Y, Z) coefficients for (R_linear, G_linear, B_linear).
SRGB_TO_XYZ = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)

# Inverse: CIE XYZ to linear sRGB (D65 illuminant, 2-degree observer).
XYZ_TO_SRGB = (
    (3.2404542, -1.5371385, -0.4985314),
    (-0.9692660, 1.8760108, 0.0415560),
    (0.0556434, -0.2040259, 1.0572252),
)

# D65 illuminant reference white (2-degree observer).
D65_XN = 0.95047
D65_YN = 1.00000
D65_ZN = 1.08883

# CIE L*a*b* constants.
LAB_EPSILON = 216 / 24389  # 0.008856...
LAB_KAPPA = 24389 / 27  # 903.3...
