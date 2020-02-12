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

"""PyAMS_form.browser.multi module

This module provides multi-widgets implementation.
"""

from operator import attrgetter

from zope.interface import implementer
from zope.schema.interfaces import IDict, IField, IList, ITuple

from pyams_form.browser.widget import HTMLFormElement
from pyams_form.button import Buttons, button_and_handler
from pyams_form.interfaces.button import IActions
from pyams_form.interfaces.form import IButtonForm, IHandlerForm
from pyams_form.interfaces.widget import IMultiWidget, IFieldWidget
from pyams_form.widget import MultiWidget, FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'

from pyams_form import _


@implementer(IButtonForm, IHandlerForm)
class FormMixin:
    """Form mixin class"""


@implementer(IMultiWidget)
class MultiWidget(HTMLFormElement, MultiWidget, FormMixin):
    """Multi widget implementation."""

    buttons = Buttons()

    prefix = 'widget'
    klass = 'multi-widget'
    css = 'multi'
    items = ()

    actions = None
    show_label = True  # show labels for item subwidgets or not

    # Internal attributes
    _adapter_value_attributes = MultiWidget._adapter_value_attributes + ('show_label',)

    def update(self):
        """See pyams_form.interfaces.widget.IWidget."""
        super(MultiWidget, self).update()
        self.update_actions()
        self.actions.execute()
        self.update_actions()  # Update again, as conditions may change

    def update_actions(self):
        self.update_allow_add_remove()
        if self.name is not None:
            self.prefix = self.name
        registry = self.request.registry
        self.actions = registry.getMultiAdapter((self, self.request, self), IActions)
        self.actions.update()

    @button_and_handler(_('Add'), name='add',
                        condition=attrgetter('allow_adding'))
    def handle_add(self, action):
        self.append_adding_widget()

    @button_and_handler(_('Remove selected'), name='remove',
                        condition=attrgetter('allow_removing'))
    def handle_remove(self, action):
        self.remove_widgets([widget.name for widget in self.widgets
                             if '{}.remove'.format(widget.name) in self.request.params])


@adapter_config(required=(IDict, IFormLayer),
                provided=IFieldWidget)
def MultiFieldWidgetFactory(field, request):
    """IFieldWidget factory for MultiWidget."""
    return FieldWidget(field, MultiWidget(request))


@adapter_config(required=(IDict, IField, IFormLayer),
                provided=IFieldWidget)
@adapter_config(required=(IList, IField, IFormLayer),
                provided=IFieldWidget)
@adapter_config(required=(ITuple, IField, IFormLayer),
                provided=IFieldWidget)
def MultiFieldWidget(field, value_type, request):
    """IFieldWidget factory for MultiWidget."""
    return MultiFieldWidgetFactory(field, request)
