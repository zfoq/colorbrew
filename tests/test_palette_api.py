"""Tests for optional stdlib-only palette loading and refresh."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.error import URLError

import pytest

from colorbrew.data import get_palette, list_palettes, refresh_palette
from colorbrew.exceptions import ColorValueError


class _FakeResponse:
    def __init__(self, payload: object):
        self._payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, *_args, **_kwargs):
        return self._payload


class TestPaletteApi:
    """Test optional palette loading helpers."""

    def test_list_palettes(self):
        """Expose the built-in palette family names."""
        assert list_palettes() == ("named", "tailwind", "material")

    def test_get_palette_defaults_to_bundled(self):
        """Load bundled data without cache or network."""
        palette = get_palette("tailwind")
        assert palette["sky-500"] == "#0ea5e9"

    def test_get_palette_reads_cache_when_enabled(self, tmp_path: Path):
        """Read a cached palette only when cache access is enabled."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "tailwind.json").write_text('{"brand-500": "#112233"}\n')
        assert get_palette(
            "tailwind",
            source="cache",
            allow_cache=True,
            cache_dir=cache_dir,
        ) == {"brand-500": "#112233"}

    def test_get_palette_rejects_disabled_cache(self, tmp_path: Path):
        """Reject cache reads when cache access is disabled."""
        with pytest.raises(ColorValueError, match="cache access is disabled"):
            get_palette("tailwind", source="cache", cache_dir=tmp_path)

    def test_get_palette_rejects_disabled_network(self):
        """Reject API reads when network access is disabled."""
        with pytest.raises(ColorValueError, match="network access is disabled"):
            get_palette("tailwind", source="api")

    def test_refresh_palette_fetches_and_caches(self, monkeypatch, tmp_path: Path):
        """Fetch remote JSON and write it to the optional cache."""
        def fake_urlopen(url: str, timeout: float):
            assert url == "https://example.com/tailwind.json"
            assert timeout == 5.0
            return _FakeResponse({"brand-500": "#112233"})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        cache_dir = tmp_path / "cache"
        palette = refresh_palette(
            "tailwind",
            url="https://example.com/tailwind.json",
            cache_dir=cache_dir,
        )
        assert palette == {"brand-500": "#112233"}
        assert json.loads((cache_dir / "tailwind.json").read_text()) == {
            "brand-500": "#112233"
        }

    def test_get_palette_auto_falls_back_to_cache_then_bundled(
        self, monkeypatch, tmp_path: Path
    ):
        """Fall back from API to cache, then to bundled data."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "tailwind.json").write_text('{"brand-500": "#112233"}\n')

        def failing_urlopen(_url: str, timeout: float):
            raise URLError("offline")

        monkeypatch.setattr("colorbrew.data.api.urlopen", failing_urlopen)
        assert get_palette(
            "tailwind",
            source="auto",
            allow_network=True,
            allow_cache=True,
            cache_dir=cache_dir,
            url="https://example.com/tailwind.json",
        ) == {"brand-500": "#112233"}
        assert get_palette(
            "tailwind",
            source="auto",
            allow_network=True,
            allow_cache=False,
            url="https://example.com/tailwind.json",
        )["sky-500"] == "#0ea5e9"
