ObjectWidget
------------

The `ObjectWidget` widget is about rendering a schema's fields as a single
widget.

There are way too many preconditions to exercise the `ObjectWidget` as it
relies heavily on the from and widget framework. It renders the sub-widgets in
a sub-form.

In order to not overwhelm you with our set of well-chosen defaults,
all the default component registrations have been made prior to doing those
examples:

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

  >>> from pyams_form.testing import IMySubObject
  >>> from pyams_form.testing import IMySecond
  >>> from pyams_form.testing import MySubObject
  >>> from pyams_form.testing import MySecond

As for all widgets, the objectwidget must provide the new `IWidget`
interface:

  >>> from pyams_form import interfaces
  >>> import pyams_form.browser.object

  >>> interfaces.widget.IWidget.implementedBy(pyams_form.browser.object.ObjectWidget)
  True

The widget can be instantiated only using the request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()
  >>> widget = pyams_form.browser.object.ObjectWidget(request)

Before rendering the widget, one has to set the name and id of the widget:

  >>> widget.id = 'widget-id'
  >>> widget.name = 'widget.name'

Also, stand-alone widgets need to ignore the context:

  >>> widget.ignoreContext = True

There is no life for ObjectWidget without a schema to render:

  >>> widget.update()
  Traceback (most recent call last):
  ...
  ValueError: <ObjectWidget 'widget.name'> .field is None,
              that's a blocking point

This schema is specified by the field:

  >>> from pyams_form.widget import FieldWidget
  >>> from pyams_form.testing import IMySubObject
  >>> import zope.schema
  >>> field = zope.schema.Object(
  ...     __name__='subobject',
  ...     title='my object widget',
  ...     schema=IMySubObject)

Apply the field nicely with the helper:

  >>> widget = FieldWidget(field, widget)

We can now render the widget:

  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="object-widget required">
              <div class="label">
                      <label for="subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="subobject-widgets-foofield"
         name="subobject.widgets.foofield"
         class="text-widget required int-field"
         value="1,111" />
              </div>
              <div class="label">
                      <label for="subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="subobject-widgets-barfield"
         name="subobject.widgets.barfield"
         class="text-widget int-field"
         value="2,222" />
              </div>
      <input name="subobject-empty-marker" type="hidden" value="1"/>
  </div>


As you see all sort of default values are rendered.

Let's provide a more meaningful value:

  >>> from pyams_form.testing import MySubObject
  >>> v = MySubObject()
  >>> v.foofield = 42
  >>> v.barfield = 666
  >>> v.__marker__ = "ThisMustStayTheSame"


  >>> widget.ignore_context = False
  >>> widget.value = dict(foofield='42', barfield='666')

  >>> widget.update()

  >>> print(format_html(widget.render()))
  <div class="object-widget required">
              <div class="label">
                      <label for="subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="subobject-widgets-foofield"
         name="subobject.widgets.foofield"
         class="text-widget required int-field"
         value="42" />
              </div>
              <div class="label">
                      <label for="subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="subobject-widgets-barfield"
         name="subobject.widgets.barfield"
         class="text-widget int-field"
         value="666" />
              </div>
      <input name="subobject-empty-marker" type="hidden" value="1"/>
  </div>


The widget's value is NO_VALUE until it gets a request:

  >>> widget.value
  <NO_VALUE>

Let's fill in some values via the request:

  >>> widget.request = TestRequest(params={'subobject.widgets.foofield':'2',
  ...                                      'subobject.widgets.barfield':'999',
  ...                                      'subobject-empty-marker':'1'})
  >>> widget.update()
  >>> print(format_html(widget.render()))
  <div class="object-widget required">
              <div class="label">
                      <label for="subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="subobject-widgets-foofield"
         name="subobject.widgets.foofield"
         class="text-widget required int-field"
         value="2" />
              </div>
              <div class="label">
                      <label for="subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="subobject-widgets-barfield"
         name="subobject.widgets.barfield"
         class="text-widget int-field"
         value="999" />
              </div>
      <input name="subobject-empty-marker" type="hidden" value="1"/>
  </div>

Widget value comes from the request:

  >>> from pprint import pprint
  >>> wv = widget.value
  >>> pprint(wv)
  {'barfield': '999', 'foofield': '2'}

