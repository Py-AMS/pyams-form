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

"""PyAMS_form.interfaces.error module

This module defines error-related interfaces.
"""

from zope.interface import Attribute, Interface
from zope.schema import Field

from pyams_layer.interfaces import IFormLayer
from pyams_template.template import template_config


__docformat__ = 'restructuredtext'

from pyams_form import _


@template_config(layer=IFormLayer,
                 template='templates/error.pt')
class IErrorViewSnippet(Interface):
    """A view providing a view for an error"""

    widget = Field(title=_("Widget"),
                   description=_("The widget that the view is on"),
                   required=True)

    error = Field(title=_('Error'),
                  description=_('Error the view is for'),
                  required=True)

    def update(self):
        """Update view"""

    def render(self):
        """Render view"""


class IMultipleErrors(Interface):
    """An error that contains many status"""

    errors = Attribute("List of status")


class IAJAXErrorsRenderer(Interface):
    """AJAX error manager"""

    def render(self, errors):
        """Render error message in AJAX"""
