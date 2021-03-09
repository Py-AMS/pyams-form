TextLines Widget
----------------

The text lines widget allows you to store a sequence of textline. This sequence
is stored as a list or tuple. This depends on what you are using as sequence
type.

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

As for all widgets, the text lines widget must provide the new ``IWidget``
interface:

  >>> from pyams_utils.testing import format_html
  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import textlines

  >>> interfaces.widget.IWidget.implementedBy(textlines.TextLinesWidget)
  True

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = textlines.TextLinesWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'id'
  >>> widget.name = 'name'

If we render the widget we get an empty textarea widget:

  >>> print(widget.render())
  <textarea id="id"
            name="name"
            class="textarea-widget"></textarea>

Adding some more attributes to the widget will make it display more:

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = 'foo\nbar'

  >>> print(widget.render())
  <textarea id="id"
            name="name"
            class="textarea-widget">foo
  bar</textarea>


TextLinesFieldWidget
####################

The field widget needs a field:

  >>> import zope.schema
  >>> text = zope.schema.List(
  ...     title='List',
  ...     value_type=zope.schema.TextLine())

  >>> widget = textlines.TextLinesFieldWidget(text, request)
  >>> widget
  <TextLinesWidget ''>

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = 'foo\nbar'

  >>> print(widget.render())
  <textarea id="id" name="name" class="textarea-widget">foo
  bar</textarea>


TextLinesFieldWidgetFactory
###########################

  >>> widget = textlines.TextLinesFieldWidgetFactory(text, text.value_type,
  ...     request)
  >>> widget
  <TextLinesWidget ''>

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = 'foo\nbar'

  >>> print(widget.render())
  <textarea id="id" name="name" class="textarea-widget">foo
  bar</textarea>


Tests cleanup:

  >>> tearDown()
