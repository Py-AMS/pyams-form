Multi Widget
------------

The multi widget allows you to add and edit one or more values.

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

As for all widgets, the multi widget must provide the new ``IWidget``
interface:

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import multi

  >>> interfaces.widget.IWidget.implementedBy(multi.MultiWidget)
  True

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

We can now render the widget:

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="0" />

As you can see the widget is empty and doesn't provide values. This is because
the widget does not know what sub-widgets to display. Since the widget doesn't provide a
field nothing useful gets rendered. Now let's define a field for this widget and check it:

  >>> import zope.schema
  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="0" />

As you can see, there is still no input value. Let's provide some values for
this widget.

  >>> widget.value = ['42', '43']
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

If we now click on the ``Add`` button, we will get a new input field for enter
a new value:

  >>> widget.request = TestRequest(params={'widget.name.count':'2',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.1':'43',
  ...                                      'widget.name.buttons.add':'Add'})
  >>> widget.update()

  >>> widget.extract()
  ['42', '43']

  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
      <div id="widget-id-2-row"
               class="row">
        <div class="label">
          <label for="widget-id-2">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-2-remove"
                   name="widget.name.2.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-2"
         name="widget.name.2"
         class="text-widget required int-field"
         value="" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="3" />

Now let's store the new value:

  >>> widget.request = TestRequest(params={'widget.name.count':'3',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.1':'43',
  ...                                      'widget.name.2':'44'})
  >>> widget.update()

  >>> widget.extract()
  ['42', '43', '44']

  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
      <div id="widget-id-2-row"
               class="row">
        <div class="label">
          <label for="widget-id-2">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-2-remove"
                   name="widget.name.2.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-2"
         name="widget.name.2"
         class="text-widget required int-field"
         value="44" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="3" />

As you can see in the above sample, the new stored value get rendered as a
real value and the new adding value input field is gone. Now let's try to
remove an existing value:

  >>> widget.request = TestRequest(params={'widget.name.count':'3',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.1':'43',
  ...                                      'widget.name.2':'44',
  ...                                      'widget.name.1.remove':'1',
  ...                                      'widget.name.buttons.remove':'Remove selected'})
  >>> widget.update()

This is good so, because the Remove selected is an widget-internal submit action

  >>> widget.extract()
  ['42', '43', '44']

  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="44" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

