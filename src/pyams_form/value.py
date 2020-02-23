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

"""PyAMS_form.value module

Simple value adapters.
"""

from zope.component import adapter
from zope.interface import implementer

from pyams_form.interfaces import IValue
from pyams_form.util import get_specification


__docformat__ = 'restructuredtext'


@implementer(IValue)
class StaticValue:
    """Static value adapter."""

    def __init__(self, value):
        self.value = value

    def get(self):
        """Get static value"""
        return self.value

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.value)


@implementer(IValue)
class ComputedValue:
    """Computed value adapter."""

    def __init__(self, func):
        self.func = func

    def get(self):
        """Get computed value"""
        return self.func(self)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.get())


class ValueFactory:
    """Computed value factory."""

    def __init__(self, value, value_class, discriminators):
        self.value = value
        self.value_class = value_class
        self.discriminators = discriminators

    def __call__(self, *args):
        value_class = self.value_class(self.value)
        for name, value in zip(self.discriminators, args):
            setattr(value_class, name, value)
        return value_class


class ValueCreator:
    """Base class for value creator"""

    value_class = StaticValue

    def __init__(self, discriminators):
        self.discriminators = discriminators

    def __call__(self, value, **kws):
        # Step 1: Check that the keyword argument names match the
        #         discriminators
        if set(kws).difference(set(self.discriminators)):
            raise ValueError('One or more keyword arguments did not match the '
                             'discriminators.')
        # Step 2: Create an attribute value factory
        factory = ValueFactory(value, self.value_class, self.discriminators)
        # Step 3: Build the adaptation signature
        signature = []
        for disc in self.discriminators:
            spec = get_specification(kws.get(disc))
            signature.append(spec)
        # Step 4: Assert the adaptation signature onto the factory
        adapter(*signature)(factory)
        implementer(IValue)(factory)
        return factory


class StaticValueCreator(ValueCreator):
    """Creates static value."""

    value_class = StaticValue


class ComputedValueCreator(ValueCreator):
    """Creates computed value."""

    value_class = ComputedValue
