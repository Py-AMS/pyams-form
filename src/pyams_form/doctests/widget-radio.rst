from pyams_layer.interfaces import PYAMS_BASE_SKIN_NAMERadio Widget
------------

The RadioWidget renders a radio input type field e.g. <input type="radio" />

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

  >>> from pyams_form.interfaces.widget import IWidget, IRadioWidget
  >>> from pyams_form.browser import radio

The ``RadioWidget`` is a widget:

 >>> IWidget.implementedBy(radio.RadioWidget)
  True

The widget can render a input field only by adapting a request:

  >>> from pyams_layer.interfaces import PYAMS_BASE_SKIN_NAME, IFormLayer
  >>> from pyams_layer.skin import apply_skin
  >>> request = testing.TestRequest()
  >>> apply_skin(request, PYAMS_BASE_SKIN_NAME)
  >>> widget = radio.RadioWidget(request)

Set a name and id for the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Such a field provides IWidget:

 >>> IWidget.providedBy(widget)
  True

If we render the widget we only get the empty marker:

  >>> print(widget.render())
  <input type="hidden" name="widget.name-empty-marker" value="1" />

Let's provide some values for this widget. We can do this by defining a source
providing ITerms. This source uses discriminators which will fit for our setup.

  >>> from zope.interface import Interface
  >>> from zc.sourcefactory.basic import BasicSourceFactory
  >>> from pyams_form.interfaces import IBoolTerms
  >>> from pyams_form import term
  >>> class YesNoSourceFactory(BasicSourceFactory):
  ...     def getValues(self):
  ...         return ['yes', 'no']
  >>> class MyTerms(term.ChoiceTermsSource):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = YesNoSourceFactory()
  >>> config.registry.registerAdapter(term.BoolTerms,
  ...     required=(Interface, IFormLayer, Interface, Interface, IRadioWidget),
  ...     provided=IBoolTerms)

Now let's try if we get widget values:

  >>> widget.update()
  >>> print(widget.render())
  <span class="option">
    <label for="widget-id-0">
      <input type="radio"
         id="widget-id-0"
         name="widget.name"
         class="radio-widget"
         value="true" />
       <span class="label">yes</span>
    </label>
  </span>
  <span class="option">
    <label for="widget-id-1">
      <input type="radio"
         id="widget-id-1"
         name="widget.name"
         class="radio-widget"
         value="false" />
       <span class="label">no</span>
    </label>
  </span>
  <input type="hidden" name="widget.name-empty-marker" value="1" />

The radio json_data representation:
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
   'type': 'radio',
   'value': ()}

If we set the value for the widget to ``yes``, we can se that the radio field
get rendered with a checked flag:

  >>> widget.value = 'true'
  >>> widget.update()
  >>> print(widget.render())
  <span class="option">
    <label for="widget-id-0">
      <input type="radio"
         id="widget-id-0"
         name="widget.name"
         class="radio-widget"
         value="true"
         checked="checked" />
      <span class="label">yes</span>
    </label>
  </span>
  <span class="option">
    <label for="widget-id-1">
      <input type="radio"
         id="widget-id-1"
         name="widget.name"
         class="radio-widget"
         value="false" />
      <span class="label">no</span>
    </label>
  </span>
  <input type="hidden" name="widget.name-empty-marker" value="1" />

The radio json_data representation:
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
   'type': 'radio',
   'value': 'true'}

We can also render the input elements for each value separately:

  >>> print(widget.render_for_value('true'))
  <input type="radio"
         id="widget-id-0"
         name="widget.name"
         class="radio-widget"
         value="true"
         checked="checked" />

  >>> print(widget.render_for_value('false'))
  <input type="radio"
         id="widget-id-1"
         name="widget.name"
         class="radio-widget"
         value="false" />

Additionally we can render the "no value" input element used for non-required fields:

  >>> from pyams_form.widget import SequenceWidget
  >>> print(SequenceWidget.no_value_token)
  --NOVALUE--
  >>> print(widget.render_for_value(SequenceWidget.no_value_token))
  <input type="radio"
         id="widget-id-novalue"
         name="widget.name"
         class="radio-widget"
         value="--NOVALUE--" />

Check HIDDEN_MODE:

  >>> from pyams_form.interfaces import HIDDEN_MODE
  >>> widget.value = ['true']
  >>> widget.mode = HIDDEN_MODE
  >>> print(widget.render())
  <input type="hidden"
         id="widget-id-0"
         name="widget.name"
         value="true" />

And independently:

  >>> print(widget.render_for_value('true'))
  <input type="hidden"
         id="widget-id-0"
         name="widget.name"
         value="true" />

The unchecked values do not need a hidden field, hence they are empty:

   >>> print(widget.render_for_value('false'))


Check DISPLAY_MODE:

  >>> from pyams_form.interfaces import DISPLAY_MODE
  >>> widget.value = ['true']
  >>> widget.mode = DISPLAY_MODE
  >>> print(widget.render())
  <span id="widget-id"
        class="radio-widget"><span
        class="selected-option">yes</span></span>

And independently:

   >>> print(widget.render_for_value('true'))
   <span id="widget-id" class="radio-widget"><span class="selected-option">yes</span></span>

Again, unchecked values are not displayed:

   >>> print(widget.render_for_value('false'))


Make sure that we produce a proper label when we have no title for a term and
the value (which is used as a backup label) contains non-ASCII characters:

  >>> from zope.schema.vocabulary import SimpleVocabulary
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

Term with non ascii __str__
###########################

Check if a term which __str__ returns non ascii string does not crash the update method

  >>> request = testing.TestRequest()
  >>> apply_skin(request, PYAMS_BASE_SKIN_NAME)
  >>> widget = radio.RadioWidget(request)
  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

  >>> import zope.schema.interfaces
  >>> from zope.schema.vocabulary import SimpleVocabulary,SimpleTerm
  >>> from pyams_form.interfaces import ITerms
  >>> import pyams_form.term
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
  ...     required=(Interface, IFormLayer, Interface, Interface, IRadioWidget),
  ...     provided=ITerms)
  >>> widget.update()
  >>> print(widget.render())
  <span class="option">
    <label for="widget-id-0">
      <input type="radio"
         id="widget-id-0"
         name="widget.name"
         class="radio-widget"
         value="one" />
      <span class="label">One</span>
    </label>
  </span>
  <span class="option">
    <label for="widget-id-1">
      <input type="radio"
         id="widget-id-1"
         name="widget.name"
         class="radio-widget"
         value="two" />
      <span class="label">Two</span>
    </label>
  </span>
  <input type="hidden" name="widget.name-empty-marker" value="1" />


Tests cleanup:

  >>> tearDown()
