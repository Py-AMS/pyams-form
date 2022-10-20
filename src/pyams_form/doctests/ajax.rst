
==========
AJAX forms
==========

What we call AJAX forms are nothing but standard forms, except that they are called by
AJAX requests and generally return a simple JSON object instead of a full HTML document.

As JSON messages contents can be dependent of the Javascript framework in use, JSON responses
are handled by adapters, so they can be easilly replaced by a custom implementation.

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

  >>> from zope.container.folder import Folder
  >>> root = Folder()

  >>> from pyams_utils.testing import format_html
  >>> from pyams_layer.interfaces import IFormLayer

Let's try to find our AJAX add view:

  >>> from pyramid.interfaces import IView
  >>> request = testing.TestRequest()
  >>> view = config.registry.queryMultiAdapter((root, request), IView, name='test-add-form.html')
  >>> view
  <pyams_form.testing.TestAddForm object at 0x...>

Let's do a few checks on this common HTML form:

  >>> view.update()
  >>> view.ajax_form_handler
  'test-add-form.json'
  >>> view.get_ajax_handler()
  'http://example.com/test-add-form.json'
  >>> view.get_form_options() is None
  True

Let's start by testing if errors are correctly handled:

  >>> import json, pprint
  >>> from pyramid.view import render_view
  >>> result = render_view(root, request, 'test-add-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'message': 'No data was created.',
   'status': 'info'}

No data has been created because no submit button value was provided:

  >>> request = testing.TestRequest(params={'form.buttons.add': 'Add'})
  >>> result = render_view(root, request, 'test-add-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'error_message': 'There were some errors.',
   'status': 'error',
   'widgets': [{'id': 'form-widgets-name',
                'label': 'Name',
                'message': 'Required input is missing.',
                'name': 'form.widgets.name'},
               {'id': 'form-widgets-value',
                'label': 'Value',
                'message': 'Required input is missing.',
                'name': 'form.widgets.value'}]}
  >>> 'pyams' in root
  False

Let's try to provide new params to out form:

  >>> request = testing.TestRequest(params={'form.widgets.name': 'PyAMS',
  ...                                       'form.widgets.value': 'Error',
  ...                                       'form.buttons.add': 'Add'})
  >>> result = render_view(root, request, 'test-add-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'error_message': 'There were some errors.',
   'status': 'error',
   'widgets': [{'id': 'form-widgets-value',
                'label': 'Value',
                'message': 'The entered value is not a valid integer literal.',
                'name': 'form.widgets.value'}]}
  >>> 'pyams' in root
  False

