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

"""PyAMS_form.browser.file module

This module provides default file widget.
"""

from zope.interface import implementer_only
from zope.schema.interfaces import IBytes

from pyams_form.browser.text import TextWidget
from pyams_form.interfaces.widget import IFieldWidget, IFileWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@implementer_only(IFileWidget)
class FileWidget(TextWidget):
    """File input widget implementation"""

    klass = 'file-widget'
    css = 'file'

    # headers and filename attributes are set by ``IDataConverter`` to the widget
    # provided by the FileUpload object of the form
    headers = None
    filename = None

    def json_data(self):
        data = super().json_data()  # pylint: disable=bad-super-call
        data['type'] = 'file'
        return data


@adapter_config(required=(IBytes, IFormLayer),
                provides=IFieldWidget)
def FileFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for FileWidget."""
    return FieldWidget(field, FileWidget(request))
