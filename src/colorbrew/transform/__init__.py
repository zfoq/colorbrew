"""Color manipulation and generation — blend modes, palettes, adjustments."""

from __future__ import annotations

from colorbrew.transform.blending import blend
from colorbrew.transform.manipulation import (
    darken,
    desaturate,
    gradient,
    grayscale,
    invert,
    lighten,
    mix,
    rotate_hue,
    saturate,
    shade,
    tint,
    tone,
)
from colorbrew.transform.palettes import (
    analogous,
    complementary,
    split_complementary,
    tetradic,
    triadic,
)

__all__ = [
    "analogous",
    "blend",
    "complementary",
    "darken",
    "desaturate",
    "gradient",
    "grayscale",
    "invert",
    "lighten",
    "mix",
    "rotate_hue",
    "saturate",
    "shade",
    "split_complementary",
    "tetradic",
    "tint",
    "tone",
    "triadic",
]
