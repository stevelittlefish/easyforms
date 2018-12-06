"""
Contains the definitions for the more exotic types of form inputs, such as date pickers and gender selection inputs
"""

import logging
import datetime
import re
import io
from collections import OrderedDict

from flask import request, url_for
from littlefish import timetool
from littlefish import htmlutil
import requests

from . import basicfields
from . import validate
from . import form
from .env import env
from .config import CkeditorConfig

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)


class NameField(basicfields.TextField):
    def __init__(self, name, **kwargs):
        """
        :param name: The name of the field (the name field in the generated input)
        """
        super(NameField, self).__init__(name, 'text', **kwargs)

    def convert_value(self):
        # convert to title case
        if self.value is not None:
            self.value = self.value.title()


class CodeField(basicfields.TextField):
    """Field for entering url safe lower case strings"""

    def __init__(self, name, **kwargs):
        super().__init__(name, 'text', **kwargs)
        
        self.validators.append(validate.url_safe)

    def convert_value(self):
        # convert to lower case
        if self.value is not None:
            self.value = self.value.lower()


class EmailField(basicfields.TextField):
    def __init__(self, name, type='email', **kwargs):
        """
        :param name: The name of the field (the name field in the generated input)
        :param type: The type, i.e. text, email
        """
        if type not in ['email', 'text']:
            raise ValueError('Type must be \'email\' or \'text\'')

        super(EmailField, self).__init__(name, type, **kwargs)

        self.validators.append(validate.email)

    def convert_value(self):
        # convert to lower case
        if self.value is not None:
            self.value = self.value.lower()


class UrlField(basicfields.TextField):
    def __init__(self, name, type='url', **kwargs):
        """
        :param name: The name of the field (the name field in the generated input)
        :param type: The type, i.e. text, url
        """
        if type not in ['url', 'text']:
            raise ValueError('Type must be \'url\' or \'text\'')

        super(UrlField, self).__init__(name, type, **kwargs)

        self.validators.append(validate.url)


class PhoneNumberField(basicfields.TextField):
    def __init__(self, name, type='tel', **kwargs):
        """
        :param name: The name of the field (the name field in the generated input)
        :param type: The type, i.e. text, email
        """
        if type not in ['tel', 'text']:
            raise ValueError('Type must be \'tel\' or \'text\'')

        super(PhoneNumberField, self).__init__(name, type, **kwargs)

        self.validators.append(validate.phone_number)

    def convert_value(self):
        # Strip out spaces
        if self.value is not None:
            self.value = self.value.replace(' ', '')


class PostcodeField(basicfields.TextField):
    def __init__(self, name, must_contain_space=False, **kwargs):
        """
        :param name: The name of the field (the name field in the generated input)
        :param type: The type, i.e. text, email
        """
        if 'type' in kwargs:
            raise Exception('Invalid keyword argument: type')

        super(PostcodeField, self).__init__(name, 'text', **kwargs)

        self.validators.append(validate.postcode)
        if must_contain_space:
            def validate_space(x):
                if ' ' not in x:
                    return 'Please enter a UK postcode including a space in the middle'

            self.validators.append(validate_space)

    def convert_value(self):
        if self.value is not None:
            self.value = self.value.upper()


class GenderField(form.Field):
    def __init__(self, name, **kwargs):
        super(GenderField, self).__init__(name, allow_missing=True, **kwargs)

    def render(self):
        return env.get_template('advanced/gender.html').render(field=self)


class DateSelectField(form.Field):
    def __init__(self, name, years=None, **kwargs):
        super().__init__(name, **kwargs)

        if years is None:
            this_year = datetime.datetime.now().year
            self.years = [i for i in range(this_year, this_year - 115, -1)]
        else:
            self.years = years

    def render(self):
        return env.get_template('advanced/date_select.html')\
            .render(field=self, day=self.value.day if self.value else None,
                    month=self.value.month if self.value else None, year=self.value.year if self.value else None,
                    this_year=datetime.datetime.now().year)

    def extract_value(self, data):
        day_str = data['%s-day' % self.name]
        month_str = data['%s-month' % self.name]
        year_str = data['%s-year' % self.name]

        # Validate and process date
        if day_str and month_str and year_str:
            try:
                day = int(day_str)
                month = int(month_str)
                year = int(year_str)

                if year not in self.years:
                    self.error = 'Invalid year'
                else:
                    self.value = datetime.date(year, month, day)
            except Exception:
                self.error = 'Invalid date'
        elif self.required:
            self.error = 'Required'


