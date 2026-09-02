"""Tests for the public top-level and data-package exports."""

from __future__ import annotations

from collections.abc import Callable
from typing import NamedTuple

import pytest

import colorbrew
import colorbrew.data


class TestPublicExports:
    """Top-level ``colorbrew`` exports the planned public surface."""

    EXPECTED = {
        "Color",
        "Palette",
        "Theme",
        "Settings",
        "NameMatch",
        "WcagReport",
        "ColorClass",
        "ColorBrewError",
        "ColorParseError",
        "ColorValueError",
        "PaletteError",
        "configure",
        "settings_context",
        "list_systems",
        "get_system",
        "register_system",
        "get_palette",
        "list_palettes",
        "resolve_name",
        "cmyk_to_rgb",
        "hex_to_rgb",
        "hsl_to_rgb",
        "hsv_to_rgb",
        "rgb_to_cmyk",
        "rgb_to_hex",
        "rgb_to_hsl",
        "rgb_to_hsv",
        "lab_to_rgb",
        "rgb_to_lab",
        "delta_e_76",
        "delta_e_2000",
    }

    def test_all_exports_are_present(self):
        """Every planned name appears in ``__all__``."""
        missing = self.EXPECTED - set(colorbrew.__all__)
        assert not missing, f"Missing from __all__: {missing}"

    def test_no_extra_exports_are_present(self):
        """``__all__`` contains exactly the planned names."""
        extra = set(colorbrew.__all__) - self.EXPECTED
        assert not extra, f"Unexpected __all__ entries: {extra}"

    def test_exported_classes_and_functions(self):
        """Exported names have the expected kinds."""
        assert isinstance(colorbrew.Color, type)
        assert isinstance(colorbrew.Palette, type)
        assert isinstance(colorbrew.Theme, type)
        assert isinstance(colorbrew.Settings, type)
        assert isinstance(colorbrew.NameMatch, type)
        assert isinstance(colorbrew.WcagReport, type)
        assert isinstance(colorbrew.ColorClass, type)
        assert issubclass(colorbrew.ColorBrewError, Exception)
        assert issubclass(colorbrew.ColorParseError, Exception)
        assert issubclass(colorbrew.ColorValueError, Exception)
        assert issubclass(colorbrew.PaletteError, Exception)
        assert isinstance(colorbrew.configure, Callable)
        assert isinstance(colorbrew.settings_context, Callable)
        assert isinstance(colorbrew.list_systems, Callable)
        assert isinstance(colorbrew.get_system, Callable)
        assert isinstance(colorbrew.register_system, Callable)
        assert isinstance(colorbrew.get_palette, Callable)
        assert isinstance(colorbrew.list_palettes, Callable)
        assert isinstance(colorbrew.resolve_name, Callable)
        assert isinstance(colorbrew.rgb_to_hex, Callable)

    def test_name_match_is_namedtuple(self):
        """NameMatch remains a lightweight named tuple."""
        assert issubclass(colorbrew.NameMatch, tuple)
        assert hasattr(colorbrew.NameMatch, "_fields")


class TestDataPackageExports:
    """The ``colorbrew.data`` package exposes registry helpers, not stale models."""

    EXPECTED_DATA = {
        "SystemRecord",
        "get_palette",
        "refresh_palette",
        "get_system",
        "list_palettes",
        "list_systems",
        "register_system",
        "resolve_name",
        "MATERIAL_COLORS",
        "NAMED_COLORS",
        "TAILWIND_COLORS",
    }

    def test_data_exports_registry_and_data_functions(self):
        """Required registry/data names are exported."""
        missing = self.EXPECTED_DATA - set(colorbrew.data.__all__)
        assert not missing, f"Missing from colorbrew.data.__all__: {missing}"

    def test_data_does_not_reexport_palette(self):
        """``Palette`` is no longer re-exported from ``colorbrew.data``."""
        assert "Palette" not in colorbrew.data.__all__
        with pytest.raises(AttributeError):
            colorbrew.data.Palette


class TestLegacySurfaceRemoved:
    """Compatibility helpers that conflict with the new model are gone."""

    def test_get_palette_entries_not_exported(self):
        """``get_palette_entries`` is not part of the public surface."""
        assert "get_palette_entries" not in dir(colorbrew)
        assert "get_palette_entries" not in colorbrew.__all__

    def test_legacy_color_naming_constructors_removed(self):
        """Removed Color naming helpers are no longer available."""
        assert not hasattr(colorbrew.Color, "from_name")
        assert not hasattr(colorbrew.Color, "from_tailwind")
        assert not hasattr(colorbrew.Color, "from_material")
        assert not hasattr(colorbrew.Color, "closest_name")
        assert not hasattr(colorbrew.Color, "closest_tailwind")
        assert not hasattr(colorbrew.Color, "closest_material")
        assert not hasattr(colorbrew.Color, "nearest_palette")
