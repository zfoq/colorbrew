"""Tests for colorbrew.palettes — palette generation algorithms."""

from colorbrew.converters import rgb_to_hsl
from colorbrew.palettes import (
    analogous,
    complementary,
    split_complementary,
    tetradic,
    triadic,
)


class TestComplementary:
    """Test complementary color generation."""

    def test_hue_offset(self):
        """Complement has hue shifted by 180 degrees."""
        h_orig, _s, _l = rgb_to_hsl(255, 0, 0)
        result = complementary(255, 0, 0)
        h_comp, _, _ = rgb_to_hsl(*result)
        assert abs(h_comp - (h_orig + 180) % 360) <= 1

    def test_preserves_saturation_and_lightness(self):
        """Complement preserves saturation and lightness."""
        _, s_orig, l_orig = rgb_to_hsl(52, 152, 219)
        result = complementary(52, 152, 219)
        _, s_comp, l_comp = rgb_to_hsl(*result)
        assert abs(s_orig - s_comp) <= 1
        assert abs(l_orig - l_comp) <= 1


class TestAnalogous:
    """Test analogous palette generation."""

    def test_default_count(self):
        """Return 3 colors by default."""
        colors = analogous(52, 152, 219)
        assert len(colors) == 3

    def test_custom_count(self):
        """Return the requested number of colors."""
        colors = analogous(52, 152, 219, n=5)
        assert len(colors) == 5

    def test_valid_rgb_values(self):
        """All returned colors have valid RGB values."""
        colors = analogous(52, 152, 219)
        for r, g, b in colors:
            assert 0 <= r <= 255
            assert 0 <= g <= 255
            assert 0 <= b <= 255


class TestTriadic:
    """Test triadic palette generation."""

    def test_returns_two(self):
        """Return exactly 2 colors."""
        colors = triadic(52, 152, 219)
        assert len(colors) == 2

    def test_hue_spacing(self):
        """Triadic colors are roughly 120 degrees apart."""
        h_orig = rgb_to_hsl(255, 0, 0)[0]
        colors = triadic(255, 0, 0)
        h1 = rgb_to_hsl(*colors[0])[0]
        h2 = rgb_to_hsl(*colors[1])[0]
        assert abs(h1 - (h_orig + 120) % 360) <= 1
        assert abs(h2 - (h_orig + 240) % 360) <= 1


class TestSplitComplementary:
    """Test split-complementary palette generation."""

    def test_returns_two(self):
        """Return exactly 2 colors."""
        colors = split_complementary(52, 152, 219)
        assert len(colors) == 2


class TestTetradic:
    """Test tetradic palette generation."""

    def test_returns_three(self):
        """Return exactly 3 colors."""
        colors = tetradic(52, 152, 219)
        assert len(colors) == 3
