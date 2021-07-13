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

"""PyAMS_form.widget module

Base widget implementation.
"""

from pyramid_chameleon.interfaces import IChameleonTranslate
from zope.interface import Invalid, alsoProvides, implementer, implementer_only
from zope.location import Location
from zope.schema import ValidationError
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import IMinMaxLen, ITitledTokenizedTerm

from pyams_form.interfaces import IDataConverter, INPUT_MODE, ITerms, \
    IValidator, IValue, IWidgetLayoutTemplate
from pyams_form.interfaces.error import IErrorViewSnippet
from pyams_form.interfaces.form import IContextAware, IFormAware
from pyams_form.interfaces.widget import IAfterWidgetUpdateEvent, IFieldWidget, IMultiWidget, \
    ISequenceWidget, IWidget, IWidgetEvent
from pyams_form.template import get_widget_layout, get_widget_template
from pyams_form.util import sorted_none
from pyams_form.value import ComputedValueCreator, StaticValueCreator
from pyams_utils.interfaces.form import IDataManager, NO_VALUE
from pyams_utils.registry import query_utility


__docformat__ = 'restructuredtext'


PLACEHOLDER = object()

# pylint: disable=invalid-name
StaticWidgetAttribute = StaticValueCreator(
    discriminators=('context', 'request', 'view', 'field', 'widget')
)

# pylint: disable=invalid-name
ComputedWidgetAttribute = ComputedValueCreator(
    discriminators=('context', 'request', 'view', 'field', 'widget')
)


def apply_value_to_widget(parent, widget, value):
    """Apply given value to widget"""
    if value is not NO_VALUE:
        request = parent.request
        registry = request.registry
        try:
            # convert widget value to field value
            converter = IDataConverter(widget)
            # pylint: disable=assignment-from-no-return
            fvalue = converter.to_field_value(value)
            # validate field value
            registry.getMultiAdapter((parent.context, request, parent.form,
                                      getattr(widget, 'field', None), widget),
                                     IValidator).validate(fvalue)
            # convert field value back to widget value
            # that will probably format the value too
            # pylint: disable=assignment-from-no-return
            widget.value = converter.to_widget_value(fvalue)
        except (ValidationError, ValueError) as error:
            # on exception, setup the widget error message
            view = registry.getMultiAdapter((error, request, widget,
                                             widget.field, parent.form, parent.context),
                                            IErrorViewSnippet)
            view.update()
            widget.error = view
            # set the wrong value as value despite it's wrong
            # we want to re-show wrong values
            widget.value = value


