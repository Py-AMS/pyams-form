#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_form.interfaces module

This module defines all package interfaces.
"""

from zope.interface import Interface
from zope.interface.common.mapping import IEnumerableMapping
from zope.schema import Bool, Field, TextLine


__docformat__ = 'reStructuredText'

from pyams_form import _


# Forms modes

INPUT_MODE = 'input'
DISPLAY_MODE = 'display'
HIDDEN_MODE = 'hidden'


#
# Generic manager interfaces
#

class IManager(IEnumerableMapping):
    """A manager of some kind of items.

    *Important*: While managers are mappings, the order of the items is
    assumed to be important! Effectively, a manager is an ordered mapping.

    In general, managers do not have to support a manipulation
    API. Oftentimes, managers are populated during initialization or while
    updating.
    """


class ISelectionManager(IManager):
    """Managers that support item selection and management.

    This manager allows one to more carefully specify the contained items.

    *Important*: The API is chosen in a way, that the manager is still
    immutable. All methods in this interface must return *new* instances of
    the manager.
    """

    def __add__(self, other):
        """Used for merge two managers."""

    def select(self, *names):
        """Return a modified instance with an ordered subset of items."""

    def omit(self, *names):
        """Return a modified instance omitting given items."""

    def copy(self):
        """Copy all items to a new instance and return it."""


#
# Forms validators
#

class IData(Interface):
    """A proxy object for form data.

    The object will make all keys within its data attribute available as
    attributes. The schema that is represented by the data will be directly
    provided by instances.
    """

    def __init__(self, schema, data, context):  # pylint: disable=super-init-not-called
        """The data proxy is instantiated using the schema it represents, the
        data fulfilling the schema and the context in which the data are
        validated.
        """

    __context__ = Field(title=_('Context'),
                        description=_('The context in which the data are validated'),
                        required=True)


class IValidator(Interface):
    """A validator for a particular value"""

    def validate(self, value, force=False):
        """Validate the value.

        If successful, return ``None``. Otherwise raise an ``Invalid`` error.
        """


class IManagerValidator(Interface):
    """A validator that validates a set of data."""

    def validate(self, data):
        """Validate a dictionary of data.

        This method is only responsible of validating relationships between
        the values in the data. It can be assumed that all values have been
        validated in isolation before.

        The return value of this method is a tuple of errors that occurred
        during the validation process.
        """

    def validate_object(self, obj):
        """Validate an object.

        The same semantics as in ``validate()`` apply, except that the values
        are retrieved from the object and not the data dictionary.
        """


#
# Forms fields
#

class IField(Interface):
    """Field wrapping a schema field used in the form."""

    __name__ = TextLine(title=_('Title'),
                        description=_('The name of the field within the form'),
                        required=True)

    field = Field(title=_('Schema Field'),
                  description=_('The schema field that is to be rendered'),
                  required=True)

    prefix = Field(title=_('Prefix'),
                   description=_('The prefix of the field used to avoid name clashes'),
                   required=True)

    mode = Field(title=_('Mode'),
                 description=_('The mode in which to render the widget for the field'),
                 required=True)

    interface = Field(title=_('Interface'),
                      description=_('The interface from which the field is coming'),
                      required=True)

    ignore_context = Bool(title=_('Ignore Context'),
                          description=_('A flag, when set, forces the widget not to look at '
                                        'the context for a value'),
                          required=False)

    widget_factory = Field(title=_('Widget Factory'),
                           description=_('The widget factory'),
                           required=False,
                           default=None,
                           missing_value=None)

    show_default = Bool(title=_('Show default value'),
                        description=_('A flag, when set, makes the widget to display '
                                      'field|adapter provided default values'),
                        default=True,
                        required=False)


class IFields(ISelectionManager):
    """IField manager."""

    def select(self, *names, prefix=None, interface=None):  # pylint: disable=arguments-differ
        """Return a modified instance with an ordered subset of items.

        This extension to the ``ISelectionManager`` allows for handling cases
        with name-conflicts better by separating field selection and prefix
        specification.
        """

    def omit(self, *names, prefix=None, interface=None):  # pylint: disable=arguments-differ
        """Return a modified instance omitting given items.

        This extension to the ``ISelectionManager`` allows for handling cases
        with name-conflicts better by separating field selection and prefix
        specification.
        """


class IContentProviders(IManager):
    """A content provider manager"""


#
# Forms data converters
#

class IDataConverter(Interface):
    """A data converter from field to widget values and vice versa"""

    def to_widget_value(self, value):
        """Convert the field value to a widget output value.

        If conversion fails or is not possible, a ``ValueError`` *must* be
        raised. However, this method should effectively never fail, because
        incoming value is well-defined.
        """

    def to_field_value(self, value):
        """Convert an input value to a field/system internal value.

        This methods *must* also validate the converted value against the
        field.

        If the conversion fails, a ``ValueError`` *must* be raised. If
        the validation fails, a ``ValidationError`` *must* be raised.
        """


#
# Widgets and fields values
#

class IValue(Interface):
    """A value"""

    def get(self):  # pylint: disable=arguments-differ
        """Returns the value."""


#
# Terms interfaces
#

class IVocabularyTerms(Interface):
    """Base vocabulary terms lookup interface

    We keep camelCase naming convention here to be able to use zope.schema vocabularies
    easilly!
    """

    def getTerm(self, value):  # pylint: disable=invalid-name
        """Return an ITitledTokenizedTerm object for the given value

        LookupError is raised if the value isn't in the source
        """

    def getValue(self, token):  # pylint: disable=invalid-name
        """Return a value for a given identifier token

        LookupError is raised if there isn't a value in the source.
        """


class ITerms(IVocabularyTerms):
    """A selection term"""

    context = Field()
    request = Field()
    form = Field()
    field = Field()
    widget = Field()

    def getTermByToken(self, token):  # pylint: disable=invalid-name
        """Return an ITokenizedTerm for the passed-in token.

        If `token` is not represented in the vocabulary, `LookupError`
        is raised.
        """

    def __iter__(self):
        """Iterate over terms."""

    def __len__(self, ):
        """Return number of terms."""

    def __contains__(self, value):
        """Check wether terms containes the ``value``."""


class IBoolTerms(ITerms):
    """A specialization that handles boolean choices."""

    true_label = TextLine(title=_('True-value Label'),
                          description=_('The label for a true value of the Bool field'),
                          required=True)

    false_label = TextLine(title=_('False-value Label'),
                           description=_('The label for a false value of the Bool field'),
                           required=False)


#
# Objects factories
#

class IObjectFactory(Interface):
    """Factory that will instantiate our objects for ObjectWidget.

    It could also pre-populate properties as it gets the values extracted
    from the form passed in ``value``.
    """

    def __call__(self, value):  # pylint: disable=signature-differs
        """Return a default object created to be populated.
        """


#
# Subform factories
#

class ISubformFactory(Interface):
    """Factory that will instantiate our subforms for ObjectWidget"""

    def __call__(self):  # pylint: disable=signature-differs
        """Return a default object created to be populated"""


#
# Widgets layout template
# This interface isn't into "widget" module to avoid cyclic dependencies...
#

class IWidgetLayoutTemplate(Interface):
    """Widget layout template marker used for render the widget layout.

    It is important that we don't inherit this template from IPageTemplate.
    otherwise we will get into trouble since we lookup an IPageTemplate
    in the widget/render method.
    """
