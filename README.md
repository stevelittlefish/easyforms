# Easy Forms

Form processing library using Flask and Jinja2.

This library makes it very simple to create forms with field by field validation, and render them
into Bootstrap 3 style forms.

If you want to use this with Bootstrap 4 contact me - I will gladly add Bootstrap 4 support!

Included in this repository is a sample application in the `testapp` folder.  Have a look through
the code to see some examples of the library being used.

You can view examples of the forms with this library, including most of the included fields at the
following url: [http://littlefish.solutions/easyforms/](http://littlefish.solutions/easyforms/)

## Basic Usage

To create a form and pass into the template:

```python
import easyforms

@app.route('/some-url', method=['GET', 'POST'])
def some_view_function():
    form = easyforms.Form([
        easyforms.TextInput('some-text', required=True),
        easyforms.IntegerInput('a-number', min_value=1, required=True)
     ])
   
     return render_template('some-template.html', form=form)
```

Then to render it, inside the template:

```html
<html>
    <body>
        <h1>My Page</h1>
        {{ form.render() }}
    </body>
</html>
```

If the form has been submitted, and there are no validation error, form.ready will be `True`
To read from the form access it like a dictionary, using the name of each field to index:

```python
@app.route('/some-url', method=['GET', 'POST'])
def some_view_function():
    form = easyforms.Form([
        easyforms.TextInput('some-text', required=True),
        easyforms.IntegerInput('a-number', min_value=1, required=True)
    ])

    if form.ready:
        text = form['some-text']
        number = form['a-number']
        print('Submitted values: {} {}'.format(text, number))

    return render_template('some-template.html', form=form)
```

## Multi Section Forms

You can create forms in multiple sections like this:

```python
@app.route('/some-url', method=['GET', 'POST'])
def some_view_function():
    # read_form_data=False will ensure that we don't read form data until we have
    # finished adding all of the sections
    form = easyforms.Form([], read_form_data=False)

    form.add_section('Section 1', [
        easyforms.TextField('text-field', required=True,
                            help_text='Any text will be accepted'),
        easyforms.PasswordField('password-field', required=True)
    ])
    
    form.add_section('Section 2', [
        easyforms.EmailField('email-address', required=True),
        easyforms.BooleanCheckbox('confirm', help_text='I confirm I want to do this!')
    ])

    return render_template('some-template.html', form=form)
```

If we simply call `form.render()` in the template, the entire form will be rendered with
headings separating each section, but this isn't usually what you want to do. You can
also render each of the form sections yourself to create customer layouts:

```html
<html>
    <body>
        <h1>Two Column Form</h1>
        {{ form.render_before_sections() }}
            <div class="row">
                <div class="col-md-6">
                    {{ form.render_section('Section 1') }}
                </div>
                <div class="col-md-6">
                    {{ form.render_section('Section 2') }}
                </div>
            </div>
            <hr>
        {{ form.render_after_sections() }}
    </body>
</html>
```

The first call to `form.render_before_sections()` is equivalent to opening a form tag. Then
we can render each section by name using `form.render_section('Section Name')`.  Finally
we call `form.render_after_sections()` which will render the submit button and close the form.

When we're processing our form data, we have to manually tell the form to read the form data
once we've finished adding our sections (remember that parameter read_form_data=False?).
Then we can access all of the fields from all sections as if it were a single dictionary:

```python
@app.route('/some-url', method=['GET', 'POST'])
def some_view_function():
    # read_form_data=False will ensure that we don't read form data until we have
    # finished adding all of the sections
    form = easyforms.Form([], read_form_data=False)

    form.add_section('Section 1', [
        easyforms.TextField('text-field', required=True,
                            help_text='Any text will be accepted'),
        easyforms.PasswordField('password-field', required=True)
    ])
    
    form.add_section('Section 2', [
        easyforms.EmailField('email-address', required=True),
        easyforms.BooleanCheckbox('confirm', help_text='I confirm I want to do this!')
    ])
    
    form.read_form_data()

    if form.submitted:
        text = form['text-field']
        confirmed = form['confirm']
        if confirmed:
            print('Confirmed with this text: {}'.format(text))

    return render_template('some-template.html', form=form)
```

## Custom Validation

There are 2 approaches to adding customer validation. The first method is to manually do the
validation in the view function:

```python
@main.route('/custom-validation-1', methods=['GET', 'POST'])
def custom_validation_1():
    form = easyforms.Form([
        easyforms.IntegerField('an-integer', help_text='Any whole number!', required=True),
        easyforms.TextField('two-or-three', required=True)
    ])
    
    if form.submitted:
        # The form was submitted, but not necessarily validated
        # If there is a value in the two-or-three field, and it doen't already have an error set
        if form['two-or-three'] and not form.has_error('two-or-three'):
            # Check if the string contains "two" or "three" and set an error if it doesn't
            two_or_three = form['two-or-three']
            if two_or_three != 'two' and two_or_three != 'three':
                form.set_error('two-or-three', 'Please enter "two" or "three" (lower case)')
    
    # If we set an error, form.ready will no longer be True
    if form.ready:
        print('The form was submitted!')

    return render_template('custom_validation_1.html', form=form)

```

This works, and is good for one-offs, but is a bit tedious and ugly.  Another method we can use is
to define validation functions and pass them into the form fields:

```python
@main.route('/custom-validation-2', methods=['GET', 'POST'])
def custom_validation_2():
    def is_two_or_three(val):
        if val and val != 'two' and val != 'three':
            return 'Please enter "two" or "three" (lower case)'

    form = easyforms.Form([
        easyforms.IntegerField('an-integer', help_text='Any whole number!', required=True),
        easyforms.TextField('two-or-three', required=True, validators=[is_two_or_three])
    ])
    
    if form.ready:
        print('The form was submitted!')

    return render_template('custom_validation_2.html', form=form)
```

Here we define a function `is_two_or_three` that takes a single argument, and if that argument is
not valid, returns an error message. It's usually a good idea not to return an error message if
the value is not set, otherwise it's impossible to use the validator on an optional field.

This is a little bit neater and has the advantage of making the validator functions reusable.

## Custom Fields

Sooner or later you are going to want to add some custom fields, either to add fields that
look different to the standard fields, or to add fields which handle different types of data.
This involves a little bit of setup.  Look at the `testapp.customfields` package for an example.

### Custom field to handle different data

This first example is a very simple example that doesn't affect the rendering of the field it's
based on, but changes the behaviour.  In this example, any text that's submitted into the field
is converted to upper case.

Define the following class for the field:

```python
from easyforms import basicfields


class UpperCaseTextField(basicfields.TextField):
    def __init__(self, name, value=None, **kwargs):
        super().__init__(name, value.upper() if value is not None else None)
    
    def convert_value(self):
        # self.value is the raw string
        if self.value is not None:
            # The string is present - convert to upper case
            self.value = self.value.upper()
```

When a field is submitted, the raw string is taken from the form data and placed in the `value`
attribute.  Then, for each field in the form, `convert_value` is called, which should convert
the value to whatever data-type it's supposed to be and store it back in `value`.

In this example, the submitted value is simply converted to upper case, but you could convert it
to any data type you wanted, or even query a database and place a model in value, or return any
kind of complex object.

It should be noted that it's normally best to leave `None` values as `None` so that optional fields
can be created.

### Custom field with customer renderer - without using jinja2

This next example shows how to create a field that looks different to the standard fields.  You'd
probably never want to actually create a field in quite this manner, but it does demonstrate how
to override the `render` method of a field, and that you don't have to use Jinja2:

```python
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
```

Here we simply override the `render` method and output some html which we construct manually.

### Custom Field with Jinja2 Renderer

This is a bit more in depth and could probably be acheived in any number of ways.

Very briefly, this is what you'll probably want to do:

#### 1. Create a package and a jinja2 environment for your fields

Create a package, and inside that package create a python file called env.py with the jinja2
environment like this:

```python
import logging
import os

from jinja2 import Environment, FileSystemLoader
import jinja2

from easyforms import formtype

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
```

You can base this off of the env.py in the easyforms package.

#### 2. Create a templates directory and optionally copy in the easyform macros

Inside you package create a folder called `templates`. If you want to use the easyform macros
(hint: you probably do) copy in 'easyforms/templates/macros.html` so that you can import it
in your templates.

Now create your template for your new field.  I created `text_field.html` to create a field
with a custom label with the text "[ CUSTOM FIELD ]" in green as part of the label text:

```html
{% import 'macros.html' as macros %}

<div {{ field.form_group_attributes }}>
	{% if field.label_width > 0 %}
		<label for="{{ field.id }}" class="{{ field.label_column_class }}">
			<strong class="green">[ CUSTOM FIELD ]</strong>
			{{ field.label_html }}
		</label>
	{% endif %}

	<div {{ field.input_column_attributes }}>
		<input type="{{ field.type }}"
	       class="form-control {{ field.css_class|sn }}"
	       name="{{ field.name }}"
	       id="{{ field.id }}" value="{{ field.value|sn }}" placeholder="{{ field.placeholder|sn }}"
	       {% if field.readonly %}readonly{% endif %}>

	</div>

	{{ macros.standard_error(field) }}
	{{ macros.standard_help_text(field) }}
</div>

```


#### 3. Create a module in you package with your customer fields

Here we're going to create our `CustomTextField` class:

```python
from easyforms import basicfields

from .env import env

class CustomTextField(basicfields.TextField):
    def render(self):
        return env.get_template('text_field.html').render(field=self)
```

Now we can use this in our form:

```python

import easyforms
from customfields.fields import CustomTextField

def some_view():
    form = easyforms.Form([
        easyforms.TextField('normal-text-field'),
        CustomTextField('custom-field')
    ])
```

### A Custom Template and Custom Behaviour

This final example will implement a field where the user can type in a comma separated list of
strings, and it will be converted into a list.  This also means that the developer can pass in
a list of strings into the `value` parameter of the form field.

First the template in `templates/comma_separated_list.html`:

```html
{% import 'macros.html' as macros %}

<div {{ field.form_group_attributes }}>
	{{ macros.standard_label(field) }}

	<div {{ field.input_column_attributes }}>
		<input type="{{ field.type }}"
	       class="form-control {{ field.css_class|sn }}"
	       name="{{ field.name }}"
	       id="{{ field.id }}" value="{{ ', '.join(field.value) if field.value else '' }}" placeholder="{{ field.placeholder|sn }}"
	       {% if field.readonly %}readonly{% endif %}>

	</div>

	{{ macros.standard_error(field) }}
	{{ macros.standard_help_text(field) }}
</div>
```

Look at what we did with the `value` attribute.

Now the python class:

```python
class CommaSeparatedListField(basicfields.TextField):
    def render(self):
        return env.get_template('comma_separated_list.html').render(field=self)

    def convert_value(self):
        # self.value is the raw string
        if self.value is not None:
            # The string is present - convert it into a list
            parts = self.value.split(',')
            self.value = [x.strip() for x in parts if x.strip()]
```

Now we can use it like this:

```python
import easyforms
from customfields.fields import CommaSeparatedListField

def some_view():
    form = easyforms.Form([
        CommaSeparatedListField('list', value=['hello', 'goodbye', 'testing')
    ])

    if form.ready:
        list = form['list']
        # list is a list of strings instead of the raw string
        print(list)
        # prints something like: ['hello', 'goodbye', 'testing']
```

