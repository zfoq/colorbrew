"""Photoshop-style blend modes operating per-channel on RGB values.

Each mode function accepts two RGB tuples (base and top layer) and returns
a new RGB tuple. Calculations are performed on normalized 0.0-1.0 values
to match the W3C compositing specification.
"""

from __future__ import annotations


def _norm(v: int) -> float:
    """Normalize an 0-255 integer to 0.0-1.0."""
    return v / 255.0


def _denorm(v: float) -> int:
    """Convert a 0.0-1.0 float back to a clamped 0-255 integer."""
    return round(max(0.0, min(1.0, v)) * 255)


def _apply(
    base: tuple[int, int, int],
    top: tuple[int, int, int],
    fn: object,
) -> tuple[int, int, int]:
    """Apply a per-channel blend function and return an RGB tuple."""
    # fn is typed loosely to keep the module simple; it's always a callable
    _fn = fn  # type: ignore[assignment]
    return (
        _denorm(_fn(_norm(base[0]), _norm(top[0]))),
        _denorm(_fn(_norm(base[1]), _norm(top[1]))),
        _denorm(_fn(_norm(base[2]), _norm(top[2]))),
    )


def _multiply(a: float, b: float) -> float:
    return a * b


def _screen(a: float, b: float) -> float:
    return 1.0 - (1.0 - a) * (1.0 - b)


def _overlay_ch(a: float, b: float) -> float:
    if a < 0.5:
        return 2.0 * a * b
    return 1.0 - 2.0 * (1.0 - a) * (1.0 - b)


def _soft_light_ch(a: float, b: float) -> float:
    """W3C compositing spec soft-light formula."""
    if b <= 0.5:
        return a - (1.0 - 2.0 * b) * a * (1.0 - a)
    if a <= 0.25:
        d = ((16.0 * a - 12.0) * a + 4.0) * a
    else:
        d = a ** 0.5
    return a + (2.0 * b - 1.0) * (d - a)


def _hard_light_ch(a: float, b: float) -> float:
    """Overlay with layers swapped."""
    return _overlay_ch(b, a)


def _difference_ch(a: float, b: float) -> float:
    return abs(a - b)


_MODES: dict[str, object] = {
    "multiply": _multiply,
    "screen": _screen,
    "overlay": _overlay_ch,
    "soft_light": _soft_light_ch,
    "hard_light": _hard_light_ch,
    "difference": _difference_ch,
}


def blend(
    base: tuple[int, int, int],
    top: tuple[int, int, int],
    mode: str = "multiply",
) -> tuple[int, int, int]:
    """Apply a Photoshop-style blend mode to two RGB colors.

    Args:
        base: Base layer RGB tuple.
        top: Top layer RGB tuple.
        mode: Blend mode name (``"multiply"``, ``"screen"``, ``"overlay"``,
            ``"soft_light"``, ``"hard_light"``, ``"difference"``).

    Returns:
        Blended RGB tuple.

    Raises:
        ValueError: If the mode name is not recognized.
    """
    fn = _MODES.get(mode)
    if fn is None:
        raise ValueError(
            f"Unknown blend mode {mode!r}. "
            f"Supported: {', '.join(sorted(_MODES))}"
        )
    return _apply(base, top, fn)
