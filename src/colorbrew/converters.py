"""Pure conversion functions between color formats.

All functions in this module are stateless and side-effect-free.
They accept and return primitive types (int, float, str, tuple).
"""

from __future__ import annotations


def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert a hex color string to an RGB tuple.

    Accepts 3-digit or 6-digit hex strings with or without a leading ``#``.

    Args:
        hex_str: Hex color string (e.g. ``"#3498db"``, ``"fff"``).

    Returns:
        Tuple of (red, green, blue) integers in range 0-255.
    """
    h = hex_str.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB integers to a lowercase 6-digit hex string with ``#`` prefix.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Hex string like ``"#3498db"``.
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def rgb_to_hsl(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Convert RGB integers to an HSL tuple.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Tuple of (hue 0-360, saturation 0-100, lightness 0-100).
    """
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    c_max = max(r_norm, g_norm, b_norm)
    c_min = min(r_norm, g_norm, b_norm)
    delta = c_max - c_min

    # Lightness
    lightness = (c_max + c_min) / 2.0

    if delta == 0.0:
        hue = 0.0
        saturation = 0.0
    else:
        # Saturation
        if lightness <= 0.5:
            saturation = delta / (c_max + c_min)
        else:
            saturation = delta / (2.0 - c_max - c_min)

        # Hue
        if c_max == r_norm:
            hue = ((g_norm - b_norm) / delta) % 6.0
        elif c_max == g_norm:
            hue = (b_norm - r_norm) / delta + 2.0
        else:
            hue = (r_norm - g_norm) / delta + 4.0

        hue *= 60.0
        if hue < 0:
            hue += 360.0

    return (round(hue), round(saturation * 100), round(lightness * 100))


def hsl_to_rgb(h: int, s: int, lit: int) -> tuple[int, int, int]:
    """Convert HSL values to an RGB tuple.

    Args:
        h: Hue in degrees (0-360).
        s: Saturation as percentage (0-100).
        lit: Lightness as percentage (0-100).

    Returns:
        Tuple of (red, green, blue) integers in range 0-255.
    """
    s_norm = s / 100.0
    l_norm = lit / 100.0

    if s_norm == 0.0:
        v = round(l_norm * 255)
        return (v, v, v)

    c = (1.0 - abs(2.0 * l_norm - 1.0)) * s_norm
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = l_norm - c / 2.0

    if h < 60:
        r1, g1, b1 = c, x, 0.0
    elif h < 120:
        r1, g1, b1 = x, c, 0.0
    elif h < 180:
        r1, g1, b1 = 0.0, c, x
    elif h < 240:
        r1, g1, b1 = 0.0, x, c
    elif h < 300:
        r1, g1, b1 = x, 0.0, c
    else:
        r1, g1, b1 = c, 0.0, x

    return (
        round((r1 + m) * 255),
        round((g1 + m) * 255),
        round((b1 + m) * 255),
    )


def rgb_to_cmyk(r: int, g: int, b: int) -> tuple[int, int, int, int]:
    """Convert RGB integers to a CMYK tuple with values 0-100.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Tuple of (cyan, magenta, yellow, key/black) integers 0-100.
    """
    if r == 0 and g == 0 and b == 0:
        return (0, 0, 0, 100)

    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    k = 1.0 - max(r_norm, g_norm, b_norm)
    c = (1.0 - r_norm - k) / (1.0 - k)
    m = (1.0 - g_norm - k) / (1.0 - k)
    y = (1.0 - b_norm - k) / (1.0 - k)

    return (round(c * 100), round(m * 100), round(y * 100), round(k * 100))


def cmyk_to_rgb(c: int, m: int, y: int, k: int) -> tuple[int, int, int]:
    """Convert CMYK values (0-100) to an RGB tuple.

    Args:
        c: Cyan (0-100).
        m: Magenta (0-100).
        y: Yellow (0-100).
        k: Key/black (0-100).

    Returns:
        Tuple of (red, green, blue) integers in range 0-255.
    """
    c_norm = c / 100.0
    m_norm = m / 100.0
    y_norm = y / 100.0
    k_norm = k / 100.0

    r = round(255 * (1 - c_norm) * (1 - k_norm))
    g = round(255 * (1 - m_norm) * (1 - k_norm))
    b = round(255 * (1 - y_norm) * (1 - k_norm))

    return (r, g, b)


def rgb_to_hsv(r: int, g: int, b: int) -> tuple[int, int, int]:
    """Convert RGB integers to an HSV tuple.

    Args:
        r: Red channel (0-255).
        g: Green channel (0-255).
        b: Blue channel (0-255).

    Returns:
        Tuple of (hue 0-360, saturation 0-100, value 0-100).
    """
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    c_max = max(r_norm, g_norm, b_norm)
    c_min = min(r_norm, g_norm, b_norm)
    delta = c_max - c_min

    # Value
    value = c_max

    if delta == 0.0:
        hue = 0.0
        saturation = 0.0
    else:
        # Saturation
        saturation = delta / c_max

        # Hue (same calculation as HSL)
        if c_max == r_norm:
            hue = ((g_norm - b_norm) / delta) % 6.0
        elif c_max == g_norm:
            hue = (b_norm - r_norm) / delta + 2.0
        else:
            hue = (r_norm - g_norm) / delta + 4.0

        hue *= 60.0
        if hue < 0:
            hue += 360.0

    return (round(hue), round(saturation * 100), round(value * 100))


def hsv_to_rgb(h: int, s: int, v: int) -> tuple[int, int, int]:
    """Convert HSV values to an RGB tuple.

    Args:
        h: Hue in degrees (0-360).
        s: Saturation as percentage (0-100).
        v: Value/brightness as percentage (0-100).

    Returns:
        Tuple of (red, green, blue) integers in range 0-255.
    """
    s_norm = s / 100.0
    v_norm = v / 100.0

    if s_norm == 0.0:
        val = round(v_norm * 255)
        return (val, val, val)

    c = v_norm * s_norm
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = v_norm - c

    if h < 60:
        r1, g1, b1 = c, x, 0.0
    elif h < 120:
        r1, g1, b1 = x, c, 0.0
    elif h < 180:
        r1, g1, b1 = 0.0, c, x
    elif h < 240:
        r1, g1, b1 = 0.0, x, c
    elif h < 300:
        r1, g1, b1 = x, 0.0, c
    else:
        r1, g1, b1 = c, 0.0, x

    return (
        round((r1 + m) * 255),
        round((g1 + m) * 255),
        round((b1 + m) * 255),
    )
