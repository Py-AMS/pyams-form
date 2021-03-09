File Widget
-----------

The file widget allows you to upload a new file to the server. The "file" type
of the "INPUT" element is described here:

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

As for all widgets, the file widget must provide the new ``IWidget``
interface:

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import file

  >>> interfaces.widget.IWidget.implementedBy(file.FileWidget)
  True

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = file.FileWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

If we render the widget we get a simple input element:

  >>> print(widget.render())
  <input type="file" id="widget.id" name="widget.name"
         class="file-widget" />

Let's now make sure that we can extract user entered data from a widget:

  >>> try:
  ...     from StringIO import StringIO as BytesIO
  ... except ImportError:
  ...     from io import BytesIO
  >>> myfile = BytesIO(b'My file contents.')

  >>> widget.request = TestRequest(params={'widget.name': myfile})
  >>> widget.update()
  >>> isinstance(widget.extract(), BytesIO)
  True

If nothing is found in the request, the default is returned:

  >>> widget.request = TestRequest()
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>

Make also sure that we can handle FileUpload objects given form a file upload.

  >>> from zope.publisher.browser import FileUpload

Let's define a FieldStorage stub:

  >>> class FieldStorageStub:
  ...     def __init__(self, file):
  ...         self.file = file
  ...         self.headers = {}
  ...         self.filename = 'foo.bar'

Now build a FileUpload:

  >>> myfile = BytesIO(b'File upload contents.')
  >>> aFieldStorage = FieldStorageStub(myfile)
  >>> myUpload = FileUpload(aFieldStorage)

  >>> widget.request = TestRequest(params={'widget.name': myUpload})
  >>> widget.update()
  >>> widget.extract()
  <zope.publisher.browser.FileUpload object at ...>

If we render them, we get a regular file upload widget:

  >>> print(widget.render())
  <input type="file" id="widget.id" name="widget.name"
         class="file-widget" />

  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget.id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'required': False,
   'type': 'file',
   'value': <...FileUpload object at 0x...>}


Tests cleanup:

  >>> tearDown()
