"""Core Color class — the main entry point for the ColorBrew library.

Stores a color internally as an RGB tuple of integers (0-255). All
transformation methods return new ``Color`` instances; nothing is mutated.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from typing import overload

from colorbrew import converters as _conv
from colorbrew import css_output as _css
from colorbrew.exceptions import ColorParseError, ColorValueError
from colorbrew.named_colors import NAMED_COLORS
from colorbrew.parsing import parse_rgb_args, parse_string


class Color:
    """An immutable color value with conversion, manipulation, and analysis.

    Stores the color internally as an RGB tuple of integers (0-255).
    All transformation methods return new ``Color`` instances.

    Args:
        *args: Either a single string (hex, CSS function, or named color)
            or three integers (r, g, b).

    Raises:
        ColorParseError: If a string argument cannot be parsed.
        ColorValueError: If integer arguments are outside 0-255.
    """

    __slots__ = ("_rgb",)

    @overload
    def __init__(self, value: str, /) -> None: ...

    @overload
    def __init__(self, r: int, g: int, b: int, /) -> None: ...

    def __init__(self, *args: str | int) -> None:
        """Create a Color from a string or three RGB integers."""
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                self._rgb = parse_string(arg)
            elif isinstance(arg, int):
                raise ColorValueError(
                    "Single integer is not a valid color. "
                    "Use Color(r, g, b) or Color('#hex')."
                )
            else:
                raise ColorParseError(
                    f"Unsupported argument type: {type(arg).__name__}"
                )
        elif len(args) == 3:
            r, g, b = args
            if not (isinstance(r, int) and isinstance(g, int) and isinstance(b, int)):
                raise ColorValueError("RGB values must be integers.")
            self._rgb = parse_rgb_args(r, g, b)  # type: ignore[arg-type]
        else:
            raise ColorParseError(
                f"Color() takes 1 or 3 arguments, got {len(args)}."
            )

    # --- Class methods / alternate constructors ---

    @classmethod
    def from_hsl(cls, h: int, s: int, lit: int) -> Color:
        """Create a Color from HSL values.

        Args:
            h: Hue in degrees (0-360).
            s: Saturation as percentage (0-100).
            lit: Lightness as percentage (0-100).

        Returns:
            A new Color instance.
        """
        rgb = _conv.hsl_to_rgb(h, s, lit)
        return cls(*rgb)

    @classmethod
    def from_cmyk(cls, c: int, m: int, y: int, k: int) -> Color:
        """Create a Color from CMYK values (0-100 each).

        Args:
            c: Cyan (0-100).
            m: Magenta (0-100).
            y: Yellow (0-100).
            k: Key/black (0-100).

        Returns:
            A new Color instance.
        """
        rgb = _conv.cmyk_to_rgb(c, m, y, k)
        return cls(*rgb)

    @classmethod
    def from_name(cls, name: str) -> Color:
        """Create a Color from a CSS named color string.

        Args:
            name: CSS color name (case-insensitive), e.g. ``"cornflowerblue"``.

        Returns:
            A new Color instance.

        Raises:
            ColorParseError: If the name is not a recognized CSS color.
        """
        lower = name.lower().strip()
        if lower not in NAMED_COLORS:
            raise ColorParseError(f"Unknown color name: {name!r}")
        return cls(NAMED_COLORS[lower])

    @classmethod
    def random(cls) -> Color:
        """Create a random Color using ``random.randint``.

        Returns:
            A new Color with random RGB values.
        """
        return cls(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    # --- Properties: channel access ---

    @property
    def r(self) -> int:
        """Red channel (0-255)."""
        return self._rgb[0]

    @property
    def g(self) -> int:
        """Green channel (0-255)."""
        return self._rgb[1]

    @property
    def b(self) -> int:
        """Blue channel (0-255)."""
        return self._rgb[2]

    @property
    def rgb(self) -> tuple[int, int, int]:
        """RGB tuple ``(r, g, b)``."""
        return self._rgb

    # --- Properties: format conversion ---

    @property
    def hex(self) -> str:
        """Lowercase 6-digit hex string with ``#`` prefix."""
        return _conv.rgb_to_hex(*self._rgb)

    @property
    def hsl(self) -> tuple[int, int, int]:
        """HSL tuple ``(hue 0-360, saturation 0-100, lightness 0-100)``."""
        return _conv.rgb_to_hsl(*self._rgb)

    @property
    def cmyk(self) -> tuple[int, int, int, int]:
        """CMYK tuple ``(c, m, y, k)`` with values 0-100."""
        return _conv.rgb_to_cmyk(*self._rgb)

    # --- Properties: CSS / HTML output ---

    @property
    def css_hex(self) -> str:
        """CSS hex color string (alias of ``hex``)."""
        return self.hex

    @property
    def css_rgb(self) -> str:
        """CSS ``rgb()`` function string."""
        return _css.to_css_rgb(*self._rgb)

    @property
    def css_hsl(self) -> str:
        """CSS ``hsl()`` function string."""
        return _css.to_css_hsl(*self._rgb)

    # --- Methods: CSS / HTML output ---

    def css_rgba(self, alpha: float = 1.0) -> str:
        """Return a CSS ``rgba()`` function string.

        Args:
            alpha: Alpha value (0.0-1.0).

        Returns:
            String like ``"rgba(52, 152, 219, 0.8)"``.
        """
        return _css.to_css_rgba(*self._rgb, alpha)

    def css_hsla(self, alpha: float = 1.0) -> str:
        """Return a CSS ``hsla()`` function string.

        Args:
            alpha: Alpha value (0.0-1.0).

        Returns:
            String like ``"hsla(204, 70%, 53%, 0.8)"``.
        """
        return _css.to_css_hsla(*self._rgb, alpha)

    # --- Dunder / magic methods ---

    def __repr__(self) -> str:
        """Return a string representation like ``Color('#3498db')``."""
        return f"Color('{self.hex}')"

    def __str__(self) -> str:
        """Return the hex string like ``#3498db``."""
        return self.hex

    def __eq__(self, other: object) -> bool:
        """Return True if the other Color has the same RGB values."""
        if not isinstance(other, Color):
            return NotImplemented
        return self._rgb == other._rgb

    def __hash__(self) -> int:
        """Return hash based on the RGB tuple."""
        return hash(self._rgb)

    def __iter__(self) -> Iterator[int]:
        """Yield r, g, b — enables ``r, g, b = color``."""
        return iter(self._rgb)

    def __format__(self, format_spec: str) -> str:
        """Support format specs: ``hex``, ``rgb``, ``hsl``.

        Args:
            format_spec: One of ``"hex"``, ``"rgb"``, ``"hsl"``, or ``""``
                (defaults to hex).

        Returns:
            Formatted color string.
        """
        if format_spec == "" or format_spec == "hex":
            return self.hex
        if format_spec == "rgb":
            return self.css_rgb
        if format_spec == "hsl":
            return self.css_hsl
        raise ValueError(
            f"Unknown format spec {format_spec!r}. Use 'hex', 'rgb', or 'hsl'."
        )