Change again a value after delete:

  >>> widget.request = TestRequest(params={'widget.name.count':'2',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.1':'45'})
  >>> widget.update()

  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="45" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

Error handling is next. Let's use the value "bad" (an invalid integer literal)
as input for our internal (sub) widget.

  >>> widget.request = TestRequest(params={'widget.name.count':'2',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.1':'bad'})
  >>> widget.update()

  >>> widget.extract()
  ['42', 'bad']

  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
          <div class="error">The entered value is not a valid integer literal.</div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="bad" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

The widget filters out the add and remove buttons depending on the
current value and the field constraints. You already saw that there's
no remove button for empty value. Now, let's check rendering with
minimum and maximum lengths defined in the field constraints.

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     min_length=1,
  ...     max_length=3
  ...     )
  >>> widget.field = field
  >>> widget.widgets = []
  >>> widget.value = []

Let's test with minimum sequence, there should be no remove button:

  >>> widget.request = TestRequest(params={'widget.name.count':'1',
  ...                                      'widget.name.0':'42'})
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="1" />

Now, with middle-length sequence. All buttons should be there.

  >>> widget.request = TestRequest(params={'widget.name.count':'2',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.1':'43'})
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

Okay, now let's check the maximum-length sequence. There should be
no add button:

  >>> widget.request = TestRequest(params={'widget.name.count':'3',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.1':'43',
  ...                                      'widget.name.2':'44'})
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
      <div id="widget-id-2-row"
               class="row">
        <div class="label">
          <label for="widget-id-2">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-2-remove"
                   name="widget.name.2.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-2"
         name="widget.name.2"
         class="text-widget required int-field"
         value="44" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="3" />


Dictionaries
############

The multi widget also supports IDict schemas.

  >>> field = zope.schema.Dict(
  ...     __name__='foo',
  ...     key_type=zope.schema.Int(title='Number'),
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.widgets = []
  >>> widget.value = [('1','42')]
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
          <div class="label">
            <label for="widget-id-key-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-input-key">
              <input type="text"
         id="widget-id-key-0"
         name="widget.name.key.0"
         class="text-widget required int-field"
         value="1" />
            </div>
          </div>
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="1" />

If we now click on the ``Add`` button, we will get a new input field for entering
a new value:

  >>> widget.request = TestRequest(params={'widget.name.count':'1',
  ...                                      'widget.name.key.0':'1',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.buttons.add':'Add'})
  >>> widget.update()

  >>> widget.extract()
  [('1', '42')]

  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
          <div class="label">
            <label for="widget-id-key-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-input-key">
              <input type="text"
         id="widget-id-key-0"
         name="widget.name.key.0"
         class="text-widget required int-field"
         value="1" />
            </div>
          </div>
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
          <div class="label">
            <label for="widget-id-key-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-input-key">
              <input type="text"
         id="widget-id-key-1"
         name="widget.name.key.1"
         class="text-widget required int-field"
         value="" />
            </div>
          </div>
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />

Now let's store the new value:

  >>> widget.request = TestRequest(params={'widget.name.count':'2',
  ...                                      'widget.name.key.0':'1',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.key.1':'2',
  ...                                      'widget.name.1':'43'})
  >>> widget.update()

  >>> widget.extract()
  [('1', '42'), ('2', '43')]

We will get an error if we try and set the same key twice

  >>> widget.request = TestRequest(params={'widget.name.count':'2',
  ...                                      'widget.name.key.0':'1',
  ...                                      'widget.name.0':'42',
  ...                                      'widget.name.key.1':'1',
  ...                                      'widget.name.1':'43'})
  >>> widget.update()

  >>> widget.extract()
  [('1', '42'), ('1', '43')]

  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
          <div class="label">
            <label for="widget-id-key-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-input-key">
              <input type="text"
         id="widget-id-key-0"
         name="widget.name.key.0"
         class="text-widget required int-field"
         value="1" />
            </div>
          </div>
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
          <div class="label">
            <label for="widget-id-key-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
            <div class="error">Duplicate key</div>
          <div class="widget">
            <div class="multi-widget-input-key">
              <input type="text"
         id="widget-id-key-1"
         name="widget.name.key.1"
         class="text-widget required int-field"
         value="1" />
            </div>
          </div>
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-name-buttons-remove"
         name="widget.name.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="2" />


Displaying
##########

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Set the mode to DISPLAY_MODE:

  >>> widget.mode = interfaces.DISPLAY_MODE

We can now render the widget:

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div id="widget-id"
       class="multi-widget">
  </div>

As you can see the widget is empty and doesn't provide values. This is because
the widget does not know what sub-widgets to display. Since the widget doesn't
provide a field nothing useful gets rendered. Now let's define a field for this
widget and check it again:

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div id="widget-id"
       class="multi-widget">
  </div>

As you can see, there is still no input value. Let's provide some values for
this widget. Before we can do that, we will need to register a data converter
for our multi widget and the data converter dispatcher adapter, which is done
automatically when including package:

  >>> widget.update()
  >>> widget.value = ['42', '43']
  >>> print(format_html(widget.render()))
  <div id="widget-id"
       class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-display">
              <span id="widget-id-0"
        class="text-widget int-field">42</span>
            </div>
          </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-display">
              <span id="widget-id-1"
        class="text-widget int-field">43</span>
            </div>
          </div>
      </div>
  </div>

We can also use the multi widget with dictionaries:

  >>> field = zope.schema.Dict(
  ...     __name__='foo',
  ...     key_type=zope.schema.Int(title='Number'),
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.value = [('1', '42'), ('2', '43')]
  >>> print(format_html(widget.render()))
  <div id="widget-id"
       class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
          <div class="label">
            <label for="widget-id-key-0">
                <span>Number"</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <div class="multi-widget-display">
                <span id="widget-id-key-0"
        class="text-widget int-field">1</span>
              </div>
            </div>
          <div class="label">
            <label for="widget-id-0">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-display">
              <span id="widget-id-0"
        class="text-widget int-field">42</span>
            </div>
          </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
          <div class="label">
            <label for="widget-id-key-1">
                <span>Number"</span>
                <span class="required">*</span>
              </label>
            </div>
            <div class="widget">
              <div class="multi-widget-display">
                <span id="widget-id-key-1"
        class="text-widget int-field">2</span>
              </div>
            </div>
          <div class="label">
            <label for="widget-id-1">
              <span>Number</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-display">
              <span id="widget-id-1"
        class="text-widget int-field">43</span>
            </div>
          </div>
      </div>
  </div>


Hidden mode
###########

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Set the mode to HIDDEN_MODE:

  >>> widget.mode = interfaces.HIDDEN_MODE

We can now render the widget:

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <input type="hidden" name="widget.name.count" value="0" />

As you can see the widget is empty and doesn't provide values. This is because
the widget does not know what sub-widgets to display.

Since the widget doesn't provide a field nothing useful
gets rendered. Now let's define a field for this widget and check it again:

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <input type="hidden" name="widget.name.count" value="0" />

As you can see, there is still no input value. Let's provide some values for
this widget. Before we can do that, we will need to register a data converter
for our multi widget and the data converter dispatcher adapter:

  >>> widget.update()
  >>> widget.value = ['42', '43']
  >>> print(format_html(widget.render()))
      <input type="hidden"
         id="widget-id-0"
         name="widget.name.0"
         value="42"
         class="hidden-widget" />
      <input type="hidden"
         id="widget-id-1"
         name="widget.name.1"
         value="43"
         class="hidden-widget" />
  <input type="hidden" name="widget.name.count" value="2" />

We can also use the multi widget with dictionaries:

  >>> field = zope.schema.Dict(
  ...     __name__='foo',
  ...     key_type=zope.schema.Int(title='Number'),
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> widget.field = field
  >>> widget.value = [('1', '42'), ('2', '43')]
  >>> print(format_html(widget.render()))
              <input type="hidden"
         id="widget-id-key-0"
         name="widget.name.key.0"
         value="1"
         class="hidden-widget" />
      <input type="hidden"
         id="widget-id-0"
         name="widget.name.0"
         value="42"
         class="hidden-widget" />
              <input type="hidden"
         id="widget-id-key-1"
         name="widget.name.key.1"
         value="2"
         class="hidden-widget" />
      <input type="hidden"
         id="widget-id-1"
         name="widget.name.1"
         value="43"
         class="hidden-widget" />
  <input type="hidden" name="widget.name.count" value="2" />


Label
#####

There is an option which allows to disable the label for the subwidgets.
You can set the `show_label` option to `False` which will skip rendering the
labels. Alternatively you can also register your own template for your layer
if you like to skip the label rendering for all widgets. One more way
is to register an attribute adapter for specific field/widget/layer/etc.
See below for an example.

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(
  ...         title='Ignored'),
  ...     )
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)
  >>> widget.field = field
  >>> widget.value = ['42', '43']
  >>> widget.show_label = False
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="None-0-row"
               class="row">
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="None-0-remove"
                   name="None.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="None-0"
         name="None.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="None-1-row"
               class="row">
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="None-1-remove"
                   name="None.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="None-1"
         name="None.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-buttons-add"
         name="widget.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-buttons-remove"
         name="widget.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="None.count" value="2" />

We can also override the show_label attribute value with an attribute
adapter. We set it to False for our widget before, but the update method
sets adapted attributes, so if we provide an attribute, it will be used
to set the ``show_label``. Let's see.

  >>> from pyams_form.widget import StaticWidgetAttribute

  >>> doShowLabel = StaticWidgetAttribute(True, widget=widget)
  >>> config.registry.registerAdapter(doShowLabel, name="show_label")

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="None-0-row"
               class="row">
        <div class="label">
          <label for="None-0">
            <span>Ignored</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="None-0-remove"
                   name="None.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="None-0"
         name="None.0"
         class="text-widget required int-field"
         value="42" />
          </div>
        </div>
      </div>
      <div id="None-1-row"
               class="row">
        <div class="label">
          <label for="None-1">
            <span>Ignored</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="None-1-remove"
                   name="None.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="None-1"
         name="None.1"
         class="text-widget required int-field"
         value="43" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-buttons-add"
         name="widget.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="widget-buttons-remove"
         name="widget.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="None.count" value="2" />


Coverage happiness
##################

  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Int(title='Number'),
  ...     )
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)
  >>> widget.field = field
  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'
  >>> widget.widgets = []
  >>> widget.value = []

  >>> widget.request = TestRequest()
  >>> widget.update()

  >>> widget.value = ['42', '43', '44']
  >>> widget.value = ['99']

  >>> print(format_html(widget.render()))
  <div class="multi-widget">
      <div id="widget-id-0-row"
               class="row">
        <div class="label">
          <label for="widget-id-0">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-0-remove"
                   name="widget.name.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-0"
         name="widget.name.0"
         class="text-widget required int-field"
         value="99" />
          </div>
        </div>
      </div>
      <div id="widget-id-1-row"
               class="row">
        <div class="label">
          <label for="widget-id-1">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-1-remove"
                   name="widget.name.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-1"
         name="widget.name.1"
         class="text-widget required int-field"
         value="" />
          </div>
        </div>
      </div>
      <div id="widget-id-2-row"
               class="row">
        <div class="label">
          <label for="widget-id-2">
            <span>Number</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="widget-id-2-remove"
                   name="widget.name.2.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <input type="text"
         id="widget-id-2"
         name="widget.name.2"
         class="text-widget required int-field"
         value="" />
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="widget-name-buttons-add"
         name="widget.name.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </div>
  <input type="hidden" name="widget.name.count" value="3" />


Tests cleanup:

  >>> tearDown()
