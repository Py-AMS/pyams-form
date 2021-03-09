===============
Browser support
===============

The ``pyams_form`` library provides a form framework and widgets. This document
ensures that we implement a widget for each field defined in
``zope.schema``. Take a look at the different widget doctest files for more
information about the widgets.

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

  >>> import zope.schema
  >>> from pyams_form import browser

Also define a helper method for test the widgets:

  >>> from pyams_form import interfaces
  >>> from pyams_form.testing import TestRequest
  >>> def setupWidget(field):
  ...     request = TestRequest()
  ...     widget = zope.component.getMultiAdapter((field, request),
  ...         interfaces.widget.IFieldWidget)
  ...     widget.id = 'foo'
  ...     widget.name = 'bar'
  ...     return widget

  >>> from pyams_utils.testing import format_html


ASCII
-----

  >>> field = zope.schema.ASCII(default='This is\n ASCII.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.textarea.TextAreaWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from ASCII to TextAreaWidget>

  >>> print(widget.render())
  <textarea id="foo" name="bar" class="textarea-widget required ascii-field">This is
   ASCII.</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="textarea-widget required ascii-field">This is
   ASCII.</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="textarea-widget required ascii-field">This is
   ASCII.</span></div>
  </div>

As you can see, we will get an additional error class called ``row-error`` if
we render a widget with an error view assigned:

  >>> class DummyErrorView(object):
  ...    def render(self):
  ...        return 'Dummy Error'
  >>> widget.error = (DummyErrorView())
  >>> print(widget())
  <div id="foo-row"
       class="row-error row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="textarea-widget required ascii-field">This is
   ASCII.</span></div>
  </div>


ASCIILine
---------

  >>> field = zope.schema.ASCIILine(default='An ASCII line.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from ASCIILine to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar"
         class="text-widget required asciiline-field" value="An ASCII line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required asciiline-field">An ASCII line.</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required asciiline-field">An ASCII line.</span></div>
  </div>


Bool
----

  >>> field = zope.schema.Bool(default=True, title="Check me")
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.radio.RadioWidget'>

  >>> interfaces.IDataConverter(widget)
  <SequenceDataConverter converts from Bool to RadioWidget>

  >>> print(widget.render())
  <span class="option">
    <label for="foo-0">
      <input type="radio"
         id="foo-0"
         name="bar"
         class="radio-widget bool-field"
         value="true"
         checked="checked" />
      <span class="label">yes</span>
    </label>
  </span>
  <span class="option">
    <label for="foo-1">
      <input type="radio"
         id="foo-1"
         name="bar"
         class="radio-widget bool-field"
         value="false" />
      <span class="label">no</span>
    </label>
  </span>
  <input type="hidden" name="bar-empty-marker" value="1" />


  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo"
        class="radio-widget bool-field"><span
        class="selected-option">yes</span></span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row">
      <div class="label">
              <label for="foo">
                      <span>Check me</span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="radio-widget bool-field"><span
        class="selected-option">yes</span></span></div>
  </div>

For the boolean, the checkbox widget can be used as well:

  >>> from pyams_form.browser import checkbox
  >>> widget = checkbox.CheckBoxFieldWidget(field, TestRequest())
  >>> widget.id = 'foo'
  >>> widget.name = 'bar'
  >>> widget.update()

  >>> print(format_html(widget.render()))
  <span id="foo">
    <span
          class="option">
      <input type="checkbox"
                     checked="checked"
             id="foo-0"
             name="bar"
             class="checkbox-widget bool-field"
             value="true" />
      <label for="foo-0">
        <span class="label">yes</span>
      </label>
    </span>
    <span
          class="option">
      <input type="checkbox"
             id="foo-1"
             name="bar"
             class="checkbox-widget bool-field"
             value="false" />
      <label for="foo-1">
        <span class="label">no</span>
      </label>
    </span>
  </span>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo"
        class="checkbox-widget bool-field"><span
        class="selected-option">yes</span></span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row">
      <div class="label">
              <label for="foo">
                      <span>Check me</span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="checkbox-widget bool-field"><span
        class="selected-option">yes</span></span></div>
  </div>

We can also have a single checkbox button for the boolean.

  >>> widget = checkbox.SingleCheckBoxFieldWidget(field, TestRequest())
  >>> widget.id = 'foo'
  >>> widget.name = 'bar'
  >>> widget.update()

  >>> print(format_html(widget.render()))
    <span id="foo"
          class="option">
      <input type="checkbox"
                     checked="checked"
             id="foo-0"
             name="bar"
             class="single-checkbox-widget bool-field"
             value="selected" />
      <label for="foo-0">
        <span class="label">Check me</span>
      </label>
    </span>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo"
        class="single-checkbox-widget bool-field"><span
        class="selected-option">Check me</span></span>

Note that the widget label is not repeated twice:

  >>> widget.label
  ''

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="single-checkbox-widget bool-field"><span
        class="selected-option">Check me</span></span></div>
  </div>


Button
------

  >>> from pyams_form import button
  >>> field = button.Button(title='Press me!')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.submit.SubmitWidget'>

  >>> print(format_html(widget.render()))
  <input type="submit"
         id="foo"
         name="bar"
         class="submit-widget button-field"
         value="Press me!" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(format_html(widget.render()))
  <input type="submit"
         disabled="disabled"
         id="foo"
         name="bar"
         class="submit-widget button-field"
         value="Press me!" />

There exists an alternative widget for the button field, the button widget. It
is not used by default, but available for use:

  >>> from pyams_form.browser.button import ButtonFieldWidget
  >>> widget = ButtonFieldWidget(field, TestRequest())
  >>> widget.id = "foo"
  >>> widget.name = "bar"

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <input type="submit"
         id="foo"
         name="bar"
         class="button-widget button-field"
         value="Press me!" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(format_html(widget.render()))
  <input type="submit"
         disabled="disabled"
         id="foo"
         name="bar"
         class="button-widget button-field"
         value="Press me!" />


Bytes
-----

  >>> field = zope.schema.Bytes(default=b'Default bytes')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.file.FileWidget'>

  >>> interfaces.IDataConverter(widget)
  <FileUploadDataConverter converts from Bytes to FileWidget>

  >>> print(widget.render())
  <input type="file" id="foo" name="bar" class="file-widget required bytes-field" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(format_html(widget.render()))
  <span id="foo"
        class="file-widget required bytes-field"></span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="file-widget required bytes-field"></span></div>
  </div>


BytesLine
---------

  >>> field = zope.schema.BytesLine(default=b'A Bytes line.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from BytesLine to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required bytesline-field"
         value="A Bytes line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required bytesline-field">A Bytes line.</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required bytesline-field">A Bytes line.</span></div>
  </div>


Choice
------

  >>> from zope.schema import vocabulary
  >>> terms = [vocabulary.SimpleTerm(*value) for value in
  ...          [(True, 'yes', 'Yes'), (False, 'no', 'No')]]
  >>> vocabulary = vocabulary.SimpleVocabulary(terms)
  >>> field = zope.schema.Choice(default=True, vocabulary=vocabulary)
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.select.SelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <SequenceDataConverter converts from Choice to SelectWidget>

  >>> print(widget.render())
  <select id="foo" name="bar" class="select-widget required choice-field"
          size="1">
    <option id="foo-0" value="yes" selected="selected">Yes</option>
    <option id="foo-1" value="no">No</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="select-widget required choice-field"><span
    class="selected-option">Yes</span></span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="select-widget required choice-field"><span
        class="selected-option">Yes</span></span></div>
  </div>


Date
----

  >>> import datetime
  >>> field = zope.schema.Date(default=datetime.date(2007, 4, 1))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <DateDataConverter converts from Date to TextWidget>

  >>> print(widget.render())
  <input type="text"
         id="foo"
         name="bar"
         class="text-widget required date-field"
         value="4/1/07" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required date-field">4/1/07</span>

Calling the widget will return the widget including the layout:

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required date-field">4/1/07</span></div>
  </div>


Datetime
--------

  >>> field = zope.schema.Datetime(default=datetime.datetime(2007, 4, 1, 12))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <DatetimeDataConverter converts from Datetime to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required datetime-field"
         value="4/1/07 12:00 PM" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required datetime-field">4/1/07 12:00 PM</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required datetime-field">4/1/07 12:00 PM</span></div>
  </div>


Decimal
-------

  >>> import decimal
  >>> field = zope.schema.Decimal(default=decimal.Decimal('1265.87'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <DecimalDataConverter converts from Decimal to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required decimal-field"
         value="1,265.87" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required decimal-field">1,265.87</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required decimal-field">1,265.87</span></div>
  </div>


Dict
----

There is no default widget for this field, since the sematics are fairly
complex.


DottedName
----------

  >>> field = zope.schema.DottedName(default='pyams_form')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from DottedName to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required dottedname-field"
         value="pyams_form" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required dottedname-field">pyams_form</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required dottedname-field">pyams_form</span></div>
  </div>


Float
-----

  >>> field = zope.schema.Float(default=1265.8)
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FloatDataConverter converts from Float to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required float-field"
         value="1,265.8" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required float-field">1,265.8</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required float-field">1,265.8</span></div>
  </div>


FrozenSet
---------

  >>> field = zope.schema.FrozenSet(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=frozenset([1, 3]) )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.select.SelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <CollectionSequenceDataConverter converts from FrozenSet to SelectWidget>

  >>> print(format_html(widget.render()))
  <select id="foo" name="bar" class="select-widget required frozenset-field"
          multiple="multiple" size="5">
    <option id="foo-0" value="1" selected="selected">1</option>
    <option id="foo-1" value="2">2</option>
    <option id="foo-2" value="3" selected="selected">3</option>
    <option id="foo-3" value="4">4</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="select-widget required frozenset-field"><span
    class="selected-option">1</span>, <span
    class="selected-option">3</span></span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="select-widget required frozenset-field"><span
        class="selected-option">1</span>, <span
        class="selected-option">3</span></span></div>
  </div>

Id
--

  >>> field = zope.schema.Id(default='pyams_form.id')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from Id to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required id-field"
         value="pyams_form.id" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required id-field">pyams_form.id</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required id-field">pyams_form.id</span></div>
  </div>


ImageButton
-----------

Let's say we have a simple image field that uses the ``pressme.png`` image.

  >>> from pyams_form import button
  >>> field = button.ImageButton(
  ...     image='pressme.png',
  ...     title='Press me!')

  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.image.ImageWidget'>

  >>> print(widget.render())
  <input type="image"
         id="foo"
         name="bar"
         class="image-widget imagebutton-field"
         value="Press me!"
         src="pressme.png" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <input type="image"
         disabled="disabled"
         id="foo"
         name="bar"
         class="image-widget imagebutton-field"
         value="Press me!"
         src="pressme.png" />


Int
---

  >>> field = zope.schema.Int(default=1200)
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <IntegerDataConverter converts from Int to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required int-field"
         value="1,200" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required int-field">1,200</span>


List - ASCII
------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.ASCII(
  ...         title='ASCII',
  ...         default='This is\n ASCII.'),
  ...     default=['foo\nfoo', 'bar\nbar'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>ASCII</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-0"
                name="bar.0"
                class="textarea-widget required ascii-field">foo
  foo</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>ASCII</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-1"
                name="bar.1"
                class="textarea-widget required ascii-field">bar
  bar</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - ASCIILine
----------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.ASCIILine(
  ...         title='ASCIILine',
  ...         default='An ASCII line.'),
  ...     default=['foo', 'bar'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>ASCIILine</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required asciiline-field"
         value="foo" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>ASCIILine</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required asciiline-field"
         value="bar" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Choice
-------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=[1, 3] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.orderedselect.OrderedSelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <CollectionSequenceDataConverter converts from List to OrderedSelectWidget>

  >>> print(format_html(widget.render()))
  <script type="text/javascript" src="/++static++/pyams_form/js/orderedselect-input.js"></script>
  <table border="0" class="ordered-selection-field" id="foo">
    <tr>
      <td>
        <select id="foo-from"
                name="bar.from"
                class="required list-field"
                multiple="multiple"
                size="5">
            <option value="2">2</option>
            <option value="4">4</option>
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button" value="&rarr;"
                onClick="javascript:from2to('foo')">&rarr;</button>
        <br />
        <button name="to2fromButton" type="button" value="&larr;"
                onClick="javascript:to2from('foo')">&larr;</button>
      </td>
      <td>
        <select id="foo-to"
                name="bar.to"
                class="required list-field"
                multiple="multiple"
                size="5">
            <option value="1">1</option>
            <option value="3">3</option>
        </select>
        <input name="bar-empty-marker" type="hidden" />
        <span id="foo-toDataContainer" style="display: none">
          <script type="text/javascript">copyDataForSubmit('foo');</script>
        </span>
      </td>
      <td>
        <button name="upButton" type="button" value="&uarr;"
                onClick="javascript:moveUp('foo')">&uarr;</button>
        <br />
        <button name="downButton" type="button" value="&darr;"
                onClick="javascript:moveDown('foo')">&darr;</button>
      </td>
    </tr>
  </table>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(format_html(widget.render()))
  <span id="foo"
        class="required list-field">
      <span class="selected-option">1</span>,
      <span class="selected-option">3</span></span>


List - Date
-----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Date(
  ...         title='Date',
  ...         default=datetime.date(2007, 4, 1)),
  ...     default=[datetime.date(2008, 9, 27), datetime.date(2008, 9, 28)])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Date</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required date-field"
         value="9/27/08" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Date</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required date-field"
         value="9/28/08" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Datetime
---------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Datetime(
  ...         title='Datetime',
  ...         default=datetime.datetime(2007, 4, 1, 12)),
  ...     default=[datetime.datetime(2008, 9, 27, 12),
  ...              datetime.datetime(2008, 9, 28, 12)])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Datetime</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required datetime-field"
         value="9/27/08 12:00 PM" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Datetime</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required datetime-field"
         value="9/28/08 12:00 PM" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Decimal
---------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Decimal(
  ...         title='Decimal',
  ...         default=decimal.Decimal('1265.87')),
  ...     default=[decimal.Decimal('123.456'), decimal.Decimal('1')])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Decimal</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required decimal-field"
         value="123.456" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Decimal</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required decimal-field"
         value="1" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - DottedName
-----------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.DottedName(
  ...         title='DottedName',
  ...         default='pyams_form.id'),
  ...     default=['pyams_form.id', 'pyams.wizard'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>DottedName</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required dottedname-field"
         value="pyams_form.id" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>DottedName</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required dottedname-field"
         value="pyams.wizard" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Float
------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Float(
  ...         title='Float',
  ...         default=123.456),
  ...     default=[1234.5, 1])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Float</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required float-field"
         value="1,234.5" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Float</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required float-field"
         value="1.0" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Id
---------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Id(
  ...         title='Id',
  ...         default='pyams_form.id'),
  ...     default=['pyams_form.id', 'pyams.wizard'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Id</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required id-field"
         value="pyams_form.id" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Id</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required id-field"
         value="pyams.wizard" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Int
----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Int(
  ...         title='Int',
  ...         default=666),
  ...     default=[42, 43])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Int</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Int</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Password
---------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Password(
  ...         title='Password',
  ...         default='mypwd'),
  ...     default=['pwd', 'pass'])
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Password</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="password"
         id="foo-0"
         name="bar.0"
         class="password-widget required password-field" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Password</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="password"
         id="foo-1"
         name="bar.1"
         class="password-widget required password-field" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - SourceText
-----------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.SourceText(
  ...         title='SourceText',
  ...         default='<source />'),
  ...     default=['<html></body>foo</body></html>', '<h1>bar</h1>'] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>SourceText</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-0"
                name="bar.0"
                class="textarea-widget required sourcetext-field">&lt;html&gt;&lt;/body&gt;foo&lt;/body&gt;&lt;/html&gt;</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>SourceText</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-1"
                name="bar.1"
                class="textarea-widget required sourcetext-field">&lt;h1&gt;bar&lt;/h1&gt;</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Text
-----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Text(
  ...         title='Text',
  ...         default='Some\n Text.'),
  ...     default=['foo\nfoo', 'bar\nbar'] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Text</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-0"
                name="bar.0"
                class="textarea-widget required text-field">foo
  foo</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Text</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-1"
                name="bar.1"
                class="textarea-widget required text-field">bar
  bar</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - TextLine
---------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.TextLine(
  ...         title='TextLine',
  ...         default='Some Text line.'),
  ...     default=['foo', 'bar'] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>TextLine</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required textline-field"
         value="foo" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>TextLine</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required textline-field"
         value="bar" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Time
-----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Time(
  ...         title='Time',
  ...         default=datetime.time(12, 0)),
  ...     default=[datetime.time(13, 0), datetime.time(14, 0)] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Time</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required time-field"
         value="1:00 PM" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Time</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required time-field"
         value="2:00 PM" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - Timedelta
----------------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.Timedelta(
  ...         title='Timedelta',
  ...         default=datetime.timedelta(days=3)),
  ...     default=[datetime.timedelta(days=4), datetime.timedelta(days=5)] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Timedelta</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required timedelta-field"
         value="4 days, 0:00:00" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Timedelta</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required timedelta-field"
         value="5 days, 0:00:00" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


List - URI
----------

  >>> field = zope.schema.List(
  ...     value_type=zope.schema.URI(
  ...         title='URI',
  ...         default='http://zope.org'),
  ...     default=['http://www.python.org', 'http://www.zope.com'] )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from List to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>URI</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required uri-field"
         value="http://www.python.org" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>URI</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required uri-field"
         value="http://www.zope.com" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Object
------

By default, we are not going to provide widgets for an object, since we
believe this is better done using sub-forms.


Password
--------

  >>> field = zope.schema.Password(default='mypwd')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.password.PasswordWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from Password to PasswordWidget>

  >>> print(widget.render())
  <input type="password" id="foo" name="bar"
         class="password-widget required password-field" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="password-widget required password-field">mypwd</span>


Set
---

  >>> field = zope.schema.Set(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=set([1, 3]) )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.select.SelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <CollectionSequenceDataConverter converts from Set to SelectWidget>

  >>> print(widget.render())
  <select id="foo" name="bar" class="select-widget required set-field"
          multiple="multiple"  size="5">
    <option id="foo-0" value="1" selected="selected">1</option>
    <option id="foo-1" value="2">2</option>
    <option id="foo-2" value="3" selected="selected">3</option>
    <option id="foo-3" value="4">4</option>
  </select>
  <input name="bar-empty-marker" type="hidden" value="1" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="select-widget required set-field"><span
      class="selected-option">1</span>, <span
      class="selected-option">3</span></span>


SourceText
----------

  >>> field = zope.schema.SourceText(default='<source />')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.textarea.TextAreaWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from SourceText to TextAreaWidget>

  >>> print(widget.render())
  <textarea id="foo" name="bar"
            class="textarea-widget required sourcetext-field">&lt;source /&gt;</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="textarea-widget required sourcetext-field">&lt;source /&gt;</span>


Text
----

  >>> field = zope.schema.Text(default='Some\n Text.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.textarea.TextAreaWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from Text to TextAreaWidget>

  >>> print(widget.render())
  <textarea id="foo" name="bar" class="textarea-widget required text-field">Some
   Text.</textarea>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="textarea-widget required text-field">Some
    Text.</span>


TextLine
--------

  >>> field = zope.schema.TextLine(default='Some Text line.')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from TextLine to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required textline-field"
         value="Some Text line." />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required textline-field">Some Text line.</span>


Time
----

  >>> field = zope.schema.Time(default=datetime.time(12, 0))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <TimeDataConverter converts from Time to TextWidget>


  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required time-field"
         value="12:00 PM" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required time-field">12:00 PM</span>


Timedelta
---------

  >>> field = zope.schema.Timedelta(default=datetime.timedelta(days=3))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <TimedeltaDataConverter converts from Timedelta to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required timedelta-field"
         value="3 days, 0:00:00" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required timedelta-field">3 days, 0:00:00</span>


Tuple - ASCII
-------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.ASCII(
  ...         title='ASCII',
  ...         default='This is\n ASCII.'),
  ...     default=('foo\nfoo', 'bar\nbar'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>ASCII</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-0"
                name="bar.0"
                class="textarea-widget required ascii-field">foo
  foo</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>ASCII</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-1"
                name="bar.1"
                class="textarea-widget required ascii-field">bar
  bar</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - ASCIILine
-----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.ASCIILine(
  ...         title='ASCIILine',
  ...         default='An ASCII line.'),
  ...     default=('foo', 'bar'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>ASCIILine</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required asciiline-field"
         value="foo" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>ASCIILine</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required asciiline-field"
         value="bar" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Choice
--------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Choice(values=(1, 2, 3, 4)),
  ...     default=(1, 3) )
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.orderedselect.OrderedSelectWidget'>

  >>> interfaces.IDataConverter(widget)
  <CollectionSequenceDataConverter converts from Tuple to OrderedSelectWidget>

  >>> print(format_html(widget.render()))
  <script type="text/javascript" src="/++static++/pyams_form/js/orderedselect-input.js"></script>
  <table border="0" class="ordered-selection-field" id="foo">
    <tr>
      <td>
        <select id="foo-from"
                name="bar.from"
                class="required tuple-field"
                multiple="multiple"
                size="5">
            <option value="2">2</option>
            <option value="4">4</option>
        </select>
      </td>
      <td>
        <button name="from2toButton" type="button" value="&rarr;"
                onClick="javascript:from2to('foo')">&rarr;</button>
        <br />
        <button name="to2fromButton" type="button" value="&larr;"
                onClick="javascript:to2from('foo')">&larr;</button>
      </td>
      <td>
        <select id="foo-to"
                name="bar.to"
                class="required tuple-field"
                multiple="multiple"
                size="5">
            <option value="1">1</option>
            <option value="3">3</option>
        </select>
        <input name="bar-empty-marker" type="hidden" />
        <span id="foo-toDataContainer" style="display: none">
          <script type="text/javascript">copyDataForSubmit('foo');</script>
        </span>
      </td>
      <td>
        <button name="upButton" type="button" value="&uarr;"
                onClick="javascript:moveUp('foo')">&uarr;</button>
        <br />
        <button name="downButton" type="button" value="&darr;"
                onClick="javascript:moveDown('foo')">&darr;</button>
      </td>
    </tr>
  </table>

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(format_html(widget.render()))
  <span id="foo"
        class="required tuple-field">
      <span class="selected-option">1</span>,
      <span class="selected-option">3</span></span>


Tuple - Date
------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Date(
  ...         title='Date',
  ...         default=datetime.date(2007, 4, 1)),
  ...     default=(datetime.date(2008, 9, 27), datetime.date(2008, 9, 28)))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Date</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required date-field"
         value="9/27/08" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Date</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required date-field"
         value="9/28/08" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Datetime
----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Datetime(
  ...         title='Datetime',
  ...         default=datetime.datetime(2007, 4, 1, 12)),
  ...     default=(datetime.datetime(2008, 9, 27, 12),
  ...              datetime.datetime(2008, 9, 28, 12)))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Datetime</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required datetime-field"
         value="9/27/08 12:00 PM" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Datetime</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required datetime-field"
         value="9/28/08 12:00 PM" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Decimal
----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Decimal(
  ...         title='Decimal',
  ...         default=decimal.Decimal('1265.87')),
  ...     default=(decimal.Decimal('123.456'), decimal.Decimal('1')))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Decimal</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required decimal-field"
         value="123.456" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Decimal</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required decimal-field"
         value="1" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - DottedName
------------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.DottedName(
  ...         title='DottedName',
  ...         default='pyams_form.id'),
  ...     default=('pyams_form.id', 'pyams.wizard'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>DottedName</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required dottedname-field"
         value="pyams_form.id" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>DottedName</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required dottedname-field"
         value="pyams.wizard" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Float
-------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Float(
  ...         title='Float',
  ...         default=123.456),
  ...     default=(1234.5, 1))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Float</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required float-field"
         value="1,234.5" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Float</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required float-field"
         value="1.0" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Id
----------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Id(
  ...         title='Id',
  ...         default='pyams_form.id'),
  ...     default=('pyams_form.id', 'pyams.wizard'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Id</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required id-field"
         value="pyams_form.id" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Id</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required id-field"
         value="pyams.wizard" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Int
-----------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Int(
  ...         title='Int',
  ...         default=666),
  ...     default=(42, 43))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Int</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Int</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Password
----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Password(
  ...         title='Password',
  ...         default='mypwd'),
  ...     default=('pwd', 'pass'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Password</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="password"
         id="foo-0"
         name="bar.0"
         class="password-widget required password-field" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Password</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="password"
         id="foo-1"
         name="bar.1"
         class="password-widget required password-field" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - SourceText
------------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.SourceText(
  ...         title='SourceText',
  ...         default='<source />'),
  ...     default=('<html></body>foo</body></html>', '<h1>bar</h1>'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>SourceText</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-0"
                name="bar.0"
                class="textarea-widget required sourcetext-field">&lt;html&gt;&lt;/body&gt;foo&lt;/body&gt;&lt;/html&gt;</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>SourceText</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-1"
                name="bar.1"
                class="textarea-widget required sourcetext-field">&lt;h1&gt;bar&lt;/h1&gt;</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Text
------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Text(
  ...         title='Text',
  ...         default='Some\n Text.'),
  ...     default=('foo\nfoo', 'bar\nbar'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Text</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-0"
                name="bar.0"
                class="textarea-widget required text-field">foo
  foo</textarea>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Text</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <textarea id="foo-1"
                name="bar.1"
                class="textarea-widget required text-field">bar
  bar</textarea>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - TextLine
----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.TextLine(
  ...         title='TextLine',
  ...         default='Some Text line.'),
  ...     default=('foo', 'bar'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>TextLine</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required textline-field"
         value="foo" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>TextLine</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required textline-field"
         value="bar" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Time
------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Time(
  ...         title='Time',
  ...         default=datetime.time(12, 0)),
  ...     default=(datetime.time(13, 0), datetime.time(14, 0)))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Time</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required time-field"
         value="1:00 PM" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Time</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required time-field"
         value="2:00 PM" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - Timedelta
-----------------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.Timedelta(
  ...         title='Timedelta',
  ...         default=datetime.timedelta(days=3)),
  ...     default=(datetime.timedelta(days=4), datetime.timedelta(days=5)))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>Timedelta</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required timedelta-field"
         value="4 days, 0:00:00" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>Timedelta</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required timedelta-field"
         value="5 days, 0:00:00" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


Tuple - URI
-----------

  >>> field = zope.schema.Tuple(
  ...     value_type=zope.schema.URI(
  ...         title='URI',
  ...         default='http://zope.org'),
  ...     default=('http://www.python.org', 'http://www.zope.com'))
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.multi.MultiWidget'>

  >>> interfaces.IDataConverter(widget)
  <MultiConverter converts from Tuple to MultiWidget>

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>URI</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="bar.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-0"
         name="bar.0"
         class="text-widget required uri-field"
         value="http://www.python.org" />
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>URI</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="bar.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="foo-1"
         name="bar.1"
         class="text-widget required uri-field"
         value="http://www.zope.com" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="bar-buttons-add"
         name="bar.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="bar-buttons-remove"
         name="bar.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="bar.count" value="2" />


URI
---

  >>> field = zope.schema.URI(default='http://zope.org')
  >>> widget = setupWidget(field)
  >>> widget.update()

  >>> widget.__class__
  <class 'pyams_form.browser.text.TextWidget'>

  >>> interfaces.IDataConverter(widget)
  <FieldDataConverter converts from URI to TextWidget>

  >>> print(widget.render())
  <input type="text" id="foo" name="bar" class="text-widget required uri-field"
         value="http://zope.org" />

  >>> widget.mode = interfaces.DISPLAY_MODE
  >>> print(widget.render())
  <span id="foo" class="text-widget required uri-field">http://zope.org</span>

Calling the widget will return the widget including the layout

  >>> print(widget())
  <div id="foo-row"
       class="row-required row">
      <div class="label">
              <label for="foo">
                      <span></span>
              </label>
      </div>
      <div class="widget"><span id="foo"
        class="text-widget required uri-field">http://zope.org</span></div>
  </div>


Tests cleanup:

  >>> tearDown()
