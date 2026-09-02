"""Runtime registry for built-in and custom color systems."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from colorbrew.data.loader import (
    MATERIAL_COLORS,
    NAMED_COLORS,
    TAILWIND_COLORS,
    ColorBrewerColors,
    load_colorbrewer_colors,
)
from colorbrew.exceptions import ColorValueError


@dataclass(frozen=True)
class SystemRecord:
    """Registered color system metadata and palettes."""

    name: str
    default_version: str
    palettes: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
    colorbrewer_palettes: ColorBrewerColors = field(default_factory=dict)


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


def _freeze_palettes(palettes: Mapping[str, Mapping[str, str]]) -> Mapping[str, Mapping[str, str]]:
    return MappingProxyType(
        {
            _normalize_version(version): MappingProxyType(dict(colors))
            for version, colors in palettes.items()
        }
    )


def _freeze_colorbrewer(colors: ColorBrewerColors) -> ColorBrewerColors:
    return MappingProxyType(
        {
            scheme: MappingProxyType({size: tuple(hexes) for size, hexes in sizes.items()})
            for scheme, sizes in colors.items()
        }
    )  # type: ignore[return-value]


def register_system(
    name: str,
    *,
    default_version: str,
    palettes: Mapping[str, Mapping[str, str]] | None = None,
    colorbrewer_palettes: ColorBrewerColors | None = None,
) -> SystemRecord:
    """Register or replace a color system at runtime."""
    system_name = _normalize_name(name)
    version = _normalize_version(default_version)
    record = SystemRecord(
        name=system_name,
        default_version=version,
        palettes=_freeze_palettes(palettes or {}),
        colorbrewer_palettes=_freeze_colorbrewer(colorbrewer_palettes or {}),
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
        names = [record.name]
        names.extend(f"{record.name}@{version}" for version in record.palettes)
        names.extend(
            f"{record.name}:{scheme}-{size}"
            for scheme, sizes in record.colorbrewer_palettes.items()
            for size in sizes
        )
        return tuple(dict.fromkeys(names))
    return tuple(name for system_name in list_systems() for name in list_palettes(system_name))


def get_palette(name: str):
    """Return a Palette from a registered system."""
    from colorbrew.palette import Palette

    family, _, variant = name.partition(":")
    system, version = resolve_name(family)
    record = get_system(system)
    if variant:
        scheme, _, size = variant.rpartition("-")
        try:
            return Palette.from_hexes(
                record.colorbrewer_palettes[scheme][size],
                kind="system",
                system=system,
                version=size,
                source="bundled",
            )
        except KeyError as exc:
            raise ColorValueError(f"Unknown palette: {name!r}") from exc

    palette_version = version or record.default_version
    try:
        colors = record.palettes[palette_version]
    except KeyError as exc:
        raise ColorValueError(f"Palette version is not available bundled: {name!r}") from exc
    return Palette.from_mapping(
        colors,
        kind="system",
        system=system,
        version=palette_version,
        source="bundled",
    )


register_system("css", default_version="v1", palettes={"v1": NAMED_COLORS})
register_system("tailwind", default_version="v3", palettes={"v3": TAILWIND_COLORS})
register_system("material", default_version="v2", palettes={"v2": MATERIAL_COLORS})
register_system(
    "colorbrewer",
    default_version="bundled",
    colorbrewer_palettes=load_colorbrewer_colors(),
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
