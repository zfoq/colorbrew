"""Color vision deficiency simulation.

Simulates how colors appear to people with protanopia (red-blind),
deuteranopia (green-blind), or tritanopia (blue-blind) using the
Viénot 1999 / Brettel 1997 matrix transformations.
"""

from __future__ import annotations

from colorbrew.contrast import _linearize

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


def _delinearize(v: float) -> int:
    """Convert a linear-light float back to an sRGB 0-255 integer."""
    if v <= 0.0031308:
        out = v * 12.92
    else:
        out = 1.055 * (v ** (1.0 / 2.4)) - 0.055
    return round(max(0.0, min(1.0, out)) * 255)


def simulate(
    r: int, g: int, b: int, deficiency: str
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
    rl = _linearize(r)
    gl = _linearize(g)
    bl = _linearize(b)

    # Apply simulation matrix
    r_sim = matrix[0][0] * rl + matrix[0][1] * gl + matrix[0][2] * bl
    g_sim = matrix[1][0] * rl + matrix[1][1] * gl + matrix[1][2] * bl
    b_sim = matrix[2][0] * rl + matrix[2][1] * gl + matrix[2][2] * bl

    # linear → sRGB
    return (_delinearize(r_sim), _delinearize(g_sim), _delinearize(b_sim))
