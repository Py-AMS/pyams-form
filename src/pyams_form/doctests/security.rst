
==========================
Managing forms permissions
==========================

Forms security can rely on several mechanisms.

The first one is to define a permission which is required to access the form's content from an
HTTP request; as forms are generally defined as views (or pagelets), the permission is the one
which is declared into view declaration, and is used by standard Pyramid's security policy.

The second security mechanism can be used to protect objects from updates inside a form. Several
mechanisms can be used here:

 - if a form's context field is wrapped into a Zope security proxy (see :py:mod:`zope.security`
   package), the :py:class:`pyams_utils.interfaces.form.IDataManager` adapter will determine if
   this field can be in input mode or in display mode

 - if an edit permission is defined on the form, this permission will be required to get access
   to form's input mode; otherwise, the form will be in display mode

 - a (multi-)adapter to :py:class:`pyams_form.interfaces.form.IViewContextPermissionChecker` can
   be defined, for context, request and form or only for context; this adapter, if any, will
   return the permission required to get access to form in edit mode.

Add form generally don't implement a specific edit permission, as getting access to form is
enough; edit form can implement more complex rules using *IViewContextPermissionChecker* adapters,
notably when form's content is using an update workflow.

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

Let's start by creating a simple context, and a form:

  >>> from zope.interface import Interface, implementer
  >>> from zope.schema import TextLine, fieldproperty

  >>> class IMyContext(Interface):
  ...     """Context marker interface"""
  ...     value = TextLine(title="Simple value")

  >>> @implementer(IMyContext)
  ... class MyContext:
  ...     """Context implementation"""
  ...     value = fieldproperty.FieldProperty(IMyContext['value'])

  >>> from pyams_form.form import EditForm
  >>> from pyams_form.field import Fields

  >>> class MyEditForm(EditForm):
  ...     fields = Fields(IMyContext)

  >>> context = MyContext()
  >>> request = testing.TestRequest()
  >>> my_form = MyEditForm(context, request)

Default mode for an edit form is INPUT_MODE:

  >>> my_form.update()
  >>> my_form.edit_permission is None
  True
  >>> my_form.mode
  'input'
  >>> my_form.widgets['value'].mode
  'input'

Let's try to set an edit permission; the FORBIDDEN_PERMISSION is denied for any principal,
including the system manager:

  >>> from pyams_security.interfaces.base import FORBIDDEN_PERMISSION
  >>> my_form._edit_permission = FORBIDDEN_PERMISSION
  >>> my_form.update()
  >>> my_form.edit_permission == FORBIDDEN_PERMISSION
  True
  >>> my_form.mode
  'display'

Let's try to use another permission:

  >>> my_form._edit_permission = 'manage'
  >>> my_form.update()
  >>> my_form.edit_permission
  'manage'
  >>> my_form.mode
  'input'

The form is always in input mode because request's permissions can't be verified
without an authentication and an authorization policies; we are going to create fake policies
for testing (which will always deny permissions):

  >>> from pyramid.interfaces import IAuthenticationPolicy, IAuthorizationPolicy
  >>> from pyramid.security import Everyone
  >>> class AuthenticationPolicy:
  ...     def effective_principals(self, request, context=None):
  ...         return {Everyone}

  >>> from pyramid.security import ACLDenied
  >>> class AuthorizationPolicy:
  ...     def permits(self, context, principals, permission):
  ...         return ACLDenied(None, None, None, permission, context)

  >>> policy = AuthenticationPolicy()
  >>> config.registry.registerUtility(policy, IAuthenticationPolicy)
  >>> policy = AuthorizationPolicy()
  >>> config.registry.registerUtility(policy, IAuthorizationPolicy)

  >>> my_form.update()
  >>> my_form.mode
  'display'
  >>> my_form.widgets['value'].mode
  'display'


Using form context security adapter
-----------------------------------

We are now going to use a form context security checker adapter:

  >>> from pyams_utils.adapter import ContextAdapter
  >>> from pyams_security.interfaces import IViewContextPermissionChecker

  >>> @implementer(IViewContextPermissionChecker)
  ... class ForbiddenSecurityChecker(ContextAdapter):
  ...     @property
  ...     def edit_permission(self):
  ...         return FORBIDDEN_PERMISSION

  >>> config.registry.registerAdapter(ForbiddenSecurityChecker,
  ...       required=(IMyContext,),
  ...       provided=IViewContextPermissionChecker)

  >>> my_form._edit_permission = None
  >>> my_form.update()
  >>> my_form.edit_permission == FORBIDDEN_PERMISSION
  True
  >>> my_form.mode
  'display'

If a security checker returns a null permission, it's always granted:

  >>> @implementer(IViewContextPermissionChecker)
  ... class AllowedSecurityChecker(ContextAdapter):
  ...     @property
  ...     def edit_permission(self):
  ...         return None

  >>> config.registry.registerAdapter(AllowedSecurityChecker,
  ...       required=(IMyContext,),
  ...       provided=IViewContextPermissionChecker)

  >>> my_form.update()
  >>> my_form.edit_permission is None
  True
  >>> my_form.mode
  'input'


Tests cleanup:

  >>> tearDown()