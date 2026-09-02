"""Optional stdlib-only palette loading and refresh helpers."""

from __future__ import annotations

import json
import re
import time
from importlib.metadata import version as _package_version
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from colorbrew.conversion.oklab import oklch_css_to_rgb
from colorbrew.data.loader import (
    MATERIAL_COLORS,
    NAMED_COLORS,
    TAILWIND_COLORS,
)
from colorbrew.exceptions import ColorValueError
from colorbrew.palette import Palette
from colorbrew.settings import Settings, get_settings

_PACKAGE_VERSION = _package_version("colorbrew")

_HEX_RE = re.compile(r"^#[0-9a-f]{6}$")
_CSS_VAR_RE = re.compile(
    r"--([a-zA-Z0-9_-]+):\s*(#[0-9a-f]{6}|oklch\([^)]+\))\s*;",
    re.IGNORECASE,
)

_DEFAULT_VERSIONS: dict[str, str] = {
    "named": "v1",
    "tailwind": "v3",
    "material": "v2",
}

_SUPPORTED_VERSIONS: dict[str, tuple[str, ...]] = {
    "named": ("v1",),
    "tailwind": ("v3", "v4"),
    "material": ("v2", "v3"),
}

_BUNDLED_PALETTES: dict[str, dict[str, str]] = {
    "named": NAMED_COLORS,
    "named@v1": NAMED_COLORS,
    "tailwind": TAILWIND_COLORS,
    "tailwind@v3": TAILWIND_COLORS,
    "material": MATERIAL_COLORS,
    "material@v2": MATERIAL_COLORS,
}

_PALETTE_URLS: dict[str, str] = {
    "tailwind@v3": (
        "https://gist.githubusercontent.com/indaco/"
        "e2a62b02a637619897b02da8405f3022/raw/tailwindcss_colors.json"
    ),
    "tailwind@v4": (
        "https://raw.githubusercontent.com/tailwindlabs/tailwindcss/"
        "v4.0.0/packages/tailwindcss/theme.css"
    ),
    "material@v3": (
        "https://raw.githubusercontent.com/material-foundation/material-tokens/"
        "main/css/baseline.css"
    ),
}


def _cache_file(name: str, cache_dir: Path | None) -> Path:
    base = cache_dir if cache_dir is not None else get_settings().cache_dir
    return base / f"{name}.json"


def _cache_key(family: str, version: str) -> str:
    return f"{family}-{version}"


def _normalize_palette(palette: object) -> dict[str, str]:
    if not isinstance(palette, dict) or not palette:
        raise ColorValueError("Palette data must be a non-empty mapping.")

    normalized: dict[str, str] = {}
    for key, value in palette.items():
        if not isinstance(key, str):
            raise ColorValueError("Palette keys must be strings.")
        name = key.strip().lower()
        if not name:
            raise ColorValueError("Palette keys must not be empty.")

        if isinstance(value, str):
            hex_value = value.strip().lower()
            if not _HEX_RE.match(hex_value):
                raise ColorValueError(f"Invalid hex color for {key!r}: {value!r}")
            normalized[name] = hex_value
        elif isinstance(value, dict):
            for shade, shade_value in value.items():
                shade_str = str(shade).strip().lower()
                if not isinstance(shade_value, str):
                    raise ColorValueError(
                        f"Palette entries must be string-to-string mappings: {key!r}"
                    )
                hex_value = shade_value.strip().lower()
                if not _HEX_RE.match(hex_value):
                    raise ColorValueError(
                        f"Invalid hex color for {key!r}.{shade!r}: {shade_value!r}"
                    )
                normalized[f"{name}-{shade_str}"] = hex_value
        else:
            raise ColorValueError("Palette entries must be string-to-string mappings.")
    return normalized


def _parse_css_palette(text: str) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for name, value in _CSS_VAR_RE.findall(text):
        key = name.strip().lower()
        value = value.strip().lower()
        if value.startswith("#"):
            hex_value = value
        else:
            try:
                rgb = oklch_css_to_rgb(value)
            except ValueError as exc:
                raise ColorValueError(f"Invalid OKLCH value for {key!r}: {value!r}") from exc
            hex_value = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        if not _HEX_RE.match(hex_value):
            raise ColorValueError(f"Invalid hex color for {key!r}: {value!r}")
        normalized[key] = hex_value
    if not normalized:
        raise ColorValueError("No color custom properties found in CSS payload.")
    return normalized


