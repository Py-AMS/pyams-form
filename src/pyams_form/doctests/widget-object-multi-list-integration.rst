ObjectWidget integration with MultiWidget of list
-------------------------------------------------

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

a.k.a. list of objects widget

  >>> from datetime import date
  >>> from pyams_form import form
  >>> from pyams_form import field
  >>> from pyams_form import testing

  >>> from pyams_form.object import register_factory_adapter
  >>> register_factory_adapter(testing.IObjectWidgetMultiSubIntegration,
  ...     testing.ObjectWidgetMultiSubIntegration)

  >>> request = testing.TestRequest()

  >>> class EForm(form.EditForm):
  ...     form.extends(form.EditForm)
  ...     fields = field.Fields(
  ...         testing.IMultiWidgetListIntegration).select('list_of_objects')

Our multi content object:

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
  ListOfObject label
  <BLANKLINE>
  [Add]
  [Apply]

Some valid default values
#########################

  >>> sub1 = testing.ObjectWidgetMultiSubIntegration(
  ...     multi_int=-100,
  ...     multi_bool=False,
  ...     multi_choice='two',
  ...     multi_choice_opt='six',
  ...     multi_textline='some text one',
  ...     multi_date=date(2014, 6, 20))

  >>> sub2 = testing.ObjectWidgetMultiSubIntegration(
  ...     multi_int=42,
  ...     multi_bool=True,
  ...     multi_choice='one',
  ...     multi_choice_opt='four',
  ...     multi_textline='second txt',
  ...     multi_date=date(2011, 3, 15))

  >>> obj.list_of_objects = [sub1, sub2]

  >>> from pprint import pprint
  >>> pprint(obj.list_of_objects)
  [<ObjectWidgetMultiSubIntegration
    multi_bool: False
    multi_choice: 'two'
    multi_choice_opt: 'six'
    multi_date: datetime.date(2014, 6, 20)
    multi_int: -100
    multi_textline: 'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multi_bool: True
    multi_choice: 'one'
    multi_choice_opt: 'four'
    multi_date: datetime.date(2011, 3, 15)
    multi_int: 42
    multi_textline: 'second txt'>]

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  ListOfObject label Object label *
  [ ]
  Int label *
  [-100]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [some text one]
  Date label *
  [6/20/14]
  Object label *
  [ ]
  Int label *
  [42]
  Bool label
  (O) yes ( ) no
  Choice label *
  [one]
  ChoiceOpt label
  [four]
  TextLine label *
  [second txt]
  Date label *
  [3/15/11]
  [Add] [Remove selected]
  [Apply]

