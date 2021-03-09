=====================
Hint (title) Adapters
=====================

A widget can provide a hint. Hints are not a standard concept, the
implementations can be very different in each project. Hints are most
of the time implemented with JavaScript since the default ``input
title`` hint in browsers are almost unusable.

Our hint support is limited and only offers some helpers. Which means
we will offer an adapter that shows the schema field description as
the title. Since this is very specific we only provide a
``FieldDescriptionAsHint`` adapter which you can configure as a named
IValue adapter.

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

We also need to setup the form defaults:

  >>> from pyams_utils.testing import format_html
  >>> from pyams_form import testing
  >>> testing.setup_form_defaults(config.registry)

  >>> from pyams_layer.interfaces import IFormLayer
  >>> from pyams_form import interfaces
  >>> from pyams_form import form
  >>> from pyams_form import field
  >>> from pyams_form import hint

Let's create a couple of simple widgets and forms first:

  >>> import zope.interface
  >>> import zope.schema

  >>> class IContent(zope.interface.Interface):
  ...
  ...     textLine = zope.schema.TextLine(
  ...         title='Title',
  ...         description='A TextLine description')
  ...
  ...     anotherLine = zope.schema.TextLine(
  ...         title='Other')

  >>> @zope.interface.implementer(IContent)
  ... class Content:
  ...     textLine = None
  ...     otherLine = None
  ...
  >>> content = Content()

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

  >>> class HintForm(form.Form):
  ...     fields = field.Fields(IContent)

  >>> hintForm = HintForm(content, request)

As you can see, there is no title value set for our widgets:

  >>> hintForm.update()
  >>> print(hintForm.widgets['textLine'].render())
  <input type="text"
         id="form-widgets-textLine"
         name="form.widgets.textLine"
         class="text-widget required textline-field"
         title="A TextLine description"
         value="" />

  >>> print(hintForm.widgets['anotherLine'].render())
  <input type="text"
         id="form-widgets-anotherLine"
         name="form.widgets.anotherLine"
         class="text-widget required textline-field"
         value="" />

Let's configure our IValue ``hint`` adapter:

  >>> from pyams_form.hint import FieldDescriptionAsHint
  >>> config.registry.registerAdapter(FieldDescriptionAsHint,
  ...       required=(zope.interface.Interface, IFormLayer, interfaces.form.IForm, interfaces.IField, interfaces.widget.IWidget),
  ...       provided=interfaces.IValue, name='title')

If we update our form, we can see that the title is used based on the schema
field description:

  >>> hintForm.update()
  >>> print(hintForm.widgets['textLine'].render())
  <input type="text"
         id="form-widgets-textLine"
         name="form.widgets.textLine"
         class="text-widget required textline-field"
         title="A TextLine description"
         value="" />

If the field has no description as it is with the second one, no "title"
will be set for the widget:

  >>> print(hintForm.widgets['anotherLine'].render())
  <input type="text"
         id="form-widgets-anotherLine"
         name="form.widgets.anotherLine"
         class="text-widget required textline-field"
         value="" />


Check all fields
----------------

Just to make sure that all the widgets are handled correctly, we will
go through all of them. This sample can be useful if you need to
implement a JavaScript based hint concept:

  >>> import datetime
  >>> import decimal
  >>> from zope.schema import vocabulary

