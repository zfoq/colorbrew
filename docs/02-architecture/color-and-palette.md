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
