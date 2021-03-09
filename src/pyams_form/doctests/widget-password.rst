Password Widget
---------------

The password widget allows you to upload a new password to the server. The
"password" type of the "INPUT" element is described here:

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

As for all widgets, the password widget must provide the new ``IWidget``
interface:

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import password

  >>> interfaces.widget.IWidget.implementedBy(password.PasswordWidget)
  True

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = password.PasswordWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

If we render the widget we get a simple input element:

  >>> print(widget.render())
  <input type="password" id="widget.id" name="widget.name"
         class="password-widget" />

Even when we set a value on the widget, it is not displayed for security
reasons:

  >>> widget.value = 'password'
  >>> print(widget.render())
  <input type="password" id="widget.id" name="widget.name"
         class="password-widget" />

Adding some more attributes to the widget will make it display more:

  >>> widget.style = 'color: blue'
  >>> widget.placeholder = 'Confirm password'
  >>> widget.autocapitalize = 'off'

  >>> print(widget.render())
  <input type="password"
         id="widget.id"
         name="widget.name"
         class="password-widget"
         style="color: blue"
         placeholder="Confirm password"
         autocapitalize="off" />

Let's now make sure that we can extract user entered data from a widget:

  >>> widget.request = TestRequest(params={'widget.name': 'password'})
  >>> widget.update()
  >>> widget.extract()
  'password'

If nothing is found in the request, the default is returned:

  >>> widget.request = TestRequest()
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>


Tests cleanup:

  >>> tearDown()
