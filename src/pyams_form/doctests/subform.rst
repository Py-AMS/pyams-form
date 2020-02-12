=========
Sub-Forms
=========

Traditionally, the Zope community talks about sub-forms in a generic manner
without defining their purpose, restrictions and assumptions. When we
initially talked about sub-forms for this package, we quickly noticed that
there are several classes of sub-forms with different goals.

Of course, we need to setup our defaults for this demonstration as well:

  >>> from pyramid.testing import setUp, tearDown
  >>> config = setUp()

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


Class I: The form within the form
---------------------------------

This class of sub-forms provides a complete form within a form, including its
own actions. When an action of the sub-form is submitted, the parent form
usually does not interact with that action at all. The same is true for the
reverse; when an action of the parent form is submitted, the sub-form does not
react.

A classic example for this type of sub-form is uploading an image. The subform
allows uploading a file and once the file is uploaded the image is shown as
well as a "Delete"/"Clear" button. The sub-form will store the image in the
session and when the main form is submitted it looks in the session for the
image.

This scenario was well supported in ``zope.formlib`` and also does not require
special support in ``pyams_form``. Let me show you, how this can be done.

In this example, we would like to describe a car and its owner:

  >>> import zope.interface
  >>> import zope.schema

  >>> class IOwner(zope.interface.Interface):
  ...     name = zope.schema.TextLine(title='Name')
  ...     license = zope.schema.TextLine(title='License')

  >>> class ICar(zope.interface.Interface):
  ...     model = zope.schema.TextLine(title='Model')
  ...     make = zope.schema.TextLine(title='Make')
  ...     owner = zope.schema.Object(title='Owner', schema=IOwner)

Let's now implement the two interfaces and create instances, so that we can
create edit forms for it:

  >>> @zope.interface.implementer(IOwner)
  ... class Owner:
  ...     def __init__(self, name, license):
  ...         self.name = name
  ...         self.license = license

  >>> @zope.interface.implementer(ICar)
  ... class Car:
  ...     def __init__(self, model, make, owner):
  ...         self.model = model
  ...         self.make = make
  ...         self.owner = owner

  >>> me = Owner('Stephan Richter', 'MA-1231FW97')
  >>> mycar = Car('Nissan', 'Sentra', me)

We define the owner sub-form as we would any other form. The only difference
is the template, which should not render a form-tag:

  >>> import os
  >>> from pyams_form import form, field, tests

  >>> templatePath = os.path.dirname(tests.__file__)

  >>> class OwnerForm(form.EditForm):
  ...     fields = field.Fields(IOwner)
  ...     prefix = 'owner'

  >>> from pyams_template.interfaces import IContentTemplate
  >>> from pyams_template.template import TemplateFactory
  >>> from pyams_layer.interfaces import IFormLayer
  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-owneredit.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, OwnerForm), IContentTemplate)

Next we define the car form, which has the owner form as a sub-form. The car
form also needs a special template, since it needs to render the sub-form at
some point. For the simplicity of this example, I have duplicated a lot of
template code here, but you can use your favorite template techniques, such as
METAL macros, viewlets, or pagelets to make better reuse of some code.

  >>> class CarForm(form.EditForm):
  ...     fields = field.Fields(ICar).select('model', 'make')
  ...     prefix = 'car'
  ...     def update(self):
  ...         self.owner = OwnerForm(self.context.owner, self.request)
  ...         self.owner.update()
  ...         super(CarForm, self).update()

  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-caredit.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, CarForm), IContentTemplate)

