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

"""PyAMS_form.browser.button module

This module provides base form button widget.
"""

from zope.interface import implementer_only

from pyams_form.browser.widget import HTMLInputWidget, add_field_class
from pyams_form.interfaces.button import IButton
from pyams_form.interfaces.widget import IButtonWidget, IFieldWidget
from pyams_form.widget import Widget, FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@implementer_only(IButtonWidget)
class ButtonWidget(HTMLInputWidget, Widget):
    """A simple button of a form."""

    klass = 'button-widget'
    css = 'button'

    def update(self):
        # We do not need to use the widget's update method, because it is
        # mostly about ectracting the value, which we do not need to do.
        add_field_class(self)


@adapter_config(required=(IButton, IFormLayer), provides=IFieldWidget)
def ButtonFieldWidget(field, request):  # pylint: disable=invalid-name
    """Simple form button widget factory adapter"""
    button = FieldWidget(field, ButtonWidget(request))
    button.value = field.title
    return button
