"""Palette generation algorithms based on color-wheel hue relationships.

All functions accept an RGB tuple and return a list of RGB tuples
representing the generated palette colors (not including the original).
"""

from __future__ import annotations

from colorbrew.converters import hsl_to_rgb, rgb_to_hsl


def complementary(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Return the complementary color (hue + 180 degrees).

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Single RGB tuple of the complementary color.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    return hsl_to_rgb((h + 180) % 360, s, lit)


def analogous(
    r: int, g: int, b: int, n: int = 3, step: int = 30
) -> list[tuple[int, int, int]]:
    """Return analogous colors spread evenly around the hue.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).
        n: Number of colors to generate.
        step: Degrees between each color.

    Returns:
        List of n RGB tuples.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    colors: list[tuple[int, int, int]] = []
    start = h - step * (n // 2)
    for i in range(n):
        new_h = (start + step * i) % 360
        colors.append(hsl_to_rgb(new_h, s, lit))
    return colors


def triadic(r: int, g: int, b: int) -> list[tuple[int, int, int]]:
    """Return two triadic colors (hue + 120 and + 240 degrees).

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        List of 2 RGB tuples.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    return [
        hsl_to_rgb((h + 120) % 360, s, lit),
        hsl_to_rgb((h + 240) % 360, s, lit),
    ]


def split_complementary(r: int, g: int, b: int) -> list[tuple[int, int, int]]:
    """Return two split-complementary colors (hue + 150 and + 210 degrees).

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        List of 2 RGB tuples.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    return [
        hsl_to_rgb((h + 150) % 360, s, lit),
        hsl_to_rgb((h + 210) % 360, s, lit),
    ]


def tetradic(r: int, g: int, b: int) -> list[tuple[int, int, int]]:
    """Return three tetradic colors (hue + 90, + 180, + 270 degrees).

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        List of 3 RGB tuples.
    """
    h, s, lit = rgb_to_hsl(r, g, b)
    return [
        hsl_to_rgb((h + 90) % 360, s, lit),
        hsl_to_rgb((h + 180) % 360, s, lit),
        hsl_to_rgb((h + 270) % 360, s, lit),
    ]
