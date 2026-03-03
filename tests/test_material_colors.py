"""Tests for colorbrew.material_colors — Material Design palette data integrity."""

import re

from colorbrew.material_colors import MATERIAL_COLORS

_HEX_RE = re.compile(r"^#[0-9a-f]{6}$")

_FAMILIES = [
    "red", "pink", "purple", "deep-purple", "indigo",
    "blue", "light-blue", "cyan", "teal", "green",
    "light-green", "lime", "yellow", "amber", "orange",
    "deep-orange", "brown", "grey", "blue-grey",
]

_SHADES = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]


class TestMaterialDataCompleteness:
    """Verify the Material palette has the right number of entries."""

    def test_total_count(self):
        """19 families × 10 shades = 190 colors."""
        assert len(MATERIAL_COLORS) == 190

    def test_all_families_present(self):
        """Every Material family has all 10 shades."""
        for family in _FAMILIES:
            for shade in _SHADES:
                key = f"{family}-{shade}"
                assert key in MATERIAL_COLORS, f"Missing: {key}"


class TestMaterialDataFormat:
    """Verify key and value formats."""

    def test_keys_are_lowercase(self):
        """All keys should be lowercase."""
        for key in MATERIAL_COLORS:
            assert key == key.lower(), f"Key not lowercase: {key}"

    def test_values_are_valid_hex(self):
        """All values should be 7-char hex strings like #rrggbb."""
        for key, value in MATERIAL_COLORS.items():
            assert _HEX_RE.match(value), f"Invalid hex for {key}: {value}"

    def test_key_format(self):
        """All keys should end with a numeric shade."""
        for key in MATERIAL_COLORS:
            parts = key.rsplit("-", 1)
            assert len(parts) == 2, f"Bad key format: {key}"
            assert parts[1].isdigit(), f"Shade not numeric: {key}"
