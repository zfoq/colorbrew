from collections.abc import Callable
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
    assert record.version == "v3"
    assert record.source == "bundled"
    assert isinstance(record.entries, Callable)
    assert isinstance(record.palettes, Callable)
    assert isinstance(record.entries(), MappingProxyType)
    assert isinstance(record.palettes(), MappingProxyType)

    with pytest.raises(Exception):
        record.name = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        record.entries()["v3"] = {}  # type: ignore[index]


def test_registry_resolves_names_and_registers_custom_systems() -> None:
    record = register_system(
        "Example",
        version="V1",
        entries={"brand": "#123456"},
        palettes={
            "V1": Palette.from_mapping(
                {"brand": "#123456"},
                kind="system",
                system="example",
                version="v1",
                source="custom",
            ),
        },
    )

    assert record.name == "example"
    assert record.version == "v1"
    assert resolve_name("example@V1") == ("example", "v1")
    assert "example" in list_systems()
    assert list_palettes("example") == ("example", "example@v1")
    assert get_palette("example").get("brand").hex == "#123456"


def test_registry_colorbrewer_scheme_count_palettes_and_lazy_palette_import() -> None:
    palette = get_palette("colorbrewer:Blues-3")

    assert isinstance(palette, Palette)
    assert palette.hexes == ("#deebf7", "#9ecae1", "#3182bd")
    assert "colorbrewer:blues-3" in list_palettes("colorbrewer")


def test_registry_rejects_unknown_values() -> None:
    with pytest.raises(ColorValueError):
        get_system("missing")
    with pytest.raises(ColorValueError):
        get_palette("tailwind@missing")
    with pytest.raises(ColorValueError):
        get_palette("colorbrewer:Missing-3")


@pytest.mark.parametrize(
    ("name", "expected_size"),
    [
        ("colorbrewer:Blues-3", 3),
        ("colorbrewer:BuPu-5", 5),
        ("colorbrewer:Set3-12", 12),
    ],
)
def test_registry_colorbrewer_palettes_by_scheme_and_size(
    name: str, expected_size: int
) -> None:
    palette = get_palette(name)
    assert isinstance(palette, Palette)
    assert len(palette) == expected_size
    assert palette.system == "colorbrewer"
    assert palette.source == "bundled"


def test_registry_lists_colorbrewer_palettes() -> None:
    names = list_palettes("colorbrewer")
    assert "colorbrewer:blues-3" in names
    assert "colorbrewer:bupu-5" in names
    assert "colorbrewer:set3-12" in names


def test_palette_from_system_colorbrewer() -> None:
    palette = Palette.from_system("colorbrewer:Blues-3")
    assert isinstance(palette, Palette)
    assert len(palette) == 3
    assert palette.system == "colorbrewer"
    assert palette.source == "bundled"
