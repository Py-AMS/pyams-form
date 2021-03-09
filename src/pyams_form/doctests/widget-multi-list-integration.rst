MultiWidget List integration tests
----------------------------------

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

  >>> from pyams_form import util, testing
  >>> testing.setup_form_defaults(config.registry)

  >>> from pyams_utils.testing import format_html

Checking components on the highest possible level.

  >>> from datetime import date
  >>> from pyams_form import form
  >>> from pyams_form import field
  >>> from pyams_form import testing

  >>> request = testing.TestRequest()

  >>> class EForm(form.EditForm):
  ...     form.extends(form.EditForm)
  ...     fields = field.Fields(
  ...         testing.IMultiWidgetListIntegration).omit(
  ...             'list_of_choice', 'list_of_objects')

Our single content object:

  >>> obj = testing.MultiWidgetListIntegration()

We recreate the form each time, to stay as close as possible.
In real life the form gets instantiated and destroyed with each request.

  >>> import os
  >>> from pyams_template.interfaces import IContentTemplate
  >>> from pyams_template.template import TemplateFactory
  >>> from pyams_layer.interfaces import IFormLayer
  >>> from pyams_form import interfaces, tests

  >>> def getForm(request):
  ...     factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                               'templates', 'integration-edit.pt'), 'text/html')
  ...     config.registry.registerAdapter(factory, (None, IFormLayer, EForm), IContentTemplate)
  ...     frm = EForm(obj, request)
  ...     frm.update()
  ...     content = frm.render()
  ...     return content

Empty
#####

All blank and empty values:

  >>> content = getForm(request)

  >>> print(testing.plain_text(content))
  ListOfInt label
  <BLANKLINE>
  [Add]
  ListOfBool label
  <BLANKLINE>
  [Add]
  ListOfTextLine label
  <BLANKLINE>
  [Add]
  ListOfDate label
  <BLANKLINE>
  [Add]
  [Apply]

Some valid default values
#########################

  >>> obj.list_of_int = [-100, 1, 100]
  >>> obj.list_of_bool = [True, False, True]
  >>> obj.list_of_choice = ['two', 'three']
  >>> obj.list_of_textline = ['some text one', 'some txt two']
  >>> obj.list_of_date = [date(2014, 6, 20)]

  >>> from pprint import pprint
  >>> pprint(obj)
  <MultiWidgetListIntegration
    list_of_bool: [True, False, True]
    list_of_choice: ['two', 'three']
    list_of_date: [datetime.date(2014, 6, 20)]
    list_of_int: [-100, 1, 100]
    list_of_textline: ['some text one', 'some txt two']>

  >>> content = getForm(request)

  >>> print(testing.plain_text(content))
  ListOfInt label Int label *
  [ ]
  [-100]
  Int label *
  [ ]
  [1]
  Int label *
  [ ]
  [100]
  [Add] [Remove selected]
  ListOfBool label Bool label
  [ ]
  (O) yes ( ) no
  Bool label
  [ ]
  ( ) yes (O) no
  Bool label
  [ ]
  (O) yes ( ) no
  [Add] [Remove selected]
  ListOfTextLine label TextLine label *
  [ ]
  [some text one]
  TextLine label *
  [ ]
  [some txt two]
  [Add] [Remove selected]
  ListOfDate label Date label *
  [ ]
  [6/20/14]
  [Add] [Remove selected]
  [Apply]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    list_of_bool: [True, False, True]
    list_of_choice: ['two', 'three']
    list_of_date: [datetime.date(2014, 6, 20)]
    list_of_int: [-100, 1, 100]
    list_of_textline: ['some text one', 'some txt two']>

list_of_int
###########

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_int.1'] = 'foobar'

  >>> submit['form.widgets.list_of_int.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request)

  >>> print(testing.plain_text(content,
  ...       './/div[@id="row-form-widgets-list_of_int"]'))
  ListOfInt label Int label *
  [ ]
  [-100]
  Int label *
  The entered value is not a valid integer literal.
  [ ]
  [foobar]
  Int label *
  [ ]
  [100]
  Int label *
  [ ]
  []
  [Add] [Remove selected]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_int"]//div[@class="error"]'))
  The entered value is not a valid integer literal.
  Required input is missing.

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_int.1.remove'] = '1'
  >>> submit['form.widgets.list_of_int.2.remove'] = '1'
  >>> submit['form.widgets.list_of_int.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_int"]'))
  ListOfInt label
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  [-100]
  Int label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    list_of_bool: [True, False, True]
    list_of_choice: ['two', 'three']
    list_of_date: [datetime.date(2014, 6, 20)]
    list_of_int: [-100, 1, 100]
    list_of_textline: ['some text one', 'some txt two']>


list_of_bool
############

