"""Tests for new features.

Alpha channel, suggest_text_color, find_accessible_color, perceptual
gradient, modern CSS parsing, and palette scale generation.
"""

import pytest

from colorbrew import Color

# ============================================================
# Alpha channel support
# ============================================================


class TestAlphaParsing:
    """Test alpha channel parsing from strings."""

    def test_hex_6digit_default_alpha(self):
        """6-digit hex has alpha 1.0."""
        c = Color("#3498db")
        assert c.alpha == 1.0

    def test_hex_8digit_full_opaque(self):
        """8-digit hex ff is fully opaque."""
        c = Color("#3498dbff")
        assert c.alpha == 1.0

    def test_hex_8digit_half(self):
        """8-digit hex 80 is ~0.5 alpha."""
        c = Color("#3498db80")
        assert c.rgb == (52, 152, 219)
        assert abs(c.alpha - 128 / 255) < 0.01

    def test_hex_4digit(self):
        """4-digit hex includes alpha."""
        c = Color("#f008")
        assert c.rgb == (255, 0, 0)
        assert abs(c.alpha - 136 / 255) < 0.01

    def test_hex_3digit_default_alpha(self):
        """3-digit hex has alpha 1.0."""
        c = Color("#fff")
        assert c.alpha == 1.0

    def test_rgba_legacy(self):
        """Legacy rgba() parses alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.rgb == (52, 152, 219)
        assert c.alpha == 0.5

    def test_rgb_legacy_no_alpha(self):
        """Legacy rgb() defaults to alpha 1.0."""
        c = Color("rgb(52, 152, 219)")
        assert c.alpha == 1.0

    def test_hsla_legacy(self):
        """Legacy hsla() parses alpha."""
        c = Color("hsla(204, 70%, 53%, 0.3)")
        assert c.alpha == 0.3

    def test_rgb_modern_space_separated(self):
        """Modern rgb() with spaces."""
        c = Color("rgb(52 152 219)")
        assert c.rgb == (52, 152, 219)
        assert c.alpha == 1.0

    def test_rgb_modern_with_alpha(self):
        """Modern rgb() with slash alpha."""
        c = Color("rgb(52 152 219 / 0.5)")
        assert c.rgb == (52, 152, 219)
        assert c.alpha == 0.5

    def test_rgb_modern_alpha_percent(self):
        """Modern rgb() with percent alpha."""
        c = Color("rgb(52 152 219 / 50%)")
        assert c.rgb == (52, 152, 219)
        assert c.alpha == 0.5

    def test_hsl_modern_deg(self):
        """Modern hsl() with deg unit."""
        c = Color("hsl(204deg 70% 53%)")
        assert c.alpha == 1.0
        assert c.hsl[0] == 204

    def test_hsl_modern_with_alpha(self):
        """Modern hsl() with slash alpha."""
        c = Color("hsl(204 70% 53% / 0.7)")
        assert c.alpha == 0.7

    def test_named_color_alpha(self):
        """Named colors have alpha 1.0."""
        c = Color("red")
        assert c.alpha == 1.0


class TestAlphaProperties:
    """Test alpha-aware properties and methods."""

    def test_rgba_property(self):
        """RGBA property includes alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.rgba == (52, 152, 219, 0.5)

    def test_hex_opaque(self):
        """Opaque color returns 6-digit hex."""
        c = Color(52, 152, 219)
        assert c.hex == "#3498db"

    def test_hex_with_alpha(self):
        """Translucent color returns 8-digit hex."""
        c = Color("rgba(255, 0, 0, 0.5)")
        h = c.hex
        assert h.startswith("#ff0000")
        assert len(h) == 9

    def test_css_rgb_opaque(self):
        """Opaque color uses rgb() format."""
        c = Color(52, 152, 219)
        assert c.css_rgb == "rgb(52, 152, 219)"

    def test_css_rgb_with_alpha(self):
        """Translucent color uses rgba() format."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert "rgba" in c.css_rgb
        assert "0.5" in c.css_rgb

    def test_css_hsl_opaque(self):
        """Opaque color uses hsl() format."""
        c = Color(52, 152, 219)
        assert c.css_hsl.startswith("hsl(")

    def test_css_hsl_with_alpha(self):
        """Translucent color uses hsla() format."""
        c = Color("hsla(204, 70%, 53%, 0.5)")
        assert "hsla" in c.css_hsl

    def test_with_alpha(self):
        """with_alpha returns new Color with updated alpha."""
        c = Color(255, 0, 0)
        c2 = c.with_alpha(0.5)
        assert c2.rgb == (255, 0, 0)
        assert c2.alpha == 0.5
        assert c.alpha == 1.0

    def test_with_alpha_invalid(self):
        """with_alpha rejects out-of-range values."""
        c = Color(255, 0, 0)
        with pytest.raises(Exception):
            c.with_alpha(1.5)

    def test_opaque(self):
        """Opaque returns Color with alpha 1.0."""
        c = Color("rgba(255, 0, 0, 0.5)")
        o = c.opaque
        assert o.alpha == 1.0
        assert o.rgb == (255, 0, 0)

    def test_opaque_already(self):
        """Opaque returns same instance if already opaque."""
        c = Color(255, 0, 0)
        assert c.opaque is c


class TestAlphaPreservation:
    """Test that alpha is preserved through transformations."""

    def test_lighten_preserves_alpha(self):
        """Lighten preserves alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.lighten(10).alpha == 0.5

    def test_darken_preserves_alpha(self):
        """Darken preserves alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.darken(10).alpha == 0.5

    def test_saturate_preserves_alpha(self):
        """Saturate preserves alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.saturate(10).alpha == 0.5

    def test_invert_preserves_alpha(self):
        """Invert preserves alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.invert().alpha == 0.5

    def test_grayscale_preserves_alpha(self):
        """Grayscale preserves alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.grayscale().alpha == 0.5

    def test_complementary_preserves_alpha(self):
        """Complementary preserves alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.complementary().alpha == 0.5

    def test_simulate_colorblind_preserves_alpha(self):
        """Colorblind simulation preserves alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        assert c.simulate_colorblind("protanopia").alpha == 0.5

    def test_mix_interpolates_alpha(self):
        """Mix interpolates alpha between two colors."""
        c1 = Color("rgba(255, 0, 0, 1.0)")
        c2 = Color("rgba(0, 0, 255, 0.0)")
        mixed = c1.mix(c2, 0.5)
        assert abs(mixed.alpha - 0.5) < 0.01


