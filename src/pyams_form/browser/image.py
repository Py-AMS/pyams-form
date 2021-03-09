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

"""PyAMS_form.browser.image module

This module provides form's image button widget.
"""

from zope.interface import implementer_only
from zope.schema.fieldproperty import FieldProperty

from pyams_form.browser.button import ButtonWidget
from pyams_form.browser.interfaces import IHTMLImageWidget
from pyams_form.interfaces.button import IImageButton
from pyams_form.interfaces.widget import IFieldWidget, IImageWidget
from pyams_form.util import to_unicode
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import NO_VALUE


__docformat__ = 'restructuredtext'


@implementer_only(IImageWidget)
class ImageWidget(ButtonWidget):
    """Form image button widget."""

    src = FieldProperty(IHTMLImageWidget['src'])

    klass = 'image-widget'
    css = 'image'

    def extract(self, default=NO_VALUE):
        """See pyams_form.interfaces.IWidget."""
        params = self.request.params
        if self.name + '.x' not in params:
            return default
        return {
            'x': int(params[self.name + '.x']),
            'y': int(params[self.name + '.y']),
            'value': params[self.name]
        }

    def json_data(self):
        data = super().json_data()
        data['type'] = 'image'
        data['src'] = self.src
        return data


@adapter_config(required=(IImageButton, IFormLayer), provides=IFieldWidget)
def ImageFieldWidget(field, request):  # pylint: disable=invalid-name
    """Form image button widget factory adapter"""
    image = FieldWidget(field, ImageWidget(request))
    image.value = field.title
    # Get the full resource URL for the image:
    image.src = to_unicode(field.image)
    return image
