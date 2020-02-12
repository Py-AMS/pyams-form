ObjectWidget single widgets integration tests
---------------------------------------------

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

  >>> from pyams_utils.testing import format_html
  >>> from pyams_layer.interfaces import IFormLayer

  >>> from pyams_form import util, testing
  >>> testing.setup_form_defaults(config.registry)

Checking components on the highest possible level.

  >>> from datetime import date
  >>> from pyams_form import form
  >>> from pyams_form import field
  >>> from pyams_form import testing

  >>> from pyams_form.object import register_factory_adapter
  >>> register_factory_adapter(testing.IObjectWidgetSingleSubIntegration,
  ...     testing.ObjectWidgetSingleSubIntegration)

  >>> request = testing.TestRequest()

  >>> from pyams_form.object import register_factory_adapter
  >>> register_factory_adapter(testing.IObjectWidgetSingleSubIntegration,
  ...     testing.ObjectWidgetSingleSubIntegration)


  >>> class EForm(form.EditForm):
  ...     form.extends(form.EditForm)
  ...     fields = field.Fields(testing.IObjectWidgetSingleIntegration)

Our single content object:

  >>> obj = testing.ObjectWidgetSingleIntegration()

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
  Object label
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
  ReadOnly label *
  []
  [Apply]

Some valid default values
#########################

  >>> obj.subobj = testing.ObjectWidgetSingleSubIntegration(
  ...     singleInt=-100,
  ...     singleBool=False,
  ...     singleChoice='two',
  ...     singleChoiceOpt='six',
  ...     singleTextLine='some text one',
  ...     singleDate=date(2014, 6, 20),
  ...     singleReadOnly='some R/O text')

  >>> content = getForm(request)

  >>> print(testing.plain_text(content))
  Object label Int label *
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
  ReadOnly label *
  some R/O text
  [Apply]


Wrong values
############

Set wrong values:

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.subobj.widgets.singleInt'] = 'foobar'
  >>> submit['form.widgets.subobj.widgets.singleChoice:list'] = 'two'
  >>> submit['form.widgets.subobj.widgets.singleTextLine'] = 'foo\nbar'
  >>> submit['form.widgets.subobj.widgets.singleDate'] = 'foobar'

  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

We should get lots of errors:

  >>> content = getForm(request)
  >>> print(testing.plain_text(content,
  ...       './/ul[@id="form-errors"]'))
  * Object label: The entered value is not a valid integer literal.
  <BLANKLINE>
  Constraint not satisfied
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.

  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-subobj"]/b/div[@class="error"]'))
  The entered value is not a valid integer literal.
  <BLANKLINE>
  Constraint not satisfied
  <BLANKLINE>
  The datetime string did not match the pattern 'M/d/yy'.

  >>> print(testing.plain_text(content,
  ...     './/div[@id="row-form-widgets-subobj"]'))
  The entered value is not a valid integer literal.
  Constraint not satisfied
  The datetime string did not match the pattern 'M/d/yy'.
  Object label Int label *
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
  ReadOnly label *
  some R/O text

Let's fix the values:

  >>> submit = testing.get_submit_values(content)

  >>> submit['form.widgets.subobj.widgets.singleInt'] = '1042'
  >>> submit['form.widgets.subobj.widgets.singleBool'] = 'true'
  >>> submit['form.widgets.subobj.widgets.singleChoice:list'] = 'three'
  >>> submit['form.widgets.subobj.widgets.singleChoiceOpt:list'] = 'four'
  >>> submit['form.widgets.subobj.widgets.singleTextLine'] = 'foobar'
  >>> submit['form.widgets.subobj.widgets.singleDate'] = '6/14/21'

  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated.Object label Int label *
  [1,042]
  Bool label *
  (O) yes ( ) no
  Choice label *
  [three]
  ChoiceOpt label
  [four]
  TextLine label *
  [foobar]
  Date label *
  [6/14/21]
  ReadOnly label *
  some R/O text
  [Apply]


Bool was misbehaving

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.subobj.widgets.singleBool'] = 'false'
  >>> submit['form.widgets.subobj.widgets.singleChoice'] = 'three'
  >>> submit['form.widgets.subobj.widgets.singleChoiceOpt'] = 'four'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated...
  ...

  >>> from pprint import pprint
  >>> pprint(obj.subobj)
  <ObjectWidgetSingleSubIntegration
    singleBool: False
    singleChoice: 'three'
    singleChoiceOpt: 'four'
    singleDate: datetime.date(2021, 6, 14)
    singleInt: 1042
    singleReadOnly: 'some R/O text'
    singleTextLine: 'foobar'>

  >>> submit = testing.get_submit_values(content)
  >>> submit['form.widgets.subobj.widgets.singleBool'] = 'true'
  >>> submit['form.widgets.subobj.widgets.singleChoice'] = 'three'
  >>> submit['form.widgets.subobj.widgets.singleChoiceOpt'] = 'four'
  >>> submit['form.buttons.apply'] = 'Apply'

  >>> request = testing.TestRequest(params=submit)

  >>> content = getForm(request)
  >>> print(testing.plain_text(content))
  Data successfully updated...
  ...

  >>> pprint(obj.subobj)
  <ObjectWidgetSingleSubIntegration
    singleBool: True
    singleChoice: 'three'
    singleChoiceOpt: 'four'
    singleDate: datetime.date(2021, 6, 14)
    singleInt: 1042
    singleReadOnly: 'some R/O text'
    singleTextLine: 'foobar'>


Tests cleanup:

  >>> tearDown()
