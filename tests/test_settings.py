"""Tests for colorbrew.settings global configuration."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

import colorbrew.settings as settings_module
from colorbrew.exceptions import ColorValueError
from colorbrew.settings import Settings, configure, get_settings, settings_context


def test_settings_defaults_use_platform_cache_dir() -> None:
    settings = Settings()

    assert settings.allow_network is False
    assert settings.allow_cache is True
    assert settings.cache_dir.name == "colorbrew"
    assert settings.cache_ttl == 604_800.0
    assert settings.timeout == 5.0
    assert settings.default_distance == "ciede2000"


def test_configure_updates_settings_and_context_restores() -> None:
    original = get_settings()
    configured = configure(
        allow_network=True, cache_dir="/tmp/colorbrew-test", timeout=2.5
    )

    assert configured.allow_network is True
    assert configured.cache_dir == Path("/tmp/colorbrew-test")
    assert configured.timeout == 2.5

    with settings_context(allow_network=False, cache_ttl=1.0) as temporary:
        assert temporary.allow_network is False
        assert get_settings().cache_ttl == 1.0

    assert get_settings() == configured
    configure(**original.__dict__)


def test_settings_context_restores_after_exception() -> None:
    original = get_settings()

    with pytest.raises(RuntimeError, match="boom"):
        with settings_context(timeout=1.0):
            raise RuntimeError("boom")

    assert get_settings() == original


def test_env_settings_parse_without_leaking_global_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COLORBREW_ALLOW_NETWORK", "yes")
    monkeypatch.setenv("COLORBREW_ALLOW_CACHE", "off")
    monkeypatch.setenv("COLORBREW_CACHE_DIR", "/tmp/colorbrew-env")
    monkeypatch.setenv("COLORBREW_CACHE_TTL", "12.5")
    monkeypatch.setenv("COLORBREW_TIMEOUT", "3")
    reloaded = importlib.reload(settings_module)
    current = reloaded.get_settings()

    assert current.allow_network is True
    assert current.allow_cache is False
    assert current.cache_dir == Path("/tmp/colorbrew-env")
    assert current.cache_ttl == 12.5
    assert current.timeout == 3.0

    monkeypatch.delenv("COLORBREW_ALLOW_NETWORK")
    monkeypatch.delenv("COLORBREW_ALLOW_CACHE")
    monkeypatch.delenv("COLORBREW_CACHE_DIR")
    monkeypatch.delenv("COLORBREW_CACHE_TTL")
    monkeypatch.delenv("COLORBREW_TIMEOUT")
    restored = importlib.reload(settings_module)

    assert restored.get_settings().cache_dir.name == "colorbrew"


def test_invalid_env_values_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COLORBREW_ALLOW_CACHE", "sometimes")

    with pytest.raises(ColorValueError, match="COLORBREW_ALLOW_CACHE"):
        importlib.reload(settings_module)

    monkeypatch.setenv("COLORBREW_ALLOW_CACHE", "true")
    monkeypatch.setenv("COLORBREW_TIMEOUT", "-1")

    with pytest.raises(ColorValueError, match="COLORBREW_TIMEOUT"):
        importlib.reload(settings_module)

    monkeypatch.delenv("COLORBREW_ALLOW_CACHE")
    monkeypatch.delenv("COLORBREW_TIMEOUT")
    importlib.reload(settings_module)


def test_default_cache_dir_follows_platform_suffix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings_module.sys, "platform", sys.platform)

    assert settings_module._default_cache_dir().parts[-1] == "colorbrew"
