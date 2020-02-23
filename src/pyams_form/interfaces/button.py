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

"""PyAMS_*** module

"""
from zope.interface import Attribute, Interface
from zope.schema import Field, Object, TextLine

from pyams_form.interfaces import IField, IManager, ISelectionManager
from pyams_form.interfaces.widget import IFieldWidget, IWidget


__docformat__ = 'restructuredtext'

from pyams_form import _


class ActionExecutionError(Exception):
    """An error that occurs during the execution of an action handler."""

    def __init__(self, error):  # pylint: disable=super-init-not-called
        self.error = error

    def __repr__(self):
        return '<%s wrapping %r>' % (self.__class__.__name__, self.error)


class WidgetActionExecutionError(ActionExecutionError):
    """An action execution error that occurred due to a widget value being
    incorrect."""

    def __init__(self, widget_name, error):
        ActionExecutionError.__init__(self, error)
        self.widget_name = widget_name


class IAction(Interface):
    """Action"""

    __name__ = TextLine(title=_('Name'),
                        description=_('The object name.'),
                        required=False,
                        default=None)

    title = TextLine(title=_('Title'),
                     description=_('The action title.'),
                     required=True)

    def is_executed(self):
        """Determine whether the action has been executed."""


class IActionHandler(Interface):
    """Action handler."""


class IActionEvent(Interface):
    """An event specific for an action."""

    action = Object(title=_('Action'),
                    description=_('The action for which the event is created.'),
                    schema=IAction,
                    required=True)


class IActionErrorEvent(IActionEvent):
    """An action event that is created when an error occurred."""

    error = Field(title=_('Error'),
                  description=_('The error that occurred during the action.'),
                  required=True)


class IActions(IManager):
    """A action manager"""

    executed_actions = Attribute('''An iterable of all executed actions (usually just one).''')

    def update(self):
        """Setup actions."""

    def execute(self):
        """Exceute actions.

        If an action execution error is raised, the system is notified using
        the action occurred error; on the other hand, if successful, the
        action successfull event is sent to the system.
        """


class IButton(IField):
    """A button in a form."""

    access_key = TextLine(title=_('Access Key'),
                          description=_('The key when pressed causes the button to be pressed'),
                          min_length=1,
                          max_length=1,
                          required=False)

    action_factory = Field(title=_('Action Factory'),
                           description=_('The action factory'),
                           required=False,
                           default=None,
                           missing_value=None)


class IImageButton(IButton):
    """An image button in a form."""

    image = TextLine(title=_('Image Path'),
                     description=_('A relative image path to the root of the resources'),
                     required=True)


class IButtons(ISelectionManager):
    """Button manager."""


class IButtonAction(IAction, IWidget, IFieldWidget):
    """Button action."""


class IButtonHandlers(Interface):
    """A collection of handlers for buttons."""

    def add_handler(self, button, handler):
        """Add a new handler for a button."""

    def get_handler(self, button):
        """Get the handler for the button."""

    def copy(self):
        """Copy this object and return the copy."""

    def __add__(self, other):
        """Add another handlers object.

        During the process a copy of the current handlers object should be
        created and the other one is added to the copy. The return value is
        the copy.
        """


class IButtonHandler(Interface):
    """A handler managed by the button handlers."""

    def __call__(self, form, action):  # pylint: disable=signature-differs
        """Execute the handler."""
