"""Tests for colorbrew.analysis.delta_e — Lab conversion and color distance."""

import pytest

from colorbrew.analysis.delta_e import (
    delta_e_76,
    delta_e_2000,
    distance,
    euclidean_rgb,
    rgb_to_lab,
)


class TestRgbToLab:
    """Test sRGB to CIE L*a*b* conversion."""

    def test_black(self):
        """Black maps to L*=0, a*=0, b*=0."""
        ls, a, b = rgb_to_lab(0, 0, 0)
        assert ls == pytest.approx(0.0, abs=0.01)
        assert a == pytest.approx(0.0, abs=0.01)
        assert b == pytest.approx(0.0, abs=0.01)

    def test_white(self):
        """White maps to L*=100, a*~0, b*~0."""
        ls, a, b = rgb_to_lab(255, 255, 255)
        assert ls == pytest.approx(100.0, abs=0.1)
        assert a == pytest.approx(0.0, abs=0.5)
        assert b == pytest.approx(0.0, abs=0.5)

    def test_pure_red(self):
        """Pure red has high L*, positive a*, positive b*."""
        ls, a, b = rgb_to_lab(255, 0, 0)
        assert ls == pytest.approx(53.23, abs=0.5)
        assert a == pytest.approx(80.11, abs=1.0)
        assert b == pytest.approx(67.22, abs=1.0)

    def test_pure_green(self):
        """Pure green has high L*, negative a*, positive b*."""
        ls, a, b = rgb_to_lab(0, 255, 0)
        assert ls == pytest.approx(87.74, abs=0.5)
        assert a == pytest.approx(-86.18, abs=1.0)
        assert b == pytest.approx(83.18, abs=1.0)

    def test_pure_blue(self):
        """Pure blue has low L*, positive a*, very negative b*."""
        ls, a, b = rgb_to_lab(0, 0, 255)
        assert ls == pytest.approx(32.30, abs=0.5)
        assert a == pytest.approx(79.20, abs=1.0)
        assert b == pytest.approx(-107.86, abs=1.0)

    def test_mid_gray(self):
        """Mid gray has L*~54, a*~0, b*~0."""
        ls, a, b = rgb_to_lab(128, 128, 128)
        assert 50 < ls < 60
        assert abs(a) < 0.5
        assert abs(b) < 0.5

    def test_returns_three_floats(self):
        """Result is a tuple of three floats."""
        result = rgb_to_lab(52, 152, 219)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)


class TestEuclideanRgb:
    """Test Euclidean distance in RGB space."""

    def test_identical_colors(self):
        """Same color has zero distance."""
        assert euclidean_rgb(100, 150, 200, 100, 150, 200) == 0.0

    def test_black_white(self):
        """Black to white = sqrt(3 * 255^2)."""
        d = euclidean_rgb(0, 0, 0, 255, 255, 255)
        assert d == pytest.approx(441.67, abs=0.1)

    def test_known_pair(self):
        """Single-channel difference of 100."""
        d = euclidean_rgb(100, 0, 0, 200, 0, 0)
        assert d == pytest.approx(100.0, abs=0.001)

    def test_symmetric(self):
        """Distance is symmetric: d(a,b) == d(b,a)."""
        d1 = euclidean_rgb(52, 152, 219, 231, 76, 60)
        d2 = euclidean_rgb(231, 76, 60, 52, 152, 219)
        assert d1 == pytest.approx(d2)


class TestDeltaE76:
    """Test CIE76 delta E (Euclidean in Lab)."""

    def test_identical(self):
        """Same Lab values give zero distance."""
        lab = (50.0, 25.0, -10.0)
        assert delta_e_76(lab, lab) == 0.0

    def test_known_pair(self):
        """Known delta E 76 for black vs mid gray."""
        black = rgb_to_lab(0, 0, 0)
        white = rgb_to_lab(255, 255, 255)
        d = delta_e_76(black, white)
        assert d == pytest.approx(100.0, abs=1.0)

    def test_symmetric(self):
        """Distance is symmetric."""
        lab1 = rgb_to_lab(52, 152, 219)
        lab2 = rgb_to_lab(231, 76, 60)
        assert delta_e_76(lab1, lab2) == pytest.approx(delta_e_76(lab2, lab1))