wrong input (Int)
#################

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.0.widgets.multi_int'] = 'foobar'

  >>> submit['form.widgets.list_of_objects.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...       './/div[@id="form-widgets-list_of_objects-0-row"]'))
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [some text one]
  Date label *
  [6/20/14]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...       './/div[@id="form-widgets-list_of_objects-0-row"]//div[@class="error"]'))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.

  >>> print(testing.plain_text(content,
  ...       './/div[@id="form-widgets-list_of_objects-1-row"]//div[@class="error"]'))

  >>> print(testing.plain_text(content,
  ...       './/div[@id="form-widgets-list_of_objects-2-row"]'))
  Object label *
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label
  ( ) yes ( ) no
  Choice label *
  [one]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  Required input is missing.
  []

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.1.remove'] = '1'
  >>> submit['form.widgets.list_of_objects.2.remove'] = '1'
  >>> submit['form.widgets.list_of_objects.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  ListOfObject label Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [some text one]
  Date label *
  [6/20/14]
  [Add]
  [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.list_of_objects)
  [<ObjectWidgetMultiSubIntegration
    multi_bool: False
    multi_choice: 'two'
    multi_choice_opt: 'six'
    multi_date: datetime.date(2014, 6, 20)
    multi_int: -100
    multi_textline: 'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multi_bool: True
    multi_choice: 'one'
    multi_choice_opt: 'four'
    multi_date: datetime.date(2011, 3, 15)
    multi_int: 42
    multi_textline: 'second txt'>]


wrong input (TextLine)
######################

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.0.widgets.multi_textline'] = 'foo\nbar'

  >>> submit['form.widgets.list_of_objects.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "Constraint not satisfied"
for "foo\nbar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="form-widgets-list_of_objects-0-row"]'))
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  [6/20/14]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="form-widgets-list_of_objects-0-row"]//div[@class="error"]'))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.
  Constraint not satisfied

  >>> print(format_html(testing.plain_text(content,
  ...     './/div[@id="form-widgets-list_of_objects-1-row"]//div[@class="error"]')))
  Required input is missing.
  Required input is missing.
  Required input is missing.

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.1.remove'] = '1'
  >>> submit['form.widgets.list_of_objects.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  ListOfObject label Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  [6/20/14]
  [Add] [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.list_of_objects)
  [<ObjectWidgetMultiSubIntegration
    multi_bool: False
    multi_choice: 'two'
    multi_choice_opt: 'six'
    multi_date: datetime.date(2014, 6, 20)
    multi_int: -100
    multi_textline: 'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multi_bool: True
    multi_choice: 'one'
    multi_choice_opt: 'four'
    multi_date: datetime.date(2011, 3, 15)
    multi_int: 42
    multi_textline: 'second txt'>]


wrong input (Date)
##################

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.0.widgets.multi_date'] = 'foobar'

  >>> submit['form.widgets.list_of_objects.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "The datetime string did not match the pattern"
for "foobar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  ListOfObject label Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  The datetime string did not match the pattern 'M/d/yy'.
  [foobar]
  Object label *
  [ ]
  Int label *
  []
  Bool label
  ( ) yes ( ) no
  Choice label *
  [[    ]]
  ChoiceOpt label
  [No value]
  TextLine label *
  []
  Date label *
  []
  [Add] [Remove selected]
  [Apply]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(format_html(testing.plain_text(content,
  ...     './/div[@id="form-widgets-list_of_objects-0-row"]//div[@class="error"]')))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.
  Constraint not satisfied
  The datetime string did not match the pattern 'M/d/yy'.

Add one more field:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.buttons.add'] = 'Add'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)

And fill in a valid value:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.2.widgets.multi_date'] = '6/14/21'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  ListOfObject label Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  The datetime string did not match the pattern 'M/d/yy'.
  [foobar]
  Object label *
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label
  ( ) yes ( ) no
  Choice label *
  [one]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  Required input is missing.
  []
  Object label *
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label
  ( ) yes ( ) no
  Choice label *
  [one]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  [6/14/21]
  [Add] [Remove selected]
  [Apply]

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.2.remove'] = '1'
  >>> submit['form.widgets.list_of_objects.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  ListOfObject label Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  Constraint not satisfied
  [foo
  bar]
  Date label *
  The datetime string did not match the pattern 'M/d/yy'.
  [foobar]
  Object label *
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label
  ( ) yes ( ) no
  Choice label *
  [one]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  Required input is missing.
  []
  [Add] [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.list_of_objects)
  [<ObjectWidgetMultiSubIntegration
    multi_bool: False
    multi_choice: 'two'
    multi_choice_opt: 'six'
    multi_date: datetime.date(2014, 6, 20)
    multi_int: -100
    multi_textline: 'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multi_bool: True
    multi_choice: 'one'
    multi_choice_opt: 'four'
    multi_date: datetime.date(2011, 3, 15)
    multi_int: 42
    multi_textline: 'second txt'>]

Fix values
##########

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.0.widgets.multi_int'] = '1042'
  >>> submit['form.widgets.list_of_objects.0.widgets.multi_textline'] = 'moo900'
  >>> submit['form.widgets.list_of_objects.0.widgets.multi_date'] = '6/14/23'

  >>> submit['form.widgets.list_of_objects.1.remove'] = '1'
  >>> submit['form.widgets.list_of_objects.buttons.remove'] = 'Remove selected'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  ListOfObject label Object label *
  [ ]
  Int label *
  [1,042]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [moo900]
  Date label *
  [6/14/23]
  [Add] [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.list_of_objects)
  [<ObjectWidgetMultiSubIntegration
    multi_bool: False
    multi_choice: 'two'
    multi_choice_opt: 'six'
    multi_date: datetime.date(2014, 6, 20)
    multi_int: -100
    multi_textline: 'some text one'>,
   <ObjectWidgetMultiSubIntegration
    multi_bool: True
    multi_choice: 'one'
    multi_choice_opt: 'four'
    multi_date: datetime.date(2011, 3, 15)
    multi_int: 42
    multi_textline: 'second txt'>]

And apply

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated.ListOfObject label Object label *
  [ ]
  Int label *
  [1,042]
  Bool label
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [moo900]
  Date label *
  [6/14/23]
  [Add] [Remove selected]
  [Apply]

Now the object gets updated:

  >>> pprint(obj.list_of_objects)
  [<ObjectWidgetMultiSubIntegration
    multi_bool: False
    multi_choice: 'two'
    multi_choice_opt: 'six'
    multi_date: datetime.date(2023, 6, 14)
    multi_int: 1042
    multi_textline: 'moo900'>]


Bool was misbehaving
####################

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.0.widgets.multi_bool'] = 'true'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated...
  ...

  >>> pprint(obj.list_of_objects)
  [<ObjectWidgetMultiSubIntegration
    multi_bool: True
    multi_choice: 'two'
    multi_choice_opt: 'six'
    multi_date: datetime.date(2023, 6, 14)
    multi_int: 1042
    multi_textline: 'moo900'>]


  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.list_of_objects.0.widgets.multi_bool'] = 'false'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated...
  ...

  >>> pprint(obj.list_of_objects)
  [<ObjectWidgetMultiSubIntegration
    multi_bool: False
    multi_choice: 'two'
    multi_choice_opt: 'six'
    multi_date: datetime.date(2023, 6, 14)
    multi_int: 1042
    multi_textline: 'moo900'>]


Tests cleanup:

  >>> tearDown()
