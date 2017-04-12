"""
Unit tests for forms library
"""

from decimal import Decimal

import pytest

from ..forms import Field, Form
from .. import forms
from app import create_test_app

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'


@pytest.fixture(scope='module')
def app():
    flask_app = create_test_app()

    flask_app.config['TESTING'] = True
    return flask_app


def test_field():
    field = Field('test-field')
    assert field.label == 'Test Field'
    assert field.id == 'test-field'
    assert field.value is None
    assert field.max_width is None
    assert field.width == 9
    assert field.help_text_width == 9
    assert field.label_width == 3
    assert field.column_breakpoint == 'sm'
    assert field.form is None
    assert field.form_type is None

    field.render()

    form = Form([field], label_width=2, read_form_data=False, submit_text=None)
    
    assert field.form == form
    assert field.form_type == forms.HORIZONTAL
    assert field.width == 9
    assert field.help_text_width == 9
    assert field.label_width == 2
    assert field.label_column_class == 'col-sm-2 control-label'
    assert field.input_no_label_column_class == 'col-sm-offset-2 col-sm-9'
    assert field.help_text_column_class == 'col-sm-offset-2 col-sm-9'
    assert field.error_column_class == 'col-sm-offset-2 col-sm-9'
    assert field.input_column_class == 'col-sm-9'
    assert field.input_column_style == ''
    assert field.input_column_attributes == 'class="col-sm-9"'
    assert field.form_group_classes == 'form-group'
    
    field2 = Field('another-field', width=6, help_text_width=5, label_width=4, max_width=100,
                   label='Just Another Field!', id='field')
    form2 = Form([field2], read_form_data=False, submit_text=None)

    assert field2.form == form2
    assert field2.label == 'Just Another Field!'
    assert field2.id == 'field'
    assert field2.form_type == forms.HORIZONTAL
    assert field2.width == 6
    assert field2.help_text_width == 5
    assert field2.label_width == 4
    assert field2.label_column_class == 'col-sm-4 control-label'
    assert field2.input_no_label_column_class == 'col-sm-offset-4 col-sm-6'
    assert field2.help_text_column_class == 'col-sm-offset-4 col-sm-5'
    assert field2.error_column_class == 'col-sm-offset-4 col-sm-5'
    assert field2.input_column_class == 'col-sm-6'
    assert field2.input_column_style == 'max-width: 100px;'
    assert field2.input_column_attributes == 'class="col-sm-6" style="max-width: 100px;"'
    assert field2.form_group_classes == 'form-group'

    field2.label_width = 0
    field2.column_breakpoint = 'md'
    assert field2.label_width == 0
    assert field2.label_column_class == 'control-label'
    assert field2.input_no_label_column_class == 'col-md-6'
    assert field2.help_text_column_class == 'col-md-5'
    assert field2.error_column_class == 'col-md-5'
    assert field2.input_column_class == 'col-md-6'
    assert field2.input_column_style == 'max-width: 100px;'
    assert field2.input_column_attributes == 'class="col-md-6" style="max-width: 100px;"'
    assert field2.form_group_classes == 'form-group'

    field2.error = 'Test error'
    assert field2.form_group_classes == 'form-group has-error'

    field3 = Field('another-field', max_width='25%', form_group_css_class='testing')
    form3 = Form([field3], read_form_data=False, submit_text=None, form_type=forms.VERTICAL)

    assert field3.form == form3
    assert field3.form_type == forms.VERTICAL
    assert field3.width == 9
    assert field3.help_text_width == 9
    assert field3.label_width == 3
    assert field3.label_column_class == 'control-label'
    assert field3.input_no_label_column_class == ''
    assert field3.help_text_column_class == ''
    assert field3.error_column_class == ''
    assert field3.input_column_class == ''
    assert field3.input_column_style == 'max-width: 25%;'
    assert field3.input_column_attributes == 'style="max-width: 25%;"'
    assert field3.form_group_classes == 'form-group testing'

    field3.error = 'Test'
    assert field3.form_group_classes == 'form-group has-error testing'


def test_basic_form(app):
    text_field = forms.TextField('text')
    password_field = forms.PasswordField('password')
    text_area_field = forms.TextAreaField('text-area')
    integer_field = forms.IntegerField('integer')
    decimal_field = forms.DecimalField('decimal')
    
    fields = [text_field, password_field, text_area_field, integer_field, decimal_field]
    num_fields = len(fields) + 1
    
    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'text': 'testing',
            'password': 'qwe123',
            'text-area': 'more\ntext',
            'integer': '123',
            'decimal': '456.78'}):

        form = Form(fields)
        
        assert len(form.fields) == num_fields
        assert len(form.all_fields) == num_fields

        for field in form.all_fields:
            assert field.form == form
        
        # Make sure no exceptions are thrown
        form.render()

        assert form.submitted == True
        assert form.ready == True
        assert form['text'] == 'testing'
        assert form['password'] == 'qwe123'
        assert form['text-area'] == 'more\ntext'
        assert form['integer'] == 123
        assert form['decimal'] == Decimal('456.78')
        assert form.get_field('decimal')
        assert form.get_field('bananas') is None


