"""OKLab and OKLCH conversion helpers."""

from __future__ import annotations

import math

from colorbrew.conversion.gamma import delinearize, linearize


def _check_rgb_channel(channel: int) -> None:
    if not isinstance(channel, int) or not 0 <= channel <= 255:
        msg = f"RGB channel must be an integer in 0-255, got {channel!r}"
        raise ValueError(msg)


def _check_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        msg = f"{name} must be finite, got {value!r}"
        raise ValueError(msg)


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def rgb_to_oklab(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert sRGB channels to OKLab ``(L, a, b)``."""
    for channel in (r, g, b):
        _check_rgb_channel(channel)

    lr, lg, lb = linearize(r), linearize(g), linearize(b)
    l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb

    l_, m_, s_ = math.cbrt(l), math.cbrt(m), math.cbrt(s)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(l: float, a: float, b: float) -> tuple[int, int, int]:
    """Convert OKLab ``(L, a, b)`` to clamped sRGB channels."""
    for name, value in (("l", l), ("a", a), ("b", b)):
        _check_finite(name, value)

    l_ = l + 0.3963377774 * a + 0.2158037573 * b
    m_ = l - 0.1055613458 * a - 0.0638541728 * b
    s_ = l - 0.0894841775 * a - 1.2914855480 * b
    l3, m3, s3 = l_**3, m_**3, s_**3

    r = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    bl = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3

    return (delinearize(_clamp_unit(r)), delinearize(_clamp_unit(g)), delinearize(_clamp_unit(bl)))


def oklab_to_oklch(l: float, a: float, b: float) -> tuple[float, float, float]:
    """Convert OKLab ``(L, a, b)`` to OKLCH ``(L, C, h)``."""
    for name, value in (("l", l), ("a", a), ("b", b)):
        _check_finite(name, value)
    chroma = math.hypot(a, b)
    hue = 0.0 if chroma == 0.0 else math.degrees(math.atan2(b, a)) % 360.0
    return (l, chroma, hue)


def oklch_to_oklab(l: float, c: float, h: float) -> tuple[float, float, float]:
    """Convert OKLCH ``(L, C, h)`` to OKLab ``(L, a, b)``."""
    for name, value in (("l", l), ("c", c), ("h", h)):
        _check_finite(name, value)
    if c < 0.0:
        msg = f"c must be non-negative, got {c!r}"
        raise ValueError(msg)
    radians = math.radians(h)
    return (l, c * math.cos(radians), c * math.sin(radians))


def rgb_to_oklch(r: int, g: int, b: int) -> tuple[float, float, float]:
    """Convert sRGB channels to OKLCH ``(L, C, h)``."""
    return oklab_to_oklch(*rgb_to_oklab(r, g, b))


def oklch_to_rgb(l: float, c: float, h: float) -> tuple[int, int, int]:
    """Convert OKLCH ``(L, C, h)`` to clamped sRGB channels."""
    return oklab_to_rgb(*oklch_to_oklab(l, c, h))
