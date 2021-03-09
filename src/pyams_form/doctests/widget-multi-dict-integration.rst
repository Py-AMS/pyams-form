MultiWidget Dict integration tests
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

Checking components on the highest possible level.

  >>> from datetime import date
  >>> from pyams_form import form
  >>> from pyams_form import field
  >>> from pyams_form import testing

  >>> request = testing.TestRequest()

  >>> class EForm(form.EditForm):
  ...     form.extends(form.EditForm)
  ...     fields = field.Fields(
  ...         testing.IMultiWidgetDictIntegration).omit('dict_of_objects')

Our single content object:

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
  DictOfInt label
  <BLANKLINE>
  [Add]
  DictOfBool label
  <BLANKLINE>
  [Add]
  DictOfChoice label
  <BLANKLINE>
  [Add]
  DictOfTextLine label
  <BLANKLINE>
  [Add]
  DictOfDate label
  <BLANKLINE>
  [Add]
  [Apply]

Some valid default values
#########################

  >>> obj.dict_of_int = {-101: -100, -1:1, 101:100}
  >>> obj.dict_of_bool = {True: False, False: True}
  >>> obj.dict_of_choice = {'key1': 'three', 'key3': 'two'}
  >>> obj.dict_of_textline = {'textkey1': 'some text one',
  ...     'textkey2': 'some txt two'}
  >>> obj.dict_of_date = {
  ...     date(2011, 1, 15): date(2014, 6, 20),
  ...     date(2012, 2, 20): date(2013, 5, 19)}

  >>> from pprint import pprint
  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: True, True: False}
    dict_of_choice: {'key1': 'three', 'key3': 'two'}
    dict_of_date: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dict_of_int: {-101: -100, -1: 1, 101: 100}
    dict_of_textline: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>

  >>> content = getForm(request)

  >>> print(testing.plain_text(content))
  DictOfInt label Int key *
  [-1]
  Int label *
  [ ]
  [1]
  Int key *
  [-101]
  Int label *
  [ ]
  [-100]
  Int key *
  [101]
  Int label *
  [ ]
  [100]
  [Add] [Remove selected]
  DictOfBool label Bool key
  ( ) yes (O) no
  Bool label
  [ ]
  (O) yes ( ) no
  Bool key
  (O) yes ( ) no
  Bool label
  [ ]
  ( ) yes (O) no
  [Add] [Remove selected]
  DictOfChoice label Choice key *
  [key1]
  Choice label *
  [ ]
  [three]
  Choice key *
  [key3]
  Choice label *
  [ ]
  [two]
  [Add] [Remove selected]
  DictOfTextLine label TextLine key *
  [textkey1]
  TextLine label *
  [ ]
  [some text one]
  TextLine key *
  [textkey2]
  TextLine label *
  [ ]
  [some txt two]
  [Add] [Remove selected]
  DictOfDate label Date key *
  [1/15/11]
  Date label *
  [ ]
  [6/20/14]
  Date key *
  [2/20/12]
  Date label *
  [ ]
  [5/19/13]
  [Add] [Remove selected]
  [Apply]

dict_of_int
#########

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_int.key.2'] = 'foobar'
  >>> submit['form.widgets.dict_of_int.2'] = 'foobar'

  >>> submit['form.widgets.dict_of_int.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_int"]'))
  DictOfInt label
  <BLANKLINE>
  Int key *
  <BLANKLINE>
  [-1]
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  [1]
  Int key *
  <BLANKLINE>
  [-101]
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  [-100]
  Int key *
  <BLANKLINE>
  The entered value is not a valid integer literal.
  [foobar]
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  The entered value is not a valid integer literal.
  [ ]
  [foobar]
  Int key *
  <BLANKLINE>
  []
  <BLANKLINE>
  Int label *
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
  ...     './/div[@id="row-form-widgets-dict_of_int"]//div[@class="error"]'))
  Required input is missing.
  Required input is missing.
  The entered value is not a valid integer literal.
  The entered value is not a valid integer literal.

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_int.1.remove'] = '1'
  >>> submit['form.widgets.dict_of_int.3.remove'] = '1'
  >>> submit['form.widgets.dict_of_int.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_int"]'))
  DictOfInt label
  <BLANKLINE>
  Int key *
  <BLANKLINE>
  Required input is missing.
  []
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  Int key *
  <BLANKLINE>
  [-101]
  <BLANKLINE>
  Int label *
  <BLANKLINE>
  [ ]
  [-100]
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: True, True: False}
    dict_of_choice: {'key1': 'three', 'key3': 'two'}
    dict_of_date: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dict_of_int: {-101: -100, -1: 1, 101: 100}
    dict_of_textline: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>


dict_of_bool
##########

Add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_bool.buttons.add'] = 'Add'
  >>> request = testing.TestRequest(params=submit)

