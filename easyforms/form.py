
"""
Base classes for forms and fields
"""

import logging
from collections import OrderedDict

from flask import Markup, request

from . import validate
from . import exceptions
from . import formtype
from . import styles
from .env import env

__author__ = 'Stephen Brown (Little Fish Solutions LTD)'

log = logging.getLogger(__name__)

_csrf_generation_function = None

_default_form_type = formtype.HORIZONTAL


def init_csrf(csrf_generation_function):
    """
    Calling this function will initialised CSRF behaviour in all forms in the application.
    Pass in a function that returns a string containing a valid CSRF token, and this function
    will be called in each form, and will add a hidden input named "_csrf_token". This does
    not validate the token.
    """
    global _csrf_generation_function

    _csrf_generation_function = csrf_generation_function


def convert_name_to_label(name):
    """Convert hyphen separated field names to label text"""
    return name.replace('-', ' ').title()


def set_default_form_type(form_type):
    global _default_form_type

    if form_type not in formtype.ALL_FORM_TYPES:
        raise ValueError('Invalid form type: {}'.format(form_type))

    _default_form_type = form_type


class Field(object):
    def __init__(self, name, label=None, value=None, id=None, optional=False, css_class='',
                 readonly=False, help_text=None, strip_value=True, convert_empty_to_none=True,
                 validators=[], required=False, render_after_sections=False, allow_missing=False,
                 width=9, help_text_width=9, label_width=None, units=None, pre_units=None,
                 form_group_css_class=None, noclear=False, requires_multipart=False,
                 column_breakpoint=None, max_width=None, multiple_inputs=False,
                 base_input_css_class='form-control'):
        """
        :param name: The name of the field (the name field in the generated input)
        :param label: The label text.  If None, is automatically generated from the name
        :param value: The value of the field
        :param id: The id for the input.  If None, the name is used
        :param optional: If True, '(optional)' is rendered next to the label.  Defaults to False
        :param css_class: If set, adds extra css classes to the input (space separate inside string)
        :param readonly: If True, makes this field readonly.  If the parent form.readonly is True,
                         then that will take precendence over this and this field will also be
                         readonly.  Defaults to False
        :param help_text: Text rendered beside the input
        :param strip_value: If True (by default) strips whitespace off of the submitted value
        :param convert_empty_to_none: If True (by default) converts empty strings to None in submitted values
        :param validators: List of validation functions
        :param required: If True, automatically adds the 'required' validator.  Defaults to False
        :param render_after_sections: If True, will render this after all sections in form.render_all().
                                      Defaults to False
        :param allow_missing: If True, we won't throw an error if this field is totally missing from the submitted
                              values.  Used to implement checkboxes, defaults to False
        :param width: The width of this component in the bootstrap grid system
        :param help_text_width: The width of the help text for this component in the bootstrap grid system
        :param label_width: The width of the label for this component in the bootstrap grid system
        :param units: Units to append after the input
        :param pre_units: Units to prepend before the input
        :param form_group_css_class: The css class to append to the form group
        :param noclear: If set to True, this field will not be cleared by Form.clear()
        :param requires_multipart: Does this field require multipart form data?  Used for file uploads
        :param column_breakpoint: Bootstrap column breakpoint where horizontal form degrades into
                                  vertical form.  Values: sm, md, lg.  If None (default) inherit
                                  from form
        :param max_width: Maximum width, either an integer value representing the number of pixels
                          or a string containing a units i.e. '50%' or '240px'
        :param multiple_inputs: Set to true if this field consists of multiple input tags with the same
                                name.  This will cause value to be an list of strings after
                                processing form data, with each element containing one of the
                                submitted values
        :param base_input_css_class: The default css class to put on the input. Defaults to
                                     form-control
        """
        self.name = name

        if label is None:
            self.label = convert_name_to_label(name)
        else:
            self.label = label

        if id is None:
            self.id = name
        else:
            self.id = id

        self.value = value
        self.optional = optional
        self.css_class = css_class
        self._readonly = readonly
        self.help_text = help_text
        self.strip_value = strip_value
        self.convert_empty_to_none = convert_empty_to_none
        self.validators = validators[:]
        self.error = None
        self.render_after_sections = render_after_sections
        self.allow_missing = allow_missing
        self.width = width
        self.help_text_width = help_text_width
        self._label_width = label_width
        self.units = units
        self.pre_units = pre_units
        self.form_group_css_class = form_group_css_class
        self.noclear = noclear
        self.requires_multipart = requires_multipart
        self._column_breakpoint = column_breakpoint
        self.max_width = max_width
        if isinstance(self.max_width, int):
            self.max_width = '{}px'.format(self.max_width)
        self.multiple_inputs = multiple_inputs
        self.base_input_css_class = base_input_css_class

        # This should get set by the form when we add it
        self.form = None

        # Handle common validation options
        self.required = required
        if required:
            self.validators.append(validate.required)
    
    @property
    def label_html(self):
        show_asterisks = False
        if self.form:
            show_asterisks = self.form.show_asterisks

        if show_asterisks and self.required:
            return Markup('<span class="required">*</span> ') + self.label

        return self.label

    @property
    def label_width(self):
        if self._label_width is not None:
            return self._label_width

        if self.form:
            return self.form.label_width

        return 3

    @label_width.setter
    def label_width(self, val):
        self._label_width = val

    @property
    def column_breakpoint(self):
        if self._column_breakpoint is not None:
            return self._column_breakpoint

        if self.form:
            return self.form.column_breakpoint

        return 'sm'

    @column_breakpoint.setter
    def column_breakpoint(self, val):
        self._column_breakpoint = val

    @property
    def readonly(self):
        if self.form and self.form.readonly is True:
            return True

        return self._readonly
    
    @readonly.setter
    def readonly(self, val):
        self._readonly = val

    def render(self):
        return '<div class="alert alert-warning">Render not implemented for {}!</div>'.format(self.__class__.__name__)

    def convert_value(self):
        """Convert the value from the submitted text to whatever type is required.  May cause a validation error."""
        # Default to doing nothing
        pass

    def validate(self):
        """Run the form value through the validators, and update the error field if needed"""
        if self.error:
            return False

        for v in self.validators:
            self.error = v(self.value)
            if self.error:
                return False

        return True

    def extract_value(self, data):
        """
        Extract the data from the request
        :param data: A mult-dict with either the post or get query
        """
        if self.name not in data and not self.allow_missing:
            raise exceptions.FieldNotFound('Field {} is missing from request'.format(self.name))
        
        if self.multiple_inputs:
            self.value = []
            for value in data.getlist(self.name):
                if self.strip_value:
                    value = value.strip()
                if value == '' and self.convert_empty_to_none:
                    value = None

                self.value.append(value)
        else:
            self.value = data.get(self.name)
            if self.value is not None:
                if self.strip_value:
                    self.value = self.value.strip()
                if self.value == '' and self.convert_empty_to_none:
                    self.value = None

        # Convert the value to the correct data type
        self.convert_value()

    @property
    def form_type(self):
        """
        Form type - i.e. vertical, horizontal, inline
        """
        return self.form.form_type if self.form else None

    @property
    def style(self):
        """
        Style - i.e. Bootstrap 3, Bootstrap 4
        """
        return self.form.style if self.form else None

    @property
    def label_column_class(self):
        classes = []
        if self.style == styles.BOOTSTRAP_3:
            classes.append('control-label')
        elif self.style == styles.BOOTSTRAP_4:
            classes.append('col-form-label')

        if self.form.form_type == formtype.HORIZONTAL and self.label_width > 0:
            classes.append('col-{breakpoint}-{width}'.format(
                breakpoint=self.column_breakpoint,
                width=self.label_width
            ))

        return ' '.join(classes)

    @property
    def input_no_label_column_class(self):
        if self.form.form_type == formtype.HORIZONTAL:
            classes = []
            if self.label_width > 0:
                if self.style == styles.BOOTSTRAP_3:
                    classes.append('col-{}-offset-{}'.format(self.column_breakpoint, self.label_width))
                elif self.style == styles.BOOTSTRAP_4:
                    classes.append('offset-{}-{}'.format(self.column_breakpoint, self.label_width))

            classes.append('col-{}-{}'.format(self.column_breakpoint, self.width))

            return ' '.join(classes)
        else:
            return ''

    @property
    def help_text_column_class(self):
        if self.form.form_type == formtype.INLINE:
            return ''
        elif self.form.form_type == formtype.HORIZONTAL:
            classes = []
            if self.label_width > 0:
                if self.style == styles.BOOTSTRAP_3:
                    classes.append('col-{}-offset-{}'.format(self.column_breakpoint, self.label_width))
                elif self.style == styles.BOOTSTRAP_4:
                    classes.append('offset-{}-{}'.format(self.column_breakpoint, self.label_width))

            classes.append('col-{}-{}'.format(self.column_breakpoint, self.help_text_width))

            return ' '.join(classes)
        else:
            return ''

    @property
    def error_column_class(self):
        return 'ef-error {}'.format(self.help_text_column_class)

    @property
    def input_column_class(self):
        if self.form.form_type == formtype.HORIZONTAL:
            return 'col-{breakpoint}-{width}'.format(
                breakpoint=self.column_breakpoint,
                width=self.width
            )
        else:
            return ''

    @property
    def input_column_style(self):
        style = []
        if self.form.form_type == formtype.INLINE:
            style.append('display: inline;')
        if self.max_width:
            style.append('max-width: {};'.format(self.max_width))
        return ' '.join(style)
    
    def get_input_column_attributes(self, extra_classes=None):
        """
        :param extra_classes: String with space separated list of classes or None
        """
        all_classes = []
        css_class = self.input_column_class
        if css_class:
            all_classes.append(css_class)
        if extra_classes:
            all_classes.append(extra_classes)

        style = self.input_column_style
        parts = []

        if all_classes:
            parts.append('class="{}"'.format(' '.join(all_classes)))

        if style:
            parts.append('style="{}"'.format(style))

        return Markup(' '.join(parts))

    @property
    def input_column_attributes(self):
        return self.get_input_column_attributes()

    @property
    def input_column_no_label_attributes(self):
        extra_classes = None
        if self.form_type == formtype.HORIZONTAL and self.label_width > 0:
            if self.style == styles.BOOTSTRAP_3:
                extra_classes = 'col-{}-offset-{}'.format(self.column_breakpoint, self.label_width)
            elif self.style == styles.BOOTSTRAP_4:
                extra_classes = 'offset-{}-{}'.format(self.column_breakpoint, self.label_width)
        return self.get_input_column_attributes(extra_classes=extra_classes)

    @property
    def form_group_classes(self):
        """
        Full list of classes for the class attribute of the form group. Returned as a string
        with spaces separating each class, ready for insertion into the class attribute.

        This will generally look like the following:

        'form-group has-error custom-class'
        """
        classes = ['form-group']
        if self.style == styles.BOOTSTRAP_4 and self.form_type == formtype.HORIZONTAL:
            classes.append('row')
        if self.error and self.style == styles.BOOTSTRAP_3:
            classes.append('has-error')
        if self.form_group_css_class:
            classes.append(self.form_group_css_class)

        return ' '.join(classes)

    @property
    def input_classes(self):
        """
        Full list of classes for the class attribute of the input, returned as a string with
        spaces separating each class.
        """
        classes = [self.base_input_css_class]
        if self.css_class:
            classes.append(self.css_class)

        if self.style == styles.BOOTSTRAP_4 and self.error:
            classes.append('is-invalid')

        return ' '.join(classes)

    @property
    def form_group_style(self):
        """
        Style attribute for form group
        """
        if self.form.form_type == formtype.INLINE:
            return 'vertical-align: top'
        
        return ''

    @property
    def form_group_attributes(self):
        css_classes = self.form_group_classes
        style = self.form_group_style
        parts = []
        if css_classes:
            parts.append('class="{}"'.format(css_classes))
        if style:
            parts.append('style="{}"'.format(style))
        return Markup(' '.join(parts))
        

