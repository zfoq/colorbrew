"""Tests for colorbrew.naming — reverse color name lookup across palettes."""

from colorbrew.naming import (
    find_closest_material,
    find_closest_name,
    find_closest_tailwind,
)


class TestFindClosestName:
    """Test find_closest_name lookup."""

    def test_exact_red(self):
        """Find exact match for pure red."""
        match = find_closest_name(255, 0, 0)
        assert match.name == "red"
        assert match.hex == "#ff0000"
        assert match.distance == 0.0
        assert match.exact is True

    def test_exact_black(self):
        """Find exact match for black."""
        match = find_closest_name(0, 0, 0)
        assert match.name == "black"
        assert match.exact is True

    def test_exact_white(self):
        """Find exact match for white."""
        match = find_closest_name(255, 255, 255)
        assert match.name == "white"
        assert match.exact is True

    def test_near_match(self):
        """Find a non-exact match with distance > 0."""
        match = find_closest_name(52, 152, 219)
        assert isinstance(match.name, str)
        assert match.distance > 0
        assert match.exact is False

    def test_returns_namedtuple(self):
        """Return a NameMatch with all expected fields."""
        match = find_closest_name(100, 100, 100)
        assert hasattr(match, "name")
        assert hasattr(match, "hex")
        assert hasattr(match, "distance")
        assert hasattr(match, "exact")


class TestFindClosestTailwind:
    """Test find_closest_tailwind lookup."""

    def test_exact_tailwind_red_500(self):
        """Find exact match for Tailwind red-500 (#ef4444)."""
        match = find_closest_tailwind(0xEF, 0x44, 0x44)
        assert match.name == "red-500"
        assert match.exact is True

    def test_exact_tailwind_sky_500(self):
        """Find exact match for Tailwind sky-500 (#0ea5e9)."""
        match = find_closest_tailwind(0x0E, 0xA5, 0xE9)
        assert match.name == "sky-500"
        assert match.exact is True

    def test_near_match(self):
        """Find a non-exact match with distance > 0."""
        match = find_closest_tailwind(52, 152, 219)
        assert isinstance(match.name, str)
        assert match.distance > 0
        assert match.exact is False

    def test_returns_namedtuple(self):
        """Return a NameMatch with all expected fields."""
        match = find_closest_tailwind(100, 100, 100)
        assert hasattr(match, "name")
        assert hasattr(match, "hex")
        assert hasattr(match, "distance")
        assert hasattr(match, "exact")


class TestFindClosestMaterial:
    """Test find_closest_material lookup."""

    def test_exact_material_blue_500(self):
        """Find exact match for Material blue-500 (#2196f3)."""
        match = find_closest_material(0x21, 0x96, 0xF3)
        assert match.name == "blue-500"
        assert match.exact is True

    def test_exact_material_red_500(self):
        """Find exact match for Material red-500 (#f44336)."""
        match = find_closest_material(0xF4, 0x43, 0x36)
        assert match.name == "red-500"
        assert match.exact is True

    def test_near_match(self):
        """Find a non-exact match with distance > 0."""
        match = find_closest_material(52, 152, 219)
        assert isinstance(match.name, str)
        assert match.distance > 0
        assert match.exact is False

    def test_returns_namedtuple(self):
        """Return a NameMatch with all expected fields."""
        match = find_closest_material(100, 100, 100)
        assert hasattr(match, "name")
        assert hasattr(match, "hex")
        assert hasattr(match, "distance")
        assert hasattr(match, "exact")
