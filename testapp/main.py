"""
Main blueprint for test app
"""

import logging
import decimal

from flask import Blueprint, render_template

import customfields
import easyforms


__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

main = Blueprint('main', __name__)


class KeyValue(object):
    def __init__(self, select_name, select_value):
        self.select_name = select_name
        self.select_value = select_value


EXAMPLE_KEY_PAIRS = [
    KeyValue('Example Label', 'example-value'),
    KeyValue('Example Label 2', 'example-value-2'),
    KeyValue('Another Label', 'another-value'),
    KeyValue('Short', 'short'),
    KeyValue('Looooooooooooooong label text to amke things wide', 'long')
]


def get_submitted_data(form):
    submitted_data = None

    if form.ready:
        submitted_data = {}
        for field_name in form.field_dict:
            submitted_data[field_name] = form[field_name]

    return submitted_data


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/simple-form', methods=['GET', 'POST'])
def simple_form():
    form = easyforms.Form([
        easyforms.TextField('some-text', required=True),
        easyforms.IntegerField('an-integer', help_text='Any whole number!', required=True),
        easyforms.SelectField('pick-a-value', EXAMPLE_KEY_PAIRS, empty_option=True,
                              optional=True)
    ], form_type=easyforms.VERTICAL, max_width=700)

    if form.ready:
        log.info('The form was submitted and passed validation!')
    
    return render_template('simple_form.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/large-multisection-form', methods=['GET', 'POST'])
def large_multisection_form():
    form = easyforms.Form([], read_form_data=False)

    form.add_section('Basic Fields', [
        easyforms.TextField('text-field', required=True,
                            help_text='Any text will be accepted'),
        easyforms.PasswordField('password-field', required=True, width=4),
        easyforms.IntegerField('integer-field', width=2, min_value=1, max_value=20),
        easyforms.DecimalField('decimal-field', min_value=-10, max_value=1000,
                               step=decimal.Decimal('0.1'), width=2),
        easyforms.BooleanCheckbox('boolean-checkbox', default=False),
        easyforms.HiddenField('hidden-field', value='bananas'),
        easyforms.NameField('name-field', width=4),
        easyforms.SelectField('select-field', EXAMPLE_KEY_PAIRS, empty_option=True, required=True)
    ])

    form.add_section('Advanced Fields', [
        easyforms.CodeField('code-field', width=6),
        easyforms.EmailField('email-field', width=6),
        easyforms.UrlField('url-field'),
        easyforms.PhoneNumberField('phone-number-field'),
        easyforms.PostcodeField('postcode-field', width=4),
        easyforms.GenderField('gender-field',
                              help_text='You must include images static/img/male-symbol.png and '
                              'static/img/female-symbol.png for this to work'),
        easyforms.DateSelectField('date-select-field'),
        easyforms.YearMonthSelectField('year-month-select-field'),
        easyforms.DatePickerField('date-picker-field',
                                  help_text='Required jquery ui and the following line of javascript: '
                                  '$(".date-picker").datepicker({ dateFormat: "dd/mm/yy" });'),
        easyforms.ListSelectField('list-select-field', ['Option 1', 'Option 2', 'Another Option'],
                                  width=3),
        easyforms.DictSelectField('dict-select-field', {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        }, width=3),

        easyforms.DictSelectField('dict-select-field-2', {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        }, width=3, key_is_label=False, help_text='key_is_label=False switched the keys and values'),
        
        easyforms.TitleSelectField('title-select-field'),
        easyforms.HtmlField('html-field', help_text='This required CKEditor to be installed in '
                            'static/ckeditor'),
        easyforms.TimeInputField('time-input-field'),
        easyforms.FileUploadField('file-upload-field', '.pdf'),
        easyforms.ImageUploadField('image-upload-field', min_width=100, min_height=100,
                                   max_height=200, max_width=200,
                                   help_text='This allows restrictions on image size. This example '
                                   'accepts images from 100x100 to 200x200'),
        easyforms.MultiCheckboxField('multi-checkbox-field', values=EXAMPLE_KEY_PAIRS),
        easyforms.CardNumberField('card-number', help_text='Only accepts valid card numbers')
        
    ])
    
    form.read_form_data()
    
    if form.ready:
        log.info('The form was submitted and passed validation!')
    
    return render_template('large_multisection_form.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/multisection-form-custom', methods=['GET', 'POST'])
def multisection_form_custom():
    form = easyforms.Form([], read_form_data=False, form_type=easyforms.VERTICAL, show_asterisks=True)

    form.add_section('Section 1', [
        easyforms.TextField('text-field', required=True,
                            help_text='Any text will be accepted'),
        easyforms.PasswordField('password-field', required=True),
        easyforms.IntegerField('integer-field', min_value=1, max_value=20),
        easyforms.DecimalField('decimal-field', min_value=-10, max_value=1000,
                               step=decimal.Decimal('0.1'))
    ])

    form.add_section('Section 2', [
        easyforms.BooleanCheckbox('boolean-checkbox', default=False),
        easyforms.HiddenField('hidden-field', value='bananas'),
        easyforms.NameField('name-field'),
        easyforms.SelectField('select-field', EXAMPLE_KEY_PAIRS, empty_option=True, required=True),
        easyforms.EmailField('email-field')
    ])

    form.read_form_data()
    
    if form.ready:
        log.info('The form was submitted and passed validation!')
    
    return render_template('multisection_form_custom.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/custom-validation-1', methods=['GET', 'POST'])
def custom_validation_1():
    form = easyforms.Form([
        easyforms.IntegerField('an-integer', help_text='Any whole number!', required=True),
        easyforms.TextField('two-or-three', required=True)
    ], form_type=easyforms.VERTICAL, max_width=700)
    
    if form.submitted:
        if form['two-or-three'] and not form.has_error('two-or-three'):
            two_or_three = form['two-or-three']
            if two_or_three != 'two' and two_or_three != 'three':
                form.set_error('two-or-three', 'Please enter "two" or "three" (lower case)')

    if form.ready:
        log.info('The form was submitted and passed validation!')
    
    return render_template('custom_validation_1.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/custom-validation-2', methods=['GET', 'POST'])
def custom_validation_2():
    def is_two_or_three(val):
        if val and val != 'two' and val != 'three':
            return 'Please enter "two" or "three" (lower case)'

    form = easyforms.Form([
        easyforms.IntegerField('an-integer', help_text='Any whole number!', required=True),
        easyforms.TextField('two-or-three', required=True, validators=[is_two_or_three])
    ], form_type=easyforms.VERTICAL, max_width=700)
    
    if form.ready:
        log.info('The form was submitted and passed validation!')
    
    return render_template('custom_validation_2.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/custom-fields', methods=['GET', 'POST'])
def custom_fields():
    default_list = ['hello', 'goodbye', 'foo']

    form = easyforms.Form([
        customfields.BasicCustomTextField('username', required=True),
        customfields.CustomTextField('another-text-field', required=True),
        customfields.CommaSeparatedListField('list', value=default_list),
        customfields.UpperCaseTextField('upper-case', required=True,
                                        help_text='Whatever\'s entered into this will be converted '
                                        'to upper case')
    ], form_type=easyforms.VERTICAL)

    if form.ready:
        log.info('The form was submitted and passed validation!')
        log.info('This is a list: {}'.format(form['list']))
    
    return render_template('custom_fields.html', form=form, submitted_data=get_submitted_data(form))
