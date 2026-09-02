"""Tests for colorbrew.parsing — input normalization and validation."""

import pytest

from colorbrew.conversion.parsing import (
    parse_rgb_args,
    parse_string,
    parse_string_with_alpha,
)
from colorbrew.exceptions import ColorParseError, ColorValueError


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


class TestParseStringHslValidation:
    """Test HSL value validation in hsl() parsing."""

    def test_hue_out_of_range(self):
        """Raise ColorValueError for hue above 360."""
        with pytest.raises(ColorValueError, match="Hue must be 0-360"):
            parse_string("hsl(999, 50%, 50%)")

    def test_saturation_out_of_range(self):
        """Raise ColorValueError for saturation above 100."""
        with pytest.raises(ColorValueError, match="Saturation must be 0-100"):
            parse_string("hsl(180, 200, 50)")

    def test_lightness_out_of_range(self):
        """Raise ColorValueError for lightness above 100."""
        with pytest.raises(ColorValueError, match="Lightness must be 0-100"):
            parse_string("hsl(180, 50, 150)")


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


class TestParseStringAlpha:
    """Test alpha parsing from strings."""

    def test_hex_8digit(self):
        """8-digit hex includes alpha."""
        rgb, alpha = parse_string_with_alpha("#3498db80")
        assert rgb == (52, 152, 219)
        assert abs(alpha - 128 / 255) < 0.01

    def test_hex_4digit(self):
        """4-digit hex includes alpha."""
        rgb, alpha = parse_string_with_alpha("#f008")
        assert rgb == (255, 0, 0)
        assert abs(alpha - 136 / 255) < 0.01

    def test_rgb_legacy(self):
        """Legacy rgba() parses alpha."""
        rgb, alpha = parse_string_with_alpha("rgba(52, 152, 219, 0.5)")
        assert rgb == (52, 152, 219)
        assert alpha == 0.5

    def test_rgb_modern_slash_alpha(self):
        """Modern rgb() with slash alpha."""
        rgb, alpha = parse_string_with_alpha("rgb(52 152 219 / 0.5)")
        assert rgb == (52, 152, 219)
        assert alpha == 0.5

    def test_rgb_modern_percent_alpha(self):
        """Modern rgb() with percent alpha."""
        rgb, alpha = parse_string_with_alpha("rgb(52 152 219 / 50%)")
        assert rgb == (52, 152, 219)
        assert alpha == 0.5

    def test_hsla_legacy(self):
        """Legacy hsla() parses alpha."""
        rgb, alpha = parse_string_with_alpha("hsla(204, 70%, 53%, 0.3)")
        assert rgb == (51, 152, 219)
        assert alpha == 0.3

    def test_hsl_modern_with_alpha(self):
        """Modern hsl() with slash alpha."""
        rgb, alpha = parse_string_with_alpha("hsl(204 70% 53% / 0.7)")
        assert rgb == (51, 152, 219)
        assert alpha == pytest.approx(0.7)


class TestParseStringModernCss:
    """Test modern CSS Color Level 4 syntax support."""

    def test_rgb_space_separated(self):
        """Space-separated rgb() is parsed."""
        assert parse_string("rgb(52 152 219)") == (52, 152, 219)

    def test_rgb_space_with_slash_alpha(self):
        """Space-separated rgb() with slash alpha discards alpha."""
        assert parse_string("rgb(52 152 219 / 0.5)") == (52, 152, 219)

    def test_hsl_deg_unit(self):
        """hsl() with deg unit."""
        assert parse_string("hsl(204deg 70% 53%)") == (51, 152, 219)

    def test_hsl_space_no_deg(self):
        """hsl() with space-separated, no deg unit."""
        assert parse_string("hsl(204 70% 53%)") == (51, 152, 219)

    def test_hsl_space_with_alpha(self):
        """hsl() with space-separated and slash alpha."""
        assert parse_string("hsl(204deg 70% 53% / 0.7)") == (51, 152, 219)
