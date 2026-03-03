"""Color analysis — contrast, naming, temperature, color blindness, distance."""

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
from colorbrew.analysis.delta_e import (
    delta_e_76,
    delta_e_2000,
    distance,
    euclidean_rgb,
    rgb_to_lab,
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
    "delta_e_76",
    "delta_e_2000",
    "distance",
    "estimate_kelvin",
    "euclidean_rgb",
    "find_closest_material",
    "find_closest_name",
    "find_closest_tailwind",
    "is_dark",
    "is_light",
    "meets_aa",
    "meets_aaa",
    "relative_luminance",
    "rgb_to_lab",
    "simulate",
]
