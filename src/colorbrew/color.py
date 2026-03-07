"""Core Color class — the main entry point for the ColorBrew library.

Stores a color internally as an RGB tuple of integers (0-255) and an
optional alpha channel (0.0-1.0, default 1.0). All transformation
methods return new ``Color`` instances; nothing is mutated.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from typing import Literal, overload

from colorbrew.analysis import colorblind as _cb
from colorbrew.analysis import contrast as _contrast
from colorbrew.analysis import delta_e as _delta_e
from colorbrew.analysis import naming as _naming
from colorbrew.analysis import temperature as _temp
from colorbrew.conversion import converters as _conv
from colorbrew.conversion import css_output as _css
from colorbrew.conversion.parsing import parse_rgb_args, parse_string_with_alpha
from colorbrew.data.material_colors import MATERIAL_COLORS
from colorbrew.data.named_colors import NAMED_COLORS
from colorbrew.data.tailwind_colors import TAILWIND_COLORS
from colorbrew.exceptions import ColorParseError, ColorValueError
from colorbrew.transform import blending as _blending
from colorbrew.transform import manipulation as _manip
from colorbrew.transform import palettes as _palettes
from colorbrew.types import BlendMode, ColorVisionDeficiency, DistanceMethod, NameMatch


def _new(rgb: tuple[int, int, int], alpha: float = 1.0) -> Color:
    """Internal fast-path constructor that skips validation."""
    c = object.__new__(Color)
    c._rgb = rgb
    c._alpha = alpha
    return c


class Color:
    """An immutable color value with conversion, manipulation, and analysis.

    Stores the color internally as an RGB tuple of integers (0-255) and
    an alpha channel (0.0-1.0). All transformation methods return new
    ``Color`` instances.

    Args:
        *args: Either a single string (hex, CSS function, or named color)
            or three integers (r, g, b).

    Raises:
        ColorParseError: If a string argument cannot be parsed.
        ColorValueError: If integer arguments are outside 0-255.
    """

    __slots__ = ("_alpha", "_rgb")

    @overload
    def __init__(self, value: str, /) -> None: ...

    @overload
    def __init__(self, r: int, g: int, b: int, /) -> None: ...

    def __init__(self, *args: str | int) -> None:
        """Create a Color from a string or three RGB integers."""
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                self._rgb, self._alpha = parse_string_with_alpha(arg)
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
            self._alpha = 1.0
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

        Raises:
            ColorValueError: If any value is out of range.
        """
        if not (0 <= h <= 360):
            raise ColorValueError(f"Hue must be 0-360, got {h}")
        if not (0 <= s <= 100):
            raise ColorValueError(f"Saturation must be 0-100, got {s}")
        if not (0 <= lit <= 100):
            raise ColorValueError(f"Lightness must be 0-100, got {lit}")
        return _new(_conv.hsl_to_rgb(h, s, lit))

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

        Raises:
            ColorValueError: If any value is out of range.
        """
        for name, val in (("Cyan", c), ("Magenta", m), ("Yellow", y), ("Key", k)):
            if not (0 <= val <= 100):
                raise ColorValueError(f"{name} must be 0-100, got {val}")
        return _new(_conv.cmyk_to_rgb(c, m, y, k))

    @classmethod
    def from_hsv(cls, h: int, s: int, v: int) -> Color:
        """Create a Color from HSV values.

        Args:
            h: Hue in degrees (0-360).
            s: Saturation as percentage (0-100).
            v: Value/brightness as percentage (0-100).

        Returns:
            A new Color instance.

        Raises:
            ColorValueError: If any value is out of range.
        """
        if not (0 <= h <= 360):
            raise ColorValueError(f"Hue must be 0-360, got {h}")
        if not (0 <= s <= 100):
            raise ColorValueError(f"Saturation must be 0-100, got {s}")
        if not (0 <= v <= 100):
            raise ColorValueError(f"Value must be 0-100, got {v}")
        return _new(_conv.hsv_to_rgb(h, s, v))

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
        return _new(_conv.hex_to_rgb(NAMED_COLORS[lower]))

    @classmethod
    def from_tailwind(cls, name: str) -> Color:
        """Create a Color from a Tailwind CSS color name.

        Args:
            name: Tailwind color name (case-insensitive), e.g. ``"sky-500"``.

        Returns:
            A new Color instance.

        Raises:
            ColorParseError: If the name is not a recognized Tailwind color.
        """
        lower = name.lower().strip()
        if lower not in TAILWIND_COLORS:
            raise ColorParseError(f"Unknown Tailwind color: {name!r}")
        return _new(_conv.hex_to_rgb(TAILWIND_COLORS[lower]))

    @classmethod
    def from_material(cls, name: str) -> Color:
        """Create a Color from a Material Design color name.

        Args:
            name: Material color name (case-insensitive), e.g. ``"blue-600"``.

        Returns:
            A new Color instance.

        Raises:
            ColorParseError: If the name is not a recognized Material color.
        """
        lower = name.lower().strip()
        if lower not in MATERIAL_COLORS:
            raise ColorParseError(f"Unknown Material Design color: {name!r}")
        return _new(_conv.hex_to_rgb(MATERIAL_COLORS[lower]))

    @classmethod
    def random(cls) -> Color:
        """Create a random Color using ``random.randint``.

        Returns:
            A new Color with random RGB values.
        """
        return _new((
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        ))

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
    def alpha(self) -> float:
        """Alpha channel (0.0-1.0, default 1.0)."""
        return self._alpha

    @property
    def rgb(self) -> tuple[int, int, int]:
        """RGB tuple ``(r, g, b)``."""
        return self._rgb

    @property
    def rgba(self) -> tuple[int, int, int, float]:
        """RGBA tuple ``(r, g, b, alpha)``."""
        return (*self._rgb, self._alpha)

    # --- Properties: format conversion ---

    @property
    def hex(self) -> str:
        """Lowercase 6-digit hex string with ``#`` prefix.

        If alpha < 1.0, returns an 8-digit hex string with alpha suffix.
        """
        h = _conv.rgb_to_hex(*self._rgb)
        if self._alpha < 1.0:
            return f"{h}{round(self._alpha * 255):02x}"
        return h

    @property
    def hsl(self) -> tuple[int, int, int]:
        """HSL tuple ``(hue 0-360, saturation 0-100, lightness 0-100)``."""
        return _conv.rgb_to_hsl(*self._rgb)

    @property
    def cmyk(self) -> tuple[int, int, int, int]:
        """CMYK tuple ``(c, m, y, k)`` with values 0-100."""
        return _conv.rgb_to_cmyk(*self._rgb)

    @property
    def hsv(self) -> tuple[int, int, int]:
        """HSV tuple ``(hue 0-360, saturation 0-100, value 0-100)``."""
        return _conv.rgb_to_hsv(*self._rgb)

    @property
    def lab(self) -> tuple[float, float, float]:
        """CIE L*a*b* tuple ``(L*, a*, b*)`` using D65 illuminant."""
        return _delta_e.rgb_to_lab(*self._rgb)

    # --- Properties: CSS / HTML output ---

    @property
    def css_hex(self) -> str:
        """CSS hex color string (alias of ``hex``)."""
        return self.hex

    @property
    def css_rgb(self) -> str:
        """CSS ``rgb()`` or ``rgba()`` function string.

        Automatically includes alpha when alpha < 1.0.
        """
        if self._alpha < 1.0:
            return _css.to_css_rgba(*self._rgb, self._alpha)
        return _css.to_css_rgb(*self._rgb)

    @property
    def css_hsl(self) -> str:
        """CSS ``hsl()`` or ``hsla()`` function string.

        Automatically includes alpha when alpha < 1.0.
        """
        if self._alpha < 1.0:
            return _css.to_css_hsla(*self._rgb, self._alpha)
        return _css.to_css_hsl(*self._rgb)

    # --- Methods: CSS / HTML output ---

    def css_rgba(self, alpha: float | None = None) -> str:
        """Return a CSS ``rgba()`` function string.

        Args:
            alpha: Override alpha (0.0-1.0). Defaults to the color's alpha.

        Returns:
            String like ``"rgba(52, 152, 219, 0.8)"``.
        """
        a = self._alpha if alpha is None else alpha
        return _css.to_css_rgba(*self._rgb, a)

    def css_hsla(self, alpha: float | None = None) -> str:
        """Return a CSS ``hsla()`` function string.

        Args:
            alpha: Override alpha (0.0-1.0). Defaults to the color's alpha.

        Returns:
            String like ``"hsla(204, 70%, 53%, 0.8)"``.
        """
        a = self._alpha if alpha is None else alpha
        return _css.to_css_hsla(*self._rgb, a)

    # --- Methods: alpha ---

    def with_alpha(self, alpha: float) -> Color:
        """Return a copy of this color with a different alpha value.

        Args:
            alpha: New alpha value (0.0-1.0).

        Returns:
            A new Color with the specified alpha.

        Raises:
            ColorValueError: If alpha is outside 0.0-1.0.
        """
        if not (0.0 <= alpha <= 1.0):
            raise ColorValueError(f"Alpha must be 0.0-1.0, got {alpha}")
        return _new(self._rgb, alpha)

    @property
    def opaque(self) -> Color:
        """Return a fully opaque copy (alpha = 1.0)."""
        if self._alpha == 1.0:
            return self
        return _new(self._rgb, 1.0)

    # --- Methods: name lookup ---

    def closest_name(self, method: DistanceMethod = "euclidean") -> NameMatch:
        """Find the closest CSS named color.

        Args:
            method: Distance algorithm — ``"euclidean"``, ``"cie76"``,
                or ``"ciede2000"``.

        Returns:
            A NameMatch with the closest CSS color name.
        """
        return _naming.find_closest_name(*self._rgb, method)

    def closest_tailwind(self, method: DistanceMethod = "euclidean") -> NameMatch:
        """Find the closest Tailwind CSS color.

        Args:
            method: Distance algorithm — ``"euclidean"``, ``"cie76"``,
                or ``"ciede2000"``.

        Returns:
            A NameMatch with the closest Tailwind color name.
        """
        return _naming.find_closest_tailwind(*self._rgb, method)

    def closest_material(self, method: DistanceMethod = "euclidean") -> NameMatch:
        """Find the closest Material Design color.

        Args:
            method: Distance algorithm — ``"euclidean"``, ``"cie76"``,
                or ``"ciede2000"``.

        Returns:
            A NameMatch with the closest Material Design color name.
        """
        return _naming.find_closest_material(*self._rgb, method)

    # --- Methods: color distance ---

    def distance(self, other: Color, method: DistanceMethod = "ciede2000") -> float:
        """Calculate the perceptual distance to another color.

        Args:
            other: The color to compare against.
            method: Distance algorithm — ``"euclidean"`` (RGB space),
                ``"cie76"`` (Lab Euclidean), or ``"ciede2000"`` (perceptual).

        Returns:
            Distance as a non-negative float.
        """
        return _delta_e.distance(*self._rgb, *other._rgb, method=method)

    # --- Methods: manipulation ---

    def lighten(self, amount: int = 10) -> Color:
        """Return a lighter version of this color.

        Args:
            amount: Percentage points to add to lightness (0-100).

        Returns:
            A new Color with increased lightness.
        """
        return _new(_manip.lighten(*self._rgb, amount), self._alpha)

    def darken(self, amount: int = 10) -> Color:
        """Return a darker version of this color.

        Args:
            amount: Percentage points to subtract from lightness (0-100).

        Returns:
            A new Color with decreased lightness.
        """
        return _new(_manip.darken(*self._rgb, amount), self._alpha)

    def saturate(self, amount: int = 10) -> Color:
        """Return a more saturated version of this color.

        Args:
            amount: Percentage points to add to saturation (0-100).

        Returns:
            A new Color with increased saturation.
        """
        return _new(_manip.saturate(*self._rgb, amount), self._alpha)

    def desaturate(self, amount: int = 10) -> Color:
        """Return a less saturated version of this color.

        Args:
            amount: Percentage points to subtract from saturation (0-100).

        Returns:
            A new Color with decreased saturation.
        """
        return _new(_manip.desaturate(*self._rgb, amount), self._alpha)

    def rotate(self, degrees: int) -> Color:
        """Return a color with shifted hue.

        Args:
            degrees: Degrees to rotate (wraps at 360).

        Returns:
            A new Color with the adjusted hue.
        """
        return _new(_manip.rotate_hue(*self._rgb, degrees), self._alpha)

    def invert(self) -> Color:
        """Return the inverted color (255 minus each channel)."""
        return _new(_manip.invert(*self._rgb), self._alpha)

    def grayscale(self) -> Color:
        """Return the grayscale version (saturation set to 0)."""
        return _new(_manip.grayscale(*self._rgb), self._alpha)

    def mix(self, other: Color, weight: float = 0.5) -> Color:
        """Blend this color with another using linear interpolation.

        Args:
            other: The color to mix with.
            weight: Blend weight toward ``other`` (0.0-1.0).

        Returns:
            A new blended Color.
        """
        w = max(0.0, min(1.0, weight))
        mixed_alpha = self._alpha + (other._alpha - self._alpha) * w
        return _new(_manip.mix(self._rgb, other._rgb, weight), mixed_alpha)

    def shade(self, amount: float = 0.5) -> Color:
        """Return a darker shade by mixing with black.

        Args:
            amount: Weight toward black (0.0 = original, 1.0 = black).

        Returns:
            A new darker Color.
        """
        return _new(_manip.shade(*self._rgb, amount), self._alpha)

    def tint(self, amount: float = 0.5) -> Color:
        """Return a lighter tint by mixing with white.

        Args:
            amount: Weight toward white (0.0 = original, 1.0 = white).

        Returns:
            A new lighter Color.
        """
        return _new(_manip.tint(*self._rgb, amount), self._alpha)

    def tone(self, amount: float = 0.5) -> Color:
        """Return a muted tone by mixing with gray.

        Args:
            amount: Weight toward gray (0.0 = original, 1.0 = gray).

        Returns:
            A new muted Color.
        """
        return _new(_manip.tone(*self._rgb, amount), self._alpha)

    def gradient(
        self,
        other: Color,
        steps: int = 5,
        space: Literal["rgb", "lab"] = "rgb",
    ) -> list[Color]:
        """Generate a gradient of colors to another color.

        Args:
            other: The end color.
            steps: Number of colors to generate (minimum 2).
            space: Interpolation color space — ``"rgb"`` or ``"lab"``.

        Returns:
            List of Color instances from this color to ``other``.
        """
        rgbs = _manip.gradient(self._rgb, other._rgb, steps, space)
        n = len(rgbs)
        if n <= 1:
            return [_new(rgb, self._alpha) for rgb in rgbs]
        return [
            _new(rgb, self._alpha + (other._alpha - self._alpha) * i / (n - 1))
            for i, rgb in enumerate(rgbs)
        ]

    # --- Methods: blending ---

    def blend(self, other: Color, mode: BlendMode = "multiply") -> Color:
        """Apply a Photoshop-style blend mode with another color.

        Args:
            other: The top-layer color.
            mode: Blend mode name (e.g. ``"multiply"``, ``"screen"``).

        Returns:
            A new blended Color.

        Raises:
            ValueError: If the mode name is not recognized.
        """
        return _new(_blending.blend(self._rgb, other._rgb, mode), self._alpha)

    # --- Methods: palette generation ---

    def complementary(self) -> Color:
        """Return the complementary color (hue + 180 degrees).

        Returns:
            A new Color with the opposite hue.
        """
        return _new(_palettes.complementary(*self._rgb), self._alpha)

    def analogous(self, n: int = 3, step: int = 30) -> list[Color]:
        """Return analogous colors spread evenly around the hue.

        Args:
            n: Number of colors to generate.
            step: Degrees between each color.

        Returns:
            List of n Color instances.
        """
        return [
            _new(rgb, self._alpha)
            for rgb in _palettes.analogous(*self._rgb, n, step)
        ]

    def triadic(self) -> list[Color]:
        """Return two triadic colors (hue + 120 and + 240 degrees).

        Returns:
            List of 2 Color instances.
        """
        return [_new(rgb, self._alpha) for rgb in _palettes.triadic(*self._rgb)]

    def split_complementary(self) -> list[Color]:
        """Return two split-complementary colors (hue + 150 and + 210).

        Returns:
            List of 2 Color instances.
        """
        return [
            _new(rgb, self._alpha)
            for rgb in _palettes.split_complementary(*self._rgb)
        ]

    def tetradic(self) -> list[Color]:
        """Return three tetradic colors (hue + 90, + 180, + 270).

        Returns:
            List of 3 Color instances.
        """
        return [_new(rgb, self._alpha) for rgb in _palettes.tetradic(*self._rgb)]

    def scale(self) -> dict[int, Color]:
        """Generate a Tailwind-like 50-950 shade scale from this color.

        Returns:
            Dict mapping step numbers (50-950) to Color instances.
        """
        return {
            step: _new(rgb, self._alpha)
            for step, rgb in _palettes.scale(*self._rgb).items()
        }

    # --- Methods: accessibility ---

    @property
    def luminance(self) -> float:
        """WCAG relative luminance (0.0 for black, 1.0 for white)."""
        return _contrast.relative_luminance(*self._rgb)

    @property
    def is_light(self) -> bool:
        """True if the color is perceptually light (luminance > 0.5)."""
        return _contrast.is_light(*self._rgb)

    @property
    def is_dark(self) -> bool:
        """True if the color is perceptually dark (luminance <= 0.5)."""
        return _contrast.is_dark(*self._rgb)

    def contrast(self, other: Color) -> float:
        """Calculate WCAG contrast ratio against another color.

        Args:
            other: The color to compare against.

        Returns:
            Contrast ratio between 1.0 and 21.0.
        """
        return _contrast.contrast_ratio(self._rgb, other._rgb)

    def meets_aa(self, other: Color, large: bool = False) -> bool:
        """Check if this color meets WCAG AA contrast with another.

        Args:
            other: The color to compare against.
            large: True for large text (threshold 3.0 instead of 4.5).

        Returns:
            True if the pair meets AA requirements.
        """
        return _contrast.meets_aa(self._rgb, other._rgb, large)

    def meets_aaa(self, other: Color, large: bool = False) -> bool:
        """Check if this color meets WCAG AAA contrast with another.

        Args:
            other: The color to compare against.
            large: True for large text (threshold 4.5 instead of 7.0).

        Returns:
            True if the pair meets AAA requirements.
        """
        return _contrast.meets_aaa(self._rgb, other._rgb, large)

    def suggest_text_color(self) -> Color:
        """Suggest black or white text for maximum readability on this color.

        Returns:
            ``Color(0, 0, 0)`` or ``Color(255, 255, 255)``.
        """
        return _new(_contrast.suggest_text_color(*self._rgb))

    def find_accessible_color(
        self,
        target: Color,
        level: str = "aa",
        large: bool = False,
    ) -> Color:
        """Find the closest color to *target* that meets contrast requirements.

        Adjusts the lightness of *target* toward black or white until the
        WCAG contrast threshold against this color is met.

        Args:
            target: The desired foreground color.
            level: ``"aa"`` or ``"aaa"``.
            large: True for large text (lower thresholds).

        Returns:
            An accessible Color close to *target*.
        """
        return _new(
            _contrast.find_accessible_color(self._rgb, target._rgb, level, large)
        )

    # --- Methods: color blindness simulation ---

    def simulate_colorblind(self, deficiency: ColorVisionDeficiency) -> Color:
        """Simulate how this color appears with a color vision deficiency.

        Args:
            deficiency: One of ``"protanopia"`` (red-blind),
                ``"deuteranopia"`` (green-blind), or
                ``"tritanopia"`` (blue-blind).

        Returns:
            A new Color representing the simulated perception.

        Raises:
            ValueError: If the deficiency type is not recognized.
        """
        return _new(_cb.simulate(*self._rgb, deficiency), self._alpha)

    # --- Methods: temperature ---

    @property
    def temperature(self) -> str:
        """Classify this color as ``"warm"``, ``"cool"``, or ``"neutral"``."""
        return _temp.classify_temperature(*self._rgb)

    @property
    def kelvin(self) -> int:
        """Estimated correlated color temperature in Kelvin (1000-40000)."""
        return _temp.estimate_kelvin(*self._rgb)

    # --- Dunder / magic methods ---

    def __repr__(self) -> str:
        """Return a string representation like ``Color('#3498db')``."""
        return f"Color('{self.hex}')"

    def __str__(self) -> str:
        """Return the hex string like ``#3498db``."""
        return self.hex

    def __eq__(self, other: object) -> bool:
        """Return True if the other Color has the same RGB and alpha values."""
        if not isinstance(other, Color):
            return NotImplemented
        return self._rgb == other._rgb and self._alpha == other._alpha

    def __hash__(self) -> int:
        """Return hash based on the RGB tuple and alpha."""
        return hash((self._rgb, self._alpha))

    def __iter__(self) -> Iterator[int]:
        """Yield r, g, b — enables ``r, g, b = color``."""
        return iter(self._rgb)

    def __format__(self, format_spec: str) -> str:
        """Support format specs: ``hex``, ``rgb``, ``hsl``, ``hsv``.

        Args:
            format_spec: One of ``"hex"``, ``"rgb"``, ``"hsl"``, ``"hsv"``,
                or ``""`` (defaults to hex).

        Returns:
            Formatted color string.
        """
        if format_spec == "" or format_spec == "hex":
            return self.hex
        if format_spec == "rgb":
            return self.css_rgb
        if format_spec == "hsl":
            return self.css_hsl
        if format_spec == "hsv":
            h, s, v = self.hsv
            return f"hsv({h}, {s}%, {v}%)"
        raise ValueError(
            f"Unknown format spec {format_spec!r}. "
            "Use 'hex', 'rgb', 'hsl', or 'hsv'."
        )