@implementer(IWidget)
class Widget(Location):
    """Widget base class."""

    # widget specific attributes
    name = FieldProperty(IWidget['name'])
    label = FieldProperty(IWidget['label'])
    mode = FieldProperty(IWidget['mode'])
    required = FieldProperty(IWidget['required'])
    error = FieldProperty(IWidget['error'])
    value = FieldProperty(IWidget['value'])

    ignore_request = FieldProperty(IWidget['ignore_request'])
    ignore_required_on_validation = FieldProperty(IWidget['ignore_required_on_validation'])
    set_errors = FieldProperty(IWidget['set_errors'])
    show_default = FieldProperty(IWidget['show_default'])

    # rendering attributes
    layout = get_widget_layout()
    template = get_widget_template()

    # The following attributes are for convenience. They are declared in
    # extensions to the simple widget.

    # See ``interfaces.IContextAware``
    context = None
    ignore_context = False
    # See ``interfaces.IFormAware``
    form = None
    # See ``interfaces.IFieldWidget``
    field = None

    # Internal attributes
    _adapter_value_attributes = ('label', 'name', 'required', 'title')

    def __init__(self, request):
        self.request = request

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Step 1: Determine the value.
        value = NO_VALUE
        look_for_default = False
        registry = self.request.registry
        # Step 1.1: If possible, get a value from the request
        if not self.ignore_request:
            # at this turn we do not need errors to be set on widgets
            # errors will be set when extract gets called from form.extractData
            self.set_errors = False
            widget_value = self.extract()
            if widget_value is not NO_VALUE:
                # Once we found the value in the request, it takes precendence
                # over everything and nothing else has to be done.
                self.value = widget_value
                value = PLACEHOLDER
        # Step 1.2: If we have a widget with a field and we have no value yet,
        #           we have some more possible locations to get the value
        if (IFieldWidget.providedBy(self) and
                value is NO_VALUE and
                value is not PLACEHOLDER):
            # Step 1.2.1: If the widget knows about its context and the
            #             context is to be used to extract a value, get
            #             it now via a data manager.
            if IContextAware.providedBy(self) and not self.ignore_context:
                value = registry.getMultiAdapter((self.context, self.field), IDataManager).query()
            # Step 1.2.2: If we still do not have a value, we can always use
            #             the default value of the field, if set
            # NOTE: It should check field.default is not missing_value, but
            # that requires fixing zope.schema first
            # We get a clone of the field with the context binded
            field = self.field.bind(self.context)

            if value is field.missing_value or value is NO_VALUE:
                default_value = field.default
                if default_value is not None and self.show_default:
                    value = field.default
                    look_for_default = True

        # Step 1.3: If we still have not found a value, then we try to get it
        #           from an attribute value
        if (value is NO_VALUE or look_for_default) and self.show_default:
            adapter = registry.queryMultiAdapter((self.context, self.request, self.form,
                                                  self.field, self),
                                                 IValue, name='default')
            if adapter:
                value = adapter.get()
        # Step 1.4: Convert the value to one that the widget can understand
        if value not in (NO_VALUE, PLACEHOLDER):
            converter = IDataConverter(self)
            # pylint: disable=assignment-from-no-return
            self.value = converter.to_widget_value(value)
        # Step 2: Update selected attributes
        for attr_name in self._adapter_value_attributes:
            # only allow to set values for known attributes
            if hasattr(self, attr_name):
                value = registry.queryMultiAdapter((self.context, self.request, self.form,
                                                    self.field, self),
                                                   IValue, name=attr_name)
                if value is not None:
                    setattr(self, attr_name, value.get())

    def extract(self, default=NO_VALUE):
        """See z3c.form.interfaces.IWidget."""
        return self.request.params.get(self.name, default)

    render = get_widget_template()

    def json_data(self):
        """Get widget data in JSON format"""
        return {
            'mode': self.mode,
            'error': self.error.message if self.error else '',
            'value': self.value,
            'required': self.required,
            'name': self.name,
            'id': getattr(self, 'id', ''),
            'type': 'text',
            'label': self.label or ''
        }

    def __call__(self, **kwargs):
        """Get and return layout template which is calling widget/render"""
        layout = self.layout
        if layout is None:
            registry = self.request.registry
            layout = registry.getMultiAdapter((self.context, self.request, self.form,
                                               self.field, self),
                                              IWidgetLayoutTemplate, name=self.mode)
        cdict = {
            'context': self.context,
            'request': self.request,
            'view': self,
            'translate': query_utility(IChameleonTranslate)
        }
        cdict.update(kwargs)
        return layout(**cdict)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


@implementer(ISequenceWidget)
class SequenceWidget(Widget):
    """Term based sequence widget base.

    The sequence widget is used for select items from a sequence. Don't get
    confused, this widget does support to choose one or more values from a
    sequence. The word sequence is not used for the schema field, it's used
    for the values where this widget can choose from.

    This widget base class is used for build single or sequence values based
    on a sequence which is in most use case a collection. e.g.
    IList of IChoice for sequence values or IChoice for single values.

    See also the MultiWidget for build sequence values based on none collection
    based values. e.g. IList of ITextLine
    """

    value = ()
    terms = None
    separator = ','

    no_value_token = '--NOVALUE--'

    @property
    def display_value(self):
        """Widget display value"""
        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.no_value_token:
                continue
            try:
                term = self.terms.getTermByToken(token)
            except LookupError:
                # silently ignore missing tokens, because INPUT_MODE and
                # HIDDEN_MODE does that too
                continue
            if ITitledTokenizedTerm.providedBy(term):
                translate = self.request.localizer.translate
                value.append(translate(term.title))
            else:
                value.append(term.value)
        return value

    def update_terms(self):
        """Get terms from widget context"""
        if self.terms is None:
            registry = self.request.registry
            self.terms = registry.getMultiAdapter((self.context, self.request, self.form,
                                                   self.field, self),
                                                  ITerms)
        return self.terms

    def update(self):
        """See pyams_form.interfaces.widget.IWidget."""
        # Create terms first, since we need them for the generic update.
        self.update_terms()
        super().update()

    def extract(self, default=NO_VALUE):
        """See pyams_form.interfaces.widget.IWidget."""
        params = self.request.params
        if (self.name not in params and self.name + '-empty-marker' in params):
            return ()
        try:
            value = params.getall(self.name) or default
        except AttributeError:
            value = params.get(self.name, default)
        if value != default:
            values = []
            if not isinstance(value, (tuple, list)):
                # this is here to make any single value a tuple
                value = (value,)
            for val in value:
                values.extend(val.split(self.separator))
            value = tuple(values)
            # do some kind of validation, at least only use existing values
            for token in value:
                if token == self.no_value_token:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    return default
        return value

    def json_data(self):
        data = super().json_data()
        data['type'] = 'sequence'
        return data


