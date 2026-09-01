"""Tailwind CSS v3 color palette loaded from packaged JSON data."""

from __future__ import annotations

import json
from importlib import resources


def _load() -> dict[str, str]:
    return json.loads(
        resources.files(__package__).joinpath("tailwind_colors.json").read_text()
    )


TAILWIND_COLORS: dict[str, str] = _load()

__all__ = ["TAILWIND_COLORS"]
