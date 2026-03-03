"""Tests for colorbrew.tailwind_colors — Tailwind CSS palette data integrity."""

import re

from colorbrew.data.tailwind_colors import TAILWIND_COLORS

_HEX_RE = re.compile(r"^#[0-9a-f]{6}$")

_FAMILIES = [
    "slate", "gray", "zinc", "neutral", "stone",
    "red", "orange", "amber", "yellow", "lime",
    "green", "emerald", "teal", "cyan", "sky",
    "blue", "indigo", "violet", "purple", "fuchsia",
    "pink", "rose",
]

_SHADES = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]


class TestTailwindDataCompleteness:
    """Verify the Tailwind palette has the right number of entries."""

    def test_total_count(self):
        """22 families × 11 shades = 242 colors."""
        assert len(TAILWIND_COLORS) == 242

    def test_all_families_present(self):
        """Every Tailwind family has all 11 shades."""
        for family in _FAMILIES:
            for shade in _SHADES:
                key = f"{family}-{shade}"
                assert key in TAILWIND_COLORS, f"Missing: {key}"


class TestTailwindDataFormat:
    """Verify key and value formats."""

    def test_keys_are_lowercase(self):
        """All keys should be lowercase."""
        for key in TAILWIND_COLORS:
            assert key == key.lower(), f"Key not lowercase: {key}"

    def test_values_are_valid_hex(self):
        """All values should be 7-char hex strings like #rrggbb."""
        for key, value in TAILWIND_COLORS.items():
            assert _HEX_RE.match(value), f"Invalid hex for {key}: {value}"

    def test_key_format(self):
        """All keys should match family-shade pattern."""
        for key in TAILWIND_COLORS:
            parts = key.rsplit("-", 1)
            assert len(parts) == 2, f"Bad key format: {key}"
            assert parts[1].isdigit(), f"Shade not numeric: {key}"
