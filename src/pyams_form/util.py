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

"""PyAMS_form.util module

Forms management utilities.
"""

import re
from binascii import hexlify
from collections import OrderedDict
from functools import total_ordering
from string import ascii_letters, digits

from six import class_types
from zope.contenttype import guess_content_type
from zope.interface import alsoProvides, directlyProvidedBy, implementer
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import ISpecification
from zope.schema.interfaces import IObject

from pyams_form.interfaces import IManager, ISelectionManager
from pyams_form.interfaces.form import IContextAware
from pyams_utils.interfaces.form import IDataManager
from pyams_utils.registry import get_current_registry


__docformat__ = 'restructuredtext'

from pyams_form import _  # pylint: disable=ungrouped-imports


_IDENTIFIER = re.compile('[A-Za-z][a-zA-Z0-9_]*$')
_ACCEPTABLE_CHARS = ascii_letters + digits + '_-'


def to_unicode(obj):
    """Convert object to unicode"""
    if isinstance(obj, bytes):
        return obj.decode('utf-8', 'ignore')
    return str(obj)


def to_bytes(obj):
    """Convert object to bytes"""
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, str):
        return obj.encode('utf-8')
    return str(obj).encode('utf-8')


def create_id(name):
    """Returns a *native* string as id of the given name."""
    if _IDENTIFIER.match(name):
        return str(name).lower()
    return hexlify(name.encode('utf-8')).decode()


@total_ordering
class MinType:
    """Minimum value"""

    def __le__(self, other):
        return True

    def __eq__(self, other):
        return self is other


def sorted_none(items):
    """Items sorter"""
    min_type = MinType()
    return sorted(items, key=lambda x: min_type if x is None else x)


def create_css_id(name):
    """Create CSS id"""
    return str(''.join([
        (char if char in _ACCEPTABLE_CHARS else
         hexlify(char.encode('utf-8')).decode())
        for char in name]))


def get_specification(spec, force=False):
    """Get the specification of the given object.

    If the given object is already a specification acceptable to the component
    architecture, it is simply returned. This is true for classes
    and specification objects (which includes interfaces).

    In case of instances, an interface is generated on the fly and tagged onto
    the object. Then the interface is returned as the specification.
    """
    # If the specification is an instance, then we do some magic.
    if (force or
            (spec is not None and
             not ISpecification.providedBy(spec) and
             not isinstance(spec, class_types))):

        # Step 1: Calculate an interface name
        iface_name = 'IGeneratedForObject_%i' % id(spec)

        # Step 2: Find out if we already have such an interface
        existing_interfaces = [
            i for i in directlyProvidedBy(spec) if i.__name__ == iface_name
        ]

        # Step 3a: Return an existing interface if there is one
        if len(existing_interfaces) > 0:
            spec = existing_interfaces[0]
        # Step 3b: Create a new interface if not
        else:
            iface = InterfaceClass(iface_name)
            alsoProvides(spec, iface)
            spec = iface
    return spec


def expand_prefix(prefix):
    """Expand prefix string by adding a trailing period if needed.

    expandPrefix(p) should be used instead of p+'.' in most contexts.
    """
    if prefix and not prefix.endswith('.'):
        return prefix + '.'
    return prefix


def get_widget_by_id(form, widget_id):
    """Get a widget by it's rendered DOM element id."""
    # convert the id to a name
    name = widget_id.replace('-', '.')
    prefix = form.prefix + form.widgets.prefix
    if not name.startswith(prefix):
        raise ValueError("Name %r must start with prefix %r" % (name, prefix))
    short_name = name[len(prefix):]
    return form.widgets.get(short_name, None)


def extract_content_type(form, widget_id):
    """Extract the content type of the widget with the given id."""
    widget = get_widget_by_id(form, widget_id)
    return guess_content_type(widget.filename)[0]


def extract_file_name(form, widget_id, cleanup=True, allow_empty_postfix=False):
    """Extract the filename of the widget with the given id.

    Uploads from win/IE need some cleanup because the filename includes also
    the path. The option ``cleanup=True`` will do this for you. The option
    ``allowEmptyPostfix`` allows to have a filename without extensions. By
    default this option is set to ``False`` and will raise a ``ValueError`` if
    a filename doesn't contain a extension.
    """
    widget = get_widget_by_id(form, widget_id)
    clean_file_name = ''
    dotted_parts = []
    if not allow_empty_postfix or cleanup:
        # We need to strip out the path section even if we do not reomve them
        # later, because we just need to check the filename extension.
        clean_file_name = widget.filename.split('\\')[-1]
        clean_file_name = clean_file_name.split('/')[-1]
        dotted_parts = clean_file_name.split('.')
    if not allow_empty_postfix:
        if len(dotted_parts) <= 1:
            raise ValueError(_('Missing filename extension.'))
    if cleanup:
        return clean_file_name
    return widget.filename


def changed_field(field, value, context=None):
    """Figure if a field's value changed

    Comparing the value of the context attribute and the given value"""
    if context is None:
        context = field.context
    if context is None:
        # IObjectWidget madness
        return True
    if IObject.providedBy(field):
        return True

    # Get the datamanager and get the original value
    dman = get_current_registry().getMultiAdapter((context, field), IDataManager)
    # now figure value changed status
    # Or we can not get the original value, in which case we can not check
    # Or it is an Object, in case we'll never know
    if (not dman.can_access()) or (dman.query() != value):
        return True
    return False


def changed_widget(widget, value, field=None, context=None):
    """Figure if a widget's value changed

    Comparing the value of the widget context attribute and the given value.
    """
    if IContextAware.providedBy(widget) and not widget.ignore_context:
        # if the widget is context aware, figure if it's field changed
        if field is None:
            field = widget.field
        if context is None:
            context = widget.context
        return changed_field(field, value, context=context)
    # otherwise we cannot, return 'always changed'
    return True


@implementer(IManager)
class Manager(OrderedDict):
    """Non-persistent IManager implementation."""

    def create_according_to_list(self, data, order):
        """Arrange elements from data according to sorting of given list"""
        self.clear()
        for key in order:
            if key in data:
                self[key] = data[key]

    def __getitem__(self, key):
        if key not in self:
            try:
                return getattr(self, key)
            except AttributeError:
                # make sure a KeyError is raised later
                pass
        return super().__getitem__(key)


@implementer(ISelectionManager)
class SelectionManager(Manager):
    """Non-persistent ISelectionManager implementation."""

    manager_interface = None

    def __add__(self, other):
        if not self.manager_interface.providedBy(other):
            return NotImplemented
        return self.__class__(self, other)

    def select(self, *names):
        """See interfaces.ISelectionManager"""
        return self.__class__(*[self[name] for name in names])

    def omit(self, *names):
        """See interfaces.ISelectionManager"""
        return self.__class__(
            *[item for name, item in self.items()
              if name not in names])

    def copy(self):
        """See interfaces.ISelectionManager"""
        return self.__class__(*self.values())
