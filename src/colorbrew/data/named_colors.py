"""CSS named colors loaded from packaged JSON data."""

from __future__ import annotations

import json
from importlib import resources


def _load() -> dict[str, str]:
    return json.loads(
        resources.files(__package__).joinpath("named_colors.json").read_text()
    )


NAMED_COLORS: dict[str, str] = _load()

__all__ = ["NAMED_COLORS"]