Finally: let's provide correct values:

  >>> request = testing.TestRequest(params={'form.widgets.name': 'PyAMS',
  ...                                       'form.widgets.value': '2020',
  ...                                       'form.buttons.add': 'Add'})
  >>> result = render_view(root, request, 'test-add-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'status': 'reload'}
  >>> 'pyams' in root
  True
  >>> root['pyams']
  <...AJAXTestContent object at 0x...>

We can create a custom form renderer for this add form:

  >>> from pyams_utils.adapter import ContextRequestViewAdapter
  >>> from pyams_form.interfaces.form import IAJAXFormRenderer
  >>> from pyams_form.testing import ITestAddForm, TestAddForm

  >>> class TestAddFormRenderer(ContextRequestViewAdapter):
  ...     def render(self, changes):
  ...         return {'status': 'success',
  ...                 'message': 'Content was correctly created.'}
  >>> config.registry.registerAdapter(TestAddFormRenderer,
  ...       required=(None, IFormLayer, ITestAddForm),
  ...       provided=IAJAXFormRenderer)

  >>> request = testing.TestRequest(params={'form.widgets.name': 'ZTFY',
  ...                                       'form.widgets.value': '2010',
  ...                                       'form.buttons.add': 'Add'})
  >>> result = render_view(root, request, 'test-add-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'message': 'Content was correctly created.',
   'status': 'success'}
  >>> 'ztfy' in root
  True

Let's now try to create an AJAX edit form:

  >>> request = testing.TestRequest()
  >>> content = root['ztfy']
  >>> content
  <...AJAXTestContent object at 0x...>

  >>> from pyams_form.testing import IAJAXTestContent, AJAXTestContent
  >>> IAJAXTestContent.providedBy(content)
  True

  >>> result = render_view(content, request, 'test-edit-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'message': 'No changes were applied.', 'status': 'info'}

Like in the add form, a submit button is required to apply updates:

  >>> request = testing.TestRequest(params={'form.buttons.apply': 'Apply'})
  >>> result = render_view(content, request, 'test-edit-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'error_message': 'There were some errors.',
   'status': 'error',
   'widgets': [{'id': 'form-widgets-name',
                'label': 'Name',
                'message': 'Required input is missing.',
                'name': 'form.widgets.name'},
               {'id': 'form-widgets-value',
                'label': 'Value',
                'message': 'Required input is missing.',
                'name': 'form.widgets.value'}]}

Errors occured because we didn't provided any new value. We can check that form's context
wasn't modified:

  >>> content.name
  'ZTFY'
  >>> content.value
  2010

Let's try to provide other values:

  >>> request = testing.TestRequest(params={'form.widgets.name': 'ZTFY',
  ...                                       'form.widgets.value': 'error',
  ...                                       'form.buttons.apply': 'Apply'})
  >>> result = render_view(content, request, 'test-edit-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'error_message': 'There were some errors.',
   'status': 'error',
   'widgets': [{'id': 'form-widgets-value',
                'label': 'Value',
                'message': 'The entered value is not a valid integer literal.',
                'name': 'form.widgets.value'}]}

Finally, let's provide correct values:

  >>> request = testing.TestRequest(params={'form.widgets.name': 'Zope 3',
  ...                                       'form.widgets.value': '2008',
  ...                                       'form.buttons.apply': 'Apply'})
  >>> result = render_view(content, request, 'test-edit-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'message': 'Data successfully updated.',
   'status': 'success'}
  >>> content.name
  'Zope 3'
  >>> content.value
  2008

We can also provide a custom renderer for an edit form:

  >>> from pyams_form.testing import ITestEditForm, TestEditForm

  >>> class TestEditFormRenderer(ContextRequestViewAdapter):
  ...     def render(self, changes):
  ...         return {'status': 'success',
  ...                 'message': 'Content was correctly updated.'}
  >>> config.registry.registerAdapter(TestEditFormRenderer,
  ...       required=(None, IFormLayer, ITestEditForm),
  ...       provided=IAJAXFormRenderer)

  >>> request = testing.TestRequest(params={'form.widgets.name': 'PyAMS',
  ...                                       'form.widgets.value': '2020',
  ...                                       'form.buttons.apply': 'Apply'})
  >>> result = render_view(content, request, 'test-edit-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'message': 'Content was correctly updated.',
   'status': 'success'}
  >>> content.name
  'PyAMS'
  >>> content.value
  2020

Let's try now to add a subform to this edit form:

  >>> from zope.interface import Interface, implementer
  >>> from zope.schema import TextLine
  >>> class IAJAXTestElement(Interface):
  ...     label = TextLine(title="Label")

  >>> from zope.schema.fieldproperty import FieldProperty
  >>> @implementer(IAJAXTestElement)
  ... class AJAXTestElement:
  ...     label = FieldProperty(IAJAXTestElement['label'])

  >>> def test_content_element_factory(context):
  ...     element = getattr(context, 'element', None)
  ...     if element is None:
  ...         element = context.element = AJAXTestElement()
  ...     return element

  >>> config.registry.registerAdapter(test_content_element_factory,
  ...       required=(AJAXTestContent,),
  ...       provided=IAJAXTestElement)

  >>> from zope.interface import implementer
  >>> from pyams_form.interfaces.form import IInnerSubForm
  >>> from pyams_form import field, subform

  >>> @implementer(IInnerSubForm)
  ... class TestElementEditSubform(subform.InnerEditForm):
  ...     """Test element edit subform"""
  ...     fields = field.Fields(IAJAXTestElement)
  ...     prefix = 'element.'
  ...
  ...     def get_content(self):
  ...         return IAJAXTestElement(self.context)

  >>> config.registry.registerAdapter(TestElementEditSubform,
  ...       required=(None, IFormLayer, TestEditForm),
  ...       provided=IInnerSubForm, name='element')

  >>> class TestElementEditSubformRenderer(ContextRequestViewAdapter):
  ...     """Test element edit subform AJAX renderer"""
  ...
  ...     def render(self, changes):
  ...         if not changes:
  ...             return None
  ...         return {
  ...             'events': [{
  ...                 'event_type': 'refresh',
  ...                 'source': self.view.widgets['label'].name,
  ...                 'value': self.view.widgets['label'].value
  ...             }]
  ...         }

  >>> config.registry.registerAdapter(TestElementEditSubformRenderer,
  ...       required=(None, IFormLayer, TestElementEditSubform),
  ...       provided=IAJAXFormRenderer)

  >>> request = testing.TestRequest()
  >>> result = render_view(content, request, 'test-edit-form.html')
  Traceback (most recent call last):
  ...
  zope.interface.interfaces.ComponentLookupError: ((...), <...ILayoutTemplate>, '')

Our form is needing a content and a layout templates:

  >>> import os
  >>> from pyams_template.interfaces import IContentTemplate, ILayoutTemplate
  >>> from pyams_template.template import TemplateFactory
  >>> from pyams_form.interfaces.form import IForm, IInnerForm
  >>> from pyams_form import tests

  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-edit-with-subforms.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, IForm), IContentTemplate)

  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-subedit.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, IInnerForm), IContentTemplate)

  >>> factory = TemplateFactory(os.path.join(os.path.dirname(tests.__file__),
  ...                           'templates', 'simple-layout.pt'), 'text/html')
  >>> config.registry.registerAdapter(factory, (None, IFormLayer, TestEditForm), ILayoutTemplate)

  >>> result = render_view(content, request, 'test-edit-form.html')
  >>> print(format_html(result.decode()))
  <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
  <html xmlns="http://www.w3.org/1999/xhtml">
  <body>
  <form action=".">
    <div class="row">
      <label for="form-widgets-name">Name</label>
      <input type="text"
         id="form-widgets-name"
         name="form.widgets.name"
         class="text-widget required textline-field"
         value="PyAMS" />
    </div>
    <div class="row">
      <label for="form-widgets-value">Value</label>
      <input type="text"
         id="form-widgets-value"
         name="form.widgets.value"
         class="text-widget required int-field"
         value="2,020" />
    </div>
    <fieldset>
      <legend></legend>
      <div class="row">
        <label for="element-widgets-label">Label</label>
        <input type="text"
             id="element-widgets-label"
             name="element.widgets.label"
             class="text-widget required textline-field"
             value="" />
      </div>
    </fieldset>
    <div class="action">
      <input type="submit"
         id="form-buttons-apply"
         name="form.buttons.apply"
         class="submit-widget button-field"
         value="Apply" />
    </div>
  </form>
  </body>
  </html>

  >>> request = testing.TestRequest(params={'form.widgets.name': 'PyAMS',
  ...                                       'form.widgets.value': '2020',
  ...                                       'form.buttons.apply': 'Apply'})
  >>> result = render_view(content, request, 'test-edit-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'error_message': 'There were some errors.',
   'status': 'error',
   'widgets': [{'id': 'element-widgets-label',
                'label': 'Label',
                'message': 'Required input is missing.',
                'name': 'element.widgets.label'}]}

