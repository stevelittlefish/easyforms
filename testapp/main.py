"""
Main blueprint for test app
"""

import logging
import decimal
from enum import Enum

from flask import Blueprint, render_template, current_app, url_for, request

import customfields
import easyforms
import sessionutil
from easyforms import styles


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
    KeyValue('Looooooooooooooong label text to make things wide', 'long')
]


class ColourEnum(Enum):
    RED = 'Red'
    GREEN = 'Green'
    BLUE = 'Blue'
    RAINBOW = 'Rainbow'


def get_submitted_data(form):
    submitted_data = None

    if form.ready:
        submitted_data = {}
        for field_name in form.field_dict:
            submitted_data[field_name] = form[field_name]

    return submitted_data


@main.before_request
def main_before_request():
    new_render_style = request.args.get('--render-style')
    
    if new_render_style in styles.ALL_STYLES:
        sessionutil.set_render_style(new_render_style)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/simple-form', methods=['GET', 'POST'])
def simple_form():
    form = easyforms.Form([
        easyforms.TextField('some-text', required=True),
        easyforms.IntegerField('an-integer', help_text='Any whole number!', optional=True),
        easyforms.SelectField('pick-a-value', EXAMPLE_KEY_PAIRS, empty_option=True,
                              required=True)
    ], form_type=easyforms.VERTICAL, max_width=700, style=sessionutil.get_render_style())

    if form.ready:
        log.info('The form was submitted and passed validation!')
    
    return render_template('simple_form.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/large-multisection-form', methods=['GET', 'POST'])
def large_multisection_form():
    form = easyforms.Form([], read_form_data=False, style=sessionutil.get_render_style(),
                          form_type=easyforms.HORIZONTAL)

    form.add_section('Basic Fields', [
        easyforms.TextField('text-field', required=True,
                            help_text='Any text will be accepted'),
        easyforms.PasswordField('password-field', required=True, width=4),
        easyforms.TextAreaField('text-area', required=True,
                                help_text='You can enter multiple lines of text!'),
        easyforms.IntegerField('integer-field', width=2, min_value=1, max_value=20),
        easyforms.DecimalField('decimal-field', min_value=-10, max_value=1000,
                               step=decimal.Decimal('0.1'), width=2),
        easyforms.BooleanCheckbox('boolean-checkbox', default=False,
                                  help_text='This is required'),
        easyforms.HiddenField('hidden-field', value='bananas'),
        easyforms.NameField('name-field', width=4),
        easyforms.SelectField('select-field', EXAMPLE_KEY_PAIRS, empty_option=True, required=True,
                              help_text='You must select something otherwise you will get '
                                        'a validation error')
    ])

    form.add_section('Advanced Fields', [
        easyforms.CodeField('code-field', width=6),
        easyforms.EmailField('email-field', width=6),
        easyforms.UrlField('url-field'),
        easyforms.PhoneNumberField('phone-number-field'),
        easyforms.PostcodeField('postcode-field', width=4),
        easyforms.ColourField('colour-field', width=1),
        easyforms.GenderField('gender-field', required=True,
                              help_text='You must include images static/img/male-symbol.png and '
                              'static/img/female-symbol.png for this to work'),
        easyforms.DateSelectField('date-select-field', required=True,
                                  help_text='Enter a date please'),
        easyforms.YearMonthSelectField('year-month-select-field', required=True,
                                       help_text='This field accepts a year and month only'),
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
        easyforms.TimeInputField('time-input-field', help_text='Enter a time in format HH:MM',
                                 required=True),
        easyforms.FileUploadField('file-upload-field', ''),
        easyforms.ImageUploadField('image-upload-field', min_image_width=100, min_image_height=100,
                                   max_image_height=200, max_image_width=200,
                                   help_text='This allows restrictions on image size. This example '
                                   'accepts images from 100x100 to 200x200'),
        easyforms.MultiCheckboxField('multi-checkbox-field', values=EXAMPLE_KEY_PAIRS,
                                     help_text='Please select at least one of the above options'),
        easyforms.CardNumberField('card-number', help_text='Only accepts valid card numbers'),
        easyforms.MultiSubmitButton('multi-submit',
                                    ['Submit', 'Proceed', 'Continue', 'OK'],
                                    ['btn-secondary', 'btn-danger', 'btn-success']),
        easyforms.EnumSelectField('enum-select', ColourEnum, value=ColourEnum.RED)
        
    ])

    form.add_section('Input Groups', [
        easyforms.IntegerField('units', units='%', width=3),
        easyforms.IntegerField('pre-units', pre_units='£', width=4),
        easyforms.IntegerField('both-units', pre_units='£', units='.00', width=4, required=True,
                               help_text='Make sure you fill this one in')
    ])
    
    form.read_form_data()

    if form.submitted:
        if not form['boolean-checkbox']:
            form.set_error('boolean-checkbox', 'Please tick this box')

        if not form['multi-checkbox-field']:
            form.set_error('multi-checkbox-field', 'You must select at least one of the above options')
    
    if form.ready:
        log.info('The form was submitted and passed validation!')
    
    return render_template('large_multisection_form.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/readonly-fields', methods=['GET', 'POST'])
