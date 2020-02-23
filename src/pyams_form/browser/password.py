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

"""PyAMS_form.browser.password module

Password widget implementation.
"""

from zope.interface import implementer_only
from zope.schema.interfaces import IPassword

from pyams_form.browser.text import TextWidget
from pyams_form.interfaces.widget import IPasswordWidget, IFieldWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config

__docformat__ = 'restructuredtext'


@implementer_only(IPasswordWidget)
class PasswordWidget(TextWidget):
    """Input type password widget implementation."""

    klass = 'password-widget'
    css = 'password'


@adapter_config(required=(IPassword, IFormLayer), provides=IFieldWidget)
def PasswordFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for IPasswordWidget."""
    return FieldWidget(field, PasswordWidget(request))
