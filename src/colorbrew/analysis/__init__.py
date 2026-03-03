"""Color analysis — contrast, naming, temperature, color blindness."""

from __future__ import annotations

from colorbrew.analysis.colorblind import simulate
from colorbrew.analysis.contrast import (
    contrast_ratio,
    is_dark,
    is_light,
    meets_aa,
    meets_aaa,
    relative_luminance,
)
from colorbrew.analysis.naming import (
    find_closest_material,
    find_closest_name,
    find_closest_tailwind,
)
from colorbrew.analysis.temperature import classify_temperature, estimate_kelvin

__all__ = [
    "classify_temperature",
    "contrast_ratio",
    "estimate_kelvin",
    "find_closest_material",
    "find_closest_name",
    "find_closest_tailwind",
    "is_dark",
    "is_light",
    "meets_aa",
    "meets_aaa",
    "relative_luminance",
    "simulate",
]