def _fetch_palette(url: str, timeout: float) -> dict[str, str]:
    try:
        with urlopen(url, timeout=timeout) as response:  # nosec: caller opts into network access
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        raise ColorValueError(f"Remote palette request failed for {url!r}: {exc}") from exc
    except OSError as exc:
        raise ColorValueError(f"Remote palette request failed for {url!r}: {exc}") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return _parse_css_palette(payload)
    return _normalize_palette(data)


def _load_cached_palette(name: str, cache_dir: Path | None) -> dict[str, str]:
    path = _cache_file(name, cache_dir)
    return _normalize_palette(json.loads(path.read_text()))


def _is_cache_fresh(path: Path, cache_ttl: float) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) <= cache_ttl


def _write_cached_palette(
    name: str,
    palette: dict[str, str],
    cache_dir: Path | None,
) -> None:
    path = _cache_file(name, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f".tmp.{_PACKAGE_VERSION}")
    tmp.write_text(json.dumps(palette, sort_keys=True, indent=2) + "\n")
    tmp.replace(path)


def list_palettes() -> tuple[str, ...]:
    """Return the built-in palette family names."""
    return tuple(_DEFAULT_VERSIONS)


def _palette_key(family: str, version: str) -> str:
    return f"{family}@{version}"


def _parse_palette_name(name: str) -> tuple[str, str | None]:
    parts = name.strip().split("@", 1)
    family = parts[0].strip().lower()
    version = parts[1].strip().lower() if len(parts) > 1 else None
    return family, version


def _validate_palette_version(family: str, version: str) -> str:
    if version not in _SUPPORTED_VERSIONS[family]:
        raise ColorValueError(
            f"Unsupported palette version for {family!r}: {version!r}"
        )
    return version


def _validate_palette_name(name: str) -> tuple[str, str]:
    family, version = _parse_palette_name(name)
    if family not in _DEFAULT_VERSIONS:
        raise ColorValueError(f"Unknown palette family: {name!r}")
    effective_version = version or _DEFAULT_VERSIONS[family]
    _validate_palette_version(family, effective_version)
    return family, effective_version


def _validate_source(source: str) -> str:
    source_name = source.strip().lower()
    if source_name not in {"bundled", "cache", "api", "auto"}:
        raise ColorValueError(f"Unknown palette source: {source!r}")
    return source_name


def _resolve_settings(
    allow_network: bool | None,
    allow_cache: bool | None,
    cache_dir: str | Path | None,
    cache_ttl: float | None,
    timeout: float | None,
) -> Settings:
    settings = get_settings()
    return Settings(
        allow_network=settings.allow_network if allow_network is None else allow_network,
        allow_cache=settings.allow_cache if allow_cache is None else allow_cache,
        cache_dir=Path(cache_dir) if cache_dir is not None else settings.cache_dir,
        cache_ttl=settings.cache_ttl if cache_ttl is None else cache_ttl,
        timeout=settings.timeout if timeout is None else timeout,
        default_distance=settings.default_distance,
    )


