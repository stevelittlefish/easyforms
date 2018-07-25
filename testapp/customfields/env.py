"""
Contains the jinja2 environment for the custom fields
"""

import logging
import os

from jinja2 import Environment, FileSystemLoader
import jinja2

from easyforms import formtype
from easyforms import styles

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


def _suppress_none(val):
    """Returns an empty string if None is passed in, otherwide returns what was passed in"""
    if val is None:
        return ''
    return val

# Create the jinja2 environment
_current_path = os.path.dirname(os.path.realpath(__file__))
_template_path = os.path.join(_current_path, 'templates')

env = Environment(loader=FileSystemLoader(_template_path), autoescape=True)
# Don't allow undefined variables to be ignored
env.undefined = jinja2.StrictUndefined
# Custom filter to replace None with empty string
env.filters['sn'] = _suppress_none
env.globals['formtype'] = formtype
env.globals['styles'] = styles

