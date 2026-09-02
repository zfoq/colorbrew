# Color, Palette, and Theme

`Color` is the single-color value object. It stores RGB plus alpha, parses strings or RGB integers, and exposes conversion, manipulation, accessibility, naming, and classification helpers. `Color` instances are immutable and hashable; methods like `lighten`, `mix`, and `with_alpha` return new values.

`Palette` is an immutable ordered collection of `Color` values. It keeps optional names beside the colors, supports sequence operations, set-style operators, mapping-style access for named palettes, and batch operations that apply a `Color` method to every member.

`Theme` is a role-keyed `Palette`. Role names such as `primary`, `text`, or `accent` become stable names and attributes, and `Theme.to_css_vars()` emits those roles as CSS custom properties.

Use the smallest object that matches the job:

| Need | Use |
|---|---|
| One parsed or transformed color | `Color` |
| Ordered swatches or a registered color system | `Palette` |
| Semantic UI roles and CSS variables | `Theme` |

All three are immutable after construction. Change helpers return a new `Color`, `Palette`, or `Theme` instead of editing the original.

## Public API examples

Use `Color` when one color is enough:

```python
from colorbrew import Color

brand = Color("#336699")
brand.rgb                         # (51, 102, 153)
brand.oklch                       # (L, C, h) tuple
brand.css_oklch                   # "oklch(...)"
brand.classify().family           # "azure"
brand.names()["css"].name         # nearest CSS named color
Color.named("tailwind:sky-500")   # bundled Tailwind color
```

Use `Palette` for ordered swatches, named systems, and batch transforms:

```python
from colorbrew import Palette, get_palette

brand = Palette(["#336699", "gold", (204, 153, 51)])
brand.hexes                       # ('#336699', '#ffd700', '#cc9933')
brand.lighten(10).hexes           # transformed copy
brand.classify()[0].tone          # perceptual class for the first color

system = Palette.from_system("tailwind")
system["sky-500"].hex             # '#0ea5e9'
get_palette("colorbrewer:blues-3").hexes
```

Use `Theme` when names are semantic roles:

```python
from colorbrew import Theme

theme = Theme({"primary": "#336699", "text": "white"})
theme.primary.hex                 # '#336699'
theme.with_role("accent", "gold").roles
print(theme.to_css_vars())        # --cb-primary: #336699; ...
```

Settings control optional network/cache behavior without changing normal offline use:

```python
from colorbrew import configure, get_palette, settings_context

configure(allow_cache=True, allow_network=False)

with settings_context(allow_network=True):
    palette = get_palette("tailwind", version="v4", source="api")
    palette.source                # 'api'
```

Standalone converters are exported for code that does not need a `Color` object:

```python
from colorbrew import hex_to_rgb, rgb_to_hex

rgb_to_hex (52, 152, 219)         # '#3498db'
hex_to_rgb("#3498db")             # (52, 152, 219)
```
