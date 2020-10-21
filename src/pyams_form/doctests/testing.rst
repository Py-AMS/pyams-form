===============
Testing support
===============

Data Converter for Testing
--------------------------

Sometimes, we want to upload binary files. Particulary in Selenium
tests, it is nearly impossible to correctly input binary data - so we
allow the user to specify `base64` encoded data to be uploaded. This
is accomplished by using a hidden input field that holds the value
of the encoding desired.

  >>> from pyramid.testing import setUp, tearDown
  >>> config = setUp(hook_zca=True)

  >>> import zope.schema
  >>> from pyams_form import widget
  >>> from pyams_form import testing

As in converter.rst, we want to test a file upload widget.

  >>> filedata = zope.schema.Text(
  ...     __name__='data',
  ...     title='Some data to upload',)

Lets try passing a simple string, and not specify any encoding.

  >>> dataWidget = widget.Widget(testing.TestRequest(
  ...    params={'data.testing': 'haha'}))
  >>> dataWidget.name = 'data'

  >>> conv = testing.TestingFileUploadDataConverter(filedata, dataWidget)
  >>> conv.to_field_value('')
  b'haha'

And now, specify a encoded string

  >>> import base64
  >>> encStr = base64.b64encode(b'hoohoo')
  >>> dataWidget = widget.Widget(testing.TestRequest(
  ...    params={'data.testing': encStr, 'data.encoding': 'base64'}))
  >>> dataWidget.name = 'data'

  >>> conv = testing.TestingFileUploadDataConverter(filedata, dataWidget)
  >>> conv.to_field_value('')
  b'hoohoo'


Tests cleanup:

  >>> tearDown()
