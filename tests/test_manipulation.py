"""Tests for colorbrew.manipulation — color adjustment functions."""

from colorbrew.converters import rgb_to_hsl
from colorbrew.manipulation import (
    darken,
    desaturate,
    gradient,
    grayscale,
    invert,
    lighten,
    mix,
    rotate_hue,
    saturate,
    shade,
    tint,
    tone,
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


class TestDarkenEdgeCases:
    """Test edge cases for darken function."""

    def test_clamps_at_0(self):
        """Darkening past 0% clamps to black."""
        result = darken(10, 10, 10, 100)
        assert rgb_to_hsl(*result)[2] == 0


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


class TestRotateHueEdgeCases:
    """Test edge cases for rotate_hue."""

    def test_negative_rotation(self):
        """Negative degrees wrap correctly."""
        result = rotate_hue(255, 0, 0, -30)
        h, _, _ = rgb_to_hsl(*result)
        assert abs(h - 330) <= 1


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


class TestShade:
    """Test shade function (mix with black)."""

    def test_zero_returns_original(self):
        """Amount 0 returns the original color."""
        assert shade(255, 0, 0, 0.0) == (255, 0, 0)

    def test_one_returns_black(self):
        """Amount 1 returns black."""
        assert shade(255, 0, 0, 1.0) == (0, 0, 0)

    def test_half_shade(self):
        """Amount 0.5 returns halfway to black."""
        assert shade(200, 100, 50, 0.5) == (100, 50, 25)


class TestTint:
    """Test tint function (mix with white)."""

    def test_zero_returns_original(self):
        """Amount 0 returns the original color."""
        assert tint(255, 0, 0, 0.0) == (255, 0, 0)

    def test_one_returns_white(self):
        """Amount 1 returns white."""
        assert tint(255, 0, 0, 1.0) == (255, 255, 255)

    def test_half_tint(self):
        """Amount 0.5 returns halfway to white."""
        result = tint(0, 0, 0, 0.5)
        assert result == (128, 128, 128)


class TestTone:
    """Test tone function (mix with gray)."""

    def test_zero_returns_original(self):
        """Amount 0 returns the original color."""
        assert tone(255, 0, 0, 0.0) == (255, 0, 0)

    def test_one_returns_gray(self):
        """Amount 1 returns gray."""
        assert tone(255, 0, 0, 1.0) == (128, 128, 128)

    def test_half_tone(self):
        """Amount 0.5 moves halfway to gray."""
        result = tone(200, 100, 0, 0.5)
        assert result == (164, 114, 64)


class TestGradient:
    """Test gradient function."""

    def test_step_count(self):
        """Gradient returns the requested number of steps."""
        result = gradient((0, 0, 0), (255, 255, 255), 5)
        assert len(result) == 5

    def test_endpoints(self):
        """First and last colors match the inputs."""
        result = gradient((0, 0, 0), (255, 255, 255), 5)
        assert result[0] == (0, 0, 0)
        assert result[-1] == (255, 255, 255)

    def test_midpoint(self):
        """Midpoint of black to white is gray."""
        result = gradient((0, 0, 0), (255, 255, 255), 3)
        assert result[1] == (128, 128, 128)

    def test_two_steps(self):
        """Two steps returns just the endpoints."""
        result = gradient((0, 0, 0), (255, 255, 255), 2)
        assert result == [(0, 0, 0), (255, 255, 255)]

    def test_single_step(self):
        """Single step returns just the first color."""
        result = gradient((0, 0, 0), (255, 255, 255), 1)
        assert result == [(0, 0, 0)]