class YearMonthSelectField(form.Field):
    def __init__(self, name, years=None, **kwargs):
        super(YearMonthSelectField, self).__init__(name, **kwargs)
        
        if years is None:
            this_year = datetime.datetime.now().year
            self.years = [i for i in range(this_year, this_year - 115, -1)]
        else:
            self.years = years

    def render(self):
        return env.get_template('advanced/year_month_select.html')\
            .render(field=self, month=self.value.month if self.value else None,
                    year=self.value.year if self.value else None,
                    this_year=datetime.datetime.now().year)

    def extract_value(self, data):
        month_str = data['%s-month' % self.name]
        year_str = data['%s-year' % self.name]

        # Validate and process date
        if month_str and year_str:
            try:
                day = 1
                month = int(month_str)
                year = int(year_str)

                if year not in self.years:
                    self.error = 'Year outside of allowed date range'
                else:
                    self.value = datetime.date(year, month, day)
            except Exception:
                self.error = 'Invalid date'


class DatePickerField(form.Field):
    """
    You must enable the date picker javascript for this to work!
    """
    def __init__(self, name, **kwargs):
        if 'width' not in kwargs:
            kwargs['width'] = 3
        super(DatePickerField, self).__init__(name, css_class='date-picker', **kwargs)

    def render(self):
        date = self.value
        if date is not None:
            date = timetool.datetime_to_datepicker(date)

        return env.get_template('advanced/date_picker.html').render(field=self, date=date)

    def convert_value(self):
        if self.value is not None:
            try:
                self.value = timetool.datetime_from_datepicker(self.value).date()
            except ValueError:
                self.error = 'Invalid date: "%s"' % self.value
                self.value = datetime.datetime.now()


class IntegerSelectField(basicfields.SelectField):
    def __init__(self, name, key_pairs, empty_option=False, empty_option_name='', button_link_url=None,
                 button_link_text=None, **kwargs):
        super(IntegerSelectField, self).__init__(name, key_pairs, empty_option=empty_option,
                                                 empty_option_name=empty_option_name, button_link_url=button_link_url,
                                                 button_link_text=button_link_text, **kwargs)

    def convert_value(self):
        if self.value is not None:
            try:
                self.value = int(self.value)
            except ValueError:
                self.error = 'Invalid value'


class ListSelectField(basicfields.SelectField):
    def __init__(self, name, values, **kwargs):
        class KeyPair(object):
            def __init__(self, x):
                self.select_name = x
                self.select_value = x

        key_pairs = [KeyPair(x) for x in values]

        super().__init__(name, key_pairs, **kwargs)


class ObjectListSelectField(basicfields.SelectField):
    """
    Use this when you want to get the original key_pair from the list
    out in the value of the form
    """
    def __init__(self, name, key_pairs, **kwargs):
        super().__init__(name, key_pairs, **kwargs)

    def convert_value(self):
        for key_pair in self.key_pairs:
            if str(key_pair.select_value) == self.value:
                self.value = key_pair
                return

        self.error = 'Invalid Value'


class EnumSelectField(basicfields.SelectField):
    def __init__(self, name, enum_class, **kwargs):
        class KeyPair(object):
            def __init__(self, x):
                self.select_name = x.name
                self.select_value = x.value

        super().__init__(name, key_pairs=enum_class, **kwargs)

        self.enum_class = enum_class

    def render(self):
        return env.get_template('advanced/enum_select.html').render(field=self)

    def convert_value(self):
        if not self.value:
            return

        for item in self.enum_class:
            if item.value == self.value:
                self.value = item
                return

        self.error = 'Invalid value: {}'.format(self.value)
        self.value = None


