"""
Contains the jinja2 environment
"""

import logging
import os

from jinja2 import Environment, FileSystemLoader
import jinja2
from flask import url_for

from . import formtype

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


def _suppress_none(val):
    if val is None:
        return ''
    return val

# Create the jinja2 environment
_current_path = os.path.dirname(os.path.realpath(__file__))
_template_path = os.path.join(_current_path, 'templates')

env = Environment(loader=FileSystemLoader(_template_path), autoescape=True)
env.undefined = jinja2.StrictUndefined
env.filters['sn'] = _suppress_none
env.globals['url_for'] = url_for
env.globals['hasattr'] = hasattr
env.globals['formtype'] = formtype


