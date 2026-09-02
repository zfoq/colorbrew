import pytest

from colorbrew import Color, Palette
from colorbrew.exceptions import ColorValueError, PaletteError
from colorbrew.palette import Theme


def test_theme_constructor_normalizes_order_and_access() -> None:
    theme = Theme({" Primary ": "#336699", "Text": (255, 255, 255)})

    assert theme.roles == ("primary", "text")
    assert theme.names == ("primary", "text")
    assert theme["PRIMARY"].hex == "#336699"
    assert theme.primary.hex == "#336699"
    assert theme.text.hex == "#ffffff"
    assert list(theme) == [Color("#336699"), Color("#ffffff")]

    with pytest.raises(KeyError):
        theme["missing"]
    with pytest.raises(AttributeError):
        theme.missing
    with pytest.raises(PaletteError):
        Theme({"Primary": "#000000", " primary ": "#ffffff"})
    with pytest.raises(ColorValueError):
        theme.primary = Color("#000000")


def test_theme_with_and_without_role_keep_originals_unchanged() -> None:
    theme = Theme({"primary": "#336699", "text": "#ffffff"})

    changed = theme.with_role(" primary ", "#000000")
    expanded = theme.with_role("Accent", "#ff0000")
    reduced = expanded.without_role("TEXT")

    assert isinstance(changed, Theme)
    assert changed.roles == ("primary", "text")
    assert changed.primary.hex == "#000000"
    assert expanded.roles == ("primary", "text", "accent")
    assert reduced.roles == ("primary", "accent")
    assert theme.as_dict() == {"primary": "#336699", "text": "#ffffff"}

    with pytest.raises(KeyError):
        theme.without_role("accent")
    with pytest.raises(PaletteError):
        Theme({"only": "#111111"}).without_role("only")


def test_theme_elementwise_operations_return_theme_and_preserve_roles() -> None:
    theme = Theme({"primary": "#336699", "text": "#ffffff"})

    lighter = theme.lighten(10)
    mixed = theme.mix(Color("#000000"), 0.5)
    blended = theme.blend(Theme({"primary": "#ffffff", "text": "#000000"}), "multiply")

    assert isinstance(lighter, Theme)
    assert isinstance(mixed, Theme)
    assert isinstance(blended, Theme)
    assert lighter.roles == theme.roles
    assert mixed.roles == theme.roles
    assert blended.roles == theme.roles
    assert lighter.primary != theme.primary
    assert theme.primary.hex == "#336699"


def test_theme_from_color_outputs_and_reports() -> None:
    theme = Theme.from_color("#336699", scheme="triadic")

    assert isinstance(theme, Theme)
    assert theme.roles == ("primary", "secondary", "accent")
    assert theme.primary.hex == "#336699"
    assert theme.as_dict()["primary"] == "#336699"
    assert (
        theme.to_css_vars()
        == "--cb-primary: #336699;\n--cb-secondary: #993366;\n--cb-accent: #669933;"
    )

    report = theme.contrast_report()
    assert set(report) == {
        ("primary", "secondary"),
        ("primary", "accent"),
        ("secondary", "accent"),
    }
    assert all(r.ratio >= 1.0 for r in report.values())

    explicit = Theme.from_color(
        "#336699", scheme="complementary", roles=("base", "opposite")
    )
    assert explicit.roles == ("base", "opposite")

    scale = Theme.from_color("#336699", scheme="scale")
    assert isinstance(scale, Palette)
    assert not isinstance(scale, Theme)
    assert scale.names == (
        "50",
        "100",
        "200",
        "300",
        "400",
        "500",
        "600",
        "700",
        "800",
        "900",
        "950",
    )

    with pytest.raises(PaletteError):
        Theme.from_color("#336699", scheme="unknown")
    with pytest.raises(PaletteError):
        Theme.from_color("#336699", scheme="triadic", roles=("primary", "secondary"))
