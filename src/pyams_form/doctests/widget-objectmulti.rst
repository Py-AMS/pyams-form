Multi+Object Widget
-------------------

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

In order to not overwhelm you with our set of well-chosen defaults,
all the default component registrations have been made prior to doing those
examples:

  >>> from pyams_form import util, testing
  >>> testing.setup_form_defaults(config.registry)

As for all widgets, the multi widget must provide the new ``IWidget``
interface:

  >>> from pyams_form import interfaces
  >>> from pyams_form.browser import multi

  >>> interfaces.widget.IWidget.implementedBy(multi.MultiWidget)
  True

The widget can be instantiated only using the request:

  >>> from pyams_utils.testing import format_html
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
the widget does not know what sub-widgets to display. Now let's define a field
for this widget and check it again:

  >>> from pyams_form.widget import FieldWidget

  >>> from pyams_form.testing import IMySubObjectMulti
  >>> from pyams_form.testing import MySubObjectMulti

  >>> from pyams_form.object import register_factory_adapter
  >>> register_factory_adapter(IMySubObjectMulti, MySubObjectMulti)

  >>> import zope.schema
  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Object(title='my object widget',
  ...                                   schema=IMySubObjectMulti),
  ...     )

  >>> widget = FieldWidget(field, widget)
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
    <div class="buttons">
        <input type="submit"
         id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="0" />

As you can see, there is still no input value. Let's provide some values for
this widget.

It must not fail if we assign values that do not meet the constraints,
just cry about it in the HTML:

  >>> from pyams_form import object
  >>> widget.value = [object.ObjectWidgetValue(
  ...     {'foofield': '', 'barfield': '666'})]
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
          <div class="error"></div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="foo.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
                      <div class="error">Required input is missing.</div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-foofield"
         name="foo.0.widgets.foofield"
         class="text-widget required int-field"
         value="" />
              </div>
              <div class="label">
                      <label for="foo-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-barfield"
         name="foo.0.widgets.barfield"
         class="text-widget int-field"
         value="666" />
              </div>
      <input name="foo.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="foo-buttons-remove"
         name="foo.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="1" />


Let's set acceptable values:

  >>> widget.value = [
  ...     object.ObjectWidgetValue(dict(foofield='42', barfield='666')),
  ...     object.ObjectWidgetValue(dict(foofield='789', barfield='321'))]

  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="foo.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-foofield"
         name="foo.0.widgets.foofield"
         class="text-widget required int-field"
         value="42" />
              </div>
              <div class="label">
                      <label for="foo-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-barfield"
         name="foo.0.widgets.barfield"
         class="text-widget int-field"
         value="666" />
              </div>
      <input name="foo.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="foo.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-1-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-foofield"
         name="foo.1.widgets.foofield"
         class="text-widget required int-field"
         value="789" />
              </div>
              <div class="label">
                      <label for="foo-1-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-barfield"
         name="foo.1.widgets.barfield"
         class="text-widget int-field"
         value="321" />
              </div>
      <input name="foo.1-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="foo-buttons-remove"
         name="foo.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="2" />

Let's see what we get on value extraction:

  >>> widget.extract()
  <NO_VALUE>

If we now click on the ``Add`` button, we will get a new input field for enter
a new value:

  >>> widget.request = TestRequest(params={'foo.count': '2',
  ...                                      'foo.0.widgets.foofield': '42',
  ...                                      'foo.0.widgets.barfield': '666',
  ...                                      'foo.0-empty-marker': '1',
  ...                                      'foo.1.widgets.foofield': '789',
  ...                                      'foo.1.widgets.barfield': '321',
  ...                                      'foo.1-empty-marker': '1',
  ...                                      'foo.buttons.add': 'Add'})
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="foo.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-foofield"
         name="foo.0.widgets.foofield"
         class="text-widget required int-field"
         value="42" />
              </div>
              <div class="label">
                      <label for="foo-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-barfield"
         name="foo.0.widgets.barfield"
         class="text-widget int-field"
         value="666" />
              </div>
      <input name="foo.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="foo.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-1-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-foofield"
         name="foo.1.widgets.foofield"
         class="text-widget required int-field"
         value="789" />
              </div>
              <div class="label">
                      <label for="foo-1-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-barfield"
         name="foo.1.widgets.barfield"
         class="text-widget int-field"
         value="321" />
              </div>
      <input name="foo.1-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
      <div id="foo-2-row"
               class="row">
        <div class="label">
          <label for="foo-2">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-2-remove"
                   name="foo.2.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-2-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-2-widgets-foofield"
         name="foo.2.widgets.foofield"
         class="text-widget required int-field"
         value="" />
              </div>
              <div class="label">
                      <label for="foo-2-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-2-widgets-barfield"
         name="foo.2.widgets.barfield"
         class="text-widget int-field"
         value="2,222" />
              </div>
      <input name="foo.2-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="foo-buttons-remove"
         name="foo.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="3" />

