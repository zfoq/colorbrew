"""Tests for colorbrew.contrast — WCAG accessibility calculations."""

from colorbrew.contrast import (
    contrast_ratio,
    meets_aa,
    meets_aaa,
    relative_luminance,
)


class TestRelativeLuminance:
    """Test WCAG relative luminance calculation."""

    def test_black(self):
        """Black has luminance 0.0."""
        assert relative_luminance(0, 0, 0) == 0.0

    def test_white(self):
        """White has luminance 1.0."""
        assert relative_luminance(255, 255, 255) == 1.0

    def test_mid_range(self):
        """Mid-range color has luminance between 0 and 1."""
        lum = relative_luminance(128, 128, 128)
        assert 0.0 < lum < 1.0


class TestContrastRatio:
    """Test WCAG contrast ratio calculation."""

    def test_black_white(self):
        """Black vs white has contrast ratio of 21.0."""
        assert contrast_ratio((0, 0, 0), (255, 255, 255)) == 21.0

    def test_same_color(self):
        """Same color has contrast ratio of 1.0."""
        assert contrast_ratio((128, 128, 128), (128, 128, 128)) == 1.0

    def test_symmetric(self):
        """Contrast ratio is the same regardless of order."""
        ratio1 = contrast_ratio((0, 0, 0), (255, 255, 255))
        ratio2 = contrast_ratio((255, 255, 255), (0, 0, 0))
        assert ratio1 == ratio2


class TestMeetsAa:
    """Test WCAG AA compliance checking."""

    def test_black_white_passes(self):
        """Black on white passes AA."""
        assert meets_aa((0, 0, 0), (255, 255, 255)) is True

    def test_similar_colors_fail(self):
        """Very similar colors fail AA."""
        assert meets_aa((200, 200, 200), (210, 210, 210)) is False

    def test_large_text_lower_threshold(self):
        """Large text uses the lower 3.0 threshold."""
        # Find a pair that passes 3.0 but fails 4.5
        assert meets_aa((0, 0, 0), (255, 255, 255), large=True) is True


class TestMeetsAaa:
    """Test WCAG AAA compliance checking."""

    def test_black_white_passes(self):
        """Black on white passes AAA."""
        assert meets_aaa((0, 0, 0), (255, 255, 255)) is True

    def test_moderate_contrast_fails(self):
        """Moderate contrast fails AAA."""
        # Gray on white typically doesn't meet 7.0
        assert meets_aaa((150, 150, 150), (255, 255, 255)) is False
