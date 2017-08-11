"""
Customer Fields for easyforms library
"""

import logging

from easyforms import basicfields

from .env import env

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class UpperCaseTextField(basicfields.TextField):
    def __init__(self, name, value=None, **kwargs):
        super().__init__(name, value.upper() if value is not None else None)
    
    def convert_value(self):
        # self.value is the raw string
        if self.value is not None:
            # The string is present - convert to upper case
            self.value = self.value.upper()


class BasicCustomTextField(basicfields.TextField):
    def render(self):
        html = '[BASIC FIELD]<br> {label}: <input type="text" name="{name}" value="{value}"><br><br>'.format(
            label=self.label,
            name=self.name,
            value=self.value if self.value else ''
        )

        if self.error:
            html = '<p><strong>ERROR: {}</strong></p>{}'.format(self.error, html)

        return html


class CustomTextField(basicfields.TextField):
    def render(self):
        return env.get_template('text_field.html').render(field=self)


class CommaSeparatedListField(basicfields.TextField):
    def render(self):
        return env.get_template('comma_separated_list.html').render(field=self)

    def convert_value(self):
        # self.value is the raw string
        if self.value is not None:
            # The string is present - convert it into a list
            parts = self.value.split(',')
            self.value = [x.strip() for x in parts if x.strip()]