Let's now instantiate the form and render it:

  >>> from pyams_utils.testing import format_html
  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

  >>> carForm = CarForm(mycar, request)
  >>> carForm.update()
  >>> print(format_html(carForm.render()))
    <form action=".">
      <div class="row">
        <label for="car-widgets-model">Model</label>
        <input type="text"
           id="car-widgets-model"
           name="car.widgets.model"
           class="text-widget required textline-field"
           value="Nissan" />
      </div>
      <div class="row">
        <label for="car-widgets-make">Make</label>
        <input type="text"
           id="car-widgets-make"
           name="car.widgets.make"
           class="text-widget required textline-field"
           value="Sentra" />
      </div>
      <fieldset>
        <legend>Owner</legend>
    <div class="row">
      <label for="owner-widgets-name">Name</label>
      <input type="text"
           id="owner-widgets-name"
           name="owner.widgets.name"
           class="text-widget required textline-field"
           value="Stephan Richter" />
    </div>
    <div class="row">
      <label for="owner-widgets-license">License</label>
      <input type="text"
           id="owner-widgets-license"
           name="owner.widgets.license"
           class="text-widget required textline-field"
           value="MA-1231FW97" />
    </div>
    <div class="action">
      <input type="submit"
           id="owner-buttons-apply"
           name="owner.buttons.apply"
           class="submit-widget"
           value="Apply" />
    </div>
      </fieldset>
      <div class="action">
        <input type="submit"
           id="car-buttons-apply"
           name="car.buttons.apply"
           class="submit-widget"
           value="Apply" />
      </div>
    </form>

I can now submit the owner form, which should not submit any car changes I
might have made in the form:

  >>> request = TestRequest(params={
  ...     'car.widgets.model': 'BMW',
  ...     'car.widgets.make': '325',
  ...     'owner.widgets.name': 'Stephan Richter',
  ...     'owner.widgets.license': 'MA-97097A87',
  ...     'owner.buttons.apply': 'Apply'
  ...     })

  >>> carForm = CarForm(mycar, request)
  >>> carForm.update()

  >>> mycar.model
  'Nissan'
  >>> mycar.make
  'Sentra'

  >>> me.name
  'Stephan Richter'
  >>> me.license
  'MA-97097A87'

Also, the form should say that the data of the owner has changed:

  >>> print(format_html(carForm.render()))
    <form action=".">
      <div class="row">
        <label for="car-widgets-model">Model</label>
        <input type="text"
           id="car-widgets-model"
           name="car.widgets.model"
           class="text-widget required textline-field"
           value="BMW" />
      </div>
      <div class="row">
        <label for="car-widgets-make">Make</label>
        <input type="text"
           id="car-widgets-make"
           name="car.widgets.make"
           class="text-widget required textline-field"
           value="325" />
      </div>
      <fieldset>
        <legend>Owner</legend>
        <i>Data successfully updated.</i>
    <div class="row">
      <label for="owner-widgets-name">Name</label>
      <input type="text"
           id="owner-widgets-name"
           name="owner.widgets.name"
           class="text-widget required textline-field"
           value="Stephan Richter" />
    </div>
    <div class="row">
      <label for="owner-widgets-license">License</label>
      <input type="text"
           id="owner-widgets-license"
           name="owner.widgets.license"
           class="text-widget required textline-field"
           value="MA-97097A87" />
    </div>
    <div class="action">
      <input type="submit"
           id="owner-buttons-apply"
           name="owner.buttons.apply"
           class="submit-widget"
           value="Apply" />
    </div>
      </fieldset>
      <div class="action">
        <input type="submit"
           id="car-buttons-apply"
           name="car.buttons.apply"
           class="submit-widget"
           value="Apply" />
      </div>
    </form>

The same is true the other way around as well. Submitting the overall form
does not submit the owner form:

  >>> request = TestRequest(params={
  ...     'car.widgets.model': 'BMW',
  ...     'car.widgets.make': '325',
  ...     'car.buttons.apply': 'Apply',
  ...     'owner.widgets.name': 'Claudia Richter',
  ...     'owner.widgets.license': 'MA-123403S2',
  ...     })

  >>> carForm = CarForm(mycar, request)
  >>> carForm.update()

  >>> mycar.model
  'BMW'
  >>> mycar.make
  '325'

  >>> me.name
  'Stephan Richter'
  >>> me.license
  'MA-97097A87'


