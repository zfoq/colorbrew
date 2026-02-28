"""Tests for colorbrew.blending — Photoshop-style blend modes."""

import pytest

from colorbrew.blending import blend


class TestBlendMultiply:
    """Test multiply blend mode."""

    def test_white_times_any(self):
        """White multiplied by any color equals that color."""
        result = blend((255, 255, 255), (52, 152, 219), mode="multiply")
        assert result == (52, 152, 219)

    def test_black_times_any(self):
        """Black multiplied by any color equals black."""
        result = blend((0, 0, 0), (52, 152, 219), mode="multiply")
        assert result == (0, 0, 0)

    def test_color_with_self(self):
        """Multiply a color with itself darkens it."""
        base = (128, 128, 128)
        result = blend(base, base, mode="multiply")
        assert all(r <= b for r, b in zip(result, base))


class TestBlendScreen:
    """Test screen blend mode."""

    def test_black_screen_any(self):
        """Screen with black returns the other color."""
        result = blend((0, 0, 0), (52, 152, 219), mode="screen")
        assert result == (52, 152, 219)

    def test_white_screen_any(self):
        """Screen with white returns white."""
        result = blend((255, 255, 255), (52, 152, 219), mode="screen")
        assert result == (255, 255, 255)


class TestBlendOverlay:
    """Test overlay blend mode."""

    def test_returns_valid_rgb(self):
        """Overlay returns values in 0-255 range."""
        result = blend((100, 150, 200), (50, 100, 150), mode="overlay")
        assert all(0 <= v <= 255 for v in result)


class TestBlendSoftLight:
    """Test soft_light blend mode."""

    def test_returns_valid_rgb(self):
        """Soft light returns values in 0-255 range."""
        result = blend((100, 150, 200), (50, 100, 150), mode="soft_light")
        assert all(0 <= v <= 255 for v in result)


class TestBlendHardLight:
    """Test hard_light blend mode."""

    def test_returns_valid_rgb(self):
        """Hard light returns values in 0-255 range."""
        result = blend((100, 150, 200), (50, 100, 150), mode="hard_light")
        assert all(0 <= v <= 255 for v in result)


class TestBlendDifference:
    """Test difference blend mode."""

    def test_same_color(self):
        """Difference of same color is black."""
        result = blend((52, 152, 219), (52, 152, 219), mode="difference")
        assert result == (0, 0, 0)

    def test_with_black(self):
        """Difference with black returns the original."""
        result = blend((52, 152, 219), (0, 0, 0), mode="difference")
        assert result == (52, 152, 219)


class TestBlendInvalidMode:
    """Test error handling for unknown blend modes."""

    def test_unknown_mode_raises(self):
        """Raise ValueError for an unknown blend mode."""
        with pytest.raises(ValueError, match="Unknown blend mode"):
            blend((0, 0, 0), (255, 255, 255), mode="invalid")
