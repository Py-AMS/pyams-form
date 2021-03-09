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

"""PyAMS_form.button module

Form buttons management.
"""

import sys

from six import class_types
from zope.interface import Interface, alsoProvides, implementedBy, implementer, providedBy
from zope.interface.adapter import AdapterRegistry
from zope.interface.interfaces import IInterface
from zope.location import Location, locate
from zope.schema import Field, getFieldsInOrder
from zope.schema.fieldproperty import FieldProperty

from pyams_form.action import Action, ActionHandlerBase, Actions
from pyams_form.browser.image import ImageWidget
from pyams_form.browser.submit import SubmitWidget
from pyams_form.interfaces import IValue
from pyams_form.interfaces.button import IActionHandler, IActions, IButton, IButtonAction, \
    IButtonHandler, IButtonHandlers, IButtons, IImageButton
from pyams_form.interfaces.form import IButtonForm, IFormAware, IHandlerForm
from pyams_form.util import SelectionManager, create_id, expand_prefix, get_specification, \
    to_unicode
from pyams_form.value import ComputedValueCreator, StaticValueCreator
from pyams_form.widget import AfterWidgetUpdateEvent
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


# pylint: disable=invalid-name
StaticButtonActionAttribute = StaticValueCreator(
    discriminators=('form', 'request', 'content', 'button', 'manager')
)

# pylint: disable=invalid-name
ComputedButtonActionAttribute = ComputedValueCreator(
    discriminators=('form', 'request', 'content', 'button', 'manager')
)


@implementer(IButton)
class Button(Field):
    """A simple button in a form."""

    access_key = FieldProperty(IButton['access_key'])
    action_factory = FieldProperty(IButton['action_factory'])

    def __init__(self, *args, **kwargs):
        # Provide some shortcut ways to specify the name
        if args:
            kwargs['__name__'] = args[0]
            args = args[1:]
        if 'name' in kwargs:
            kwargs['__name__'] = kwargs['name']
            del kwargs['name']
        # Extract button-specific arguments
        self.access_key = kwargs.pop('access_key', None)
        self.condition = kwargs.pop('condition', None)
        # Initialize the button
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.__name__, self.title)


@implementer(IImageButton)
class ImageButton(Button):
    """A simple image button in a form."""

    image = FieldProperty(IImageButton['image'])

    def __init__(self, image, *args, **kwargs):
        self.image = image
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s %r %r>' %(
            self.__class__.__name__, self.__name__, self.image)


@implementer(IButtons)
class Buttons(SelectionManager):
    """Button manager."""

    manager_interface = IButtons
    prefix = 'buttons'

    def __init__(self, *args):
        buttons = []
        for arg in args:
            if IInterface.providedBy(arg):
                for name, button in getFieldsInOrder(arg):
                    if IButton.providedBy(button):
                        buttons.append((name, button))
            elif self.manager_interface.providedBy(arg):
                buttons += arg.items()
            elif IButton.providedBy(arg):
                if not arg.__name__:
                    arg.__name__ = create_id(arg.title)
                buttons.append((arg.__name__, arg))
            else:
                raise TypeError("Unrecognized argument type", arg)
        super().__init__(buttons)


@implementer(IButtonHandlers)
class Handlers:
    """Action Handlers for a Button-based form."""

    def __init__(self):
        self._registry = AdapterRegistry()
        self._handlers = ()

    def add_handler(self, button, handler):  # pylint: disable=redefined-outer-name
        """See interfaces.button.IButtonHandlers"""
        # Create a specification for the button
        button_spec = get_specification(button)
        if isinstance(button_spec, class_types):
            button_spec = implementedBy(button_spec)
        # Register the handler
        self._registry.register(
            (button_spec,), IButtonHandler, '', handler)
        self._handlers += ((button, handler),)

    def get_handler(self, button):
        """See interfaces.button.IButtonHandlers"""
        button_provided = providedBy(button)
        # pylint: disable=no-member
        return self._registry.lookup1(button_provided, IButtonHandler)

    def copy(self):
        """See interfaces.button.IButtonHandlers"""
        handlers = Handlers()
        for button, handler in self._handlers:  # pylint: disable=redefined-outer-name
            handlers.add_handler(button, handler)
        return handlers

    def __add__(self, other):
        """See interfaces.button.IButtonHandlers"""
        if not isinstance(other, Handlers):
            raise NotImplementedError
        handlers = self.copy()
        for button, handler in other._handlers:  # pylint: disable=redefined-outer-name
            handlers.add_handler(button, handler)
        return handlers

    def __repr__(self):
        # pylint: disable=redefined-outer-name
        return '<Handlers %r>' % [handler for button, handler in self._handlers]


