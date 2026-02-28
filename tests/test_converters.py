"""Tests for colorbrew.converters — pure color-format conversion functions."""

import pytest

from colorbrew.converters import (
    cmyk_to_rgb,
    hex_to_rgb,
    hsl_to_rgb,
    rgb_to_cmyk,
    rgb_to_hex,
    rgb_to_hsl,
)


class TestHexToRgb:
    """Test hex_to_rgb conversion."""

    @pytest.mark.parametrize(
        "hex_val,expected",
        [
            ("#000000", (0, 0, 0)),
            ("#ffffff", (255, 255, 255)),
            ("#ff0000", (255, 0, 0)),
            ("#00ff00", (0, 255, 0)),
            ("#0000ff", (0, 0, 255)),
            ("#3498db", (52, 152, 219)),
        ],
    )
    def test_standard_hex(self, hex_val, expected):
        """Convert standard 6-digit hex values."""
        assert hex_to_rgb(hex_val) == expected

    def test_short_hex(self):
        """Expand 3-digit shorthand hex."""
        assert hex_to_rgb("#fff") == (255, 255, 255)
        assert hex_to_rgb("#000") == (0, 0, 0)
        assert hex_to_rgb("#f00") == (255, 0, 0)

    def test_no_hash(self):
        """Accept hex without leading hash."""
        assert hex_to_rgb("3498db") == (52, 152, 219)

    def test_uppercase(self):
        """Accept uppercase hex digits."""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)


class TestRgbToHex:
    """Test rgb_to_hex conversion."""

    @pytest.mark.parametrize(
        "rgb,expected",
        [
            ((0, 0, 0), "#000000"),
            ((255, 255, 255), "#ffffff"),
            ((255, 0, 0), "#ff0000"),
            ((52, 152, 219), "#3498db"),
        ],
    )
    def test_known_values(self, rgb, expected):
        """Convert known RGB values to hex."""
        assert rgb_to_hex(*rgb) == expected


class TestRgbToHsl:
    """Test rgb_to_hsl conversion."""

    def test_black(self):
        """Convert black to HSL."""
        assert rgb_to_hsl(0, 0, 0) == (0, 0, 0)

    def test_white(self):
        """Convert white to HSL."""
        assert rgb_to_hsl(255, 255, 255) == (0, 0, 100)

    def test_pure_red(self):
        """Convert pure red to HSL."""
        assert rgb_to_hsl(255, 0, 0) == (0, 100, 50)

    def test_pure_green(self):
        """Convert pure green to HSL."""
        assert rgb_to_hsl(0, 255, 0) == (120, 100, 50)

    def test_pure_blue(self):
        """Convert pure blue to HSL."""
        assert rgb_to_hsl(0, 0, 255) == (240, 100, 50)

    def test_mid_gray(self):
        """Convert mid gray to HSL."""
        _h, s, lit = rgb_to_hsl(128, 128, 128)
        assert s == 0
        assert lit == 50


class TestHslToRgb:
    """Test hsl_to_rgb conversion."""

    def test_black(self) -> None:
        """Convert HSL black to RGB."""
        assert hsl_to_rgb(0, 0, 0) == (0, 0, 0)

    def test_white(self):
        """Convert HSL white to RGB."""
        assert hsl_to_rgb(0, 0, 100) == (255, 255, 255)

    def test_pure_red(self):
        """Convert HSL pure red to RGB."""
        assert hsl_to_rgb(0, 100, 50) == (255, 0, 0)

    def test_pure_green(self):
        """Convert HSL pure green to RGB."""
        assert hsl_to_rgb(120, 100, 50) == (0, 255, 0)

    def test_pure_blue(self):
        """Convert HSL pure blue to RGB."""
        assert hsl_to_rgb(240, 100, 50) == (0, 0, 255)

    def test_gray(self):
        """Convert achromatic HSL to gray."""
        r, g, b = hsl_to_rgb(0, 0, 50)
        assert r == g == b == 128


class TestHslToRgbEdgeCases:
    """Test edge cases for hsl_to_rgb."""

    def test_hue_360(self):
        """Hue 360 produces the same result as hue 0 (red)."""
        assert hsl_to_rgb(360, 100, 50) == (255, 0, 0)

    def test_hue_360_equals_hue_0(self):
        """Hue 360 and hue 0 are equivalent."""
        assert hsl_to_rgb(360, 100, 50) == hsl_to_rgb(0, 100, 50)


class TestRgbToHslRoundTrip:
    """Test that rgb -> hsl -> rgb is stable for key values."""

    @pytest.mark.parametrize(
        "rgb",
        [
            (0, 0, 0),
            (255, 255, 255),
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (128, 128, 128),
        ],
    )
    def test_round_trip(self, rgb):
        """Verify round-trip conversion stability."""
        h, s, lit = rgb_to_hsl(*rgb)
        result = hsl_to_rgb(h, s, lit)
        for orig, conv in zip(rgb, result):
            assert abs(orig - conv) <= 1


class TestRgbToCmyk:
    """Test rgb_to_cmyk conversion."""

    def test_black(self):
        """Convert black to CMYK."""
        assert rgb_to_cmyk(0, 0, 0) == (0, 0, 0, 100)

    def test_white(self):
        """Convert white to CMYK."""
        assert rgb_to_cmyk(255, 255, 255) == (0, 0, 0, 0)

    def test_pure_red(self):
        """Convert pure red to CMYK."""
        assert rgb_to_cmyk(255, 0, 0) == (0, 100, 100, 0)


class TestCmykToRgb:
    """Test cmyk_to_rgb conversion."""

    def test_black(self):
        """Convert CMYK black to RGB."""
        assert cmyk_to_rgb(0, 0, 0, 100) == (0, 0, 0)

    def test_white(self):
        """Convert CMYK white to RGB."""
        assert cmyk_to_rgb(0, 0, 0, 0) == (255, 255, 255)

    def test_pure_red(self):
        """Convert CMYK pure red to RGB."""
        assert cmyk_to_rgb(0, 100, 100, 0) == (255, 0, 0)
