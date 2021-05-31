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

"""PyAMS_form.browser.textlines module

This module provides default textlines widget.
"""

from zope.interface import implementer, implementer_only

from pyams_form.browser.textarea import TextAreaWidget
from pyams_form.interfaces.widget import IFieldWidget, ITextLinesWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config
from pyams_utils.schema import ITextLineListField


__docformat__ = 'restructuredtext'


@implementer_only(ITextLinesWidget)
class TextLinesWidget(TextAreaWidget):
    """Input type sequence widget implementation."""


@adapter_config(required=(ITextLineListField, IFormLayer),
                provides=IFieldWidget)
def TextLinesFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for TextLinesWidget."""
    return FieldWidget(field, TextLinesWidget(request))


@implementer(IFieldWidget)
def TextLinesFieldWidgetFactory(field, value_type, request):
    # pylint: disable=invalid-name,unused-argument
    """IFieldWidget factory for TextLinesWidget."""
    return TextLinesFieldWidget(field, request)