Class II: The logical unit
--------------------------

In this class of sub-forms, a sub-form is often just a collection of widgets
without any actions. Instead, the sub-form must be able to react to the
actions of the parent form. A good example of those types of sub-forms is
actually the example I chose above.

So let's redevelop our example above in a way that the owner sub-form is just
a logical unit that shares the action with its parent form. Initially, the
example does not look very different, except that we use ``EditSubForm`` as a
base class:

  >>> from pyams_form import subform

  >>> class OwnerForm(subform.EditSubForm):
  ...     fields = field.Fields(IOwner)
  ...     prefix = 'owner'

  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-subedit.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, OwnerForm), IContentTemplate)

The main form also is pretty much the same, except that a subform takes three
constructor arguments, the last one being the parent form:

  >>> class CarForm(form.EditForm):
  ...     fields = field.Fields(ICar).select('model', 'make')
  ...     prefix = 'car'
  ...
  ...     def update(self):
  ...         super(CarForm, self).update()
  ...         self.owner = OwnerForm(self.context.owner, self.request, self)
  ...         self.owner.update()

  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-caredit.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, CarForm), IContentTemplate)

Rendering the form works as before:

  >>> request = TestRequest()
  >>> carForm = CarForm(mycar, request)
  >>> carForm.update()
  >>> print(format_html(carForm.render()))
    <form action=".">
      <div class="row">
        <label for="car-widgets-model">Model</label>
        <input type="text"
           id="car-widgets-model"
           name="car.widgets.model"
           class="text-widget required textline-field"
           value="BMW" />
      </div>
      <div class="row">
        <label for="car-widgets-make">Make</label>
        <input type="text"
           id="car-widgets-make"
           name="car.widgets.make"
           class="text-widget required textline-field"
           value="325" />
      </div>
      <fieldset>
        <legend>Owner</legend>
    <div class="row">
      <label for="owner-widgets-name">Name</label>
      <input type="text"
           id="owner-widgets-name"
           name="owner.widgets.name"
           class="text-widget required textline-field"
           value="Stephan Richter" />
    </div>
    <div class="row">
      <label for="owner-widgets-license">License</label>
      <input type="text"
           id="owner-widgets-license"
           name="owner.widgets.license"
           class="text-widget required textline-field"
           value="MA-97097A87" />
    </div>
      </fieldset>
      <div class="action">
        <input type="submit"
           id="car-buttons-apply"
           name="car.buttons.apply"
           class="submit-widget"
           value="Apply" />
      </div>
    </form>

The interesting part of this setup is that the "Apply" button calls the action
handlers for both, the main and the sub-form:

  >>> request = TestRequest(params={
  ...     'car.widgets.model': 'Ford',
  ...     'car.widgets.make': 'F150',
  ...     'car.buttons.apply': 'Apply',
  ...     'owner.widgets.name': 'Claudia Richter',
  ...     'owner.widgets.license': 'MA-991723FDG',
  ...     })

  >>> carForm = CarForm(mycar, request)
  >>> carForm.update()

  >>> mycar.model
  'Ford'
  >>> mycar.make
  'F150'
  >>> me.name
  'Claudia Richter'
  >>> me.license
  'MA-991723FDG'

Let's now have a look at cases where an error happens. If an error occurs in
the parent form, the sub-form is still submitted:

  >>> request = TestRequest(params={
  ...     'car.widgets.model': 'Volvo\n~',
  ...     'car.widgets.make': '450',
  ...     'car.buttons.apply': 'Apply',
  ...     'owner.widgets.name': 'Stephan Richter',
  ...     'owner.widgets.license': 'MA-991723FDG',
  ...     })

  >>> carForm = CarForm(mycar, request)
  >>> carForm.update()

  >>> mycar.model
  'Ford'
  >>> mycar.make
  'F150'
  >>> me.name
  'Stephan Richter'
  >>> me.license
  'MA-991723FDG'

