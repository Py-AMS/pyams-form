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

"""PyAMS_form.browser.text module

This module provides default text widget.
"""

from zope.interface import implementer_only
from zope.schema.interfaces import IASCIILine, IBytesLine, IDate, IDatetime, IDecimal, IFloat, \
    IId, IInt, ITextLine, ITime, ITimedelta, IURI

from pyams_form.browser.widget import HTMLTextInputWidget, add_field_class
from pyams_form.interfaces.widget import IFieldWidget, ITextWidget
from pyams_form.widget import FieldWidget, Widget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@implementer_only(ITextWidget)
class TextWidget(HTMLTextInputWidget, Widget):
    """Input type text widget implementation."""

    klass = 'text-widget'
    css = 'text'
    value = ''

    def update(self):
        super().update()
        add_field_class(self)


@adapter_config(required=(IBytesLine, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IASCIILine, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(ITextLine, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IId, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IInt, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IFloat, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IDecimal, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IDate, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IDatetime, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(ITime, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(ITimedelta, IFormLayer),
                provides=IFieldWidget)
@adapter_config(required=(IURI, IFormLayer),
                provides=IFieldWidget)
def TextFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for TextWidget."""
    return FieldWidget(field, TextWidget(request))
