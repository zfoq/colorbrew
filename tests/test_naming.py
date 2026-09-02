"""Tests for colorbrew.naming — reverse color name lookup across palettes."""

import pytest

from colorbrew.analysis.naming import (
    find_closest,
    find_closest_in_palette,
)


class TestFindClosestInPalette:
    """Test find_closest_in_palette lookup."""

    def test_exact_match(self):
        """Find an exact match in a custom palette."""
        palette = {"brand": "#3498db", "accent": "#e74c3c"}
        match = find_closest_in_palette(0x34, 0x98, 0xDB, palette)
        assert match.name == "brand"
        assert match.hex == "#3498db"
        assert match.distance == 0.0
        assert match.exact is True

    def test_accepts_palette_object(self):
        """Find an exact match when a Palette object is passed."""
        from colorbrew.data import get_palette

        palette = get_palette("tailwind")
        match = find_closest_in_palette(0x0E, 0xA5, 0xE9, palette)
        assert match.name == "sky-500"
        assert match.exact is True


class TestFindClosest:
    """Test registry-aware find_closest lookup."""

    def test_exact_css_red(self):
        """Find exact match for pure red in CSS system."""
        match = find_closest(255, 0, 0, system="css")
        assert match.name == "red"
        assert match.hex == "#ff0000"
        assert match.distance == 0.0
        assert match.exact is True

    def test_exact_tailwind_sky_500(self):
        """Find exact match for Tailwind sky-500."""
        match = find_closest(0x0E, 0xA5, 0xE9, system="tailwind")
        assert match.name == "sky-500"
        assert match.exact is True

    def test_exact_material_blue_500(self):
        """Find exact match for Material blue-500."""
        match = find_closest(0x21, 0x96, 0xF3, system="material")
        assert match.name == "blue-500"
        assert match.exact is True

    def test_near_match(self):
        """Find a non-exact match with distance > 0."""
        match = find_closest(52, 152, 219, system="css")
        assert isinstance(match.name, str)
        assert match.distance > 0
        assert match.exact is False

    def test_returns_namedtuple(self):
        """Return a NameMatch with all expected fields."""
        match = find_closest(100, 100, 100, system="css")
        assert hasattr(match, "name")
        assert hasattr(match, "hex")
        assert hasattr(match, "distance")
        assert hasattr(match, "exact")

    def test_unknown_system_raises(self):
        """Raise for an unregistered system name."""
        with pytest.raises(Exception):  # ColorValueError from registry
            find_closest(0, 0, 0, system="notasystem")
