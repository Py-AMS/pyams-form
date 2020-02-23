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

"""PyAMS_form.error module

This module provides snippets to display error messages.
"""

from zope.component import adapter
from zope.interface import Invalid, implementer
from zope.schema import ValidationError

from pyams_form.interfaces import IValue
from pyams_form.interfaces.error import IErrorViewSnippet, IMultipleErrors
from pyams_form.util import get_specification
from pyams_form.value import ComputedValueCreator, StaticValueCreator
from pyams_template.template import get_view_template
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'

from pyams_form import _  # pylint: disable=ungrouped-imports


# pylint: disable=invalid-name
ErrorViewMessage = StaticValueCreator(
    discriminators=('error', 'request', 'widget', 'field', 'form', 'content')
)

# pylint: disable=invalid-name
ComputedErrorViewMessage = ComputedValueCreator(
    discriminators=('error', 'request', 'widget', 'field', 'form', 'content')
)


def ErrorViewDiscriminators(error_view, error=None, request=None, widget=None,
                            field=None, form=None, content=None):
    # pylint: disable=invalid-name,too-many-arguments
    """Error view discriminators"""
    adapter(get_specification(error),
            get_specification(request),
            get_specification(widget),
            get_specification(field),
            get_specification(form),
            get_specification(content))(error_view)


@adapter_config(required=(ValidationError, None, None, None, None, None),
                provides=IErrorViewSnippet)
@implementer(IErrorViewSnippet)
class ErrorViewSnippet:  # pylint: disable=too-many-instance-attributes
    """Base error view snippet."""

    message = None

    def __init__(self, error, request, widget, field, form, content):
        # pylint: disable=too-many-arguments
        self.error = self.context = error
        self.request = request
        self.widget = widget
        self.field = field
        self.form = form
        self.content = content

    def create_message(self):
        """Get error message"""
        return self.error.doc()

    def update(self):
        """Update snippet content"""
        registry = self.request.registry
        value = registry.queryMultiAdapter((self.context, self.request, self.widget,
                                            self.field, self.form, self.content),
                                           IValue, name='message')
        if value is not None:
            self.message = value.get()
        else:
            self.message = self.create_message()

    render = get_view_template()

    def __repr__(self):
        return '<%s for %s>' % (self.__class__.__name__, self.error.__class__.__name__)


@adapter_config(required=(ValueError, None, None, None, None, None),
                provides=IErrorViewSnippet)
class ValueErrorViewSnippet(ErrorViewSnippet):
    """An error view for ValueError."""

    default_message = _('The system could not process the given value.')

    def create_message(self):
        return self.default_message


@adapter_config(required=(Invalid, None, None, None, None, None),
                provides=IErrorViewSnippet)
class InvalidErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet."""

    def create_message(self):
        return self.error.args[0]


@implementer(IMultipleErrors)
class MultipleErrors(Exception):
    """An error that contains many errors"""

    def __init__(self, errors):  # pylint: disable=super-init-not-called
        self.errors = errors


@adapter_config(required=(IMultipleErrors, None, None, None, None, None),
                provides=IErrorViewSnippet)
class MultipleErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet for multiple errors."""

    def update(self):
        """Snippet update"""

    def render(self):
        """Render multiple errors"""
        return ''.join([view.render() for view in self.error.errors])
