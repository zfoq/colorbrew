"""Tests for colorbrew.temperature — color temperature classification."""

from colorbrew.temperature import classify_temperature, estimate_kelvin


class TestClassifyTemperature:
    """Test warm/cool/neutral classification."""

    def test_red_is_warm(self):
        """Pure red is classified as warm."""
        assert classify_temperature(255, 0, 0) == "warm"

    def test_orange_is_warm(self):
        """Orange is classified as warm."""
        assert classify_temperature(255, 165, 0) == "warm"

    def test_blue_is_cool(self):
        """Pure blue is classified as cool."""
        assert classify_temperature(0, 0, 255) == "cool"

    def test_green_is_cool(self):
        """Pure green is classified as cool."""
        assert classify_temperature(0, 255, 0) == "cool"

    def test_gray_is_neutral(self):
        """Mid gray is classified as neutral."""
        assert classify_temperature(128, 128, 128) == "neutral"

    def test_near_white_is_neutral(self):
        """Near-white (low saturation) is classified as neutral."""
        assert classify_temperature(245, 245, 245) == "neutral"


class TestEstimateKelvin:
    """Test Kelvin color temperature estimation."""

    def test_returns_int(self):
        """Return an integer."""
        assert isinstance(estimate_kelvin(255, 0, 0), int)

    def test_within_range(self):
        """Return value within 1000-40000 K range."""
        k = estimate_kelvin(52, 152, 219)
        assert 1000 <= k <= 40000

    def test_warm_color_lower_kelvin(self):
        """Warm colors have lower Kelvin than cool colors."""
        warm_k = estimate_kelvin(255, 100, 0)
        cool_k = estimate_kelvin(0, 100, 255)
        assert warm_k < cool_k

    def test_black_returns_minimum(self):
        """Black returns the minimum Kelvin value."""
        assert estimate_kelvin(0, 0, 0) == 1000
