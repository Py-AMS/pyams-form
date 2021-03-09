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

"""PyAMS_form.object module

This module defines ObjectWidget related classes.
"""

from zope.interface import Interface, alsoProvides, implementer
from zope.lifecycleevent import Attributes, ObjectCreatedEvent, ObjectModifiedEvent
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IObject

from pyams_form.converter import BaseDataConverter
from pyams_form.error import MultipleErrors
from pyams_form.field import FieldWidgets, Fields
from pyams_form.interfaces import DISPLAY_MODE, IDataConverter, INPUT_MODE, IObjectFactory
from pyams_form.interfaces.form import IFormAware
from pyams_form.interfaces.widget import IFieldWidget, IObjectWidget, IWidget
from pyams_form.widget import Widget, apply_value_to_widget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config
from pyams_utils.factory import get_interface_name
from pyams_utils.interfaces.form import IDataManager, NO_VALUE
from pyams_utils.registry import get_current_registry


__docformat__ = 'restructuredtext'


class ObjectWidget_NO_VALUE:  # pylint: disable=invalid-name
    """No-value object widget placeholder"""
    def __repr__(self):
        return '<ObjectWidget_NO_VALUE>'


ObjectWidget_NO_VALUE = ObjectWidget_NO_VALUE()  # pylint: disable=invalid-name


class ObjectWidgetValue(dict):
    """Object widget value mapping"""
    original_value = ObjectWidget_NO_VALUE  # will store the original object


@adapter_config(required=(IObject, IObjectWidget),
                provides=IDataConverter)
class ObjectConverter(BaseDataConverter):
    """Data converter for IObjectWidget."""

    def to_widget_value(self, value):
        """Just dispatch it."""
        if value is self.field.missing_value:
            return NO_VALUE

        retval = ObjectWidgetValue()
        retval.original_value = value

        registry = self.widget.request.registry
        for name, field in getFieldsInOrder(self.field.schema):
            dman = registry.getMultiAdapter((value, field), IDataManager)
            subv = dman.query()

            if subv is NO_VALUE:
                # look up default value
                subv = field.default
                # XXX: too many discriminators
                # adapter = zope.component.queryMultiAdapter(
                #    (context, self.request, self.view, field, widget),
                #    interfaces.IValue, name='default')
                # if adapter:
                #    value = adapter.get()

            widget = registry.getMultiAdapter((field, self.widget.request),
                                              IFieldWidget)
            if IFormAware.providedBy(self.widget):
                # form property required by objectwidget
                widget.form = self.widget.form
                alsoProvides(widget, IFormAware)
            converter = registry.getMultiAdapter((field, widget), IDataConverter)
            retval[name] = converter.to_widget_value(subv)

        return retval

    def adapted_obj(self, obj):
        """Widget adapter object getter"""
        return self.field.schema(obj)

    def to_field_value(self, value):
        """field value is an Object type, that provides field.schema"""
        if value is NO_VALUE:
            return self.field.missing_value

        # try to get the original object, or if there's no chance an empty one
        obj = self.widget.get_object(value)
        obj = self.adapted_obj(obj)

        names = []
        registry = self.widget.request.registry
        for name, field in getFieldsInOrder(self.field.schema):
            if not field.readonly:
                try:
                    newval_raw = value[name]
                except KeyError:
                    continue

                widget = registry.getMultiAdapter((field, self.widget.request), IFieldWidget)
                converter = registry.getMultiAdapter((field, widget), IDataConverter)
                newval = converter.to_field_value(newval_raw)

                dman = registry.getMultiAdapter((obj, field), IDataManager)
                oldval = dman.query()
                if (oldval != newval) or IObject.providedBy(field):
                    dman.set(newval)
                    names.append(name)

        if names:
            registry.notify(ObjectModifiedEvent(obj, Attributes(self.field.schema, *names)))

        return obj


