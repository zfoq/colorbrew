"""Tests for colorbrew.palettes — palette generation algorithms."""

from colorbrew import Color, Palette
from colorbrew.conversion.converters import rgb_to_hsl
from colorbrew.transform.palettes import (
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


class TestColorPalette:
    """Test the Color-based Palette class."""

    def test_construct_from_color_objects(self):
        """Palette accepts Color instances."""
        palette = Palette([Color("red"), Color("#00ff00"), Color(0, 0, 255)])
        assert len(palette) == 3
        assert all(isinstance(c, Color) for c in palette.colors)

    def test_construct_from_parseable_values(self):
        """Palette coerces strings and RGB tuples to Color."""
        palette = Palette(["red", "#00ff00", (0, 0, 255)])
        assert palette.hexes == ["#ff0000", "#00ff00", "#0000ff"]

    def test_members_are_ordered_and_unique(self):
        """Duplicate colors are removed while preserving order."""
        palette = Palette(["red", "#ff0000", "blue", "red"])
        assert palette.hexes == ["#ff0000", "#0000ff"]

    def test_iteration_yields_colors(self):
        """A color-mode palette iterates over its Color members."""
        palette = Palette(["red", "#00ff00"])
        colors = list(palette)
        assert colors == [Color("red"), Color("#00ff00")]

    def test_index_and_slice(self):
        """Palette supports sequence access."""
        palette = Palette(["red", "#00ff00", "blue"])
        assert palette[0] == Color("red")
        assert palette[-1] == Color("blue")
        assert palette[1:].hexes == ["#00ff00", "#0000ff"]

    def test_membership(self):
        """Palette membership works for Color objects."""
        palette = Palette(["red", "#00ff00"])
        assert Color("red") in palette
        assert Color("blue") not in palette

    def test_reversed(self):
        """Palette can be reversed."""
        palette = Palette(["red", "#00ff00", "blue"])
        assert list(reversed(palette)) == [
            Color("blue"),
            Color("#00ff00"),
            Color("red"),
        ]

    def test_set_union(self):
        """Palettes support union via the | operator."""
        a = Palette(["red", "#00ff00"])
        b = Palette(["#00ff00", "blue"])
        assert (a | b).hexes == ["#ff0000", "#00ff00", "#0000ff"]

    def test_mapping_mode_still_works(self):
        """Palette still behaves as a read-only mapping for bundled data."""
        from colorbrew.data import get_palette

        palette = get_palette("tailwind")
        assert isinstance(palette, Palette)
        assert palette["sky-500"] == "#0ea5e9"
        assert "sky-500" in palette
        assert "sky-500" in dict(palette)

    def test_gradient_method_with_other(self):
        """Palette.gradient produces a gradient to another color."""
        palette = Palette([Color("red")]).gradient(Color("blue"), steps=3)
        assert isinstance(palette, Palette)
        assert len(palette) == 3
        assert palette[0] == Color("red")
        assert palette[-1] == Color("blue")

    def test_gradient_method_between_members(self):
        """Palette.gradient stitches gradients between consecutive colors."""
        palette = Palette([Color("red"), Color("blue")]).gradient(steps=3)
        assert len(palette) == 3
        assert palette[0] == Color("red")
        assert palette[-1] == Color("blue")

    def test_complementary_method(self):
        """Palette.complementary returns a Palette."""
        palette = Palette([Color("red")]).complementary()
        assert isinstance(palette, Palette)
        assert len(palette) == 1
        assert palette[0] == Color("red").complementary()

    def test_analogous_method(self):
        """Palette.analogous returns a flattened Palette."""
        palette = Palette([Color("red")]).analogous(n=3)
        assert isinstance(palette, Palette)
        assert len(palette) == 3

    def test_triadic_method(self):
        """Palette.triadic returns a flattened Palette."""
        palette = Palette([Color("red")]).triadic()
        assert isinstance(palette, Palette)
        assert len(palette) == 2

    def test_tetradic_method(self):
        """Palette.tetradic returns a flattened Palette."""
        palette = Palette([Color("red")]).tetradic()
        assert isinstance(palette, Palette)
        assert len(palette) == 3

    def test_scale_method(self):
        """Palette.scale returns a step-to-Palette mapping."""
        palette = Palette([Color("red")]).scale()
        assert set(palette.keys()) == {50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950}
        for step, shades in palette.items():
            assert isinstance(shades, Palette)
            assert len(shades) == 1
            assert isinstance(shades[0], Color)

    def test_alpha_preserved_through_palette_methods(self):
        """Color-mode methods preserve the source alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        palette = Palette([c]).complementary()
        assert palette[0].alpha == 0.5
