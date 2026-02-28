"""Custom exceptions for the ColorBrew library.

All public exceptions inherit from ``ColorBrewError`` so callers can
catch the entire family with a single ``except`` clause.
"""

from __future__ import annotations


class ColorBrewError(Exception):
    """Base exception for the ColorBrew library."""


class ColorValueError(ColorBrewError):
    """Raised when an RGB, HSL, or CMYK value is out of its valid range."""


class ColorParseError(ColorBrewError):
    """Raised when an input string cannot be parsed as a color."""
