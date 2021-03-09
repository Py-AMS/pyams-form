Text Widget
-----------

The widget can render a input field for a text line:

  >>> from pyramid.testing import setUp, tearDown
  >>> config = setUp(hook_zca=True)

  >>> from cornice import includeme as include_cornice
  >>> include_cornice(config)
  >>> from pyams_utils import includeme as include_utils
  >>> include_utils(config)
  >>> from pyams_template import includeme as include_template
  >>> include_template(config)
  >>> from pyams_form import includeme as include_form
  >>> include_form(config)

  >>> from pyams_form import testing
  >>> testing.setup_form_defaults(config.registry)

  >>> from pyams_form.interfaces.widget import IWidget
  >>> from pyams_form.browser import text

The TextWidget is a widget:

  >>> IWidget.implementedBy(text.TextWidget)
  True

The widget can render a input field only by adapting a request:

  >>> from pyams_layer.interfaces import PYAMS_BASE_SKIN_NAME
  >>> from pyams_layer.skin import apply_skin
  >>> request = testing.TestRequest()
  >>> apply_skin(request, PYAMS_BASE_SKIN_NAME)
  >>> widget = text.TextWidget(request)

Such a field provides IWidget:

 >>> IWidget.providedBy(widget)
  True

If we render the widget we get the HTML:

  >>> print(widget.render())
  <input type="text" class="text-widget" value="" />

Adding some more attributes to the widget will make it display more:

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = 'value'
  >>> widget.style = 'color: blue'
  >>> widget.placeholder = 'Email address'
  >>> widget.autocapitalize = 'off'

  >>> print(widget.render())
  <input type="text"
         id="id"
         name="name"
         class="text-widget"
         style="color: blue"
         value="value"
         placeholder="Email address"
         autocapitalize="off" />


Check DISPLAY_MODE:

  >>> from pyams_form.interfaces import DISPLAY_MODE
  >>> widget.value = 'foobar'
  >>> widget.style = None
  >>> widget.mode = DISPLAY_MODE
  >>> print(widget.render())
  <span id="id" class="text-widget">foobar</span>

Check HIDDEN_MODE:

  >>> from pyams_form.interfaces import HIDDEN_MODE
  >>> widget.value = u'foobar'
  >>> widget.mode = HIDDEN_MODE
  >>> print(widget.render())
  <input type="hidden"
         id="id"
         name="name"
         value="foobar"
         class="hidden-widget" />


Tests cleanup:

  >>> tearDown()