def test_form_add_methods(app):
    text_field = forms.TextField('text')
    password_field = forms.PasswordField('password')
    text_area_field = forms.TextAreaField('text-area')
    integer_field = forms.IntegerField('integer')
    decimal_field = forms.DecimalField('decimal')
    
    fields = [text_field, password_field, text_area_field, integer_field, decimal_field]

    form = Form(read_form_data=False)
    form.add_field(text_field)
    form.add_field(password_field)
    form.add_fields([text_area_field, integer_field, decimal_field])
    
    num_fields = len(fields) + 1

    assert len(form.fields) == num_fields
    assert len(form.all_fields) == num_fields
    assert form.submitted == False
    assert form.ready == False

    for field in form.all_fields:
        assert field.form == form

    # Make sure no exceptions are thrown
    form.render()

    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'text': 'testing',
            'password': 'qwe123',
            'text-area': 'more\ntext',
            'integer': '123',
            'decimal': '456.78'}):

        form.read_form_data()

        assert form.submitted == True
        assert form.ready == True
        assert form['text'] == 'testing'
        assert form['password'] == 'qwe123'
        assert form['text-area'] == 'more\ntext'
        assert form['integer'] == 123
        assert form['decimal'] == Decimal('456.78')


def test_form_sections(app):
    text_field = forms.TextField('text')
    password_field = forms.PasswordField('password')
    text_area_field = forms.TextAreaField('text-area')
    integer_field = forms.IntegerField('integer')
    decimal_field = forms.DecimalField('decimal')
    
    fields = [text_field, password_field, text_area_field, integer_field, decimal_field]

    form = Form(read_form_data=False, css_class='foo')
    form.add_field(text_field)
    form.add_section('section-1', [password_field])
    form.add_section('section-2', [text_area_field, integer_field, decimal_field])
    form.add_section('section-3', [])
    
    num_fields = len(fields) + 1

    assert len(form.fields) == 2
    assert len(form.all_fields) == num_fields
    assert form.submitted == False
    assert form.ready == False

    assert form.has_section('section-1')
    assert form.get_section('section-2') is not None
    assert form.has_section('section-3')

    assert form.is_section_empty('section-1') is False
    assert form.is_section_empty('section-2') is False
    assert form.is_section_empty('section-3')

    for field in form.all_fields:
        assert field.form == form

    # Make sure no exceptions are thrown
    form.render()
    form.render_before_sections()
    form.render_after_sections()
    form.render_sections()
    form.render_section('section-1')

    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'text': 'testing',
            'password': 'qwe123',
            'text-area': 'more\ntext',
            'integer': '123',
            'decimal': '456.78'}):

        form.read_form_data()

        assert form.submitted == True
        assert form.ready == True
        assert form['text'] == 'testing'
        assert form['password'] == 'qwe123'
        assert form['text-area'] == 'more\ntext'
        assert form['integer'] == 123
        assert form['decimal'] == Decimal('456.78')


def test_form_invalid_method(app):
    with pytest.raises(ValueError):
        Form(method='PUT')


def test_form_get(app):
    with app.test_request_context(
            '/?{}=1&text=hello&integer=42'.format(Form.SUBMITTED_HIDDEN_INPUT_NAME)):

        form = Form([forms.TextField('text'), forms.IntegerField('integer')], method='GET')
        
        assert form['text'] == 'hello'
        assert form['integer'] == 42


def test_multiple_read_form_data(app):
    with app.test_request_context(
            '/?{}=1'.format(Form.SUBMITTED_HIDDEN_INPUT_NAME)):

        form = Form([], method='GET')
        
        with pytest.raises(forms.exceptions.AlreadyProcessed):
            form.read_form_data()


def test_readonly_field(app):
    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'text': 'overwritten'}):

        form = Form([forms.TextField('text', value='original', readonly=True)])
        
        assert form['text'] == 'original'


def test_basic_fields_invalid_types():
    with pytest.raises(ValueError):
        forms.PasswordField('test', type='text')

    with pytest.raises(ValueError):
        forms.IntegerField('test', type='submit')

    with pytest.raises(ValueError):
        forms.DecimalField('text', type='submit')