We can see here that an error which occurred into a subform is returned normally into the result
object.
We can now provide correct values, but we have to restore the default form renderer before:

  >>> from pyams_form.ajax import AJAXFormRenderer
  >>> config.registry.registerAdapter(AJAXFormRenderer,
  ...       required=(None, IFormLayer, ITestEditForm),
  ...       provided=IAJAXFormRenderer)

  >>> request = testing.TestRequest(params={'form.widgets.name': 'PyAMS',
  ...                                       'form.widgets.value': '2020',
  ...                                       'element.widgets.label': 'PyAMS form',
  ...                                       'form.buttons.apply': 'Apply'})
  >>> result = render_view(content, request, 'test-edit-form.json')
  >>> pprint.pprint(json.loads(result.decode()))
  {'events': [{'event_type': 'refresh',
               'source': 'element.widgets.label',
               'value': 'PyAMS form'}],
   'message': 'Data successfully updated.',
   'status': 'success'}

  >>> content.element.label
  'PyAMS form'


AJAX form decorator
-------------------

PyAMS provides a custom decorator, which can be used to register a pagelet to handle HTML form
and a Pyramid view to handle JSON submit:

    >>> from pyramid.interfaces import IRequest
    >>> from pyams_utils.testing import call_decorator
    >>> from pyams_form.ajax import ajax_form_config
    >>> from pyams_pagelet.interfaces import IPagelet

    >>> call_decorator(config, ajax_form_config, TestEditForm,
    ...                name='test.html', context=None)

    >>> config.registry.queryMultiAdapter((content, request), IPagelet, name='test.html')
    <pyams_form.testing.TestEditForm object at 0x...>

    >>> from pyramid.view import _find_views
    >>> _find_views(config.registry, IRequest, Interface, view_name='test.html')
    [<function rendered_view.<locals>.viewresult_to_response at 0x...>]
    >>> _find_views(config.registry, IRequest, Interface, view_name='test.json')
    [<function attr_wrapped_view.<locals>.attr_view at 0x...>]

