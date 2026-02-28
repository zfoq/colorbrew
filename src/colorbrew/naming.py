"""Reverse name lookup: find the closest CSS named color to an RGB value.

Uses Euclidean distance in RGB space to find the best match among all
148 CSS named colors.
"""

from __future__ import annotations

import math

from colorbrew.converters import hex_to_rgb
from colorbrew.named_colors import NAMED_COLORS
from colorbrew.types import NameMatch


def find_closest_name(r: int, g: int, b: int) -> NameMatch:
    """Find the CSS named color closest to the given RGB value.

    Iterates all CSS named colors and returns the one with the
    smallest Euclidean distance in RGB space.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        A NameMatch with the closest color name, its hex value,
        the distance, and whether it was an exact match.
    """
    best_name = ""
    best_hex = ""
    best_dist = float("inf")

    for name, hex_val in NAMED_COLORS.items():
        nr, ng, nb = hex_to_rgb(hex_val)
        dist = math.sqrt((r - nr) ** 2 + (g - ng) ** 2 + (b - nb) ** 2)
        if dist < best_dist:
            best_dist = dist
            best_name = name
            best_hex = hex_val
            if dist == 0.0:
                break

    return NameMatch(
        name=best_name,
        hex=best_hex,
        distance=round(best_dist, 4),
        exact=best_dist == 0.0,
    )
