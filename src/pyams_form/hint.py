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

"""PyAMS_form.hint module

Field title hint adapter implementation.
"""

from zope.interface import Interface
from zope.schema.interfaces import IField

from pyams_form.interfaces import IValue
from pyams_form.interfaces.form import IForm
from pyams_form.interfaces.widget import IWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@adapter_config(name='title',
                required=(Interface, IFormLayer, IForm, IField, IWidget),
                provides=IValue)
class FieldDescriptionAsHint:
    """Schema field description as widget's ```Title`` IValue adapter"""

    def __init__(self, context, request, form, field, widget):
        # pylint: disable=too-many-arguments
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

    def get(self):
        """Return the value"""
        return self.field.description if self.field.description else None