Add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_bool.buttons.add'] = 'Add'
  >>> request = testing.TestRequest(params=submit)

Important is that we get a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_bool"]'))
  ListOfBool label
  <BLANKLINE>
  Bool label
  <BLANKLINE>
  [ ]
  (O) yes ( ) no
  Bool label
  <BLANKLINE>
  [ ]
  ( ) yes (O) no
  Bool label
  <BLANKLINE>
  [ ]
  (O) yes ( ) no
  Bool label
  <BLANKLINE>
  [ ]
  ( ) yes ( ) no
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_bool"]//div[@class="error"]'))
  <BLANKLINE>

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_bool.1.remove'] = '1'
  >>> submit['form.widgets.list_of_bool.2.remove'] = '1'
  >>> submit['form.widgets.list_of_bool.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_bool"]'))
  ListOfBool label Bool label
  [ ]
  (O) yes ( ) no
  Bool label
  [ ]
  ( ) yes ( ) no
  [Add] [Remove selected]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    list_of_bool: [True, False, True]
    list_of_choice: ['two', 'three']
    list_of_date: [datetime.date(2014, 6, 20)]
    list_of_int: [-100, 1, 100]
    list_of_textline: ['some text one', 'some txt two']>


list_of_textline
################

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_textline.1'] = 'foo\nbar'

  >>> submit['form.widgets.list_of_textline.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "Constraint not satisfied"
for "foo\nbar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_textline"]'))
  ListOfTextLine label
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  [ ]
  [some text one]
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [ ]
  [foo
  bar]
  TextLine label *
  <BLANKLINE>
  [ ]
  []
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_textline"]//div[@class="error"]'))
  Constraint not satisfied
  Required input is missing.

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_textline.0.remove'] = '1'
  >>> submit['form.widgets.list_of_textline.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_textline"]'))
  ListOfTextLine label
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [ ]
  [foo
  bar]
  TextLine label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    list_of_bool: [True, False, True]
    list_of_choice: ['two', 'three']
    list_of_date: [datetime.date(2014, 6, 20)]
    list_of_int: [-100, 1, 100]
    list_of_textline: ['some text one', 'some txt two']>


list_of_date
############

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_date.0'] = 'foobar'

  >>> submit['form.widgets.list_of_date.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "The datetime string did not match the pattern"
for "foobar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_date"]'))
  ListOfDate label
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [ ]
  [foobar]
  Date label *
  <BLANKLINE>
  [ ]
  []
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_date"]//div[@class="error"]'))
  The datetime string did not match the pattern 'M/d/yy'.
  Required input is missing.

Add one more field:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_date.buttons.add'] = 'Add'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)

And fill in a valid value:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_date.2'] = '6/21/14'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_date"]'))
  ListOfDate label Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [ ]
  [foobar]
  Date label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  Date label *
  <BLANKLINE>
  [ ]
  [6/21/14]
  [Add]
  [Remove selected]

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_date.2.remove'] = '1'
  >>> submit['form.widgets.list_of_date.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-list_of_date"]'))
  ListOfDate label
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [ ]
  [foobar]
  Date label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetListIntegration
    list_of_bool: [True, False, True]
    list_of_choice: ['two', 'three']
    list_of_date: [datetime.date(2014, 6, 20)]
    list_of_int: [-100, 1, 100]
    list_of_textline: ['some text one', 'some txt two']>


And apply

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  There were some errors.* ListOfInt label: Wrong contained type
  * ListOfTextLine label: Constraint not satisfied
  * ListOfDate label: The datetime string did not match the pattern 'M/d/yy'...
  ...

  >>> pprint(obj)
  <MultiWidgetListIntegration
    list_of_bool: [True, False, True]
    list_of_choice: ['two', 'three']
    list_of_date: [datetime.date(2014, 6, 20)]
    list_of_int: [-100, 1, 100]
    list_of_textline: ['some text one', 'some txt two']>

Let's fix the values

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_int.1'] = '42'
  >>> submit['form.widgets.list_of_bool.1'] = 'false'
  >>> submit['form.widgets.list_of_textline.0'] = 'ipsum lorem'
  >>> submit['form.widgets.list_of_textline.1'] = 'lorem ipsum'
  >>> submit['form.widgets.list_of_date.0'] = '6/25/14'
  >>> submit['form.widgets.list_of_date.1'] = '6/24/14'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated...
  ...

  >>> pprint(obj)
  <MultiWidgetListIntegration
    list_of_bool: [True, False]
    list_of_choice: ['two', 'three']
    list_of_date: [datetime.date(2014, 6, 25), datetime.date(2014, 6, 24)]
    list_of_int: [-100, 42]
    list_of_textline: ['ipsum lorem', 'lorem ipsum']>


Tests cleanup:

  >>> tearDown()