Important is that we get a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_bool"]'))
  DictOfBool label Bool key
  ( ) yes (O) no
  Bool label
  [ ]
  (O) yes ( ) no
  Bool key
  (O) yes ( ) no
  Bool label
  [ ]
  ( ) yes (O) no
  Bool key
  ( ) yes ( ) no
  Bool label
  [ ]
  ( ) yes ( ) no
  [Add] [Remove selected]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_bool"]//div[@class="error"]'))
  <BLANKLINE>

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_bool.1.remove'] = '1'
  >>> submit['form.widgets.dict_of_bool.2.remove'] = '1'
  >>> submit['form.widgets.dict_of_bool.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_bool"]'))
  DictOfBool label Bool key
  ( ) yes ( ) no
  Bool label
  [ ]
  ( ) yes ( ) no
  [Add] [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: True, True: False}
    dict_of_choice: {'key1': 'three', 'key3': 'two'}
    dict_of_date: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dict_of_int: {-101: -100, -1: 1, 101: 100}
    dict_of_textline: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>


dict_of_choice
############

Add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_choice.buttons.add'] = 'Add'
  >>> request = testing.TestRequest(params=submit)

Important is that we get a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_choice"]'))
  DictOfChoice label
  <BLANKLINE>
  Choice key *
  <BLANKLINE>
  [key1]
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [ ]
  [three]
  Choice key *
  <BLANKLINE>
  [key3]
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [ ]
  [two]
  Choice key *
  <BLANKLINE>
  [[    ]]
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [ ]
  [[    ]]
  [Add]
  [Remove selected]

Submit again with the empty field:

  >>> submit = testing.get_submit_values(content)
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_choice"]//div[@class="error"]'))
  Duplicate key

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_choice.0.remove'] = '1'
  >>> submit['form.widgets.dict_of_choice.1.remove'] = '1'
  >>> submit['form.widgets.dict_of_choice.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_choice"]'))
  DictOfChoice label
  <BLANKLINE>
  Choice key *
  <BLANKLINE>
  [key3]
  <BLANKLINE>
  Choice label *
  <BLANKLINE>
  [ ]
  [two]
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: True, True: False}
    dict_of_choice: {'key1': 'three', 'key3': 'two'}
    dict_of_date: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dict_of_int: {-101: -100, -1: 1, 101: 100}
    dict_of_textline: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>


dict_of_textline
##############

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_textline.key.0'] = 'foo\nbar'
  >>> submit['form.widgets.dict_of_textline.0'] = 'foo\nbar'

  >>> submit['form.widgets.dict_of_textline.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "Constraint not satisfied"
for "foo\nbar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_textline"]'))
  DictOfTextLine label
  <BLANKLINE>
  TextLine key *
  <BLANKLINE>
  Constraint not satisfied
  [foo
  bar]
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [ ]
  [foo
  bar]
  TextLine key *
  <BLANKLINE>
  [textkey2]
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  [ ]
  [some txt two]
  TextLine key *
  <BLANKLINE>
  []
  <BLANKLINE>
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
  ...     './/div[@id="row-form-widgets-dict_of_textline"]//div[@class="error"]'))
  Required input is missing.
  Required input is missing.
  Constraint not satisfied
  Constraint not satisfied

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_textline.2.remove'] = '1'
  >>> submit['form.widgets.dict_of_textline.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_textline"]'))
  DictOfTextLine label
  <BLANKLINE>
  TextLine key *
  <BLANKLINE>
  Required input is missing.
  []
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Required input is missing.
  [ ]
  []
  TextLine key *
  <BLANKLINE>
  Constraint not satisfied
  [foo
  bar]
  <BLANKLINE>
  TextLine label *
  <BLANKLINE>
  Constraint not satisfied
  [ ]
  [foo
  bar]
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: True, True: False}
    dict_of_choice: {'key1': 'three', 'key3': 'two'}
    dict_of_date: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dict_of_int: {-101: -100, -1: 1, 101: 100}
    dict_of_textline: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>


dict_of_date
##########

Set a wrong value and add a new input:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_date.key.0'] = 'foobar'
  >>> submit['form.widgets.dict_of_date.0'] = 'foobar'

  >>> submit['form.widgets.dict_of_date.buttons.add'] = 'Add'

  >>> request = testing.TestRequest(params=submit)

Important is that we get "The entered value is not a valid integer literal."
for "foobar" and a new input.

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_date"]'))
  DictOfDate label
  <BLANKLINE>
  Date key *
  <BLANKLINE>
  [2/20/12]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  [5/19/13]
  Date key *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [foobar]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [ ]
  [foobar]
  Date key *
  <BLANKLINE>
  []
  <BLANKLINE>
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
  ...     './/div[@id="row-form-widgets-dict_of_date"]//div[@class="error"]'))
  Required input is missing.
  Required input is missing.
  The datetime string did not match the pattern 'M/d/yy'.
  The datetime string did not match the pattern 'M/d/yy'.

And fill in a valid value:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_date.key.0'] = '5/12/14'
  >>> submit['form.widgets.dict_of_date.0'] = '6/21/14'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_date"]'))
  DictOfDate label
  <BLANKLINE>
  Date key *
  <BLANKLINE>
  [2/20/12]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  [5/19/13]
  Date key *
  <BLANKLINE>
  [5/12/14]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  [6/21/14]
  Date key *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [foobar]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [ ]
  [foobar]
  [Add]
  [Remove selected]