Let's see what we get on value extraction:

  >>> from pprint import pprint
  >>> value = widget.extract()
  >>> pprint(value)
  [{'barfield': '666', 'foofield': '42'}, {'barfield': '321', 'foofield': '789'}]
  >>> converter = interfaces.IDataConverter(widget)

  >>> value = converter.to_field_value(value)
  >>> value
  [<pyams_form.testing.MySubObjectMulti object at ...>,
  <pyams_form.testing.MySubObjectMulti object at ...>]

  >>> value[0].foofield
  42
  >>> value[0].barfield
  666


Now let's store the new value:


  >>> widget.request = TestRequest(params={'foo.count': '3',
  ...                                      'foo.0.widgets.foofield': '42',
  ...                                      'foo.0.widgets.barfield': '666',
  ...                                      'foo.0-empty-marker': '1',
  ...                                      'foo.1.widgets.foofield': '789',
  ...                                      'foo.1.widgets.barfield': '321',
  ...                                      'foo.1-empty-marker': '1',
  ...                                      'foo.2.widgets.foofield': '46',
  ...                                      'foo.2.widgets.barfield': '98',
  ...                                      'foo.2-empty-marker': '1',
  ...                                    })
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="foo.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-foofield"
         name="foo.0.widgets.foofield"
         class="text-widget required int-field"
         value="42" />
              </div>
              <div class="label">
                      <label for="foo-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-barfield"
         name="foo.0.widgets.barfield"
         class="text-widget int-field"
         value="666" />
              </div>
      <input name="foo.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="foo.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-1-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-foofield"
         name="foo.1.widgets.foofield"
         class="text-widget required int-field"
         value="789" />
              </div>
              <div class="label">
                      <label for="foo-1-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-barfield"
         name="foo.1.widgets.barfield"
         class="text-widget int-field"
         value="321" />
              </div>
      <input name="foo.1-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
      <div id="foo-2-row"
               class="row">
        <div class="label">
          <label for="foo-2">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-2-remove"
                   name="foo.2.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-2-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-2-widgets-foofield"
         name="foo.2.widgets.foofield"
         class="text-widget required int-field"
         value="46" />
              </div>
              <div class="label">
                      <label for="foo-2-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-2-widgets-barfield"
         name="foo.2.widgets.barfield"
         class="text-widget int-field"
         value="98" />
              </div>
      <input name="foo.2-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="foo-buttons-remove"
         name="foo.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="3" />

Let's see what we get on value extraction:

  >>> value = widget.extract()
  >>> pprint(value)
  [{'barfield': '666', 'foofield': '42'},
   {'barfield': '321', 'foofield': '789'},
   {'barfield': '98', 'foofield': '46'}]
  >>> converter = interfaces.IDataConverter(widget)

  >>> value = converter.to_field_value(value)
  >>> value
  [<pyams_form.testing.MySubObjectMulti object at ...>,
  <pyams_form.testing.MySubObjectMulti object at ...>]

  >>> value[0].foofield
  42
  >>> value[0].barfield
  666