class DictSelectField(basicfields.SelectField):
    def __init__(self, name, dictionary, key_is_label=True, **kwargs):
        """
        A select (drop-down) from a dictionary.  The items will be sorted unless you pass in an
        OrderedDict.

        :param dictionary: The dictionary containing the values to select between
        :param key_is_label: If True (default) then the keys in the dictionary become the option
                             text, and the value is the submitted value.  If False, then the keys
                             in the dictionary are the submitted value and the values are the
                             option text
        """
        class KeyPair(object):
            def __init__(self, select_name, select_value):
                self.select_name = select_name
                self.select_value = select_value

        if key_is_label:
            key_pairs = [KeyPair(name, value) for (name, value) in dictionary.items()]
        else:
            key_pairs = [KeyPair(value, name) for (name, value) in dictionary.items()]
        
        if not isinstance(dictionary, OrderedDict):
            key_pairs = sorted(key_pairs, key=lambda x: x.select_name)

        super().__init__(name, key_pairs, **kwargs)


class TitleSelectField(ListSelectField):
    def __init__(self, name, **kwargs):
        # TODO: add optional ridiculous fields here?
        titles = ['Mr', 'Mrs', 'Miss', 'Ms']
        super().__init__(name, titles, **kwargs)


class CkeditorField(basicfields.TextAreaField):
    """
    HTML Editor using CKEditor
    """
    def __init__(self, name, config=CkeditorConfig(), height=None, on_change=None, **kwargs):

        super().__init__(name, **kwargs)
        
        self.config = config
        self.height = height
        self.on_change = on_change

    def render(self):
        return env.get_template('advanced/ckeditor.html').render(field=self)

    def convert_value(self):
        if self.value is not None and self.config.strip_nbsp:
            self.value = re.sub(r'\s?&nbsp;\s?', ' ', self.value)

        if self.value and self.config.strip_empty_paragraphs:
            self.value = re.sub(r'<p>\s*</p>', '', self.value)

        if self.value is not None and self.config.pretty_print_html:
            self.value = htmlutil.pretty_print(
                self.value, max_line_length=self.config.pretty_print_html_line_length
            )

    def get_height(self):
        height = self.config.default_height
        if self.height:
            height = height

        if height is None:
            return None

        if isinstance(height, int):
            return '{}px'.format(height)

        return height


class FilemanagerField(UrlField):
    """
    Only one of these per rendered page is supported!
    """
    def __init__(self, name, filemanager_url='/fm/index.html', **kwargs):
        super().__init__(name, **kwargs)

        self.filemanager_url = filemanager_url

    def render(self):
        return env.get_template('advanced/filemanager.html').render(field=self)


class HtmlField(basicfields.TextAreaField):
    """
    This field is deprecated and should no longer be used.  Please us CkeditorField
    instead
    """
    def __init__(self, name, no_smiley=True, no_image=True, no_nbsp=True, height=None,
                 on_change=None, pretty_print=False, strip_empty_paragraphs=True,
                 entities_latin=True, pretty_print_line_length=110,
                 ckeditor_url_override=None, **kwargs):

        super(HtmlField, self).__init__(name, **kwargs)

        self.no_smiley = no_smiley
        self.no_image = no_image
        self.no_nbsp = no_nbsp
        self.height = height
        self.on_change = on_change
        self.pretty_print = pretty_print
        self.pretty_print_line_length = pretty_print_line_length
        self.strip_empty_paragraphs = strip_empty_paragraphs
        self.entities_latin = entities_latin
        if ckeditor_url_override:
            self.ckeditor_url = ckeditor_url_override
        else:
            self.ckeditor_url = url_for('static', filename='ckeditor/ckeditor.js')

    def render(self):
        return env.get_template('advanced/deprecated_html_field.html').render(field=self)

    def convert_value(self):
        if self.value is not None and self.no_nbsp:
            self.value = re.sub(r'\s?&nbsp;\s?', ' ', self.value)

        if self.value and self.strip_empty_paragraphs:
            self.value = re.sub(r'<p>\s*</p>', '', self.value)

        if self.value is not None and self.pretty_print:
            self.value = htmlutil.pretty_print(self.value,
                                               max_line_length=self.pretty_print_line_length)


class TimeInputField(form.Field):
    def __init__(self, name, **kwargs):
        super(TimeInputField, self).__init__(name, **kwargs)

    def render(self):
        return env.get_template('advanced/time_input.html').render(field=self)

    def extract_value(self, data):
        hour_str = data['%s-hour' % self.name]
        minute_str = data['%s-minute' % self.name]

        # Validate and process time
        if hour_str and minute_str:
            try:
                hour = int(hour_str)
                minute = int(minute_str)

                self.value = datetime.time(hour, minute)
            except Exception:
                self.error = 'Invalid time'


