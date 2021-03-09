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

"""PyAMS_form.converter module

This module provides all default schema fields converters.
"""

import datetime
import decimal
from cgi import FieldStorage

import six
from zope.i18n.format import DateTimeParseError, NumberParseError
from zope.interface import alsoProvides, implementer
try:
    from zope.publisher.browser import FileUpload
except ImportError:
    FileUpload = None
from zope.schema import ValidationError
from zope.schema.interfaces import IBool, IBytes, ICollection, IDate, IDatetime, IDecimal, IDict, \
    IField, IFloat, IFromUnicode, IInt, ISequence, ITime, ITimedelta

from pyams_form.interfaces import IDataConverter
from pyams_form.interfaces.form import IFormAware
from pyams_form.interfaces.widget import IFieldWidget, IMultiWidget, ISequenceWidget, \
    ISingleCheckBoxWidget, ITextLinesWidget, IWidget, IFileWidget
from pyams_form.util import to_bytes, to_unicode
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import NOT_CHANGED


__docformat__ = 'restructuredtext'

from pyams_form import _  # pylint: disable=ungrouped-imports


@implementer(IDataConverter)
class BaseDataConverter:
    """A base implementation of the data converter."""

    _strip_value = True  # Remove spaces at start and end of text line

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def _get_converter(self, field):
        # We rely on the default registered widget, this is probably a
        # restriction for custom widgets. If so use your own MultiWidget and
        # register your own converter which will get the right widget for the
        # used value_type.
        registry = self.widget.request.registry
        widget = registry.getMultiAdapter((field, self.widget.request),
                                          IFieldWidget)
        if IFormAware.providedBy(self.widget):
            # form property required by object widget
            widget.form = self.widget.form
            alsoProvides(widget, IFormAware)
        converter = registry.getMultiAdapter((field, widget), IDataConverter)
        return converter

    def to_widget_value(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return ''
        return to_unicode(value)

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        if self._strip_value and isinstance(value, six.string_types):
            value = value.strip()

        if value == '':
            return self.field.missing_value

        # this is going to burp with `Object is of wrong type.`
        # if a non-unicode value comes in from the request
        return self.field.fromUnicode(value)

    def __repr__(self):
        return '<%s converts from %s to %s>' % (
            self.__class__.__name__,
            self.field.__class__.__name__,
            self.widget.__class__.__name__)


@adapter_config(required=(IField, IWidget), provides=IDataConverter)
class FieldDataConverter(BaseDataConverter):
    """A data converter using the field's ``fromUnicode()`` method."""

    def __init__(self, field, widget):
        super().__init__(field, widget)
        if not IFromUnicode.providedBy(field):
            field_name = ''
            if field.__name__:
                field_name = '``%s`` ' % field.__name__
            raise TypeError('Field %s of type ``%s`` must provide ``IFromUnicode``.' %
                            (field_name, type(field).__name__))


@adapter_config(required=IFieldWidget, provides=IDataConverter)
def FieldWidgetDataConverter(widget):  # pylint: disable=invalid-name
    """Provide a data converter based on a field widget."""
    return widget.request.registry.queryMultiAdapter((widget.field, widget), IDataConverter)


class FormatterValidationError(ValidationError):
    """Formatter validation error"""

    message = None

    def __init__(self, message, value):
        ValidationError.__init__(self, message, value)
        self.message = message

    def doc(self):
        return self.message


class NumberDataConverter(BaseDataConverter):
    """A general data converter for numbers."""

    type = None
    error_message = None

    def __init__(self, field, widget):
        super().__init__(field, widget)
        locale = self.widget.request.locale
        self.formatter = locale.numbers.getFormatter('decimal')
        self.formatter.type = self.type

    def to_widget_value(self, value):
        """See interfaces.IDataConverter"""
        if value == self.field.missing_value:
            return ''
        return self.formatter.format(value)

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        if value == '':
            return self.field.missing_value
        try:
            return self.formatter.parse(value)
        except NumberParseError as exc:
            raise FormatterValidationError(self.error_message, value) from exc


@adapter_config(required=(IInt, IWidget), provides=IDataConverter)
class IntegerDataConverter(NumberDataConverter):
    """A data converter for integers."""

    type = int
    error_message = _('The entered value is not a valid integer literal.')


@adapter_config(required=(IFloat, IWidget), provides=IDataConverter)
class FloatDataConverter(NumberDataConverter):
    """A data converter for integers."""

    type = float
    error_message = _('The entered value is not a valid decimal literal.')


@adapter_config(required=(IDecimal, IWidget), provides=IDataConverter)
class DecimalDataConverter(NumberDataConverter):
    """A data converter for integers."""

    type = decimal.Decimal
    error_message = _('The entered value is not a valid decimal literal.')


class CalendarDataConverter(BaseDataConverter):
    """A special data converter for calendar-related values."""

    type = None
    length = 'short'

    def __init__(self, field, widget):
        super().__init__(field, widget)
        locale = self.widget.request.locale
        self.formatter = locale.dates.getFormatter(self.type, self.length)

    def to_widget_value(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return ''
        return self.formatter.format(value)

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        if value == '':
            return self.field.missing_value
        try:
            return self.formatter.parse(value)
        except DateTimeParseError as err:
            raise FormatterValidationError(err.args[0], value) from err


@adapter_config(required=(IDate, IWidget), provides=IDataConverter)
class DateDataConverter(CalendarDataConverter):
    """A special data converter for dates."""

    type = 'date'


@adapter_config(required=(ITime, IWidget), provides=IDataConverter)
class TimeDataConverter(CalendarDataConverter):
    """A special data converter for times."""

    type = 'time'


@adapter_config(required=(IDatetime, IWidget), provides=IDataConverter)
class DatetimeDataConverter(CalendarDataConverter):
    """A special data converter for datetimes."""

    type = 'dateTime'


@adapter_config(required=(ITimedelta, IWidget), provides=IDataConverter)
class TimedeltaDataConverter(FieldDataConverter):
    """A special data converter for timedeltas."""

    def __init__(self, field, widget):
        # pylint: disable=super-init-not-called
        self.field = field
        self.widget = widget

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        if value == '':
            return self.field.missing_value
        try:
            days_string, crap, time_string = value.split(' ')  # pylint: disable=unused-variable
        except ValueError:
            time_string = value
            days = 0
        else:
            days = int(days_string)
        seconds = [int(part) * 60 ** (2 - n)
                   for n, part in enumerate(time_string.split(':'))]
        return datetime.timedelta(days, sum(seconds))


@adapter_config(required=(IBytes, IFileWidget), provides=IDataConverter)
class FileUploadDataConverter(BaseDataConverter):
    """A special data converter for bytes, supporting also FileUpload.

    Since IBytes represents a file upload too, this converter can handle
    zope.publisher.browser.FileUpload object as given value.
    """

    def to_widget_value(self, value):
        """See interfaces.IDataConverter"""
        return None

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        if value is None or value == '':
            # When no new file is uploaded, send a signal that we do not want
            # to do anything special.
            return NOT_CHANGED

        # By default a IBytes field is used for get a file upload widget.
        # But interfaces extending IBytes do not use file upload widgets.
        # Any way if we get a FieldStorage of FileUpload object, we'll
        # convert it.
        # We also store the additional FieldStorage/FileUpload values on the widget
        # before we loose them.
        if isinstance(value, (FieldStorage, FileUpload)):
            self.widget.headers = value.headers
            self.widget.filename = value.filename
            try:
                if isinstance(value, FieldStorage):
                    if value.fp is None:
                        seek = value.file.seek
                        read = value.file.read
                    else:
                        seek = value.fp.seek
                        read = value.fp.read
                else:
                    seek = value.seek
                    read = value.read
            except AttributeError as e:  # pylint: disable=invalid-name
                raise ValueError(_('Bytes data are not a file object')) from e
            else:
                seek(0)
                data = read()
                if data or getattr(value, 'filename', ''):
                    return data
                return self.field.missing_value
        else:
            return to_bytes(value)


@adapter_config(required=(IField, ISequenceWidget), provides=IDataConverter)
class SequenceDataConverter(BaseDataConverter):
    """Basic data converter for ISequenceWidget."""

    def to_widget_value(self, value):
        """Convert from Python bool to HTML representation."""
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return []
        # Look up the term in the terms
        terms = self.widget.update_terms()
        try:
            return [terms.getTerm(value).token]
        except LookupError:
            # Swallow lookup errors, in case the options changed.
            return []

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if (len(value) == 0) or (value[0] == widget.no_value_token):
            return self.field.missing_value
        widget.update_terms()
        return widget.terms.getValue(value[0])


@adapter_config(required=(ICollection, ISequenceWidget), provides=IDataConverter)
class CollectionSequenceDataConverter(BaseDataConverter):
    """A special converter between collections and sequence widgets."""

    def to_widget_value(self, value):
        """Convert from Python bool to HTML representation."""
        if value is self.field.missing_value:
            return []
        widget = self.widget
        if widget.terms is None:
            widget.update_terms()
        values = []
        for entry in value:
            try:
                values.append(widget.terms.getTerm(entry).token)
            except LookupError:
                # Swallow lookup errors, in case the options changed.
                pass
        return values

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        widget = self.widget
        if widget.terms is None:
            widget.update_terms()
        collection_type = self.field._type  # pylint: disable=protected-access
        if isinstance(collection_type, tuple):
            collection_type = collection_type[-1]
        return collection_type([widget.terms.getValue(token) for token in value])


@adapter_config(required=(ISequence, ITextLinesWidget), provides=IDataConverter)
class TextLinesConverter(BaseDataConverter):
    """Data converter for ITextLinesWidget."""

    def to_widget_value(self, value):
        """Convert from text lines to HTML representation."""
        # if the value is the missing value, then an empty list is produced.
        if value is self.field.missing_value:
            return ''
        return '\n'.join(to_unicode(v) for v in value)

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        collection_type = self.field._type  # pylint: disable=protected-access
        if isinstance(collection_type, tuple):
            collection_type = collection_type[-1]
        if len(value) == 0:
            return self.field.missing_value
        value_type = self.field.value_type._type  # pylint: disable=protected-access
        if isinstance(value_type, tuple):
            value_type = value_type[0]
        # having a blank line at the end matters, one might want to have a blank
        # entry at the end, resp. do not eat it once we have one
        # splitlines ate that, so need to use split now
        value = value.replace('\r\n', '\n')
        items = []
        for val in value.split('\n'):
            try:
                items.append(value_type(val))
            except ValueError as err:
                raise FormatterValidationError(str(err), val) from err
        return collection_type(items)


@adapter_config(required=(ISequence, IMultiWidget), provides=IDataConverter)
class MultiConverter(BaseDataConverter):
    """Data converter for IMultiWidget."""

    def to_widget_value(self, value):
        """Just dispatch it."""
        if value is self.field.missing_value:
            return []
        converter = self._get_converter(self.field.value_type)

        # we always return a list of values for the widget
        return [converter.to_widget_value(v) for v in value]

    def to_field_value(self, value):
        """Just dispatch it."""
        if len(value) == 0:
            return self.field.missing_value

        converter = self._get_converter(self.field.value_type)
        values = [converter.to_field_value(v) for v in value]

        # convert the field values to a tuple or list
        collection_type = self.field._type  # pylint: disable=protected-access
        return collection_type(values)


@adapter_config(required=(IDict, IMultiWidget), provides=IDataConverter)
class DictMultiConverter(BaseDataConverter):
    """Data converter for IMultiWidget."""

    def to_widget_value(self, value):
        """Just dispatch it."""
        if value is self.field.missing_value:
            return []

        key_converter = self._get_converter(self.field.key_type)
        converter = self._get_converter(self.field.value_type)
        # we always return a list of values for the widget
        return [(key_converter.to_widget_value(k), converter.to_widget_value(v))
                for k, v in value.items()]

    def to_field_value(self, value):
        """Just dispatch it."""
        if len(value) == 0:
            return self.field.missing_value

        key_converter = self._get_converter(self.field.key_type)
        converter = self._get_converter(self.field.value_type)
        return {key_converter.to_field_value(k): converter.to_field_value(v)
                for k, v in value}


@adapter_config(required=(IBool, ISingleCheckBoxWidget), provides=IDataConverter)
class BoolSingleCheckboxDataConverter(BaseDataConverter):
    "A special converter between boolean fields and single checkbox widgets."

    def to_widget_value(self, value):
        """Convert from Python bool to HTML representation."""
        if value:
            return ['selected']
        return []

    def to_field_value(self, value):
        """See interfaces.IDataConverter"""
        if value and value[0] == 'selected':
            return True
        return False
