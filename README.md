# Easy Forms

Form processing library using Flask and Jinja2.

This library makes it very simple to create forms with field by field validation, and render them
into Bootstrap 3 style forms.

If you want to use this with Bootstrap 4 contact me - I will gladly add Bootstrap 4 support!

Included in this repository is a sample application in the `testapp` folder.  Have a look through
the code to see some examples of the library being used.

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
To read from the form access it like a list, using the name of each field to index:

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
Then we can access all of the fields from all sections as if it were a single list:

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

