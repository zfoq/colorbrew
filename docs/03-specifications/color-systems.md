# Color systems

ColorBrew keeps named colors and system palettes in a runtime registry. Built-in systems are `css`, `tailwind`, `material`, and `colorbrewer`; custom systems can be added with `register_system()`.

## Included systems and palettes

| System | Included data | Default palette | Example |
|---|---|---|---|
| `css` | 148 CSS named colors, including `rebeccapurple`, `cornflowerblue`, and `transparent` | `css@v1` | `Color.named("rebeccapurple")` |
| `tailwind` | 242 bundled Tailwind CSS v3 color names, including `sky-500` | `tailwind@v3` | `Palette.from_system("tailwind")["sky-500"]` |
| `material` | 190 bundled Material Design v2 names, including `blue-600` | `material@v2` | `Color.named("blue-600", system="material")` |
| `colorbrewer` | 35 bundled ColorBrewer schemes, 264 named palettes, and 1,680 colors, including `blues-3` | none | `get_palette("colorbrewer:blues-3")` |

CSS, Tailwind, and Material expose flat name-to-hex entries for `Color.named()`, `Color.names()`, `Color.nearest()`, and `Palette.to_system()`. ColorBrewer exposes named palettes for palette lookup; its schemes are not flat named colors.

## Names and prefixes

`Color.named()` accepts either an explicit `system=` argument or a prefixed name:

| Form | Meaning |
|---|---|
| `Color.named("sky-500", system="tailwind")` | named color in one system |
| `Color.named("tailwind:sky-500")` | same lookup with an inline system prefix |
| `Palette.from_system("tailwind")` | default palette for a system |
| `get_palette("colorbrewer:blues-3")` | named palette inside a system |

System and palette names are normalized to lowercase. Palette keys use `system:palette-name` for named palettes and `system@version` for versioned defaults.

Registry inspection and custom systems use the data API:

```python
from colorbrew import Color, Palette, get_palette, list_palettes, list_systems, register_system

list_systems()                       # ('css', 'tailwind', 'material', 'colorbrewer')
list_palettes("colorbrewer")          # includes 'colorbrewer:blues-3'
get_palette("colorbrewer:blues-3").hexes

register_system("brand", entries={"primary": "#336699"})
Color.named("brand:primary").hex      # '#336699'
Palette(["#336699", "#cc9933"]).to_system("tailwind")
```

## Bundled resources

Bundled data lives under `src/colorbrew/data/resources/` and is loaded through the data loaders. The ColorBrewer resource is JSON shaped as nested mappings:

```json
{
  "Blues": {
    "3": ["#deebf7", "#9ecae1", "#3182bd"]
  }
}
```

Each `ColorBrewer` scheme maps palette sizes to ordered hex lists. The registry exposes those palettes as names like `colorbrewer:blues-3`.

## Cache and remote behavior

Normal use is offline. `get_palette()` defaults to `source="bundled"`; remote requests require `source="api"` or `source="auto"` plus `allow_network=True`, either per call or through `configure(allow_network=True)`.

```python
from colorbrew import configure, get_palette, settings_context

get_palette("tailwind")                         # bundled Tailwind v3, no network
get_palette("material", source="bundled")       # bundled Material v2

with settings_context(allow_network=True):
    get_palette("tailwind", version="v4", source="api", allow_cache=True)

configure(allow_network=False, allow_cache=True)
get_palette("tailwind", source="auto")          # cache if fresh, otherwise bundled
```

Disk cache access is controlled by `allow_cache`, `cache_dir`, and `cache_ttl`. `source="cache"` reads only the cache, `source="api"` fetches only a remote URL, and `source="auto"` reads a fresh cache first, may fetch remote data when network access is allowed, and falls back to bundled data when available.

Remote palettes may be JSON mappings or CSS custom-property payloads. CSS payloads accept hex values and OKLCH custom properties, which are converted to hex before a `Palette` is returned or cached.
