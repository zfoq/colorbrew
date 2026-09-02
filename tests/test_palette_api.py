"""Tests for optional stdlib-only palette loading and refresh helpers."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.error import URLError

import pytest

from colorbrew.data.api import (
    get_palette,
    list_palettes,
    refresh_palette,
)
from colorbrew.exceptions import ColorValueError
from colorbrew.palette import Palette


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
        """Expose the built-in palette system names."""
        assert list_palettes() == ("named", "tailwind", "material")

    def test_get_palette_defaults_to_bundled(self):
        """Load bundled data without cache or network."""
        palette = get_palette("tailwind")
        assert palette["sky-500"] == "#0ea5e9"

    def test_get_palette_returns_palette_object(self):
        """``get_palette`` returns a Palette instance."""
        palette = get_palette("tailwind")
        assert isinstance(palette, Palette)

    def test_get_palette_has_system_version_source(self):
        """Palette exposes system, version, and source metadata."""
        palette = get_palette("tailwind")
        assert palette.system == "tailwind"
        assert palette.source == "bundled"
        assert isinstance(palette.version, str)
        assert palette.as_dict()["sky-500"] == "#0ea5e9"

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
        assert palette1 is not palette2
        assert palette1.colors is not palette2.colors

    def test_get_palette_reads_cache_when_enabled(self, tmp_path: Path):
        """Read a cached palette only when cache access is enabled."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "tailwind-v3.json").write_text('{"brand-500": "#112233"}\n')
        assert get_palette(
            "tailwind",
            source="cache",
            allow_cache=True,
            cache_dir=cache_dir,
        ).as_dict() == {"brand-500": "#112233"}

    def test_get_palette_rejects_disabled_cache(self, tmp_path: Path):
        """Reject cache reads when cache access is disabled."""
        with pytest.raises(ColorValueError, match="cache access is disabled"):
            get_palette(
                "tailwind",
                source="cache",
                allow_cache=False,
                cache_dir=tmp_path,
            )

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
        assert palette.as_dict() == {"brand-500": "#112233"}
        assert json.loads((cache_dir / "tailwind-v3.json").read_text()) == {
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
        (cache_dir / "tailwind-v3.json").write_text('{"brand-500": "#112233"}\n')

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
        ).as_dict() == {"brand-500": "#112233"}
        assert (
            get_palette(
                "tailwind",
                source="auto",
                allow_network=True,
                allow_cache=False,
            )["sky-500"]
            == "#0ea5e9"
        )

    def test_tailwind_bundled_defaults_to_v3(self):
        """Default Tailwind load returns the bundled v3 palette."""
        palette = get_palette("tailwind")
        assert palette.version == "v3"
        assert palette["sky-500"] == "#0ea5e9"

    def test_tailwind_version_v3_bundled(self):
        """Explicit Tailwind v3 uses bundled data without network."""
        palette = get_palette("tailwind", version="v3")
        assert palette.version == "v3"
        assert palette.source == "bundled"
        assert palette["sky-500"] == "#0ea5e9"

    def test_tailwind_version_v4_upstream_default_url(self, monkeypatch):
        """Tailwind v4 fetches from the default upstream URL when enabled."""
        called_with: list[str] = []

        def fake_urlopen(url: str, timeout: float):
            called_with.append(url)
            return _FakeResponse({"brand": {"500": "#aabbcc"}})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        palette = get_palette(
            "tailwind",
            version="v4",
            source="api",
            allow_network=True,
        )
        assert palette.version == "v4"
        assert palette.source == "api"
        assert palette["brand-500"] == "#aabbcc"
        assert called_with == [
            "https://raw.githubusercontent.com/tailwindlabs/tailwindcss/"
            "v4.0.0/packages/tailwindcss/theme.css"
        ]

    def test_tailwind_version_v4_upstream_explicit_url(self, monkeypatch):
        """Tailwind v4 upstream URL can be overridden explicitly."""
        called_with: list[str] = []

        def fake_urlopen(url: str, timeout: float):
            called_with.append(url)
            return _FakeResponse({"brand": {"500": "#ddeeff"}})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        palette = get_palette(
            "tailwind",
            version="v4",
            source="api",
            allow_network=True,
            url="https://example.com/tailwind-v4.json",
        )
        assert palette["brand-500"] == "#ddeeff"
        assert called_with == ["https://example.com/tailwind-v4.json"]

    def test_tailwind_bundled_preserves_offline_behavior(self):
        """Default Tailwind load never touches the network."""
        palette = get_palette("tailwind")
        assert palette.source == "bundled"
        assert palette.version == "v3"

    def test_material_v2_bundled_defaults(self):
        """Default Material load returns the bundled v2 palette."""
        palette = get_palette("material")
        assert palette.version == "v2"
        assert palette["blue-600"] == "#1e88e5"

    def test_material_v2_bundled_explicit(self):
        """Explicit Material v2 uses bundled data."""
        palette = get_palette("material", version="v2")
        assert palette.version == "v2"
        assert palette.source == "bundled"

    def test_material_v3_upstream(self, monkeypatch):
        """Material v3 fetches from the default upstream URL when enabled."""
        called_with: list[str] = []

        def fake_urlopen(url: str, timeout: float):
            called_with.append(url)
            return _FakeResponse({"primary": {"500": "#123456"}})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        palette = get_palette(
            "material",
            version="v3",
            source="api",
            allow_network=True,
        )
        assert palette.version == "v3"
        assert palette.source == "api"
        assert palette["primary-500"] == "#123456"
        assert called_with == [
            "https://raw.githubusercontent.com/material-foundation/material-tokens/"
            "main/css/baseline.css"
        ]

    def test_material_version_v3(self, monkeypatch):
        """Material v3 exposes its version and system metadata."""

        def fake_urlopen(_url: str, timeout: float):
            return _FakeResponse({"primary": {"500": "#123456"}})

        monkeypatch.setattr("colorbrew.data.api.urlopen", fake_urlopen)
        palette = get_palette(
            "material",
            version="v3",
            source="api",
            allow_network=True,
        )
        assert palette.version == "v3"
        assert palette.system == "material"

    def test_version_reject_unsupported_tailwind(self):
        """Unsupported Tailwind versions fail before any network access."""
        with pytest.raises(ColorValueError, match="Unsupported palette version"):
            get_palette("tailwind", version="v5", source="api", allow_network=True)

    def test_version_reject_unsupported_material(self):
        """Unsupported Material versions fail before any network access."""
        with pytest.raises(ColorValueError, match="Unsupported palette version"):
            get_palette("material", version="v1", source="api", allow_network=True)

    def test_version_reject_bundled_upstream_only(self):
        """Upstream-only versions fail cleanly when bundled source is requested."""
        with pytest.raises(ColorValueError, match="not available bundled"):
            get_palette("tailwind", version="v4", source="bundled")

    def test_version_parsed_from_palette_name(self):
        """Version can be pinned with system@version syntax."""
        palette = get_palette("tailwind@v3")
        assert palette.version == "v3"
        assert palette.source == "bundled"
