File Testing Widget
-------------------

The File Testing widget is just like the file widget except it has
another hidden field where the contents of a file can be uploaded in a textarea.

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

  >>> from pyams_form import interfaces, tests
  >>> from pyams_form.browser import file

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = file.FileWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

We can also register a custom template for this widget:

  >>> import os
  >>> from pyams_template.interfaces import IPageTemplate
  >>> from pyams_form.template import WidgetTemplateFactory
  >>> from pyams_layer.interfaces import IFormLayer
  >>> factory = WidgetTemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                                 'templates', 'file-testing-input.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory,
  ...       required=(None, IFormLayer, None, None, interfaces.widget.IFileWidget),
  ...       provided=IPageTemplate, name=interfaces.INPUT_MODE)

If we render the widget we get a text area element instead of a simple
input element, but also with a text area:

  >>> print(widget.render())
  <input type="file"
         id="widget.id"
         name="widget.name"
         class="file-widget" />
  <input type="hidden"
         name="widget.name.encoding"
         value="plain" />
  <textarea name="widget.name.testing" style="display: none;"><!-- nothing here --></textarea>

Let's now make sure that we can extract user entered data from a widget:

  >>> try:
  ...   from cStringIO import cStringIO as BytesIO
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

Make also sure that we can handle FileUpload objects given from a file upload.

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
  <input type="file"
         id="widget.id"
         name="widget.name"
         class="file-widget" />
  <input type="hidden"
         name="widget.name.encoding"
         value="plain" />
  <textarea name="widget.name.testing" style="display: none;"><!-- nothing here --></textarea>

Alternatively, we can also pass in the file upload content via the
testing text area:

  >>> widget.request = TestRequest(
  ...     params={'widget.name.testing': 'File upload contents.'})
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>

The extract method uses the request directly, but we can get the value
using the data converter.

  >>> from pyams_form import testing
  >>> import zope.schema
  >>> conv = testing.TestingFileUploadDataConverter(
  ...     zope.schema.Bytes(), widget)
  >>> conv
  <TestingFileUploadDataConverter converts from Bytes to FileWidget>
  >>> conv.to_field_value("")
  b'File upload contents.'


Tests cleanup:

  >>> tearDown()