As you can see in the above sample, the new stored value gets rendered as a
real value and the new adding value input field is gone. Now let's try to
remove an existing value:

  >>> widget.request = TestRequest(params={'foo.count':'3',
  ...                                      'foo.0.widgets.foofield':'42',
  ...                                      'foo.0.widgets.barfield':'666',
  ...                                      'foo.0-empty-marker':'1',
  ...                                      'foo.1.widgets.foofield':'789',
  ...                                      'foo.1.widgets.barfield':'321',
  ...                                      'foo.1-empty-marker':'1',
  ...                                      'foo.2.widgets.foofield':'46',
  ...                                      'foo.2.widgets.barfield':'98',
  ...                                      'foo.2-empty-marker':'1',
  ...                                      'foo.1.remove':'1',
  ...                                      'foo.buttons.remove':'Remove selected'})
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="foo.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-foofield"
         name="foo.0.widgets.foofield"
         class="text-widget required int-field"
         value="42" />
              </div>
              <div class="label">
                      <label for="foo-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-barfield"
         name="foo.0.widgets.barfield"
         class="text-widget int-field"
         value="666" />
              </div>
      <input name="foo.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="foo.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-1-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-foofield"
         name="foo.1.widgets.foofield"
         class="text-widget required int-field"
         value="46" />
              </div>
              <div class="label">
                      <label for="foo-1-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-barfield"
         name="foo.1.widgets.barfield"
         class="text-widget int-field"
         value="98" />
              </div>
      <input name="foo.1-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="foo-buttons-remove"
         name="foo.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="2" />

Let's see what we get on value extraction:
(this is good so, because Remove selected is a widget-internal submit)

  >>> value = widget.extract()
  >>> pprint(value)
  [{'barfield': '666', 'foofield': '42'},
   {'barfield': '321', 'foofield': '789'},
   {'barfield': '98', 'foofield': '46'}]
  >>> converter = interfaces.IDataConverter(widget)

  >>> value = converter.to_field_value(value)
  >>> value
  [<pyams_form.testing.MySubObjectMulti object at ...>,
  <pyams_form.testing.MySubObjectMulti object at ...>]

  >>> value[0].foofield
  42
  >>> value[0].barfield
  666


Error handling is next. Let's use the value "bad" (an invalid integer literal)
as input for our internal (sub) widget.

  >>> widget.request = TestRequest(params={'foo.count':'2',
  ...                                      'foo.0.widgets.foofield':'42',
  ...                                      'foo.0.widgets.barfield':'666',
  ...                                      'foo.0-empty-marker':'1',
  ...                                      'foo.1.widgets.foofield':'bad',
  ...                                      'foo.1.widgets.barfield':'98',
  ...                                      'foo.1-empty-marker':'1',
  ...                                      })

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="label">
          <label for="foo-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="foo.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-foofield"
         name="foo.0.widgets.foofield"
         class="text-widget required int-field"
         value="42" />
              </div>
              <div class="label">
                      <label for="foo-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-barfield"
         name="foo.0.widgets.barfield"
         class="text-widget int-field"
         value="666" />
              </div>
      <input name="foo.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="label">
          <label for="foo-1">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
          <div class="error">The entered value is not a valid integer literal.</div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="foo.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-1-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
                      <div class="error">The entered value is not a valid integer literal.</div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-foofield"
         name="foo.1.widgets.foofield"
         class="text-widget required int-field"
         value="bad" />
              </div>
              <div class="label">
                      <label for="foo-1-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-barfield"
         name="foo.1.widgets.barfield"
         class="text-widget int-field"
         value="98" />
              </div>
      <input name="foo.1-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="foo-buttons-remove"
         name="foo.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="2" />

Let's see what we get on value extraction:

  >>> value = widget.extract()
  >>> pprint(value)
  [{'barfield': '666', 'foofield': '42'},
   {'barfield': '98', 'foofield': 'bad'}]


Label
#####

