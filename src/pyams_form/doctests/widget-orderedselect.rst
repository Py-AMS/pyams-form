
Ordered-Select Widget
---------------------

The ordered select widget allows you to select one or more values from a set
of given options and sort those options. Unfortunately, HTML does not provide
such a widget as part of its specification, so that the system has to use a
combnation of "option" elements, buttons and Javascript.

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

  >>> from pyams_utils.testing import format_html, render_xpath

As for all widgets, the select widget must provide the new ``IWidget``
interface:

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import orderedselect

  >>> interfaces.widget.IWidget.implementedBy(orderedselect.OrderedSelectWidget)
  True

The widget can be instantiated only using the request:

  >>> from pyams_form import testing
  >>> request = testing.TestRequest()

  >>> widget = orderedselect.OrderedSelectWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

If we render the widget we get an empty widget:

  >>> print(format_html(widget.render()))
  <script type="text/javascript" src="/++static++/pyams_form/js/orderedselect-input.js"></script>
  <table border="0" class="ordered-selection-field" id="widget-id">
    <tr>
      <td>
        <select id="widget-id-from"
                name="widget.name.from"
                multiple="multiple"
                size="5">
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button" value="&rarr;"
                onClick="javascript:from2to('widget-id')">&rarr;</button>
        <br />
        <button name="to2fromButton" type="button" value="&larr;"
                onClick="javascript:to2from('widget-id')">&larr;</button>
      </td>
      <td>
        <select id="widget-id-to"
                name="widget.name.to"
                multiple="multiple"
                size="5">
        </select>
        <input name="widget.name-empty-marker" type="hidden" />
        <span id="widget-id-toDataContainer" style="display: none">
          <script type="text/javascript">copyDataForSubmit('widget-id');</script>
        </span>
      </td>
      <td>
        <button name="upButton" type="button" value="&uarr;"
                onClick="javascript:moveUp('widget-id')">&uarr;</button>
        <br />
        <button name="downButton" type="button" value="&darr;"
                onClick="javascript:moveDown('widget-id')">&darr;</button>
      </td>
    </tr>
  </table>

The json data representing the oredered select widget:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'not_selected': (),
   'options': (),
   'required': False,
   'selected': (),
   'type': 'multi_select',
   'value': ()}

Let's provide some values for this widget. We can do this by defining a source
providing ``ITerms``. This source uses descriminators wich will fit our setup.

  >>> import zope.schema.interfaces
  >>> from zope.schema.vocabulary import SimpleVocabulary
  >>> from pyams_layer.interfaces import IFormLayer
  >>> import pyams_form.term

  >>> class SelectionTerms(pyams_form.term.Terms):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = SimpleVocabulary([
  ...              SimpleVocabulary.createTerm(1, 'a', 'A'),
  ...              SimpleVocabulary.createTerm(2, 'b', 'B'),
  ...              SimpleVocabulary.createTerm(3, 'c', 'C'),
  ...              SimpleVocabulary.createTerm(4, 'd', 'A'),
  ...              ])

  >>> config.registry.registerAdapter(SelectionTerms,
  ...     required=(None, IFormLayer, None, None, interfaces.widget.IOrderedSelectWidget),
  ...     provided=interfaces.ITerms)

Now let's try if we get widget values:

  >>> widget.update()
  >>> print(format_html(render_xpath(widget, './/table//td[1]')))
  <td>
        <select id="widget-id-from" name="widget.name.from" multiple="multiple" size="5">
            <option value="a">A</option>
            <option value="b">B</option>
            <option value="c">C</option>
            <option value="d">A</option>
        </select>
      </td>

If we select item "b", then it should be selected:

  >>> widget.value = ['b']
  >>> widget.update()
  >>> print(format_html(render_xpath(widget, './/table//select[@id="widget-id-from"]/..')))
  <td>
        <select id="widget-id-from" name="widget.name.from" multiple="multiple" size="5">
            <option value="a">A</option>
            <option value="c">C</option>
            <option value="d">A</option>
        </select>
      </td>

  >>> print(format_html(render_xpath(widget, './/table//select[@id="widget-id-to"]')))
  <select id="widget-id-to" name="widget.name.to" multiple="multiple" size="5">
            <option value="b">B</option>
        </select>

The json data representing the oredered select widget:
  >>> from pprint import pprint
  >>> pprint(widget.json_data())
  {'error': '',
   'id': 'widget-id',
   'label': '',
   'mode': 'input',
   'name': 'widget.name',
   'not_selected': [{'content': 'A', 'id': 'widget-id-0', 'value': 'a'},
                    {'content': 'C', 'id': 'widget-id-2', 'value': 'c'},
                    {'content': 'A', 'id': 'widget-id-3', 'value': 'd'}],
   'options': [{'content': 'A', 'id': 'widget-id-0', 'value': 'a'},
               {'content': 'B', 'id': 'widget-id-1', 'value': 'b'},
               {'content': 'C', 'id': 'widget-id-2', 'value': 'c'},
               {'content': 'A', 'id': 'widget-id-3', 'value': 'd'}],
   'required': False,
   'selected': [{'content': 'B', 'id': 'widget-id-0', 'value': 'b'}],
   'type': 'multi_select',
   'value': ['b']}

Let's now make sure that we can extract user entered data from a widget:

  >>> widget.request = testing.TestRequest(params={'widget.name': ['c']})
  >>> widget.update()
  >>> widget.extract()
  ('c',)

Unfortunately, when nothing is selected, we do not get an empty list sent into
the request, but simply no entry at all. For this we have the empty marker, so
that:

  >>> widget.request = testing.TestRequest(params={'widget.name-empty-marker': '1'})
  >>> widget.update()
  >>> widget.extract()
  ()

If nothing is found in the request, the default is returned:

  >>> widget.request = testing.TestRequest()
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>

Let's now make sure that a bogus value causes extract to return the default as
described by the interface:

  >>> widget.request = testing.TestRequest(params={'widget.name': ['x']})
  >>> widget.update()
  >>> widget.extract()
  <NO_VALUE>

Finally, let's check correctness of widget rendering in one rare case when
we got selection terms with callable values and without titles. For example,
you can get those terms when you using the "Content Types" vocabulary from
zope.app.content.

  >>> class CallableValue(object):
  ...     def __init__(self, value):
  ...         self.value = value
  ...     def __call__(self):
  ...         pass
  ...     def __str__(self):
  ...        return 'Callable Value %s' % self.value

  >>> class SelectionTermsWithCallableValues(pyams_form.term.Terms):
  ...     def __init__(self, context, request, form, field, widget):
  ...         self.terms = SimpleVocabulary([
  ...              SimpleVocabulary.createTerm(CallableValue(1), 'a'),
  ...              SimpleVocabulary.createTerm(CallableValue(2), 'b'),
  ...              SimpleVocabulary.createTerm(CallableValue(3), 'c')
  ...              ])

  >>> widget.terms = SelectionTermsWithCallableValues(
  ...     None, testing.TestRequest(), None, None, widget)
  >>> widget.update()
  >>> print(format_html(render_xpath(widget, './/table//select[@id="widget-id-from"]')))
  <select id="widget-id-from" name="widget.name.from" multiple="multiple" size="5">
            <option value="a">Callable Value 1</option>
            <option value="b">Callable Value 2</option>
            <option value="c">Callable Value 3</option>
        </select>


Tests cleanup:

  >>> tearDown()
