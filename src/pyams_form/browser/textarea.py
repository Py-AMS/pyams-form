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

"""PyAMS_form.browser.textarea module

This module provides textarea widget.
"""

from zope.interface import implementer_only
from zope.schema.interfaces import IASCII, IText

from pyams_form.browser.widget import HTMLTextAreaWidget, add_field_class
from pyams_form.interfaces.widget import IFieldWidget, ITextAreaWidget
from pyams_form.widget import FieldWidget, Widget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@implementer_only(ITextAreaWidget)
class TextAreaWidget(HTMLTextAreaWidget, Widget):
    """Textarea widget implementation."""

    klass = 'textarea-widget'
    css = 'textarea'
    value = ''

    def update(self):
        super().update()
        add_field_class(self)

    def json_data(self):
        data = super().json_data()
        data['type'] = 'textarea'
        return data


@adapter_config(required=(IASCII, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IText, IFormLayer),
                provides=IFieldWidget)
def TextAreaFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, TextAreaWidget(request))