Let's look at the rendered form:

  >>> print(format_html(carForm.render()))
    <i>There were some errors.</i>
    <ul>
      <li>
        Model:
        <div class="error">Constraint not satisfied</div>
      </li>
    </ul>
    <form action=".">
      <div class="row">
        <b><div class="error">Constraint not satisfied</div></b>
        <label for="car-widgets-model">Model</label>
        <input type="text"
           id="car-widgets-model"
           name="car.widgets.model"
           class="text-widget required textline-field"
           value="Volvo
    ~" />
      </div>
      <div class="row">
        <label for="car-widgets-make">Make</label>
        <input type="text"
           id="car-widgets-make"
           name="car.widgets.make"
           class="text-widget required textline-field"
           value="450" />
      </div>
      <fieldset>
        <legend>Owner</legend>
        <i>Data successfully updated.</i>
    <div class="row">
      <label for="owner-widgets-name">Name</label>
      <input type="text"
           id="owner-widgets-name"
           name="owner.widgets.name"
           class="text-widget required textline-field"
           value="Stephan Richter" />
    </div>
    <div class="row">
      <label for="owner-widgets-license">License</label>
      <input type="text"
           id="owner-widgets-license"
           name="owner.widgets.license"
           class="text-widget required textline-field"
           value="MA-991723FDG" />
    </div>
      </fieldset>
      <div class="action">
        <input type="submit"
           id="car-buttons-apply"
           name="car.buttons.apply"
           class="submit-widget"
           value="Apply" />
      </div>
    </form>

Now, we know, we know. This might not be the behavior that *you* want. But
remember how we started this document. We started with the recognition that
there are many classes and policies surrounding subforms. So while this
package provides some sensible default behavior, it is not intended to be
comprehensive.

Let's now create an error in the sub-form, ensuring that an error message
occurs:

  >>> request = TestRequest(params={
  ...     'car.widgets.model': 'Volvo',
  ...     'car.widgets.make': '450',
  ...     'car.buttons.apply': 'Apply',
  ...     'owner.widgets.name': 'Claudia\n Richter',
  ...     'owner.widgets.license': 'MA-991723F12',
  ...     })

  >>> carForm = CarForm(mycar, request)
  >>> carForm.update()

  >>> mycar.model
  'Volvo'
  >>> mycar.make
  '450'
  >>> me.name
  'Stephan Richter'
  >>> me.license
  'MA-991723FDG'

  >>> print(format_html(carForm.render()))
  <i>Data successfully updated.</i>
  ...
    <fieldset>
      <legend>Owner</legend>
      <i>There were some errors.</i>
  <ul>
     <li>
       Name:
       <div class="error">Constraint not satisfied</div>
     </li>
  </ul>
  ...
    </fieldset>
  ...
  </form>

If the data did not change, it is also locally reported:

  >>> request = TestRequest(params={
  ...     'car.widgets.model': 'Ford',
  ...     'car.widgets.make': 'F150',
  ...     'car.buttons.apply': 'Apply',
  ...     'owner.widgets.name': 'Stephan Richter',
  ...     'owner.widgets.license': 'MA-991723FDG',
  ...     })

  >>> carForm = CarForm(mycar, request)
  >>> carForm.update()
  >>> print(format_html(carForm.render()))
  <i>Data successfully updated.</i>
  ...
    <fieldset>
      <legend>Owner</legend>
      <i>No changes were applied.</i>
      ...
    </fieldset>
  ...
  </form>

Final Note: With ``zope.formlib`` and ``zope.app.form`` people usually wrote
complex object widgets to handle objects within forms. We never considered
this a good way of programming, since one loses control over the layout too
easily.


Context-free subforms
---------------------