def readonly_fields():
    form = easyforms.Form([
        easyforms.TextField('some-text', required=True),
        easyforms.TextField('readonly-text', readonly=True, value='You can\'t change me!'),
        easyforms.IntegerField('an-integer', help_text='Any whole number!', required=True),
        easyforms.SelectField('pick-a-value', EXAMPLE_KEY_PAIRS, empty_option=True,
                              optional=True),
        easyforms.SelectField('pick-another-value', EXAMPLE_KEY_PAIRS, readonly=True,
                              value=EXAMPLE_KEY_PAIRS[1], help_text='This field cannot be changed'),
    ], form_type=easyforms.VERTICAL, max_width=700, style=sessionutil.get_render_style())

    if form.ready:
        log.info('The form was submitted and passed validation!')
    
    return render_template('readonly_fields.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/readonly-form', methods=['GET', 'POST'])
def readonly_form():
    form = easyforms.Form([
        easyforms.TextField('text-field', required=True,
                            help_text='Any text will be accepted'),
        easyforms.PasswordField('password-field', required=True, width=4),
        easyforms.IntegerField('integer-field', width=2, min_value=1, max_value=20),
        easyforms.DecimalField('decimal-field', min_value=-10, max_value=1000,
                               step=decimal.Decimal('0.1'), width=2),
        easyforms.BooleanCheckbox('boolean-checkbox', default=False),
        easyforms.HiddenField('hidden-field', value='bananas'),
        easyforms.NameField('name-field', width=4),
        easyforms.SelectField('select-field', EXAMPLE_KEY_PAIRS, empty_option=True, required=True),

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
        easyforms.ImageUploadField('image-upload-field', min_image_width=100, min_image_height=100,
                                   max_image_height=200, max_image_width=200,
                                   help_text='This allows restrictions on image size. This example '
                                   'accepts images from 100x100 to 200x200'),
        easyforms.MultiCheckboxField('multi-checkbox-field', values=EXAMPLE_KEY_PAIRS),
        easyforms.CardNumberField('card-number', help_text='Only accepts valid card numbers')
    ], form_type=easyforms.VERTICAL, max_width=700, readonly=True, style=sessionutil.get_render_style())

    if form.ready:
        raise Exception('Readonly form was somehow submitted!')
    
    return render_template('readonly_form.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/multisection-form-custom', methods=['GET', 'POST'])
