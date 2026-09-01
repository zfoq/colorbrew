"""Single loader for all bundled palette JSON resources."""

from __future__ import annotations

import json
from importlib import resources


def _load_palette(name: str) -> dict[str, str]:
    """Load a bundled palette JSON resource by file stem."""
    return json.loads(
        resources.files(__package__).joinpath(f"{name}_colors.json").read_text()
    )


NAMED_COLORS: dict[str, str] = _load_palette("named")
TAILWIND_COLORS: dict[str, str] = _load_palette("tailwind")
MATERIAL_COLORS: dict[str, str] = _load_palette("material")

__all__ = ["MATERIAL_COLORS", "NAMED_COLORS", "TAILWIND_COLORS"]
