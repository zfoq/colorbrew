"""Material Design v2 color palette loaded from packaged JSON data."""

from __future__ import annotations

import json
from importlib import resources


def _load() -> dict[str, str]:
    return json.loads(
        resources.files(__package__).joinpath("material_colors.json").read_text()
    )


MATERIAL_COLORS: dict[str, str] = _load()

__all__ = ["MATERIAL_COLORS"]
