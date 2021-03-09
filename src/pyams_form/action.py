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

"""PyAMS_form.action module

This module defines all actions.
"""

from zope.interface import implementer, implementer_only

from pyams_form.interfaces.button import ActionExecutionError, IAction, IActionErrorEvent, \
    IActionEvent, IActionHandler, IActions
from pyams_form.util import Manager, create_id


__docformat__ = 'restructuredtext'


@implementer(IActionEvent)
class ActionEvent:
    """Base action event class"""

    def __init__(self, action):
        self.action = action

    def __repr__(self):
        return '<%s for %r>' % (self.__class__.__name__, self.action)


@implementer(IActionErrorEvent)
class ActionErrorOccurred(ActionEvent):
    """An event telling the system that an error occurred during action
    execution."""

    def __init__(self, action, error):
        super().__init__(action)
        self.error = error


class ActionSuccessful(ActionEvent):
    """An event signalizing that an action has been successfully executed."""


@implementer(IAction)
class Action:
    """Action class."""

    __name__ = __parent__ = None

    def __init__(self, request, title, name=None):
        self.request = request
        self.title = title
        if name is None:
            name = create_id(title)
        self.name = name

    def is_executed(self):
        """Check if action was executed by looking for action name into request params"""
        return self.name in self.request.params

    def __repr__(self):
        return '<%s %r %r>' % (self.__class__.__name__, self.name, self.title)


@implementer_only(IActions)
class Actions(Manager):
    """Action manager class."""

    __name__ = __parent__ = None

    def __init__(self, form, request, content):
        super().__init__()
        self.form = form
        self.request = request
        self.content = content

    @property
    def executed_actions(self):
        """Get list of executed actions"""
        return [action for action in self.values()
                if action.is_executed()]

    def update(self):
        """See pyams_form.interfaces.button.IActions."""

    def execute(self):
        """See pyams_form.interfaces.button.IActions."""
        registry = self.request.registry
        for action in self.executed_actions:
            handler = registry.queryMultiAdapter((self.form, self.request, self.content, action),
                                                 IActionHandler)
            if handler is not None:
                try:
                    result = handler()
                except ActionExecutionError as error:
                    registry.notify(ActionErrorOccurred(action, error))
                else:
                    registry.notify(ActionSuccessful(action))
                    return result
        return None

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


@implementer(IActionHandler)
class ActionHandlerBase:
    """Action handler base adapter."""

    def __init__(self, form, request, content, action):
        self.form = form
        self.request = request
        self.content = content
        self.action = action