But our object will not be modified, since there was no "apply"-like control.

  >>> v
  <pyams_form.testing.MySubObject object at ...>
  >>> v.foofield
  42
  >>> v.barfield
  666

The marker must stay (we have to modify the same object):

  >>> v.__marker__
  'ThisMustStayTheSame'


  >>> converter = interfaces.IDataConverter(widget)

  >>> value = converter.to_field_value(wv)
  Traceback (most recent call last):
  ...
  RuntimeError: No IObjectFactory adapter registered for pyams_form.testing.IMySubObject

We have to register object factory adapters to allow the objectwidget to
create objects:

  >>> from pyams_form.object import register_factory_adapter
  >>> register_factory_adapter(IMySubObject, MySubObject, config.registry)
  >>> register_factory_adapter(IMySecond, MySecond, config.registry)

  >>> value = converter.to_field_value(wv)
  >>> value
  <pyams_form.testing.MySubObject object at ...>
  >>> value.foofield
  2
  >>> value.barfield
  999

This is a different object:

  >>> value.__marker__
  Traceback (most recent call last):
  ...
  AttributeError: 'MySubObject' object has no attribute '__marker__'


Setting missing values on the widget works too:

  >>> widget.value = converter.to_widget_value(field.missing_value)

  >>> widget.update()

Default values get rendered:

  >>> print(format_html(widget.render()))
  <div class="object-widget required">
              <div class="label">
                      <label for="subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="subobject-widgets-foofield"
         name="subobject.widgets.foofield"
         class="text-widget required int-field"
         value="2" />
              </div>
              <div class="label">
                      <label for="subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="subobject-widgets-barfield"
         name="subobject.widgets.barfield"
         class="text-widget int-field"
         value="999" />
              </div>
      <input name="subobject-empty-marker" type="hidden" value="1"/>
  </div>

But on the return we get default values back:

  >>> pprint(widget.value)
  {'barfield': '999', 'foofield': '2'}

  >>> value = converter.to_field_value(widget.value)
  >>> value
  <pyams_form.testing.MySubObject object at ...>

HMMMM.... do we have to test error handling here?
I'm tempted to leave it out as no widgets seem to do this.


In forms
========

Do all that fun in add and edit forms too.

Forms and our objectwidget fire events on add and edit, setup a subscriber
for those:

  >>> eventlog = []
  >>> import zope.lifecycleevent

  >>> def logEvent(event):
  ...     eventlog.append(event)
  >>> _ = config.add_subscriber(logEvent, zope.lifecycleevent.interfaces.IObjectModifiedEvent)
  >>> _ = config.add_subscriber(logEvent, zope.lifecycleevent.interfaces.IObjectCreatedEvent)
  >>> _ = config.add_subscriber(logEvent, zope.lifecycleevent.interfaces.IObjectAddedEvent)

  >>> def logEvent2(event):
  ...     eventlog.append(event)

  # >>> _ = config.add_subscriber(logEvent2, zope.lifecycleevent.interfaces.IObjectCreatedEvent)

  >>> def printEvents():
  ...     for event in eventlog:
  ...         print(str(event))
  ...         if isinstance(event, zope.lifecycleevent.ObjectModifiedEvent):
  ...             for attr in event.descriptions:
  ...                 print(attr.interface)
  ...                 print(sorted(attr.attributes))

We define an interface containing a subobject, and an addform for it:

  >>> from pyams_form import form, field
  >>> from pyams_form.testing import MyObject, IMyObject

Note, that creating an object will print some information about it:

  >>> class MyAddForm(form.AddForm):
  ...     fields = field.Fields(IMyObject)
  ...     def create(self, data):
  ...         print("MyAddForm.create")
  ...         pprint(data)
  ...         return MyObject(**data)
  ...     def add(self, obj):
  ...         self.context[obj.name] = obj
  ...     def next_url(self):
  ...         pass

We create the form and try to update it:

  >>> from zope.container.folder import Folder
  >>> root = Folder()
  >>> request = TestRequest()
  >>> myaddform =  MyAddForm(root, request)

  >>> myaddform.update()

As usual, the form contains a widget manager with the expected widget

  >>> list(myaddform.widgets.keys())
  ['subobject', 'name']
  >>> list(myaddform.widgets.values())
  [<ObjectWidget 'form.widgets.subobject'>, <TextWidget 'form.widgets.name'>]

