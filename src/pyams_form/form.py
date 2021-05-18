#
# Copyright (c) 2015-2020 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_form.form module

This module defines all main forms management classes.
"""

import json
import sys

from persistent import IPersistent
from pyramid.decorator import reify
from pyramid.events import subscriber
from pyramid.response import Response
from zope.interface import implementer
from zope.lifecycleevent import Attributes, ObjectCreatedEvent, ObjectModifiedEvent
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty

from pyams_form.button import Buttons, Handlers, button_and_handler
from pyams_form.events import DataExtractedEvent, FormCreatedEvent
from pyams_form.field import Fields
from pyams_form.interfaces import DISPLAY_MODE, INPUT_MODE
from pyams_form.interfaces.button import IActionErrorEvent, IActions, WidgetActionExecutionError
from pyams_form.interfaces.error import IErrorViewSnippet
from pyams_form.interfaces.form import IActionForm, IAddForm, IButtonForm, IDisplayForm, \
    IEditForm, IFieldsForm, IForm, IFormAware, IGroup, IGroupManager, IHandlerForm, \
    IInnerSubForm, IInnerTabForm, IInputForm
from pyams_form.interfaces.widget import IWidgets
from pyams_form.util import changed_field
from pyams_security.interfaces.base import FORBIDDEN_PERMISSION
from pyams_security.permission import get_edit_permission
from pyams_template.template import get_content_template, get_layout_template
from pyams_utils.adapter import ContextRequestAdapter
from pyams_utils.factory import get_object_factory, is_interface
from pyams_utils.interfaces import ICacheKeyValue
from pyams_utils.interfaces.form import IDataManager, NOT_CHANGED
from pyams_utils.url import absolute_url


__docformat__ = 'restructuredtext'

from pyams_form import _  # pylint: disable=ungrouped-imports


REDIRECT_STATUS_CODES = (300, 301, 302, 303, 304, 305, 307)


def get_form_weight(form):
    """Try to get form weight attribute"""
    try:
        return form.weight
    except AttributeError:
        return 0


def apply_changes(form, content, data):
    """Apply form changes to content"""
    data = data.get(form, data)
    changes = {}
    registry = form.request.registry
    for name, field in form.fields.items():
        # If the field is not in the data, then go on to the next one
        try:
            new_value = data[name]
        except KeyError:
            continue
        # If the value is NOT_CHANGED, ignore it, since the widget/converter
        # sent a strong message not to do so.
        if new_value is NOT_CHANGED:
            continue
        if changed_field(field.field, new_value, context=content):
            # Only update the data, if it is different
            dman = registry.getMultiAdapter((content, field.field), IDataManager)
            dman.set(new_value)
            # Record the change using information required later
            changes.setdefault(dman.field.interface, []).append(name)
    return changes


def extends(*args, **kwargs):
    """Extend fields, buttons and handlers"""
    frame = sys._getframe(1)  # pylint: disable=protected-access
    f_locals = frame.f_locals
    if not kwargs.get('ignore_fields', False):
        f_locals['fields'] = Fields()
        for arg in args:
            f_locals['fields'] += getattr(arg, 'fields', Fields())
    if not kwargs.get('ignore_buttons', False):
        f_locals['buttons'] = Buttons()
        for arg in args:
            f_locals['buttons'] += getattr(arg, 'buttons', Buttons())
    if not kwargs.get('ignore_handlers', False):
        f_locals['handlers'] = Handlers()
        for arg in args:
            f_locals['handlers'] += getattr(arg, 'handlers', Handlers())


def merge_changes(source, changes):
    """Merge new changes with existing ones"""
    for intf, field_names in changes.items():
        source[intf] = source.get(intf, []) + field_names


@subscriber(IActionErrorEvent)
def handle_action_error(event):
    """Action error subscriber"""
    # Only react to the event, if the form is a standard form.
    if not (IFormAware.providedBy(event.action) and
            IForm.providedBy(event.action.form)):
        return
    # If the error was widget-specific, look up the widget.
    widget = None
    if isinstance(event.error, WidgetActionExecutionError):
        widget = event.action.form.widgets[event.error.widget_name]
    # Create an error view for the error.
    action = event.action
    form = action.form
    registry = form.request.registry
    error_view = registry.getMultiAdapter((event.error.error, action.request, widget,
                                           getattr(widget, 'field', None), form,
                                           form.get_content()),
                                          IErrorViewSnippet)
    error_view.update()
    # Assign the error view to all necessary places.
    if widget:
        widget.error = error_view
    form.widgets.errors += (error_view,)
    # If the form supports the ``form_errors_message`` attribute, then set the
    # status to it.
    if hasattr(form, 'form_errors_message'):
        form.status = form.form_errors_message


@implementer(IForm, IFieldsForm)
class BaseForm(ContextRequestAdapter):
    """A base form."""

    fields = Fields()

    title = None
    legend = None
    required_label = _('<span class="required">*</span>&ndash; required')

    prefix = 'form.'
    status = ''
    widgets = None

    template = get_content_template()
    layout = get_layout_template()

    _mode = INPUT_MODE
    _edit_permission = None

    ignore_context = False
    ignore_request = False
    ignore_readonly = False
    ignore_required_on_extract = False

    @property
    def mode(self):
        """Current mode getter"""
        mode = self._mode
        if mode == DISPLAY_MODE:  # already custom mode
            return mode
        permission = self.edit_permission
        if permission:
            if permission == FORBIDDEN_PERMISSION:
                mode = DISPLAY_MODE
            else:
                content = self.get_content()
                if not self.request.has_permission(permission, context=content):
                    mode = DISPLAY_MODE
        return mode

    @mode.setter
    def mode(self, value):
        """Form mode setter"""
        self._mode = value

    @property
    def edit_permission(self):
        """Permission required to access form in input mode"""
        permission = self._edit_permission
        if permission is not None:  # locally defined edit permission
            return permission
        content = self.get_content()
        return get_edit_permission(self.request, content, self)

    def get_content(self):
        """See interfaces.form.IForm"""
        return self.context

    @property
    def required_info(self):
        """Form required information label"""
        if (self.required_label is not None and self.widgets is not None and
                self.widgets.has_required_fields):
            return self.request.localizer.translate(self.required_label)
        return None

    @reify
    def subforms(self):
        """Get list of internal sub-forms"""
        registry = self.request.registry
        return sorted((adapter
                       for name, adapter in registry.getAdapters((self.context, self.request, self),
                                                                 IInnerSubForm)),
                      key=get_form_weight)

    @reify
    def tabforms(self):
        """Get list of internal tab-forms"""
        registry = self.request.registry
        return sorted((adapter
                       for name, adapter in registry.getAdapters((self.context, self.request, self),
                                                                 IInnerTabForm)),
                      key=get_form_weight)

    def get_forms(self, include_self=True):
        """Get all forms associated with this form"""
        if include_self:
            yield self
        manager = IGroupManager(self, None)
        if manager is not None:
            for group in manager.groups:
                yield from group.get_forms()
        for form in self.subforms:
            yield from form.get_forms()
        for form in self.tabforms:
            yield from form.get_forms()

    def update(self):
        """See interfaces.form.IForm"""
        self.update_widgets()
        [subform.update() for subform in self.subforms]  # pylint: disable=expression-not-assigned
        [tabform.update() for tabform in self.tabforms]  # pylint: disable=expression-not-assigned

    def update_widgets(self, prefix=None):
        """See interfaces.form.IForm"""
        registry = self.request.registry
        self.widgets = registry.getMultiAdapter((self, self.request, self.get_content()),
                                                IWidgets)
        if prefix is not None:
            self.widgets.prefix = prefix
        self.widgets.mode = self.mode
        self.widgets.ignore_context = self.ignore_context
        self.widgets.ignore_request = self.ignore_request
        self.widgets.ignore_readonly = self.ignore_readonly
        self.widgets.update()

    def extract_data(self, set_errors=True):
        """See interfaces.form.IForm"""
        self.widgets.set_errors = set_errors
        self.widgets.ignore_required_on_extract = self.ignore_required_on_extract
        data, errors = self.widgets.extract()
        self.request.registry.notify(DataExtractedEvent(data, errors, self))
        if not errors:
            errors = self.widgets.errors
        return data, errors

    def get_errors(self):
        """Get all errors, including groups and inner forms"""
        for form in self.get_forms():
            yield from form.widgets.errors

    def render(self):
        """See interfaces.form.IForm"""
        return self.template()

    def __call__(self, **kwargs):
        """Call update and return layout template"""
        self.request.registry.notify(FormCreatedEvent(self))
        self.update()

        # Don't render anything if we are doing a redirect
        request = self.request
        if request.response.status_code in REDIRECT_STATUS_CODES:
            return Response('')

        return Response(self.layout(**kwargs))

    def json(self):
        """Get form data in JSON format"""
        data = {
            'errors': [
                error.message
                for error in (self.widgets.errors or [])
                if error.field is None
            ],
            'prefix': self.prefix,
            'status': self.status,
            'mode': self.mode,
            'fields': [
                widget.json_data()
                for widget in self.widgets.values()
            ],
            'title': self.title or '',
            'legend': self.legend or ''
        }
        return json.dumps(data)


@implementer(IDisplayForm)
class DisplayForm(BaseForm):
    """Display only form"""

    _mode = DISPLAY_MODE
    ignore_request = True


@implementer(IInputForm, IButtonForm, IHandlerForm, IActionForm)
class Form(BaseForm):
    """The Form."""

    buttons = Buttons()

    method = FieldProperty(IInputForm['method'])
    enctype = FieldProperty(IInputForm['enctype'])
    accept_charset = FieldProperty(IInputForm['accept_charset'])
    accept = FieldProperty(IInputForm['accept'])
    autocomplete = FieldProperty(IInputForm['autocomplete'])

    actions = FieldProperty(IActionForm['actions'])
    refresh_actions = FieldProperty(IActionForm['refresh_actions'])

    # AJAX related form properties
    ajax_form_handler = FieldProperty(IInputForm['ajax_form_handler'])
    ajax_form_options = FieldProperty(IInputForm['ajax_form_options'])
    ajax_form_target = FieldProperty(IInputForm['ajax_form_target'])
    ajax_form_callback = FieldProperty(IInputForm['ajax_form_callback'])

    # common string for use in validation status messages
    form_errors_message = _('There were some errors.')

    def __init__(self, context, request):
        super().__init__(context, request)
        self.finished_state = {}

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.request.url

    @property
    def name(self):
        """See interfaces.IInputForm"""
        return self.prefix.strip('.')

    @property
    def id(self):  # pylint: disable=invalid-name
        """Form ID"""
        return self.name.replace('.', '-')

    def update_actions(self):
        """Update form actions"""
        registry = self.request.registry
        self.actions = registry.getMultiAdapter((self, self.request, self.get_content()),
                                                IActions)
        self.actions.update()

    def update(self):
        super().update()
        self.update_actions()
        self.actions.execute()
        if self.refresh_actions:
            self.update_actions()

    def get_ajax_handler(self):
        """Get absolute URL of AJAX handler"""
        return absolute_url(self.context, self.request, self.ajax_form_handler)

    def get_form_options(self):
        """Get form options in JSON format"""
        return json.dumps(self.ajax_form_options) if self.ajax_form_options else None


@implementer(IAddForm)
class AddForm(Form):
    """A field and button based add form."""

    ignore_context = True
    ignore_readonly = True

    content_factory = None

    @button_and_handler(_('Add'), name='add')
    def handle_add(self, action):  # pylint: disable=unused-argument
        """Handler for *add* button"""
        data, errors = {}, {}
        for form in self.get_forms():
            form_data, form_errors = form.extract_data()
            if form_errors:
                if not IGroup.providedBy(form):
                    form.status = getattr(form, 'form_errors_message', self.form_errors_message)
                errors[form] = form_errors
            data[form] = form_data
        if errors:
            self.status = self.form_errors_message
            return
        obj = self.create_and_add(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self.finished_state.update({
                'action': action,
                'changes': obj
            })

    def create_and_add(self, data):
        """Create new content and add it to context"""
        obj = self.create(data.get(self, {}))
        self.request.registry.notify(ObjectCreatedEvent(obj))
        if IPersistent.providedBy(obj):  # temporary locate to fix raising of INotYet exceptions
            locate(obj, self.context)
        self.update_content(obj, data)
        self.add(obj)
        return obj

    def create(self, data):  # pylint: disable=unused-argument
        """Create new content from form data"""
        if self.content_factory is not None:
            factory = get_object_factory(self.content_factory) \
                if is_interface(self.content_factory) else self.content_factory
            return factory()  # pylint: disable=not-callable
        raise NotImplementedError

    def add(self, obj):  # pylint: disable=redefined-builtin
        """Add new object to form context"""
        raise NotImplementedError

    def update_content(self, obj, data):
        """Update content with form data after creation"""
        changes = {}
        for form in self.get_forms():
            if form.mode == DISPLAY_MODE:
                continue
            merge_changes(changes, apply_changes(form, obj, data))
        return changes

    def next_url(self):
        """Redirection URL after object creation"""
        return self.action

    def render(self):
        if self.finished_state:
            self.request.response.location = self.next_url()
            self.request.response.status = 302
            return ''
        return super().render()


@implementer(IEditForm)
class EditForm(Form):
    """A simple edit form with an apply button."""

    success_message = _('Data successfully updated.')
    no_changes_message = _('No changes were applied.')

    @button_and_handler(_('Apply'), name='apply')
    def handle_apply(self, action):  # pylint: disable=unused-argument
        """Apply action handler"""
        data, errors = {}, {}
        for form in self.get_forms():
            form_data, form_errors = form.extract_data()
            if form_errors:
                if not IGroup.providedBy(form):
                    form.status = getattr(form, 'form_errors_message', self.form_errors_message)
                errors[form] = form_errors
            data[form] = form_data
        if errors:
            self.status = self.form_errors_message
            return
        changes = self.apply_changes(data)
        if changes:
            self.status = self.success_message
        else:
            self.status = self.no_changes_message
        self.finished_state.update({
            'action': action,
            'changes': changes
        })

    def apply_changes(self, data):
        """Apply updates to form context"""
        changes = {}
        contents, changed_contents = {}, {}
        for form in self.get_forms():
            if form.mode == DISPLAY_MODE:
                continue
            content = form.get_content()
            form_changes = apply_changes(form, content, data)
            if form_changes:
                merge_changes(changes, form_changes)
                content_hash = ICacheKeyValue(content)
                contents[content_hash] = content
                merge_changes(changed_contents.setdefault(content_hash, {}), form_changes)
        if changes:
            # Construct change-descriptions for the object-modified event
            for content_hash, content_changes in changed_contents.items():
                descriptions = []
                for interface, names in content_changes.items():
                    descriptions.append(Attributes(interface, *names))
                # Send out a detailed object-modified event
                self.request.registry.notify(ObjectModifiedEvent(contents[content_hash],
                                                                 *descriptions))
        return changes


class FormSelector:
    """Form event selector

    This predicate can be used by subscribers to filter form events
    """

    def __init__(self, ifaces, config):  # pylint: disable=unused-argument
        if not isinstance(ifaces, (list, tuple)):
            ifaces = (ifaces,)
        self.interfaces = ifaces

    def text(self):
        """Form's selector text"""
        return 'form_selector = %s' % str(self.interfaces)

    phash = text

    def __call__(self, event):
        for intf in self.interfaces:
            try:
                if intf.providedBy(event.form):
                    return True
            except (AttributeError, TypeError):
                if isinstance(event.form, intf):
                    return True
        return False
