"""Global settings for ColorBrew."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterator

from colorbrew.exceptions import ColorValueError
from colorbrew.types import DistanceMethod

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


def _default_cache_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "colorbrew"
    if os.name == "nt":
        return (
            Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            / "colorbrew"
        )
    return Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache")) / "colorbrew"


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in _TRUE:
        return True
    if normalized in _FALSE:
        return False
    raise ColorValueError(f"{name} must be a boolean value.")


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ColorValueError(f"{name} must be a number.") from exc
    if parsed < 0:
        raise ColorValueError(f"{name} must be non-negative.")
    return parsed


@dataclass(frozen=True)
class Settings:
    """Runtime settings for optional palette I/O."""

    allow_network: bool = False
    allow_cache: bool = True
    cache_dir: Path = _default_cache_dir()
    cache_ttl: float = 604_800.0
    timeout: float = 5.0
    default_distance: DistanceMethod = "ciede2000"


def _from_env() -> Settings:
    return Settings(
        allow_network=_env_bool("COLORBREW_ALLOW_NETWORK", False),
        allow_cache=_env_bool("COLORBREW_ALLOW_CACHE", True),
        cache_dir=Path(os.getenv("COLORBREW_CACHE_DIR", _default_cache_dir())),
        cache_ttl=_env_float("COLORBREW_CACHE_TTL", 604_800.0),
        timeout=_env_float("COLORBREW_TIMEOUT", 5.0),
    )


_settings = _from_env()


def get_settings() -> Settings:
    """Return the active global settings."""
    return _settings


def configure(**changes: object) -> Settings:
    """Update global settings and return the new value."""
    global _settings
    if "cache_dir" in changes:
        changes["cache_dir"] = Path(changes["cache_dir"])  # type: ignore[arg-type]
    _settings = replace(_settings, **changes)
    return _settings


@contextmanager
def settings_context(**changes: object) -> Iterator[Settings]:
    """Temporarily update global settings inside a context manager."""
    global _settings
    previous = _settings
    try:
        yield configure(**changes)
    finally:
        _settings = previous
