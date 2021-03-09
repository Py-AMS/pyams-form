=====
Forms
=====

The purpose of this package is to make development of forms as simple
as possible, while still providing all the hooks to do customization
at any level as required by our real-world use cases. Thus, once the
system is set up with all its default registrations, it should be
trivial to develop a new form.

The strategy of this document is to provide the most common, and thus
simplest, case first and then demonstrate the available customization
options. In order to not overwhelm you with our set of well-chosen defaults,
all the default component registrations have been made prior to doing those
examples:

  >>> from pyramid.testing import setUp, tearDown
  >>> config = setUp(hook_zca=True)

  >>> from cornice import includeme as include_cornice
  >>> include_cornice(config)
  >>> from pyams_utils import includeme as include_utils
  >>> include_utils(config)
  >>> from pyams_site import includeme as include_site
  >>> include_site(config)
  >>> from pyams_i18n import includeme as include_i18n
  >>> include_i18n(config)
  >>> from pyams_form import includeme as include_form
  >>> include_form(config)

  >>> from pyams_utils.testing import format_html, render_xpath
  >>> from pyams_form import util, testing
  >>> testing.setup_form_defaults(config.registry)

Before we can start writing forms, we must have the content to work with:

  >>> import zope.interface
  >>> import zope.schema
  >>> class IPerson(zope.interface.Interface):
  ...
  ...     id = zope.schema.TextLine(
  ...         title='ID',
  ...         readonly=True,
  ...         required=True)
  ...
  ...     name = zope.schema.TextLine(
  ...         title='Name',
  ...         required=True)
  ...
  ...     gender = zope.schema.Choice(
  ...         title='Gender',
  ...         values=('male', 'female'),
  ...         required=False)
  ...
  ...     age = zope.schema.Int(
  ...         title='Age',
  ...         description="The person's age.",
  ...         min=0,
  ...         default=20,
  ...         required=False)
  ...
  ...     @zope.interface.invariant
  ...     def ensureIdAndNameNotEqual(person):
  ...         if person.id == person.name:
  ...             raise zope.interface.Invalid(
  ...                 "The id and name cannot be the same.")

  >>> from zope.schema.fieldproperty import FieldProperty
  >>> @zope.interface.implementer(IPerson)
  ... class Person:
  ...     id = FieldProperty(IPerson['id'])
  ...     name = FieldProperty(IPerson['name'])
  ...     gender = FieldProperty(IPerson['gender'])
  ...     age = FieldProperty(IPerson['age'])
  ...
  ...     def __init__(self, id, name, gender=None, age=None):
  ...         self.id = id
  ...         self.name = name
  ...         if gender:
  ...             self.gender = gender
  ...         if age:
  ...             self.age = age
  ...
  ...     def __repr__(self):
  ...         return '<%s %r>' % (self.__class__.__name__, self.name)

Okay, that should suffice for now.

What's next? Well, first things first. Let's create an add form for the
person. Since practice showed that the ``IAdding`` interface is overkill for
most projects, the default add form of ``pyams_form`` requires you to define the
creation and adding mechanism.

**Note**:

  If it is not done, ``NotImplementedError[s]`` are raised:

    >>> from pyams_form.testing import TestRequest
    >>> from pyams_form import form, field

    >>> abstract = form.AddForm(None, TestRequest())

    >>> abstract.create({})
    Traceback (most recent call last):
    ...
    NotImplementedError

    >>> abstract.add(1)
    Traceback (most recent call last):
    ...
    NotImplementedError

    >>> abstract.next_url() == abstract.action
    True


Thus let's now create a working add form:

  >>> class PersonAddForm(form.AddForm):
  ...
  ...     fields = field.Fields(IPerson)
  ...
  ...     def create(self, data):
  ...         return Person(**data)
  ...
  ...     def add(self, object):
  ...         self.context[object.id] = object
  ...
  ...     def nextURL(self):
  ...         return 'index.html'

This is as simple as it gets. We explicitly define the pieces that
are custom to every situation and let the default setup of the
framework do the rest. This is intentionally similar to
``zope.formlib``, because we really like the simplicity of
``zope.formlib``'s way of dealing with the common use cases.

Let's try to add a new person object to the root folder (which
was created during test setup).  For this add form, of course, the
context is now the root folder:

  >>> root = {}
  >>> request = TestRequest()
  >>> addForm = PersonAddForm(root, request)

Since forms are not necessarily pages -- in fact often they are not --
they must not have a ``__call__`` method that does all the processing
and rendering at once. Instead, we use the update/render
pattern. Thus, we first call the ``update()`` method.

  >>> addForm.update()

Actually a lot of things happen during this stage. Let us step through it one
by one pointing out the effects.


Find a widget manager and update it
-----------------------------------

The default widget manager knows to look for the ``fields`` attribute in the
form, since it implements ``IFieldsForm``:

  >>> from pyams_form import interfaces
  >>> interfaces.form.IFieldsForm.providedBy(addForm)
  True

The widget manager is then stored in the ``widgets`` attribute as promised by
the ``IForm`` interface:

  >>> addForm.widgets
  FieldWidgets([...])

The widget manager will have four widgets, one for each field:

  >>> list(addForm.widgets.keys())
  ['id', 'name', 'gender', 'age']

When the widget manager updates itself, several sub-tasks are processed. The
manager goes through each field, trying to create a fully representative
widget for the field.

Field Availability
~~~~~~~~~~~~~~~~~~

Just because a field is requested in the field manager, does not mean that a
widget has to be created for the field. There are cases when a field
declaration might be ignored. The following reasons come to mind:

* No widget is created if the data are not accessible in the content.
* A custom widget manager has been registered to specifically ignore a field.

In our simple example, all fields will be converted to widgets.

Widget Creation
~~~~~~~~~~~~~~~

During the widget creation process, several pieces of information are
transferred from the field to the widget:

  >>> age = addForm.widgets['age']

  # field.title -> age.label

  >>> age.label
  'Age'

  # field.required -> age.required

  >>> age.required
  False

All these values can be overridden at later stages of the updating
process.

Widget Value
~~~~~~~~~~~~

The next step is to determine the value that should be displayed by the
widget. This value could come from three places (looked up in this order):

1. The field's default value.
2. The content object that the form is representing.
3. The request in case a form has not been submitted or an error occurred.

Since we are currently building an add form and not an edit form,
there is no content object to represent, so the second step is not
applicable. The third step is also not applicable as we do not have
anything in the request. Therefore, the value should be the field's
default value, or be empty. In this case the field provides a default
value:

  >>> age.value
  '20'

While the default of the age field is actually the integer ``20``, the
widget has converted the value to the output-ready string ``'20'``
using a data converter.

Widget Mode
~~~~~~~~~~~

Now the widget manager looks at the field to determine the widget mode -- in
other words whether the widget is a display or edit widget. In this case all
fields are input fields:

  >>> age.mode
  'input'

Deciding which mode to use, however, might not be a trivial operation. It
might depend on several factors (items listed later override earlier ones):

* The global ``mode`` flag of the widget manager
* The permission to the content's data value
* The ``readonly`` flag in the schema field
* The ``mode`` flag in the field


Widget Attribute Values
~~~~~~~~~~~~~~~~~~~~~~~

As mentioned before, several widget attributes are optionally overridden when
the widget updates itself:

* label
* required
* mode