Many decorator settings are automatically based on form attributes, but can be overriden using
an *ajax_* prefix:

    >>> call_decorator(config, ajax_form_config, TestEditForm,
    ...                name='test-2.html', ajax_name='another-name.json',
    ...                ajax_method='POST', ajax_permission='forbidden', ajax_xhr=False,
    ...                ajax_require_csrf=False)

    >>> _find_views(config.registry, IRequest, Interface, view_name='another-name.json')
    [<function attr_wrapped_view.<locals>.attr_view at 0x...>]


AJAX rendering with inner forms
-------------------------------

By default, when a form is containing sub-forms, the default AJAXFormRenderer is only calling
the form renderer of each subform before merging the output. But it is sometimes required to
override this default behaviour!

Let's get an example where:
 - if an attribute of the main form is modified, you need to reload the page
 - if another attribute of the main form is modified, you need to update widgets
 - if another attribute of the subform is modified, you need to update widgets.

    >>> from pyams_utils.adapter import adapter_config

    >>> class TestFormRenderer(AJAXFormRenderer):
    ...     def render(self, changes):
    ...         if 'name' in changes.get(IAJAXTestContent, ()):
    ...             return {'status': 'reload'}
    ...         return super().render(changes)

    >>> call_decorator(config, adapter_config, TestFormRenderer,
    ...                required=(IAJAXTestContent, IRequest, TestEditForm),
    ...                provides=IAJAXFormRenderer)

    >>> class MainTestFormRenderer(ContextRequestViewAdapter):
    ...     def render(self, changes):
    ...         if not changes:
    ...             return None
    ...         if 'value' in changes.get(IAJAXTestContent, ()):
    ...             return {'callback': 'MyAPP.handlers.refreshWidget'}
    ...         return None

    >>> call_decorator(config, adapter_config, MainTestFormRenderer,
    ...                name='main',
    ...                required=(IAJAXTestContent, IRequest, TestEditForm),
    ...                provides=IAJAXFormRenderer)

    >>> request = testing.TestRequest(params={'form.widgets.name': 'PyAMS form',
    ...                                       'form.widgets.value': '2021',
    ...                                       'element.widgets.label': 'PyAMS form',
    ...                                       'form.buttons.apply': 'Apply'})
    >>> result = render_view(content, request, 'test-edit-form.json')
    >>> pprint.pprint(json.loads(result.decode()))
    {'status': 'reload'}

    >>> request = testing.TestRequest(params={'form.widgets.name': 'PyAMS form',
    ...                                       'form.widgets.value': '2022',
    ...                                       'element.widgets.label': 'PyAMS form',
    ...                                       'form.buttons.apply': 'Apply'})
    >>> result = render_view(content, request, 'test-edit-form.json')
    >>> pprint.pprint(json.loads(result.decode()))
    {'callback': 'MyAPP.handlers.refreshWidget',
     'events': [{'event_type': 'refresh',
                 'source': 'element.widgets.label',
                 'value': 'PyAMS form'}],
     'message': 'Data successfully updated.',
     'status': 'success'}


Tests cleanup:

  >>> tearDown()
