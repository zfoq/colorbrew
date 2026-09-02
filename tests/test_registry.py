from types import MappingProxyType

import pytest

from colorbrew.data.registry import (
    SystemRecord,
    get_palette,
    get_system,
    list_palettes,
    list_systems,
    register_system,
    resolve_name,
)
from colorbrew.exceptions import ColorValueError
from colorbrew.palette import Palette


def test_registry_exposes_frozen_system_records() -> None:
    assert list_systems()[:4] == ("css", "tailwind", "material", "colorbrewer")
    record = get_system("tailwind")
    assert isinstance(record, SystemRecord)
    assert record.default_version == "v3"
    assert isinstance(record.palettes, MappingProxyType)

    with pytest.raises(Exception):
        record.name = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        record.palettes["v3"] = {}  # type: ignore[index]


def test_registry_resolves_names_and_registers_custom_systems() -> None:
    record = register_system(
        "Example",
        default_version="V1",
        palettes={"V1": {"brand": "#123456"}},
    )

    assert record.name == "example"
    assert resolve_name("example@V1") == ("example", "v1")
    assert "example" in list_systems()
    assert list_palettes("example") == ("example", "example@v1")
    assert get_palette("example").get("brand") == "#123456"


def test_registry_colorbrewer_scheme_count_palettes_and_lazy_palette_import() -> None:
    palette = get_palette("colorbrewer:Blues-3")

    assert isinstance(palette, Palette)
    assert palette.hexes == ("#deebf7", "#9ecae1", "#3182bd")
    assert "colorbrewer:Blues-3" in list_palettes("colorbrewer")


def test_registry_rejects_unknown_values() -> None:
    with pytest.raises(ColorValueError):
        get_system("missing")
    with pytest.raises(ColorValueError):
        get_palette("tailwind@missing")
    with pytest.raises(ColorValueError):
        get_palette("colorbrewer:Missing-3")