Let's setup a simple vocabulary:

  >>> vocab = vocabulary.SimpleVocabulary([
  ...     vocabulary.SimpleVocabulary.createTerm(1, '1', 'One'),
  ...     vocabulary.SimpleVocabulary.createTerm(2, '2', 'Two'),
  ...     vocabulary.SimpleVocabulary.createTerm(3, '3', 'Three'),
  ...     vocabulary.SimpleVocabulary.createTerm(4, '4', 'Four'),
  ...     vocabulary.SimpleVocabulary.createTerm(5, '5', 'Five')
  ...     ])

  >>> class IAllInOne(zope.interface.Interface):
  ...
  ...     asciiField = zope.schema.ASCII(
  ...         title='ASCII',
  ...         description='This is an ASCII field.',
  ...         default='This is\n ASCII.')
  ...
  ...     asciiLineField = zope.schema.ASCIILine(
  ...         title='ASCII Line',
  ...         description='This is an ASCII-Line field.',
  ...         default='An ASCII line.')
  ...
  ...     boolField = zope.schema.Bool(
  ...         title='Boolean',
  ...         description='This is a Bool field.',
  ...         default=True)
  ...
  ...     checkboxBoolField = zope.schema.Bool(
  ...         title='Boolean (Checkbox)',
  ...         description='This is a Bool field displayed suing a checkbox.',
  ...         default=True)
  ...
  ...     bytesLineField = zope.schema.BytesLine(
  ...         title='Bytes Line',
  ...         description='This is a bytes line field.',
  ...         default=b'A Bytes line.')
  ...
  ...     choiceField = zope.schema.Choice(
  ...         title='Choice',
  ...         description='This is a choice field.',
  ...         default=3,
  ...         vocabulary=vocab)
  ...
  ...     optionalChoiceField = zope.schema.Choice(
  ...         title='Choice (Not Required)',
  ...         description='This is a non-required choice field.',
  ...         vocabulary=vocab,
  ...         required=False)
  ...
  ...     promptChoiceField = zope.schema.Choice(
  ...         title='Choice (Explicit Prompt)',
  ...         description='This is a choice field with an explicit prompt.',
  ...         vocabulary=vocab,
  ...         required=False)
  ...
  ...     dateField = zope.schema.Date(
  ...         title='Date',
  ...         description='This is a Date field.',
  ...         default=datetime.date(2007, 4, 1))
  ...
  ...     datetimeField = zope.schema.Datetime(
  ...         title='Date/Time',
  ...         description='This is a Datetime field.',
  ...         default=datetime.datetime(2007, 4, 1, 12))
  ...
  ...     decimalField = zope.schema.Decimal(
  ...         title='Decimal',
  ...         description='This is a Decimal field.',
  ...         default=decimal.Decimal('12.87'))
  ...
  ...     dottedNameField = zope.schema.DottedName(
  ...         title='Dotted Name',
  ...         description='This is a DottedName field.',
  ...         default='pyams_form.util')
  ...
  ...     floatField = zope.schema.Float(
  ...         title='Float',
  ...         description='This is a Float field.',
  ...         default=12.8)
  ...
  ...     frozenSetField = zope.schema.FrozenSet(
  ...         title='Frozen Set',
  ...         description='This is a FrozenSet field.',
  ...         value_type=choiceField,
  ...         default=frozenset([1, 3]) )
  ...
  ...     idField = zope.schema.Id(
  ...         title='Id',
  ...         description='This is an Id field.',
  ...         default='pyams_form.util')
  ...
  ...     intField = zope.schema.Int(
  ...         title='Integer',
  ...         description='This is an Int field.',
  ...         default=12345)
  ...
  ...     listField = zope.schema.List(
  ...         title='List',
  ...         description='This is a List field.',
  ...         value_type=choiceField,
  ...         default=[1, 3])
  ...
  ...     passwordField = zope.schema.Password(
  ...         title='Password',
  ...         description='This is a Password field.',
  ...         default='mypwd',
  ...         required=False)
  ...
  ...     setField = zope.schema.Set(
  ...         title='Set',
  ...         description='This is a Set field.',
  ...         value_type=choiceField,
  ...         default=set([1, 3]) )
  ...
  ...     sourceTextField = zope.schema.SourceText(
  ...         title='Source Text',
  ...         description='This is a SourceText field.',
  ...         default='<source />')
  ...
  ...     textField = zope.schema.Text(
  ...         title='Text',
  ...         description='This is a Text field.',
  ...         default='Some\n Text.')
  ...
  ...     textLineField = zope.schema.TextLine(
  ...         title='Text Line',
  ...         description='This is a TextLine field.',
  ...         default='Some Text line.')
  ...
  ...     timeField = zope.schema.Time(
  ...         title='Time',
  ...         description='This is a Time field.',
  ...         default=datetime.time(12, 0))
  ...
  ...     timedeltaField = zope.schema.Timedelta(
  ...         title='Time Delta',
  ...         description='This is a Timedelta field.',
  ...         default=datetime.timedelta(days=3))
  ...
  ...     tupleField = zope.schema.Tuple(
  ...         title='Tuple',
  ...         description='This is a Tuple field.',
  ...         value_type=choiceField,
  ...         default=(1, 3))
  ...
  ...     uriField = zope.schema.URI(
  ...         title='URI',
  ...         description='This is an URI field.',
  ...         default='http://pyams.readthedocs.io')
  ...
  ...     hiddenField = zope.schema.TextLine(
  ...         title='Hidden Text Line',
  ...         description='This is a hidden TextLine field.',
  ...         default='Some Hidden Text.')

  >>> @zope.interface.implementer(IAllInOne)
  ... class AllInOne:
  ...     asciiField = None
  ...     asciiLineField = None
  ...     boolField = None
  ...     checkboxBoolField = None
  ...     choiceField = None
  ...     optionalChoiceField = None
  ...     promptChoiceField = None
  ...     dateField = None
  ...     decimalField = None
  ...     dottedNameField = None
  ...     floatField = None
  ...     frozenSetField = None
  ...     idField = None
  ...     intField = None
  ...     listField = None
  ...     passwordField = None
  ...     setField = None
  ...     sourceTextField = None
  ...     textField = None
  ...     textLineField = None
  ...     timeField = None
  ...     timedeltaField = None
  ...     tupleField = None
  ...     uriField = None
  ...     hiddenField = None

  >>> allInOne = AllInOne()

  >>> class AllInOneForm(form.Form):
  ...     fields = field.Fields(IAllInOne)

