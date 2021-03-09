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

"""PyAMS_form.browser.submit module

This module provides form submit button widget.
"""

from zope.interface import implementer_only

from pyams_form.browser.button import ButtonWidget
from pyams_form.interfaces.button import IButton
from pyams_form.interfaces.widget import ISubmitWidget, IFieldWidget
from pyams_form.widget import FieldWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@implementer_only(ISubmitWidget)
class SubmitWidget(ButtonWidget):
    """Form submit button."""

    klass = 'submit-widget'
    css = 'submit'

    def json_data(self):
        data = super().json_data()
        data['type'] = 'submit'
        return data


@adapter_config(required=(IButton, IFormLayer), provides=IFieldWidget)
def SubmitFieldWidget(field, request):  # pylint: disable=invalid-name
    """Form submit button factory adapter"""
    submit = FieldWidget(field, SubmitWidget(request))
    submit.value = field.title
    return submit
