=============================
Utility Functions and Classes
=============================

This file documents the utility functions and classes that are otherwise not
tested.

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


``create_id(name)`` Function
----------------------------

This function converts an arbitrary unicode string into a valid Python
identifier. If the name is a valid identifier, then it is just returned, but
all upper case letters are lowered:

  >>> util.create_id('Change')
  'change'

  >>> util.create_id('Change_2')
  'change_2'

If a name is not a valid identifier, a hex code of the string is created:

  >>> util.create_id('Change 3')
  '4368616e67652033'

The function can also handle non-ASCII characters:

  >>> id = util.create_id('Ändern')

Since the output depends on how Python is compiled (UCS-2 or 4), we only check
that we have a valid id:

  >>> util._IDENTIFIER.match(id) is not None
  True


``create_css_id(name)`` Function
--------------------------------

This function takes any unicode name and coverts it into an id that
can be easily referenced by CSS selectors.  Characters that are in the
ascii alphabet, are numbers, or are '-' or '_' will be left the same.
All other characters will be converted to ordinal numbers:

  >>> util.create_css_id('NormalId')
  'NormalId'
  >>> id = util.create_css_id('عَرَ')
  >>> util._IDENTIFIER.match(id) is not None
  True
  >>> util.create_css_id('This has spaces')
  'This20has20spaces'

  >>> util.create_css_id(str([(1, 'x'), ('foobar', 42)]))
  '5b2812c2027x27292c202827foobar272c2042295d'


``get_widget_by_id(form, id)`` Function
---------------------------------------

Given a form and a widget id, this function extracts the widget for you. First
we need to create a properly developed form:

  >>> import zope.interface
  >>> import zope.schema

  >>> class IPerson(zope.interface.Interface):
  ...     name = zope.schema.TextLine(title='Name')

  >>> from pyams_form import form, field
  >>> class AddPerson(form.AddForm):
  ...     fields = field.Fields(IPerson)

  >>> request = testing.TestRequest()
  >>> addPerson = AddPerson(None, request)
  >>> addPerson.update()

We can now ask for the widget:

  >>> util.get_widget_by_id(addPerson, 'form-widgets-name')
  <TextWidget 'form.widgets.name'>

The widget id can be split into a prefix and a widget name. The id must always
start with the correct prefix, otherwise a value error is raised:

  >>> util.get_widget_by_id(addPerson, 'myform-widgets-name')
  Traceback (most recent call last):
  ...
  ValueError: Name 'myform.widgets.name' must start with prefix 'form.widgets.'

If the widget is not found but the prefix is correct, ``None`` is returned:

  >>> util.get_widget_by_id(addPerson, 'form-widgets-myname') is None
  True


``extract_file_name(form, id, cleanup=True, allow_empty_postfix=False)`` Function
-----------------------------------------------------------------------------

Test the filename extraction method:

  >>> class IDocument(zope.interface.Interface):
  ...     data = zope.schema.Bytes(title='Data')

Define a widgets stub and a upload widget stub class and setup them as a
faked form:

  >>> class FileUploadWidgetStub:
  ...     def __init__(self):
  ...         self.filename = None

  >>> class WidgetsStub:
  ...     def __init__(self):
  ...         self.data = FileUploadWidgetStub()
  ...         self.prefix = 'widgets.'
  ...     def get(self, name, default):
  ...         return self.data

  >>> class FileUploadFormStub(form.AddForm):
  ...     def __init__(self):
  ...         self.widgets = WidgetsStub()
  ...
  ...     def set_fake_file_name(self, filename):
  ...         self.widgets.data.filename = filename

Now we can setup the stub form. Note this form is just a fake it's not a real
implementation. We just provide a form like class which simulates the
FileUpload object in the a widget. See `z3c/form/browser/file.rst` for a real
file upload test uscase:

  >>> uploadForm = FileUploadFormStub()
  >>> uploadForm.set_fake_file_name('foo.txt')

