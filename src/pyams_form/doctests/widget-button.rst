Button Widget
-------------

The button widget allows you to provide buttons whose actions are defined
using Javascript scripts. The "button" type of the "INPUT" element is
described here:

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

As for all widgets, the button widget must provide the new ``IWidget``
interface:

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import button

  >>> interfaces.widget.IWidget.implementedBy(button.ButtonWidget)
  True

The widget can be instantiated only using the request:

  >>> request = testing.TestRequest()
  >>> widget = button.ButtonWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget.id'
  >>> widget.name = 'widget.name'

If we render the widget we get a simple input element:

  >>> print(widget.render())
  <input type="submit"
         id="widget.id"
         name="widget.name"
         class="button-widget" />

Setting a value for the widget effectively changes the button label:

  >>> widget.value = 'Button'
  >>> print(widget.render())
  <input type="submit"
         id="widget.id"
         name="widget.name"
         class="button-widget"
         value="Button" />

Let's now make sure that we can extract user entered data from a widget:

  >>> widget.request = testing.TestRequest(params={'widget.name': 'button'})
  >>> widget.update()
  >>> widget.extract()
  'button'

If nothing is found in the request, the default is returned:

  >>> widget.request = testing.TestRequest()
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>


Tests cleanup:

  >>> tearDown()
