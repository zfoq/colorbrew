"""Reverse name lookup: find the closest color name in any palette.

Supports multiple distance methods: Euclidean RGB (fast, default for
backward compatibility), CIE76 (Lab Euclidean), and CIEDE2000 (perceptual).

Palette RGB and Lab values are lazily cached on first use to avoid
repeated hex-to-RGB and RGB-to-Lab conversions.
"""

from __future__ import annotations

from colorbrew.analysis.delta_e import (
    delta_e_76,
    delta_e_2000,
    euclidean_rgb,
    rgb_to_lab,
)
from colorbrew.conversion.converters import hex_to_rgb
from colorbrew.data.material_colors import MATERIAL_COLORS
from colorbrew.data.named_colors import NAMED_COLORS
from colorbrew.data.tailwind_colors import TAILWIND_COLORS
from colorbrew.types import DistanceMethod, NameMatch

# Lazily built caches: palette id(dict) -> list of (name, hex, r, g, b)
_rgb_cache: dict[int, list[tuple[str, str, int, int, int]]] = {}
# palette id(dict) -> list of (name, hex, L*, a*, b*)
_lab_cache: dict[int, list[tuple[str, str, float, float, float]]] = {}


def _get_rgb_entries(
    palette: dict[str, str],
) -> list[tuple[str, str, int, int, int]]:
    """Return cached list of (name, hex, r, g, b) for a palette."""
    key = id(palette)
    if key not in _rgb_cache:
        entries = []
        for name, hex_val in palette.items():
            r, g, b = hex_to_rgb(hex_val)
            entries.append((name, hex_val, r, g, b))
        _rgb_cache[key] = entries
    return _rgb_cache[key]


def _get_lab_entries(
    palette: dict[str, str],
) -> list[tuple[str, str, float, float, float]]:
    """Return cached list of (name, hex, L*, a*, b*) for a palette."""
    key = id(palette)
    if key not in _lab_cache:
        entries = []
        for name, hex_val, r, g, b in _get_rgb_entries(palette):
            ls, a, b_val = rgb_to_lab(r, g, b)
            entries.append((name, hex_val, ls, a, b_val))
        _lab_cache[key] = entries
    return _lab_cache[key]


def _find_closest(
    r: int, g: int, b: int, palette: dict[str, str],
    method: DistanceMethod = "euclidean",
) -> NameMatch:
    """Find the palette color closest to the given RGB value.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        palette: Mapping of color names to hex strings.
        method: Distance algorithm — ``"euclidean"``, ``"cie76"``,
            or ``"ciede2000"``.

    Returns:
        A NameMatch with the closest color name, its hex value,
        the distance, and whether it was an exact match.
    """
    best_name = ""
    best_hex = ""
    best_dist = float("inf")

    if method == "euclidean":
        for name, hex_val, nr, ng, nb in _get_rgb_entries(palette):
            dist = euclidean_rgb(r, g, b, nr, ng, nb)
            if dist < best_dist:
                best_dist = dist
                best_name = name
                best_hex = hex_val
                if dist == 0.0:
                    break
    else:
        lab_input = rgb_to_lab(r, g, b)
        dist_fn = delta_e_2000 if method == "ciede2000" else delta_e_76
        for name, hex_val, ls, a, b_val in _get_lab_entries(palette):
            dist = dist_fn(lab_input, (ls, a, b_val))
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


def find_closest_name(
    r: int, g: int, b: int, method: DistanceMethod = "euclidean"
) -> NameMatch:
    """Find the CSS named color closest to the given RGB value.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        method: Distance algorithm — ``"euclidean"``, ``"cie76"``,
            or ``"ciede2000"``.

    Returns:
        A NameMatch with the closest CSS color name.
    """
    return _find_closest(r, g, b, NAMED_COLORS, method)


def find_closest_tailwind(
    r: int, g: int, b: int, method: DistanceMethod = "euclidean"
) -> NameMatch:
    """Find the Tailwind CSS color closest to the given RGB value.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        method: Distance algorithm — ``"euclidean"``, ``"cie76"``,
            or ``"ciede2000"``.

    Returns:
        A NameMatch with the closest Tailwind color name (e.g. ``"sky-500"``).
    """
    return _find_closest(r, g, b, TAILWIND_COLORS, method)


def find_closest_material(
    r: int, g: int, b: int, method: DistanceMethod = "euclidean"
) -> NameMatch:
    """Find the Material Design color closest to the given RGB value.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        method: Distance algorithm — ``"euclidean"``, ``"cie76"``,
            or ``"ciede2000"``.

    Returns:
        A NameMatch with the closest Material color name (e.g. ``"blue-600"``).
    """
    return _find_closest(r, g, b, MATERIAL_COLORS, method)
