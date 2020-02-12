ObjectWidget integration with MultiWidget of dict
-------------------------------------------------

  >>> from pyramid.testing import setUp, tearDown
  >>> config = setUp()

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

a.k.a. dict of objects widget

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
  ...         testing.IMultiWidgetDictIntegration).select('dictOfObject')

Our multi content object:

  >>> obj = testing.MultiWidgetDictIntegration()

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
  DictOfObject label
  <BLANKLINE>
  [Add]
  [Apply]

Some valid default values
#########################

  >>> sub1 = testing.ObjectWidgetMultiSubIntegration(
  ...     multiInt=-100,
  ...     multiBool=False,
  ...     multiChoice='two',
  ...     multiChoiceOpt='six',
  ...     multiTextLine='some text one',
  ...     multiDate=date(2014, 6, 20))

  >>> sub2 = testing.ObjectWidgetMultiSubIntegration(
  ...     multiInt=42,
  ...     multiBool=True,
  ...     multiChoice='one',
  ...     multiChoiceOpt='four',
  ...     multiTextLine='second txt',
  ...     multiDate=date(2011, 3, 15))

  >>> obj.dictOfObject = {'subob1': sub1, 'subob2': sub2}

  >>> from pprint import pprint
  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>,
   'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>}

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  DictOfObject label Object key *
  [subob1]
  Object label *
  [ ]
  Int label *
  [-100]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [some text one]
  Date label *
  [6/20/14]
  Object key *
  [subob2]
  Object label *
  [ ]
  Int label *
  [42]
  Bool label *
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
  >>> submit['form.widgets.dictOfObject.0.widgets.multiInt'] = 'foobar'

  >>> submit['form.widgets.dictOfObject.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request)
  >>> print(format_html(testing.plain_text(content,
  ...       './/div[@id="form-widgets-dictOfObject-0-row"]')))
  Object key *
  [subob1]
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
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
  >>> print(format_html(testing.plain_text(content,
  ...     './/div[@id="form-widgets-dictOfObject-0-row"]//div[@class="error"]')))
  Required input is missing.
  Required input is missing.
  Required input is missing.
  Required input is missing.
  Required input is missing.

  >>> print(format_html(testing.plain_text(content,
  ...     './/div[@id="form-widgets-dictOfObject-1-row"]//div[@class="error"]')))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.

  >>> print(format_html(testing.plain_text(content,
  ...     './/div[@id="form-widgets-dictOfObject-0-row"]')))
  Object key *
  Required input is missing.
  []
  Object label *
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label *
  Required input is missing.
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
  >>> submit['form.widgets.dictOfObject.0.remove'] = '1'
  >>> submit['form.widgets.dictOfObject.2.remove'] = '1'
  >>> submit['form.widgets.dictOfObject.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(format_html(testing.plain_text(content)))
  DictOfObject label Object key *
  [subob1]
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [some text one]
  Date label *
  [6/20/14]
  [Add] [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>,
   'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>}


wrong input (TextLine)
######################

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.0.widgets.multiTextLine'] = 'foo\nbar'

  >>> submit['form.widgets.dictOfObject.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "Constraint not satisfied"
for "foo\nbar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="form-widgets-dictOfObject-0-row"]'))
  Object key *
  [subob1]
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
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

  >>> print(format_html(testing.plain_text(content,
  ...     './/div[@id="form-widgets-dictOfObject-0-row"]//div[@class="error"]')))
  Required input is missing.
  Required input is missing.
  Required input is missing.
  Required input is missing.
  Required input is missing.

  >>> print(format_html(testing.plain_text(content,
  ...     './/div[@id="form-widgets-dictOfObject-1-row"]//div[@class="error"]')))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.
  Constraint not satisfied

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.0.remove'] = '1'
  >>> submit['form.widgets.dictOfObject.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(format_html(testing.plain_text(content)))
  DictOfObject label Object key *
  [subob1]
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
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

  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>,
   'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>}


wrong input (Date)
##################

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.0.widgets.multiDate'] = 'foobar'

  >>> submit['form.widgets.dictOfObject.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "The datetime string did not match the pattern"
for "foobar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  DictOfObject label Object key *
  [subob1]
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
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
  Object key *
  []
  Object label *
  [ ]
  Int label *
  []
  Bool label *
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
  ...     './/div[@id="form-widgets-dictOfObject-1-row"]//div[@class="error"]')))
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.
  Constraint not satisfied
  The datetime string did not match the pattern 'M/d/yy'.

Fill in a valid value:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.0.widgets.multiDate'] = '6/21/14'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  DictOfObject label Object key *
  Required input is missing.
  []
  Object label *
  [ ]
  Int label *
  Required input is missing.
  []
  Bool label *
  Required input is missing.
  ( ) yes ( ) no
  Choice label *
  [one]
  ChoiceOpt label
  [No value]
  TextLine label *
  Required input is missing.
  []
  Date label *
  [6/21/14]
  Object key *
  [subob1]
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
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
  [Add] [Remove selected]
  [Apply]

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.0.remove'] = '1'
  >>> submit['form.widgets.dictOfObject.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  DictOfObject label Object key *
  [subob1]
  Object label *
  The entered value is not a valid integer literal.
  [ ]
  Int label *
  The entered value is not a valid integer literal.
  [foobar]
  Bool label *
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
  [Add] [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>,
   'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>}

Fix values
##########

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.0.widgets.multiInt'] = '1042'
  >>> submit['form.widgets.dictOfObject.0.widgets.multiTextLine'] = 'moo900'
  >>> submit['form.widgets.dictOfObject.0.widgets.multiDate'] = '6/23/14'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  DictOfObject label Object key *
  [subob1]
  Object label *
  [ ]
  Int label *
  [1,042]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [moo900]
  Date label *
  [6/23/14]
  [Add] [Remove selected]
  [Apply]

The object is unchanged:

  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>,
   'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>}

And apply

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated.DictOfObject label Object key *
  [subob1]
  Object label *
  [ ]
  Int label *
  [1,042]
  Bool label *
  ( ) yes (O) no
  Choice label *
  [two]
  ChoiceOpt label
  [six]
  TextLine label *
  [moo900]
  Date label *
  [6/23/14]
  [Add] [Remove selected]
  [Apply]

Now the object gets updated:

  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 23)
    multiInt: 1042
    multiTextLine: 'moo900'>}


Twisting some keys
##################

Change key values, item values must stick to the new values.

  >>> sub1 = testing.ObjectWidgetMultiSubIntegration(
  ...     multiInt=-100,
  ...     multiBool=False,
  ...     multiChoice='two',
  ...     multiChoiceOpt='six',
  ...     multiTextLine='some text one',
  ...     multiDate=date(2014, 6, 20))

  >>> sub2 = testing.ObjectWidgetMultiSubIntegration(
  ...     multiInt=42,
  ...     multiBool=True,
  ...     multiChoice='one',
  ...     multiChoiceOpt='four',
  ...     multiTextLine='second txt',
  ...     multiDate=date(2011, 3, 15))

  >>> obj.dictOfObject = {'subob1': sub1, 'subob2': sub2}

  >>> request = testing.TestRequest()
  >>> content = getForm(request)

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.key.0'] = 'twisted'  # was subob1

  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

  >>> content = getForm(request)

  >>> pprint(obj.dictOfObject)
  {'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>,
   'twisted': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>}


  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.key.1'] = 'subob2'  # was twisted
  >>> submit['form.widgets.dictOfObject.key.0'] = 'subob1'  # was subob2

  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

  >>> content = getForm(request)

  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>,
   'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>}

Bool was misbehaving
####################

  >>> sub1 = testing.ObjectWidgetMultiSubIntegration(
  ...     multiInt=-100,
  ...     multiBool=False,
  ...     multiChoice='two',
  ...     multiChoiceOpt='six',
  ...     multiTextLine='some text one',
  ...     multiDate=date(2014, 6, 20))

  >>> sub2 = testing.ObjectWidgetMultiSubIntegration(
  ...     multiInt=42,
  ...     multiBool=True,
  ...     multiChoice='one',
  ...     multiChoiceOpt='four',
  ...     multiTextLine='second txt',
  ...     multiDate=date(2011, 3, 15))

  >>> obj.dictOfObject = {'subob1': sub1, 'subob2': sub2}

  >>> request = testing.TestRequest()
  >>> content = getForm(request)

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.0.widgets.multiBool'] = 'true'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated...
  ...

  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>,
   'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>}


  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dictOfObject.0.widgets.multiBool'] = 'false'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated...
  ...

  >>> pprint(obj.dictOfObject)
  {'subob1': <ObjectWidgetMultiSubIntegration
    multiBool: False
    multiChoice: 'two'
    multiChoiceOpt: 'six'
    multiDate: datetime.date(2014, 6, 20)
    multiInt: -100
    multiTextLine: 'some text one'>,
   'subob2': <ObjectWidgetMultiSubIntegration
    multiBool: True
    multiChoice: 'one'
    multiChoiceOpt: 'four'
    multiDate: datetime.date(2011, 3, 15)
    multiInt: 42
    multiTextLine: 'second txt'>}


Tests cleanup:

  >>> tearDown()
