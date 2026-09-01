"""Palette models for bundled and upstream-loaded palette data."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Palette(Mapping[str, str]):
    """A normalized palette payload with source metadata.

    ``Palette`` behaves like a read-only mapping of color names to hex
    strings, so existing code that subscripts or iterates over a palette
    continues to work. Use :meth:`as_dict` (or :func:`get_palette_entries`)
    when a plain ``dict[str, str]`` is required.
    """

    family: str
    version: str
    entries: dict[str, str]
    source: str = "bundled"

    @staticmethod
    def _normalize_key(name: str) -> str:
        return name.lower().strip()

    def __getitem__(self, key: str) -> str:
        return self.entries[self._normalize_key(key)]

    def __iter__(self) -> Iterator[str]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __hash__(self) -> int:
        return hash(
            (self.family, self.version, self.source, frozenset(self.entries.items()))
        )

    def get(self, name: str, default: str | None = None) -> str | None:
        """Return an entry by name, with case-insensitive key lookup."""
        return self.entries.get(self._normalize_key(name), default)

    def as_dict(self) -> dict[str, str]:
        """Return a shallow copy of the entries as a plain dict."""
        return dict(self.entries)
