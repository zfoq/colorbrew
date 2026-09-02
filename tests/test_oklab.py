"""Tests for OKLab and OKLCH conversion helpers."""

import math

import pytest

from colorbrew.conversion import (
    oklab_to_oklch,
    oklab_to_rgb,
    oklch_to_oklab,
    oklch_to_rgb,
    rgb_to_oklab,
    rgb_to_oklch,
)


@pytest.mark.parametrize(
    "rgb,expected_l",
    [
        ((0, 0, 0), 0.0),
        ((255, 255, 255), 1.0),
    ],
)
def test_oklab_lightness_extremes(rgb: tuple[int, int, int], expected_l: float) -> None:
    """Black and white map to the OKLab lightness endpoints."""
    lightness, a, b = rgb_to_oklab(*rgb)
    assert lightness == pytest.approx(expected_l, abs=1e-6)
    assert a == pytest.approx(0.0, abs=1e-6)
    assert b == pytest.approx(0.0, abs=1e-6)


@pytest.mark.parametrize(
    "rgb",
    [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (128, 128, 128),
    ],
)
def test_oklab_round_trips_primary_and_gray_rgb(rgb: tuple[int, int, int]) -> None:
    """RGB values survive an OKLab round trip within one channel step."""
    result = oklab_to_rgb(*rgb_to_oklab(*rgb))
    assert result == pytest.approx(rgb, abs=1)


@pytest.mark.parametrize(
    "rgb",
    [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (128, 128, 128),
    ],
)
def test_oklch_round_trips_primary_and_gray_rgb(rgb: tuple[int, int, int]) -> None:
    """RGB values survive an OKLCH round trip within one channel step."""
    result = oklch_to_rgb(*rgb_to_oklch(*rgb))
    assert result == pytest.approx(rgb, abs=1)


def test_oklab_oklch_round_trip_preserves_components() -> None:
    """OKLab values survive conversion through polar OKLCH coordinates."""
    oklab = (0.6279553606, 0.2248630611, 0.1258462985)
    assert oklch_to_oklab(*oklab_to_oklch(*oklab)) == pytest.approx(oklab, abs=1e-12)


@pytest.mark.parametrize(
    "func,args",
    [
        (rgb_to_oklab, (-1, 0, 0)),
        (rgb_to_oklch, (0, 256, 0)),
        (oklab_to_rgb, (math.nan, 0.0, 0.0)),
        (oklch_to_rgb, (0.5, -0.1, 0.0)),
    ],
)
def test_oklab_rejects_invalid_inputs(func, args: tuple[float, ...]) -> None:
    """Invalid RGB and OKLab/OKLCH channels are rejected at the boundary."""
    with pytest.raises(ValueError):
        func(*args)


def test_oklab_to_rgb_clamps_out_of_gamut_output() -> None:
    """Out-of-gamut OKLab input returns valid RGB channels."""
    assert all(0 <= channel <= 255 for channel in oklab_to_rgb(1.2, 0.4, -0.4))