@implementer(IButtonHandler)
class Handler:
    """Button handler class"""

    def __init__(self, button, func):
        self.button = button
        self.func = func

    def __call__(self, form, action):
        return self.func(form, action)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.button)


def handler(button):
    """A decorator for defining a success handler."""

    def create_handler(func):
        handler = Handler(button, func)  # pylint: disable=redefined-outer-name
        frame = sys._getframe(1)  # pylint: disable=protected-access
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('handlers', Handlers())
        handlers.add_handler(button, handler)
        return handler

    return create_handler


def button_and_handler(title, **kwargs):
    """Button with handler method decorator"""
    # Add the title to button constructor keyword arguments
    kwargs['title'] = title
    # Extract directly provided interfaces:
    provides = kwargs.pop('provides', ())
    # Create button and add it to the button manager
    button = Button(**kwargs)
    alsoProvides(button, provides)
    frame = sys._getframe(1)  # pylint: disable=protected-access
    f_locals = frame.f_locals
    f_locals.setdefault('buttons', Buttons())
    f_locals['buttons'] += Buttons(button)
    # Return the handler decorator
    return handler(button)


@adapter_config(required=(IFormLayer, IButton),
                provides=IButtonAction)
class ButtonAction(Action, SubmitWidget, Location):
    """Button action"""

    def __init__(self, request, field):
        Action.__init__(self, request, field.title)
        SubmitWidget.__init__(self, request)
        self.field = field

    @property
    def access_key(self):
        """Button access key"""
        return self.field.access_key

    @property
    def value(self):
        """Button value"""
        return self.title

    @property
    def id(self):
        """Button ID"""
        return self.name.replace('.', '-')


@adapter_config(required=(IFormLayer, IImageButton),
                provides=IButtonAction)
class ImageButtonAction(ImageWidget, ButtonAction):
    """Image button action"""

    def __init__(self, request, field):  # pylint: disable=super-init-not-called
        Action.__init__(self, request, field.title)  # pylint: disable=non-parent-init-called
        SubmitWidget.__init__(self, request)  # pylint: disable=non-parent-init-called
        self.field = field

    @property
    def src(self):
        """Image source"""
        return to_unicode(self.field.image)

    def is_executed(self):
        return self.name + '.x' in self.request.params


@adapter_config(required=(IButtonForm, Interface, Interface),
                provides=IActions)
class ButtonActions(Actions):
    """Button actions manager"""

    def update(self):
        """See pyams_form.interfaces.button.IActions."""
        # Create a unique prefix.
        prefix = expand_prefix(self.form.prefix)
        prefix += expand_prefix(self.form.buttons.prefix)
        # Walk through each field, making an action out of it.
        d = {}
        d.update(self)
        registry = self.request.registry
        for name, button in self.form.buttons.items():
            # Step 1: Only create an action for the button, if the condition is
            #         fulfilled.
            if button.condition is not None and not button.condition(self.form):
                # Step 1.1: If the action already existed, but now the
                #           condition became false, remove the old action.
                if name in d:
                    del d[name]
                continue
            # Step 2: Get the action for the given button.
            new_button = True
            if name in self:
                button_action = self[name]
                new_button = False
            elif button.action_factory is not None:
                button_action = button.action_factory(self.request, button)
            else:
                button_action = registry.getMultiAdapter((self.request, button), IButtonAction)
            # Step 3: Set the name on the button
            button_action.name = prefix + name
            # Step 4: Set any custom attribute values.
            title = registry.queryMultiAdapter((self.form, self.request, self.content,
                                                button, self),
                                               IValue, name='title')
            if title is not None:
                button_action.title = title.get()
            # Step 5: Set the form
            button_action.form = self.form
            if not IFormAware.providedBy(button_action):
                alsoProvides(button_action, IFormAware)
            # Step 6: Update the new action
            button_action.update()
            registry.notify(AfterWidgetUpdateEvent(button_action))
            # Step 7: Add the widget to the manager
            if new_button:
                d[name] = button_action
                locate(button_action, self, name)

        self.create_according_to_list(d, self.form.buttons.keys())


@adapter_config(required=(IHandlerForm, Interface, Interface, ButtonAction),
                provides=IActionHandler)
class ButtonActionHandler(ActionHandlerBase):
    """Button action handler"""

    def __call__(self):
        # pylint: disable=redefined-outer-name
        handler = self.form.handlers.get_handler(self.action.field)
        # If no handler is found, then that's okay too.
        if handler is None:
            return None
        return handler(self.form, self.action)