@implementer(IMultiWidget)
class MultiWidget(Widget):
    # pylint: disable=too-many-instance-attributes
    """None Term based sequence widget base.

    The multi widget is used for ITuple, IList or IDict if no other widget is
    defined.

    Some IList, ITuple or IDict are using another specialized widget if they can
    choose from a collection. e.g. a IList of IChoice. The base class of such
    widget is the ISequenceWidget.

    This widget can handle none collection based sequences and offers add or
    remove values to or from the sequence. Each sequence value get rendered by
    it's own relevant widget. e.g. IList of ITextLine or ITuple of IInt

    Each widget get rendered within a sequence value. This means each internal
    widget will represent one value from the multi widget value. Based on the
    nature of this (sub) widget setup the internal widget do not have a real
    context and can't get bound to it. This makes it impossible to use a
    sequence of collection where the collection needs a context. But that
    should not be a problem since sequence of collection will use the
    SequenceWidget as base.
    """

    allow_adding = True
    allow_removing = True

    widgets = None
    key_widgets = None
    _value = None
    _widgets_updated = False

    _mode = FieldProperty(IWidget['mode'])

    def __init__(self, request):
        super().__init__(request)
        self.widgets = []
        self.key_widgets = []
        self._value = []

    @property
    def is_dict(self):
        """Check field key type"""
        return getattr(self.field, 'key_type', None) is not None

    @property
    def counter_name(self):
        """Counter name getter"""
        return '%s.count' % self.name

    @property
    def counter_marker(self):
        """Counter HTML marker getter"""
        # this get called in render from the template and contains always the
        # right amount of widgets we use.
        return '<input type="hidden" name="%s" value="%d" />' % (
            self.counter_name, len(self.widgets))

    @property
    def mode(self):
        """This gets the subwidgets mode."""
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Subwidgets mode setter"""
        self._mode = mode
        # ensure that we apply the new mode to the widgets
        for w in self.widgets:
            w.mode = mode
        for w in self.key_widgets:
            if w is not None:
                w.mode = mode

    def get_widget(self, idx, prefix=None, type_field="value_type"):
        """Setup widget based on index id with or without value."""
        value_type = getattr(self.field, type_field)
        registry = self.request.registry
        widget = registry.getMultiAdapter((value_type, self.request), IFieldWidget)
        self.set_name(widget, idx, prefix)
        widget.mode = self.mode
        # set widget.form (objectwidget needs this)
        if IFormAware.providedBy(self):
            widget.form = self.form
            alsoProvides(widget, IFormAware)
        widget.update()
        return widget

    def set_name(self, widget, idx, prefix=None):
        """Set widget name based on index position"""
        names = lambda id: [str(n) for n in [id] + [prefix, idx] if n is not None]
        widget.name = '.'.join([str(self.name)] + names(None))
        widget.id = '-'.join([str(self.id)] + names(None))  # pylint: disable=no-member

    def append_adding_widget(self):
        """Simply append a new empty widget with correct (counter) name."""
        # since we start with idx 0 (zero) we can use the len as next idx
        idx = len(self.widgets)
        widget = self.get_widget(idx)
        self.widgets.append(widget)
        if self.is_dict:
            widget = self.get_widget(idx, "key", "key_type")
            self.key_widgets.append(widget)
        else:
            self.key_widgets.append(None)

    def remove_widgets(self, names):
        """
        :param names: list of widget.name to remove from the value
        :return: None
        """
        zipped = list(zip(self.key_widgets, self.widgets))
        self.key_widgets = [k for k, v in zipped if v.name not in names]
        self.widgets = [v for k, v in zipped if v.name not in names]
        if self.is_dict:
            self.value = [(k.value, v.value)
                          for k, v in zip(self.key_widgets, self.widgets)]
        else:
            self.value = [widget.value for widget in self.widgets]

    def apply_value(self, widget, value=NO_VALUE):
        """Validate and apply value to given widget.

        This method gets called on any multi widget value change and is
        responsible for validating the given value and setup an error message.

        This is internal apply value and validation process is needed because
        nothing outside this multi widget does know something about our
        internal sub widgets.
        """
        apply_value_to_widget(self, widget, value)

    def update_widgets(self):  # pylint: disable=too-many-branches
        """Setup internal widgets based on the value_type for each value item.
        """
        old_len = len(self.widgets)
        # Ensure at least min_length widgets are shown
        if (IMinMaxLen.providedBy(self.field) and
                self.mode == INPUT_MODE and self.allow_adding and
                old_len < self.field.min_length):
            old_len = self.field.min_length
        self.widgets = []
        self.key_widgets = []
        keys = set()
        idx = 0
        if self.value:
            if self.is_dict:
                # mainly sorting for testing reasons
                # and dict's have no order!, but
                # XXX: this should be done in the converter... here we get
                #      always strings as keys, sorting an str(int/date) is lame
                #      also, newly added item should be the last...
                try:
                    items = sorted_none(self.value)
                except:  # pylint: disable=bare-except
                    # just in case it's impossible to sort don't fail
                    items = self.value
            else:
                items = zip([None] * len(self.value), self.value)
            for key, v in items:
                widget = self.get_widget(idx)
                self.apply_value(widget, v)
                self.widgets.append(widget)

                if self.is_dict:
                    # This is needed, since sequence widgets (such as for
                    # choices) return lists of values.
                    hash_key = key if not isinstance(key, list) else tuple(key)
                    widget = self.get_widget(idx, "key", "key_type")
                    self.apply_value(widget, key)
                    if hash_key in keys and widget.error is None:
                        error = Invalid('Duplicate key')
                        registry = self.request.registry
                        view = registry.getMultiAdapter((error, self.request, widget,
                                                         widget.field, self.form, self.context),
                                                        IErrorViewSnippet)
                        view.update()
                        widget.error = view
                    self.key_widgets.append(widget)
                    keys.add(hash_key)
                else:
                    # makes the template easier to have this the same length
                    self.key_widgets.append(None)
                idx += 1
        missing = old_len - len(self.widgets)
        if missing > 0:
            # add previous existing new added widgtes
            for _i in range(missing):
                widget = self.get_widget(idx)
                self.widgets.append(widget)
                if self.is_dict:
                    widget = self.get_widget(idx, "key", "key_type")
                    self.key_widgets.append(widget)
                else:
                    self.key_widgets.append(None)
                idx += 1
        self._widgets_updated = True

    def update_allow_add_remove(self):
        """Update the allow_adding/allow_removing attributes
        basing on field constraints and current number of widgets
        """
        if not IMinMaxLen.providedBy(self.field):
            return
        max_length = self.field.max_length
        min_length = self.field.min_length
        num_items = len(self.widgets)
        self.allow_adding = bool((not max_length) or (num_items < max_length))
        self.allow_removing = bool(num_items and (num_items > min_length))

    @property
    def value(self):
        """This invokes updateWidgets on any value change e.g. update/extract."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        # ensure that we apply our new values to the widgets
        self.update_widgets()

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        # Ensure that updateWidgets is called.
        super().update()
        if not self._widgets_updated:
            self.update_widgets()

    def extract(self, default=NO_VALUE):
        # This method is responsible to get the widgets value based on the
        # request and nothing else.
        # We have to setup the widgets for extract their values, because we
        # don't know how to do this for every field without the right widgets.
        # Later we will setup the widgets based on this values. This is needed
        # because we probably set a new value in the form for our multi widget
        # which would generate a different set of widgets.
        params = self.request.params
        if params.get(self.counter_name) is None:
            # counter marker not found
            return NO_VALUE
        counter = int(params.get(self.counter_name, 0))
        # extract value for existing widgets
        values = []
        append = values.append
        # extract value for existing widgets
        for idx in range(counter):
            widget = self.get_widget(idx)
            if self.is_dict:
                key_widget = self.get_widget(idx, "key", "key_type")
                append((key_widget.value, widget.value))
            else:
                append(widget.value)
        return values

    def json_data(self):
        data = super().json_data()
        data['widgets'] = [widget.json_data() for widget in self.widgets]
        data['type'] = 'multi'
        return data


