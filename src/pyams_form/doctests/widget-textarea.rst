TextArea Widget
---------------

The widget can render a text area field for a text:

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
  >>> from pyams_form.browser import textarea

The ``TextAreaWidget`` is a widget:

  >>> IWidget.implementedBy(textarea.TextAreaWidget)
  True

The widget can render a input field only by adapting a request:

  >>> from pyams_layer.interfaces import PYAMS_BASE_SKIN_NAME
  >>> from pyams_layer.skin import apply_skin
  >>> request = testing.TestRequest()
  >>> apply_skin(request, PYAMS_BASE_SKIN_NAME)
  >>> widget = textarea.TextAreaWidget(request)

Such a field provides IWidget:

  >>> IWidget.providedBy(widget)
  True

If we render the widget we get the HTML:

  >>> print(widget.render())
  <textarea class="textarea-widget"></textarea>

Adding some more attributes to the widget will make it display more:

  >>> widget.id = 'id'
  >>> widget.name = 'name'
  >>> widget.value = 'value'

  >>> print(widget.render())
  <textarea id="id" name="name" class="textarea-widget">value</textarea>

The json data representing the textarea widget:

  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'id',
   'label': '',
   'mode': 'input',
   'name': 'name',
   'required': False,
   'type': 'textarea',
   'value': 'value'}

Check DISPLAY_MODE:

  >>> from pyams_form.interfaces import HIDDEN_MODE, DISPLAY_MODE

  >>> widget.value = 'foobar'
  >>> widget.mode = DISPLAY_MODE
  >>> print(widget.render())
  <span id="id" class="textarea-widget">foobar</span>

Check HIDDEN_MODE:

  >>> widget.value = 'foobar'
  >>> widget.mode = HIDDEN_MODE
  >>> print(widget.render())
  <input type="hidden"
         id="id"
         name="name"
         value="foobar" />


Tests cleanup:

  >>> tearDown()
