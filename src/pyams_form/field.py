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

"""PyAMS_form.field module

Form field definitions.
"""

from zope.interface import Interface, Invalid, alsoProvides, implementer
from zope.interface.interface import InterfaceClass
from zope.location import locate
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IField as ISchemaField

from pyams_form.error import MultipleErrors
from pyams_form.interfaces import DISPLAY_MODE, IDataConverter, IField, IFields, \
    IManagerValidator, INPUT_MODE, IValidator
from pyams_form.interfaces.error import IErrorViewSnippet
from pyams_form.interfaces.form import IContextAware, IFieldsForm, IFormAware
from pyams_form.interfaces.widget import IFieldWidget, IWidgets
from pyams_form.util import Manager, SelectionManager, expand_prefix
from pyams_form.widget import AfterWidgetUpdateEvent
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import IDataManager, NO_VALUE
from pyams_utils.registry import get_current_registry


__docformat__ = 'restructuredtext'


def _initkw(keep_readonly=(), omit_readonly=False, **defaults):
    """Init keywords"""
    return keep_readonly, omit_readonly, defaults


class WidgetFactories(dict):
    """Widget factories"""

    def __init__(self):
        super().__init__()
        self.default = None

    def __getitem__(self, key):
        if key not in self and self.default:
            return self.default
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key not in self and self.default:
            return self.default
        return super().get(key, default)


class WidgetFactoryProperty:
    """Widget factory property"""

    def __get__(self, inst, klass):
        if not hasattr(inst, '_widget_factories'):
            inst._widget_factories = WidgetFactories()
        return inst._widget_factories

    def __set__(self, inst, value):
        if not hasattr(inst, '_widget_factories'):
            inst._widget_factories = WidgetFactories()
        inst._widget_factories.default = value


@implementer(IField)
class Field:
    """Field implementation."""

    widget_factory = WidgetFactoryProperty()

    # pylint: disable=too-many-arguments
    def __init__(self, field, name=None, prefix='', mode=None, interface=None,
                 ignore_context=None, show_default=None):
        self.field = field
        if name is None:
            name = field.__name__
        assert name
        self.__name__ = expand_prefix(prefix) + name
        self.prefix = prefix
        self.mode = mode
        if interface is None:
            interface = field.interface
        self.interface = interface
        self.ignore_context = ignore_context
        self.show_default = show_default

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


@implementer(IFields)
class Fields(SelectionManager):
    """Field manager."""

    manager_interface = IFields

    def __init__(self, *args, **kw):  # pylint: disable=too-many-branches
        keep_readonly, omit_readonly, defaults = _initkw(**kw)

        fields = []
        for arg in args:
            if isinstance(arg, InterfaceClass):
                for name, field in getFieldsInOrder(arg):
                    fields.append((name, field, arg))

            elif ISchemaField.providedBy(arg):
                name = arg.__name__
                if not name:
                    raise ValueError("Field has no name")
                fields.append((name, arg, arg.interface))

            elif self.manager_interface.providedBy(arg):
                for form_field in arg.values():
                    fields.append(
                        (form_field.__name__, form_field, form_field.interface))

            elif isinstance(arg, Field):
                fields.append((arg.__name__, arg, arg.interface))

            else:
                raise TypeError("Unrecognized argument type", arg)

        super().__init__()
        for name, field, iface in fields:
            if isinstance(field, Field):
                form_field = field
            else:
                if field.readonly:
                    if omit_readonly and (name not in keep_readonly):
                        continue
                custom_defaults = defaults.copy()
                if iface is not None:
                    custom_defaults['interface'] = iface
                form_field = Field(field, **custom_defaults)
                name = form_field.__name__

            if name in self:
                raise ValueError("Duplicate name", name)

            self[name] = form_field

    def select(self, *names, **kwargs):  # pylint: disable=arguments-differ
        """See interfaces.IFields"""
        prefix = kwargs.pop('prefix', None)
        interface = kwargs.pop('interface', None)
        assert len(kwargs) == 0
        if prefix:
            names = [expand_prefix(prefix) + name for name in names]
        mapping = self
        if interface is not None:
            mapping = {field.field.__name__: field for field in self.values()
                       if field.field.interface is interface}
        return self.__class__(*[mapping[name] for name in names])

    def omit(self, *names, **kwargs):  # pylint: disable=arguments-differ
        """See interfaces.IFields"""
        prefix = kwargs.pop('prefix', None)
        interface = kwargs.pop('interface', None)
        assert len(kwargs) == 0
        if prefix:
            names = [expand_prefix(prefix) + name for name in names]
        return self.__class__(
            *[field for name, field in self.items()
              if not ((name in names and interface is None) or
                      (field.field.interface is interface and
                       field.field.__name__ in names))])


@adapter_config(required=(IFieldsForm, IFormLayer, Interface),
                provides=IWidgets)
