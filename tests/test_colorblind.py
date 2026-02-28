"""Tests for colorbrew.colorblind — color vision deficiency simulation."""

import pytest

from colorbrew.colorblind import simulate


class TestSimulateProtanopia:
    """Test protanopia (red-blind) simulation."""

    def test_red_loses_red(self):
        """Red appears much less red to someone with protanopia."""
        r, _g, _b = simulate(255, 0, 0, "protanopia")
        assert r < 130

    def test_blue_preserved(self):
        """Blue is largely preserved in protanopia."""
        r, g, b = simulate(0, 0, 255, "protanopia")
        assert b > 200

    def test_black_unchanged(self):
        """Black stays black."""
        assert simulate(0, 0, 0, "protanopia") == (0, 0, 0)

    def test_white_unchanged(self):
        """White stays white."""
        assert simulate(255, 255, 255, "protanopia") == (255, 255, 255)


class TestSimulateDeuteranopia:
    """Test deuteranopia (green-blind) simulation."""

    def test_green_shifts(self):
        """Pure green shifts significantly."""
        _r, g, _b = simulate(0, 255, 0, "deuteranopia")
        assert g < 255

    def test_blue_preserved(self):
        """Blue is largely preserved in deuteranopia."""
        r, g, b = simulate(0, 0, 255, "deuteranopia")
        assert b > 200

    def test_black_unchanged(self):
        """Black stays black."""
        assert simulate(0, 0, 0, "deuteranopia") == (0, 0, 0)


class TestSimulateTritanopia:
    """Test tritanopia (blue-blind) simulation."""

    def test_blue_shifts(self):
        """Pure blue shifts significantly."""
        _r, _g, b = simulate(0, 0, 255, "tritanopia")
        assert b < 100

    def test_red_preserved(self):
        """Red is largely preserved in tritanopia."""
        r, _g, _b = simulate(255, 0, 0, "tritanopia")
        assert r > 200

    def test_black_unchanged(self):
        """Black stays black."""
        assert simulate(0, 0, 0, "tritanopia") == (0, 0, 0)


class TestSimulateGrayscale:
    """Test that achromatic colors are stable across all deficiencies."""

    @pytest.mark.parametrize("deficiency", ["protanopia", "deuteranopia", "tritanopia"])
    def test_gray_stable(self, deficiency):
        """Mid-gray should be nearly unchanged."""
        result = simulate(128, 128, 128, deficiency)
        for channel in result:
            assert abs(channel - 128) <= 2


class TestSimulateInvalidMode:
    """Test error handling for unknown deficiency types."""

    def test_unknown_raises(self):
        """Raise ValueError for an unknown deficiency type."""
        with pytest.raises(ValueError, match="Unknown deficiency"):
            simulate(255, 0, 0, "invalid")
