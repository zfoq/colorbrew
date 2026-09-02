# Getting started

Install ColorBrew, import the public API, and use bundled color systems without network access.

```pycon
>>> from colorbrew import Color, Palette, Theme, get_palette, list_systems
>>> brand = Color("#336699")
>>> brand.hex
'#336699'
>>> brand.lighten(10).hex
'#4080bf'
```

## Install and import

```bash
pip install colorbrew
```

ColorBrew requires Python 3.10+ and has no runtime dependencies. Most code starts with the top-level imports:

```pycon
>>> from colorbrew import Color, Palette, Theme
>>> Color("cornflowerblue").hex
'#6495ed'
```

## Color

Use `Color` for one parsed, converted, transformed, named, or classified color:

```pycon
>>> sky = Color.named("tailwind:sky-500")
>>> sky.hex
'#0ea5e9'
>>> sky.classify().family
'blue'
>>> sky.meets_aa(Color("white"))
False
```

## Palette

Use `Palette` for ordered swatches, registered systems, and batch transforms:

```pycon
>>> palette = Palette(["#336699", "gold", (204, 153, 51)])
>>> palette.hexes
('#336699', '#ffd700', '#cc9933')
>>> palette.lighten(10).hexes
('#4080bf', '#ffe033', '#d6ad5c')
>>> Palette.from_system("material")["blue-600"].hex
'#1e88e5'
```

ColorBrewer palettes are bundled too:

```pycon
>>> get_palette("colorbrewer:blues-3").hexes
('#deebf7', '#9ecae1', '#3182bd')
```

## Theme

Use `Theme` for semantic UI roles and CSS custom properties:

```pycon
>>> theme = Theme({"primary": "#336699", "text": "white"})
>>> theme.primary.hex
'#336699'
>>> theme.to_css_vars()
'--cb-primary: #336699;\n--cb-text: #ffffff;'
```

## Included systems and offline fetching

Bundled systems are available offline: CSS named colors, Tailwind CSS, Material Design, and ColorBrewer.

```pycon
>>> list_systems()
('css', 'tailwind', 'material', 'colorbrewer')
```

Normal palette loading is offline by default. Remote fetching requires an API source and `allow_network=True`.

```pycon
>>> from colorbrew import configure, settings_context
>>> _ = configure(allow_network=False, allow_cache=True)
>>> get_palette("tailwind").source
'bundled'
>>> with settings_context(allow_network=False):
...     get_palette("colorbrewer:blues-3").source
'bundled'
```
