"""Runtime registry for built-in and custom color systems."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from colorbrew.data.loader import load_colorbrewer_colors
from colorbrew.data.material_colors import MATERIAL_COLORS
from colorbrew.data.named_colors import NAMED_COLORS
from colorbrew.data.tailwind_colors import TAILWIND_COLORS
from colorbrew.exceptions import ColorValueError


@dataclass(frozen=True)
class SystemRecord:
    """Registered color system metadata and palettes."""

    name: str
    version: str | None
    entries: Callable[[], Mapping[str, str]] = field(
        default_factory=lambda: lambda: MappingProxyType({})
    )
    palettes: Callable[[], Mapping[str, object]] = field(
        default_factory=lambda: lambda: MappingProxyType({})
    )
    source: str = "custom"


_SYSTEMS: dict[str, SystemRecord] = {}


def _normalize_name(name: str) -> str:
    normalized = name.strip().lower()
    if not normalized:
        raise ColorValueError("System names must not be empty.")
    return normalized


def _normalize_version(version: str) -> str:
    normalized = version.strip().lower()
    if not normalized:
        raise ColorValueError("System versions must not be empty.")
    return normalized


def _normalize_palette_key(key: str) -> str:
    return key.strip().lower().replace("/", "-")


def _freeze_entries(
    entries: Mapping[str, str] | Callable[[], Mapping[str, str]],
) -> Callable[[], Mapping[str, str]]:
    if callable(entries):

        def _wrapped() -> Mapping[str, str]:
            return MappingProxyType(dict(entries()))

        return _wrapped
    frozen = MappingProxyType(dict(entries))
    return lambda: frozen


def _freeze_palettes(
    palettes: Mapping[str, object] | Callable[[], Mapping[str, object]],
) -> Callable[[], Mapping[str, object]]:
    if callable(palettes):

        def _wrapped() -> Mapping[str, object]:
            return MappingProxyType(
                {_normalize_palette_key(k): v for k, v in palettes().items()}
            )

        return _wrapped
    frozen = MappingProxyType(
        {_normalize_palette_key(k): v for k, v in palettes.items()}
    )
    return lambda: frozen


def register_system(
    name: str,
    *,
    version: str | None = None,
    entries: Mapping[str, str] | Callable[[], Mapping[str, str]] | None = None,
    palettes: Mapping[str, object] | Callable[[], Mapping[str, object]] | None = None,
    source: str = "custom",
) -> SystemRecord:
    """Register or replace a color system at runtime."""
    system_name = _normalize_name(name)
    record = SystemRecord(
        name=system_name,
        version=_normalize_version(version) if version is not None else None,
        entries=_freeze_entries(entries or {}),
        palettes=_freeze_palettes(palettes or {}),
        source=source.strip().lower(),
    )
    _SYSTEMS[system_name] = record
    return record


def list_systems() -> tuple[str, ...]:
    """Return registered systems in deterministic order."""
    return tuple(_SYSTEMS)


def get_system(name: str) -> SystemRecord:
    """Return a registered system record."""
    system_name = _normalize_name(name)
    try:
        return _SYSTEMS[system_name]
    except KeyError as exc:
        raise ColorValueError(f"Unknown color system: {name!r}") from exc


def resolve_name(name: str) -> tuple[str, str | None]:
    """Resolve ``system`` or ``system@version`` names."""
    system, _, version = name.partition("@")
    resolved = get_system(system).name
    return resolved, _normalize_version(version) if version else None


def list_palettes(system: str | None = None) -> tuple[str, ...]:
    """Return available palette names."""
    if system is not None:
        record = get_system(system)
        names = []
        for key in record.palettes():
            if key == record.version:
                names.append(record.name)
                names.append(f"{record.name}@{key}")
            else:
                names.append(f"{record.name}:{key}")
        return tuple(dict.fromkeys(names))
    return tuple(
        name for system_name in list_systems() for name in list_palettes(system_name)
    )


def get_palette(name: str):
    """Return a Palette from a registered system."""
    family, sep, key = name.partition(":")
    if sep:
        record = get_system(family)
        palettes = record.palettes()
        lookup_key = _normalize_palette_key(key)
        try:
            return palettes[lookup_key]
        except KeyError as exc:
            raise ColorValueError(f"Unknown palette: {name!r}") from exc

    system, _, version = family.partition("@")
    record = get_system(system)
    palettes = record.palettes()
    if version:
        lookup_key = _normalize_palette_key(version)
    elif record.version is not None:
        lookup_key = record.version
    else:
        raise ColorValueError(f"No default palette for system: {name!r}")
    try:
        return palettes[lookup_key]
    except KeyError as exc:
        raise ColorValueError(f"Unknown palette: {name!r}") from exc


def _css_palettes() -> dict[str, object]:
    from colorbrew.palette import Palette

    return {
        "v1": Palette.from_mapping(
            NAMED_COLORS,
            kind="system",
            system="css",
            version="v1",
            source="bundled",
        ),
    }


def _tailwind_palettes() -> dict[str, object]:
    from colorbrew.palette import Palette

    return {
        "v3": Palette.from_mapping(
            TAILWIND_COLORS,
            kind="system",
            system="tailwind",
            version="v3",
            source="bundled",
        ),
    }


def _material_palettes() -> dict[str, object]:
    from colorbrew.palette import Palette

    return {
        "v2": Palette.from_mapping(
            MATERIAL_COLORS,
            kind="system",
            system="material",
            version="v2",
            source="bundled",
        ),
    }


def _colorbrewer_palettes() -> dict[str, object]:
    from colorbrew.palette import Palette

    return {
        f"{scheme}-{size}": Palette.from_hexes(
            hexes,
            kind="system",
            system="colorbrewer",
            version=size,
            source="bundled",
        )
        for scheme, sizes in load_colorbrewer_colors().items()
        for size, hexes in sizes.items()
    }


register_system(
    "css",
    version="v1",
    entries=NAMED_COLORS,
    palettes=_css_palettes,
    source="bundled",
)
register_system(
    "tailwind",
    version="v3",
    entries=TAILWIND_COLORS,
    palettes=_tailwind_palettes,
    source="bundled",
)
register_system(
    "material",
    version="v2",
    entries=MATERIAL_COLORS,
    palettes=_material_palettes,
    source="bundled",
)
register_system(
    "colorbrewer",
    version=None,
    entries={},
    palettes=_colorbrewer_palettes,
    source="bundled",
)

__all__ = [
    "SystemRecord",
    "get_palette",
    "get_system",
    "list_palettes",
    "list_systems",
    "register_system",
    "resolve_name",
]
