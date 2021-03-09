Customizing widget lookup for IChoice
-------------------------------------

Widgets for fields implementing IChoice are looked up not only according to the
field, but also according to the source used by the field.

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

  >>> import zope.interface
  >>> from pyams_form import interfaces
  >>> from pyams_form.testing import TestRequest

  >>> def setupWidget(field):
  ...     request = TestRequest()
  ...     widget = config.registry.getMultiAdapter((field, request),
  ...         interfaces.widget.IFieldWidget)
  ...     widget.id = 'foo'
  ...     widget.name = 'bar'
  ...     return widget

We define a sample field and source:

  >>> from zope.schema import vocabulary
  >>> terms = [vocabulary.SimpleTerm(*value) for value in
  ...          [(True, 'yes', 'Yes'), (False, 'no', 'No')]]
  >>> vocabulary = vocabulary.SimpleVocabulary(terms)
  >>> field = zope.schema.Choice(default=True, vocabulary=vocabulary)

The default widget is the SelectWidget:

  >>> widget = setupWidget(field)
  >>> type(widget)
  <class 'pyams_form.browser.select.SelectWidget'>

But now we define a marker interface and have our source provide it:

  >>> from pyams_form.widget import FieldWidget
  >>> class ISampleSource(zope.interface.Interface):
  ...     pass
  >>> zope.interface.alsoProvides(vocabulary, ISampleSource)

We can then create and register a special widget for fields using sources with
the ISampleSource marker:

  >>> from pyams_layer.interfaces import IFormLayer
  >>> from pyams_form.browser import select
  >>> class SampleSelectWidget(select.SelectWidget):
  ...     pass
  >>> def SampleSelectFieldWidget(field, source, request):
  ...     return FieldWidget(field, SampleSelectWidget(request))
  >>> config.registry.registerAdapter(
  ...   SampleSelectFieldWidget,
  ...   (zope.schema.interfaces.IChoice, ISampleSource, IFormLayer),
  ...   interfaces.widget.IFieldWidget)

If we now look up the widget for the field, we get the specialized widget:

  >>> widget = setupWidget(field)
  >>> type(widget)
  <class '....SampleSelectWidget'>

Backwards compatibility
#######################

To maintain backwards compatibility, SelectFieldWidget() still can be called
without passing a source:

  >>> request = TestRequest()
  >>> widget = select.SelectFieldWidget(field, request)
  >>> type(widget)
  <class 'pyams_form.browser.select.SelectWidget'>


Tests cleanup:

  >>> tearDown()