class TestAlphaEquality:
    """Test that equality and hash include alpha."""

    def test_same_rgb_different_alpha_not_equal(self):
        """Different alpha means not equal."""
        c1 = Color(255, 0, 0)
        c2 = c1.with_alpha(0.5)
        assert c1 != c2

    def test_same_rgb_same_alpha_equal(self):
        """Same RGB and alpha means equal."""
        c1 = Color("rgba(255, 0, 0, 0.5)")
        c2 = Color(255, 0, 0).with_alpha(0.5)
        assert c1 == c2

    def test_hash_different_alpha(self):
        """Different alpha produces different hash."""
        c1 = Color(255, 0, 0)
        c2 = c1.with_alpha(0.5)
        assert hash(c1) != hash(c2)


# ============================================================
# suggest_text_color
# ============================================================


class TestSuggestTextColor:
    """Test suggest_text_color convenience method."""

    def test_dark_background_suggests_white(self):
        """Black background suggests white text."""
        c = Color(0, 0, 0)
        assert c.suggest_text_color().rgb == (255, 255, 255)

    def test_light_background_suggests_black(self):
        """White background suggests black text."""
        c = Color(255, 255, 255)
        assert c.suggest_text_color().rgb == (0, 0, 0)

    def test_medium_blue(self):
        """Medium blue suggests readable text."""
        c = Color(52, 152, 219)
        text = c.suggest_text_color()
        assert text.rgb in ((0, 0, 0), (255, 255, 255))
        assert c.contrast(text) >= 3.0

    def test_yellow_suggests_black(self):
        """Bright yellow suggests black text."""
        c = Color(255, 255, 0)
        text = c.suggest_text_color()
        assert text.rgb == (0, 0, 0)


# ============================================================
# find_accessible_color
# ============================================================


class TestFindAccessibleColor:
    """Test find_accessible_color for WCAG compliance."""

    def test_already_accessible(self):
        """Already accessible color is returned unchanged."""
        bg = Color(255, 255, 255)
        fg = Color(0, 0, 0)
        result = bg.find_accessible_color(fg)
        assert result.rgb == (0, 0, 0)

    def test_adjusts_to_meet_aa(self):
        """Light-on-white is adjusted to meet AA."""
        bg = Color(255, 255, 255)
        fg = Color(200, 200, 200)
        result = bg.find_accessible_color(fg)
        assert bg.meets_aa(result)

    def test_adjusts_to_meet_aaa(self):
        """Dark-on-black is adjusted to meet AAA."""
        bg = Color(0, 0, 0)
        fg = Color(50, 50, 50)
        result = bg.find_accessible_color(fg, level="aaa")
        assert bg.meets_aaa(result)

    def test_dark_bg_lightens_target(self):
        """Dark background causes target to lighten."""
        bg = Color(0, 0, 0)
        fg = Color(30, 30, 30)
        result = bg.find_accessible_color(fg)
        assert result.luminance > fg.luminance


# ============================================================
# Perceptual gradient (Lab interpolation)
# ============================================================


