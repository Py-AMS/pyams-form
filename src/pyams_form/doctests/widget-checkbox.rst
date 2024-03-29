Checkbox Widget
---------------

Note: the checkbox widget isn't registered for a field by default. You can use
the ``widgetFactory`` argument of a ``IField`` object if you construct fields
or set the custom widget factory on selected fields later.

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

The ``CheckBoxWidget`` widget renders a checkbox input type field e.g.  <input
type="checkbox" />

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import checkbox

The ``CheckboxWidget`` is a widget:

  >>> interfaces.widget.IWidget.implementedBy(checkbox.CheckBoxWidget)
  True

The widget can render a input field only by adapting a request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = checkbox.CheckBoxWidget(request)

Set a name and id for the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Such a field provides IWidget:

  >>> interfaces.widget.IWidget.providedBy(widget)
  True

If we render the widget we only get the empty marker:

  >>> print(widget.render())
  <input name="widget.name-empty-marker" type="hidden" value="1" />

Let's provide some values for this widget. We can do this by defining
a vocabulary providing ``ITerms``. This vocabulary uses descriminators
wich will fit for our setup.

  >>> import zope.schema.interfaces
  >>> from zope.schema.vocabulary import SimpleVocabulary
  >>> from pyams_layer.interfaces import IFormLayer
  >>> import pyams_form.term
  >>> class MyTerms(pyams_form.term.ChoiceTermsVocabulary):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = SimpleVocabulary.fromValues(['yes', 'no'])
  >>> config.registry.registerAdapter(pyams_form.term.BoolTerms,
  ...     required=(zope.interface.Interface,
  ...               IFormLayer, zope.interface.Interface,
  ...               zope.interface.Interface, interfaces.widget.ICheckBoxWidget),
  ...     provided=interfaces.ITerms)

Now let's try if we get widget values:

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <span id="widget-id">
    <span
          class="option">
      <input type="checkbox"
             id="widget-id-0"
             name="widget.name"
             class="checkbox-widget"
             value="true" />
      <label for="widget-id-0">
        <span class="label">yes</span>
      </label>
    </span>
    <span
          class="option">
      <input type="checkbox"
             id="widget-id-1"
             name="widget.name"
             class="checkbox-widget"
             value="false" />
      <label for="widget-id-1">
        <span class="label">no</span>
      </label>
    </span>
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

The checkbox json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'checked': False,
                'id': 'widget-id-0',
                'label': 'yes',
                'name': 'widget.name',
                'value': 'true'},
               {'checked': False,
                'id': 'widget-id-1',
                'label': 'no',
                'name': 'widget.name',
                'value': 'false'}],
   'required': False,
   'type': 'check',
   'value': ()}

If we set the value for the widget to ``yes``, we can se that the checkbox
field get rendered with a checked flag:

  >>> widget.value = 'true'
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <span id="widget-id">
    <span
          class="option">
      <input type="checkbox"
                     checked="checked"
             id="widget-id-0"
             name="widget.name"
             class="checkbox-widget"
             value="true" />
      <label for="widget-id-0">
        <span class="label">yes</span>
      </label>
    </span>
    <span
          class="option">
      <input type="checkbox"
             id="widget-id-1"
             name="widget.name"
             class="checkbox-widget"
             value="false" />
      <label for="widget-id-1">
        <span class="label">no</span>
      </label>
    </span>
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

The checkbox json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'checked': True,
                'id': 'widget-id-0',
                'label': 'yes',
                'name': 'widget.name',
                'value': 'true'},
               {'checked': False,
                'id': 'widget-id-1',
                'label': 'no',
                'name': 'widget.name',
                'value': 'false'}],
   'required': False,
   'type': 'check',
   'value': 'true'}

Check HIDDEN_MODE:

  >>> widget.value = 'true'
  >>> widget.mode = interfaces.HIDDEN_MODE
  >>> print(widget.render())
  <span class="option">
    <input type="hidden" id="widget-id-0" name="widget.name"
           class="checkbox-widget" value="true" />
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

The checkbox json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'hidden',
   'name': 'widget.name',
   'options': [{'checked': True,
                'id': 'widget-id-0',
                'label': 'yes',
                'name': 'widget.name',
                'value': 'true'},
               {'checked': False,
                'id': 'widget-id-1',
                'label': 'no',
                'name': 'widget.name',
                'value': 'false'}],
   'required': False,
   'type': 'check',
   'value': 'true'}

Make sure that we produce a proper label when we have no title for a term and
the value (which is used as a backup label) contains non-ASCII characters:

  >>> terms = SimpleVocabulary.fromValues([b'yes\012', b'no\243'])
  >>> widget.terms = terms
  >>> widget.update()
  >>> pprint(list(widget.items))
  [{'checked': False,
    'id': 'widget-id-0',
    'label': 'yes\n',
    'name': 'widget.name',
    'value': 'yes\n'},
   {'checked': False,
    'id': 'widget-id-1',
    'label': 'no',
    'name': 'widget.name',
    'value': 'no...'}]