Ok, that was easy. But what about writing a form including a subform without a
context? Let's show how we can write a form without any context using the
sample above. Note, this sample form does not include actions which store the
form input. You can store the values like in any other forms using the forms
widget method ``self.widgets.extract()`` which will return the form and
subform input values.

  >>> from pyams_form.interfaces.widget import IWidgets
  >>> class OwnerAddForm(form.EditForm):
  ...     fields = field.Fields(IOwner)
  ...     prefix = 'owner'
  ...
  ...     def update_widgets(self):
  ...         self.widgets = config.registry.getMultiAdapter(
  ...             (self, self.request, self.get_content()), IWidgets)
  ...         self.widgets.ignore_context = True
  ...         self.widgets.update()

  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-owneredit.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, OwnerAddForm), IContentTemplate)

Next we define the car form, which has the owner form as a sub-form.

  >>> class CarAddForm(form.EditForm):
  ...     fields = field.Fields(ICar).select('model', 'make')
  ...     prefix = 'car'
  ...
  ...     def update_widgets(self):
  ...         self.widgets = config.registry.getMultiAdapter(
  ...             (self, self.request, self.get_content()), IWidgets)
  ...         self.widgets.ignore_context = True
  ...         self.widgets.update()
  ...
  ...     def update(self):
  ...         self.owner = OwnerAddForm(None, self.request)
  ...         self.owner.update()
  ...         super(CarAddForm, self).update()

  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-caredit.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, CarAddForm), IContentTemplate)

Let's now instantiate the form and render it. but first set up a simple
container which we can use for the add form context:

  >>> class Container:
  ...    """Simple context simulating a container."""
  >>> container = Container()

Set up a test request:

  >>> from pyams_form.testing import TestRequest
  >>> request = TestRequest()

And render the form. As you can see, the widgets get rendered without any
*real* context.

  >>> carForm = CarAddForm(container, request)
  >>> carForm.update()
  >>> print(format_html(carForm.render()))
    <form action=".">
      <div class="row">
        <label for="car-widgets-model">Model</label>
        <input type="text"
           id="car-widgets-model"
           name="car.widgets.model"
           class="text-widget required textline-field"
           value="" />
      </div>
      <div class="row">
        <label for="car-widgets-make">Make</label>
        <input type="text"
           id="car-widgets-make"
           name="car.widgets.make"
           class="text-widget required textline-field"
           value="" />
      </div>
      <fieldset>
        <legend>Owner</legend>
    <div class="row">
      <label for="owner-widgets-name">Name</label>
      <input type="text"
           id="owner-widgets-name"
           name="owner.widgets.name"
           class="text-widget required textline-field"
           value="" />
    </div>
    <div class="row">
      <label for="owner-widgets-license">License</label>
      <input type="text"
           id="owner-widgets-license"
           name="owner.widgets.license"
           class="text-widget required textline-field"
           value="" />
    </div>
    <div class="action">
      <input type="submit"
           id="owner-buttons-apply"
           name="owner.buttons.apply"
           class="submit-widget"
           value="Apply" />
    </div>
      </fieldset>
      <div class="action">
        <input type="submit"
           id="car-buttons-apply"
           name="car.buttons.apply"
           class="submit-widget"
           value="Apply" />
      </div>
    </form>

Let's show how we can extract the input values of the form and the subform.
First give them some input:

  >>> request = TestRequest(params={
  ...     'car.widgets.model': 'Ford',
  ...     'car.widgets.make': 'F150',
  ...     'owner.widgets.name': 'Stephan Richter',
  ...     'owner.widgets.license': 'MA-991723FDG',
  ...     })
  >>> carForm = CarAddForm(container, request)
  >>> carForm.update()

Now get the form values. This is normally done in a action handler:

  >>> from pprint import pprint
  >>> pprint(carForm.widgets.extract())
  ({'make': 'F150', 'model': 'Ford'}, ())

  >>> pprint(carForm.owner.widgets.extract())
  ({'license': 'MA-991723FDG', 'name': 'Stephan Richter'}, ())


Tests cleanup:

  >>> tearDown()
