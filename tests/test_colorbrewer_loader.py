from __future__ import annotations

import json

import pytest

from colorbrew.data import loader
from colorbrew.exceptions import PaletteError


def test_colorbrewer_loader_reads_bundled_data() -> None:
    data = loader.load_colorbrewer_colors()

    assert data["Blues"]["3"] == ["#deebf7", "#9ecae1", "#3182bd"]
    assert data["RdBu"]["3"] == ["#ef8a62", "#f7f7f7", "#67a9cf"]
    assert data["Set2"]["3"] == ["#66c2a5", "#fc8d62", "#8da0cb"]


def test_colorbrewer_loader_caches_module_level_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = loader.load_colorbrewer_colors()

    def fail_files(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("cache was not used")

    monkeypatch.setattr(loader.resources, "files", fail_files)

    assert loader.load_colorbrewer_colors() is first


def test_colorbrewer_loader_wraps_malformed_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    loader._COLORBREWER_COLORS = None

    resource = type("Resource", (), {"read_text": lambda self: "{"})()
    package = type("Package", (), {"joinpath": lambda self, name: resource})()
    monkeypatch.setattr(loader.resources, "files", lambda package_name: package)

    with pytest.raises(PaletteError, match="Could not load bundled ColorBrewer data"):
        loader.load_colorbrewer_colors()


def test_colorbrewer_loader_wraps_missing_data(monkeypatch: pytest.MonkeyPatch) -> None:
    loader._COLORBREWER_COLORS = None

    def missing() -> str:
        raise FileNotFoundError("missing")

    resource = type("Resource", (), {"read_text": lambda self: missing()})()
    package = type("Package", (), {"joinpath": lambda self, name: resource})()
    monkeypatch.setattr(loader.resources, "files", lambda package_name: package)

    with pytest.raises(PaletteError, match="Could not load bundled ColorBrewer data"):
        loader.load_colorbrewer_colors()


def test_colorbrewer_loader_rejects_invalid_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    loader._COLORBREWER_COLORS = None

    resource = type(
        "Resource",
        (),
        {
            "read_text": lambda self: json.dumps(
                {"Blues": {"3": ["#deebf7", 1, "#3182bd"]}}
            )
        },
    )()
    package = type("Package", (), {"joinpath": lambda self, name: resource})()
    monkeypatch.setattr(loader.resources, "files", lambda package_name: package)

    with pytest.raises(PaletteError, match="Invalid bundled ColorBrewer data"):
        loader.load_colorbrewer_colors()
