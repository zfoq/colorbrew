"""Tests for colorbrew.color — the core Color class."""

import pytest

from colorbrew import Color
from colorbrew.exceptions import ColorParseError, ColorValueError


class TestColorFromHex:
    """Test Color construction from hex strings."""

    def test_standard_hex(self):
        """Accept a standard 6-digit hex with hash prefix."""
        c = Color("#3498db")
        assert c.rgb == (52, 152, 219)

    def test_short_hex(self):
        """Expand a 3-digit shorthand hex to full 6 digits."""
        c = Color("#fff")
        assert c.rgb == (255, 255, 255)

    def test_no_hash(self):
        """Accept hex without the leading hash character."""
        c = Color("3498db")
        assert c.hex == "#3498db"

    def test_invalid_hex_raises(self):
        """Raise ColorParseError for non-hex characters."""
        with pytest.raises(ColorParseError):
            Color("#xyz")

    @pytest.mark.parametrize(
        "hex_val,expected",
        [
            ("#000000", (0, 0, 0)),
            ("#ffffff", (255, 255, 255)),
            ("#ff0000", (255, 0, 0)),
        ],
    )
    def test_known_values(self, hex_val, expected):
        """Verify conversion for well-known color values."""
        assert Color(hex_val).rgb == expected


class TestColorFromRgb:
    """Test Color construction from RGB integers."""

    def test_standard_rgb(self):
        """Accept three valid integers."""
        c = Color(52, 152, 219)
        assert c.rgb == (52, 152, 219)

    def test_out_of_range_raises(self):
        """Raise ColorValueError for values outside 0-255."""
        with pytest.raises(ColorValueError):
            Color(256, 0, 0)

    def test_negative_raises(self):
        """Raise ColorValueError for negative values."""
        with pytest.raises(ColorValueError):
            Color(-1, 0, 0)

    def test_single_int_raises(self):
        """Raise ColorValueError for a single integer."""
        with pytest.raises(ColorValueError):
            Color(42)


class TestColorFromHsl:
    """Test Color.from_hsl class method."""

    def test_red(self):
        """Create red from HSL."""
        c = Color.from_hsl(0, 100, 50)
        assert c.rgb == (255, 0, 0)

    def test_green(self):
        """Create green from HSL."""
        c = Color.from_hsl(120, 100, 50)
        assert c.rgb == (0, 255, 0)


class TestColorFromCmyk:
    """Test Color.from_cmyk class method."""

    def test_white(self):
        """Create white from CMYK."""
        c = Color.from_cmyk(0, 0, 0, 0)
        assert c.rgb == (255, 255, 255)

    def test_black(self):
        """Create black from CMYK."""
        c = Color.from_cmyk(0, 0, 0, 100)
        assert c.rgb == (0, 0, 0)


class TestColorFromName:
    """Test Color.from_name class method."""

    def test_known_name(self):
        """Create color from a known CSS name."""
        c = Color.from_name("cornflowerblue")
        assert c.hex == "#6495ed"

    def test_case_insensitive(self):
        """Accept case-insensitive names."""
        c = Color.from_name("CornflowerBlue")
        assert c.hex == "#6495ed"

    def test_unknown_raises(self):
        """Raise ColorParseError for unknown names."""
        with pytest.raises(ColorParseError):
            Color.from_name("notacolor")


class TestColorRandom:
    """Test Color.random class method."""

    def test_returns_color(self):
        """Return a Color instance."""
        c = Color.random()
        assert isinstance(c, Color)

    def test_valid_rgb_range(self):
        """Generate values within 0-255."""
        c = Color.random()
        assert all(0 <= v <= 255 for v in c.rgb)


class TestColorProperties:
    """Test read-only properties on Color."""

    def test_r_g_b(self):
        """Access individual channels."""
        c = Color(52, 152, 219)
        assert c.r == 52
        assert c.g == 152
        assert c.b == 219

    def test_hex(self):
        """Get hex representation."""
        assert Color(52, 152, 219).hex == "#3498db"

    def test_hsl(self):
        """Get HSL tuple."""
        c = Color(255, 0, 0)
        assert c.hsl == (0, 100, 50)

    def test_cmyk(self):
        """Get CMYK tuple."""
        c = Color(255, 0, 0)
        assert c.cmyk == (0, 100, 100, 0)


class TestColorNamedString:
    """Test Color from named color strings via constructor."""

    def test_named_red(self):
        """Create red from string 'red'."""
        assert Color("red") == Color("#ff0000")

    def test_named_cornflowerblue(self):
        """Create cornflowerblue from string."""
        assert Color("cornflowerblue") == Color("#6495ed")


class TestColorCssString:
    """Test Color from CSS function strings."""

    def test_rgb_function(self):
        """Parse an rgb() string."""
        c = Color("rgb(52, 152, 219)")
        assert c.rgb == (52, 152, 219)

    def test_hsl_function(self):
        """Parse an hsl() string."""
        c = Color("hsl(0, 100%, 50%)")
        assert c.rgb == (255, 0, 0)


class TestColorDunder:
    """Test dunder/magic methods."""

    def test_repr(self):
        """Return repr like Color('#3498db')."""
        c = Color(52, 152, 219)
        assert repr(c) == "Color('#3498db')"

    def test_str(self):
        """Return hex string."""
        c = Color(52, 152, 219)
        assert str(c) == "#3498db"

    def test_eq(self):
        """Compare colors by RGB."""
        assert Color("#ff0000") == Color(255, 0, 0)

    def test_neq(self):
        """Detect different colors."""
        assert Color("#ff0000") != Color("#0000ff")

    def test_eq_non_color(self):
        """Return NotImplemented for non-Color comparison."""
        assert Color("#ff0000") != "not a color"

    def test_hash(self):
        """Equal colors have the same hash."""
        c1 = Color("#ff0000")
        c2 = Color(255, 0, 0)
        assert hash(c1) == hash(c2)

    def test_hash_set(self):
        """Colors can be used in sets."""
        s = {Color("#ff0000"), Color(255, 0, 0)}
        assert len(s) == 1

    def test_iter(self):
        """Iterate yields r, g, b."""
        r, g, b = Color(52, 152, 219)
        assert (r, g, b) == (52, 152, 219)

    def test_format_hex(self):
        """Format with 'hex' spec."""
        c = Color(52, 152, 219)
        assert f"{c:hex}" == "#3498db"

    def test_format_rgb(self):
        """Format with 'rgb' spec."""
        c = Color(52, 152, 219)
        assert f"{c:rgb}" == "rgb(52, 152, 219)"

    def test_format_hsl(self):
        """Format with 'hsl' spec."""
        c = Color(255, 0, 0)
        assert f"{c:hsl}" == "hsl(0, 100%, 50%)"

    def test_format_default(self):
        """Default format returns hex."""
        c = Color(52, 152, 219)
        assert f"{c}" == "#3498db"

    def test_format_invalid_raises(self):
        """Raise ValueError for unknown format spec."""
        with pytest.raises(ValueError):
            f"{Color('#ff0000'):invalid}"


class TestColorImmutability:
    """Test that Color operations never modify the original."""

    def test_from_hsl_immutable(self):
        """From HSL returns a new Color, not affecting other instances."""
        c1 = Color("#3498db")
        c2 = Color.from_hsl(0, 100, 50)
        assert c1.rgb == (52, 152, 219)
        assert c2.rgb == (255, 0, 0)

    def test_slots_prevent_attr(self):
        """__slots__ prevents setting arbitrary attributes."""
        c = Color("#3498db")
        with pytest.raises(AttributeError):
            c.custom_attr = "nope"  # type: ignore[attr-defined]
