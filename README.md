# ColorBrew

A lightweight, zero-dependency Python library for working with colors.

## Features

- Parse colors from hex strings (`#3498db`, `#fff`, `3498db`)
- Parse CSS function strings (`rgb(52, 152, 219)`, `hsl(204, 70%, 53%)`)
- Parse CSS named colors (`cornflowerblue`, `red`, etc.)
- Convert between hex, RGB, HSL, CMYK, and HSV/HSB formats
- Input validation with clear error messages
- 148 built-in CSS named colors
- Immutable `Color` class with format properties and dunder methods
- CSS/HTML-ready output (hex, `rgb()`, `rgba()`, `hsl()`, `hsla()`, `hsv()`)
- Format string support (`f"{color:rgb}"`, `f"{color:hsl}"`, `f"{color:hsv}"`)
- Reverse name lookup — find the closest CSS named color with distance score
- Color manipulation — lighten, darken, saturate, desaturate, rotate hue, invert, grayscale, mix
- Shade, tint, tone — mix with black, white, or gray
- Gradient generation — interpolate between two colors
- Light/dark detection — `is_light` / `is_dark` based on WCAG luminance
- Photoshop-style blend modes — multiply, screen, overlay, soft light, hard light, difference
- Palette generation — complementary, analogous, triadic, split-complementary, tetradic
- WCAG accessibility — luminance, contrast ratio, AA/AAA compliance checks
- Color temperature — warm/cool/neutral classification, Kelvin estimation
- Color blindness simulation — protanopia, deuteranopia, tritanopia (Viénot/Brettel matrices)

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
c = Color.from_hsv(204, 76, 86)
c = Color.from_name("cornflowerblue")

# Access any format — input format doesn't matter
c.rgb                       # (52, 152, 219)
c.hex                       # "#3498db"
c.hsl                       # (204, 70, 53)
c.cmyk                      # (76, 31, 0, 14)
c.hsv                       # (204, 76, 86)

# Cross-format conversion — any format in, any format out
Color.from_hsl(204, 70, 53).hex       # HSL → hex
Color.from_hsv(0, 100, 100).cmyk      # HSV → CMYK
Color.from_cmyk(76, 31, 0, 14).hsl    # CMYK → HSL
Color("#3498db").hsv                   # hex → HSV

# CSS output
c.css_rgb                   # "rgb(52, 152, 219)"
c.css_hsl                   # "hsl(204, 70%, 53%)"
c.css_hex                   # "#3498db"
c.css_rgba(0.5)             # "rgba(52, 152, 219, 0.5)"
c.css_hsla(0.8)             # "hsla(204, 70%, 53%, 0.8)"

# Format strings
f"{c:rgb}"                  # "rgb(52, 152, 219)"
f"{c:hsl}"                  # "hsl(204, 70%, 53%)"
f"{c:hsv}"                  # "hsv(204, 76%, 86%)"
f"{c:hex}"                  # "#3498db"

# Reverse name lookup
match = c.closest_name
match.name                  # "dodgerblue"
match.distance              # 42.9418
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
c.shade(0.5)                # darken by mixing with black
c.tint(0.5)                 # lighten by mixing with white
c.tone(0.5)                 # mute by mixing with gray
c.gradient(Color("red"), 5) # 5-step gradient

# Light/dark detection
c.is_light                     # True (luminance > 0.5)
c.is_dark                      # False

# Blend modes
c.blend(Color("white"), "multiply")   # multiply blend
c.blend(Color("black"), "screen")     # screen blend

# Palette generation
c.complementary()              # opposite hue
c.analogous()                  # 3 neighboring hues
c.triadic()                    # 2 colors at 120° intervals
c.split_complementary()        # 2 colors flanking the complement
c.tetradic()                   # 3 colors at 90° intervals

# Accessibility (WCAG 2.1)
c.luminance                    # relative luminance (0.0-1.0)
c.contrast(Color("white"))     # contrast ratio (1.0-21.0)
c.meets_aa(Color("white"))     # True if passes WCAG AA
c.meets_aaa(Color("white"))    # True if passes WCAG AAA

# Color temperature
c.temperature                  # "warm", "cool", or "neutral"
c.kelvin                       # estimated Kelvin (1000-40000)

# Color blindness simulation
c.simulate_colorblind("protanopia")    # red-blind
c.simulate_colorblind("deuteranopia")  # green-blind
c.simulate_colorblind("tritanopia")    # blue-blind

# Iteration and comparison
r, g, b = c                 # unpack RGB
Color("#ff0000") == Color("red")  # True
```

## Standalone Converter Functions

For cases where you don't need the full `Color` class, all converter functions are available directly:

```python
from colorbrew import rgb_to_hex, hex_to_rgb, rgb_to_hsl, hsl_to_rgb
from colorbrew import rgb_to_hsv, hsv_to_rgb, rgb_to_cmyk, cmyk_to_rgb

rgb_to_hex(52, 152, 219)       # "#3498db"
hex_to_rgb("#3498db")        # (52, 152, 219)
rgb_to_hsl(255, 0, 0)          # (0, 100, 50)
hsl_to_rgb(0, 100, 50)         # (255, 0, 0)
rgb_to_hsv(255, 0, 0)          # (0, 100, 100)
hsv_to_rgb(0, 100, 100)        # (255, 0, 0)
rgb_to_cmyk(255, 0, 0)         # (0, 100, 100, 0)
cmyk_to_rgb(0, 100, 100, 0)    # (255, 0, 0)
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/
```

## License

MIT