Since we have no customization components registered, all of those fields will
remain as set before.


Find an action manager, update and execute it
---------------------------------------------

After all widgets have been instantiated and the ``update()`` method has been
called successfully, the actions are set up. By default, the form machinery
uses the button declaration on the form to create its actions. For the add
form, an add button is defined by default, so that we did not need to create
our own. Thus, there should be one action:

  >>> len(addForm.actions)
  1

The add button is an action and a widget at the same time:

  >>> addAction = addForm.actions['add']
  >>> addAction.title
  'Add'
  >>> addAction.value
  'Add'

After everything is set up, all pressed buttons are executed. Once a submitted
action is detected, a special action handler adapter is used to determine the
actions to take. Since the add button has not been pressed yet, no action
occurred.


Rendering the form
------------------

Once the update is complete we can render the form using one of two methods reder or json.
If we want to generate json data to be consumed by the client all we need to do is call json():

 >>> import json
 >>> from pprint import pprint
 >>> pprint(json.loads(addForm.json()))
 {'errors': [],
  'fields': [{'error': '',
              'id': 'form-widgets-id',
              'label': 'ID',
              'mode': 'input',
              'name': 'form.widgets.id',
              'required': True,
              'type': 'text',
              'value': ''},
             {'error': '',
              'id': 'form-widgets-name',
              'label': 'Name',
              'mode': 'input',
              'name': 'form.widgets.name',
              'required': True,
              'type': 'text',
              'value': ''},
             {'error': '',
              'id': 'form-widgets-gender',
              'label': 'Gender',
              'mode': 'input',
              'name': 'form.widgets.gender',
              'options': [{'content': 'No value',
                           'id': 'form-widgets-gender-novalue',
                           'selected': True,
                           'value': '--NOVALUE--'},
                          {'content': 'male',
                           'id': 'form-widgets-gender-0',
                           'selected': False,
                           'value': 'male'},
                          {'content': 'female',
                           'id': 'form-widgets-gender-1',
                           'selected': False,
                           'value': 'female'}],
              'required': False,
              'type': 'select',
              'value': []},
             {'error': '',
              'id': 'form-widgets-age',
              'label': 'Age',
              'mode': 'input',
              'name': 'form.widgets.age',
              'required': False,
              'type': 'text',
              'value': '20'}],
  'legend': '',
  'mode': 'input',
  'prefix': 'form.',
  'status': '',
  'title': ''}


The other way we can render the form is using the render() method.

The render method requires us to specify a template, we have to do this now.
We have prepared a small and very simple template as part of this example:

  >>> import os
  >>> from pyams_template.interfaces import IContentTemplate
  >>> from pyams_template.template import TemplateFactory
  >>> from pyams_layer.interfaces import IFormLayer
  >>> from pyams_form import tests
  >>> def addTemplate(form, template='simple-edit.pt'):
  ...     factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                               'templates', template), 'text/html')
  ...     config.registry.registerAdapter(factory, (None, IFormLayer, form), IContentTemplate)
  >>> addTemplate(PersonAddForm)

Let's now render the page:

  >>> print(format_html(addForm.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-id">ID</label>
      <input type="text"
       id="form-widgets-id"
       name="form.widgets.id"
       class="text-widget required textline-field"
       value="" />
    </div>
    <div class="row">
      <label for="form-widgets-name">Name</label>
      <input type="text"
       id="form-widgets-name"
       name="form.widgets.name"
       class="text-widget required textline-field"
       value="" />
    </div>
    <div class="row">
      <label for="form-widgets-gender">Gender</label>
      <select id="form-widgets-gender"
        name="form.widgets.gender"
        class="select-widget choice-field"
        size="1">
    <option id="form-widgets-gender-novalue"
            value="--NOVALUE--"
            selected="selected">No value</option>
    <option id="form-widgets-gender-0"
            value="male">male</option>
    <option id="form-widgets-gender-1"
            value="female">female</option>
  </select>
  <input name="form.widgets.gender-empty-marker" type="hidden" value="1" />
    </div>
    <div class="row">
      <label for="form-widgets-age">Age</label>
      <input type="text"
       id="form-widgets-age"
       name="form.widgets.age"
       class="text-widget int-field"
       title="The person's age."
       value="20" />
    </div>
    <div class="action">
      <input type="submit"
       id="form-buttons-add"
       name="form.buttons.add"
       class="submit-widget button-field"
       value="Add" />
    </div>
  </form>

The update()/render() cycle is what happens when the form is called, i.e.
when it is published:

  >>> print(format_html(addForm()))
  Traceback (most recent call last):
  ...
  zope.interface.interfaces.ComponentLookupError: (...), <InterfaceClass ...ILayoutTemplate>, '')

An exception is raised because form execution is based on a *layout*, so we have to provide a
custom layout template:

  >>> from pyams_template.interfaces import ILayoutTemplate
  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-layout.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, PersonAddForm), ILayoutTemplate)

As calling a form returns a Response object, we have to get only it's body and decode it to get
HTML content:

  >>> print(format_html(addForm().body.decode()))
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml">
  <body>
  <form action=".">
    <div class="row">
      <label for="form-widgets-id">ID</label>
      <input type="text"
         id="form-widgets-id"
         name="form.widgets.id"
         class="text-widget required textline-field"
         value="" />
    </div>
    <div class="row">
      <label for="form-widgets-name">Name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="" />
    </div>
    <div class="row">
      <label for="form-widgets-gender">Gender</label>
      <select id="form-widgets-gender"
          name="form.widgets.gender"
          class="select-widget choice-field"
          size="1">
      <option id="form-widgets-gender-novalue"
              value="--NOVALUE--"
              selected="selected">No value</option>
      <option id="form-widgets-gender-0"
              value="male">male</option>
      <option id="form-widgets-gender-1"
              value="female">female</option>
  </select>
  <input name="form.widgets.gender-empty-marker" type="hidden" value="1" />
    </div>
    <div class="row">
      <label for="form-widgets-age">Age</label>
      <input type="text"
         id="form-widgets-age"
         name="form.widgets.age"
         class="text-widget int-field"
         title="The person's age."
         value="20" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-add"
         name="form.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </form>
  </body>
  </html>

Note that we don't actually call render if the response has been set to a 3xx
type status code (e.g. a redirect or not modified response), since the browser
would not render it anyway:

  >>> request.response.status = 304
  >>> print(addForm().body.decode())

Let's go back to a normal status to continue the test.

  >>> request.response.status = 200


Registering a custom event handler for the DataExtractedEvent
--------------------------------------------------------------

  >>> data_extracted_eventlog = []
  >>> def data_extracted_logger(event):
  ...     data_extracted_eventlog.append(event)
  >>> _ = config.add_subscriber(data_extracted_logger, interfaces.form.IDataExtractedEvent)


Submitting an add form successfully
-----------------------------------

Initially the root folder of the application is empty:

  >>> sorted(root)
  []

Let's now fill the request with all the right values so that upon submitting
the form with the "Add" button, the person should be added to the root folder:

  >>> request = TestRequest(params={
  ...     'form.widgets.id': 'srichter',
  ...     'form.widgets.name': 'Stephan Richter',
  ...     'form.widgets.gender': ['male'],
  ...     'form.widgets.age': '20',
  ...     'form.buttons.add': 'Add'}
  ...     )

  >>> addForm = PersonAddForm(root, request)
  >>> addForm.update()

  >>> sorted(root)
  ['srichter']
  >>> stephan = root['srichter']
  >>> stephan.id
  'srichter'
  >>> stephan.name
  'Stephan Richter'
  >>> stephan.gender
  'male'
  >>> stephan.age
  20


