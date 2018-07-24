"""
Code to manage session variables
"""

import logging

from flask import session

from easyforms import styles

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

KEY_RENDER_STYLE = 'render-style'


def get_render_style():
    # Default to bs4
    return session.get(KEY_RENDER_STYLE, styles.BOOTSTRAP_4)


def set_render_style(render_style):
    if render_style not in styles.ALL_STYLES:
        raise ValueError('Invalid Render Style: {}'.format(render_style))

    session[KEY_RENDER_STYLE] = render_style

