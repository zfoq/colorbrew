# 🎨 ColorBrew

[![PyPI version](https://img.shields.io/pypi/v/colorbrew)](https://pypi.org/project/colorbrew/)
[![Python versions](https://img.shields.io/pypi/pyversions/colorbrew)](https://pypi.org/project/colorbrew/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/zfoq/colorbrew/blob/main/LICENSE)
[![Tests](https://github.com/zfoq/colorbrew/actions/workflows/ci.yml/badge.svg)](https://github.com/zfoq/colorbrew/actions)
[![PyPI downloads](https://img.shields.io/pypi/dm/colorbrew)](https://pypi.org/project/colorbrew/)

A lightweight, zero-dependency Python library for color manipulation, conversion, and accessibility analysis.

```python
from colorbrew import Color

brand = Color("#3498db")
brand.lighten(20).hex                          # "#8ac4ea"
brand.with_alpha(0.8).css_rgb_modern()         # "rgb(52 152 219 / 0.8)"
brand.meets_aa(Color("white"))                 # True
brand.suggest_text_color()                     # Color('#000000')
brand.scale()[500]                             # Color('#2986c7')
```

## Why ColorBrew?

- **Zero dependencies** — pure Python, nothing to install.
- **One object, every format** — hex, RGB, HSL, HSV, CMYK, Lab, CSS named colors. Parse any, convert to all.
- **Alpha channel** — first-class support for transparency in hex, CSS, and all transforms.
- **CSS Color Level 4** — parse and output modern `rgb(52 152 219 / 0.8)` syntax.
- **Immutable & hashable** — safe to use as dict keys and in sets.
- **WCAG accessibility** — contrast ratios, AA/AAA checks, auto text color, accessible color finder.
- **Perceptual color science** — CIE L\*a\*b\*, CIEDE2000, Lab-space gradients.
- **Designer tools** — palettes, blend modes, shade scales, color temperature, colorblind simulation.
- **Fully typed** — ships with `py.typed` marker; all parameters use `Literal` types for autocomplete.

## Installation

```bash
pip install colorbrew
```

Requires Python 3.10+.

---

## Quick Start

### Creating Colors

```python
from colorbrew import Color

# From hex (3, 4, 6, or 8 digits)
c = Color("#3498db")
c = Color("#3498db80")       # with alpha

# From RGB integers
c = Color(52, 152, 219)

# From CSS strings (legacy and modern)
c = Color("rgb(52, 152, 219)")
c = Color("rgb(52 152 219 / 0.8)")
c = Color("hsl(204 70% 53%)")
c = Color("hsla(204, 70%, 53%, 0.5)")

# From CSS named colors
c = Color("cornflowerblue")

# From other color spaces
c = Color.from_hsl(204, 70, 53)
c = Color.from_hsv(204, 76, 86)
c = Color.from_cmyk(76, 31, 0, 14)
c = Color.from_lab(61.0, -3.4, -38.3)

# From built-in palettes
c = Color.from_tailwind("sky-500")
c = Color.from_material("blue-600")
c = Color.from_name("steelblue")

# Random
c = Color.random()
```

### Converting Between Formats

Every property returns the same color in a different format — input format doesn't matter:

```python
c = Color("#3498db")

c.rgb          # (52, 152, 219)
c.hex          # "#3498db"
c.hsl          # (204, 70, 53)
c.hsv          # (204, 76, 86)
c.cmyk         # (76, 31, 0, 14)
c.lab          # (61.0, -3.4, -38.3)
c.r, c.g, c.b  # 52, 152, 219
```

### CSS Output

```python
c = Color("#3498db")

# Legacy syntax
c.css_rgb              # "rgb(52, 152, 219)"
c.css_hsl              # "hsl(204, 70%, 53%)"
c.css_rgba(0.5)        # "rgba(52, 152, 219, 0.5)"
c.css_hsla(0.5)        # "hsla(204, 70%, 53%, 0.5)"

# Modern CSS Color Level 4 syntax
c.css_rgb_modern()     # "rgb(52 152 219)"
c.with_alpha(0.8).css_rgb_modern()  # "rgb(52 152 219 / 0.8)"
c.css_hsl_modern()     # "hsl(204 70% 53%)"

# Format strings
f"{c:hex}"             # "#3498db"
f"{c:rgb}"             # "rgb(52, 152, 219)"
f"{c:hsl}"             # "hsl(204, 70%, 53%)"
```

---

## Alpha Channel

Full transparency support — parsed from input, preserved through transforms, output in CSS:

```python
# Parse alpha from any format
c = Color("#3498db80")                # 8-digit hex
c = Color("rgba(52, 152, 219, 0.5)")  # legacy CSS
c = Color("rgb(52 152 219 / 0.5)")    # modern CSS

c.alpha          # 0.5
c.rgba           # (52, 152, 219, 0.5)
c.hex            # "#3498db80"

# Modify alpha
c.with_alpha(0.3)  # new Color with alpha 0.3
c.opaque           # new Color with alpha 1.0

# Transforms preserve alpha
c.lighten(20).alpha       # 0.5 (unchanged)
c.complementary().alpha   # 0.5 (unchanged)

# Mix interpolates alpha
Color("#ff000080").mix(Color("#0000ff"), 0.5).alpha  # 0.75
```

---

## Color Manipulation

All methods return new `Color` instances — nothing is mutated:

```python
c = Color("#3498db")

# Lightness & saturation
c.lighten(20)           # increase lightness by 20%
c.darken(10)            # decrease lightness by 10%
c.saturate(15)          # increase saturation by 15%
c.desaturate(25)        # decrease saturation by 25%

# Hue
c.rotate(180)           # shift hue by 180 degrees
c.complementary()       # shortcut for rotate(180)

# Special transforms
c.invert()              # RGB inverse (255 - each channel)
c.grayscale()           # remove saturation

# Mixing
c.mix(Color("red"), 0.5)  # 50/50 blend in RGB space
c.shade(0.3)              # mix with black (darken)
c.tint(0.3)               # mix with white (lighten)
c.tone(0.3)               # mix with gray (mute)
```

### Gradients

Generate smooth color ramps between two colors:

```python
# RGB interpolation (default)
c.gradient(Color("red"), steps=7)

# Lab interpolation (perceptually uniform)
c.gradient(Color("red"), steps=7, space="lab")
```

Lab-space gradients avoid the muddy midpoints you get with RGB interpolation — colors stay vibrant through the transition.

---

## Palette Generation

### Color Harmonies

```python
c = Color("#3498db")

c.complementary()            # 1 color — opposite hue (180°)
c.analogous()                # 3 colors — neighboring hues (30° apart)
c.analogous(n=5, step=15)    # customize count and spacing
c.triadic()                  # 2 colors — 120° intervals
c.split_complementary()      # 2 colors — flanking the complement
c.tetradic()                 # 3 colors — 90° intervals
```

### Shade Scales

Generate Tailwind-like 50–950 shade scales from any color:

```python
scale = Color("#3498db").scale()

scale[50]     # lightest
scale[500]    # mid-tone (closest to original)
scale[950]    # darkest

# Use in a design system
for step, color in scale.items():
    print(f"--brand-{step}: {color.hex};")
```

Output:

```css
--brand-50: #e2f0f9;
--brand-100: #cde5f5;
--brand-200: #a5d0ee;
--brand-300: #6db4e4;
--brand-400: #3e9cdb;
--brand-500: #2986c7;
--brand-600: #226fa6;
--brand-700: #1b5885;
--brand-800: #133c5c;
--brand-900: #0e2d46;
--brand-950: #091c2c;
```

### Reverse Name Lookup

Find the closest named color from built-in palettes:

```python
match = Color("#3498db").closest_name()
match.name       # "dodgerblue"
match.hex        # "#1e90ff"
match.distance   # 42.94
match.exact      # False

# Tailwind and Material Design lookups
Color("#3498db").closest_tailwind()    # NameMatch("sky-500", ...)
Color("#3498db").closest_material()    # NameMatch("blue-400", ...)

# Use perceptual distance for better accuracy
Color("#3498db").closest_name(method="ciede2000")
```

Available palettes: 148 CSS named colors, 264 Tailwind CSS colors, 210 Material Design colors.

---

## Accessibility (WCAG 2.1)

### Contrast Checking

```python
bg = Color("#1a1a2e")
text = Color("#e0e0e0")

bg.contrast(text)              # 12.72 (contrast ratio 1:1 to 21:1)
bg.meets_aa(text)              # True  (≥ 4.5:1)
bg.meets_aaa(text)             # True  (≥ 7:1)
bg.meets_aa(text, large=True)  # True  (large text: ≥ 3:1)
```

### Auto Text Color

Choose black or white text for maximum readability on any background:

```python
bg = Color("#3498db")
bg.suggest_text_color()   # Color('#000000') — black is more readable

bg = Color("#1a1a2e")
bg.suggest_text_color()   # Color('#ffffff') — white is more readable
```

### Accessible Color Finder

Have a brand color that doesn't pass contrast? Find the closest shade that does:

```python
bg = Color("#ffffff")
brand = Color("#99ccff")         # too light for white bg

# Find the closest color to brand that passes AA
accessible = bg.find_accessible_color(brand, level="aa")
accessible.hex                   # darker shade that passes 4.5:1

# AAA level
accessible = bg.find_accessible_color(brand, level="aaa")
```

### Luminance & Light/Dark Detection

```python
c = Color("#3498db")
c.luminance     # 0.29 (WCAG relative luminance)
c.is_light      # False
c.is_dark       # True
```

---

## Perceptual Color Distance

Compare colors using human-perception-aware algorithms:

```python
a = Color("#3498db")
b = Color("#2ecc71")

# CIEDE2000 — best perceptual accuracy (default)
a.distance(b)                            # 34.18

# CIE76 — faster, less accurate
a.distance(b, method="cie76")            # 44.57

# Euclidean RGB — simple, not perceptual
a.distance(b, method="euclidean")        # 158.69
```

### Standalone Functions

```python
from colorbrew import rgb_to_lab, lab_to_rgb, delta_e_76, delta_e_2000

lab = rgb_to_lab(52, 152, 219)     # (61.0, -3.4, -38.3)
rgb = lab_to_rgb(61.0, -3.4, -38.3)  # (52, 152, 219)

delta_e_2000(lab1, lab2)   # perceptual distance
delta_e_76(lab1, lab2)     # CIE76 distance
```

---

## Color Blindness Simulation

Preview how colors appear to users with color vision deficiencies:

```python
c = Color("#ff4444")

c.simulate_colorblind("protanopia")     # red-blind
c.simulate_colorblind("deuteranopia")   # green-blind
c.simulate_colorblind("tritanopia")     # blue-blind
```

Uses Viénot/Brettel simulation matrices — industry standard for accessibility testing.

---

## Color Temperature

```python
c = Color("#ff6b35")
c.temperature    # "warm"
c.kelvin         # estimated color temperature in Kelvin (1000–40000)

Color("#3498db").temperature   # "cool"
Color("#808080").temperature   # "neutral"
```

---

## Blend Modes

Photoshop-style blend modes for compositing:

```python
base = Color("#3498db")
top = Color("#e74c3c")

base.blend(top, "multiply")
base.blend(top, "screen")
base.blend(top, "overlay")
base.blend(top, "soft_light")
base.blend(top, "hard_light")
base.blend(top, "difference")
```

---

## Standalone Converter Functions

For cases where you don't need the full `Color` class:

```python
from colorbrew import (
    hex_to_rgb, rgb_to_hex,
    hsl_to_rgb, rgb_to_hsl,
    hsv_to_rgb, rgb_to_hsv,
    cmyk_to_rgb, rgb_to_cmyk,
    rgb_to_lab, lab_to_rgb,
)

rgb_to_hex(52, 152, 219)      # "#3498db"
hex_to_rgb("#3498db")          # (52, 152, 219)
rgb_to_hsl(255, 0, 0)         # (0, 100, 50)
hsl_to_rgb(0, 100, 50)        # (255, 0, 0)
rgb_to_lab(52, 152, 219)      # (61.0, -3.4, -38.3)
lab_to_rgb(61.0, -3.4, -38.3) # (52, 152, 219)
```

---

## Real-World Use Cases

### Building a Design System

```python
from colorbrew import Color

primary = Color("#3498db")
scale = primary.scale()

css_vars = "\n".join(
    f"  --primary-{step}: {color.hex};"
    for step, color in scale.items()
)
print(f":root {{\n{css_vars}\n}}")
```

### Accessible UI Components

```python
def button_styles(bg_hex: str) -> dict:
    bg = Color(bg_hex)
    text = bg.suggest_text_color()
    hover = bg.darken(10)
    border = bg.darken(20)
    return {
        "background": bg.hex,
        "color": text.hex,
        "hover_bg": hover.hex,
        "border": border.hex,
        "contrast_ratio": bg.contrast(text),
    }
```

### Checking Brand Color Accessibility

```python
brand = Color("#ff6b35")
bg = Color("#ffffff")

print(f"Contrast ratio: {brand.contrast(bg):.1f}:1")
print(f"AA pass: {brand.meets_aa(bg)}")
print(f"AAA pass: {brand.meets_aaa(bg)}")

if not brand.meets_aa(bg):
    fixed = bg.find_accessible_color(brand)
    print(f"Suggested fix: {fixed.hex} (ratio: {fixed.contrast(bg):.1f}:1)")
```

### Generating a Perceptual Gradient for Data Visualization

```python
start = Color("#3498db")
end = Color("#e74c3c")

# Lab-space gradient stays vibrant (no muddy browns)
gradient = start.gradient(end, steps=10, space="lab")
colors = [c.hex for c in gradient]
```

### Colorblind-Safe Palette Validation

```python
palette = [Color("#e74c3c"), Color("#2ecc71"), Color("#3498db")]

for deficiency in ["protanopia", "deuteranopia", "tritanopia"]:
    simulated = [c.simulate_colorblind(deficiency) for c in palette]
    for i, (a, b) in enumerate(zip(simulated, simulated[1:])):
        dist = a.distance(b)
        if dist < 10:
            print(f"Warning: colors {i} and {i+1} are too similar "
                  f"under {deficiency} (ΔE={dist:.1f})")
```

---

## Development

```bash
uv sync
uv run pytest
uv run ruff check src/
```

## Contributing

Contributions are welcome! Please [open an issue](https://github.com/zfoq/colorbrew/issues) first to discuss what you'd like to change.

## Changelog

See [Releases](https://github.com/zfoq/colorbrew/releases) for a full list of changes.

## License

[MIT](https://github.com/zfoq/colorbrew/blob/main/LICENSE)
