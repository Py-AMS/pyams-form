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

"""PyAMS_form.group module

This module handles groups of widgets within forms.
"""

from zope.interface import implementer
from zope.lifecycleevent import Attributes, ObjectModifiedEvent

from pyams_form.events import DataExtractedEvent
from pyams_form.form import BaseForm, apply_changes
from pyams_form.interfaces.form import IGroup, IGroupForm
from pyams_form.interfaces.widget import IWidgets


__docformat__ = 'restructuredtext'


@implementer(IGroup)
class Group(BaseForm):
    """Group of field widgets within form"""

    groups = ()

    def __init__(self, context, request, parent_form):
        self.context = context
        self.request = request
        self.parent_form = self.__parent__ = parent_form

    def update_widgets(self, prefix=None):
        """See interfaces.IForm"""
        registry = self.request.registry
        self.widgets = registry.getMultiAdapter((self, self.request, self.get_content()),
                                                IWidgets)
        for attr_name in ('mode', 'ignore_request', 'ignore_context', 'ignore_readonly'):
            value = getattr(self.parent_form.widgets, attr_name)
            setattr(self.widgets, attr_name, value)
        if prefix is not None:
            self.widgets.prefix = prefix
        self.widgets.update()

    def update(self):
        """See interfaces.IForm"""
        self.update_widgets()
        groups = []
        for group_class in self.groups:
            # only instantiate the group_class if it hasn't already
            # been instantiated
            if IGroup.providedBy(group_class):
                group = group_class
            else:
                group = group_class(self.context, self.request, self)
            group.update()
            groups.append(group)
        self.groups = tuple(groups)

    def extract_data(self, set_errors=True):
        """See interfaces.IForm"""
        data, errors = super(Group, self).extract_data(set_errors=set_errors)
        for group in self.groups:
            group_data, group_errors = group.extract_data(set_errors=set_errors)
            data.update(group_data)
            if group_errors:
                if errors:
                    errors += group_errors
                else:
                    errors = group_errors
        registry = self.request.registry
        registry.notify(DataExtractedEvent(data, errors, self))
        return data, errors

    def apply_changes(self, data):
        """See interfaces.IEditForm"""
        content = self.get_content()
        changed = apply_changes(self, content, data)
        for group in self.groups:
            group_changed = group.apply_changes(data)
            for interface, names in group_changed.items():
                changed[interface] = changed.get(interface, []) + names
        return changed


@implementer(IGroupForm)
class GroupForm:
    """A mix-in class for add and edit forms to support groups."""

    groups = ()

    def extract_data(self, set_errors=True):
        """See interfaces.IForm"""
        data, errors = super(GroupForm, self).extract_data(set_errors=set_errors)
        for group in self.groups:
            group_data, group_errors = group.extract_data(set_errors=set_errors)
            data.update(group_data)
            if group_errors:
                if errors:
                    errors += group_errors
                else:
                    errors = group_errors
        registry = self.request.registry
        registry.notify(DataExtractedEvent(data, errors, self))
        return data, errors

    def apply_changes(self, data):
        """See interfaces.IEditForm"""
        descriptions = []
        content = self.get_content()
        changed = apply_changes(self, content, data)
        for group in self.groups:
            group_changed = group.apply_changes(data)
            for interface, names in group_changed.items():
                changed[interface] = changed.get(interface, []) + names
        if changed:
            for interface, names in changed.items():
                descriptions.append(Attributes(interface, *names))
            # Send out a detailed object-modified event
            registry = self.request.registry
            registry.notify(ObjectModifiedEvent(content, *descriptions))
        return changed

    def update(self):
        """See interfaces.IForm"""
        self.update_widgets()
        groups = []
        for group_class in self.groups:
            # only instantiate the group_class if it hasn't already
            # been instantiated
            if IGroup.providedBy(group_class):
                group = group_class
            else:
                group = group_class(self.context, self.request, self)
            group.update()
            groups.append(group)
        self.groups = tuple(groups)
        self.update_actions()
        self.actions.execute()