def multisection_form_custom():
    form = easyforms.Form([], read_form_data=False, form_type=easyforms.VERTICAL, show_asterisks=True, style=sessionutil.get_render_style())

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
    ], form_type=easyforms.VERTICAL, max_width=700, style=sessionutil.get_render_style())
    
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
    ], form_type=easyforms.VERTICAL, max_width=700, style=sessionutil.get_render_style())
    
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
    ], form_type=easyforms.VERTICAL, style=sessionutil.get_render_style())

    if form.ready:
        log.info('The form was submitted and passed validation!')
        log.info('This is a list: {}'.format(form['list']))
    
    return render_template('custom_fields.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/captcha', methods=['GET', 'POST'])
def captcha():
    form = easyforms.Form([
        easyforms.TextField('required-text-field', required=True),
        easyforms.TextField('optional-text-field'),
        easyforms.RecaptchaField('recaptcha', site_key=current_app.config['RECAPTCHA_SITE_KEY'],
                                 secret_key=current_app.config['RECAPTCHA_SECRET_KEY'])
    ], show_asterisks=True, style=sessionutil.get_render_style())

    if form.ready:
        log.info('The form was submitted and passed validation!')

    return render_template('captcha.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/ckeditor', methods=['GET', 'POST'])
def ckeditor():
    config = easyforms.CkeditorConfig(
        default_height=300,
        filemanager_url=None,
        codesnippet_enabled=True,
        custom_styles_js_url=url_for('static', filename='js/ckeditor_styles.js'),
        custom_contents_css_url=url_for('static', filename='css/ckeditor_contents.css'),
        unwrap_images=True
    )

    form = easyforms.Form([
        easyforms.CkeditorField('ckeditor', config=config, required=True,
                                help_text='Use this editor to edit rich HTML based content'),
    ], form_type=easyforms.VERTICAL, style=sessionutil.get_render_style())

    return render_template('ckeditor.html', form=form, submitted_data=get_submitted_data(form))
    

@main.route('/single-button-clone', methods=['GET', 'POST'])
def single_button_clone():
    form = easyforms.Form([
        easyforms.TextField('some-text', required=True),
        easyforms.IntegerField('an-integer', help_text='Any whole number!', required=True),
        easyforms.SelectField('pick-a-value', EXAMPLE_KEY_PAIRS, empty_option=True,
                              optional=True),
        easyforms.BooleanCheckbox('boolean')
    ], form_type=easyforms.VERTICAL, max_width=700, style=sessionutil.get_render_style())

    if form.ready:
        log.info('The form was submitted and passed validation!')

    button1 = form.create_single_button_clone('All The Same Values')
    button2 = form.create_single_button_clone('Some Text = FooBar')
    button2.set_value('some-text', 'FooBar')
    
    return render_template('single_button_clone.html', form=form, button1=button1, button2=button2,
                           submitted_data=get_submitted_data(form))


@main.route('/getaddress', methods=['GET', 'POST'])
def getaddress():
    form = easyforms.Form([
        easyforms.NameField('first-name', required=True),
        easyforms.NameField('last-name', required=True),
        easyforms.GetaddressPostcodeField(
            'postcode', current_app.config['GETADDRESS_API_KEY'], required=True,
            line1_id='address-line-1', line2_id='address-line-2', line3_id='address-line-3',
            town_id='city', width=5
        ),
        easyforms.TextField('address-line-1', required=True),
        easyforms.TextField('address-line-2'),
        easyforms.TextField('address-line-3'),
        easyforms.TextField('city', label='Town/City', required=True),
        easyforms.TextField('billing-phone-no', required=True, label='Contact Phone No.')
    ], form_type=easyforms.HORIZONTAL, max_width=700, style=sessionutil.get_render_style())

    return render_template('getaddress.html', form=form, submitted_data=get_submitted_data(form))


@main.route('/filemanager', methods=['GET', 'POST'])
def filemanager():
    form = easyforms.Form([
        easyforms.FilemanagerField('file', required=True),
        easyforms.TextField('must-not-be-blank', required=True)
    ], form_type=easyforms.VERTICAL, style=sessionutil.get_render_style())

    return render_template('filemanager.html', form=form, submitted_data=get_submitted_data(form))