There is an option which allows to disable the label for the (sub) widgets.
You can set the `show_label` option to `False` which will skip rendering the
labels. Alternatively you can also register your own template for your layer
if you like to skip the label rendering for all widgets.


  >>> field = zope.schema.List(
  ...     __name__='foo',
  ...     value_type=zope.schema.Object(title=u'ignored_title',
  ...                                   schema=IMySubObjectMulti),
  ...     )
  >>> request = TestRequest()
  >>> widget = multi.MultiWidget(request)
  >>> widget = FieldWidget(field, widget)
  >>> widget.value = [
  ...     object.ObjectWidgetValue(dict(foofield='42', barfield='666')),
  ...     object.ObjectWidgetValue(dict(foofield='789', barfield='321'))]
  >>> widget.show_label = False
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="multi-widget required">
      <div id="foo-0-row"
               class="row">
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-0-remove"
                   name="foo.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-foofield"
         name="foo.0.widgets.foofield"
         class="text-widget required int-field"
         value="42" />
              </div>
              <div class="label">
                      <label for="foo-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-0-widgets-barfield"
         name="foo.0.widgets.barfield"
         class="text-widget int-field"
         value="666" />
              </div>
      <input name="foo.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
      <div id="foo-1-row"
               class="row">
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="foo-1-remove"
                   name="foo.1.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="foo-1-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-foofield"
         name="foo.1.widgets.foofield"
         class="text-widget required int-field"
         value="789" />
              </div>
              <div class="label">
                      <label for="foo-1-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="foo-1-widgets-barfield"
         name="foo.1.widgets.barfield"
         class="text-widget int-field"
         value="321" />
              </div>
      <input name="foo.1-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="foo-buttons-add"
         name="foo.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="foo-buttons-remove"
         name="foo.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="foo.count" value="2" />


In a form
#########

Let's try a simple example in a form.

Forms and our objectwidget fire events on add and edit, setup a subscriber
for those:

  >>> eventlog = []
  >>> import zope.lifecycleevent
  >>> @zope.component.adapter(zope.lifecycleevent.ObjectModifiedEvent)
  ... def logEvent(event):
  ...     eventlog.append(event)
  >>> _ = config.add_subscriber(logEvent, zope.lifecycleevent.interfaces.IObjectCreatedEvent)
  >>> _ = config.add_subscriber(logEvent, zope.lifecycleevent.interfaces.IObjectModifiedEvent)

  >>> def printEvents():
  ...     for event in eventlog:
  ...         print(event)
  ...         if isinstance(event, zope.lifecycleevent.ObjectModifiedEvent):
  ...             for attr in event.descriptions:
  ...                 print(attr.interface)
  ...                 print(sorted(attr.attributes))

We define an interface containing a subobject, and an addform for it:

  >>> from pyams_form import form, field
  >>> from pyams_form.testing import MyMultiObject, IMyMultiObject

Note, that creating an object will print some information about it:

  >>> class MyAddForm(form.AddForm):
  ...     fields = field.Fields(IMyMultiObject)
  ...     def create(self, data):
  ...         print("MyAddForm.create")
  ...         pprint(data)
  ...         return MyMultiObject(**data)
  ...     def add(self, obj):
  ...         self.context[obj.name] = obj
  ...     def nextURL(self):
  ...         pass

We create the form and try to update it:

  >>> from zope.container.folder import Folder
  >>> root = Folder()
  >>> request = TestRequest()
  >>> myaddform =  MyAddForm(root, request)

  >>> myaddform.update()

As usual, the form contains a widget manager with the expected widget

  >>> list(myaddform.widgets.keys())
  ['list_of_objects', 'name']
  >>> list(myaddform.widgets.values())
  [<MultiWidget 'form.widgets.list_of_objects'>, <TextWidget 'form.widgets.name'>]

If we want to render the addform, we must give it a template:

  >>> import os
  >>> from pyams_template.interfaces import IContentTemplate
  >>> from pyams_template.template import TemplateFactory
  >>> from pyams_layer.interfaces import IFormLayer
  >>> from pyams_form import tests
  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-edit.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, MyAddForm), IContentTemplate)

