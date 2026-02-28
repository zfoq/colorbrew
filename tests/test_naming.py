"""Tests for colorbrew.naming — reverse CSS color name lookup."""

from colorbrew.naming import find_closest_name


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
