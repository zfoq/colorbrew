"""Tests for colorbrew.manipulation — color adjustment functions."""

from colorbrew.converters import rgb_to_hsl
from colorbrew.manipulation import (
    darken,
    desaturate,
    grayscale,
    invert,
    lighten,
    mix,
    rotate_hue,
    saturate,
)


class TestLighten:
    """Test lighten function."""

    def test_increases_lightness(self):
        """Lighten increases the L component."""
        original = rgb_to_hsl(52, 152, 219)
        result_rgb = lighten(52, 152, 219, 20)
        result_hsl = rgb_to_hsl(*result_rgb)
        assert result_hsl[2] > original[2]

    def test_white_stays_white(self):
        """Lightening white stays white."""
        result = lighten(255, 255, 255, 20)
        assert result == (255, 255, 255)

    def test_clamps_at_100(self):
        """Lightening past 100% clamps to white."""
        result = lighten(200, 200, 200, 100)
        assert rgb_to_hsl(*result)[2] == 100


class TestDarken:
    """Test darken function."""

    def test_decreases_lightness(self):
        """Darken decreases the L component."""
        original = rgb_to_hsl(52, 152, 219)
        result_rgb = darken(52, 152, 219, 20)
        result_hsl = rgb_to_hsl(*result_rgb)
        assert result_hsl[2] < original[2]

    def test_black_stays_black(self):
        """Darkening black stays black."""
        result = darken(0, 0, 0, 20)
        assert result == (0, 0, 0)


class TestSaturate:
    """Test saturate function."""

    def test_increases_saturation(self):
        """Saturate increases the S component."""
        # Use a color with room to increase saturation
        original = rgb_to_hsl(100, 120, 140)
        result_rgb = saturate(100, 120, 140, 20)
        result_hsl = rgb_to_hsl(*result_rgb)
        assert result_hsl[1] >= original[1]


class TestDesaturate:
    """Test desaturate function."""

    def test_decreases_saturation(self):
        """Desaturate decreases the S component."""
        original = rgb_to_hsl(255, 0, 0)
        result_rgb = desaturate(255, 0, 0, 20)
        result_hsl = rgb_to_hsl(*result_rgb)
        assert result_hsl[1] <= original[1]


class TestRotateHue:
    """Test rotate_hue function."""

    def test_180_degree_rotation(self):
        """Rotate hue by 180 degrees produces complement."""
        h_orig, _s, _l = rgb_to_hsl(255, 0, 0)
        result_rgb = rotate_hue(255, 0, 0, 180)
        h_new, _, _ = rgb_to_hsl(*result_rgb)
        assert abs(h_new - (h_orig + 180) % 360) <= 1

    def test_360_degree_returns_same(self):
        """Rotate by 360 degrees returns the same color."""
        result = rotate_hue(52, 152, 219, 360)
        for orig, rotated in zip((52, 152, 219), result):
            assert abs(orig - rotated) <= 1


class TestInvert:
    """Test invert function."""

    def test_black_to_white(self):
        """Invert black to white."""
        assert invert(0, 0, 0) == (255, 255, 255)

    def test_white_to_black(self):
        """Invert white to black."""
        assert invert(255, 255, 255) == (0, 0, 0)

    def test_specific_value(self):
        """Invert a specific color."""
        assert invert(52, 152, 219) == (203, 103, 36)


class TestGrayscale:
    """Test grayscale function."""

    def test_removes_saturation(self):
        """Grayscale sets saturation to 0."""
        result = grayscale(255, 0, 0)
        _, s, _ = rgb_to_hsl(*result)
        assert s == 0

    def test_gray_unchanged(self):
        """Gray values stay the same."""
        result = grayscale(128, 128, 128)
        assert result == (128, 128, 128)


class TestMix:
    """Test mix function."""

    def test_equal_mix(self):
        """Mix two colors equally."""
        result = mix((0, 0, 0), (255, 255, 255), 0.5)
        assert result == (128, 128, 128)

    def test_weight_zero(self):
        """Weight 0.0 returns the first color."""
        result = mix((100, 100, 100), (200, 200, 200), 0.0)
        assert result == (100, 100, 100)

    def test_weight_one(self):
        """Weight 1.0 returns the second color."""
        result = mix((100, 100, 100), (200, 200, 200), 1.0)
        assert result == (200, 200, 200)

    def test_mix_with_self(self):
        """Mixing a color with itself returns the same color."""
        result = mix((52, 152, 219), (52, 152, 219), 0.5)
        assert result == (52, 152, 219)