def test_validation_part_1(app):
    def create_fields():
        return [
            forms.TextField('required', required=True),
            forms.TextField('anything-goes'),
            forms.IntegerField('integer', min_value=5, max_value=10),
            forms.EmailField('email'),
            forms.UrlField('url')
        ]

    data = {
        Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
        'required': '',
        'anything-goes': '',
        'integer': '1',
        'email': 'spoons',
        'url': 'not-a-url'
    }

    with app.test_request_context('/', method='POST', data=data):
        form = forms.Form(create_fields())
        assert form.submitted
        assert form.ready is False
        
        assert form.get_error('required') == 'Required'
        assert form.get_error('anything-goes') is None
        assert form.get_error('integer') == 'Must be at least 5'
        assert form.get_error('email') == 'Must be a valid email address'
        assert form.get_error('url').startswith('Must be a valid URL')

    data['required'] = 'something'
    data['integer'] = 'bananas'
    data['email'] = 'spoons@cutlery'
    data['url'] = 'http://example.org/'

    with app.test_request_context('/', method='POST', data=data):
        form = forms.Form(create_fields())
        assert form.submitted
        assert form.ready is False
        
        assert form.get_error('required') is None
        assert form.get_error('anything-goes') is None
        assert form.get_error('integer') == 'Invalid integer'
        assert form.get_error('email') == 'Must be a valid email address'
        assert form.get_error('url') is None

    data['integer'] = '234754392374'
    data['email'] = 'spoons@cutlery.co'

    with app.test_request_context('/', method='POST', data=data):
        form = forms.Form(create_fields())
        assert form.submitted
        assert form.ready is False
        
        assert form.get_error('required') is None
        assert form.get_error('anything-goes') is None
        assert form.get_error('integer') == 'Must be less than or equal to 10'
        assert form.get_error('email') is None
        assert form.get_error('url') is None

    data['integer'] = '7'

    with app.test_request_context('/', method='POST', data=data):
        form = forms.Form(create_fields())
        assert form.submitted
        assert form.ready
        
    data['integer'] = ''
    data['email'] = ''
    data['url'] = ''
    
    with app.test_request_context('/', method='POST', data=data):
        form = forms.Form(create_fields())
        assert form.submitted
        assert form.ready


def test_disabled_validation(app):
    def create_fields():
        return [
            forms.TextField('required', required=True),
            forms.TextField('anything-goes'),
            forms.IntegerField('integer', min_value=5, max_value=10),
            forms.EmailField('email'),
            forms.UrlField('url')
        ]

    data = {
        Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
        'required': '',
        'anything-goes': '',
        'integer': '1',
        'email': 'spoons',
        'url': 'not-a-url',
        'required2': ''
    }

    with app.test_request_context('/', method='POST', data=data):
        form = forms.Form(create_fields())
        
        assert form.submitted
        assert form.ready is False
        
        assert form.get_error('required') == 'Required'
        assert form.get_error('anything-goes') is None
        assert form.get_error('integer') == 'Must be at least 5'
        assert form.get_error('email') == 'Must be a valid email address'
        assert form.get_error('url').startswith('Must be a valid URL')

    form2 = forms.Form(create_fields(), read_form_data=False)
    form2.add_section('section', [forms.TextField('required2', required=True)])

    form2.disable_validation('required')
    
    with app.test_request_context('/', method='POST', data=data):
        form2.read_form_data()
        assert form2.submitted
        assert form2.ready is False
        
        assert form2.get_error('required') is None
        assert form2.has_error('required2')
    
    # Disable all validation
    form3 = forms.Form(create_fields(), read_form_data=False)
    form3.add_section('section', [forms.TextField('required2', required=True)])
    
    for field in form3.all_fields:
        form3.disable_validation(field.name)

    with app.test_request_context('/', method='POST', data=data):
        form3.read_form_data()
        assert form3.submitted
        assert form3.ready is True


def test_missing_value(app):
    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1'}):

        with pytest.raises(forms.exceptions.FieldNotFound):
            Form([forms.TextField('text')])


def test_form_not_processed():
    form = Form([forms.TextField('a')], read_form_data=False)

    with pytest.raises(forms.exceptions.FormNotProcessed):
        form['a']
    
    with pytest.raises(forms.exceptions.FormNotProcessed):
        form.get_error('a')


def test_invalid_field_name(app):
    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'text': 'dsfsdf'
    }):
        form = Form([forms.TextField('text')])
        
        with pytest.raises(forms.exceptions.FieldNotFound):
            form['bananas']
        
        with pytest.raises(forms.exceptions.FieldNotFound):
            form.get_error('bananas')

        with pytest.raises(forms.exceptions.FieldNotFound):
            form.disable_validation('banananas')


