"""Color vision deficiency simulation.

Simulates how colors appear to people with protanopia (red-blind),
deuteranopia (green-blind), or tritanopia (blue-blind) using the
Viénot 1999 / Brettel 1997 matrix transformations.
"""

from __future__ import annotations

from colorbrew.conversion.gamma import delinearize, linearize
from colorbrew.types import ColorVisionDeficiency

# Pre-multiplied simulation matrices operating in linear RGB space.
# Protanopia and deuteranopia: Viénot et al. 1999
# Tritanopia: simplified single-plane Brettel approximation
_MATRICES: dict[str, list[list[float]]] = {
    "protanopia": [
        [0.170556992, 0.829443014, 0.0],
        [0.170556991, 0.829443008, 0.0],
        [-0.004517144, 0.004517144, 1.0],
    ],
    "deuteranopia": [
        [0.330660070, 0.669339930, 0.0],
        [0.330660070, 0.669339930, 0.0],
        [-0.027855380, 0.027855380, 1.0],
    ],
    "tritanopia": [
        [1.0, 0.127398900, -0.127398900],
        [0.0, 0.873909300, 0.126090700],
        [0.0, 0.873909300, 0.126090700],
    ],
}


def simulate(
    r: int, g: int, b: int, deficiency: ColorVisionDeficiency
) -> tuple[int, int, int]:
    """Simulate how a color appears with a color vision deficiency.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        deficiency: Type of color blindness — ``"protanopia"``,
            ``"deuteranopia"``, or ``"tritanopia"``.

    Returns:
        Simulated RGB tuple (0-255).

    Raises:
        ValueError: If the deficiency type is not recognized.
    """
    matrix = _MATRICES.get(deficiency)
    if matrix is None:
        raise ValueError(
            f"Unknown deficiency {deficiency!r}. "
            f"Supported: {', '.join(sorted(_MATRICES))}"
        )

    # sRGB → linear
    rl = linearize(r)
    gl = linearize(g)
    bl = linearize(b)

    # Apply simulation matrix
    r_sim = matrix[0][0] * rl + matrix[0][1] * gl + matrix[0][2] * bl
    g_sim = matrix[1][0] * rl + matrix[1][1] * gl + matrix[1][2] * bl
    b_sim = matrix[2][0] * rl + matrix[2][1] * gl + matrix[2][2] * bl

    # linear → sRGB
    return (delinearize(r_sim), delinearize(g_sim), delinearize(b_sim))
