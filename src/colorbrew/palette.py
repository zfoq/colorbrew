"""Immutable ordered color palettes."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import overload

from colorbrew.exceptions import ColorParseError, ColorValueError, PaletteError
from colorbrew.types import ColorClass, ColorVisionDeficiency, DistanceMethod, NameMatch

ColorLike = object


class _Hexes(tuple):
    def __new__(cls, values: Iterable[str]):
        return super().__new__(cls, values)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, list):
            return list(self) == other
        return super().__eq__(other)


def _name(name: str | None) -> str | None:
    if name is None:
        return None
    normalized = name.strip().lower()
    if not normalized:
        raise PaletteError("Palette names must not be empty.")
    return normalized

def _metadata(source: "Palette", *, kind: str | None = None) -> dict[str, object]:
    return {
        "kind": source.kind if kind is None else kind,
        "system": source.system,
        "version": source.version,
        "source": source.source,
    }

class Palette:
    """An immutable ordered collection of colors."""

    __slots__ = ("_colors", "_names", "_kind", "_system", "_version", "_source", "_frozen")

    def __init__(
        self,
        colors: Iterable[ColorLike],
        *,
        names: Iterable[str | None] | None = None,
        kind: str = "custom",
        system: str | None = None,
        version: str | None = None,
        source: str = "custom",
    ) -> None:
        object.__setattr__(self, "_frozen", False)
        raw_colors = tuple(self._coerce_color(c) for c in colors)
        raw_names = tuple(_name(n) for n in names) if names is not None else (None,) * len(raw_colors)
        if len(raw_names) != len(raw_colors):
            raise PaletteError("Palette names must match color count.")
        by_color = dict(zip(raw_colors, raw_names, strict=True))
        coerced = tuple(by_color)
        if not coerced:
            raise PaletteError("Palette must contain at least one color.")
        normalized_names = tuple(by_color.values())
        named = [n for n in normalized_names if n is not None]
        if len(named) != len(set(named)):
            raise PaletteError("Palette names must be unique.")
        object.__setattr__(self, "_colors", coerced)
        object.__setattr__(self, "_names", normalized_names)
        object.__setattr__(self, "_kind", kind)
        object.__setattr__(self, "_system", system)
        object.__setattr__(self, "_version", version)
        object.__setattr__(self, "_source", source)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: object) -> None:
        if getattr(self, "_frozen", False):
            raise ColorValueError("Palette is immutable.")
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if getattr(self, "_frozen", False):
            raise ColorValueError("Palette is immutable.")
        object.__delattr__(self, name)

    @staticmethod
    def _coerce_color(value: ColorLike):
        from colorbrew.color import Color

        if isinstance(value, Color):
            return value
        if isinstance(value, str):
            return Color(value)
        if isinstance(value, tuple) and len(value) == 3 and all(isinstance(v, int) for v in value):
            return Color(*value)
        raise ColorParseError(f"Cannot coerce {value!r} to Color")

    @classmethod
    def from_hexes(cls, hexes: Iterable[str], **metadata: object) -> Palette:
        return cls(hexes, **metadata)

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, str], **metadata: object) -> Palette:
        return cls(mapping.values(), names=mapping.keys(), **metadata)

    @classmethod
    def from_system(cls, name: str, *, version: str | None = None) -> Palette:
        from colorbrew.data import get_palette

        return get_palette(name, version=version) if version is not None else get_palette(name)

    @property
    def colors(self):
        return self._colors

    @property
    def names(self) -> tuple[str | None, ...]:
        return self._names

    @property
    def hexes(self):
        return _Hexes(c.hex for c in self._colors)

    @property
    def kind(self) -> str:
        return self._kind

    @property
    def system(self) -> str | None:
        return self._system

    @property
    def version(self) -> str | None:
        return self._version

    @property
    def source(self) -> str:
        return self._source

    def _replace(self, colors: Iterable[ColorLike], *, names: Iterable[str | None] | None = None, kind: str | None = None) -> Palette:
        return Palette(
            colors,
            names=self._names if names is None else names,
            **_metadata(self, kind=kind),
        )

    @overload
    def __getitem__(self, key: int) -> object: ...

    @overload
    def __getitem__(self, key: slice) -> Palette: ...

    @overload
    def __getitem__(self, key: str) -> object: ...

    def __getitem__(self, key: int | slice | str):
        if isinstance(key, slice):
            return self._replace(self._colors[key], names=self._names[key])
        if isinstance(key, str):
            normalized = _name(key)
            for name, color in zip(self._names, self._colors, strict=True):
                if name == normalized:
                    return color.hex if self._kind == "system" else color
            raise KeyError(key)
        return self._colors[key]

    def __iter__(self) -> Iterator[object]:
        return iter(self._colors)

    def __len__(self) -> int:
        return len(self._colors)

    def __contains__(self, item: object) -> bool:
        from colorbrew.color import Color

        return _name(item) in self._names if isinstance(item, str) else isinstance(item, Color) and item in self._colors

    def nearest_names(self, system: str, method: DistanceMethod | None = None) -> dict[int, NameMatch]:
        from colorbrew.analysis.naming import find_closest_in_palette
        from colorbrew.data import get_palette

        mapping = get_palette(system).as_dict()
        return {i: find_closest_in_palette(*c.rgb, mapping, method or "ciede2000") for i, c in enumerate(self._colors)}

    def as_dict(self) -> dict[str, str]:
        return {n: c.hex for n, c in zip(self._names, self._colors, strict=True) if n is not None}

    def items(self):
        return tuple((n, c) for n, c in zip(self._names, self._colors, strict=True) if n is not None)

    def keys(self):
        return self.as_dict().keys()

    def values(self):
        return self.as_dict().values()

    def get(self, name: str, default: str | None = None) -> str | None:
        return self.as_dict().get(_name(name), default)

    def _other(self, other: object) -> Palette:
        return other if isinstance(other, Palette) else Palette(other)  # type: ignore[arg-type]

    def __or__(self, other: object) -> Palette:
        other_palette = self._other(other)
        colors = list(self._colors)
        names = list(self._names)
        for color, name in zip(other_palette.colors, other_palette.names, strict=True):
            if color not in colors:
                colors.append(color)
                names.append(name)
        return Palette(colors, names=names, kind=self._kind, system=self._system, version=self._version, source=self._source)

    def __and__(self, other: object) -> Palette:
        other_palette = self._other(other)
        pairs = [(c, n) for c, n in zip(self._colors, self._names, strict=True) if c in other_palette.colors]
        return Palette((c for c, _ in pairs), names=(n for _, n in pairs), kind=self._kind, system=self._system, version=self._version, source=self._source)

    def __sub__(self, other: object) -> Palette:
        other_palette = self._other(other)
        pairs = [(c, n) for c, n in zip(self._colors, self._names, strict=True) if c not in other_palette.colors]
        return Palette((c for c, _ in pairs), names=(n for _, n in pairs), kind=self._kind, system=self._system, version=self._version, source=self._source)

    def map(self, fn: Callable[[object], object], *, kind: str | None = None) -> Palette:
        return self._replace((fn(c) for c in self._colors), kind=kind)

    def with_alpha(self, alpha: float) -> Palette: return self.map(lambda c: c.with_alpha(alpha))
    def lighten(self, amount: int = 10) -> Palette: return self.map(lambda c: c.lighten(amount))
    def darken(self, amount: int = 10) -> Palette: return self.map(lambda c: c.darken(amount))
    def saturate(self, amount: int = 10) -> Palette: return self.map(lambda c: c.saturate(amount))
    def desaturate(self, amount: int = 10) -> Palette: return self.map(lambda c: c.desaturate(amount))
    def rotate(self, degrees: int) -> Palette: return self.map(lambda c: c.rotate(degrees))
    def invert(self) -> Palette: return self.map(lambda c: c.invert())
    def grayscale(self) -> Palette: return self.map(lambda c: c.grayscale())
    def shade(self, amount: float = 0.5) -> Palette: return self.map(lambda c: c.shade(amount))
    def tint(self, amount: float = 0.5) -> Palette: return self.map(lambda c: c.tint(amount))
    def tone(self, amount: float = 0.5) -> Palette: return self.map(lambda c: c.tone(amount))
    def simulate_colorblind(self, deficiency: ColorVisionDeficiency) -> Palette: return self.map(lambda c: c.simulate_colorblind(deficiency))

    def _zip_binary(self, other: object) -> tuple[object, ...]:
        from colorbrew.color import Color

        if isinstance(other, Color):
            return (other,) * len(self)
        other_palette = self._other(other)
        if len(other_palette) != len(self):
            raise PaletteError("Palette lengths must match.")
        return other_palette.colors

    def mix(self, other: object, weight: float = 0.5, *, space: str = "rgb") -> Palette:
        if space != "rgb":
            raise PaletteError("Only rgb palette mixing is currently supported.")
        return self._replace(c.mix(o, weight) for c, o in zip(self._colors, self._zip_binary(other), strict=True))

    def blend(self, other: object, mode: str = "multiply") -> Palette:
        return self._replace(c.blend(o, mode) for c, o in zip(self._colors, self._zip_binary(other), strict=True))

    def resample(self, n: int, *, space: str = "rgb") -> Palette:
        if n < 2:
            raise PaletteError("Palette resampling requires at least two colors.")
        if len(self) == 1:
            return self._replace([self._colors[0]] * n, names=[None] * n)
        out = []
        last = len(self) - 1
        for i in range(n):
            pos = i * last / (n - 1)
            left = min(int(pos), last - 1)
            out.append(self._colors[left].mix(self._colors[left + 1], pos - left))
        return Palette(out, kind=self._kind, system=self._system, version=self._version, source=self._source)

    def gradient(self, other: object | None = None, steps: int = 5, space: str = "rgb") -> Palette:
        if other is None:
            return self.resample(steps, space=space)
        if len(self) != 1:
            raise PaletteError("Palette.gradient with another color requires one source color.")
        from colorbrew.color import Color

        target = other if isinstance(other, Color) else self._coerce_color(other)
        return Palette(self._colors[0].gradient(target, steps, space))

    def extend(self, n: int, *, space: str = "rgb") -> Palette:
        return self.resample(n, space=space)

    def complementary(self) -> Palette:
        return Palette(c.complementary() for c in self._colors)

    def analogous(self, n: int = 3, step: int = 30) -> Palette:
        return Palette(color for c in self._colors for color in c.analogous(n=n, step=step))

    def triadic(self) -> Palette:
        return Palette(color for c in self._colors for color in c.triadic())

    def split_complementary(self) -> Palette:
        return Palette(color for c in self._colors for color in c.split_complementary())

    def tetradic(self) -> Palette:
        return Palette(color for c in self._colors for color in c.tetradic())

    def scale(self) -> dict[int, Palette]:
        scales = [c.scale() for c in self._colors]
        return {step: Palette(s[step] for s in scales) for step in sorted(scales[0])}

    def distance_matrix(self, method: DistanceMethod | None = None) -> tuple[tuple[float, ...], ...]:
        m = method or "ciede2000"
        return tuple(tuple(a.distance(b, m) for b in self._colors) for a in self._colors)

    def contrast_matrix(self) -> tuple[tuple[float, ...], ...]:
        return tuple(tuple(a.contrast(b) for b in self._colors) for a in self._colors)

    def nearest(self, color: object, method: DistanceMethod | None = None):
        target = self._coerce_color(color)
        distances = [c.distance(target, method or "ciede2000") for c in self._colors]
        i = min(range(len(distances)), key=distances.__getitem__)
        return i, self._colors[i], distances[i]

    def sort(self, by: str = "hue") -> Palette:
        def key(pair: tuple[object, str | None]):
            color, name = pair
            h, s, l = color.hsl
            return {"hue": h, "lightness": l, "chroma": s, "luminance": color.luminance, "name": name or ""}[by]

        pairs = sorted(zip(self._colors, self._names, strict=True), key=key)
        return self._replace((c for c, _ in pairs), names=(n for _, n in pairs))

    def dedupe(self, threshold: float = 0.0, method: DistanceMethod | None = None) -> Palette:
        colors = []
        names = []
        for color, name in zip(self._colors, self._names, strict=True):
            if not any(color.distance(c, method or "ciede2000") <= threshold for c in colors):
                colors.append(color)
                names.append(name)
        return self._replace(colors, names=names)

    def is_colorblind_safe(self, threshold: float = 10.0, deficiency: ColorVisionDeficiency = "deuteranopia") -> bool:
        simulated = self.simulate_colorblind(deficiency)
        matrix = simulated.distance_matrix()
        return all(matrix[i][j] >= threshold for i in range(len(simulated)) for j in range(i + 1, len(simulated)))

    def classify(self) -> tuple[ColorClass, ...]:
        classes = []
        buckets = ("red", "orange", "yellow", "chartreuse", "green", "spring", "cyan", "azure", "blue", "violet", "magenta", "rose")
        for color in self._colors:
            h, s, l = color.hsl
            family = "neutral" if s < 10 else buckets[round(h / 30) % 12]
            tone = "dark" if l < 25 else "muted-dark" if l < 45 else "mid" if l < 65 else "light" if l < 85 else "pale"
            chroma = "neutral" if s < 10 else "muted" if s < 50 else "vivid"
            classes.append(ColorClass(family, tone, chroma, float(l), float(h)))
        return tuple(classes)

    def to_system(self, system: str, method: DistanceMethod | None = None) -> Palette:
        matches = self.nearest_names(system, method)
        return Palette.from_mapping({m.name: m.hex for m in matches.values()}, kind=self._kind, system=system, source="nearest")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Palette) and (self._colors, self._names, self._kind, self._system, self._version, self._source) == (other._colors, other._names, other._kind, other._system, other._version, other._source)

    def __hash__(self) -> int:
        return hash((self._colors, self._names, self._kind, self._system, self._version, self._source))

    def __repr__(self) -> str:
        return f"Palette({self.hexes!r})"

class Theme(Palette):
    """A role-keyed Palette."""

    def __init__(
        self,
        colors: Mapping[str, ColorLike],
        *,
        kind: str = "theme",
        system: str | None = None,
        version: str | None = None,
        source: str = "custom",
    ) -> None:
        if not colors:
            raise PaletteError("Theme must contain at least one role.")
        roles = tuple(_name(role) for role in colors)
        if len(set(roles)) != len(roles):
            raise PaletteError("Theme roles must be unique.")
        super().__init__(colors.values(), names=roles, kind=kind, system=system, version=version, source=source)

    @property
    def roles(self) -> tuple[str, ...]:
        return self._names  # type: ignore[return-value]

    def __getattr__(self, name: str) -> object:
        if name.startswith("_") or not name.isidentifier():
            raise AttributeError(name)
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def _replace(self, colors: Iterable[ColorLike], *, names: Iterable[str | None] | None = None, kind: str | None = None) -> Theme:
        roles = self.roles if names is None else tuple(_name(n) for n in names)
        return Theme(dict(zip(roles, colors, strict=True)), **_metadata(self, kind=kind or "theme"))

    def with_role(self, role: str, color: ColorLike) -> Theme:
        normalized = _name(role)
        values = dict(zip(self.roles, self._colors, strict=True))
        values[normalized] = self._coerce_color(color)
        return Theme(values, **_metadata(self, kind="theme"))

    def without_role(self, role: str) -> Theme:
        normalized = _name(role)
        values = dict(zip(self.roles, self._colors, strict=True))
        if normalized not in values:
            raise KeyError(role)
        if len(values) == 1:
            raise PaletteError("Theme must contain at least one role.")
        del values[normalized]
        return Theme(values, **_metadata(self, kind="theme"))

    @classmethod
    def from_color(cls, seed: ColorLike, *, scheme: str = "triadic", roles: Iterable[str] | None = None) -> Palette:
        color = cls._coerce_color(seed)
        generated = {
            "complementary": lambda: (color, color.complementary()),
            "analogous": lambda: tuple(color.analogous()),
            "triadic": lambda: (color, *color.triadic()),
            "split_complementary": lambda: (color, *color.split_complementary()),
            "tetradic": lambda: (color, *color.tetradic()),
        }
        if scheme == "scale":
            scale = color.scale()
            default_roles = tuple(str(step) for step in scale)
            colors = tuple(scale.values())
            if roles is None:
                return Palette(colors, names=default_roles, kind="scale")
        elif scheme in generated:
            colors = generated[scheme]()
            default_roles = ("primary", "secondary", "accent", "accent2")[: len(colors)]
        else:
            raise PaletteError(f"Unknown theme scheme: {scheme}")
        normalized_roles = tuple(_name(r) for r in (roles or default_roles))
        if len(normalized_roles) != len(colors):
            raise PaletteError("Theme roles must match generated color count.")
        return cls(dict(zip(normalized_roles, colors, strict=True)))

    def contrast_report(self):
        return {
            (left_role, right_role): left_color.wcag_report(right_color)
            for i, (left_role, left_color) in enumerate(zip(self.roles, self._colors, strict=True))
            for right_role, right_color in tuple(zip(self.roles, self._colors, strict=True))[i + 1 :]
        }

    def to_css_vars(self, prefix: str = "--cb") -> str:
        return "\n".join(f"{prefix}-{role}: {color.hex};" for role, color in zip(self.roles, self._colors, strict=True))
