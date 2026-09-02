"""Tests for the immutable Palette API."""

import pytest

from colorbrew import Color, Palette
from colorbrew.exceptions import ColorValueError, PaletteError


def test_palette_constructor_coerces_names_and_is_immutable():
    palette = Palette(
        [Color("red"), "#00ff00", (0, 0, 255)], names=[" Red ", None, "Blue"]
    )

    assert palette.hexes == ("#ff0000", "#00ff00", "#0000ff")
    assert palette.names == ("red", None, "blue")
    assert list(palette) == [Color("red"), Color("#00ff00"), Color("blue")]
    assert palette["RED"] == Color("red")
    assert palette[1:].names == (None, "blue")
    assert palette.as_dict() == {"red": "#ff0000", "blue": "#0000ff"}
    assert palette.items() == (("red", Color("red")), ("blue", Color("blue")))
    assert "red" in palette
    assert Color("blue") in palette
    with pytest.raises(ColorValueError):
        palette._colors = ()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"colors": [], "names": []},
        {"colors": ["red"], "names": ["red", "blue"]},
        {"colors": ["red", "blue"], "names": ["same", " same "]},
    ],
)
def test_palette_validates_constructor(kwargs):
    with pytest.raises(PaletteError):
        Palette(**kwargs)


def test_palette_set_ops_preserve_first_names():
    first = Palette(["red", "green"], names=["red", "green"])
    second = Palette(["green", "blue"], names=["lime", "blue"])

    assert (first | second).items() == (
        ("red", Color("red")),
        ("green", Color("green")),
        ("blue", Color("blue")),
    )
    assert (first & second).items() == (("green", Color("green")),)
    assert (first - second).items() == (("red", Color("red")),)


def test_palette_map_and_binary_operations_preserve_metadata_and_validate_lengths():
    palette = Palette(
        ["red", "blue"],
        names=["red", "blue"],
        kind="brand",
        system="x",
        version="1",
        source="test",
    )

    lighter = palette.lighten(5)
    assert lighter.names == palette.names
    assert (lighter.kind, lighter.system, lighter.version, lighter.source) == (
        "brand",
        "x",
        "1",
        "test",
    )

    mixed = palette.mix(Color("white"), 0.5)
    assert mixed.names == palette.names
    assert palette.blend(Palette(["white", "black"])).names == palette.names
    with pytest.raises(PaletteError):
        palette.mix(Palette(["white"]))


def test_palette_aggregate_methods_and_system_mapping():
    palette = Palette(["red", "#ff0101", "blue"], names=["red", "near-red", "blue"])

    assert len(palette.distance_matrix()) == 3
    assert all(len(row) == 3 for row in palette.distance_matrix())
    assert len(palette.contrast_matrix()) == 3
    index, color, distance = palette.nearest(Color("#fe0000"))
    assert (index, color) == (0, Color("red"))
    assert distance >= 0
    assert palette.sort("name").names == ("blue", "near-red", "red")
    assert palette.dedupe(threshold=2, method="euclidean").hexes == (
        "#ff0000",
        "#0000ff",
    )
    assert isinstance(palette.is_colorblind_safe(), bool)
    assert len(palette.classify()) == 3
    assert palette.nearest_names("css")[0].name == "red"
    assert palette.to_system("css").hexes[0] == "#ff0000"


def test_palette_gradient_and_resample_return_square_count():
    palette = Palette(["red", "blue"])

    assert palette.resample(5).hexes[0] == "#ff0000"
    assert palette.resample(5).hexes[-1] == "#0000ff"
    assert len(palette.gradient(steps=4)) == 4
    assert len(Palette(["red"]).gradient(Color("blue"), steps=3)) == 3
