Image Widget
------------

The image widget allows you to submit a form to the server by clicking on an
image. The "image" type of the "INPUT" element is described here:

http://www.w3.org/TR/1999/REC-html401-19991224/interact/forms.html#edef-INPUT

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

As for all widgets, the image widget must provide the new ``IWidget``
interface:

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import image

  >>> interfaces.widget.IWidget.implementedBy(image.ImageWidget)
  True

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = image.ImageWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

If we render the widget we get a simple input element:

  >>> print(widget.render())
  <input type="image" id="widget.id" name="widget.name"
         class="image-widget" />

Setting an image source for the widget effectively changes the "src" attribute:

  >>> widget.src = 'widget.png'
  >>> print(widget.render())
  <input type="image" id="widget.id" name="widget.name"
         class="image-widget" src="widget.png" />


Let's now make sure that we can extract user entered data from a widget:

  >>> widget.request = TestRequest(
  ...     params={'widget.name.x': '10',
  ...             'widget.name.y': '20',
  ...             'widget.name': 'value'})
  >>> widget.update()
  >>> sorted(widget.extract().items())
  [('value', 'value'), ('x', 10), ('y', 20)]


If nothing is found in the request, the default is returned:

  >>> widget.request = TestRequest()
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>

  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget.id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'required': False,
   'src': 'widget.png',
   'type': 'image',
   'value': None}


Tests cleanup:

  >>> tearDown()
