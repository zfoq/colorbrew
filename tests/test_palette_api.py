"""Tests for optional stdlib-only palette loading and refresh."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.error import URLError

import pytest

from colorbrew.data import (
    Palette,
    get_palette,
    get_palette_entries,
    list_palettes,
    refresh_palette,
)
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

    def test_get_palette_returns_palette_object(self):
        """``get_palette`` returns a Palette instance."""
        palette = get_palette("tailwind")
        assert isinstance(palette, Palette)

    def test_get_palette_has_family_version_source_entries(self):
        """Palette exposes family, version, source, and entries."""
        palette = get_palette("tailwind")
        assert palette.family == "tailwind"
        assert palette.source == "bundled"
        assert isinstance(palette.version, str)
        assert palette.entries["sky-500"] == "#0ea5e9"

    def test_get_palette_entries_returns_plain_dict(self):
        """Compatibility helper returns old dict entries."""
        entries = get_palette_entries("tailwind")
        assert isinstance(entries, dict)
        assert entries["sky-500"] == "#0ea5e9"

    def test_get_palette_acts_like_a_mapping(self):
        """Palette supports subscript, membership, and iteration."""
        palette = get_palette("tailwind")
        assert "sky-500" in palette
        assert palette["sky-500"] == "#0ea5e9"
        assert isinstance(len(palette), int)
        assert "sky-500" in dict(palette)

    def test_palette_mapping_uses_case_insensitive_key_semantics(self):
        """Subscript, membership, and get agree on normalized keys."""
        palette = get_palette("tailwind")
        assert palette[" SKY-500 "] == "#0ea5e9"
        assert palette.get("SKY-500") == "#0ea5e9"
        assert "Sky-500" in palette
        assert "missing" not in palette
        assert palette.get("missing") is None
        assert palette.get("missing", "#000000") == "#000000"
        with pytest.raises(KeyError):
            palette["missing"]

    def test_palette_hash_is_explicit_and_stable(self):
        """Palette exposes a working content hash, not a broken dataclass default."""
        palette1 = get_palette("tailwind")
        palette2 = get_palette("tailwind")
        assert hash(palette1) == hash(palette2)
        assert isinstance(hash(palette1), int)
        assert len({palette1, palette2}) == 1

    def test_get_palette_returns_a_copy(self):
        """Bundled lookups should not expose the module constant by reference."""
        palette1 = get_palette("tailwind")
        palette2 = get_palette("tailwind")
        assert palette1.entries is not palette2.entries
        palette1.entries["sky-500"] = "#112233"
        assert palette2.entries["sky-500"] == "#0ea5e9"

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
        ).entries == {"brand-500": "#112233"}

    def test_get_palette_rejects_disabled_cache(self, tmp_path: Path):
        """Reject cache reads when cache access is disabled."""
        with pytest.raises(ColorValueError, match="cache access is disabled"):
            get_palette("tailwind", source="cache", cache_dir=tmp_path)

    def test_get_palette_rejects_disabled_network(self):
        """Reject API reads when network access is disabled."""
        with pytest.raises(ColorValueError, match="network access is disabled"):
            get_palette("tailwind", source="api")

    def test_get_palette_rejects_unknown_source(self):
        """Reject invalid source names."""
        with pytest.raises(ColorValueError, match="Unknown palette source"):
            get_palette("tailwind", source="elsewhere")

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
        assert isinstance(palette, Palette)
        assert palette.entries == {"brand-500": "#112233"}
        assert json.loads((cache_dir / "tailwind.json").read_text()) == {
            "brand-500": "#112233"
        }

    def test_refresh_palette_rejects_empty_url(self, tmp_path: Path):
        """Reject blank refresh URLs."""
        with pytest.raises(ColorValueError, match="URL must not be empty"):
            refresh_palette("tailwind", url="   ", cache_dir=tmp_path)

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
        ).entries == {"brand-500": "#112233"}
        assert (
            get_palette(
                "tailwind",
                source="auto",
                allow_network=True,
                allow_cache=False,
                url="https://example.com/tailwind.json",
            )["sky-500"]
            == "#0ea5e9"
        )
