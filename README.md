# ColorBrew

A lightweight, zero-dependency Python library for working with colors.

## Features

- Parse colors from hex strings (`#3498db`, `#fff`, `3498db`)
- Parse CSS function strings (`rgb(52, 152, 219)`, `hsl(204, 70%, 53%)`)
- Parse CSS named colors (`cornflowerblue`, `red`, etc.)
- Convert between hex, RGB, HSL, and CMYK formats
- Input validation with clear error messages
- 148 built-in CSS named colors
- Immutable `Color` class with format properties and dunder methods
- CSS/HTML-ready output (`rgb()`, `rgba()`, `hsl()`, `hsla()`, hex)
- Format string support (`f"{color:rgb}"`, `f"{color:hsl}"`)
- Reverse name lookup — find the closest CSS named color with distance score
- Color manipulation — lighten, darken, saturate, desaturate, rotate hue, invert, grayscale, mix
- Photoshop-style blend modes — multiply, screen, overlay, soft light, hard light, difference
- Palette generation — complementary, analogous, triadic, split-complementary, tetradic

## Installation

```bash
pip install colorbrew
```

Requires Python 3.12+. Zero runtime dependencies.

## Quick Start

```python
from colorbrew import Color

# Create from any format
c = Color("#3498db")
c = Color(52, 152, 219)
c = Color("rgb(52, 152, 219)")
c = Color("cornflowerblue")

# Alternate constructors
c = Color.from_hsl(204, 70, 53)
c = Color.from_cmyk(76, 31, 0, 14)
c = Color.from_name("cornflowerblue")

# Access format properties
c.rgb                       # (52, 152, 219)
c.hex                       # "#3498db"
c.hsl                       # (204, 70, 53)
c.cmyk                      # (76, 31, 0, 14)

# CSS output
c.css_rgb                   # "rgb(52, 152, 219)"
c.css_hsl                   # "hsl(204, 70%, 53%)"
c.css_hex                   # "#3498db"
c.css_rgba(0.5)             # "rgba(52, 152, 219, 0.5)"
c.css_hsla(0.8)             # "hsla(204, 70%, 53%, 0.8)"

# Format strings
f"{c:rgb}"                  # "rgb(52, 152, 219)"
f"{c:hsl}"                  # "hsl(204, 70%, 53%)"
f"{c:hex}"                  # "#3498db"

# Reverse name lookup
match = c.closest_name
match.name                  # "steelblue"
match.distance              # 10.7703
match.exact                 # False

# Manipulation (all return new Color instances)
c.lighten(20)               # lighter color
c.darken(10)                # darker color
c.saturate(15)              # more vivid
c.desaturate(15)            # more muted
c.rotate(180)               # shift hue
c.invert()                  # RGB inverse
c.grayscale()               # remove saturation
c.mix(Color("red"), 0.5)    # blend two colors

# Blend modes
c.blend(Color("white"), "multiply")   # multiply blend
c.blend(Color("black"), "screen")     # screen blend

# Palette generation
c.complementary()              # opposite hue
c.analogous()                  # 3 neighboring hues
c.triadic()                    # 2 colors at 120° intervals
c.split_complementary()        # 2 colors flanking the complement
c.tetradic()                   # 3 colors at 90° intervals

# Iteration and comparison
r, g, b = c                 # unpack RGB
Color("#ff0000") == Color("red")  # True
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/
```

## License

MIT