Now rendering the addform renders no items yet:

  >>> print(format_html(myaddform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-list_of_objects">My list field</label>
      <div class="multi-widget required">
    <div class="buttons">
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-add"
         name="form.widgets.list_of_objects.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </div>
  <input type="hidden" name="form.widgets.list_of_objects.count" value="0" />
    </div>
    <div class="row">
      <label for="form-widgets-name">name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-add"
         name="form.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </form>

We don't have the object (yet) in the root:

  >>> root['first']
  Traceback (most recent call last):
  ...
  KeyError: 'first'

Add a row to the multi widget:

  >>> request = TestRequest(params={
  ...     'form.widgets.list_of_objects.count':'0',
  ...     'form.widgets.list_of_objects.buttons.add':'Add'})
  >>> myaddform.request = request

Update with the request:

  >>> myaddform.update()

Render the form:

  >>> print(format_html(myaddform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-list_of_objects">My list field</label>
      <div class="multi-widget required">
      <div id="form-widgets-list_of_objects-0-row"
               class="row">
        <div class="label">
          <label for="form-widgets-list_of_objects-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="form-widgets-list_of_objects-0-remove"
                   name="form.widgets.list_of_objects.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-list_of_objects-0-widgets-foofield"
         name="form.widgets.list_of_objects.0.widgets.foofield"
         class="text-widget required int-field"
         value="" />
              </div>
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-list_of_objects-0-widgets-barfield"
         name="form.widgets.list_of_objects.0.widgets.barfield"
         class="text-widget int-field"
         value="2,222" />
              </div>
      <input name="form.widgets.list_of_objects.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-add"
         name="form.widgets.list_of_objects.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-remove"
         name="form.widgets.list_of_objects.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="form.widgets.list_of_objects.count" value="1" />
    </div>
    <div class="row">
      <label for="form-widgets-name">name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-add"
         name="form.buttons.add"
         class="submit-widget button-field"
         value="Add" />
    </div>
  </form>

Now we can fill in some values to the object, and a name to the whole schema:

  >>> request = TestRequest(params={
  ...     'form.widgets.list_of_objects.count':'1',
  ...     'form.widgets.list_of_objects.0.widgets.foofield':'66',
  ...     'form.widgets.list_of_objects.0.widgets.barfield':'99',
  ...     'form.widgets.list_of_objects.0-empty-marker':'1',
  ...     'form.widgets.name':'first',
  ...     'form.buttons.add':'Add'})
  >>> myaddform.request = request

Update the form with the request:

  >>> myaddform.update()
  MyAddForm.create
  {'list_of_objects': [<pyams_form.testing.MySubObjectMulti ...],
   'name': 'first'}

Wow, it got added:

  >>> root['first']
  <pyams_form.testing.MyMultiObject object at ...>

  >>> root['first'].list_of_objects
  [<pyams_form.testing.MySubObjectMulti object at ...>]

Field values need to be right:

  >>> root['first'].list_of_objects[0].foofield
  66
  >>> root['first'].list_of_objects[0].barfield
  99

Let's see our event log:

  >>> len(eventlog)
  5

((why is IMySubObjectMulti created twice???))

  >>> printEvents()
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMySubObjectMulti>
  ['barfield', 'foofield']
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMySubObjectMulti>
  ['barfield', 'foofield']
  <zope...ObjectCreatedEvent object at ...>

# TODO: look for missing ContainerModifiedEvent!!!

  >>> eventlog = []

Let's try to edit that newly added object:

  >>> class MyEditForm(form.EditForm):
  ...     fields = field.Fields(IMyMultiObject)

  >>> editform = MyEditForm(root['first'], TestRequest())
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, MyEditForm), IContentTemplate)
  >>> editform.update()

Watch for the widget values in the HTML:

  >>> print(format_html(editform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-list_of_objects">My list field</label>
      <div class="multi-widget required">
      <div id="form-widgets-list_of_objects-0-row"
               class="row">
        <div class="label">
          <label for="form-widgets-list_of_objects-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="form-widgets-list_of_objects-0-remove"
                   name="form.widgets.list_of_objects.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-list_of_objects-0-widgets-foofield"
         name="form.widgets.list_of_objects.0.widgets.foofield"
         class="text-widget required int-field"
         value="66" />
              </div>
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-list_of_objects-0-widgets-barfield"
         name="form.widgets.list_of_objects.0.widgets.barfield"
         class="text-widget int-field"
         value="99" />
              </div>
      <input name="form.widgets.list_of_objects.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-add"
         name="form.widgets.list_of_objects.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-remove"
         name="form.widgets.list_of_objects.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="form.widgets.list_of_objects.count" value="1" />
    </div>
    <div class="row">
      <label for="form-widgets-name">name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="first" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field"
         value="Apply" />
    </div>
  </form>

Let's modify the values:

  >>> request = TestRequest(params={
  ...     'form.widgets.list_of_objects.count':'1',
  ...     'form.widgets.list_of_objects.0.widgets.foofield':'43',
  ...     'form.widgets.list_of_objects.0.widgets.barfield':'55',
  ...     'form.widgets.list_of_objects.0-empty-marker':'1',
  ...     'form.widgets.name':'first',
  ...     'form.buttons.apply':'Apply'})

They are still the same:

  >>> root['first'].list_of_objects[0].foofield
  66
  >>> root['first'].list_of_objects[0].barfield
  99

  >>> editform.request = request
  >>> editform.update()

Until we have updated the form:

  >>> root['first'].list_of_objects[0].foofield
  43
  >>> root['first'].list_of_objects[0].barfield
  55

Let's see our event log:

  >>> len(eventlog)
  5

((TODO: now this is real crap here, why is IMySubObjectMulti created 3 times???))

  >>> printEvents()
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMySubObjectMulti>
  ['barfield', 'foofield']
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMySubObjectMulti>
  ['barfield', 'foofield']
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMyMultiObject>
  ['list_of_objects']

  >>> eventlog=[]


After the update the form says that the values got updated and renders the new
values:

  >>> print(format_html(editform.render()))
  <i>Data successfully updated.</i>
  <form action=".">
    <div class="row">
      <label for="form-widgets-list_of_objects">My list field</label>
      <div class="multi-widget required">
      <div id="form-widgets-list_of_objects-0-row"
               class="row">
        <div class="label">
          <label for="form-widgets-list_of_objects-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="form-widgets-list_of_objects-0-remove"
                   name="form.widgets.list_of_objects.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-list_of_objects-0-widgets-foofield"
         name="form.widgets.list_of_objects.0.widgets.foofield"
         class="text-widget required int-field"
         value="43" />
              </div>
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-list_of_objects-0-widgets-barfield"
         name="form.widgets.list_of_objects.0.widgets.barfield"
         class="text-widget int-field"
         value="55" />
              </div>
      <input name="form.widgets.list_of_objects.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-add"
         name="form.widgets.list_of_objects.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-remove"
         name="form.widgets.list_of_objects.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="form.widgets.list_of_objects.count" value="1" />
    </div>
    <div class="row">
      <label for="form-widgets-name">name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="first" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field"
         value="Apply" />
    </div>
  </form>


Let's see if the widget keeps the old object on editing:

We add a special property to keep track of the object:

  >>> root['first'].list_of_objects[0].__marker__ = "ThisMustStayTheSame"

  >>> root['first'].list_of_objects[0].foofield
  43
  >>> root['first'].list_of_objects[0].barfield
  55

Let's modify the values:

  >>> request = TestRequest(params={
  ...     'form.widgets.list_of_objects.count':'1',
  ...     'form.widgets.list_of_objects.0.widgets.foofield':'666',
  ...     'form.widgets.list_of_objects.0.widgets.barfield':'999',
  ...     'form.widgets.list_of_objects.0-empty-marker':'1',
  ...     'form.widgets.name':'first',
  ...     'form.buttons.apply':'Apply'})

  >>> editform.request = request

  >>> editform.update()

Let's check what are ther esults of the update:

  >>> root['first'].list_of_objects[0].foofield
  666
  >>> root['first'].list_of_objects[0].barfield
  999

((TODO: bummer... we can't keep the old object))

  #>>> root['first'].list_of_objects[0].__marker__
  #'ThisMustStayTheSame'


Let's make a nasty error, by typing 'bad' instead of an integer:

  >>> request = TestRequest(params={
  ...     'form.widgets.list_of_objects.count':'1',
  ...     'form.widgets.list_of_objects.0.widgets.foofield':'99',
  ...     'form.widgets.list_of_objects.0.widgets.barfield':'bad',
  ...     'form.widgets.list_of_objects.0-empty-marker':'1',
  ...     'form.widgets.name':'first',
  ...     'form.buttons.apply':'Apply'})

  >>> editform.request = request
  >>> eventlog=[]
  >>> editform.update()

Eventlog must be clean:

  >>> len(eventlog)
  2

((TODO: bummer... who creates those 2 objects???))

  >>> printEvents()
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectCreatedEvent object at ...>


Watch for the error message in the HTML:
it has to appear at the field itself and at the top of the form:
((not nice: at the top ``Object is of wrong type.`` appears))

  >>> print(format_html(editform.render()))
  <i>There were some errors.</i>
  <ul>
    <li>
        My list field
      <div class="error">The entered value is not a valid integer literal.</div>
    </li>
  </ul>
  <form action=".">
    <div class="row">
      <b><div class="error">The entered value is not a valid integer literal.</div></b>
      <label for="form-widgets-list_of_objects">My list field</label>
      <div class="multi-widget required">
      <div id="form-widgets-list_of_objects-0-row"
               class="row">
        <div class="label">
          <label for="form-widgets-list_of_objects-0">
            <span>my object widget</span>
            <span class="required">*</span>
          </label>
        </div>
          <div class="error">The entered value is not a valid integer literal.</div>
        <div class="widget">
          <div class="multi-widget-checkbox">
            <input type="checkbox"
                   id="form-widgets-list_of_objects-0-remove"
                   name="form.widgets.list_of_objects.0.remove"
                   class="multi-widget-checkbox checkbox-widget"
                   value="1" />
          </div>
          <div class="multi-widget-input">
            <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-list_of_objects-0-widgets-foofield"
         name="form.widgets.list_of_objects.0.widgets.foofield"
         class="text-widget required int-field"
         value="99" />
              </div>
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
                      <div class="error">The entered value is not a valid integer literal.</div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-list_of_objects-0-widgets-barfield"
         name="form.widgets.list_of_objects.0.widgets.barfield"
         class="text-widget int-field"
         value="bad" />
              </div>
      <input name="form.widgets.list_of_objects.0-empty-marker" type="hidden" value="1"/>
  </div>
          </div>
        </div>
      </div>
    <div class="buttons">
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-add"
         name="form.widgets.list_of_objects.buttons.add"
         class="submit-widget button-field"
         value="Add" />
        <input type="submit"
         id="form-widgets-list_of_objects-buttons-remove"
         name="form.widgets.list_of_objects.buttons.remove"
         class="submit-widget button-field"
         value="Remove selected" />
    </div>
  </div>
  <input type="hidden" name="form.widgets.list_of_objects.count" value="1" />
    </div>
    <div class="row">
      <label for="form-widgets-name">name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="first" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field"
         value="Apply" />
    </div>
  </form>

The object values must stay at the old ones:

  >>> root['first'].list_of_objects[0].foofield
  666
  >>> root['first'].list_of_objects[0].barfield
  999



Simple but often used use-case is the display form:

  >>> editform = MyEditForm(root['first'], TestRequest())
  >>> editform.mode = interfaces.DISPLAY_MODE
  >>> editform.update()
  >>> print(format_html(editform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-list_of_objects">My list field</label>
      <div id="form-widgets-list_of_objects"
       class="multi-widget">
      <div id="form-widgets-list_of_objects-0-row"
               class="row">
          <div class="label">
            <label for="form-widgets-list_of_objects-0">
              <span>my object widget</span>
              <span class="required">*</span>
            </label>
          </div>
          <div class="widget">
            <div class="multi-widget-display">
              <div class="object-widget">
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-foofield">
                  <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <span id="form-widgets-list_of_objects-0-widgets-foofield"
        class="text-widget int-field">666</span>
              </div>
              <div class="label">
                      <label for="form-widgets-list_of_objects-0-widgets-barfield">
                  <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <span id="form-widgets-list_of_objects-0-widgets-barfield"
        class="text-widget int-field">999</span>
              </div>
  </div>
            </div>
          </div>
      </div>
  </div>
    </div>
    <div class="row">
      <label for="form-widgets-name">name</label>
      <span id="form-widgets-name"
        class="text-widget textline-field">first</span>
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field"
         value="Apply" />
    </div>
  </form>


Tests cleanup:

  >>> tearDown()