Check, if DataExtractedEvent was thrown
-----------------------------------------

  >>> event = data_extracted_eventlog[0]
  >>> 'name' in event.data
  True

  >>> event.errors
  ()

  >>> event.form
  <...PersonAddForm object at ...>


Submitting an add form with invalid data
----------------------------------------

Next we try to submit the add form with the required name missing. Thus, the
add form should not complete with the addition, but return with the add form
pointing out the error.

  >>> request = TestRequest(params={
  ...     'form.widgets.id': 'srichter',
  ...     'form.widgets.gender': ['male'],
  ...     'form.widgets.age': '23',
  ...     'form.buttons.add': 'Add'}
  ...     )

  >>> addForm = PersonAddForm(root, request)
  >>> addForm.update()

The widget manager and the widget causing the error should have an error
message:

  >>> [(error.widget.__name__, error) for error in addForm.widgets.errors]
  [('name', <ErrorViewSnippet for RequiredMissing>)]

  >>> addForm.widgets['name'].error
  <ErrorViewSnippet for RequiredMissing>


Check, if event was thrown:

  >>> event = data_extracted_eventlog[-1]
  >>> 'id' in event.data
  True

  >>> event.errors
  (<ErrorViewSnippet for RequiredMissing>,)

  >>> event.form
  <...PersonAddForm object at ...


Let's now render the form:

  >>> print(format_html(addForm.render()))
  <i>There were some errors.</i>
  <ul>
    <li>
        Name
      <div class="error">Required input is missing.</div>
    </li>
  </ul>
  <form action=".">
    <div class="row">
      <label for="form-widgets-id">ID</label>
      <input type="text"
         id="form-widgets-id"
         name="form.widgets.id"
         class="text-widget required textline-field"
         value="srichter" />
    </div>
    <div class="row">
      <b><div class="error">Required input is missing.</div></b>
      <label for="form-widgets-name">Name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="" />
    </div>
    <div class="row">
      <label for="form-widgets-gender">Gender</label>
      <select id="form-widgets-gender"
          name="form.widgets.gender"
          class="select-widget choice-field"
          size="1">
      <option id="form-widgets-gender-novalue"
              value="--NOVALUE--">No value</option>
      <option id="form-widgets-gender-0"
              value="male"
              selected="selected">male</option>
      <option id="form-widgets-gender-1"
              value="female">female</option>
  </select>
  <input name="form.widgets.gender-empty-marker" type="hidden" value="1" />
    </div>
    <div class="row">
      <label for="form-widgets-age">Age</label>
      <input type="text"
         id="form-widgets-age"
         name="form.widgets.age"
         class="text-widget int-field"
         title="The person's age."
         value="23" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-add"
         name="form.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </form>

Notice the errors are present in the json output of the form as well
  >>> import json
  >>> from pprint import pprint
  >>> pprint(json.loads(addForm.json()))
  {'errors': [],
   'fields': [{'error': '',
                'id': 'form-widgets-id',
                'label': 'ID',
                'mode': 'input',
                'name': 'form.widgets.id',
                'required': True,
                'type': 'text',
                'value': 'srichter'},
               {'error': 'Required input is missing.',
                'id': 'form-widgets-name',
                'label': 'Name',
                'mode': 'input',
                'name': 'form.widgets.name',
                'required': True,
                'type': 'text',
                'value': ''},
               {'error': '',
                'id': 'form-widgets-gender',
                'label': 'Gender',
                'mode': 'input',
                'name': 'form.widgets.gender',
                'options': [{'content': 'No value',
                              'id': 'form-widgets-gender-novalue',
                              'selected': False,
                              'value': '--NOVALUE--'},
                             {'content': 'male',
                              'id': 'form-widgets-gender-0',
                              'selected': True,
                              'value': 'male'},
                             {'content': 'female',
                              'id': 'form-widgets-gender-1',
                              'selected': False,
                              'value': 'female'}],
                'required': False,
                'type': 'select',
                'value': ['male']},
               {'error': '',
                'id': 'form-widgets-age',
                'label': 'Age',
                'mode': 'input',
                'name': 'form.widgets.age',
                'required': False,
                'type': 'text',
                'value': '23'}],
   'legend': '',
   'mode': 'input',
   'prefix': 'form.',
   'status': 'There were some errors.',
   'title': ''}


Note that the values of the field are now extracted from the request.

Another way to receive an error is by not fulfilling the invariants of the
schema. In our case, the id and name cannot be the same. So let's provoke the
error now:

  >>> request = TestRequest(params={
  ...     'form.widgets.id': 'Stephan',
  ...     'form.widgets.name': 'Stephan',
  ...     'form.widgets.gender': ['male'],
  ...     'form.widgets.age': '23',
  ...     'form.buttons.add': 'Add'}
  ...     )

  >>> addForm = PersonAddForm(root, request)
  >>> addForm.update()

and see how the form looks like:

  >>> print(format_html(addForm.render()))
  <i>There were some errors.</i>
  <ul>
    <li>
      <div class="error">The id and name cannot be the same.</div>
    </li>
  </ul>
  ...

and through as json:
  >>> import json
  >>> from pprint import pprint
  >>> pprint(json.loads(addForm.json()))
   {'errors': ['The id and name cannot be the same.'],
    'fields': [{'error': '',
                'id': 'form-widgets-id',
                'label': 'ID',
                'mode': 'input',
                'name': 'form.widgets.id',
                'required': True,
                'type': 'text',
                'value': 'Stephan'},
               {'error': '',
                'id': 'form-widgets-name',
                'label': 'Name',
                'mode': 'input',
                'name': 'form.widgets.name',
                'required': True,
                'type': 'text',
                'value': 'Stephan'},
               {'error': '',
                'id': 'form-widgets-gender',
                'label': 'Gender',
                'mode': 'input',
                'name': 'form.widgets.gender',
                'options': [{'content': 'No value',
                              'id': 'form-widgets-gender-novalue',
                              'selected': False,
                              'value': '--NOVALUE--'},
                             {'content': 'male',
                              'id': 'form-widgets-gender-0',
                              'selected': True,
                              'value': 'male'},
                             {'content': 'female',
                              'id': 'form-widgets-gender-1',
                              'selected': False,
                              'value': 'female'}],
                'required': False,
                'type': 'select',
                'value': ['male']},
               {'error': '',
                'id': 'form-widgets-age',
                'label': 'Age',
                'mode': 'input',
                'name': 'form.widgets.age',
                'required': False,
                'type': 'text',
                'value': '23'}],
    'legend': '',
    'mode': 'input',
    'prefix': 'form.',
    'status': 'There were some errors.',
    'title': ''}

Let's try to provide a negative age, which is not possible either:

  >>> request = TestRequest(params={
  ...     'form.widgets.id': 'srichter',
  ...     'form.widgets.gender': ['male'],
  ...     'form.widgets.age': '-5',
  ...     'form.buttons.add': 'Add'}
  ...     )

  >>> addForm = PersonAddForm(root, request)
  >>> addForm.update()

  >>> [(view.widget.label, view) for view in addForm.widgets.errors]
  [('Name', <ErrorViewSnippet for RequiredMissing>),
   ('Age', <ErrorViewSnippet for TooSmall>)]