class FieldWidgets(Manager):
    """Widget manager for IFieldWidget."""

    prefix = 'widgets.'
    mode = INPUT_MODE
    errors = ()
    has_required_fields = False
    ignore_context = False
    ignore_request = False
    ignore_readonly = False
    ignore_required_on_extract = False
    set_errors = True

    def __init__(self, form, request, content):
        super().__init__()
        self.form = form
        self.request = request
        self.content = content

    def validate(self, data):
        """Validate widgets fields"""
        fields = self.form.fields.values()

        # Step 1: Collect the data for the various schemas
        schema_data = {}
        for field in fields:
            schema = field.interface
            if schema is None:
                continue

            field_data = schema_data.setdefault(schema, {})
            if field.__name__ in data:
                field_data[field.field.__name__] = data[field.__name__]

        # Step 2: Validate the individual schemas and collect errors
        errors = ()
        content = self.content
        if self.ignore_context:
            content = None
        registry = self.request.registry
        for schema, field_data in schema_data.items():
            validator = registry.getMultiAdapter((content, self.request, self.form, schema, self),
                                                 IManagerValidator)
            errors += validator.validate(field_data)

        return errors

    def update(self):
        """See interfaces.widget.IWidgets"""
        # Create a unique prefix.
        prefix = expand_prefix(self.form.prefix) + expand_prefix(self.prefix)
        # Walk through each field, making a widget out of it.
        data = {}
        data.update(self)
        registry = self.request.registry
        for field in self.form.fields.values():
            # Step 0. Determine whether the context should be ignored.
            ignore_context = self.ignore_context
            if field.ignore_context is not None:
                ignore_context = field.ignore_context
            # Step 1: Determine the mode of the widget.
            mode = self.mode
            if field.mode is not None:
                mode = field.mode
            elif field.field.readonly and not self.ignore_readonly:
                mode = DISPLAY_MODE
            elif not ignore_context:
                # If we do not have enough permissions to write to the
                # attribute, then switch to display mode.
                dman = registry.getMultiAdapter((self.content, field.field), IDataManager)
                if not dman.can_write():
                    mode = DISPLAY_MODE
            # Step 2: Get the widget for the given field.
            short_name = field.__name__
            new_widget = True
            if short_name in self:
                # reuse existing widget
                widget = data[short_name]
                new_widget = False
            elif field.widget_factory.get(mode) is not None:
                factory = field.widget_factory.get(mode)
                widget = factory(field.field, self.request)
            else:
                widget = registry.getMultiAdapter((field.field, self.request), IFieldWidget)
            # Step 3: Set the prefix for the widget
            widget.name = prefix + short_name
            widget.id = (prefix + short_name).replace('.', '-')
            # Step 4: Set the context
            widget.context = self.content
            # Step 5: Set the form
            widget.form = self.form
            # Optimization: Set both interfaces here, rather in step 4 and 5:
            # ``alsoProvides`` is quite slow
            alsoProvides(widget, IContextAware, IFormAware)
            # Step 6: Set some variables
            widget.ignore_context = ignore_context
            widget.ignore_request = self.ignore_request
            if field.show_default is not None:
                widget.show_default = field.show_default
            # Step 7: Set the mode of the widget
            widget.mode = mode
            # Step 8: Update the widget
            widget.update()
            get_current_registry().notify(AfterWidgetUpdateEvent(widget))
            # Step 9: Add the widget to the manager
            if widget.required:
                self.has_required_fields = True
            if new_widget:
                data[short_name] = widget
                locate(widget, self, short_name)
        self.create_according_to_list(data, self.form.fields.keys())

    def _extract(self, return_raw=False):
        data = {}
        errors = ()
        registry = self.request.registry
        for name, widget in self.items():
            if widget.mode == DISPLAY_MODE:
                continue
            value = widget.field.missing_value
            try:
                widget.set_errors = self.set_errors
                raw = widget.extract()
                if raw is not NO_VALUE:
                    # pylint: disable=assignment-from-no-return
                    value = IDataConverter(widget).to_field_value(raw)
                widget.ignore_required_on_validation = self.ignore_required_on_extract
                registry.getMultiAdapter((self.content, self.request, self.form,
                                          getattr(widget, 'field', None), widget),
                                         IValidator).validate(value)
            except (Invalid, ValueError, MultipleErrors) as error:
                view = registry.getMultiAdapter((error, self.request, widget, widget.field,
                                                 self.form, self.content),
                                                IErrorViewSnippet)
                view.update()
                if self.set_errors:
                    widget.error = view
                errors += (view,)
            else:
                name = widget.__name__
                if return_raw:
                    data[name] = raw
                else:
                    data[name] = value
        for error in self.validate(data):
            view = registry.getMultiAdapter((error, self.request, None, None,
                                             self.form, self.content),
                                            IErrorViewSnippet)
            view.update()
            errors += (view,)
        if self.set_errors:
            self.errors = errors
        return data, errors

    def extract(self):
        """See interfaces.IWidgets"""
        return self._extract(return_raw=False)

    def extract_raw(self):
        """See interfaces.IWidgets"""
        return self._extract(return_raw=True)

    def copy(self):
        """See interfaces.ISelectionManager"""
        clone = self.__class__(self.form, self.request, self.content)
        super(self.__class__, clone).update(self)
        return clone
