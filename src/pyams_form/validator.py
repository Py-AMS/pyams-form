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

"""PyAMS_form.validator module

Default validation adapters.
"""

import copy

from zope.component import adapter
from zope.interface import Interface, Invalid, alsoProvides, implementer
from zope.interface.interfaces import IInterface, IMethod
from zope.schema.interfaces import IBytes, IField

from pyams_form.interfaces import IData, IManagerValidator, IValidator, IValue
from pyams_form.interfaces.form import IContextAware
from pyams_form.interfaces.widget import IFileWidget
from pyams_form.util import changed_widget, get_specification
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import IDataManager, NOT_CHANGED, NO_VALUE
from pyams_utils.registry import get_current_registry


__docformat__ = 'restructuredtext'


@implementer(IValidator)
class StrictSimpleFieldValidator:
    """Strict simple field validator

    Validates all incoming values
    """

    def __init__(self, context, request, view, field, widget):
        # pylint: disable=too-many-arguments
        self.context = context
        self.request = request
        self.view = view
        self.field = field
        self.widget = widget

    def validate(self, value, force=False):  # pylint: disable=unused-argument
        """See interfaces.IValidator"""
        context = self.context
        field = self.field
        widget = self.widget
        if field.required and widget and widget.ignore_required_on_validation:
            # make the field not-required while checking
            field = copy.copy(field)
            field.required = False
        if context is not None:
            field = field.bind(context)
        registry = self.request.registry
        if value is NOT_CHANGED:
            if IContextAware.providedBy(widget) and not widget.ignore_context:
                # get value from context
                value = registry.getMultiAdapter((context, field), IDataManager).query()
            else:
                value = NO_VALUE
            if value is NO_VALUE:
                # look up default value
                value = field.default
                # pylint: disable=redefined-outer-name
                adapter = registry.queryMultiAdapter(
                    (context, self.request, self.view, field, widget),
                    IValue, name='default')
                if adapter:
                    value = adapter.get()
        return field.validate(value)

    def __repr__(self):
        return "<%s for %s['%s']>" % (
            self.__class__.__name__,
            self.field.interface.getName(),
            self.field.__name__)


@adapter_config(required=(Interface, Interface, Interface, IField, Interface),
                provides=IValidator)
class SimpleFieldValidator(StrictSimpleFieldValidator):
    """Simple Field Validator

    Ignores unchanged values.
    """

    def validate(self, value, force=False):
        """See interfaces.IValidator"""
        if value is self.field.missing_value:
            # let missing values run into stricter validation
            # most important case is not let required fields pass
            return super().validate(value, force)

        if not force:
            if value is NOT_CHANGED:
                # no need to validate unchanged values
                return None

            if self.widget and not changed_widget(
                    self.widget, value, field=self.field, context=self.context):
                # if new value == old value, no need to validate
                return None

        # otherwise StrictSimpleFieldValidator will do the job
        return super().validate(value, force)


@adapter_config(required=(Interface, Interface, Interface, IBytes, IFileWidget),
                provides=IValidator)
class FileUploadValidator(StrictSimpleFieldValidator):
    """File upload validator
    """
    # only FileUploadDataConverter seems to use NOT_CHANGED, but that needs
    # to be validated, because file upload is a special case
    # the most special case if when an ad-hoc IBytes field is required


def WidgetValidatorDiscriminators(validator, context=None, request=None, view=None,
                                  field=None, widget=None):
    # pylint: disable=invalid-name,too-many-arguments
    """Widget validator discriminators"""
    adapter(
        get_specification(context),
        get_specification(request),
        get_specification(view),
        get_specification(field),
        get_specification(widget)
    )(validator)


class NoInputData(Invalid):
    """There was no input data because:

    - It wasn't asked for

    - It wasn't entered by the user

    - It was entered by the user, but the value entered was invalid

    This exception is part of the internal implementation of checkInvariants.

    """


@implementer(IData)
class Data:
    """Form data proxy implementation"""

    def __init__(self, schema, data, context):
        self._Data_data___ = data  # pylint: disable=invalid-name
        self._Data_schema___ = schema  # pylint: disable=invalid-name
        alsoProvides(self, schema)
        self.__context__ = context

    def __getattr__(self, name):
        schema = self._Data_schema___
        data = self._Data_data___
        try:
            field = schema[name]
        except KeyError as err:
            raise AttributeError(name) from err
        # If the found field is a method, then raise an error.
        if IMethod.providedBy(field):
            raise RuntimeError("Data value is not a schema field", name)
        # Try to get the value for the field
        value = data.get(name, data)
        if value is data:
            if self.__context__ is None:
                raise NoInputData(name)
            registry = get_current_registry()
            dman = registry.getMultiAdapter((self.__context__, field), IDataManager)
            value = dman.get()
        # Optimization: Once we know we have a good value, set it as an
        # attribute for faster access.
        setattr(self, name, value)
        return value


@adapter_config(required=(Interface, Interface, Interface, IInterface, Interface),
                provides=IManagerValidator)
class InvariantsValidator:
    """Simple Field Validator"""

    def __init__(self, context, request, view, schema, manager):
        # pylint: disable=too-many-arguments
        self.context = context
        self.request = request
        self.view = view
        self.schema = schema
        self.manager = manager

    def validate(self, data):
        """See interfaces.IManagerValidator"""
        return self.validate_object(Data(self.schema, data, self.context))

    def validate_object(self, object):  # pylint: disable=redefined-builtin
        """validate given object"""
        errors = []
        try:
            self.schema.validateInvariants(object, errors)
        except Invalid:
            pass  # Just collect the errors

        return tuple([error for error in errors
                      if not isinstance(error, NoInputData)])

    def __repr__(self):
        return '<%s for %s>' %(self.__class__.__name__, self.schema.getName())


def WidgetsValidatorDiscriminators(validator, context=None, request=None, view=None,
                                   schema=None, manager=None):
    # pylint: disable=invalid-name,too-many-arguments
    """Widgets validator discriminators"""
    adapter(
        get_specification(context),
        get_specification(request),
        get_specification(view),
        get_specification(schema),
        get_specification(manager)
    )(validator)
