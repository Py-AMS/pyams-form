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
from pyramid_chameleon.interfaces import IChameleonTranslate
from zope.interface import implementer
from zope.lifecycleevent import Attributes, ObjectCreatedEvent, ObjectModifiedEvent
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty

from pyams_form.button import Buttons, Handlers, button_and_handler
from pyams_form.events import DataExtractedEvent
from pyams_form.field import Fields
from pyams_form.interfaces import DISPLAY_MODE, INPUT_MODE
from pyams_form.interfaces.button import IActionErrorEvent, IActions, WidgetActionExecutionError
from pyams_form.interfaces.error import IErrorViewSnippet
from pyams_form.interfaces.form import IActionForm, IAddForm, IButtonForm, IDisplayForm, IEditForm, \
    IFieldsForm, IForm, IFormAware, IFormContextPermissionChecker, IGroup, IGroupManager, \
    IHandlerForm, IInnerSubForm, IInnerTabForm, IInputForm
from pyams_form.interfaces.widget import IWidgets
from pyams_form.util import changed_field
from pyams_security.interfaces.base import FORBIDDEN_PERMISSION
from pyams_template.interfaces import IContentTemplate, ILayoutTemplate
from pyams_template.template import get_content_template, get_layout_template
from pyams_utils.adapter import ContextRequestAdapter
from pyams_utils.interfaces import ICacheKeyValue
from pyams_utils.interfaces.form import IDataManager, NOT_CHANGED
from pyams_utils.registry import query_utility


__docformat__ = 'restructuredtext'

from pyams_form import _


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
            dm = registry.getMultiAdapter((content, field.field), IDataManager)
            dm.set(new_value)
            # Record the change using information required later
            changes.setdefault(dm.field.interface, []).append(name)
    return changes


def extends(*args, **kwargs):
    """Extend fields, buttons and handlers"""
    frame = sys._getframe(1)
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

    label = None
    label_required = _('<span class="required">*</span>&ndash; required')

    prefix = 'form.'
    status = ''
    layout = get_layout_template()
    template = get_content_template()
    widgets = None

    _mode = INPUT_MODE
    _edit_permission = None

    ignore_context = False
    ignore_request = False
    ignore_readonly = False
    ignore_required_on_extract = False

    @property
    def mode(self):
        mode = self._mode
        if mode == DISPLAY_MODE:  # already updated mode
            return mode
        permission = self.edit_permission
        if permission:
            if permission == FORBIDDEN_PERMISSION:
                mode = DISPLAY_MODE
            else:
                content = self.get_content()
                if not self.request.has_permission(permission, content):
                    mode = DISPLAY_MODE
        return mode

    @mode.setter
    def mode(self, value):
        self._mode = value

    @property
    def edit_permission(self):
        permission = self._edit_permission
        if permission is not None:  # locally defined edit permission
            return permission
        registry = self.request.registry
        content = self.get_content()
        checker = registry.queryMultiAdapter((content, self.request, self),
                                             IFormContextPermissionChecker)
        if checker is None:
            checker = registry.queryAdapter(content, IFormContextPermissionChecker)
        if checker is not None:
            return checker.edit_permission
        return None

    def get_content(self):
        """See interfaces.IForm"""
        return self.context

    @property
    def required_info(self):
        if (self.label_required is not None and
                self.widgets is not None and
                self.widgets.has_required_fields):
            return self.request.localizer.translate(self.label_required)

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
        registry = self.request.registry
        return sorted((adapter
                       for name, adapter in registry.getAdapters((self.context, self.request, self),
                                                                 IInnerTabForm)),
                      key=get_form_weight)

    def get_forms(self, include_self=True):
        """Get all forms associated with this form"""
        if include_self:
            yield self
        if IGroupManager.providedBy(self):
            for group in self.groups:
                yield from group.get_forms()
        for form in self.subforms:
            yield from form.get_forms()
        for form in self.tabforms:
            yield from form.get_forms()

    def update(self):
        """See interfaces.IForm"""
        self.update_widgets()
        [subform.update() for subform in self.subforms]
        [tabform.update() for tabform in self.tabforms]

    def update_widgets(self, prefix=None):
        """See interfaces.IForm"""
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
        """See interfaces.IForm"""
        self.widgets.set_errors = set_errors
        self.widgets.ignore_required_on_extract = self.ignore_required_on_extract
        data, errors = self.widgets.extract()
        self.request.registry.notify(DataExtractedEvent(data, errors, self))
        return data, errors

    def get_errors(self):
        """Get all errors, including groups and inner forms"""
        result = []
        for form in self.get_forms():
            result.extend(form.widgets.errors)
        return result

    def render(self):
        """See interfaces.IForm"""
        # render content template
        request = self.request
        cdict = {
            'context': self.context,
            'request': request,
            'view': self,
            'translate': query_utility(IChameleonTranslate)
        }
        if self.template is None:
            registry = request.registry
            template = registry.queryMultiAdapter((self.context, self.request, self),
                                                  IContentTemplate)
            if template is None:
                template = registry.getMultiAdapter((self, self.request), IContentTemplate)
            return template(**cdict)
        return self.template(**cdict)

    def __call__(self, **kwargs):
        self.update()

        # Don't render anything if we are doing a redirect
        request = self.request
        if request.response.status_code in REDIRECT_STATUS_CODES:
            return Response('')

        cdict = {
            'context': self.context,
            'request': request,
            'view': self,
            'translate': query_utility(IChameleonTranslate)
        }
        cdict.update(kwargs)
        if self.layout is None:
            registry = request.registry
            layout = registry.queryMultiAdapter((self.context, self.request, self),
                                                ILayoutTemplate)
            if layout is None:
                layout = registry.getMultiAdapter((self, request), ILayoutTemplate)
            return Response(layout(**cdict))
        return Response(self.layout(**cdict))

    def json(self):
        data = {
            'errors': [
                error.message for error in
                (self.widgets.errors or []) if error.field is None
            ],
            'prefix': self.prefix,
            'status': self.status,
            'mode': self.mode,
            'fields': [widget.json_data() for widget in self.widgets.values()],
            'label': self.label or ''
        }
        return json.dumps(data)


