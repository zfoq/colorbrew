from __future__ import annotations

from typing import get_args

from colorbrew.exceptions import ColorBrewError, ColorParseError, ColorValueError, PaletteError
from colorbrew.types import ColorClass, DistanceMethod, NameMatch, WcagReport


def test_types_exports_are_stdlib_runtime_values() -> None:
    assert set(get_args(DistanceMethod)) == {"euclidean", "cie76", "ciede2000"}
    assert NameMatch("red", "#ff0000", 0.0, True).exact is True
    assert WcagReport(4.5, True, False, True, False).ratio == 4.5
    assert ColorClass("red", "mid", "vivid", 0.55, 20.0).family == "red"


def test_palette_error_is_colorbrew_error() -> None:
    assert issubclass(PaletteError, ColorBrewError)


def test_existing_exception_imports_remain_compatible() -> None:
    assert issubclass(ColorValueError, ColorBrewError)
    assert issubclass(ColorParseError, ColorBrewError)