And extract the filename

  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test a unicode filename:

  >>> uploadForm.set_fake_file_name('foo.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test a windows IE uploaded filename:

  >>> uploadForm.set_fake_file_name('D:\\some\\folder\\foo.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test another filename:

  >>> uploadForm.set_fake_file_name('D:/some/folder/foo.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test another filename:

  >>> uploadForm.set_fake_file_name('/tmp/folder/foo.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.txt'

Test special characters in filename, e.g. dots:

  >>> uploadForm.set_fake_file_name('/tmp/foo.bar.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  'foo.bar.txt'

Test some other special characters in filename:

  >>> uploadForm.set_fake_file_name('/tmp/foo-bar.v.0.1.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  'foo-bar.v.0.1.txt'

Test special characters in file path of filename:

  >>> uploadForm.set_fake_file_name('/tmp-v.1.0/foo-bar.v.0.1.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  'foo-bar.v.0.1.txt'

Test optional keyword arguments. But remember it's hard for Zope to guess the
content type for filenames without extensions:

  >>> uploadForm.set_fake_file_name('minimal')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True,
  ...     allow_empty_postfix=True)
  'minimal'

  >>> uploadForm.set_fake_file_name('/tmp/minimal')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True,
  ...     allow_empty_postfix=True)
  'minimal'

  >>> uploadForm.set_fake_file_name('D:\\some\\folder\\minimal')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True,
  ...     allow_empty_postfix=True)
  'minimal'

There will be a ValueError if we get a empty filename by default:

  >>> uploadForm.set_fake_file_name('/tmp/minimal')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=True)
  Traceback (most recent call last):
  ...
  ValueError: Missing filename extension.

We also can skip removing a path from a upload. Note only IE will upload a
path in a upload ``<input type="file" ...>`` field:

  >>> uploadForm.set_fake_file_name('/tmp/foo.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=False)
  '/tmp/foo.txt'

  >>> uploadForm.set_fake_file_name('/tmp-v.1.0/foo-bar.v.0.1.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=False)
  '/tmp-v.1.0/foo-bar.v.0.1.txt'

  >>> uploadForm.set_fake_file_name('D:\\some\\folder\\foo.txt')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=False)
  'D:\\some\\folder\\foo.txt'

And missing filename extensions are also not allowed by deafault if we skip
the filename:

  >>> uploadForm.set_fake_file_name('/tmp/minimal')
  >>> util.extract_file_name(uploadForm, 'form.widgets.data', cleanup=False)
  Traceback (most recent call last):
  ...
  ValueError: Missing filename extension.


``extract_content_type(form, id)`` Function
-------------------------------------------

There is also a method which is able to extract the content type for a given
file upload. We can use the stub form from the previous test.

Not sure if this an error but on my windows system this test returns
image/pjpeg (progressive jpeg) for foo.jpg and image/x-png for foo.png. So
let's allow this too since this depends on guess_content_type and is not
really a part of pyams_form.

  >>> uploadForm = FileUploadFormStub()
  >>> uploadForm.set_fake_file_name('foo.txt')
  >>> util.extract_content_type(uploadForm, 'form.widgets.data')
  'text/plain'

  >>> uploadForm.set_fake_file_name('foo.gif')
  >>> util.extract_content_type(uploadForm, 'form.widgets.data')
  'image/gif'

  >>> uploadForm.set_fake_file_name('foo.jpg')
  >>> util.extract_content_type(uploadForm, 'form.widgets.data')
  'image/...jpeg'

  >>> uploadForm.set_fake_file_name('foo.png')
  >>> util.extract_content_type(uploadForm, 'form.widgets.data')
  'image/...png'

  >>> uploadForm.set_fake_file_name('foo.tif')
  >>> util.extract_content_type(uploadForm, 'form.widgets.data')
  'image/tiff'

  >>> uploadForm.set_fake_file_name('foo.doc')
  >>> util.extract_content_type(uploadForm, 'form.widgets.data')
  'application/msword'

  >>> uploadForm.set_fake_file_name('foo.zip')
  >>> (util.extract_content_type(uploadForm, 'form.widgets.data')
  ...     in ('application/zip', 'application/x-zip-compressed'))
  True

  >>> uploadForm.set_fake_file_name('foo.unknown')
  >>> util.extract_content_type(uploadForm, 'form.widgets.data')
  'text/x-unknown-content-type'


`Manager` object
----------------

The manager object is a base class of a mapping object that keeps track of the
key order as they are added.

  >>> manager = util.Manager()

Initially the manager is empty:

  >>> len(manager)
  0

Since this base class mainly defines a read-interface, we have to add the
values manually:

  >>> manager['b'] = 2
  >>> manager['a'] = 1

Let's iterate through the manager:

  >>> tuple(iter(manager))
  ('b', 'a')
  >>> list(manager.keys())
  ['b', 'a']
  >>> list(manager.values())
  [2, 1]
  >>> list(manager.items())
  [('b', 2), ('a', 1)]

Let's ow look at item access:

  >>> 'b' in manager
  True
  >>> manager.get('b')
  2
  >>> manager.get('c', 'None')
  'None'

It also supports deletion:

  >>> del manager['b']
  >>> list(manager.items())
  [('a', 1)]


`SelectionManager` object
-------------------------

The selection manager is an extension to the manager and provides a few more
API functions. Unfortunately, this base class is totally useless without a
sensible constructor:

  >>> import zope.interface

  >>> class MySelectionManager(util.SelectionManager):
  ...     manager_interface = zope.interface.Interface
  ...
  ...     def __init__(self, *args):
  ...         super().__init__()
  ...         args = list(args)
  ...         for arg in args:
  ...             if isinstance(arg, MySelectionManager):
  ...                 args += arg.values()
  ...                 continue
  ...             self[str(arg)] = arg

Let's now create two managers:

  >>> manager1 = MySelectionManager(1, 2)
  >>> manager2 = MySelectionManager(3, 4)

You can add two managers:

  >>> manager = manager1 + manager2
  >>> list(manager.values())
  [1, 2, 3, 4]

Next, you can select only certain names:

  >>> list(manager.select('1', '2', '3').values())
  [1, 2, 3]

Or simply omit a value.

  >>> list(manager.omit('2').values())
  [1, 3, 4]

You can also easily copy a manager:

  >>> manager.copy() is not manager
  True

That's all.

`get_specification()` function
------------------------------

This function is capable of returning an `ISpecification` for any object,
including instances.

For an interface, it simply returns the interface:

  >>> import zope.interface
  >>> class IFoo(zope.interface.Interface):
  ...     pass

  >>> util.get_specification(IFoo) == IFoo
  True

Ditto for a class:

  >>> class Bar(object):
  ...     pass

  >>> util.get_specification(Bar) == Bar
  True

For an instance, it will create a marker interface on the fly if necessary:

  >>> bar = Bar()
  >>> util.get_specification(bar) # doctest: +ELLIPSIS
  <InterfaceClass pyams_form.util.IGeneratedForObject_...>

The ellipsis represents a hash of the object.

If the function is called twice on the same object, it will not create a new
marker each time:

  >>> baz = Bar()
  >>> barMarker = util.get_specification(bar)
  >>> bazMarker1 = util.get_specification(baz)
  >>> bazMarker2 = util.get_specification(baz)

  >>> barMarker is bazMarker1
  False

  >>> bazMarker1 == bazMarker2
  True
  >>> bazMarker1 is bazMarker2
  True

`changed_field()` function
--------------------------

Decide whether a field was changed/modified.

  >>> class IPerson(zope.interface.Interface):
  ...     login = zope.schema.TextLine(
  ...         title='Login')
  ...     address = zope.schema.Object(
  ...         schema=zope.interface.Interface)

  >>> @zope.interface.implementer(IPerson)
  ... class Person(object):
  ...     login = 'johndoe'
  >>> person = Person()

field.context is None and no context passed:

  >>> util.changed_field(IPerson['login'], 'foo')
  True

IObject field:

  >>> util.changed_field(IPerson['address'], object(), context = person)
  True

field.context or context passed:

  >>> util.changed_field(IPerson['login'], 'foo', context = person)
  True
  >>> util.changed_field(IPerson['login'], 'johndoe', context = person)
  False

  >>> fld = IPerson['login'].bind(person)
  >>> util.changed_field(fld, 'foo')
  True
  >>> util.changed_field(fld, 'johndoe')
  False

No access:

  >>> from pyams_form import datamanager
  >>> save = datamanager.AttributeField.can_access
  >>> datamanager.AttributeField.can_access = lambda self: False

  >>> util.changed_field(IPerson['login'], 'foo', context = person)
  True
  >>> util.changed_field(IPerson['login'], 'johndoe', context = person)
  True

  >>> datamanager.AttributeField.can_access = save


`changed_widget()` function
---------------------------

Decide whether a widget value was changed/modified.

  >>> request = testing.TestRequest()
  >>> import pyams_form.widget
  >>> widget = pyams_form.widget.Widget(request)

If the widget is not IContextAware, there's nothing to check:

  >>> from pyams_form import interfaces
  >>> interfaces.form.IContextAware.providedBy(widget)
  False

  >>> util.changed_widget(widget, 'foo')
  True

Make it IContextAware:

  >>> widget.context = person
  >>> zope.interface.alsoProvides(widget, interfaces.form.IContextAware)

  >>> widget.field = IPerson['login']

  >> util.changed_widget(widget, 'foo')
  True

  >>> util.changed_widget(widget, 'johndoe')
  False

Field and context is also overridable:

  >>> widget.field = None
  >>> util.changed_widget(widget, 'johndoe', field=IPerson['login'])
  False

  >>> p2 = Person()
  >>> p2.login = 'foo'

  >>> util.changed_widget(widget, 'foo', field=IPerson['login'], context=p2)
  False

`sorted_none()` function
------------------------

  >>> util.sorted_none([None, 'a', 'b'])
  [None, 'a', 'b']

  >>> util.sorted_none([None, 1, 2])
  [None, 1, 2]

  >>> util.sorted_none([None, True, False])
  [None, False, True]

  >>> util.sorted_none([['true'], [], ['false']])
  [[], ['false'], ['true']]

  >>> util.sorted_none([('false',), ('true',), ()])
  [(), ('false',), ('true',)]


Tests cleanup:

  >>> tearDown()