But the error message for a negative age is too generic:

  >>> print(addForm.widgets['age'].error.render())
  <div class="error">Value is too small</div>

It would be better to say that negative values are disallowed. So let's
register a new error view snippet for the ``TooSmall`` error:

  >>> from pyams_form import error

  >>> @zope.component.adapter(zope.schema.interfaces.TooSmall, None, None, None, None, None)
  ... class TooSmallView(error.ErrorViewSnippet):
  ...
  ...     def update(self):
  ...         super().update()
  ...         if self.field.min == 0:
  ...             self.message = 'The value cannot be a negative number.'

  >>> config.registry.registerAdapter(TooSmallView)

  >>> addForm = PersonAddForm(root, request)
  >>> addForm.update()
  >>> print(addForm.widgets['age'].error.render())
  <div class="error">The value cannot be a negative number.</div>

Note: The ``adapts()`` declaration might look strange. An error view
snippet is actually a multiadapter that adapts a combination of 6
objects -- error, request, widget, field, form, content. By specifying
only the error, we tell the system that we do not care about the other
discriminators, which then can be anything. We could also have used
``zope.interface.Interface`` instead, which would be equivalent.


Additional Form Attributes and API
----------------------------------

Since we are talking about HTML forms here, add and edit forms support all
relevant FORM element attributes as attributes on the class.

  >>> addForm.method
  'post'
  >>> addForm.enctype
  'multipart/form-data'
  >>> addForm.accept_charset
  >>> addForm.accept

The ``action`` attribute is computed. By default it is the current URL:

  >>> addForm.action
  'http://example.com'

The name is also computed. By default it takes the prefix and removes any
trailing ".".

  >>> addForm.name
  'form'

The id is computed from the name, replacing dots with hyphens. Let's set
the prefix to something containing more than one final dot and check how
it works.

  >>> addForm.prefix = 'person.form.add.'
  >>> addForm.id
  'person-form-add'

The template can then use those attributes, if it likes to.

In the examples previously we set the template manually. If no
template is specified, the system tries to find an adapter. Without
any special configuration, there is no adapter, so rendering the form
fails; the ``pyams_template`` package provides a simple component to create adapter
factories from templates.

The form also provides a label for rendering a required info. This required
info depends by default on the given requiredInfo label and if at least one
field is required:

  >>> addForm.required_info
  '<span class="required">*</span>&ndash; required'

If we set the labelRequired to None, we do not get a requiredInfo label:

  >>> addForm.required_label = None
  >>> addForm.required_info is None
  True


Changing Widget Attribute Values
--------------------------------

It frequently happens that a customer comes along and wants to
slightly or totally change some of the text shown in forms or make
optional fields required. It does not make sense to always have to
adjust the schema or implement a custom schema for these use
cases. With the pyams_form framework all attributes -- for which it is
sensible to replace a value without touching the code -- are
customizable via an attribute value adapter.

To demonstrate this feature, let's change the label of the name widget
from "Name" to "Full Name":

  >>> from pyams_form import widget
  >>> NameLabel = widget.StaticWidgetAttribute(
  ...     'Full Name', field=IPerson['name'])
  >>> config.registry.registerAdapter(NameLabel, name='label')

When the form renders, the label has now changed:

  >>> addForm = PersonAddForm(root, TestRequest())
  >>> addForm.update()
  >>> print(format_html(render_xpath(addForm, './/div[2][@class="row"]')))
  <div class="row">
    <label for="form-widgets-name">Full Name</label>
    <input type="text" id="form-widgets-name" name="form.widgets.name" class="text-widget required textline-field" value="" />
  </div>


Adding a "Cancel" button
------------------------

Let's say a client requests that all add forms should have a "Cancel"
button. When the button is pressed, the user is forwarded to the next URL of
the add form. As always, the goal is to not touch the core implementation of
the code, but make those changes externally.

Adding a button/action is a little bit more involved than changing a value,
because you have to insert the additional action and customize the action
handler. Based on your needs of flexibility, multiple approaches could be
chosen. Here we demonstrate the simplest one.

The first step is to create a custom action manager that always inserts a
cancel action:

  >>> from pyams_form import button
  >>> @zope.component.adapter(interfaces.form.IAddForm, zope.interface.Interface,
  ...                         zope.interface.Interface)
  ... class AddActions(button.ButtonActions):
  ...
  ...     def update(self):
  ...         self.form.buttons = button.Buttons(
  ...             self.form.buttons,
  ...             button.Button('cancel', 'Cancel'))
  ...         super().update()

After registering the new action manager,

  >>> config.registry.registerAdapter(AddActions)

the add form should display a cancel button:

  >>> addForm.update()
  >>> print(format_html(render_xpath(addForm, './/div[@class="action"]')))
  <div class="action">
      <input type="submit" id="form-buttons-add" name="form.buttons.add" class="submit-widget button-field" value="Add" />
    </div>
  <div class="action">
      <input type="submit" id="form-buttons-cancel" name="form.buttons.cancel" class="submit-widget button-field" value="Cancel" />
    </div>

But showing the button does not mean it does anything. So we also need a
custom action handler to handle the cancel action:

  >>> @zope.component.adapter(interfaces.form.IAddForm, zope.interface.Interface,
  ...         zope.interface.Interface, button.ButtonAction)
  ... class AddActionHandler(button.ButtonActionHandler):
  ...
  ...     def __call__(self):
  ...         if self.action.name == 'form.buttons.cancel':
  ...            self.form.finished_state.update({
  ...                'action': self.action
  ...            })
  ...            return
  ...         super().__call__()

After registering the action handler,

  >>> config.registry.registerAdapter(AddActionHandler)

we can press the cancel button and we will be forwarded:

  >>> request = TestRequest(params={'form.buttons.cancel': 'Cancel'})

  >>> addForm = PersonAddForm(root, request)
  >>> addForm.update()
  >>> format_html(addForm.render())
  ''

  >>> request.response.status_code
  302
  >>> request.response.location
  'http://example.com'

Eventually, we might have action managers and handlers that are much more
powerful and some of the manual labor in this example would become
unnecessary.


Creating an Edit Form
---------------------

Now that we have exhaustively covered the customization possibilities of add
forms, let's create an edit form. Edit forms are even simpler than add forms,
since all actions are completely automatic:

  >>> class PersonEditForm(form.EditForm):
  ...
  ...     fields = field.Fields(IPerson)

We can use the created person from the successful addition above.

  >>> editForm = PersonEditForm(root['srichter'], TestRequest())