class FileUploadField(form.Field):
    def __init__(self, name, accept, disable_submitted_warning=False, **kwargs):
        super(FileUploadField, self).__init__(name, requires_multipart=True, allow_missing=True, **kwargs)

        self.accept = accept
        self.submitted = False
        self.file = None
        self.filename = None
        self.disable_submitted_warning = disable_submitted_warning

    def render(self):
        return env.get_template('advanced/file_upload.html').render(field=self)

    def convert_value(self):
        if self.name in request.files:
            self.file = request.files[self.name]
            self.filename = self.file.filename
            if self.filename:
                self.value = self.file.read()
                if not self.disable_submitted_warning:
                    self.submitted = True
            else:
                self.file = None
                self.filename = None
                self.value = None


class ImageUploadField(FileUploadField):
    def __init__(self, name, accept='image/*', min_image_width=None, min_image_height=None, max_image_width=None, max_image_height=None, **kwargs):
        super(ImageUploadField, self).__init__(name, accept, value=None, **kwargs)

        self.min_image_width = min_image_width
        self.min_image_height = min_image_height
        self.max_image_width = max_image_width
        self.max_image_height = max_image_height
        self.raw_image_data = None

    def convert_value(self):
        # This will get the file bytes and filename
        super(ImageUploadField, self).convert_value()

        # Import here instead at top of file so that projects can avoid a dependency on Pillow
        from PIL import Image

        if not self.value:
            return

        # Now time to process the image
        self.raw_image_data = self.value

        stream = io.BytesIO(self.value)
        image = None
        try:
            image = Image.open(stream)
        except IOError:
            self.error = 'Invalid image file'

        if not self.error:
            width = image.size[0]
            height = image.size[1]

            if (self.min_image_width is not None and width < self.min_image_width) or \
                    (self.max_image_width is not None and width > self.max_image_width) or \
                    (self.min_image_height is not None and height < self.min_image_height) or \
                    (self.max_image_height is not None and height > self.max_image_height):

                if self.min_image_width is not None and self.min_image_width == self.max_image_width and self.min_image_height is not None and self.min_image_height == self.max_image_height:
                    self.error = 'Image must be %s x %s pixels' % (self.min_image_width, self.min_image_height)
                else:
                    self.error = ''

                    if self.min_image_width is not None:
                        if self.max_image_width is not None:
                            if self.min_image_width == self.max_image_width:
                                self.error += 'Image width must be %s pixels. '
                            else:
                                self.error += 'Image width must be between %s and %s pixels. ' % (self.min_image_width, self.max_image_width)
                        else:
                            self.error += 'Image must be at least %s pixels wide. ' % self.min_image_width
                    elif self.max_image_width is not None:
                        self.error += 'Image width must be at most %s pixels wide. ' % self.max_image_width

                    if self.min_image_height is not None:
                        if self.max_image_height is not None:
                            if self.min_image_height == self.max_image_height:
                                self.error += 'Image height must be %s pixels.'
                            else:
                                self.error += 'Image height must be between %s and %s pixels.' % (self.min_image_height, self.max_image_height)
                        else:
                            self.error += 'Image must be at least %s pixels tall.' % self.min_image_height
                    elif self.max_image_height is not None:
                        self.error += 'Image height must be at most %s pixels tall.' % self.max_image_height

        if self.error:
            self.value = None
            self.file = None
            self.filename = None
            self.raw_image_data = None
        else:
            self.value = image


class MultiCheckboxField(form.Field):
    """
    This field renders as multiple checkboxes in a vertical column. The must pass in a list of
    object with select_name and select_value properties defined.  Each checkbox will have
    select_name as a label, and select_value (which must be unique) will be submitted as the
    value of the checkbox.

    When reading form data, the original objects will be copied into a new list, with each
    object that had its box ticked being present in the list.
    """
    def __init__(self, name, values, value=None, **kwargs):
        if value is None:
            value = []

        if not isinstance(value, list):
            raise Exception('Value must be a list for multi-checkbox field')

        super().__init__(name, allow_missing=True, value=value, **kwargs)

        self.values = values
        self._checked_select_values = [v.select_value for v in self.value]
    
    def render(self):
        return env.get_template('advanced/multicheckbox.html').render(field=self)

    def extract_value(self, data):
        self._checked_select_values = data.getlist(self.name)
        self.value = [v for v in self.values if v.select_value in self._checked_select_values]