def FieldWidget(field, widget):  # pylint: disable=invalid-name
    """Set the field for the widget."""
    widget.field = field
    if not IFieldWidget.providedBy(widget):
        alsoProvides(widget, IFieldWidget)
    # Initial values are set. They can be overridden while updating the widget
    # itself later on.
    widget.name = field.__name__
    widget.id = field.__name__.replace('.', '-')
    widget.label = field.title
    widget.required = field.required
    return widget


@implementer(IWidgetEvent)
class WidgetEvent:
    """Base widget event"""

    def __init__(self, widget):
        self.widget = widget

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.widget)


@implementer_only(IAfterWidgetUpdateEvent)
class AfterWidgetUpdateEvent(WidgetEvent):
    """Widget after update event"""


class WidgetSelector:
    """Widget event selector

    This predicate can be used by subscribers to filter widgets events.
    """

    def __init__(self, ifaces, config):  # pylint: disable=unused-argument
        if not isinstance(ifaces, (list, tuple)):
            ifaces = (ifaces,)
        self.interfaces = ifaces

    def text(self):
        """Widget's selector text"""
        return 'widget_selector = %s' % str(self.interfaces)

    phash = text

    def __call__(self, event):
        for intf in self.interfaces:
            try:
                if intf.providedBy(event.widget):
                    return True
            except (AttributeError, TypeError):
                if isinstance(event.widget, intf):
                    return True
        return False