@implementer(IObjectWidget)
class ObjectWidget(Widget):
    """Object widget class"""

    _mode = INPUT_MODE
    _value = NO_VALUE
    _updating = False

    prefix = ''
    fields = None
    widgets = None

    def create_object(self, value):
        """Create widget object"""
        # keep value passed, maybe some subclasses want it
        # value here is the raw extracted from the widget's subform
        # in the form of a dict key:fieldname, value:fieldvalue
        name = get_interface_name(self.field.schema)
        registry = self.request.registry
        creator = registry.queryMultiAdapter((self.context, self.request, self.form, self),
                                             IObjectFactory, name=name)
        if creator:
            obj = creator(value)
        else:
            # raise RuntimeError, that won't be swallowed
            raise RuntimeError("No IObjectFactory adapter registered for %s" % name)
        return obj

    def get_object(self, value):
        """Get widget object"""
        if value.original_value is ObjectWidget_NO_VALUE:
            # if the original_value did not survive the roundtrip
            if self.ignore_context:
                obj = self.create_object(value)
            else:
                # try to get the original object from the context.field_name
                registry = self.request.registry
                dman = registry.getMultiAdapter((self.context, self.field), IDataManager)
                try:
                    obj = dman.get()
                except (KeyError, AttributeError):
                    obj = self.create_object(value)
        else:
            # reuse the object that we got in toWidgetValue
            obj = value.original_value

        if obj is None or obj == self.field.missing_value:
            # if still None, create one, otherwise following will burp
            obj = self.create_object(value)

        return obj

    @property
    def mode(self):
        """This sets the subwidgets modes."""
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Mode setter applies mode to all widgets"""
        self._mode = mode
        # ensure that we apply the new mode to the widgets
        if self.widgets:
            for widget in self.widgets.values():
                widget.mode = mode

    def setup_fields(self):
        """Setup subform fields"""
        self.fields = Fields(self.field.schema)

    def setup_widgets(self):
        """Setup subform widgets"""
        self.setup_fields()

        self.prefix = self.name
        self.widgets = FieldWidgets(self, self.request, None)
        self.widgets.mode = self.mode
        # very-very important! otherwise the update() tries to set
        # RAW values as field values
        self.widgets.ignore_context = True
        self.widgets.ignore_request = self.ignore_request
        self.widgets.update()

    def update_widgets(self, set_errors=True):  # pylint: disable=unused-argument
        """Update subform widgets"""
        if self.field is None:
            raise ValueError("%r .field is None, that's a blocking point" % self)

        self.setup_widgets()

        if self._value is NO_VALUE:
            # XXX: maybe readonly fields/widgets should be reset here to
            #      widget.mode = INPUT_MODE
            for name, widget in self.widgets.items():
                if widget.field.readonly:
                    widget.mode = INPUT_MODE
                    widget.update()
        else:
            rawvalue = None

            for name, widget in self.widgets.items():
                if widget.mode == DISPLAY_MODE:
                    if rawvalue is None:
                        # lazy evaluation
                        registry = self.request.registry
                        converter = registry.getMultiAdapter((self.field, self),
                                                             IDataConverter)
                        obj = self.get_object(self._value)
                        rawvalue = converter.to_widget_value(obj)

                    self.apply_value(widget, rawvalue[name])
                else:
                    try:
                        val = self._value[name]
                    except KeyError:
                        pass
                    else:
                        self.apply_value(widget, val)

    def apply_value(self, widget, value):
        """Validate and apply value to given widget.

        This method gets called on any ObjectWidget value change and is
        responsible for validating the given value and setup an error message.

        This is internal apply value and validation process is needed because
        nothing outside this widget does know something about our
        internal sub widgets.
        """
        apply_value_to_widget(self, widget, value)

    def update(self):
        """Update widget contents"""
        # very-very-nasty: skip raising exceptions in extract while we're updating
        self._updating = True
        try:
            super().update()
            # create the subwidgets and set their values
            self.update_widgets(set_errors=False)
        finally:
            self._updating = False

    @property
    def value(self):
        """Widget value getter"""
        # value (get) cannot raise an exception, then we return insane values
        try:
            self.set_errors = True
            return self.extract()
        except MultipleErrors:
            value = ObjectWidgetValue()
            if self._value is not NO_VALUE:
                # send back the original object
                value.original_value = self._value.original_value

            for name, widget in self.widgets.items():
                if widget.mode != DISPLAY_MODE:
                    value[name] = widget.value
            return value

    @value.setter
    def value(self, value):
        """Widget value setter"""
        # This invokes updateWidgets on any value change e.g. update/extract.
        if (not isinstance(value, ObjectWidgetValue)) and (value is not NO_VALUE):
            value = ObjectWidgetValue(value)
        self._value = value

        # create the subwidgets and set their values
        self.update_widgets()

    def extract_raw(self, set_errors=True):
        '''See interfaces.form.IForm'''
        self.widgets.set_errors = set_errors
        data, errors = self.widgets.extract_raw()
        value = ObjectWidgetValue()
        if self._value is not NO_VALUE:
            # send back the original object
            value.original_value = self._value.original_value
        value.update(data)
        return value, errors

    def extract(self, default=NO_VALUE):
        if self.name + '-empty-marker' in self.request.params:
            self.update_widgets(set_errors=False)

            # important: widget extract MUST return RAW values
            # just an extractData is WRONG here
            value, errors = self.extract_raw(set_errors=self.set_errors)

            if errors:
                # very-very-nasty: skip raising exceptions in extract
                # while we're updating -- that happens when the widget
                # is updated and update calls extract()
                if self._updating:
                    # don't rebind value, send back the original object
                    for name, widget in self.widgets.items():
                        if widget.mode != DISPLAY_MODE:
                            value[name] = widget.value
                    return value
                raise MultipleErrors(errors)
            return value
        return default


def make_dummy_object(iface):
    """make dummy objects providing a given interface to support
    discriminating on field.schema
    """

    if iface is not None:
        @implementer(iface)
        class DummyObject:
            """Dummy object creator"""
    else:
        @implementer(Interface)
        class DummyObject:
            """Dummy object creator"""

    dummy = DummyObject()
    return dummy


@adapter_config(required=(Interface, IFormLayer, Interface, IWidget),
                provides=IObjectFactory)
class FactoryAdapter:
    """Most basic-default object factory adapter"""

    factory = None

    def __init__(self, context, request, form, widget):
        self.context = context
        self.request = request
        self.form = form
        self.widget = widget

    def __call__(self, value):
        # value is the extracted data from the form
        obj = self.factory()  # pylint: disable=not-callable
        registry = self.request.registry
        registry.notify(ObjectCreatedEvent(obj))
        return obj


# XXX: Probably we should offer a register factory method which allows to
# use all discriminators e.g. context, request, form, widget as optional
# arguments...
def register_factory_adapter(for_, klass, registry=None):
    """register the basic object factory adapter for a given interface and class"""

    class temp(FactoryAdapter):  # pylint: disable=invalid-name
        """Factory adapter class"""
        factory = klass

    name = get_interface_name(for_)
    if registry is None:
        registry = get_current_registry()
    registry.registerAdapter(temp,
                             required=(None, IFormLayer, None, IObjectWidget),
                             provided=IObjectFactory,
                             name=name)
