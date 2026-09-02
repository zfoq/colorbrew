"""Bundled palette JSON resources."""

from __future__ import annotations

import json
from importlib import resources


def load_palette_json(stem: str) -> dict[str, str]:
    """Load a bundled flat palette JSON resource by file stem."""
    text = (
        resources.files("colorbrew.data.resources")
        .joinpath(f"{stem}_colors.json")
        .read_text()
    )
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid palette data for {stem!r}")
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, str)}
