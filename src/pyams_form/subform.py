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

"""PyAMS_form.subform module

This module provides subforms management.
"""

from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent

from pyams_form.button import handler
from pyams_form.form import BaseForm, EditForm, apply_changes
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.button import IActionHandler
from pyams_form.interfaces.form import IHandlerForm, IInnerForm, ISubForm


__docformat__ = 'restructuredtext'

from pyams_form import _  # pylint: disable=ungrouped-imports


@implementer(ISubForm, IInnerForm)
class BaseInnerForm(BaseForm):
    """Base inner subform"""

    def __init__(self, context, request, parent_form):
        super().__init__(context, request)
        self.parent_form = self.__parent__ = parent_form


class InnerAddForm(BaseInnerForm):
    """Inner subform into an add form"""

    ignore_context = True


class InnerEditForm(BaseInnerForm):
    """Inner edit subform into a main edit form"""


class InnerDisplayForm(BaseInnerForm):
    """Inner display form"""

    _mode = DISPLAY_MODE


@implementer(ISubForm, IHandlerForm)
class EditSubForm(BaseForm):
    """Edit sub-form"""

    form_errors_message = _('There were some errors.')
    success_message = _('Data successfully updated.')
    no_changes_message = _('No changes were applied.')

    def __init__(self, context, request, parent_form):
        super().__init__(context, request)
        self.parent_form = self.__parent__ = parent_form

    @handler(EditForm.buttons['apply'])
    def handle_apply(self, action):  # pylint: disable=unused-argument
        """Handler for apply button"""
        data, errors = self.widgets.extract()
        if errors:
            self.status = self.form_errors_message
            return
        content = self.get_content()
        changed = apply_changes(self, content, data)
        if changed:
            registry = self.request.registry
            registry.notify(ObjectModifiedEvent(content))
            self.status = self.success_message
        else:
            self.status = self.no_changes_message

    def update(self):
        super().update()
        registry = self.request.registry
        for action in self.parent_form.actions.executed_actions:
            adapter = registry.queryMultiAdapter((self, self.request, self.get_content(), action),
                                                 IActionHandler)
            if adapter:
                adapter()
