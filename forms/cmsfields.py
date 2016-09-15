"""
Fields specific to the CMS
"""

import logging

from . import advancedfields

from .env import env

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class CmsHtmlField(advancedfields.HtmlField):
    def __init__(self, name, **kwargs):
        super(CmsHtmlField, self).__init__(name, **kwargs)

    def render(self):
        return env.get_template('cms/ckeditor.html').render(field=self)

