"""Single loader for all bundled palette JSON resources."""

from __future__ import annotations

import json
from importlib import resources
from typing import TypeAlias

from colorbrew.exceptions import PaletteError

ColorBrewerColors: TypeAlias = dict[str, dict[str, list[str]]]


_RESOURCE_PACKAGE = "colorbrew.data.resources"


def _load_palette(name: str) -> dict[str, str]:
    """Load a bundled palette JSON resource by file stem."""
    return json.loads(
        resources.files(_RESOURCE_PACKAGE).joinpath(f"{name}_colors.json").read_text()
    )


def _invalid_colorbrewer_data() -> PaletteError:
    return PaletteError("Invalid bundled ColorBrewer data.")


def _validate_colorbrewer_colors(data: object) -> ColorBrewerColors:
    if not isinstance(data, dict):
        raise _invalid_colorbrewer_data()

    colors: ColorBrewerColors = {}
    for scheme, sizes in data.items():
        if not isinstance(scheme, str) or not isinstance(sizes, dict):
            raise _invalid_colorbrewer_data()
        colors[scheme] = {}
        for size, values in sizes.items():
            if (
                not isinstance(size, str)
                or not isinstance(values, list)
                or not all(isinstance(value, str) for value in values)
            ):
                raise _invalid_colorbrewer_data()
            colors[scheme][size] = values
    return colors


_COLORBREWER_COLORS: ColorBrewerColors | None = None


def load_colorbrewer_colors() -> ColorBrewerColors:
    """Load bundled ColorBrewer schemes."""
    global _COLORBREWER_COLORS
    if _COLORBREWER_COLORS is None:
        try:
            data = json.loads(
                resources.files(_RESOURCE_PACKAGE)
                .joinpath("colorbrewer_colors.json")
                .read_text()
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise PaletteError("Could not load bundled ColorBrewer data.") from exc
        _COLORBREWER_COLORS = _validate_colorbrewer_colors(data)
    return _COLORBREWER_COLORS


NAMED_COLORS: dict[str, str] = _load_palette("named")
TAILWIND_COLORS: dict[str, str] = _load_palette("tailwind")
MATERIAL_COLORS: dict[str, str] = _load_palette("material")

__all__ = [
    "ColorBrewerColors",
    "MATERIAL_COLORS",
    "NAMED_COLORS",
    "TAILWIND_COLORS",
    "load_colorbrewer_colors",
]