class FormSection(object):
    def __init__(self, name, fields=[]):
        self.name = name
        self.fields = list(fields)

    def render(self):
        """Render the form to HTML"""
        return Markup(env.get_template('form_section.html').render(section=self))


class Form(object):
    # The name of the hidden input used to detect form submission
    SUBMITTED_HIDDEN_INPUT_NAME = '--form-submitted--'

    def __init__(self, fields=[], action='', method='POST', css_class=None, submit_text='Submit',
                 read_form_data=True, form_name='', label_width=3, form_type=None,
                 id=None, submit_css_class='btn-primary', column_breakpoint='sm',
                 show_asterisks=False, max_width=None, disable_csrf=False, readonly=False,
                 style=styles.BOOTSTRAP_3):
        """
        :param fields: List of Field objects
        :param action: Action field in generated form
        :param method: Method field in generated form.  Must be 'POST' or 'GET'
        :param css_class: CSS class of generated form
        :param submit_text: Text to render in submit button.  If None, no button is generated and has to be manually
                            added to the fields array
        :param read_form_data: If True (by default) automatically parses the form input from the current request
        :param form_name: If you have multiple forms on the same page, each must have a unique form name
        :param label_width: The width (using the grid system) of the labels for this form
        :param form_type: Form type constant (i.e. VERTICAL or HORIZONTAL)
        :param id: The id to insert into the form tag
        :param submit_css_class: The class of the automatically added submit button (if applicable)
        :param column_breakpoint: Bootstrap column breakpoint where horizontal form degrades into
                                  vertical form.  Values: sm, md, lg. Defaults to 'sm'
        :param show_asterisks: Should an asterisk be displayed next to required fields?
        :param max_width: Maximum width, either an integer value representing the number of pixels
                          or a string containing a units i.e. '50%' or '240px'
        :param disable_csrf: Set to True to remove the CSRF field (if applicable)
        :param readonly: If set to True, all fields will be readonly, and it's garunteed that the
                         fields values will not change when the form is submitted.  Allows the
                         form to be rendered, without accepting user input.  If readonly is True,
                         ready and submitted will always return False
        :param style: The "style" of form to render. This determines how the fields are laid out
                      and some of the CSS classes that are used. Bootstrap 3 or Bootstrap 4 are
                      the current supported values.  Use a constant in styles.py
        """
        if method != 'POST' and method != 'GET':
            raise ValueError('Invalid method: %s.  Valid options are GET and POST' % method)
        
        if style not in styles.ALL_STYLES:
            raise ValueError('Invalid style: {}.  Only the following values are '
                             'supported: {}'.format(
                                 ', '.join(styles.ALL_STYLES)
                             ))

        # List of all fields not in a sections
        self.fields = []

        # Keep a dictionary with all fields
        self.field_dict = OrderedDict()

        # Add fields to form
        self.add_fields(fields)

        if form_type is None:
            self.form_type = _default_form_type
        else:
            self.form_type = form_type

        self.method = method
        self.action = action
        if css_class is None:
            if self.form_type == formtype.HORIZONTAL:
                self.css_class = 'form-horizontal'
            elif self.form_type == formtype.INLINE:
                self.css_class = 'form-inline'
            else:
                self.css_class = ''
        else:
            self.css_class = css_class

        # Record if we have processed the form data yet
        self.processed_data = False
        self.form_name = form_name
        self.label_width = label_width
        self.id = id
        self.column_breakpoint = column_breakpoint
        self.show_asterisks = show_asterisks
        
        self.max_width = max_width
        if isinstance(self.max_width, int):
            self.max_width = '{}px'.format(self.max_width)

        self.disable_csrf = disable_csrf
        self.readonly = readonly
        self.style = style

        # Record whether or not we have any validation errors
        self.has_errors = False
        # Optional form 'sections' to separate out fields and to allow sections of the form to be rendered independently
        self._sections = OrderedDict()

        if submit_text:
            self.add_submit(submit_text, submit_css_class)

        if read_form_data:
            self.read_form_data()

    def add_submit(self, submit_text, css_class='btn-primary'):
        from .basicfields import SubmitButton
        self.add_field(SubmitButton('submit', submit_text, label_width=self.label_width,
                                    css_class=css_class))

    def add_field(self, field):
        if field.name in self.field_dict:
            raise exceptions.DuplicateField('A field named "{}" is already present in the form'.format(field.name))

        self.fields.append(field)
        self.field_dict[field.name] = field
        field.form = self

    def add_fields(self, fields):
        # Names of all fields we are adding
        field_names = set()
        
        for field in fields:
            if field.name in self.field_dict or field.name in field_names:
                raise exceptions.DuplicateField('A field named "{}" is already present in the form'.format(field.name))

            field_names.add(field.name)

        for field in fields:
            self.fields.append(field)
            self.field_dict[field.name] = field
            field.form = self

    def add_section(self, name, fields=[]):
        # Names of all fields we are adding
        field_names = set()

        for field in fields:
            if field.name in self.field_dict or field.name in field_names:
                raise exceptions.DuplicateField('A field named "{}" is already present in the form'.format(field.name))
            
            field_names.add(field.name)

        section = FormSection(name, fields)
        for field in section.fields:
            self.field_dict[field.name] = field
            field.form = self

        self._sections[name] = section
        return section

    def get_section(self, name):
        return self._sections[name]

    def has_section(self, name):
        return name in self._sections

    @property
    def sections(self):
        return [self._sections[key] for key in self._sections]

    @property
    def submitted_hidden_input_name(self):
        return '%s%s' % (self.SUBMITTED_HIDDEN_INPUT_NAME, self.form_name)

    def render(self):
        """Render the form and all sections to HTML"""
        return Markup(env.get_template('form.html').render(form=self,
                                                           render_open_tag=True,
                                                           render_close_tag=True,
                                                           render_before=True,
                                                           render_sections=True,
                                                           render_after=True,
                                                           generate_csrf_token=None if self.disable_csrf else _csrf_generation_function))

    def render_before_sections(self):
        """Render the form up to the first section.  This will open the form tag but not close it."""
        return Markup(env.get_template('form.html').render(form=self,
                                                           render_open_tag=True,
                                                           render_close_tag=False,
                                                           render_before=True,
                                                           render_sections=False,
                                                           render_after=False,
                                                           generate_csrf_token=None if self.action else _csrf_generation_function))

    def render_after_sections(self):
        """Render the form up to the first section.  This will close the form tag, but not open it."""
        return Markup(env.get_template('form.html').render(form=self,
                                                           render_open_tag=False,
                                                           render_close_tag=True,
                                                           render_before=False,
                                                           render_sections=False,
                                                           render_after=True,
                                                           generate_csrf_token=None if self.action else _csrf_generation_function))

    def render_sections(self):
        """
        Renders all sections in the form, each inside a fieldset with the legend generated from the section name.
        No form tag is included: just the inputs are rendered.
        """
        return Markup(env.get_template('form.html').render(form=self,
                                                           render_open_tag=False,
                                                           render_close_tag=False,
                                                           render_before=False,
                                                           render_sections=True,
                                                           render_after=False,
                                                           generate_csrf_token=_csrf_generation_function))

    def render_start(self):
        """
        This will open the form, without rendering any fields at all
        """
        return Markup(env.get_template('form.html').render(form=self,
                                                           render_open_tag=True,
                                                           render_close_tag=False,
                                                           render_before=False,
                                                           render_sections=False,
                                                           render_after=False,
                                                           generate_csrf_token=_csrf_generation_function))
        
    def render_end(self):
        """
        This will close the form, without rendering any fields at all
        """
        return Markup(env.get_template('form.html').render(form=self,
                                                           render_open_tag=False,
                                                           render_close_tag=True,
                                                           render_before=False,
                                                           render_sections=False,
                                                           render_after=False,
                                                           generate_csrf_token=_csrf_generation_function))
    
    def render_section(self, name):
        return self.get_section(name).render()

    def render_field(self, name):
        return Markup(self.get_field(name).render())

    def is_section_empty(self, name):
        return not self.get_section(name).fields

    @property
    def all_fields(self):
        # Create list of all fields from all sections
        if not self.sections:
            return self.fields
        else:
            all_fields = self.fields[:]
            for section in self.sections:
                for field in section.fields:
                    all_fields.append(field)
            return all_fields

    def read_form_data(self):
        """Attempt to read the form data from the request"""
        if self.processed_data:
            raise exceptions.AlreadyProcessed('The data has already been processed for this form')
        
        if self.readonly:
            return

        if request.method == self.method:
            if self.method == 'POST':
                data = request.form
            else:
                data = request.args

            if self.submitted_hidden_input_name in data:
                # The form has been submitted
                self.processed_data = True

                for field in self.all_fields:
                    # We need to skip readonly fields
                    if field.readonly:
                        pass
                    else:
                        field.extract_value(data)

                        # Validate the field
                        if not field.validate():
                            log.debug('Validation error in field \'%s\': %s' % (field.name, field.error))
                            self.has_errors = True

    def __getitem__(self, item):
        if not self.processed_data:
            raise exceptions.FormNotProcessed('The form data has not been processed yet')

        if item not in self.field_dict:
            raise exceptions.FieldNotFound('The field \'%s\' is not present in the processed form data' % item)

        return self.field_dict[item].value
    
    def get_if_present(self, name, default=None):
        """
        Returns the value for a field, but if the field doesn't exist will return default instead
        """
        if not self.processed_data:
            raise exceptions.FormNotProcessed('The form data has not been processed yet')

        if name in self.field_dict:
            return self[name]

        return default

    def get_error(self, field_name):
        if not self.processed_data:
            raise exceptions.FormNotProcessed('The form data has not been processed yet')
        
        field = self.get_field(field_name)
        if not field:
            raise exceptions.FieldNotFound('The field \'%s\' is not present in the form' % field_name)
            
        return field.error

    def set_error(self, field_name, error):
        field = self.field_dict.get(field_name)

        if not field:
            raise exceptions.FieldNotFound('Field not found: \'%s\' when trying to set error' % field_name)

        field.error = error
        self.has_errors = True

    def set_value(self, field_name, value):
        field = self.field_dict.get(field_name)

        if not field:
            raise exceptions.FieldNotFound('Field not found: \'%s\' when trying to set value' % field_name)
        
        field.value = value

    def disable_validation(self, field_name):
        """Disable the validation rules for a field"""
        field = self.field_dict.get(field_name)

        if not field:
            raise exceptions.FieldNotFound('Field not found: \'%s\' when trying to disable validation' % field_name)
        
        field.validators = []

    def has_error(self, field_name):
        field = self.field_dict.get(field_name)

        if not field:
            raise exceptions.FieldNotFound('Field not found: \'%s\' when trying to check for errors' % field_name)
        
        return field.error is not None

    @property
    def ready(self):
        """Has the data been processed and validated?"""
        return not self.readonly and self.processed_data and not self.has_errors

    @property
    def submitted(self):
        return not self.readonly and self.processed_data

    def clear(self):
        for field in self.all_fields:
            if not field.noclear:
                self.set_value(field.name, None)
                self.set_error(field.name, None)

    @property
    def multipart(self):
        for field in self.all_fields:
            if field.requires_multipart:
                return True
        return False

    def get_field(self, name):
        return self.field_dict.get(name)

    def create_single_button_clone(self, submit_text='Submit', submit_css_class='btn-primary',
                                   read_form_data=True, form_type=None):
        """
        This will create a copy of this form, with all of inputs replaced with hidden inputs,
        and with a single submit button.  This allows you to easily create a "button" that
        will submit a post request which is identical to the current state of the form.
        You could then, if required, change some of the values in the hidden inputs.

        Note: Submit buttons are not included, and the submit button value will change
        """
        from .basicfields import BooleanCheckbox, HiddenField, SubmitButton

        fields = []
        for field in self.all_fields:
            # If it's valid for the field to be missing, and the value of the field is empty,
            # then don't add it, otherwise create a hidden input
            if field.allow_missing:
                if field.value is None or field.value == '':
                    continue
                elif isinstance(field, BooleanCheckbox) and not field.value:
                    continue
                # TODO: is this right?
                elif isinstance(field, SubmitButton):
                    continue

            # If we get here, we need to add this field to the list
            fields.append(HiddenField(field.name, field.value))
        
        form = Form(fields, action=self.action, method=self.method, submit_css_class=submit_css_class,
                    submit_text=submit_text, read_form_data=read_form_data,
                    disable_csrf=self.disable_csrf, readonly=False,
                    form_type=form_type if form_type else self.form_type)

        return form
    
    def set_type(self, form_type, css_class=None):
        """
        Maybe you have a site where you're not allowed to change the python code,
        and for some reason you need to change the form_type in a template, not
        because you want to (because it seems like a bit of a hack) but maybe you
        don't really have a choice.  Then this function was made for you.

        Sorry

        :param form_type: The new form_type
        :param css_class: If None (default) derrive this from the form_type.
                          If a value is passed in this will be the new css_class
                          for the form
        """
        self.form_type = form_type
        
        if css_class is None:
            self.css_class = self.get_default_css_class(form_type)
        else:
            self.css_class = css_class
        
        return ''

