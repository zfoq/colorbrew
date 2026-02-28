"""Tests for colorbrew.css_output — CSS/HTML string formatting."""

from colorbrew.css_output import (
    to_css_hex,
    to_css_hsl,
    to_css_hsla,
    to_css_rgb,
    to_css_rgba,
)


class TestToCssRgb:
    """Test to_css_rgb formatting."""

    def test_standard(self):
        """Format a standard RGB value."""
        assert to_css_rgb(52, 152, 219) == "rgb(52, 152, 219)"

    def test_black(self):
        """Format black."""
        assert to_css_rgb(0, 0, 0) == "rgb(0, 0, 0)"

    def test_white(self):
        """Format white."""
        assert to_css_rgb(255, 255, 255) == "rgb(255, 255, 255)"


class TestToCssRgba:
    """Test to_css_rgba formatting."""

    def test_with_alpha(self):
        """Format with a fractional alpha."""
        assert to_css_rgba(52, 152, 219, 0.8) == "rgba(52, 152, 219, 0.8)"

    def test_full_alpha(self):
        """Format with alpha 1.0."""
        assert to_css_rgba(52, 152, 219, 1.0) == "rgba(52, 152, 219, 1.0)"

    def test_zero_alpha(self):
        """Format with alpha 0."""
        assert to_css_rgba(52, 152, 219, 0) == "rgba(52, 152, 219, 0)"


class TestToCssHsl:
    """Test to_css_hsl formatting."""

    def test_red(self):
        """Format pure red as HSL."""
        assert to_css_hsl(255, 0, 0) == "hsl(0, 100%, 50%)"

    def test_black(self):
        """Format black as HSL."""
        assert to_css_hsl(0, 0, 0) == "hsl(0, 0%, 0%)"


class TestToCssHsla:
    """Test to_css_hsla formatting."""

    def test_with_alpha(self):
        """Format with a fractional alpha."""
        result = to_css_hsla(255, 0, 0, 0.5)
        assert result == "hsla(0, 100%, 50%, 0.5)"


class TestToCssHex:
    """Test to_css_hex formatting."""

    def test_standard(self):
        """Format a standard color as hex."""
        assert to_css_hex(52, 152, 219) == "#3498db"

    def test_black(self):
        """Format black as hex."""
        assert to_css_hex(0, 0, 0) == "#000000"
