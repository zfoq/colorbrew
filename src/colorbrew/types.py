"""Shared types and named tuples used across the library.

Defines lightweight data containers that multiple modules depend on.
"""

from __future__ import annotations

from typing import Literal, NamedTuple

DistanceMethod = Literal["euclidean", "cie76", "ciede2000"]
"""Distance algorithm for color comparison."""

BlendMode = Literal[
    "multiply", "screen", "overlay", "soft_light", "hard_light", "difference"
]
"""Photoshop-style blend mode name."""

ColorVisionDeficiency = Literal["protanopia", "deuteranopia", "tritanopia"]
"""Color vision deficiency type for simulation."""


class NameMatch(NamedTuple):
    """Result of a reverse color-name lookup.

    Args:
        name: CSS color name (e.g. ``"steelblue"``).
        hex: Hex value of the named color (e.g. ``"#4682b4"``).
        distance: Euclidean distance in RGB space (0.0 = exact match).
        exact: True when distance is 0.0.
    """

    name: str
    hex: str
    distance: float
    exact: bool
