"""Tests for colorbrew.parsing — input normalization and validation."""

import pytest

from colorbrew.exceptions import ColorParseError, ColorValueError
from colorbrew.parsing import parse_rgb_args, parse_string


class TestParseStringHex:
    """Test parsing hex color strings."""

    def test_standard_hex(self):
        """Parse a standard 6-digit hex with hash."""
        assert parse_string("#3498db") == (52, 152, 219)

    def test_short_hex(self):
        """Parse a 3-digit shorthand hex."""
        assert parse_string("#fff") == (255, 255, 255)

    def test_no_hash(self):
        """Parse hex without leading hash."""
        assert parse_string("3498db") == (52, 152, 219)

    def test_uppercase_hex(self):
        """Parse uppercase hex digits."""
        assert parse_string("#FF0000") == (255, 0, 0)

    def test_invalid_hex_raises(self):
        """Raise ColorParseError for non-hex characters."""
        with pytest.raises(ColorParseError):
            parse_string("#xyz")


class TestParseStringRgbFunc:
    """Test parsing CSS rgb() function strings."""

    def test_standard_rgb(self):
        """Parse a standard rgb() string."""
        assert parse_string("rgb(52, 152, 219)") == (52, 152, 219)

    def test_rgb_no_spaces(self):
        """Parse rgb() with minimal whitespace."""
        assert parse_string("rgb(0,0,0)") == (0, 0, 0)

    def test_rgb_extra_spaces(self):
        """Parse rgb() with extra spaces."""
        assert parse_string("rgb( 255 , 255 , 255 )") == (255, 255, 255)


class TestParseStringHslFunc:
    """Test parsing CSS hsl() function strings."""

    def test_standard_hsl(self):
        """Parse a standard hsl() string."""
        result = parse_string("hsl(0, 100%, 50%)")
        assert result == (255, 0, 0)

    def test_hsl_without_percent(self):
        """Parse hsl() without percent signs."""
        result = parse_string("hsl(0, 100, 50)")
        assert result == (255, 0, 0)


class TestParseStringNamedColor:
    """Test parsing CSS named color strings."""

    def test_named_color(self):
        """Parse a named color."""
        assert parse_string("red") == (255, 0, 0)

    def test_named_color_case_insensitive(self):
        """Parse named colors case-insensitively."""
        assert parse_string("CornflowerBlue") == (100, 149, 237)

    def test_named_color_with_whitespace(self):
        """Parse named color with surrounding whitespace."""
        assert parse_string("  red  ") == (255, 0, 0)

    def test_unknown_name_raises(self):
        """Raise ColorParseError for unknown color names."""
        with pytest.raises(ColorParseError):
            parse_string("notacolor")


class TestParseRgbArgs:
    """Test parse_rgb_args validation."""

    def test_valid_values(self):
        """Accept valid 0-255 integer values."""
        assert parse_rgb_args(0, 128, 255) == (0, 128, 255)

    def test_negative_raises(self):
        """Raise ColorValueError for negative values."""
        with pytest.raises(ColorValueError):
            parse_rgb_args(-1, 0, 0)

    def test_over_255_raises(self):
        """Raise ColorValueError for values above 255."""
        with pytest.raises(ColorValueError):
            parse_rgb_args(256, 0, 0)

    def test_float_raises(self):
        """Raise ColorValueError for float values."""
        with pytest.raises(ColorValueError):
            parse_rgb_args(1.5, 0, 0)  # type: ignore[arg-type]

    def test_bool_raises(self):
        """Raise ColorValueError for boolean values."""
        with pytest.raises(ColorValueError):
            parse_rgb_args(True, 0, 0)  # type: ignore[arg-type]
