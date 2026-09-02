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


class WcagReport(NamedTuple):
    """Summary of WCAG contrast compliance for a color pair."""

    ratio: float
    aa: bool
    aaa: bool
    aa_large: bool
    aaa_large: bool


class NameMatch(NamedTuple):
    """Result of a reverse color-name lookup."""

    name: str
    hex: str
    distance: float
    exact: bool


class ColorClass(NamedTuple):
    """Computed color classification."""

    family: str
    tone: str
    chroma: str
    lightness: float
    hue: float