def test_set_error(app):
    form = Form([forms.TextField('field1'), forms.TextField('field2')], read_form_data=False)
    form.add_section('section', [forms.TextField('field3')])
    
    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'field1': '',
            'field2': '',
            'field3': ''}):

        form.read_form_data()

        assert form.get_error('field1') is None
        assert form.has_error('field1') is False
        assert form.get_error('field2') is None
        assert form.has_error('field2') is False
        assert form.get_error('field3') is None
        assert form.has_error('field3') is False

        form.set_error('field1', 'This is a test')

        assert form.get_error('field1') == 'This is a test'
        assert form.has_error('field1') is True
        assert form.get_error('field2') is None
        assert form.has_error('field2') is False
        assert form.get_error('field3') is None
        assert form.has_error('field3') is False
        
        form.set_error('field3', 'Testing')

        assert form.get_error('field1') == 'This is a test'
        assert form.has_error('field1') is True
        assert form.get_error('field2') is None
        assert form.has_error('field2') is False
        assert form.get_error('field3') == 'Testing'
        assert form.has_error('field3') is True

        with pytest.raises(forms.exceptions.FieldNotFound):
            form.set_error('field4', 'Doesn\'t exist')
        
        with pytest.raises(forms.exceptions.FieldNotFound):
            form.has_error('field4')


def test_set_value(app):
    form = Form([forms.TextField('field1'), forms.TextField('field2')], read_form_data=False)
    form.add_section('section', [forms.TextField('field3')])
    
    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'field1': '',
            'field2': '',
            'field3': ''}):

        form.read_form_data()

        assert form['field1'] is None
        assert form['field2'] is None
        assert form['field3'] is None

        form.set_value('field1', 'This is a test')

        assert form['field1'] == 'This is a test'
        assert form['field2'] is None
        assert form['field3'] is None
        
        form.set_value('field3', 'Testing')

        assert form['field1'] == 'This is a test'
        assert form['field2'] is None
        assert form['field3'] == 'Testing'

        with pytest.raises(forms.exceptions.FieldNotFound):
            form.set_value('field4', 'Doesn\'t exist')


def test_clear(app):
    form = Form([
        forms.TextField('field1'),
        forms.TextField('field2', noclear=True)
    ], read_form_data=False)

    form.add_section('section', [
        forms.TextField('field3'),
        forms.IntegerField('field4', min_value=5)])
    
    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'field1': '1',
            'field2': '2',
            'field3': '3',
            'field4': '4'}):

        form.read_form_data()

        assert form['field1'] == '1'
        assert form['field2'] == '2'
        assert form['field3'] == '3'
        assert form['field4'] == 4

        assert form.get_error('field4') == 'Must be at least 5'

        form.clear()

        assert form['field1'] is None
        # Field 2 has noclear == True
        assert form['field2'] == '2'
        assert form['field3'] is None
        assert form['field4'] is None

        assert form.has_error('field4') is False


def test_multipart(app):
    form = Form([
        forms.TextField('field1'),
        forms.IntegerField('field2'),
        forms.HiddenField('field3', 'foo'),
        forms.HtmlField('field4')
    ], read_form_data=False)

    assert form.multipart is False

    form.add_field(forms.FileUploadField('file-upload', ''))

    assert form.multipart is True


def test_duplicate_field(app):
    form = Form([forms.TextField('field1')], read_form_data=False)
    
    with pytest.raises(forms.exceptions.DuplicateField):
        form.add_field(forms.IntegerField('field1'))

    with pytest.raises(forms.exceptions.DuplicateField):
        form.add_fields([forms.IntegerField('integer'), forms.TextAreaField('field1')])

    assert form.get_field('integer') is None

    with pytest.raises(forms.exceptions.DuplicateField):
        form.add_section('section1', [forms.CodeField('field1')])

    with pytest.raises(forms.exceptions.DuplicateField):
        form.add_section('section2', [forms.IntegerField('duplicate'),
                                      forms.DatePickerField('duplicate')])

    assert form.get_field('integer') is None

    with pytest.raises(forms.exceptions.DuplicateField):
        Form([forms.TextField('a'), forms.TextField('a')], read_form_data=False)


def test_get_if_present(app):
    form = Form([
        forms.TextField('field1'),
        forms.TextField('field2', noclear=True)
    ], read_form_data=False)

    form.add_section('section', [
        forms.TextField('field3'),
        forms.IntegerField('field4', min_value=5)])
    
    with app.test_request_context('/', method='POST', data={
            Form.SUBMITTED_HIDDEN_INPUT_NAME: '1',
            'field1': '1',
            'field2': '2',
            'field3': '3',
            'field4': '4'}):

        with pytest.raises(forms.exceptions.FormNotProcessed):
            form.get_if_present('field1')

        form.read_form_data()

        assert form['field1'] == '1'
        assert form['field2'] == '2'
        assert form['field3'] == '3'
        assert form['field4'] == 4
        
        assert form.get_if_present('field1') == '1'
        assert form.get_if_present('field2', None) == '2'
        assert form.get_if_present('field3', 'x') == '3'
        assert form.get_if_present('field4') == 4
        assert form.get_if_present('field5') is None
        assert form.get_if_present('field6', 'bananas') == 'bananas'
        assert form.get_if_present('field7', 12) == 12