Note: The "\234" character is interpreted differently in Pytohn 2 and 3
here. (This is mostly due to changes int he SimpleVocabulary code.)


Single Checkbox Widget
######################

Instead of using the checkbox widget as an UI component to allow multiple
selection from a list of choices, it can be also used by itself to toggle a
selection, effectively making it a binary selector. So in this case it lends
itself well as a boolean UI input component.

The ``SingleCheckboxWidget`` is a widget:

  >>> interfaces.widget.IWidget.implementedBy(checkbox.SingleCheckBoxWidget)
  True

The widget can render a input field only by adapting a request:

  >>> request = TestRequest()
  >>> widget = checkbox.SingleCheckBoxWidget(request)

Set a name and id for the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Such a widget provides the ``IWidget`` interface:

  >>> interfaces.widget.IWidget.providedBy(widget)
  True

For there to be a sensible output, we need to give the widget a label:

  >>> widget.label = 'Do you want that?'

  >>> widget.update()
  >>> print(format_html(widget.render()))
    <span id="widget-id"
          class="option">
      <input type="checkbox"
             id="widget-id-0"
             name="widget.name"
             class="single-checkbox-widget"
             value="selected" />
      <label for="widget-id-0">
        <span class="label">Do you want that?</span>
      </label>
    </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

The checkbox json_data representation:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': 'Do you want that?',
   'mode': 'input',
   'name': 'widget.name',
   'options': [{'checked': False,
                'id': 'widget-id-0',
                'label': 'Do you want that?',
                'name': 'widget.name',
                'value': 'selected'}],
   'required': False,
   'type': 'check',
   'value': ()}

Initially, the box is not checked. Changing the widget value to the selection
value, ...

  >>> widget.value = ['selected']

will make the box checked:

  >>> widget.update()
  >>> print(format_html(widget.render()))
    <span id="widget-id"
          class="option">
      <input type="checkbox"
                     checked="checked"
             id="widget-id-0"
             name="widget.name"
             class="single-checkbox-widget"
             value="selected" />
      <label for="widget-id-0">
        <span class="label">Do you want that?</span>
      </label>
    </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

If you do not specify the label on the widget directly, it is taken from the
field

  >>> from zope.schema import Bool
  >>> widget = checkbox.SingleCheckBoxWidget(request)
  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'
  >>> widget.field = Bool(title="Do you REALLY want that?")
  >>> widget.update()
  >>> print(format_html(widget.render()))
    <span id="widget-id"
          class="option">
      <input type="checkbox"
             id="widget-id-0"
             name="widget.name"
             class="single-checkbox-widget"
             value="selected" />
      <label for="widget-id-0">
        <span class="label">Do you REALLY want that?</span>
      </label>
    </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />

Check HIDDEN_MODE:

  >>> widget.value = 'selected'
  >>> widget.mode = interfaces.HIDDEN_MODE
  >>> print(format_html(widget.render()))
  <span class="option">
    <input type="hidden" id="widget-id-0"
           name="widget.name"
           class="single-checkbox-widget" value="selected" />
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />


Term with non ascii __str__
###########################

Check if a term which __str__ returns non ascii string does not crash the update method

  >>> from pyams_form.browser import checkbox

  >>> request = TestRequest()

  >>> widget = checkbox.CheckBoxWidget(request)
  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

  >>> import zope.schema.interfaces
  >>> from zope.schema.vocabulary import SimpleVocabulary,SimpleTerm
  >>> class ObjWithNonAscii__str__:
  ...     def __str__(self):
  ...         return 'héhé!'
  >>> class MyTerms(pyams_form.term.ChoiceTermsVocabulary):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = SimpleVocabulary([
  ...             SimpleTerm(ObjWithNonAscii__str__(), 'one', 'One'),
  ...             SimpleTerm(ObjWithNonAscii__str__(), 'two', 'Two'),
  ...         ])
  >>> config.registry.registerAdapter(MyTerms,
  ...     required=(zope.interface.Interface,
  ...             IFormLayer, zope.interface.Interface,
  ...             zope.interface.Interface, interfaces.widget.ICheckBoxWidget),
  ...     provided=interfaces.ITerms)
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <span id="widget-id">
    <span
          class="option">
      <input type="checkbox"
             id="widget-id-0"
             name="widget.name"
             class="checkbox-widget"
             value="one" />
      <label for="widget-id-0">
        <span class="label">One</span>
      </label>
    </span>
    <span
          class="option">
      <input type="checkbox"
             id="widget-id-1"
             name="widget.name"
             class="checkbox-widget"
             value="two" />
      <label for="widget-id-1">
        <span class="label">Two</span>
      </label>
    </span>
  </span>
  <input name="widget.name-empty-marker" type="hidden" value="1" />


Tests cleanup:

  >>> tearDown()
