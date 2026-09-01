"""Optional stdlib-only palette loading and refresh helpers."""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from urllib.request import urlopen

from colorbrew.data.material_colors import MATERIAL_COLORS
from colorbrew.data.named_colors import NAMED_COLORS
from colorbrew.data.tailwind_colors import TAILWIND_COLORS
from colorbrew.exceptions import ColorValueError

_HEX_RE = re.compile(r"^#[0-9a-f]{6}$")

_BUNDLED_PALETTES: dict[str, dict[str, str]] = {
    "named": NAMED_COLORS,
    "tailwind": TAILWIND_COLORS,
    "material": MATERIAL_COLORS,
}

# ponytail: remote refresh is JSON-only for now; add source-specific parsers when
# canonical upstream files need direct ingestion.
_PALETTE_URLS: dict[str, str] = {}


def _cache_file(name: str, cache_dir: str | Path | None) -> Path:
    base = Path(cache_dir) if cache_dir is not None else Path(tempfile.gettempdir()) / "colorbrew-palettes"
    return base / f"{name}.json"


def _normalize_palette(palette: object) -> dict[str, str]:
    if not isinstance(palette, dict) or not palette:
        raise ColorValueError("Palette data must be a non-empty mapping.")

    normalized: dict[str, str] = {}
    for key, value in palette.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ColorValueError("Palette entries must be string-to-string mappings.")
        name = key.strip().lower()
        hex_value = value.strip().lower()
        if not name:
            raise ColorValueError("Palette keys must not be empty.")
        if not _HEX_RE.match(hex_value):
            raise ColorValueError(f"Invalid hex color for {key!r}: {value!r}")
        normalized[name] = hex_value
    return normalized


def _fetch_palette(url: str, timeout: float) -> dict[str, str]:
    with urlopen(url, timeout=timeout) as response:  # nosec: caller opts into network access
        data = json.load(response)
    return _normalize_palette(data)


def _load_cached_palette(name: str, cache_dir: str | Path | None) -> dict[str, str]:
    return _normalize_palette(json.loads(_cache_file(name, cache_dir).read_text()))


def _write_cached_palette(
    name: str,
    palette: dict[str, str],
    cache_dir: str | Path | None,
) -> None:
    path = _cache_file(name, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(palette, sort_keys=True, indent=2) + "\n")
    tmp.replace(path)


def list_palettes() -> tuple[str, ...]:
    """Return the built-in palette family names."""
    return tuple(_BUNDLED_PALETTES)


def _validate_palette_name(name: str) -> str:
    palette_name = name.strip().lower()
    if palette_name not in _BUNDLED_PALETTES:
        raise ColorValueError(f"Unknown palette family: {name!r}")
    return palette_name


def _validate_source(source: str) -> str:
    source_name = source.strip().lower()
    if source_name not in {"bundled", "cache", "api", "auto"}:
        raise ColorValueError(f"Unknown palette source: {source!r}")
    return source_name


def get_palette(
    name: str,
    *,
    source: str = "bundled",
    allow_network: bool = False,
    allow_cache: bool = False,
    cache_dir: str | Path | None = None,
    url: str | None = None,
    timeout: float = 5.0,
) -> dict[str, str]:
    """Load a palette from bundled data, cache, or an opt-in URL.

    Args:
        name: Palette family name: ``"named"``, ``"tailwind"``, or ``"material"``.
        source: ``"bundled"``, ``"cache"``, ``"api"``, or ``"auto"``.
        allow_network: Permit network fetches for ``"api"`` or ``"auto"``.
        allow_cache: Permit disk cache reads/writes for ``"cache"``, ``"api"``, or ``"auto"``.
        cache_dir: Optional cache directory override.
        url: Optional JSON URL override for remote fetches.
        timeout: Network timeout in seconds.

    Returns:
        A normalized ``dict[str, str]`` palette.

    Raises:
        ColorValueError: If the palette name/source is unknown or access is disabled.
    """
    palette_name = _validate_palette_name(name)
    source_name = _validate_source(source)

    if source_name == "bundled":
        return dict(_BUNDLED_PALETTES[palette_name])

    if source_name == "cache":
        if not allow_cache:
            raise ColorValueError("Palette cache access is disabled.")
        return _load_cached_palette(palette_name, cache_dir)

    if source_name == "api":
        if not allow_network:
            raise ColorValueError("Palette network access is disabled.")
        palette_url = url or _PALETTE_URLS.get(palette_name)
        if palette_url is None:
            raise ColorValueError(f"No remote source configured for palette: {palette_name}")
        palette = _fetch_palette(palette_url, timeout)
        if allow_cache:
            _write_cached_palette(palette_name, palette, cache_dir)
        return palette

    if source_name == "auto":
        if allow_network:
            try:
                return get_palette(
                    palette_name,
                    source="api",
                    allow_network=True,
                    allow_cache=allow_cache,
                    cache_dir=cache_dir,
                    url=url,
                    timeout=timeout,
                )
            except OSError:
                pass
            except ColorValueError:
                if url is not None:
                    raise
        if allow_cache:
            try:
                return get_palette(
                    palette_name,
                    source="cache",
                    allow_cache=True,
                    cache_dir=cache_dir,
                )
            except OSError:
                pass
        return get_palette(palette_name, source="bundled")

    raise ColorValueError(f"Unknown palette source: {source!r}")


def refresh_palette(
    name: str,
    *,
    url: str,
    cache_dir: str | Path | None = None,
    write_cache: bool = True,
    timeout: float = 5.0,
) -> dict[str, str]:
    """Fetch a palette from a JSON API and optionally cache it."""
    palette_name = _validate_palette_name(name)
    if not url.strip():
        raise ColorValueError("Palette URL must not be empty.")
    palette = _fetch_palette(url, timeout)
    if write_cache:
        _write_cached_palette(palette_name, palette, cache_dir)
    return palette
