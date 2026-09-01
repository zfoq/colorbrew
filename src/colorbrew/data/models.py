"""Palette models for bundled palettes and ordered sets of Colors."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING

from colorbrew.exceptions import ColorParseError, ColorValueError

if TYPE_CHECKING:
    from colorbrew.color import Color


class Palette:
    """A palette is either a named mapping of colors or an ordered set of Colors.

    *Mapping mode* is used by the bundled/upstream palette API: it stores
    ``family``, ``version``, ``source``, ``source_version``, and ``entries``
    metadata and behaves like a read-only mapping of color names to hex
    strings.

    *Color mode* stores an ordered, de-duplicated sequence of
    :class:`~colorbrew.color.Color` objects. It can be built from ``Color``
    instances, hex strings, CSS named colors, RGB tuples, or any value the
    :class:`~colorbrew.color.Color` constructor accepts.

    Both forms expose :attr:`colors`, :attr:`hexes`, and the palette
    generation methods that were previously only available on a single
    ``Color``.
    """

    @staticmethod
    def _normalize_key(name: str) -> str:
        return name.lower().strip()

    @staticmethod
    def _coerce_color(value: object) -> Color:
        from colorbrew.color import Color

        if isinstance(value, Color):
            return value
        if isinstance(value, str):
            return Color(value)
        if isinstance(value, (tuple, list)) and len(value) == 3:
            r, g, b = value
            if isinstance(r, int) and isinstance(g, int) and isinstance(b, int):
                return Color(r, g, b)
        raise ColorParseError(f"Cannot coerce {value!r} to Color")

    @classmethod
    def _parse_colors(cls, values: Iterable[object]) -> tuple[Color, ...]:
        colors = (cls._coerce_color(v) for v in values)
        return tuple(dict.fromkeys(colors))

    def __init__(
        self,
        *args: object,
        family: str = "custom",
        version: str = "custom",
        entries: dict[str, str] | None = None,
        source: str = "custom",
        source_version: str | None = None,
        colors: Iterable[object] | None = None,
    ) -> None:
        """Create a Palette from colors or from named entries.

        Examples:
            >>> Palette([Color("red"), "#00ff00", (0, 0, 255)])
            Palette(['#ff0000', '#00ff00', '#0000ff'])

            >>> Palette(family="tailwind", version="0.10.0",
            ...         entries={"sky-500": "#0ea5e9"})
        """
        self.family = family
        self.version = version
        self.source = source
        self.source_version = source_version
        self._color_mode = False

        if colors is not None:
            self._color_mode = True
            self._colors = self._parse_colors(colors)
            self.entries: dict[str, str] = {}
        elif entries is not None:
            self.entries = dict(entries)
            self._colors = self._parse_colors(self.entries.values())
        elif len(args) == 1 and isinstance(args[0], str):
            self.family = args[0]
            self.entries = {}
            self._colors = ()
        elif (
            len(args) == 1
            and isinstance(args[0], Iterable)
            and not isinstance(args[0], (str, bytes))
        ):
            self._color_mode = True
            self._colors = self._parse_colors(args[0])
            self.entries = {}
        elif len(args) >= 3 and isinstance(args[2], dict):
            self.family = str(args[0])
            self.version = str(args[1])
            self.entries = dict(args[2])
            if len(args) > 3:
                self.source = str(args[3])
            if len(args) > 4:
                self.source_version = str(args[4]) if args[4] is not None else None
            self._colors = self._parse_colors(self.entries.values())
        elif not args:
            self.entries = {}
            self._colors = ()
        else:
            raise ColorValueError("Invalid Palette constructor arguments")

    @property
    def colors(self) -> tuple[Color, ...]:
        """The ordered, de-duplicated ``Color`` members of this palette."""
        return self._colors

    @property
    def hexes(self) -> list[str]:
        """The hex strings for each color in this palette."""
        return [c.hex for c in self._colors]

    def __getitem__(self, key: str | int | slice):
        if isinstance(key, str):
            return self.entries[self._normalize_key(key)]
        if isinstance(key, int):
            return self._colors[key]
        if isinstance(key, slice):
            return Palette(self._colors[key])
        raise KeyError(key)

    def __iter__(self) -> Iterator[Color] | Iterator[str]:
        if self.entries:
            return iter(self.entries)
        return iter(self._colors)

    def __len__(self) -> int:
        if self.entries:
            return len(self.entries)
        return len(self._colors)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, str):
            return self._normalize_key(item) in self.entries
        from colorbrew.color import Color

        if isinstance(item, Color):
            return item in self._colors
        return False

    def __reversed__(self) -> Iterator[Color]:
        return reversed(self._colors)

    def __or__(self, other: object) -> Palette:
        if not isinstance(other, Palette):
            return NotImplemented
        combined = list(self._colors)
        for color in other._colors:
            if color not in combined:
                combined.append(color)
        return Palette(combined)

    def __ror__(self, other: object) -> Palette:
        if not isinstance(other, Palette):
            return NotImplemented
        return other.__or__(self)

    def __and__(self, other: object) -> Palette:
        if not isinstance(other, Palette):
            return NotImplemented
        return Palette([color for color in self._colors if color in other._colors])

    def __rand__(self, other: object) -> Palette:
        if not isinstance(other, Palette):
            return NotImplemented
        return other.__and__(self)

    def __sub__(self, other: object) -> Palette:
        if not isinstance(other, Palette):
            return NotImplemented
        return Palette([color for color in self._colors if color not in other._colors])

    def __rsub__(self, other: object) -> Palette:
        if not isinstance(other, Palette):
            return NotImplemented
        return other.__sub__(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Palette):
            return NotImplemented
        if self.entries or other.entries:
            return (
                self.family,
                self.version,
                self.source,
                self.source_version,
                self.entries,
            ) == (
                other.family,
                other.version,
                other.source,
                other.source_version,
                other.entries,
            )
        return self._colors == other._colors

    def __hash__(self) -> int:
        if self.entries:
            return hash(
                (
                    self.family,
                    self.version,
                    self.source,
                    self.source_version,
                    frozenset(self.entries.items()),
                )
            )
        return hash((self.family, self._colors))

    def __repr__(self) -> str:
        if self.entries:
            return (
                f"Palette(family={self.family!r}, version={self.version!r}, "
                f"entries={len(self.entries)})"
            )
        return f"Palette({self.hexes!r})"

    def get(self, name: str, default: str | None = None) -> str | None:
        """Return a named entry by name, with case-insensitive key lookup."""
        return self.entries.get(self._normalize_key(name), default)

    def as_dict(self) -> dict[str, str]:
        """Return a shallow copy of the entries as a plain dict."""
        return dict(self.entries)

    def keys(self):
        """Return the named entry keys (mapping-mode compatibility)."""
        return self.entries.keys()

    def values(self):
        """Return the named entry hex values (mapping-mode compatibility)."""
        return self.entries.values()

    def items(self):
        """Return the named entry key/value pairs (mapping-mode compatibility)."""
        return self.entries.items()

    def _ensure_colors(self) -> None:
        if not self._colors:
            raise ColorValueError("Palette must contain at least one color")

    def gradient(
        self,
        other: object | None = None,
        steps: int = 5,
        space: str = "rgb",
    ) -> Palette:
        """Generate a gradient palette.

        If ``other`` is provided, the gradient runs from the first color in
        this palette to ``other``. Otherwise the gradient is stitched between
        each consecutive pair of colors in this palette.
        """
        self._ensure_colors()
        if other is None:
            if len(self._colors) < 2:
                raise ColorValueError(
                    "Palette.gradient() between members requires at least two colors"
                )
            out: list[Color] = []
            for i in range(len(self._colors) - 1):
                segment = self._colors[i].gradient(
                    self._colors[i + 1], steps=steps, space=space
                )
                if i == 0:
                    out.extend(segment)
                else:
                    out.extend(segment[1:])
            return Palette(out)
        end = self._coerce_color(other)
        return Palette(self._colors[0].gradient(end, steps=steps, space=space))

    def complementary(self) -> Palette:
        """Return a palette of complementary colors for each member."""
        self._ensure_colors()
        return Palette([c.complementary() for c in self._colors])

    def analogous(self, n: int = 3, step: int = 30) -> Palette:
        """Return a palette of analogous colors for each member."""
        self._ensure_colors()
        return Palette(
            [color for c in self._colors for color in c.analogous(n=n, step=step)]
        )

    def triadic(self) -> Palette:
        """Return a palette of triadic colors for each member."""
        self._ensure_colors()
        return Palette([color for c in self._colors for color in c.triadic()])

    def split_complementary(self) -> Palette:
        """Return a palette of split-complementary colors for each member."""
        self._ensure_colors()
        return Palette(
            [color for c in self._colors for color in c.split_complementary()]
        )

    def tetradic(self) -> Palette:
        """Return a palette of tetradic colors for each member."""
        self._ensure_colors()
        return Palette([color for c in self._colors for color in c.tetradic()])

    def scale(self) -> dict[int, Palette]:
        """Return a Tailwind-like shade scale for each member.

        Returns a mapping from step number (50-950) to a ``Palette`` of the
        shades at that step across the members of this palette.
        """
        self._ensure_colors()
        scales = [c.scale() for c in self._colors]
        steps = sorted(scales[0].keys())
        return {step: Palette([s[step] for s in scales]) for step in steps}
