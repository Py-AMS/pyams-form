Select Widget, missing terms
----------------------------

The select widget allows you to select one or more values from a set of given
options. The "SELECT" and "OPTION" elements are described here:

http://www.w3.org/TR/1999/REC-html401-19991224/interact/forms.html#edef-SELECT

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
  >>> from pyams_layer.interfaces import IFormLayer

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import select

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

  >>> widget = select.SelectWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

We need some context:

  >>> import zope.interface
  >>> import zope.schema
  >>> class IPerson(zope.interface.Interface):
  ...     rating = zope.schema.Choice(
  ...     vocabulary='Ratings')

  >>> @zope.interface.implementer(IPerson)
  ... class Person(object):
  ...     pass
  >>> person = Person()

Let's provide some values for this widget. We can do this by defining a source
providing ``ITerms``. This source uses descriminators which will fit our setup.

  >>> import zope.schema.interfaces
  >>> from zope.schema.vocabulary import SimpleVocabulary
  >>> from zope.schema.vocabulary import SimpleTerm
  >>> import pyams_form.term

  >>> from zope.schema import vocabulary
  >>> ratings = vocabulary.SimpleVocabulary([
  ...     vocabulary.SimpleVocabulary.createTerm(0, '0', 'bad'),
  ...     vocabulary.SimpleVocabulary.createTerm(1, '1', 'okay'),
  ...     vocabulary.SimpleVocabulary.createTerm(2, '2', 'good')
  ...     ])

  >>> def RatingsVocabulary(obj):
  ...     return ratings

  >>> vr = vocabulary.getVocabularyRegistry()
  >>> vr.register('Ratings', RatingsVocabulary)

  >>> class SelectionTerms(pyams_form.term.MissingChoiceTermsVocabulary):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.context = context
  ...         self.field = field
  ...         self.terms = ratings
  ...         self.widget = widget
  ...
  ...     def _make_missing_term(self, token):
  ...         if token == 'x':
  ...             return super()._make_missing_term(token)
  ...         else:
  ...             raise LookupError

  >>> config.registry.registerAdapter(SelectionTerms,
  ...     (None, IFormLayer, None, None, interfaces.widget.ISelectWidget),
  ...     interfaces.ITerms)

Now let's try if we get widget values:

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <select id="widget-id"
          name="widget.name"
          class="select-widget"
          size="1">
      <option id="widget-id-novalue"
              value="--NOVALUE--"
              selected="selected">No value</option>
      <option id="widget-id-0"
              value="0">bad</option>
      <option id="widget-id-1"
              value="1">okay</option>
      <option id="widget-id-2"
              value="2">good</option>
  </select>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

If we set the widget value to "x", then it should be present and selected:

  >>> widget.value = ('x',)
  >>> widget.context = person
  >>> widget.field = IPerson['rating']
  >>> zope.interface.alsoProvides(widget, interfaces.form.IContextAware)
  >>> person.rating = 'x'
  >>> widget.terms = None

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <select id="widget-id"
          name="widget.name"
          class="select-widget"
          size="1">
      <option id="widget-id-novalue"
              value="--NOVALUE--">No value</option>
      <option id="widget-id-0"
              value="0">bad</option>
      <option id="widget-id-1"
              value="1">okay</option>
      <option id="widget-id-2"
              value="2">good</option>
      <option id="widget-id-missing-0"
              value="x"
              selected="selected">Missing: x</option>
  </select>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

If we set the widget value to "y", then it should NOT be around:

  >>> widget.value = ['y']
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <select id="widget-id" name="widget.name"
          class="select-widget" size="1">
  <option id="widget-id-novalue" value="--NOVALUE--">No value</option>
  <option id="widget-id-0" value="0">bad</option>
  <option id="widget-id-1" value="1">okay</option>
  <option id="widget-id-2" value="2">good</option>
  </select>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

Let's now make sure that we can extract user entered data from a widget:

  >>> widget.request = TestRequest(params={'widget.name': ['c']})
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>

Well, only of it matches the context's current value:

  >>> widget.request = TestRequest(params={'widget.name': ['x']})
  >>> widget.update()
  >>> widget.extract()
  ('x',)

When "No value" is selected, then no verification against the terms is done:

  >>> widget.request = TestRequest(params={'widget.name': ['--NOVALUE--']})
  >>> widget.update()
  >>> widget.extract(default=1)
  ('--NOVALUE--',)

Let's now make sure that we can extract user entered missing data from a widget:

  >>> widget.request = TestRequest(params={'widget.name': ['x']})
  >>> widget.update()
  >>> widget.extract()
  ('x',)

  >>> widget.request = TestRequest(params={'widget.name': ['y']})
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>

Unfortunately, when nothing is selected, we do not get an empty list sent into
the request, but simply no entry at all. For this we have the empty marker, so
that:

  >>> widget.request = TestRequest(params={'widget.name-empty-marker': '1'})
  >>> widget.update()
  >>> widget.extract()
  ()

If nothing is found in the request, the default is returned:

  >>> widget.request = TestRequest()
  >>> widget.update()
  >>> widget.extract(default=1)
  1

Let's now make sure that a bogus value causes extract to return the default as
described by the interface:

  >>> widget.request = TestRequest(params={'widget.name': ['y']})
  >>> widget.update()
  >>> widget.extract(default=1)
  1

Display Widget
##############

The select widget comes with a template for ``DISPLAY_MODE``.

Let's see what happens if we have values that are not in the vocabulary:

  >>> widget.required = True
  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> widget.value = ['0', '1', 'x']
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <span id="widget-id"
        class="select-widget"><span
        class="selected-option">bad</span>, <span
        class="selected-option">okay</span>, <span
        class="selected-option">Missing: x</span></span>

Hidden Widget
#############

The select widget comes with a template for ``HIDDEN_MODE``.

Let's see what happens if we have values that are not in the vocabulary:

  >>> widget.mode = interfaces.HIDDEN_MODE
  >>> widget.value = ['0', 'x']
  >>> widget.update()
  >>> print(format_html(widget.render()))
    <input
           type="hidden"
               class="hidden-widget"
           id="widget-id-0"
               name="widget.name"
               value="0" />
    <input
           type="hidden"
               class="hidden-widget"
           id="widget-id-missing-0"
               name="widget.name"
               value="x" />
  <input name="widget.name-empty-marker" type="hidden" value="1" />


Tests cleanup:

  >>> tearDown()