class TestPerceptualGradient:
    """Test Lab-space interpolation for gradients."""

    def test_rgb_gradient_default(self):
        """Default gradient uses RGB interpolation."""
        c1 = Color(255, 0, 0)
        c2 = Color(0, 0, 255)
        grad = c1.gradient(c2, steps=5)
        assert len(grad) == 5
        assert grad[0].rgb == (255, 0, 0)
        assert grad[-1].rgb == (0, 0, 255)

    def test_lab_gradient(self):
        """Lab gradient produces correct endpoints."""
        c1 = Color(255, 0, 0)
        c2 = Color(0, 0, 255)
        grad = c1.gradient(c2, steps=5, space="lab")
        assert len(grad) == 5
        assert grad[0].rgb == (255, 0, 0)
        assert grad[-1].rgb == (0, 0, 255)

    def test_lab_gradient_midpoint_differs_from_rgb(self):
        """Lab midpoint differs from RGB midpoint."""
        c1 = Color(255, 0, 0)
        c2 = Color(0, 0, 255)
        rgb_mid = c1.gradient(c2, steps=3)[1].rgb
        lab_mid = c1.gradient(c2, steps=3, space="lab")[1].rgb
        assert rgb_mid != lab_mid

    def test_lab_gradient_interpolates_alpha(self):
        """Lab gradient interpolates alpha values."""
        c1 = Color("rgba(255, 0, 0, 1.0)")
        c2 = Color("rgba(0, 0, 255, 0.0)")
        grad = c1.gradient(c2, steps=3, space="lab")
        assert abs(grad[1].alpha - 0.5) < 0.01


# ============================================================
# Modern CSS parsing
# ============================================================


class TestModernCssParsing:
    """Test CSS Color Level 4 syntax support."""

    def test_rgb_space_separated(self):
        """Space-separated rgb() is parsed."""
        c = Color("rgb(52 152 219)")
        assert c.rgb == (52, 152, 219)

    def test_rgb_space_with_slash_alpha(self):
        """Space-separated rgb() with slash alpha."""
        c = Color("rgb(52 152 219 / 0.5)")
        assert c.rgb == (52, 152, 219)
        assert c.alpha == 0.5

    def test_rgb_space_with_percent_alpha(self):
        """Space-separated rgb() with percent alpha."""
        c = Color("rgb(52 152 219 / 50%)")
        assert c.alpha == 0.5

    def test_hsl_deg_unit(self):
        """hsl() with deg unit."""
        c = Color("hsl(204deg 70% 53%)")
        assert c.hsl[0] == 204

    def test_hsl_space_no_deg(self):
        """hsl() with space-separated, no deg unit."""
        c = Color("hsl(204 70% 53%)")
        assert c.hsl[0] == 204

    def test_hsl_space_with_alpha(self):
        """hsl() with space-separated and slash alpha."""
        c = Color("hsl(204deg 70% 53% / 0.7)")
        assert c.alpha == 0.7

    def test_rgba_legacy_still_works(self):
        """Legacy rgba() still works."""
        c = Color("rgba(52, 152, 219, 0.8)")
        assert c.rgb == (52, 152, 219)
        assert c.alpha == 0.8

    def test_hsla_legacy_still_works(self):
        """Legacy hsla() still works."""
        c = Color("hsla(204, 70%, 53%, 0.3)")
        assert c.alpha == 0.3


# ============================================================
# Palette scale generation
# ============================================================


class TestPaletteScale:
    """Test Tailwind-like 50-950 scale generation."""

    def test_scale_returns_11_steps(self):
        """Scale returns 11 shade stops."""
        c = Color("#3498db")
        s = c.scale()
        assert len(s) == 11

    def test_scale_keys(self):
        """Scale has correct step keys."""
        c = Color("#3498db")
        s = c.scale()
        expected_keys = {50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950}
        assert set(s.keys()) == expected_keys

    def test_scale_50_is_lightest(self):
        """Step 50 is lighter than step 950."""
        c = Color("#3498db")
        s = c.scale()
        assert s[50].luminance > s[950].luminance

    def test_scale_950_is_darkest(self):
        """Step 950 is darker than step 50."""
        c = Color("#3498db")
        s = c.scale()
        assert s[950].luminance < s[50].luminance

    def test_scale_monotonic_luminance(self):
        """Luminance decreases monotonically across steps."""
        c = Color("#e74c3c")
        s = c.scale()
        steps = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]
        luminances = [s[k].luminance for k in steps]
        for i in range(len(luminances) - 1):
            assert luminances[i] >= luminances[i + 1]

    def test_scale_values_are_colors(self):
        """All scale values are Color instances."""
        c = Color("#3498db")
        s = c.scale()
        for color in s.values():
            assert isinstance(color, Color)

    def test_scale_preserves_alpha(self):
        """Scale preserves the original alpha."""
        c = Color("rgba(52, 152, 219, 0.5)")
        s = c.scale()
        for color in s.values():
            assert color.alpha == 0.5

    def test_scale_preserves_hue(self):
        """Scale preserves the hue within rounding tolerance."""
        c = Color("#3498db")
        base_h = c.hsl[0]
        s = c.scale()
        for color in s.values():
            assert abs(color.hsl[0] - base_h) <= 2
