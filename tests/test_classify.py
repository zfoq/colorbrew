"""Tests for colorbrew.analysis.classify — perceptual OKLCH classification."""

import pytest

from colorbrew.analysis.classify import classify_color
from colorbrew.types import ColorClass


class TestClassifyColorFamilies:
    """Classification picks the expected hue family for saturated colors."""

    def test_pure_red_is_red(self):
        result = classify_color(255, 0, 0)
        assert result.family == "red"

    def test_orange_is_orange(self):
        result = classify_color(255, 165, 0)
        assert result.family == "orange"

    def test_yellow_is_yellow(self):
        result = classify_color(255, 255, 0)
        assert result.family == "yellow"

    def test_pure_green_is_green(self):
        result = classify_color(0, 255, 0)
        assert result.family == "green"

    def test_cyan_is_cyan(self):
        result = classify_color(0, 255, 255)
        assert result.family == "cyan"

    def test_pure_blue_is_blue(self):
        result = classify_color(0, 0, 255)
        assert result.family == "blue"

    def test_magenta_is_magenta(self):
        result = classify_color(255, 0, 255)
        assert result.family == "magenta"


class TestClassifyNeutralLowChroma:
    """Low-chroma colors are classified as neutral and keep their coordinates."""

    def test_mid_gray_is_neutral(self):
        result = classify_color(128, 128, 128)
        assert result.family == "neutral"
        assert result.chroma == "low"
        assert result.tone == "medium"

    def test_white_is_neutral_light(self):
        result = classify_color(255, 255, 255)
        assert result.family == "neutral"
        assert result.tone == "light"

    def test_black_is_neutral_dark(self):
        result = classify_color(0, 0, 0)
        assert result.family == "neutral"
        assert result.tone == "dark"

    def test_near_gray_preserves_lightness_and_hue(self):
        result = classify_color(100, 102, 101)
        assert result.family == "neutral"
        assert isinstance(result.lightness, float)
        assert 0.0 <= result.hue <= 360.0


class TestClassifyTonesAndChroma:
    """Tone and chroma buckets are derived from OKLCH coordinates."""

    def test_dark_color_is_dark_tone(self):
        result = classify_color(30, 20, 60)
        assert result.tone == "dark"

    def test_light_color_is_light_tone(self):
        result = classify_color(250, 240, 230)
        assert result.tone == "light"

    def test_vivid_color_is_high_chroma(self):
        result = classify_color(255, 0, 0)
        assert result.chroma == "high"

    def test_pastel_color_is_medium_or_low_chroma(self):
        result = classify_color(255, 200, 200)
        assert result.chroma in ("low", "medium")

    def test_returns_color_class_namedtuple(self):
        result = classify_color(52, 152, 219)
        assert isinstance(result, ColorClass)
        assert hasattr(result, "family")
        assert hasattr(result, "tone")
        assert hasattr(result, "chroma")
        assert hasattr(result, "lightness")
        assert hasattr(result, "hue")


class TestClassifyInvalidInput:
    """Invalid inputs are rejected with a clear error."""

    def test_channel_out_of_range(self):
        with pytest.raises(ValueError):
            classify_color(256, 0, 0)

    def test_non_integer_channel(self):
        with pytest.raises(ValueError):  # type: ignore[arg-type]
            classify_color("255", 0, 0)  # type: ignore[arg-type]
