"""
This contains definitions of basic form fields, such as text, integer...
"""

import logging
from decimal import Decimal, InvalidOperation

from . import form
from .env import env
from . import validate

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class TextField(form.Field):
    def __init__(self, name, type='text', placeholder=None, **kwargs):
        """
        :param name: The name of the field (the name field in the generated input)
        :param type: The type, i.e. text, email, number
        :param placeholder: Placeholder text
        """
        super(TextField, self).__init__(name, **kwargs)

        self.type = type
        self.placeholder = placeholder

    def render(self):
        return env.get_template('ef_basic_input.html').render(field=self)


class PasswordField(TextField):
    def __init__(self, name, **kwargs):
        """
        :param name: The name of the field (the name field in the generated input)
        """
        if 'type' in kwargs:
            raise ValueError('Invalid argument: type')

        super(PasswordField, self).__init__(name, 'password', **kwargs)


class TextAreaField(form.Field):
    def __init__(self, name, rows=5, placeholder=None, maxlength=None, **kwargs):
        super(TextAreaField, self).__init__(name, **kwargs)

        self.placeholder = placeholder
        self.rows = rows
        self.maxlength = maxlength

    def render(self):
        return env.get_template('basic/text_area.html').render(field=self)


class IntegerField(TextField):
    def __init__(self, name, type='number', min_value=None, max_value=None, step=None, **kwargs):
        if type not in ['number', 'text']:
            raise ValueError('Type must be \'number\' or \'text\'')

        super(IntegerField, self).__init__(name, type, **kwargs)

        self.min_value = min_value
        self.max_value = max_value
        self.step = step

        if min_value is not None:
            self.validators.append(validate.min_value(min_value))

        if max_value is not None:
            self.validators.append(validate.max_value(max_value))

    def convert_value(self):
        if self.value is not None:
            try:
                self.value = int(self.value)
            except ValueError:
                self.error = 'Invalid integer'


class DecimalField(TextField):
    def __init__(self, name, type='number', min_value=None, max_value=None, step=0.01, **kwargs):
        if type not in ['number', 'text']:
            raise ValueError('Type must be \'number\' or \'text\'')

        super(DecimalField, self).__init__(name, type, **kwargs)

        if min_value is not None:
            self.validators.append(validate.min_value(min_value))

        if max_value is not None:
            self.validators.append(validate.max_value(max_value))

        self.min_value = min_value
        self.max_value = max_value
        self.step = step

    def convert_value(self):
        if self.value is not None:
            try:
                self.value = Decimal(self.value)
            except InvalidOperation:
                self.error = 'Invalid decimal'


class SelectField(form.Field):
    def __init__(self, name, key_pairs, empty_option=False, empty_option_name='', button_link_url=None,
                 button_link_text=None, **kwargs):

        super(SelectField, self).__init__(name, **kwargs)

        self.key_pairs = key_pairs
        self.empty_option = empty_option
        self.empty_option_name = empty_option_name
        self.button_link_url = button_link_url
        self.button_link_text = button_link_text

    def render(self):
        return env.get_template('basic/select.html').render(field=self)

    def convert_value(self):
        if self.value:
            valid = False
            for key_pair in self.key_pairs:
                if self.value == key_pair.select_value:
                    valid = True
                    break

            if not valid:
                self.error = 'Invalid selection'
                self.value = None


class BooleanCheckbox(form.Field):
    def __init__(self, name, default=False, **kwargs):
        super(BooleanCheckbox, self).__init__(name, required=False, allow_missing=True, value=default, **kwargs)

    def render(self):
        return env.get_template('basic/checkbox.html').render(field=self)

    def convert_value(self):
        if self.value is not None:
            self.value = True
        else:
            self.value = False


class SubmitButton(form.Field):
    def __init__(self, name, value=None, css_class='btn-primary', render_after_sections=True, **kwargs):
        if value is None:
            value = form.convert_name_to_label(name)

        self.submit_text = value

        super(SubmitButton, self).__init__(name, value=value, css_class=css_class, noclear=True,
                                           render_after_sections=render_after_sections, allow_missing=True, **kwargs)

    def render(self):
        return env.get_template('basic/submit.html').render(field=self)


class HiddenField(form.Field):
    def __init__(self, name, value, **kwargs):
        """
        :param name: The name of the field (the name field in the generated input)
        :param value: The value of the hidden field
        """
        super(HiddenField, self).__init__(name, value=value, **kwargs)

    def render(self):
        return env.get_template('basic/hidden_input.html').render(field=self)

