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

"""PyAMS_form.browser.object module

Object widget implementation.
"""

from zope.interface import implementer
from zope.schema.interfaces import IObject

from pyams_form.browser.widget import HTMLFormElement
from pyams_form.interfaces.widget import IFieldWidget, IObjectWidget
from pyams_form.object import ObjectWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@implementer(IObjectWidget)
class ObjectWidget(HTMLFormElement, ObjectWidget):
    """Object widget implementation"""

    klass = 'object-widget'
    css = 'object'


@adapter_config(required=(IObject, IFormLayer), provides=IFieldWidget)
def ObjectFieldWidget(field, request):
    """IFieldWidget factory for IObjectWidget."""
    return FieldWidget(field, ObjectWidget(request))
