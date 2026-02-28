# ColorBrew

A lightweight, zero-dependency Python library for working with colors.

## Features

- Parse colors from hex strings (`#3498db`, `#fff`, `3498db`)
- Parse CSS function strings (`rgb(52, 152, 219)`, `hsl(204, 70%, 53%)`)
- Parse CSS named colors (`cornflowerblue`, `red`, etc.)
- Convert between hex, RGB, HSL, and CMYK formats
- Input validation with clear error messages
- 148 built-in CSS named colors

## Installation

```bash
pip install colorbrew
```

Requires Python 3.12+. Zero runtime dependencies.

## Quick Start

```python
from colorbrew.converters import hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb
from colorbrew.parsing import parse_string

# Parse any color format to RGB
parse_string("#3498db")         # (52, 152, 219)
parse_string("rgb(52, 152, 219)")  # (52, 152, 219)
parse_string("cornflowerblue")  # (100, 149, 237)

# Convert between formats
hex_to_rgb("#ff0000")           # (255, 0, 0)
rgb_to_hex(52, 152, 219)       # "#3498db"
rgb_to_hsl(255, 0, 0)          # (0, 100, 50)
hsl_to_rgb(0, 100, 50)         # (255, 0, 0)
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/
```

## License

MIT