def get_palette(
    name: str,
    *,
    version: str | None = None,
    source: str = "bundled",
    allow_network: bool | None = None,
    allow_cache: bool | None = None,
    cache_dir: str | Path | None = None,
    cache_ttl: float | None = None,
    url: str | None = None,
    timeout: float | None = None,
) -> Palette:
    """Load a palette from bundled data, cache, or an opt-in URL.

    Args:
        name: Palette family name: ``"named"``, ``"tailwind"``, or ``"material"``.
            A version can be pinned with ``family@version`` (e.g. ``"tailwind@v4"``).
        version: Optional explicit version, e.g. ``"v3"`` or ``"v4"``.
            Defaults to the family's stable bundled version.
        source: ``"bundled"``, ``"cache"``, ``"api"``, or ``"auto"``.
        allow_network: Permit network fetches for ``"api"`` or ``"auto"``.
            Defaults to the global :class:`Settings` value.
        allow_cache: Permit disk cache reads/writes for ``"cache"``, ``"api"``, or ``"auto"``.
            Defaults to the global :class:`Settings` value.
        cache_dir: Optional cache directory override.
        cache_ttl: Optional cache time-to-live override in seconds.
        url: Optional JSON or CSS URL override for remote fetches.
        timeout: Network timeout in seconds.

    Returns:
        A :class:`Palette` with ``system``, ``version``, and ``source`` metadata.

    Raises:
        ColorValueError: If the palette name/version/source is unknown or access is disabled.
    """
    resolved = _resolve_settings(
        allow_network, allow_cache, cache_dir, cache_ttl, timeout
    )
    palette_name, parsed_version = _validate_palette_name(name)
    palette_version = (
        _validate_palette_version(palette_name, version.strip().lower())
        if version is not None
        else parsed_version
    )
    source_name = _validate_source(source)
    key = _palette_key(palette_name, palette_version)
    cache_key = _cache_key(palette_name, palette_version)

    if source_name == "bundled":
        if key not in _BUNDLED_PALETTES:
            raise ColorValueError(f"Palette version is not available bundled: {key!r}")
        return Palette.from_mapping(
            _BUNDLED_PALETTES[key],
            kind="system",
            system=palette_name,
            version=palette_version,
            source="bundled",
        )

    if source_name == "cache":
        if not resolved.allow_cache:
            raise ColorValueError("Palette cache access is disabled.")
        return Palette.from_mapping(
            _load_cached_palette(cache_key, resolved.cache_dir),
            kind="system",
            system=palette_name,
            version=palette_version,
            source="cache",
        )

    if source_name == "api":
        if not resolved.allow_network:
            raise ColorValueError("Palette network access is disabled.")
        palette_url = url or _PALETTE_URLS.get(key)
        if palette_url is None:
            raise ColorValueError(f"No remote source configured for palette: {key}")
        entries = _fetch_palette(palette_url, resolved.timeout)
        if resolved.allow_cache:
            _write_cached_palette(cache_key, entries, resolved.cache_dir)
        return Palette.from_mapping(
            entries,
            kind="system",
            system=palette_name,
            version=palette_version,
            source="api",
        )

    if source_name == "auto":
        cache_path = _cache_file(cache_key, resolved.cache_dir)
        if resolved.allow_cache and _is_cache_fresh(cache_path, resolved.cache_ttl):
            return Palette.from_mapping(
                _load_cached_palette(cache_key, resolved.cache_dir),
                kind="system",
                system=palette_name,
                version=palette_version,
                source="cache",
            )
        if resolved.allow_network:
            try:
                palette_url = url or _PALETTE_URLS.get(key)
                if palette_url is None:
                    raise ColorValueError(
                        f"No remote source configured for palette: {key}"
                    )
                entries = _fetch_palette(palette_url, resolved.timeout)
                if resolved.allow_cache:
                    _write_cached_palette(cache_key, entries, resolved.cache_dir)
                return Palette.from_mapping(
                    entries,
                    kind="system",
                    system=palette_name,
                    version=palette_version,
                    source="api",
                )
            except (OSError, ColorValueError):
                if url is not None:
                    raise
        if key not in _BUNDLED_PALETTES:
            raise ColorValueError(
                f"Palette version is not available bundled: {key!r}"
            )
        return Palette.from_mapping(
            _BUNDLED_PALETTES[key],
            kind="system",
            system=palette_name,
            version=palette_version,
            source="bundled",
        )

    raise ColorValueError(f"Unknown palette source: {source!r}")


def refresh_palette(
    name: str,
    *,
    url: str,
    version: str | None = None,
    cache_dir: str | Path | None = None,
    cache_ttl: float | None = None,
    write_cache: bool = True,
    timeout: float | None = None,
) -> Palette:
    """Fetch a palette from a remote URL and optionally cache it.

    Args:
        name: Palette family name, optionally with ``@version``.
        url: Remote JSON or CSS URL.
        version: Optional explicit version.
        cache_dir: Optional cache directory override.
        cache_ttl: Optional cache TTL; only used when ``write_cache`` is true
            to backfill the default for future ``source="auto"`` reads.
        write_cache: Write the fetched palette to the cache directory.
        timeout: Network timeout in seconds.

    Returns:
        A :class:`Palette` loaded from the remote source.
    """
    resolved = _resolve_settings(
        allow_network=True,
        allow_cache=write_cache,
        cache_dir=cache_dir,
        cache_ttl=cache_ttl,
        timeout=timeout,
    )
    palette_name, parsed_version = _validate_palette_name(name)
    palette_version = (
        _validate_palette_version(palette_name, version.strip().lower())
        if version is not None
        else parsed_version
    )
    cache_key = _cache_key(palette_name, palette_version)
    if not url.strip():
        raise ColorValueError("Palette URL must not be empty.")
    entries = _fetch_palette(url, resolved.timeout)
    if resolved.allow_cache:
        _write_cached_palette(cache_key, entries, resolved.cache_dir)
    return Palette.from_mapping(
        entries,
        kind="system",
        system=palette_name,
        version=palette_version,
        source="api",
    )
