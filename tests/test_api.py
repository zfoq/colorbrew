"""Tests for the stdlib-only data API, cache, and remote payload parsing."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError

import pytest

from colorbrew.data.api import (
    _fetch_palette,
    _parse_css_palette,
    _write_cached_palette,
    get_palette,
    refresh_palette,
)
from colorbrew.exceptions import ColorValueError
from colorbrew.settings import get_settings, settings_context


class _FakeResponse:
    """Minimal response object for monkeypatching ``urlopen``."""

    def __init__(self, payload: object, status: int = 200):
        if isinstance(payload, bytes):
            self._payload = payload
        elif isinstance(payload, str):
            self._payload = payload.encode("utf-8")
        else:
            self._payload = json.dumps(payload).encode("utf-8")
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, *_args, **_kwargs):
        return self._payload


def _make_cache(cache_dir: Path, name: str, data: dict[str, str]) -> Path:
    path = cache_dir / f"{name}.json"
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")
    return path


class TestFetchPalette:
    """Remote payload parsing for JSON and CSS sources."""

    def test_json_flat_mapping(self, monkeypatch):
        """Flat JSON objects normalize to a name-to-hex mapping."""

        def fake_urlopen(_url: str, *, timeout: float):
            assert timeout == get_settings().timeout
            return _FakeResponse({"brand": "#aabbcc", "other": "#112233"})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        entries = _fetch_palette("https://example.com/palette.json", get_settings().timeout)
        assert entries == {"brand": "#aabbcc", "other": "#112233"}

    def test_json_nested_mapping(self, monkeypatch):
        """Nested JSON objects flatten to ``name-shade`` keys."""

        def fake_urlopen(_url: str, *, timeout: float):
            return _FakeResponse({"brand": {"500": "#aabbcc", "600": "#112233"}})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        entries = _fetch_palette("https://example.com/palette.json", 5.0)
        assert entries == {"brand-500": "#aabbcc", "brand-600": "#112233"}

    def test_css_hex_custom_properties(self, monkeypatch):
        """CSS custom properties with hex values are extracted."""
        css = """
        @theme {
          --color-red-500: #ef4444;
          --color-blue-500: #3b82f6;
        }
        """

        def fake_urlopen(_url: str, *, timeout: float):
            return _FakeResponse(css)

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        entries = _fetch_palette("https://example.com/theme.css", 5.0)
        assert entries == {"color-red-500": "#ef4444", "color-blue-500": "#3b82f6"}

    def test_css_oklch_custom_properties(self, monkeypatch):
        """CSS custom properties with OKLCH values are converted to hex."""
        css = """
        @theme {
          --color-red-500: oklch(63.7% 0.237 25.331);
          --color-green-500: oklch(0.7 0.2 145);
        }
        """

        def fake_urlopen(_url: str, *, timeout: float):
            return _FakeResponse(css)

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        entries = _fetch_palette("https://example.com/theme.css", 5.0)
        assert "color-red-500" in entries
        assert entries["color-red-500"].startswith("#")
        assert entries["color-green-500"].startswith("#")

    def test_empty_css_payload_raises(self):
        """A CSS payload without color values raises a clear error."""
        with pytest.raises(ColorValueError, match="No color custom properties"):
            _parse_css_palette(":root { --spacing: 1rem; }")

    def test_invalid_json_payload_raises(self, monkeypatch):
        """An invalid remote payload raises ``ColorValueError``."""

        def fake_urlopen(_url: str, *, timeout: float):
            return _FakeResponse("not json or css")

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        with pytest.raises(ColorValueError):
            _fetch_palette("https://example.com/bad", 5.0)

    def test_http_error_raises_color_value_error(self, monkeypatch):
        """HTTP errors are surfaced as ``ColorValueError``."""

        def fake_urlopen(_url: str, *, timeout: float):
            raise HTTPError("https://example.com/404", 404, "Not Found", {}, None)

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        with pytest.raises(ColorValueError, match="Remote palette request failed"):
            _fetch_palette("https://example.com/404", 5.0)


class TestPaletteCache:
    """Cache TTL and fallback behavior for ``get_palette``."""

    def test_cache_hit_within_ttl_avoids_network(self, monkeypatch, tmp_path: Path):
        """A fresh cache is used without hitting the network."""
        cache_dir = tmp_path / "cache"
        _make_cache(cache_dir, "tailwind-v4", {"brand-500": "#aabbcc"})

        calls: list[tuple[str, float]] = []

        def fake_urlopen(url: str, *, timeout: float):
            calls.append((url, timeout))
            return _FakeResponse({"brand-500": "#ddeeff"})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        palette = get_palette(
            "tailwind",
            version="v4",
            source="auto",
            allow_network=True,
            allow_cache=True,
            cache_dir=cache_dir,
            cache_ttl=300.0,
        )
        assert palette["brand-500"] == "#aabbcc"
        assert palette.source == "cache"
        assert calls == []

    def test_stale_cache_fetches_when_network_allowed(self, monkeypatch, tmp_path: Path):
        """A stale cache triggers a remote fetch when network is allowed."""
        cache_dir = tmp_path / "cache"
        path = _make_cache(cache_dir, "tailwind-v4", {"brand-500": "#aabbcc"})
        old_time = time.time() - 600.0
        os.utime(path, (old_time, old_time))

        def fake_urlopen(_url: str, *, timeout: float):
            return _FakeResponse({"brand-500": "#ddeeff"})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        palette = get_palette(
            "tailwind",
            version="v4",
            source="auto",
            allow_network=True,
            allow_cache=True,
            cache_dir=cache_dir,
            cache_ttl=300.0,
        )
        assert palette["brand-500"] == "#ddeeff"
        assert palette.source == "api"
        assert json.loads((cache_dir / "tailwind-v4.json").read_text()) == {
            "brand-500": "#ddeeff"
        }

    def test_stale_cache_and_network_disabled_falls_back_to_bundled(
        self, monkeypatch, tmp_path: Path
    ):
        """A stale cache with network disabled falls back to bundled data."""
        cache_dir = tmp_path / "cache"
        path = _make_cache(cache_dir, "tailwind-v3", {"brand-500": "#aabbcc"})
        old_time = time.time() - 600.0
        os.utime(path, (old_time, old_time))

        calls: list[tuple[str, float]] = []

        def fake_urlopen(url: str, *, timeout: float):
            calls.append((url, timeout))
            return _FakeResponse({"brand-500": "#ddeeff"})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        palette = get_palette(
            "tailwind",
            version="v3",
            source="auto",
            allow_network=False,
            allow_cache=True,
            cache_dir=cache_dir,
            cache_ttl=300.0,
        )
        assert palette["sky-500"] == "#0ea5e9"
        assert palette.source == "bundled"
        assert calls == []

    def test_network_disabled_for_api_source_raises(self, monkeypatch, tmp_path: Path):
        """``source="api"`` with network disabled raises immediately."""
        with pytest.raises(ColorValueError, match="network access is disabled"):
            get_palette(
                "tailwind",
                version="v4",
                source="api",
                allow_network=False,
                allow_cache=True,
                cache_dir=tmp_path,
            )

    def test_cache_disabled_for_cache_source_raises(self, tmp_path: Path):
        """``source="cache"`` with cache disabled raises immediately."""
        with pytest.raises(ColorValueError, match="cache access is disabled"):
            get_palette(
                "tailwind",
                source="cache",
                allow_cache=False,
                cache_dir=tmp_path,
            )

    def test_source_cache_ignores_ttl(self, tmp_path: Path):
        """``source="cache"`` reads the file regardless of TTL."""
        cache_dir = tmp_path / "cache"
        path = _make_cache(cache_dir, "tailwind-v3", {"brand-500": "#aabbcc"})
        old_time = time.time() - 600.0
        os.utime(path, (old_time, old_time))

        palette = get_palette(
            "tailwind",
            version="v3",
            source="cache",
            allow_cache=True,
            cache_dir=cache_dir,
            cache_ttl=300.0,
        )
        assert palette["brand-500"] == "#aabbcc"
        assert palette.source == "cache"

    def test_atomic_cache_write(self, tmp_path: Path):
        """Cache writes use a temporary file and replace atomically."""
        cache_dir = tmp_path / "cache"
        _write_cached_palette("test", {"key": "#aabbcc"}, cache_dir)
        assert json.loads((cache_dir / "test.json").read_text()) == {"key": "#aabbcc"}
        assert not list(cache_dir.glob("*.tmp.*"))


class TestRefreshPalette:
    """Remote refresh helper behavior."""

    def test_refresh_palette_fetches_and_caches(self, monkeypatch, tmp_path: Path):
        """``refresh_palette`` fetches a remote URL and writes the cache."""

        def fake_urlopen(url: str, *, timeout: float):
            assert url == "https://example.com/palette.json"
            assert timeout == get_settings().timeout
            return _FakeResponse({"brand-500": "#aabbcc"})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        with settings_context(cache_dir=tmp_path):
            palette = refresh_palette("tailwind", url="https://example.com/palette.json")
        assert palette["brand-500"] == "#aabbcc"
        assert palette.source == "api"
        assert json.loads((tmp_path / "tailwind-v3.json").read_text()) == {
            "brand-500": "#aabbcc"
        }

    def test_refresh_palette_rejects_empty_url(self):
        """``refresh_palette`` rejects blank URLs."""
        with pytest.raises(ColorValueError, match="URL must not be empty"):
            refresh_palette("tailwind", url="   ")

    def test_refresh_palette_supports_css(self, monkeypatch, tmp_path: Path):
        """``refresh_palette`` can fetch and cache a CSS payload."""
        css = ":root { --primary: oklch(0.6 0.2 180); --surface: #ffffff; }"

        def fake_urlopen(_url: str, *, timeout: float):
            return _FakeResponse(css)

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        palette = refresh_palette(
            "material",
            version="v3",
            url="https://example.com/theme.css",
            cache_dir=tmp_path,
        )
        assert palette["primary"].startswith("#")
        assert palette["surface"] == "#ffffff"