class SubmitCancelButton(basicfields.SubmitButton):
    def __init__(self, name, cancel_url, value=None, cancel_text='Cancel', css_class='btn-primary',
                 cancel_css_class='btn-danger', render_after_sections=True, **kwargs):
        self.cancel_url = cancel_url
        self.cancel_text = cancel_text
        self.cancel_css_class = cancel_css_class

        super().__init__(name, value=value, css_class=css_class,
                         render_after_sections=render_after_sections, **kwargs)

    def render(self):
        return env.get_template('advanced/submit_cancel.html').render(field=self)


class CardNumberField(basicfields.TextField):
    def __init__(self, name, **kwargs):
        if 'type' in kwargs:
            raise Exception('Cannot specify type for card number field')

        super().__init__(name, type='text', validators=[validate.card_number], **kwargs)


class RecaptchaField(form.Field):
    """
    Adds a Recaptcha to the form.  This will not work if you add it more than once.

    If the recaptcha is not completed, form.ready will not return True and there will be a validation
    error. This field will always return 'True' if it was completed, or None if validation wasn't
    completed.

    :param name: The form name - really only used for the label
    :param site_key: The site key for the recaptcha (see ReCaptcha documentation)
    :param secret_key: The secret key for the recaptcha
    """
    def __init__(self, name, site_key, secret_key, **kwargs):
        if 'value' in kwargs:
            raise ValueError('Can\'t set value of RecaptchaField')

        if 'required' in kwargs:
            raise ValueError('Can\'t set required of RecaptchaField (it\'s always required!)')

        super().__init__(name, value=None, required=True, **kwargs)
        
        self.site_key = site_key
        self.secret_key = secret_key
    
    def render(self):
        return env.get_template('advanced/recaptcha.html').render(field=self)
    
    def extract_value(self, data):
        recaptcha_response = data.get('g-recaptcha-response')
        if recaptcha_response:
            url = 'https://www.google.com/recaptcha/api/siteverify'
            data = {
                'secret': self.secret_key,
                'response': recaptcha_response,
                'remoteip': request.remote_addr
            }

            r = requests.post(url, data)

            if r.status_code != 200:
                log.debug('Recaptcha failed with response code {}'.format(r.status_code))
            else:
                # log.debug('Recaptcha response: {}'.format(r.text))
                resp = r.json()
                success = resp['success']
                error_codes = resp.get('error-codes')
                if success:
                    # Passed the recaptcha
                    self.value = True
                else:
                    log.debug('Recaptcha failed with error codes: {}'.format(', '.join(error_codes)))


class GetaddressPostcodeField(PostcodeField):
    def __init__(self, name, api_key, line1_id, line2_id=None, line3_id=None, town_id=None,
                 county_id=None, sort_addresses=True,
                 button_class='btn btn-primary', button_text='Find Address',
                 inline_button=False,
                 **kwargs):
        """
        Postcode field with getaddress.io address lookup

        :param api_key: The getaddress.io API key
        :param line1_id: The id of the field to be populated with line 1 of the address
        :param line2_id: The id of the field to be populated with line 2 of the address
        :param line3_id: The id of the field to be populated with line 3 of the address
        :param town_id: The id of the field to be populated with the town of the address
        :param county_id: The id of the field to be populated with the county of the address
        :param button_class: CSS class for the search button
        :param button_text: Text to display on the search button
        :param sort_addresses: Whether or not to numerically sort the addresses (in the API call)
        :param inline_button: If True, the button will be rendered next to the main input
                              (you will probably need to add some css rules to make this look right)
        """
        super().__init__(name, **kwargs)
        
        self.api_key = api_key
        self.line1_id = line1_id
        self.line2_id = line2_id
        self.line3_id = line3_id
        self.town_id = town_id
        self.county_id = county_id
        self.button_class = button_class
        self.button_text = button_text
        self.sort_addresses = sort_addresses
        self.inline_button = inline_button

    def render(self):
        if self.readonly:
            return super().render()

        return env.get_template('advanced/getaddress_postcode_field.html').render(field=self)
