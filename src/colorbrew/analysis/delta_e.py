"""Color difference formulas — RGB/Lab conversion and perceptual distance.

Provides CIE L*a*b* color space conversion and multiple distance metrics:
Euclidean RGB, CIE76 (Euclidean in Lab), and CIEDE2000 (perceptual).

The RGB-to-Lab pipeline is: sRGB (0-255) -> linear RGB -> CIE XYZ (D65) -> L*a*b*.
"""

from __future__ import annotations

import math

from colorbrew.conversion.gamma import SRGB_TO_XYZ, linearize
from colorbrew.types import DistanceMethod

# D65 illuminant reference white (2-degree observer)
_XN = 0.95047
_YN = 1.00000
_ZN = 1.08883

# CIE constants
_EPSILON = 216 / 24389  # 0.008856...
_KAPPA = 24389 / 27  # 903.3...


def _lab_f(t: float) -> float:
    """CIE L*a*b* transfer function."""
    if t > _EPSILON:
        return t ** (1.0 / 3.0)
    return (_KAPPA * t + 16.0) / 116.0


def rgb_to_lab(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert sRGB (0-255) to CIE L*a*b* (D65, 2-degree observer).

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Tuple of (L*, a*, b*) where L* is 0-100 and a*, b* are unbounded.
    """
    # sRGB -> linear RGB (0-1)
    rl = linearize(r)
    gl = linearize(g)
    bl = linearize(b)

    # Linear RGB -> CIE XYZ (D65)
    x = SRGB_TO_XYZ[0][0] * rl + SRGB_TO_XYZ[0][1] * gl + SRGB_TO_XYZ[0][2] * bl
    y = SRGB_TO_XYZ[1][0] * rl + SRGB_TO_XYZ[1][1] * gl + SRGB_TO_XYZ[1][2] * bl
    z = SRGB_TO_XYZ[2][0] * rl + SRGB_TO_XYZ[2][1] * gl + SRGB_TO_XYZ[2][2] * bl

    # XYZ -> L*a*b*
    fx = _lab_f(x / _XN)
    fy = _lab_f(y / _YN)
    fz = _lab_f(z / _ZN)

    l_star = 116.0 * fy - 16.0
    a_star = 500.0 * (fx - fy)
    b_star = 200.0 * (fy - fz)

    return (l_star, a_star, b_star)


def euclidean_rgb(
    r1: int, g1: int, b1: int, r2: int, g2: int, b2: int
) -> float:
    """Euclidean distance between two colors in RGB space.

    Args:
        r1: Red channel of first color (0-255).
        g1: Green channel of first color (0-255).
        b1: Blue channel of first color (0-255).
        r2: Red channel of second color (0-255).
        g2: Green channel of second color (0-255).
        b2: Blue channel of second color (0-255).

    Returns:
        Distance as a non-negative float.
    """
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


def delta_e_76(
    lab1: tuple[float, float, float], lab2: tuple[float, float, float]
) -> float:
    """CIE76 color difference — Euclidean distance in L*a*b* space.

    Args:
        lab1: First color as (L*, a*, b*).
        lab2: Second color as (L*, a*, b*).

    Returns:
        Delta E value (non-negative float).
    """
    dl = lab1[0] - lab2[0]
    da = lab1[1] - lab2[1]
    db = lab1[2] - lab2[2]
    return math.sqrt(dl * dl + da * da + db * db)


def delta_e_2000(
    lab1: tuple[float, float, float], lab2: tuple[float, float, float]
) -> float:
    """CIEDE2000 color difference (ISO/CIE 11664-6:2014).

    Implements the full 7-parameter formula for perceptual color difference.
    Reference: Sharma, Wu, Dalal (2005) — "The CIEDE2000 Color-Difference
    Formula: Implementation Notes, Supplementary Test Data, and Mathematical
    Observations".

    Args:
        lab1: First color as (L*, a*, b*).
        lab2: Second color as (L*, a*, b*).

    Returns:
        Delta E 2000 value (non-negative float).
    """
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2

    # Step 1: Calculate C'ab and h'ab
    c1 = math.sqrt(a1 * a1 + b1 * b1)
    c2 = math.sqrt(a2 * a2 + b2 * b2)
    c_avg = (c1 + c2) / 2.0

    c_avg_7 = c_avg ** 7
    g = 0.5 * (1.0 - math.sqrt(c_avg_7 / (c_avg_7 + 25.0 ** 7)))

    a1p = a1 * (1.0 + g)
    a2p = a2 * (1.0 + g)

    c1p = math.sqrt(a1p * a1p + b1 * b1)
    c2p = math.sqrt(a2p * a2p + b2 * b2)

    h1p = math.degrees(math.atan2(b1, a1p)) % 360.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360.0

    # Step 2: Calculate delta L', delta C', delta H'
    dl = l2 - l1
    dc = c2p - c1p

    if c1p * c2p == 0.0:
        dh = 0.0
    elif abs(h2p - h1p) <= 180.0:
        dh = h2p - h1p
    elif h2p - h1p > 180.0:
        dh = h2p - h1p - 360.0
    else:
        dh = h2p - h1p + 360.0

    d_hp = 2.0 * math.sqrt(c1p * c2p) * math.sin(math.radians(dh / 2.0))

    # Step 3: Calculate CIEDE2000 weighting functions
    l_avg = (l1 + l2) / 2.0
    c_avgp = (c1p + c2p) / 2.0

    if c1p * c2p == 0.0:
        h_avgp = h1p + h2p
    elif abs(h1p - h2p) <= 180.0:
        h_avgp = (h1p + h2p) / 2.0
    elif h1p + h2p < 360.0:
        h_avgp = (h1p + h2p + 360.0) / 2.0
    else:
        h_avgp = (h1p + h2p - 360.0) / 2.0

    t = (
        1.0
        - 0.17 * math.cos(math.radians(h_avgp - 30.0))
        + 0.24 * math.cos(math.radians(2.0 * h_avgp))
        + 0.32 * math.cos(math.radians(3.0 * h_avgp + 6.0))
        - 0.20 * math.cos(math.radians(4.0 * h_avgp - 63.0))
    )

    sl = 1.0 + 0.015 * (l_avg - 50.0) ** 2 / math.sqrt(20.0 + (l_avg - 50.0) ** 2)
    sc = 1.0 + 0.045 * c_avgp
    sh = 1.0 + 0.015 * c_avgp * t

    c_avgp_7 = c_avgp ** 7
    rc = 2.0 * math.sqrt(c_avgp_7 / (c_avgp_7 + 25.0 ** 7))
    d_theta = 30.0 * math.exp(-((h_avgp - 275.0) / 25.0) ** 2)
    rt = -math.sin(math.radians(2.0 * d_theta)) * rc

    return math.sqrt(
        (dl / sl) ** 2
        + (dc / sc) ** 2
        + (d_hp / sh) ** 2
        + rt * (dc / sc) * (d_hp / sh)
    )


def distance(
    r1: int, g1: int, b1: int,
    r2: int, g2: int, b2: int,
    method: DistanceMethod = "ciede2000",
) -> float:
    """Calculate the distance between two RGB colors.

    Args:
        r1: Red channel of first color (0-255).
        g1: Green channel of first color (0-255).
        b1: Blue channel of first color (0-255).
        r2: Red channel of second color (0-255).
        g2: Green channel of second color (0-255).
        b2: Blue channel of second color (0-255).
        method: Distance algorithm — ``"euclidean"`` (RGB space),
            ``"cie76"`` (L*a*b* Euclidean), or ``"ciede2000"`` (perceptual).

    Returns:
        Distance as a non-negative float.

    Raises:
        ValueError: If the method is not recognized.
    """
    if method == "euclidean":
        return euclidean_rgb(r1, g1, b1, r2, g2, b2)
    if method == "cie76":
        lab1 = rgb_to_lab(r1, g1, b1)
        lab2 = rgb_to_lab(r2, g2, b2)
        return delta_e_76(lab1, lab2)
    if method == "ciede2000":
        lab1 = rgb_to_lab(r1, g1, b1)
        lab2 = rgb_to_lab(r2, g2, b2)
        return delta_e_2000(lab1, lab2)
    raise ValueError(
        f"Unknown distance method {method!r}. "
        "Supported: 'euclidean', 'cie76', 'ciede2000'"
    )