# Sharma et al. (2005) CIEDE2000 reference test data.
# Columns: L1, a1, b1, L2, a2, b2, expected_delta_e_2000
_SHARMA_DATA = [
    (50.0, 2.6772, -79.7751, 50.0, 0.0, -82.7485, 2.0425),
    (50.0, 3.1571, -77.2803, 50.0, 0.0, -82.7485, 2.8615),
    (50.0, 2.8361, -74.0200, 50.0, 0.0, -82.7485, 3.4412),
    (50.0, -1.3802, -84.2814, 50.0, 0.0, -82.7485, 1.0000),
    (50.0, -1.1848, -84.8006, 50.0, 0.0, -82.7485, 1.0000),
    (50.0, -0.9009, -85.5211, 50.0, 0.0, -82.7485, 1.0000),
    (50.0, 0.0, 0.0, 50.0, -1.0, 2.0, 2.3669),
    (50.0, -1.0, 2.0, 50.0, 0.0, 0.0, 2.3669),
    (50.0, 2.49, -0.001, 50.0, -2.49, 0.0009, 7.1792),
    (50.0, 2.49, -0.001, 50.0, -2.49, 0.001, 7.1792),
    (50.0, 2.49, -0.001, 50.0, -2.49, 0.0011, 7.2195),
    (50.0, 2.49, -0.001, 50.0, -2.49, 0.0012, 7.2195),
    (50.0, -0.001, 2.49, 50.0, 0.0009, -2.49, 4.8045),
    (50.0, -0.001, 2.49, 50.0, 0.001, -2.49, 4.8045),
    (50.0, -0.001, 2.49, 50.0, 0.0011, -2.49, 4.7461),
    (50.0, 2.5, 0.0, 50.0, 0.0, -2.5, 4.3065),
    (50.0, 2.5, 0.0, 73.0, 25.0, -18.0, 27.1492),
    (50.0, 2.5, 0.0, 61.0, -5.0, 29.0, 22.8977),
    (50.0, 2.5, 0.0, 56.0, -27.0, -3.0, 31.9030),
    (50.0, 2.5, 0.0, 58.0, 24.0, 15.0, 19.4535),
    (50.0, 2.5, 0.0, 50.0, 3.1736, 0.5854, 1.0000),
    (50.0, 2.5, 0.0, 50.0, 3.2972, 0.0, 1.0000),
    (50.0, 2.5, 0.0, 50.0, 1.8634, 0.5757, 1.0000),
    (50.0, 2.5, 0.0, 50.0, 3.2592, 0.335, 1.0000),
    (60.2574, -34.0099, 36.2677, 60.4626, -34.1751, 39.4387, 1.2644),
    (63.0109, -31.0961, -5.8663, 62.8187, -29.7946, -4.0864, 1.2630),
    (61.2901, 3.7196, -5.3901, 61.4292, 2.248, -4.962, 1.8731),
    (35.0831, -44.1164, 3.7933, 35.0232, -40.0716, 1.5901, 1.8645),
    (22.7233, 20.0904, -46.694, 23.0331, 14.973, -42.5619, 2.0373),
    (36.4612, 47.858, 18.3852, 36.2715, 50.5065, 21.2231, 1.4146),
    (90.8027, -2.0831, 1.441, 91.1528, -1.6435, 0.0447, 1.4441),
    (90.9257, -0.5406, -0.9208, 88.6381, -0.8985, -0.7239, 1.5381),
    (6.7747, -0.2908, -2.4247, 5.8714, -0.0985, -2.2286, 0.6377),
    (2.0776, 0.0795, -1.135, 0.9033, -0.0636, -0.5514, 0.9082),
]


class TestDeltaE2000:
    """Test CIEDE2000 against Sharma et al. reference data."""

    @pytest.mark.parametrize(
        ("l1", "a1", "b1", "l2", "a2", "b2", "expected"),
        _SHARMA_DATA,
        ids=[f"pair_{i + 1}" for i in range(len(_SHARMA_DATA))],
    )
    def test_sharma_reference(self, l1, a1, b1, l2, a2, b2, expected):
        """Match Sharma reference data to 4 decimal places."""
        result = delta_e_2000((l1, a1, b1), (l2, a2, b2))
        assert result == pytest.approx(expected, abs=0.0001)

    def test_identical(self):
        """Same Lab values give zero distance."""
        lab = (50.0, 25.0, -10.0)
        assert delta_e_2000(lab, lab) == 0.0

    def test_symmetric(self):
        """CIEDE2000 is symmetric: d(a,b) == d(b,a)."""
        lab1 = (50.0, 2.6772, -79.7751)
        lab2 = (50.0, 0.0, -82.7485)
        assert delta_e_2000(lab1, lab2) == pytest.approx(delta_e_2000(lab2, lab1))

    def test_black_vs_white(self):
        """Black vs white should have very large delta E."""
        black = (0.0, 0.0, 0.0)
        white = (100.0, 0.0, 0.0)
        d = delta_e_2000(black, white)
        assert d > 50


class TestDistance:
    """Test the unified distance dispatch function."""

    def test_euclidean(self):
        """Euclidean method returns RGB distance."""
        d = distance(255, 0, 0, 0, 0, 0, method="euclidean")
        assert d == pytest.approx(255.0)

    def test_cie76(self):
        """CIE76 method returns Lab Euclidean distance."""
        d = distance(0, 0, 0, 255, 255, 255, method="cie76")
        assert d == pytest.approx(100.0, abs=1.0)

    def test_ciede2000(self):
        """CIEDE2000 method returns perceptual distance."""
        d = distance(0, 0, 0, 255, 255, 255, method="ciede2000")
        assert d > 50

    def test_identical_zero(self):
        """All methods return 0 for identical colors."""
        for method in ("euclidean", "cie76", "ciede2000"):
            assert distance(100, 100, 100, 100, 100, 100, method=method) == 0.0

    def test_unknown_method_raises(self):
        """Unknown method raises ValueError."""
        with pytest.raises(ValueError, match="Unknown distance method"):
            distance(0, 0, 0, 255, 255, 255, method="unknown")

    def test_default_is_ciede2000(self):
        """Default method is ciede2000."""
        d_default = distance(255, 0, 0, 0, 255, 0)
        d_explicit = distance(255, 0, 0, 0, 255, 0, method="ciede2000")
        assert d_default == d_explicit
