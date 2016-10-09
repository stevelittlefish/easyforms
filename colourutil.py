"""
For converting colours between rgb and hsl
"""

import logging
from math import floor

__author__ = 'Yu Lee Paul (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


def rgb_to_hsl(r, g, b):
    """
    Converts an RGB color value to HSL.
    :param r: The red color value
    :param g: The green color value
    :param b: The blue color value
    :return: The HSL representation
    """
    r = float(r) / 255.0
    g = float(g) / 255.0
    b = float(b) / 255.0

    max_value = max(r, g, b)
    min_value = min(r, g, b)

    h = None
    s = None
    l = (max_value + min_value) / 2
    d = max_value - min_value

    if d == 0:
        # achromatic
        h = 0
        s = 0
    else:
        s = d / (1 - abs(2 * l - 1))

        if r == max_value:
            h = 60 * ((g - b) % 6)
            if b > g:
                h += 360
        if g == max_value:
            h = 60 * ((b - r) / d + 2)
        if b == max_value:
            h = 60 * ((r - g) / d + 4)

    return round(h, 2), round(s, 2), round(l, 2)


def hsl_to_rgb(h, s, l):
    h = float(h)
    s = float(s)
    l = float(l)

    c = (1 - abs(2 * l - 1)) * s
    mod = (h / 60.0) % 2
    x = c * (1 - abs(mod - 1))
    m = l - (c / 2)

    if h < 60:
        r = c
        g = x
        b = 0
    elif h < 120:
        r = x
        g = c
        b = 0
    elif h < 180:
        r = 0
        g = c
        b = x
    elif h < 240:
        r = 0
        g = x
        b = c
    elif h < 300:
        r = x
        g = 0
        b = c
    else:
        r = c
        g = 0
        b = x

    r = (r + m) * 255
    g = (g + m) * 255
    b = (b + m) * 255

    return floor(r), floor(g), floor(b)


def html_color_to_rgba(html_colour, alpha):
    """
    :param html_colour: Colour string like FF0088
    :param alpha: Alpha value (opacity)
    :return: RGBA semitransparent version of colour for use in css
    """
    html_colour = html_colour.upper()
    if html_colour[0] == '#':
        html_colour = html_colour[1:]

    r_str = html_colour[0:2]
    g_str = html_colour[2:4]
    b_str = html_colour[4:6]

    r = int(r_str, 16)
    g = int(g_str, 16)
    b = int(b_str, 16)

    return 'rgba(%s, %s, %s, %s)' % (r, g, b, alpha)


def blend_html_colour_to_white(html_colour, alpha):
    """
    :param html_colour: Colour string like FF552B or #334455
    :param alpha: Alpha value
    :return: Html colour alpha blended onto white
    """
    html_colour = html_colour.upper()
    has_hash = False
    if html_colour[0] == '#':
        has_hash = True
        html_colour = html_colour[1:]

    r_str = html_colour[0:2]
    g_str = html_colour[2:4]
    b_str = html_colour[4:6]

    r = int(r_str, 16)
    g = int(g_str, 16)
    b = int(b_str, 16)

    r = int(alpha * r + (1 - alpha) * 255)
    g = int(alpha * g + (1 - alpha) * 255)
    b = int(alpha * b + (1 - alpha) * 255)
    
    out = '{:02X}{:02X}{:02X}'.format(r, g, b)
    if has_hash:
        out = '#' + out

    return out