Let's remove some items:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_date.1.remove'] = '1'
  >>> submit['form.widgets.dict_of_date.buttons.remove'] = 'Remove selected'
  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-dict_of_date"]'))
  DictOfDate label
  <BLANKLINE>
  Date key *
  <BLANKLINE>
  [2/20/12]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  [ ]
  [5/19/13]
  Date key *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [foobar]
  <BLANKLINE>
  Date label *
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.
  [ ]
  [foobar]
  [Add]
  [Remove selected]

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: True, True: False}
    dict_of_choice: {'key1': 'three', 'key3': 'two'}
    dict_of_date: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dict_of_int: {-101: -100, -1: 1, 101: 100}
    dict_of_textline: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>

And apply

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  There were some errors.* DictOfInt label: Wrong contained type
  * DictOfTextLine label: Constraint not satisfied
  * DictOfDate label: The datetime string did not match the pattern 'M/d/yy'...
  ...

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: True, True: False}
    dict_of_choice: {'key1': 'three', 'key3': 'two'}
    dict_of_date: {datetime.date(2011, 1, 15): datetime.date(2014, 6, 20),
   datetime.date(2012, 2, 20): datetime.date(2013, 5, 19)}
    dict_of_int: {-101: -100, -1: 1, 101: 100}
    dict_of_textline: {'textkey1': 'some text one', 'textkey2': 'some txt two'}>

Let's fix the values

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_int.key.1'] = '42'
  >>> submit['form.widgets.dict_of_int.1'] = '43'
  >>> submit['form.widgets.dict_of_textline.0.remove'] = '1'
  >>> submit['form.widgets.dict_of_textline.buttons.remove'] = 'Remove selected'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_textline.key.0'] = 'lorem ipsum'
  >>> submit['form.widgets.dict_of_textline.0'] = 'ipsum lorem'
  >>> submit['form.widgets.dict_of_date.key.1'] = '6/25/14'
  >>> submit['form.widgets.dict_of_date.1'] = '7/28/14'
  >>> submit['form.widgets.dict_of_int.key.0'] = '-101'
  >>> submit['form.widgets.dict_of_int.0'] = '-100'
  >>> submit['form.widgets.dict_of_bool.key.0'] = 'false'
  >>> submit['form.widgets.dict_of_bool.0'] = 'true'

  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)
  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated...
  ...

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: True}
    dict_of_choice: {'key3': 'two'}
    dict_of_date: {datetime.date(2012, 2, 20): datetime.date(2013, 5, 19),
   datetime.date(2014, 6, 25): datetime.date(2014, 7, 28)}
    dict_of_int: {-101: -100, 42: 43}
    dict_of_textline: {'lorem ipsum': 'ipsum lorem'}>

Twisting some keys
##################

Change key values, item values must stick to the new values.

  >>> obj.dict_of_int = {-101: -100, -1:1, 101:100}
  >>> obj.dict_of_bool = {True: False, False: True}
  >>> obj.dict_of_choice = {'key1': 'three', 'key3': 'two'}
  >>> obj.dict_of_textline = {'textkey1': 'some text one',
  ...     'textkey2': 'some txt two'}
  >>> obj.dict_of_date = {
  ...     date(2011, 1, 15): date(2014, 6, 20),
  ...     date(2012, 2, 20): date(2013, 5, 19)}

  >>> request = testing.TestRequest()
  >>> content = getForm(request)

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.dict_of_int.key.2'] = '42'  # was 101:100
  >>> submit['form.widgets.dict_of_bool.key.0'] = 'true'  # was False:True
  >>> submit['form.widgets.dict_of_bool.key.1'] = 'false'  # was True:False
  >>> submit['form.widgets.dict_of_choice.key.1'] = 'key2'  # was key3: two
  >>> submit['form.widgets.dict_of_choice.key.0'] = 'key3'  # was key1: three
  >>> submit['form.widgets.dict_of_textline.key.1'] = 'lorem'  # was textkey2: some txt two
  >>> submit['form.widgets.dict_of_textline.1'] = 'ipsum'  # was textkey2: some txt two
  >>> submit['form.widgets.dict_of_textline.key.0'] = 'foobar'  # was textkey1: some txt one
  >>> submit['form.widgets.dict_of_date.key.0'] = '6/25/14'  # 11/01/15: 14/06/20

  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

  >>> content = getForm(request)

  >>> submit = testing.get_submit_values(content)

  >>> pprint(obj)
  <MultiWidgetDictIntegration
    dict_of_bool: {False: False, True: True}
    dict_of_choice: {'key2': 'two', 'key3': 'three'}
    dict_of_date: {datetime.date(2012, 2, 20): datetime.date(2013, 5, 19),
   datetime.date(2014, 6, 25): datetime.date(2014, 6, 20)}
    dict_of_int: {-101: -100, -1: 1, 42: 100}
    dict_of_textline: {'foobar': 'some text one', 'lorem': 'ipsum'}>


Tests cleanup:

  >>> tearDown()
