# 🎨 ColorBrew

[![PyPI version](https://img.shields.io/pypi/v/colorbrew)](https://pypi.org/project/colorbrew/)
[![Python versions](https://img.shields.io/pypi/pyversions/colorbrew)](https://pypi.org/project/colorbrew/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/zfoq/colorbrew/blob/main/LICENSE)
[![Tests](https://github.com/zfoq/colorbrew/actions/workflows/tests.yml/badge.svg)](https://github.com/zfoq/colorbrew/actions)
[![PyPI downloads](https://img.shields.io/pypi/dm/colorbrew)](https://pypi.org/project/colorbrew/)

A lightweight, zero-dependency Python library for color parsing, conversion, manipulation, and accessibility analysis.

```python
from colorbrew import Color

sky = Color("#3498db")
sky.hsl                        # (204, 70, 53)
sky.lighten(20).hex            # "#8ac4ea"
sky.complementary().css_rgb    # "rgb(219, 118, 51)"
sky.meets_aa(Color("black"))   # True (contrast ratio 6.66)
```

## Why ColorBrew?

- **Zero dependencies** — pure Python, nothing to install alongside it.
- **One object, every format** — parse from hex, RGB, HSL, HSV, CMYK, or CSS named colors. Convert to any other format instantly.
- **Immutable & hashable** — `Color` instances never mutate. Safe to use as dict keys and in sets.
- **Accessibility built-in** — WCAG 2.1 luminance, contrast ratios, and AA/AAA compliance checks out of the box.
- **Color blindness simulation** — see how your colors appear to users with protanopia, deuteranopia, or tritanopia.
- **Designer-friendly** — blend modes, palettes, gradients, shade/tint/tone, warm/cool classification.

## Installation

```bash
pip install colorbrew
```

Requires Python 3.10+. Zero runtime dependencies.

## Quick Start

```python
from colorbrew import Color

# Create from any format
c = Color("#3498db")
c = Color(52, 152, 219)
c = Color("rgb(52, 152, 219)")
c = Color("cornflowerblue")

# Convert to any format — input format doesn't matter
c.hex          # "#3498db"
c.rgb          # (52, 152, 219)
c.hsl          # (204, 70, 53)
c.cmyk         # (76, 31, 0, 14)
c.hsv          # (204, 76, 86)

# CSS-ready output
c.css_rgb      # "rgb(52, 152, 219)"
c.css_hsl      # "hsl(204, 70%, 53%)"
c.css_rgba(0.5)  # "rgba(52, 152, 219, 0.5)"
f"{c:rgb}"     # "rgb(52, 152, 219)"

# Manipulate (always returns a new Color)
c.lighten(20)
c.darken(10)
c.saturate(15)
c.rotate(180)
c.invert()
c.grayscale()
c.mix(Color("red"), 0.5)
```

## Features

### Parsing & Conversion

- Hex strings (`#3498db`, `#fff`, `3498db`)
- CSS function strings (`rgb(52, 152, 219)`, `hsl(204, 70%, 53%)`)
- 148 built-in CSS named colors (`cornflowerblue`, `red`, etc.)
- Alternate constructors: `Color.from_hsl()`, `Color.from_hsv()`, `Color.from_cmyk()`, `Color.from_name()`
- Cross-format conversion between hex, RGB, HSL, CMYK, and HSV/HSB
- Format string support: `f"{color:rgb}"`, `f"{color:hsl}"`, `f"{color:hsv}"`, `f"{color:hex}"`

### Manipulation

- Lighten, darken, saturate, desaturate, rotate hue, invert, grayscale
- Mix two colors with configurable weight
- Shade (mix with black), tint (mix with white), tone (mix with gray)
- Gradient generation — interpolate between two colors in N steps
- Photoshop-style blend modes — multiply, screen, overlay, soft light, hard light, difference

### Palette Generation

- Complementary, analogous, triadic, split-complementary, tetradic
- Reverse name lookup — find the closest CSS named color with distance score

### Accessibility & Analysis

- WCAG 2.1 relative luminance and contrast ratio
- AA/AAA compliance checks (`meets_aa()`, `meets_aaa()`)
- Light/dark detection based on WCAG luminance
- Color temperature — warm/cool/neutral classification, Kelvin estimation
- Color blindness simulation — protanopia, deuteranopia, tritanopia (Viénot/Brettel matrices)

## API Examples

### Alternate Constructors

```python
Color.from_hsl(204, 70, 53)
Color.from_cmyk(76, 31, 0, 14)
Color.from_hsv(204, 76, 86)
Color.from_name("cornflowerblue")
Color.random()
```

### Cross-Format Conversion

```python
Color.from_hsl(204, 70, 53).hex       # HSL → hex
Color.from_hsv(0, 100, 100).cmyk      # HSV → CMYK
Color.from_cmyk(76, 31, 0, 14).hsl    # CMYK → HSL
Color("#3498db").hsv                   # hex → HSV
```

### Reverse Name Lookup

```python
match = Color("#3498db").closest_name
match.name       # "dodgerblue"
match.distance   # 42.9418
match.exact      # False
```

### Shade, Tint, Tone & Gradients

```python
c = Color("#3498db")
c.shade(0.5)                # darken by mixing with black
c.tint(0.5)                 # lighten by mixing with white
c.tone(0.5)                 # mute by mixing with gray
c.gradient(Color("red"), 5) # 5-step gradient
```

### Blend Modes

```python
c.blend(Color("white"), "multiply")
c.blend(Color("black"), "screen")
```

### Palette Generation

```python
c.complementary()           # opposite hue
c.analogous()               # 3 neighboring hues
c.triadic()                 # 2 colors at 120° intervals
c.split_complementary()     # 2 colors flanking the complement
c.tetradic()                # 3 colors at 90° intervals
```

### Accessibility (WCAG 2.1)

```python
c = Color("#3498db")
c.luminance                    # relative luminance (0.0–1.0)
c.is_light                     # False
c.contrast(Color("black"))     # contrast ratio (1.0–21.0)
c.meets_aa(Color("black"))     # True if passes WCAG AA
c.meets_aaa(Color("black"))    # True if passes WCAG AAA
```

### Color Temperature

```python
c.temperature   # "warm", "cool", or "neutral"
c.kelvin        # estimated Kelvin (1000–40000)
```

### Color Blindness Simulation

```python
c.simulate_colorblind("protanopia")    # red-blind
c.simulate_colorblind("deuteranopia")  # green-blind
c.simulate_colorblind("tritanopia")    # blue-blind
```

### Iteration & Comparison

```python
r, g, b = Color("#3498db")          # unpack RGB
Color("#ff0000") == Color("red")    # True
```

## Standalone Converter Functions

For cases where you don't need the full `Color` class:

```python
from colorbrew import rgb_to_hex, hex_to_rgb, rgb_to_hsl, hsl_to_rgb
from colorbrew import rgb_to_hsv, hsv_to_rgb, rgb_to_cmyk, cmyk_to_rgb

rgb_to_hex(52, 152, 219)    # "#3498db"
hex_to_rgb("#3498db")        # (52, 152, 219)
rgb_to_hsl(255, 0, 0)       # (0, 100, 50)
hsl_to_rgb(0, 100, 50)      # (255, 0, 0)
rgb_to_hsv(255, 0, 0)       # (0, 100, 100)
hsv_to_rgb(0, 100, 100)     # (255, 0, 0)
rgb_to_cmyk(255, 0, 0)      # (0, 100, 100, 0)
cmyk_to_rgb(0, 100, 100, 0) # (255, 0, 0)
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/
```

## Contributing

Contributions are welcome! Please [open an issue](https://github.com/zfoq/colorbrew/issues) first to discuss what you'd like to change. Pull requests for bug fixes, new features, and documentation improvements are all appreciated.

## Changelog

See [Releases](https://github.com/zfoq/colorbrew/releases) for a full list of changes.

## License

[MIT](https://github.com/zfoq/colorbrew/blob/main/LICENSE)