After adding a template, we can look at the form:

  >>> addTemplate(PersonEditForm)
  >>> editForm.update()
  >>> print(format_html(editForm.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-id">ID</label>
      <span id="form-widgets-id"
        class="text-widget textline-field">srichter</span>
    </div>
    <div class="row">
      <label for="form-widgets-name">Full Name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="Stephan Richter" />
    </div>
    <div class="row">
      <label for="form-widgets-gender">Gender</label>
      <select id="form-widgets-gender"
          name="form.widgets.gender"
          class="select-widget choice-field"
          size="1">
      <option id="form-widgets-gender-novalue"
              value="--NOVALUE--">No value</option>
      <option id="form-widgets-gender-0"
              value="male"
              selected="selected">male</option>
      <option id="form-widgets-gender-1"
              value="female">female</option>
  </select>
  <input name="form.widgets.gender-empty-marker" type="hidden" value="1" />
    </div>
    <div class="row">
      <label for="form-widgets-age">Age</label>
      <input type="text"
         id="form-widgets-age"
         name="form.widgets.age"
         class="text-widget int-field"
         title="The person's age."
         value="20" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field"
         value="Apply" />
    </div>
  </form>

As you can see, the data are being pulled in from the context for the edit
form. Next we will look at the behavior when submitting the form.


Failure Upon Submission of Edit Form
------------------------------------

Let's now submit the form having some invalid data.

  >>> request = TestRequest(params={
  ...     'form.widgets.name': 'Claudia Richter',
  ...     'form.widgets.gender': ['female'],
  ...     'form.widgets.age': '-1',
  ...     'form.buttons.apply': 'Apply'}
  ...     )

  >>> editForm = PersonEditForm(root['srichter'], request)
  >>> editForm.update()
  >>> print(format_html(editForm.render()))
    <i>There were some errors.</i>
    <ul>
      <li>
          Age
        <div class="error">The value cannot be a negative number.</div>
      </li>
    </ul>
    <form action=".">
      <div class="row">
        <label for="form-widgets-id">ID</label>
        <span id="form-widgets-id"
          class="text-widget textline-field">srichter</span>
      </div>
      <div class="row">
        <label for="form-widgets-name">Full Name</label>
        <input type="text"
           id="form-widgets-name"
           name="form.widgets.name"
           class="text-widget required textline-field"
           value="Claudia Richter" />
      </div>
      <div class="row">
        <label for="form-widgets-gender">Gender</label>
        <select id="form-widgets-gender"
            name="form.widgets.gender"
            class="select-widget choice-field"
            size="1">
        <option id="form-widgets-gender-novalue"
                value="--NOVALUE--">No value</option>
        <option id="form-widgets-gender-0"
                value="male">male</option>
        <option id="form-widgets-gender-1"
                value="female"
                selected="selected">female</option>
    </select>
    <input name="form.widgets.gender-empty-marker" type="hidden" value="1" />
      </div>
      <div class="row">
        <b><div class="error">The value cannot be a negative number.</div></b>
        <label for="form-widgets-age">Age</label>
        <input type="text"
           id="form-widgets-age"
           name="form.widgets.age"
           class="text-widget int-field"
           title="The person's age."
           value="-1" />
      </div>
      <div class="action">
        <input type="submit"
           id="form-buttons-apply"
           name="form.buttons.apply"
           class="submit-widget button-field"
           value="Apply" />
      </div>
    </form>


Successfully Editing Content
----------------------------

Let's now resubmit the form with valid data, so the data should be updated.

  >>> request = TestRequest(params={
  ...     'form.widgets.name': 'Claudia Richter',
  ...     'form.widgets.gender': ['female'],
  ...     'form.widgets.age': '27',
  ...     'form.buttons.apply': 'Apply'}
  ...     )

  >>> editForm = PersonEditForm(root['srichter'], request)
  >>> editForm.update()
  >>> print(format_html(render_xpath(editForm, './/i')))
  <i>Data successfully updated.</i>

  >>> stephan = root['srichter']
  >>> stephan.name
  'Claudia Richter'
  >>> stephan.gender
  'female'
  >>> stephan.age
  27

When an edit form is successfully committed, a detailed object-modified event
is sent out telling the system about the changes. To see the error, let's
create an event subscriber for object-modified events:

  >>> eventlog = []
  >>> import zope.lifecycleevent
  >>> def logEvent(event):
  ...     eventlog.append(event)
  >>> _ = config.add_subscriber(logEvent, zope.lifecycleevent.interfaces.IObjectModifiedEvent)

Let's now submit the form again, successfully changing the age:

  >>> request = TestRequest(params={
  ...     'form.widgets.name': 'Claudia Richter',
  ...     'form.widgets.gender': ['female'],
  ...     'form.widgets.age': '29',
  ...     'form.buttons.apply': 'Apply'}
  ...     )

  >>> editForm = PersonEditForm(root['srichter'], request)
  >>> editForm.update()

We can now look at the event:

  >>> event = eventlog[-1]
  >>> event
  <zope...ObjectModifiedEvent object at ...>

  >>> attrs = event.descriptions[0]
  >>> attrs.interface
  <InterfaceClass ....IPerson>
  >>> attrs.attributes
  ('age',)


Successful Action with No Changes
---------------------------------

When submitting the form without any changes, the form will tell you so.

  >>> request = TestRequest(params={
  ...     'form.widgets.name': 'Claudia Richter',
  ...     'form.widgets.gender': ['female'],
  ...     'form.widgets.age': '29',
  ...     'form.buttons.apply': 'Apply'}
  ...     )

  >>> editForm = PersonEditForm(root['srichter'], request)
  >>> editForm.update()
  >>> print(render_xpath(editForm, './/i'))
  <i>No changes were applied.</i>


Changing Status Messages
------------------------

Depending on the project, it is often desirable to change the status messages
to fit the application. In ``zope.formlib`` this was hard to do, since the
messages were buried within fairly complex methods that one did not want to
touch. In this package all those messages are exposed as form attributes.

There are three messages for the edit form:

* ``form_errors_message`` -- Indicates that an error occurred while
  applying the changes. This message is also available for the add form.

* ``success_message`` -- The form data was successfully applied.

* ``no_changes_message`` -- No changes were found in the form data.

Let's now change the ``no_changes_message``:

  >>> editForm.no_changes_message = 'No changes were detected in the form data.'
  >>> editForm.update()
  >>> print(render_xpath(editForm, './/i'))
  <i>No changes were detected in the form data.</i>

When even more flexibility is required within a project, one could also
implement these messages as properties looking up an attribute value. However,
we have found this to be a rare case.


Creating Edit Forms for Dictionaries
------------------------------------

Sometimes it is not desirable to edit a class instance that implements the
fields, but other types of object. A good example is the need to modify a
simple dictionary, where the field names are the keys. To do that, a special
data manager for dictionaries is available:

The only step the developer has to complete is to re-implement the form's
``get_content()`` method to return the dictionary:

  >>> personDict = {'id': 'rineichen', 'name': 'Roger Ineichen',
  ...               'gender': None, 'age': None}
  >>> class PersonDictEditForm(PersonEditForm):
  ...     def get_content(self):
  ...         return personDict

We can now use the form as usual:

  >>> addTemplate(PersonDictEditForm)
  >>> editForm = PersonDictEditForm(None, TestRequest())
  >>> editForm.update()
  >>> print(format_html(editForm.render()))
    <form action=".">
      <div class="row">
        <label for="form-widgets-id">ID</label>
        <span id="form-widgets-id"
          class="text-widget textline-field">rineichen</span>
      </div>
      <div class="row">
        <label for="form-widgets-name">Full Name</label>
        <input type="text"
           id="form-widgets-name"
           name="form.widgets.name"
           class="text-widget required textline-field"
           value="Roger Ineichen" />
      </div>
      <div class="row">
        <label for="form-widgets-gender">Gender</label>
        <select id="form-widgets-gender"
            name="form.widgets.gender"
            class="select-widget choice-field"
            size="1">
        <option id="form-widgets-gender-novalue"
                value="--NOVALUE--"
                selected="selected">No value</option>
        <option id="form-widgets-gender-0"
                value="male">male</option>
        <option id="form-widgets-gender-1"
                value="female">female</option>
    </select>
    <input name="form.widgets.gender-empty-marker" type="hidden" value="1" />
      </div>
      <div class="row">
        <label for="form-widgets-age">Age</label>
        <input type="text"
           id="form-widgets-age"
           name="form.widgets.age"
           class="text-widget int-field"
           title="The person's age."
           value="20" />
      </div>
      <div class="action">
        <input type="submit"
           id="form-buttons-apply"
           name="form.buttons.apply"
           class="submit-widget button-field"
           value="Apply" />
      </div>
    </form>

Note that the name displayed in the form is identical to the one in the
dictionary. Let's now submit a form to ensure that the data are also written to
the dictionary:

  >>> request = TestRequest(params={
  ...     'form.widgets.name': 'Jesse Ineichen',
  ...     'form.widgets.gender': ['male'],
  ...     'form.widgets.age': '5',
  ...     'form.buttons.apply': 'Apply'}
  ...     )
  >>> editForm = PersonDictEditForm(None, request)
  >>> editForm.update()

  >>> len(personDict)
  4
  >>> personDict['age']
  5
  >>> personDict['gender']
  'male'
  >>> personDict['id']
  'rineichen'
  >>> personDict['name']
  'Jesse Ineichen'


Creating a Display Form
-----------------------

Creating a display form is simple; just instantiate, update and render it:

  >>> class PersonDisplayForm(form.DisplayForm):
  ...     fields = field.Fields(IPerson)
  >>> addTemplate(PersonDisplayForm, 'simple-display.pt')

  >>> display = PersonDisplayForm(stephan, TestRequest())
  >>> display.update()
  >>> print(display.render())
    <div class="row">
      <span id="form-widgets-id"
          class="text-widget textline-field">srichter</span>
    </div>
    <div class="row">
      <span id="form-widgets-name"
          class="text-widget textline-field">Claudia Richter</span>
    </div>
    <div class="row">
      <span id="form-widgets-gender"
          class="select-widget choice-field"><span
          class="selected-option">female</span></span>
    </div>
    <div class="row">
      <span id="form-widgets-age"
          class="text-widget int-field"
          title="The person's age.">29</span>
    </div>


Simple Form Customization
-------------------------

The form exposes several of the widget manager's attributes as attributes on
the form. They are: ``mode``, ``ignore_context``, ``ignore_request``, and
``ignore_readonly``.

Here are the values for the display form we just created:

  >>> display.mode
  'display'
  >>> display.ignore_context
  False
  >>> display.ignore_request
  True
  >>> display.ignore_readonly
  False

These values should be equal to the ones of the widget manager:

  >>> display.widgets.mode
  'display'
  >>> display.widgets.ignore_context
  False
  >>> display.widgets.ignore_request
  True
  >>> display.widgets.ignore_readonly
  False

Now, if we change those values before updating the widgets, ...

  >>> display.mode = interfaces.INPUT_MODE
  >>> display.ignore_context = True
  >>> display.ignore_request = False
  >>> display.ignore_readonly = True

... the widget manager will have the same values after updating the widgets:

  >>> display.update_widgets()

  >>> display.widgets.mode
  'input'
  >>> display.widgets.ignore_context
  True
  >>> display.widgets.ignore_request
  False
  >>> display.widgets.ignore_readonly
  True

We can also set the widget prefix when we update the widgets:

  >>> display.update_widgets(prefix="person")
  >>> display.widgets.prefix
  'person'

This will affect the individual widgets' names:

  >>> display.widgets['id'].name
  'form.person.id'

To use unqualified names, we must clear both the form prefix and the
widgets prefix:

  >>> display.prefix = ""
  >>> display.update_widgets(prefix="")
  >>> display.widgets['id'].name
  'id'

Extending Forms
---------------

One very common use case is to extend forms. For example, you would like to
use the edit form and its defined "Apply" button, but add another button
yourself. Unfortunately, just inheriting the form is not enough, because the
new button and handler declarations will override the inherited ones. Let me
demonstrate the problem:

  >>> class BaseForm(form.Form):
  ...     fields = field.Fields(IPerson).select('name')
  ...
  ...     @button.button_and_handler('Apply')
  ...     def handleApply(self, action):
  ...         print('success')

  >>> list(BaseForm.fields.keys())
  ['name']
  >>> list(BaseForm.buttons.keys())
  ['apply']
  >>> BaseForm.handlers
  <Handlers [<Handler for <Button 'apply' 'Apply'>>]>

Let's now derive a form from the base form:

  >>> class DerivedForm(BaseForm):
  ...     fields = field.Fields(IPerson).select('gender')
  ...
  ...     @button.button_and_handler('Cancel')
  ...     def handleCancel(self, action):
  ...         print('cancel')

  >>> list(DerivedForm.fields.keys())
  ['gender']
  >>> list(DerivedForm.buttons.keys())
  ['cancel']
  >>> DerivedForm.handlers
  <Handlers [<Handler for <Button 'cancel' 'Cancel'>>]>

The obvious method to "inherit" the base form's information is to copy it
over:

  >>> class DerivedForm(BaseForm):
  ...     fields = BaseForm.fields.copy()
  ...     buttons = BaseForm.buttons.copy()
  ...     handlers = BaseForm.handlers.copy()
  ...
  ...     fields += field.Fields(IPerson).select('gender')
  ...
  ...     @button.button_and_handler('Cancel')
  ...     def handleCancel(self, action):
  ...         print('cancel')

  >>> list(DerivedForm.fields.keys())
  ['name', 'gender']
  >>> list(DerivedForm.buttons.keys())
  ['apply', 'cancel']
  >>> DerivedForm.handlers
  <Handlers
      [<Handler for <Button 'apply' 'Apply'>>,
       <Handler for <Button 'cancel' 'Cancel'>>]>

But this is pretty clumsy. Instead, the ``form`` module provides a helper
method that will do the extending for you:

  >>> class DerivedForm(BaseForm):
  ...     form.extends(BaseForm)
  ...
  ...     fields += field.Fields(IPerson).select('gender')
  ...
  ...     @button.button_and_handler(u'Cancel')
  ...     def handleCancel(self, action):
  ...         print('cancel')

  >>> list(DerivedForm.fields.keys())
  ['name', 'gender']
  >>> list(DerivedForm.buttons.keys())
  ['apply', 'cancel']
  >>> DerivedForm.handlers
  <Handlers
      [<Handler for <Button 'apply' 'Apply'>>,
       <Handler for <Button 'cancel' 'Cancel'>>]>

If you, for example do not want to extend the buttons, you can turn that off:

  >>> class DerivedForm(BaseForm):
  ...     form.extends(BaseForm, ignore_buttons=True)
  ...
  ...     fields += field.Fields(IPerson).select('gender')
  ...
  ...     @button.button_and_handler(u'Cancel')
  ...     def handleCancel(self, action):
  ...         print('cancel')

  >>> list(DerivedForm.fields.keys())
  ['name', 'gender']
  >>> list(DerivedForm.buttons.keys())
  ['cancel']
  >>> DerivedForm.handlers
  <Handlers
      [<Handler for <Button 'apply' 'Apply'>>,
       <Handler for <Button 'cancel' 'Cancel'>>]>

If you, for example do not want to extend the handlers, you can turn that off:

  >>> class DerivedForm(BaseForm):
  ...     form.extends(BaseForm, ignore_handlers=True)
  ...
  ...     fields += field.Fields(IPerson).select('gender')
  ...
  ...     @button.button_and_handler(u'Cancel')
  ...     def handleCancel(self, action):
  ...         print('cancel')

  >>> list(DerivedForm.fields.keys())
  ['name', 'gender']
  >>> list(DerivedForm.buttons.keys())
  ['apply', 'cancel']
  >>> DerivedForm.handlers
  <Handlers [<Handler for <Button 'cancel' 'Cancel'>>]>


Custom widget factories
-----------------------

Another important part of a form is that we can use custom widgets. We can do
this in a form by defining a widget factory for a field. We can get the field
from the fields collection e.g. ``fields['foo']``. This means, we can define
new widget factories by defining ``fields['foo'].widget_factory = MyWidget``.
Let's show a sample and define a custom widget:

  >>> from pyams_form.browser import text
  >>> class MyWidget(text.TextWidget):
  ...     """My new widget."""
  ...     klass = 'MyCSS'

Now we can define a field widget factory:

  >>> def MyFieldWidget(field, request):
  ...     """IFieldWidget factory for MyWidget."""
  ...     return widget.FieldWidget(field, MyWidget(request))

We register the ``MyWidget`` in a form like:

  >>> class MyEditForm(form.EditForm):
  ...
  ...     fields = field.Fields(IPerson)
  ...     fields['name'].widget_factory = MyFieldWidget

We can see that the custom widget gets used in the rendered form:

  >>> myEdit = MyEditForm(root['srichter'], TestRequest())
  >>> addTemplate(MyEditForm)
  >>> myEdit.update()
  >>> print(format_html(render_xpath(myEdit, './/input[@id="form-widgets-name"]')))
  <input type="text" id="form-widgets-name"
         name="form.widgets.name" class="MyCSS required textline-field"
         value="Claudia Richter" />


Hidden fields
-------------

Another important part of a form is that we can generate hidden widgets. We can
do this in a form by defining a widget mode. We can do this by override the
setUpWidgets method.

  >>> class HiddenFieldEditForm(form.EditForm):
  ...
  ...     fields = field.Fields(IPerson)
  ...     fields['name'].widget_factory = MyFieldWidget
  ...
  ...     def update_widgets(self):
  ...         super().update_widgets()
  ...         self.widgets['age'].mode = interfaces.HIDDEN_MODE

We can see that the widget gets rendered as hidden:

  >>> addTemplate(HiddenFieldEditForm)
  >>> hiddenEdit = HiddenFieldEditForm(root['srichter'], TestRequest())
  >>> hiddenEdit.update()
  >>> print(render_xpath(hiddenEdit, './/input[@id="form-widgets-age"]'))
  <input type="hidden" id="form-widgets-age" name="form.widgets.age" value="29" class="hidden-widget" title="The person's age." />


Actions with Errors
-------------------

Even though the data might be validated correctly, it sometimes happens that
data turns out to be invalid while the action is executed. In those cases a
special action execution error can be raised that wraps the original error.

  >>> class PersonAddForm(form.AddForm):
  ...
  ...     fields = field.Fields(IPerson).select('id')
  ...
  ...     @button.button_and_handler('Check')
  ...     def handleCheck(self, action):
  ...         data, errors = self.extract_data()
  ...         if data['id'] in self.get_content():
  ...             raise interfaces.button.WidgetActionExecutionError(
  ...                 'id', zope.interface.Invalid('Id already exists'))

In this case the action execution error is specific to a widget. The framework
will attach a proper error view to the widget and the widget manager:

  >>> request = TestRequest(params={
  ...     'form.widgets.id': 'srichter',
  ...     'form.buttons.check': 'Check'}
  ...     )

  >>> addForm = PersonAddForm(root, request)
  >>> addForm.update()

  >>> addForm.widgets.errors
  (<InvalidErrorViewSnippet for Invalid>,)
  >>> addForm.widgets['id'].error
  <InvalidErrorViewSnippet for Invalid>
  >>> addForm.status
  'There were some errors.'

If the error is non-widget specific, then we can simply use the generic action
execution error:

  >>> class PersonAddForm(form.AddForm):
  ...
  ...     fields = field.Fields(IPerson).select('id')
  ...
  ...     @button.button_and_handler('Check')
  ...     def handleCheck(self, action):
  ...         raise interfaces.button.ActionExecutionError(
  ...             zope.interface.Invalid('Some problem occurred.'))

Let's have a look at the result:

  >>> addForm = PersonAddForm(root, request)
  >>> addForm.update()

  >>> addForm.widgets.errors
  (<InvalidErrorViewSnippet for Invalid>,)
  >>> addForm.status
  'There were some errors.'

**Note**:

  The action execution errors are connected to the form via an event
  listener called ``handler_action_error``. This event listener listens for
  ``IActionErrorEvent`` events. If the event is called for an action associated
  with a form, the listener does its work as seen above. If the action is not
  coupled to a form, then event listener does nothing:

    >>> from pyams_form import action

    >>> cancel = action.Action(request, 'Cancel')
    >>> event = action.ActionErrorOccurred(cancel, ValueError(3))

    >>> form.handle_action_error(event)


Applying Changes
----------------

When applying the data of a form to a content component, the function
``apply_changes()`` is called. It simply iterates through the fields of the
form and uses the data managers to store the values. The output of the
function is a list of changes:

  >>> roger = Person('roger', 'Roger')
  >>> roger
  <Person 'Roger'>

  >>> class BaseForm(form.Form):
  ...     fields = field.Fields(IPerson).select('name')
  >>> myForm = BaseForm(roger, TestRequest())

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {<InterfaceClass ....IPerson>: ['name']}

  >>> roger
  <Person 'Roger Ineichen'>

When a field is missing from the data, it is simply skipped:

  >>> form.apply_changes(myForm, roger, {})
  {}

If the new and old value are identical, storing the data is skipped as well:

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {}

In some cases the data converter for a field-widget pair returns the
form and uses the data managers to store the values. The output of the
function is a list of changes:

  >>> roger = Person('roger', 'Roger')
  >>> roger
  <Person 'Roger'>

  >>> class BaseForm(form.Form):
  ...     fields = field.Fields(IPerson).select('name')
  >>> myForm = BaseForm(roger, TestRequest())

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {<InterfaceClass ....IPerson>: ['name']}

  >>> roger
  <Person 'Roger Ineichen'>

When a field is missing from the data, it is simply skipped:

  >>> form.apply_changes(myForm, roger, {})
  {}

If the new and old value are identical, storing the data is skipped as well:

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {}

In some cases the data converter for a field-widget pair returns the
form and uses the data managers to store the values. The output of the
function is a list of changes:

  >>> roger = Person('roger', 'Roger')
  >>> roger
  <Person 'Roger'>

  >>> class BaseForm(form.Form):
  ...     fields = field.Fields(IPerson).select('name')
  >>> myForm = BaseForm(roger, TestRequest())

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {<InterfaceClass ....IPerson>: ['name']}

  >>> roger
  <Person 'Roger Ineichen'>

When a field is missing from the data, it is simply skipped:

  >>> form.apply_changes(myForm, roger, {})
  {}

If the new and old value are identical, storing the data is skipped as well:

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {}

In some cases the data converter for a field-widget pair returns the
form and uses the data managers to store the values. The output of the
function is a list of changes:

  >>> roger = Person('roger', 'Roger')
  >>> roger
  <Person 'Roger'>

  >>> class BaseForm(form.Form):
  ...     fields = field.Fields(IPerson).select('name')
  >>> myForm = BaseForm(roger, TestRequest())

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {<InterfaceClass ....IPerson>: ['name']}

  >>> roger
  <Person 'Roger Ineichen'>

When a field is missing from the data, it is simply skipped:

  >>> form.apply_changes(myForm, roger, {})
  {}

If the new and old value are identical, storing the data is skipped as well:

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {}

In some cases the data converter for a field-widget pair returns the
form and uses the data managers to store the values. The output of the
function is a list of changes:

  >>> roger = Person('roger', 'Roger')
  >>> roger
  <Person 'Roger'>

  >>> class BaseForm(form.Form):
  ...     fields = field.Fields(IPerson).select('name')
  >>> myForm = BaseForm(roger, TestRequest())

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {<InterfaceClass ....IPerson>: ['name']}

  >>> roger
  <Person 'Roger Ineichen'>

When a field is missing from the data, it is simply skipped:

  >>> form.apply_changes(myForm, roger, {})
  {}

If the new and old value are identical, storing the data is skipped as well:

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {}

In some cases the data converter for a field-widget pair returns the
form and uses the data managers to store the values. The output of the
function is a list of changes:

  >>> roger = Person('roger', 'Roger')
  >>> roger
  <Person 'Roger'>

  >>> class BaseForm(form.Form):
  ...     fields = field.Fields(IPerson).select('name')
  >>> myForm = BaseForm(roger, TestRequest())

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {<InterfaceClass ....IPerson>: ['name']}

  >>> roger
  <Person 'Roger Ineichen'>

When a field is missing from the data, it is simply skipped:

  >>> form.apply_changes(myForm, roger, {})
  {}

If the new and old value are identical, storing the data is skipped as well:

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {}

In some cases the data converter for a field-widget pair returns the
form and uses the data managers to store the values. The output of the
function is a list of changes:

  >>> roger = Person('roger', 'Roger')
  >>> roger
  <Person 'Roger'>

  >>> class BaseForm(form.Form):
  ...     fields = field.Fields(IPerson).select('name')
  >>> myForm = BaseForm(roger, TestRequest())

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {<InterfaceClass ....IPerson>: ['name']}

  >>> roger
  <Person 'Roger Ineichen'>

When a field is missing from the data, it is simply skipped:

  >>> form.apply_changes(myForm, roger, {})
  {}

If the new and old value are identical, storing the data is skipped as well:

  >>> form.apply_changes(myForm, roger, {'name': 'Roger Ineichen'})
  {}

In some cases the data converter for a field-widget pair returns the
``NOT_CHANGED`` value. In this case, the field is skipped as well:

  >>> from pyams_utils.interfaces.form import NOT_CHANGED

  >>> form.apply_changes(myForm, roger, {'name': NOT_CHANGED})
  {}

  >>> roger
  <Person 'Roger Ineichen'>

  >>> form.apply_changes(myForm, roger, {'name': NOT_CHANGED})
  {}

  >>> roger
  <Person 'Roger Ineichen'>

  >>> form.apply_changes(myForm, roger, {'name': NOT_CHANGED})
  {}

  >>> roger
  <Person 'Roger Ineichen'>


Refreshing actions
------------------

Sometimes, it's useful to update actions again after executing them,
because some conditions could have changed. For example, imagine
we have a sequence edit form that has a delete button. We don't
want to show delete button when the sequence is empty. The button
condition would handle this, but what if the sequence becomes empty
as a result of execution of the delete action that was available?
In that case we want to refresh our actions to new conditions to make
our delete button not visible anymore. The ``refreshActions`` form
variable is intended to handle this case.

Let's create a simple form with an action that clears our context
sequence.

  >>> class SequenceForm(form.Form):
  ...
  ...     @button.button_and_handler('Empty', condition=lambda form:bool(form.context))
  ...     def handleEmpty(self, action):
  ...         self.context[:] = []
  ...         self.refresh_actions = True

  >>> addTemplate(SequenceForm)

First, let's illustrate simple cases, when no button is pressed.
The button will be available when context is not empty.

  >>> context = [1, 2, 3, 4]
  >>> request = TestRequest()
  >>> myForm = SequenceForm(context, request)
  >>> myForm.update()
  >>> print(format_html(render_xpath(myForm, './/div[@class="action"]')))
  <div class="action">
      <input type="submit" id="form-buttons-empty" name="form.buttons.empty" class="submit-widget button-field" value="Empty" />
    </div>

The button will not be available when the context is empty.

  >>> context = []
  >>> request = TestRequest()
  >>> myForm = SequenceForm(context, request)
  >>> myForm.update()
  >>> print(format_html(myForm.render()))
  <form action=".">
  </form>

Now, the most interesting case when context is not empty, but becomes
empty as a result of pressing the "empty" button. We set the
``refreshActions`` flag in the action handler, so our actions should
be updated to new conditions.

  >>> context = [1, 2, 3, 4, 5]
  >>> request = TestRequest(params={
  ...     'form.buttons.empty': 'Empty'}
  ...     )
  >>> myForm = SequenceForm(context, request)
  >>> myForm.update()
  >>> print(format_html(myForm.render()))
  <form action=".">
  </form>

Integration tests
-----------------

Identifying the different forms can be important if it comes to layout
template lookup. Let's ensure that we support the right interfaces for the
different forms.


Form
~~~~

  >>> obj = form.Form(None, None)

  >>> interfaces.form.IForm.providedBy(obj)
  True

  >>> interfaces.form.IDisplayForm.providedBy(obj)
  False

  >>> interfaces.form.IEditForm.providedBy(obj)
  False

  >>> interfaces.form.IAddForm.providedBy(obj)
  False


DisplayForm
~~~~~~~~~~~

  >>> obj = form.DisplayForm(None, None)

  >>> interfaces.form.IForm.providedBy(obj)
  True

  >>> interfaces.form.IDisplayForm.providedBy(obj)
  True

  >>> interfaces.form.IEditForm.providedBy(obj)
  False

  >>> interfaces.form.IAddForm.providedBy(obj)
  False


EditForm
~~~~~~~~

  >>> obj = form.EditForm(None, None)

  >>> interfaces.form.IForm.providedBy(obj)
  True

  >>> interfaces.form.IDisplayForm.providedBy(obj)
  False

  >>> interfaces.form.IEditForm.providedBy(obj)
  True

  >>> interfaces.form.IAddForm.providedBy(obj)
  False


AddForm
~~~~~~~

  >>> obj = form.AddForm(None, None)

  >>> interfaces.form.IForm.providedBy(obj)
  True

  >>> interfaces.form.IDisplayForm.providedBy(obj)
  False

  >>> interfaces.form.IEditForm.providedBy(obj)
  False

  >>> interfaces.form.IAddForm.providedBy(obj)
  True


Tests cleanup:

  >>> tearDown()