Now test the hints in our widgets:

  >>> allInOneForm = AllInOneForm(allInOne, request)
  >>> allInOneForm.update()
  >>> print(allInOneForm.widgets['asciiField'].render())
  <textarea id="form-widgets-asciiField"
            name="form.widgets.asciiField"
            class="textarea-widget required ascii-field"
            title="This is an ASCII field.">This is
   ASCII.</textarea>

  >>> print(allInOneForm.widgets['asciiLineField'].render())
  <input type="text"
         id="form-widgets-asciiLineField"
         name="form.widgets.asciiLineField"
         class="text-widget required asciiline-field"
         title="This is an ASCII-Line field."
         value="An ASCII line." />

  >>> print(allInOneForm.widgets['boolField'].render())
  <span class="option">
    <label for="form-widgets-boolField-0">
      <input type="radio"
         id="form-widgets-boolField-0"
         name="form.widgets.boolField"
         class="radio-widget bool-field"
         value="true"
         title="This is a Bool field."
         checked="checked" />
      <span class="label">yes</span>
    </label>
  </span>
  <span class="option">
    <label for="form-widgets-boolField-1">
      <input type="radio"
         id="form-widgets-boolField-1"
         name="form.widgets.boolField"
         class="radio-widget bool-field"
         value="false"
         title="This is a Bool field." />
      <span class="label">no</span>
    </label>
  </span>
  <input type="hidden" name="form.widgets.boolField-empty-marker" value="1" />

  >>> print(allInOneForm.widgets['checkboxBoolField'].render())
  <span class="option">
    <label for="form-widgets-checkboxBoolField-0">
      <input type="radio"
         id="form-widgets-checkboxBoolField-0"
         name="form.widgets.checkboxBoolField"
         class="radio-widget bool-field"
         value="true"
         title="This is a Bool field displayed suing a checkbox."
         checked="checked" />
      <span class="label">yes</span>
    </label>
  </span>
  <span class="option">
    <label for="form-widgets-checkboxBoolField-1">
      <input type="radio"
         id="form-widgets-checkboxBoolField-1"
         name="form.widgets.checkboxBoolField"
         class="radio-widget bool-field"
         value="false"
         title="This is a Bool field displayed suing a checkbox." />
      <span class="label">no</span>
    </label>
  </span>
  <input type="hidden" name="form.widgets.checkboxBoolField-empty-marker" value="1" />

  >>> print(allInOneForm.widgets['textField'].render())
  <textarea id="form-widgets-textField"
            name="form.widgets.textField"
            class="textarea-widget required text-field"
            title="This is a Text field.">Some
   Text.</textarea>

  >>> print(allInOneForm.widgets['textLineField'].render())
  <input type="text"
         id="form-widgets-textLineField"
         name="form.widgets.textLineField"
         class="text-widget required textline-field"
         title="This is a TextLine field."
         value="Some Text line." />

  >>> print(allInOneForm.widgets['bytesLineField'].render())
  <input type="text"
         id="form-widgets-bytesLineField"
         name="form.widgets.bytesLineField"
         class="text-widget required bytesline-field"
         title="This is a bytes line field."
         value="A Bytes line." />

  >>> print(format_html(allInOneForm.widgets['choiceField'].render()))
  <select id="form-widgets-choiceField"
          name="form.widgets.choiceField"
          class="select-widget required choice-field"
          title="This is a choice field."
          size="1">
      <option id="form-widgets-choiceField-0"
              value="1">One</option>
      <option id="form-widgets-choiceField-1"
              value="2">Two</option>
      <option id="form-widgets-choiceField-2"
              value="3"
              selected="selected">Three</option>
      <option id="form-widgets-choiceField-3"
              value="4">Four</option>
      <option id="form-widgets-choiceField-4"
              value="5">Five</option>
  </select>
  <input name="form.widgets.choiceField-empty-marker" type="hidden" value="1" />

  >>> print(format_html(allInOneForm.widgets['optionalChoiceField'].render()))
  <select id="form-widgets-optionalChoiceField"
          name="form.widgets.optionalChoiceField"
          class="select-widget choice-field"
          title="This is a non-required choice field."
          size="1">
      <option id="form-widgets-optionalChoiceField-novalue"
              value="--NOVALUE--"
              selected="selected">No value</option>
      <option id="form-widgets-optionalChoiceField-0"
              value="1">One</option>
      <option id="form-widgets-optionalChoiceField-1"
              value="2">Two</option>
      <option id="form-widgets-optionalChoiceField-2"
              value="3">Three</option>
      <option id="form-widgets-optionalChoiceField-3"
              value="4">Four</option>
      <option id="form-widgets-optionalChoiceField-4"
              value="5">Five</option>
  </select>
  <input name="form.widgets.optionalChoiceField-empty-marker" type="hidden" value="1" />

  >>> print(format_html(allInOneForm.widgets['promptChoiceField'].render()))
  <select id="form-widgets-promptChoiceField"
          name="form.widgets.promptChoiceField"
          class="select-widget choice-field"
          title="This is a choice field with an explicit prompt."
          size="1">
      <option id="form-widgets-promptChoiceField-novalue"
              value="--NOVALUE--"
              selected="selected">No value</option>
      <option id="form-widgets-promptChoiceField-0"
              value="1">One</option>
      <option id="form-widgets-promptChoiceField-1"
              value="2">Two</option>
      <option id="form-widgets-promptChoiceField-2"
              value="3">Three</option>
      <option id="form-widgets-promptChoiceField-3"
              value="4">Four</option>
      <option id="form-widgets-promptChoiceField-4"
              value="5">Five</option>
  </select>
  <input name="form.widgets.promptChoiceField-empty-marker" type="hidden" value="1" />

  >>> print(allInOneForm.widgets['dateField'].render())
  <input type="text"
         id="form-widgets-dateField"
         name="form.widgets.dateField"
         class="text-widget required date-field"
         title="This is a Date field."
         value="4/1/07" />

  >>> print(allInOneForm.widgets['datetimeField'].render())
  <input type="text"
         id="form-widgets-datetimeField"
         name="form.widgets.datetimeField"
         class="text-widget required datetime-field"
         title="This is a Datetime field."
         value="4/1/07 12:00 PM" />

  >>> print(allInOneForm.widgets['decimalField'].render())
  <input type="text"
         id="form-widgets-decimalField"
         name="form.widgets.decimalField"
         class="text-widget required decimal-field"
         title="This is a Decimal field."
         value="12.87" />

  >>> print(allInOneForm.widgets['dottedNameField'].render())
  <input type="text"
         id="form-widgets-dottedNameField"
         name="form.widgets.dottedNameField"
         class="text-widget required dottedname-field"
         title="This is a DottedName field."
         value="pyams_form.util" />

  >>> print(allInOneForm.widgets['floatField'].render())
  <input type="text"
         id="form-widgets-floatField"
         name="form.widgets.floatField"
         class="text-widget required float-field"
         title="This is a Float field."
         value="12.8" />

  >>> print(format_html(allInOneForm.widgets['frozenSetField'].render()))
  <select id="form-widgets-frozenSetField"
          name="form.widgets.frozenSetField"
          class="select-widget required frozenset-field"
          title="This is a FrozenSet field."
          multiple="multiple"
          size="5">
      <option id="form-widgets-frozenSetField-0"
              value="1"
              selected="selected">One</option>
      <option id="form-widgets-frozenSetField-1"
              value="2">Two</option>
      <option id="form-widgets-frozenSetField-2"
              value="3"
              selected="selected">Three</option>
      <option id="form-widgets-frozenSetField-3"
              value="4">Four</option>
      <option id="form-widgets-frozenSetField-4"
              value="5">Five</option>
  </select>
  <input name="form.widgets.frozenSetField-empty-marker" type="hidden" value="1" />

  >>> print(allInOneForm.widgets['idField'].render())
  <input type="text"
         id="form-widgets-idField"
         name="form.widgets.idField"
         class="text-widget required id-field"
         title="This is an Id field."
         value="pyams_form.util" />

  >>> print(allInOneForm.widgets['intField'].render())
  <input type="text"
         id="form-widgets-intField"
         name="form.widgets.intField"
         class="text-widget required int-field"
         title="This is an Int field."
         value="12,345" />

  >>> print(format_html(allInOneForm.widgets['listField'].render()))
  <script type="text/javascript" src="/++static++/pyams_form/js/orderedselect-input.js"></script>
  <table border="0" class="ordered-selection-field" id="form-widgets-listField">
    <tr>
      <td>
        <select id="form-widgets-listField-from"
                name="form.widgets.listField.from"
                class="required list-field"
                title="This is a List field."
                multiple="multiple"
                size="5">
            <option value="2">Two</option>
            <option value="4">Four</option>
            <option value="5">Five</option>
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button" value="&rarr;"
                onClick="javascript:from2to('form-widgets-listField')">&rarr;</button>
        <br />
        <button name="to2fromButton" type="button" value="&larr;"
                onClick="javascript:to2from('form-widgets-listField')">&larr;</button>
      </td>
      <td>
        <select id="form-widgets-listField-to"
                name="form.widgets.listField.to"
                class="required list-field"
                title="This is a List field."
                multiple="multiple"
                size="5">
            <option value="1">One</option>
            <option value="3">Three</option>
        </select>
        <input name="form.widgets.listField-empty-marker" type="hidden" />
        <span id="form-widgets-listField-toDataContainer" style="display: none">
          <script type="text/javascript">copyDataForSubmit('form-widgets-listField');</script>
        </span>
      </td>
      <td>
        <button name="upButton" type="button" value="&uarr;"
                onClick="javascript:moveUp('form-widgets-listField')">&uarr;</button>
        <br />
        <button name="downButton" type="button" value="&darr;"
                onClick="javascript:moveDown('form-widgets-listField')">&darr;</button>
      </td>
    </tr>
  </table>

  >>> print(allInOneForm.widgets['passwordField'].render())
  <input type="password"
         id="form-widgets-passwordField"
         name="form.widgets.passwordField"
         class="password-widget password-field"
         title="This is a Password field." />

  >>> print(format_html(allInOneForm.widgets['setField'].render()))
  <select id="form-widgets-setField"
          name="form.widgets.setField"
          class="select-widget required set-field"
          title="This is a Set field."
          multiple="multiple"
          size="5">
      <option id="form-widgets-setField-0"
              value="1"
              selected="selected">One</option>
      <option id="form-widgets-setField-1"
              value="2">Two</option>
      <option id="form-widgets-setField-2"
              value="3"
              selected="selected">Three</option>
      <option id="form-widgets-setField-3"
              value="4">Four</option>
      <option id="form-widgets-setField-4"
              value="5">Five</option>
  </select>
  <input name="form.widgets.setField-empty-marker" type="hidden" value="1" />

  >>> print(allInOneForm.widgets['sourceTextField'].render())
  <textarea id="form-widgets-sourceTextField"
            name="form.widgets.sourceTextField"
            class="textarea-widget required sourcetext-field"
            title="This is a SourceText field.">&lt;source /&gt;</textarea>

  >>> print(allInOneForm.widgets['timeField'].render())
  <input type="text" id="form-widgets-timeField"
         name="form.widgets.timeField"
         class="text-widget required time-field"
         title="This is a Time field."
         value="12:00 PM" />

  >>> print(allInOneForm.widgets['timedeltaField'].render())
  <input type="text"
         id="form-widgets-timedeltaField"
         name="form.widgets.timedeltaField"
         class="text-widget required timedelta-field"
         title="This is a Timedelta field."
         value="3 days, 0:00:00" />

  >>> print(format_html(allInOneForm.widgets['tupleField'].render()))
  <script type="text/javascript" src="/++static++/pyams_form/js/orderedselect-input.js"></script>
  <table border="0" class="ordered-selection-field" id="form-widgets-tupleField">
    <tr>
      <td>
        <select id="form-widgets-tupleField-from"
                name="form.widgets.tupleField.from"
                class="required tuple-field"
                title="This is a Tuple field."
                multiple="multiple"
                size="5">
            <option value="2">Two</option>
            <option value="4">Four</option>
            <option value="5">Five</option>
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button" value="&rarr;"
                onClick="javascript:from2to('form-widgets-tupleField')">&rarr;</button>
        <br />
        <button name="to2fromButton" type="button" value="&larr;"
                onClick="javascript:to2from('form-widgets-tupleField')">&larr;</button>
      </td>
      <td>
        <select id="form-widgets-tupleField-to"
                name="form.widgets.tupleField.to"
                class="required tuple-field"
                title="This is a Tuple field."
                multiple="multiple"
                size="5">
            <option value="1">One</option>
            <option value="3">Three</option>
        </select>
        <input name="form.widgets.tupleField-empty-marker" type="hidden" />
        <span id="form-widgets-tupleField-toDataContainer" style="display: none">
          <script type="text/javascript">copyDataForSubmit('form-widgets-tupleField');</script>
        </span>
      </td>
      <td>
        <button name="upButton" type="button" value="&uarr;"
                onClick="javascript:moveUp('form-widgets-tupleField')">&uarr;</button>
        <br />
        <button name="downButton" type="button" value="&darr;"
                onClick="javascript:moveDown('form-widgets-tupleField')">&darr;</button>
      </td>
    </tr>
  </table>

  >>> print(allInOneForm.widgets['uriField'].render())
  <input type="text"
         id="form-widgets-uriField"
         name="form.widgets.uriField"
         class="text-widget required uri-field"
         title="This is an URI field."
         value="http://pyams.readthedocs.io" />

  >>> print(allInOneForm.widgets['hiddenField'].render())
  <input type="text"
         id="form-widgets-hiddenField"
         name="form.widgets.hiddenField"
         class="text-widget required textline-field"
         title="This is a hidden TextLine field."
         value="Some Hidden Text." />


Tests cleanup:

  >>> tearDown()