@implementer(IDisplayForm)
class DisplayForm(BaseForm):

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

    actions = FieldProperty(IActionForm['actions'])
    refresh_actions = FieldProperty(IActionForm['refresh_actions'])

    # common string for use in validation status messages
    form_errors_message = _('There were some errors.')

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.request.url

    @property
    def name(self):
        """See interfaces.IInputForm"""
        return self.prefix.strip('.')

    @property
    def id(self):
        return self.name.replace('.', '-')

    def update_actions(self):
        registry = self.request.registry
        self.actions = registry.getMultiAdapter((self, self.request, self.get_content()), IActions)
        self.actions.update()

    def update(self):
        super(Form, self).update()
        self.update_actions()
        self.actions.execute()
        if self.refresh_actions:
            self.update_actions()


@implementer(IAddForm)
class AddForm(Form):
    """A field and button based add form."""

    ignore_context = True
    ignore_readonly = True

    _finished_add = False

    @button_and_handler(_('Add'), name='add')
    def handle_add(self, action):
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
            self._finished_add = True

    def create_and_add(self, data):
        obj = self.create(data.get(self, {}))
        self.request.registry.notify(ObjectCreatedEvent(obj))
        if IPersistent.providedBy(obj):  # temporary locate to fix raising of INotYet exceptions
            locate(obj, self.context)
        self.add(obj)
        self.update_content(obj, data)
        return obj

    def create(self, data):
        raise NotImplementedError

    def add(self, object):
        raise NotImplementedError

    def update_content(self, obj, data):
        changes = {}
        for form in self.get_forms():
            if form.mode == DISPLAY_MODE:
                continue
            merge_changes(changes, apply_changes(form, obj, data))
        return changes

    def next_url(self):
        return self.action

    def render(self):
        if self._finished_add:
            self.request.response.location = self.next_url()
            self.request.response.status = 302
            return ''
        return super(AddForm, self).render()


@implementer(IEditForm)
class EditForm(Form):
    """A simple edit form with an apply button."""

    success_message = _('Data successfully updated.')
    no_changes_message = _('No changes were applied.')

    @button_and_handler(_('Apply'), name='apply')
    def handle_apply(self, action):
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