The widget has sub-widgets:

  >>> list(myaddform.widgets['subobject'].widgets.keys())
  ['foofield', 'barfield']

If we want to render the addform, we must give it a template:

  >>> import os
  >>> from pyams_template.interfaces import IContentTemplate
  >>> from pyams_template.template import TemplateFactory
  >>> from pyams_layer.interfaces import IFormLayer
  >>> from pyams_form import interfaces, tests
  >>> def addTemplate(form):
  ...     factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                               'templates', 'simple-edit.pt'), 'text/html')
  ...     config.registry.registerAdapter(factory, (None, IFormLayer, form.__class__),
  ...           IContentTemplate)
  >>> addTemplate(myaddform)

Now rendering the addform renders the subform as well:

  >>> print(format_html(myaddform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-subobject">my object</label>
      <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-foofield"
         name="form.widgets.subobject.widgets.foofield"
         class="text-widget required int-field"
         value="1,111" />
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-barfield"
         name="form.widgets.subobject.widgets.barfield"
         class="text-widget int-field"
         value="2,222" />
              </div>
      <input name="form.widgets.subobject-empty-marker" type="hidden" value="1"/>
  </div>
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

Let's try to add an object:

  >>> request = TestRequest(params={
  ...     'form.widgets.subobject.widgets.foofield':'66',
  ...     'form.widgets.subobject.widgets.barfield':'99',
  ...     'form.widgets.name':'first',
  ...     'form.widgets.subobject-empty-marker':'1',
  ...     'form.buttons.add':'Add'})
  >>> myaddform.request = request

  >>> myaddform.update()
  MyAddForm.create
  {'name': 'first',
   'subobject': <pyams_form.testing.MySubObject object at ...>}

Wow, it got added:

  >>> root['first']
  <pyams_form.testing.MyObject object at ...>

  >>> root['first'].subobject
  <pyams_form.testing.MySubObject object at ...>

Field values need to be right:

  >>> root['first'].subobject.foofield
  66
  >>> root['first'].subobject.barfield
  99

Let's see our event log:

  >>> len(eventlog)
  3

  >>> printEvents()
  <zope...ObjectCreatedEvent object at ...>
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMySubObject>
  ['barfield', 'foofield']
  <zope...ObjectCreatedEvent object at ...>

# FIXME: look for missing extra ContainerModifiedEvent !!!

  >>> eventlog = []

Let's try to edit that newly added object:

  >>> class MyEditForm(form.EditForm):
  ...     fields = field.Fields(IMyObject)

  >>> editform = MyEditForm(root['first'], TestRequest())
  >>> addTemplate(editform)
  >>> editform.update()

Watch for the widget values in the HTML:

  >>> print(format_html(editform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-subobject">my object</label>
      <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-foofield"
         name="form.widgets.subobject.widgets.foofield"
         class="text-widget required int-field"
         value="66" />
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-barfield"
         name="form.widgets.subobject.widgets.barfield"
         class="text-widget int-field"
         value="99" />
              </div>
      <input name="form.widgets.subobject-empty-marker" type="hidden" value="1"/>
  </div>
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
  ...     'form.widgets.subobject.widgets.foofield':'43',
  ...     'form.widgets.subobject.widgets.barfield':'55',
  ...     'form.widgets.name':'first',
  ...     'form.widgets.subobject-empty-marker':'1',
  ...     'form.buttons.apply':'Apply'})

They are still the same:

  >>> root['first'].subobject.foofield
  66
  >>> root['first'].subobject.barfield
  99

  >>> editform.request = request
  >>> editform.update()

Until we have updated the form:

  >>> root['first'].subobject.foofield
  43
  >>> root['first'].subobject.barfield
  55

Let's see our event log:

  >>> len(eventlog)
  2

  >>> printEvents()
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMySubObject>
  ['barfield', 'foofield']
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMyObject>
  ['subobject']


  >>> eventlog=[]


After the update the form says that the values got updated and renders the new
values:

  >>> print(format_html(editform.render()))
  <i>Data successfully updated.</i>
  <form action=".">
    <div class="row">
      <label for="form-widgets-subobject">my object</label>
      <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-foofield"
         name="form.widgets.subobject.widgets.foofield"
         class="text-widget required int-field"
         value="43" />
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-barfield"
         name="form.widgets.subobject.widgets.barfield"
         class="text-widget int-field"
         value="55" />
              </div>
      <input name="form.widgets.subobject-empty-marker" type="hidden" value="1"/>
  </div>
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

  >>> root['first'].__marker__ = "ThisMustStayTheSame"

  >>> root['first'].subobject.foofield
  43
  >>> root['first'].subobject.barfield
  55

Let's modify the values:

  >>> request = TestRequest(params={
  ...     'form.widgets.subobject.widgets.foofield':'666',
  ...     'form.widgets.subobject.widgets.barfield':'999',
  ...     'form.widgets.name':'first',
  ...     'form.widgets.subobject-empty-marker':'1',
  ...     'form.buttons.apply':'Apply'})

  >>> editform.request = request

  >>> editform.update()

Let's check what are ther esults of the update:

  >>> root['first'].subobject.foofield
  666
  >>> root['first'].subobject.barfield
  999
  >>> root['first'].__marker__
  'ThisMustStayTheSame'


Let's make a nasty error, by typing 'bad' instead of an integer:

  >>> request = TestRequest(params={
  ...     'form.widgets.subobject.widgets.foofield':'99',
  ...     'form.widgets.subobject.widgets.barfield':'bad',
  ...     'form.widgets.name':'first',
  ...     'form.widgets.subobject-empty-marker':'1',
  ...     'form.buttons.apply':'Apply'})

  >>> editform.request = request
  >>> eventlog=[]
  >>> editform.update()

Eventlog must be clean:

  >>> len(eventlog)
  0

Watch for the error message in the HTML:
it has to appear at the field itself and at the top of the form:

  >>> print(format_html(editform.render()))
  <i>There were some errors.</i>
  <ul>
    <li>
        my object
      <div class="error">The entered value is not a valid integer literal.</div>
    </li>
  </ul>
  <form action=".">
    <div class="row">
      <b><div class="error">The entered value is not a valid integer literal.</div></b>
      <label for="form-widgets-subobject">my object</label>
      <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-foofield"
         name="form.widgets.subobject.widgets.foofield"
         class="text-widget required int-field"
         value="99" />
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
                      <div class="error">The entered value is not a valid integer literal.</div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-barfield"
         name="form.widgets.subobject.widgets.barfield"
         class="text-widget int-field"
         value="bad" />
              </div>
      <input name="form.widgets.subobject-empty-marker" type="hidden" value="1"/>
  </div>
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

  >>> root['first'].subobject.foofield
  666
  >>> root['first'].subobject.barfield
  999

Let's make more errors:
Now we enter 'bad' and '999999', where '999999' hits the upper limit of the field.

  >>> request = TestRequest(params={
  ...     'form.widgets.subobject.widgets.foofield':'999999',
  ...     'form.widgets.subobject.widgets.barfield':'bad',
  ...     'form.widgets.name':'first',
  ...     'form.widgets.subobject-empty-marker':'1',
  ...     'form.buttons.apply':'Apply'})

  >>> editform.request = request
  >>> editform.update()

Both errors must appear at the top of the form:

  >>> print(format_html(editform.render()))
  <i>There were some errors.</i>
  <ul>
    <li>
        my object
      <div class="error">Value is too big</div><div class="error">The entered value is not a valid integer literal.</div>
    </li>
  </ul>
  <form action=".">
    <div class="row">
      <b><div class="error">Value is too big</div><div class="error">The entered value is not a valid integer literal.</div></b>
      <label for="form-widgets-subobject">my object</label>
      <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
                      <div class="error">Value is too big</div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-foofield"
         name="form.widgets.subobject.widgets.foofield"
         class="text-widget required int-field"
         value="999999" />
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
                      <div class="error">The entered value is not a valid integer literal.</div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-barfield"
         name="form.widgets.subobject.widgets.barfield"
         class="text-widget int-field"
         value="bad" />
              </div>
      <input name="form.widgets.subobject-empty-marker" type="hidden" value="1"/>
  </div>
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

And of course, the object values do not get modified:

  >>> root['first'].subobject.foofield
  666
  >>> root['first'].subobject.barfield
  999

Simple but often used use-case is the display form:

  >>> editform = MyEditForm(root['first'], TestRequest())
  >>> addTemplate(editform)
  >>> editform.mode = interfaces.DISPLAY_MODE
  >>> editform.update()
  >>> print(format_html(editform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-subobject">my object</label>
      <div class="object-widget">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-foofield">
                  <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <span id="form-widgets-subobject-widgets-foofield"
        class="text-widget int-field">666</span>
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-barfield">
                  <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <span id="form-widgets-subobject-widgets-barfield"
        class="text-widget int-field">999</span>
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

Let's see what happens in HIDDEN_MODE ((not quite sane thing, but we want to see the
objectwidget rendered in hidden mode):

  >>> editform = MyEditForm(root['first'], TestRequest())
  >>> addTemplate(editform)
  >>> editform.mode = interfaces.HIDDEN_MODE
  >>> editform.update()

Note, that the labels and the button is there because the form template for testing
does/should not care about the form being hidden.
What matters is that the objectwidget is rendered hidden.

  >>> print(format_html(editform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-subobject">my object</label>
      <input type="hidden"
         id="form-widgets-subobject-widgets-foofield"
         name="form.widgets.subobject.widgets.foofield"
         value="666"
         class="hidden-widget" />
      <input type="hidden"
         id="form-widgets-subobject-widgets-barfield"
         name="form.widgets.subobject.widgets.barfield"
         value="999"
         class="hidden-widget" />
    </div>
    <div class="row">
      <label for="form-widgets-name">name</label>
      <input type="hidden"
         id="form-widgets-name"
         name="form.widgets.name"
         value="first"
         class="hidden-widget" />
    </div>
    <div class="action">
      <input type="submit"
         id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field"
         value="Apply" />
    </div>
  </form>


Editforms might use dicts as context:

  >>> newsub = MySubObject()
  >>> newsub.foofield = 78
  >>> newsub.barfield = 87

  >>> class MyEditFormDict(form.EditForm):
  ...     fields = field.Fields(IMyObject)
  ...     def get_content(self):
  ...         return {'subobject': newsub, 'name': 'blooki'}

  >>> editform = MyEditFormDict(None, TestRequest())
  >>> addTemplate(editform)
  >>> editform.update()

Watch for the widget values in the HTML:

  >>> print(format_html(editform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-subobject">my object</label>
      <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-foofield"
         name="form.widgets.subobject.widgets.foofield"
         class="text-widget required int-field"
         value="78" />
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-barfield"
         name="form.widgets.subobject.widgets.barfield"
         class="text-widget int-field"
         value="87" />
              </div>
      <input name="form.widgets.subobject-empty-marker" type="hidden" value="1"/>
  </div>
    </div>
    <div class="row">
      <label for="form-widgets-name">name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="blooki" />
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
  ...     'form.widgets.subobject.widgets.foofield':'43',
  ...     'form.widgets.subobject.widgets.barfield':'55',
  ...     'form.widgets.name':'first',
  ...     'form.widgets.subobject-empty-marker':'1',
  ...     'form.buttons.apply':'Apply'})

They are still the same:

  >>> newsub.foofield
  78
  >>> newsub.barfield
  87

Until updating the form:

  >>> editform.request = request
  >>> eventlog=[]

  >>> editform.update()

  >>> newsub.foofield
  43
  >>> newsub.barfield
  55

  >>> len(eventlog)
  2
  >>> printEvents()
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMySubObject>
  ['barfield', 'foofield']
  <zope...ObjectModifiedEvent object at ...>
  <InterfaceClass pyams_form.testing.IMyObject>
  ['name', 'subobject']


Object in an Object situation
=============================


We define an interface containing a subobject, and an addform for it:

  >>> from pyams_form import form, field
  >>> from pyams_form.testing import IMyComplexObject

Note, that creating an object will print some information about it:

  >>> class MyAddForm(form.AddForm):
  ...     fields = field.Fields(IMyComplexObject)
  ...     def create(self, data):
  ...         print("MyAddForm.create", str(data))
  ...         return MyObject(**data)
  ...     def add(self, obj):
  ...         self.context[obj.name] = obj
  ...     def next_url(self):
  ...         pass

We create the form and try to update it:

  >>> request = TestRequest()

  >>> myaddform =  MyAddForm(root, request)

  >>> myaddform.update()

As usual, the form contains a widget manager with the expected widget

  >>> list(myaddform.widgets.keys())
  ['subobject', 'name']
  >>> list(myaddform.widgets.values())
  [<ObjectWidget 'form.widgets.subobject'>, <TextWidget 'form.widgets.name'>]

The addform has our ObjectWidget which in turn contains the sub-widgets:

  >>> list(myaddform.widgets['subobject'].widgets.keys())
  ['subfield', 'moofield']

  >>> list(myaddform.widgets['subobject'].widgets['subfield'].widgets.keys())
  ['foofield', 'barfield']

If we want to render the addform, we must give it a template:

  >>> addTemplate(myaddform)

Now rendering the addform renders the subform as well:

  >>> print(format_html(myaddform.render()))
  <form action=".">
    <div class="row">
      <label for="form-widgets-subobject">my object</label>
      <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-subfield">
                              <span>Second-subobject</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <div class="object-widget required">
              <div class="label">
                      <label for="form-widgets-subobject-widgets-subfield-widgets-foofield">
                              <span>My foo field</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-subfield-widgets-foofield"
         name="form.widgets.subobject.widgets.subfield.widgets.foofield"
         class="text-widget required int-field"
         value="1,111" />
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-subfield-widgets-barfield">
                              <span>My dear bar</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-subfield-widgets-barfield"
         name="form.widgets.subobject.widgets.subfield.widgets.barfield"
         class="text-widget int-field"
         value="2,222" />
              </div>
      <input name="form.widgets.subobject.widgets.subfield-empty-marker" type="hidden" value="1"/>
  </div>
              </div>
              <div class="label">
                      <label for="form-widgets-subobject-widgets-moofield">
                              <span>Something</span>
                              <span class="required">*</span>
                      </label>
              </div>
              <div class="widget">
                      <input type="text"
         id="form-widgets-subobject-widgets-moofield"
         name="form.widgets.subobject.widgets.moofield"
         class="text-widget required textline-field"
         value="" />
              </div>
      <input name="form.widgets.subobject-empty-marker" type="hidden" value="1"/>
  </div>
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


Coverage happiness
##################

Converting NO_VALUE holds None:

  >>> from pyams_utils.interfaces.form import NO_VALUE
  >>> converter.to_field_value(NO_VALUE) is None
  True


This is a complicated case.
Happens when the context is a dict, and the dict misses the field.
(Note, we're making ``sub__object`` instead of ``subobject``)

  >>> context = dict(sub__object=None, foo=123, bar=456)

All the story the create a widget:

  >>> field = zope.schema.Object(
  ...     __name__='subobject',
  ...     title='my object widget',
  ...     schema=IMySubObject)

  >>> wv = pyams_form.object.ObjectWidgetValue(
  ...     {'foofield': '2', 'barfield': '999'})

  >>> request = TestRequest()
  >>> widget = pyams_form.browser.object.ObjectWidget(request)
  >>> widget = FieldWidget(field, widget)
  >>> widget.context = context
  >>> widget.value = wv
  >>> widget.update()
  >>> converter = interfaces.IDataConverter(widget)

And still we get a MySubObject, no failure:

  >>> value = converter.to_field_value(wv)
  >>> value
  <pyams_form.testing.MySubObject object at ...>
  >>> value.foofield
  2
  >>> value.barfield
  999


Easy (after the previous).
In case the previous value on the context is None (or missing).
We need to create a new object to be able to set properties on.

  >>> context['subobject'] = None
  >>> value = converter.to_field_value(wv)
  >>> value
  <pyams_form.testing.MySubObject object at ...>
  >>> value.foofield
  2
  >>> value.barfield
  999

In case there is something that cannot be adapted to the right interface,
it just burps:
(might be an idea to create in this case also a new blank object)

  >>> context['subobject'] = 'brutal'
  >>> converter.to_field_value(wv)
  Traceback (most recent call last):
  ...
  TypeError: ('Could not adapt', 'brutal',
  <InterfaceClass pyams_form.testing.IMySubObject>)

  >>> context['subobject'] = None


One more.
Value to convert misses a field. Should never happen actually:

  >>> wv = pyams_form.object.ObjectWidgetValue(
  ...     {'foofield': '2'})
  >>> value = converter.to_field_value(wv)

Known property is set:

  >>> value.foofield
  2

Unknown sticks ti it's default value:

  >>> value.barfield
  2222


Tests cleanup:

  >>> tearDown()
