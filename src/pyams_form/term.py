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

"""PyAMS_form.term module

Terms management module.

Note: This module doesn't use snake_case for compatibility purposes with zope.schema package,
which implies many Pylint annotations...
"""

from zope.interface import Interface
from zope.schema.interfaces import IBaseVocabulary, IBool, IChoice, ICollection, IIterableSource
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_form.interfaces import IBoolTerms, ITerms, IVocabularyTerms
from pyams_form.interfaces.form import IContextAware
from pyams_form.interfaces.widget import IWidget
from pyams_form.util import create_css_id, to_unicode
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.form import IDataManager


__docformat__ = 'restructuredtext'

from pyams_form import _  # pylint: disable=ungrouped-imports


class Terms:
    """Base implementation for custom ITerms."""

    terms = None

    def getTerm(self, value):  # pylint: disable=invalid-name
        """Get term matching given value"""
        return self.terms.getTerm(value)

    def getTermByToken(self, token):  # pylint: disable=invalid-name
        """Get term matching given token"""
        return self.terms.getTermByToken(token)

    def getValue(self, token):  # pylint: disable=invalid-name
        """Get value matching given token"""
        return self.getTermByToken(token).value

    def __iter__(self):
        return iter(self.terms)

    def __len__(self):
        return self.terms.__len__()

    def __contains__(self, value):
        return self.terms.__contains__(value)


class SourceTerms(Terms):
    """Base implementation for ITerms using a source instead of a vocabulary."""

    def __init__(self, context, request, form, field, source, widget):
        # pylint: disable=too-many-arguments
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.source = source
        self.terms = request.registry.getMultiAdapter((self.source, self.request),
                                                      IVocabularyTerms)

    def getTerm(self, value):
        try:
            return super().getTerm(value)
        except KeyError as err:
            raise LookupError(value) from err

    def getTermByToken(self, token):
        # This is rather expensive
        for value in self.source:
            term = self.getTerm(value)
            if term.token == token:
                return term
        raise LookupError(token)

    def getValue(self, token):
        try:
            return self.terms.getValue(token)
        except KeyError as err:
            raise LookupError(token) from err

    def __iter__(self):
        for value in self.source:
            yield self.terms.getTerm(value)

    def __len__(self):
        return len(self.source)

    def __contains__(self, value):
        return value in self.source


@adapter_config(required=(Interface, IFormLayer, Interface, IChoice, IWidget),
                provides=ITerms)
def ChoiceTerms(context, request, form, field, widget):  # pylint: disable=invalid-name
    """Choice terms adapter"""
    if field.context is None:
        field = field.bind(context)
    terms = field.vocabulary
    return request.registry.queryMultiAdapter((context, request, form, field, terms, widget),
                                              ITerms)


@adapter_config(required=(Interface, IFormLayer, Interface, IChoice, IBaseVocabulary, IWidget),
                provides=ITerms)
class ChoiceTermsVocabulary(Terms):
    """ITerms adapter for zope.schema.IChoice based implementations using
    vocabulary."""

    def __init__(self, context, request, form, field, vocabulary, widget):
        # pylint: disable=too-many-arguments
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = vocabulary


class MissingTermsBase:  # pylint: disable=no-member
    """Base class for MissingTermsMixin classes."""

    def _can_query_current_value(self):
        return IContextAware.providedBy(self.widget) and not self.widget.ignore_context

    def _query_current_value(self):
        return self.request.registry.getMultiAdapter((self.widget.context, self.field),
                                                     IDataManager).query()

    @staticmethod
    def _make_token(value):
        """create a unique valid ASCII token"""
        return create_css_id(to_unicode(value))

    def _make_missing_term(self, value):
        """Return a term that should be displayed for the missing token"""
        uvalue = to_unicode(value)
        return SimpleTerm(value, self._make_token(value),
                          title=_('Missing: ${value}', mapping=dict(value=uvalue)))


class MissingTermsMixin(MissingTermsBase):
    """This can be used in case previous values/tokens get missing
    from the vocabulary and you still need to display/keep the values"""

    def getTerm(self, value):  # pylint: disable=invalid-name
        """Get term martching given value"""
        try:
            return super().getTerm(value)
        except LookupError:
            if self._can_query_current_value():
                cur_value = self._query_current_value()
                if cur_value == value:
                    return self._make_missing_term(value)
            raise

    def getTermByToken(self, token):  # pylint: disable=invalid-name
        """Get term matching given token"""
        try:
            return super().getTermByToken(token)
        except LookupError as err:
            if self._can_query_current_value():
                value = self._query_current_value()
                term = self._make_missing_term(value)
                if term.token == token:
                    # check if the given token matches the value, if not
                    # fall back on LookupError, otherwise we might accept
                    # any crap coming from the request
                    return term

            raise LookupError(token) from err


@adapter_config(required=(Interface, IFormLayer, Interface, IChoice, IBaseVocabulary, IWidget),
                provides=ITerms)
class MissingChoiceTermsVocabulary(MissingTermsMixin, ChoiceTermsVocabulary):
    """ITerms adapter for zope.schema.IChoice based implementations using
    vocabulary with missing terms support"""


@adapter_config(required=(Interface, IFormLayer, Interface, IChoice, IIterableSource, IWidget),
                provides=ITerms)
class ChoiceTermsSource(SourceTerms):
    """ITerms adapter for zope.schema.IChoice based implementations using source."""


@adapter_config(required=(Interface, IFormLayer, Interface, IChoice, IIterableSource, IWidget),
                provides=ITerms)
class MissingChoiceTermsSource(MissingTermsMixin, ChoiceTermsSource):
    """ITerms adapter for zope.schema.IChoice based implementations using source
       with missing terms support."""


@adapter_config(required=(Interface, IFormLayer, Interface, IBool, IWidget),
                provides=IBoolTerms)
class BoolTerms(Terms):
    """Default yes and no terms are used by default for IBool fields."""

    true_label = _('yes')
    false_label = _('no')

    def __init__(self, context, request, form, field, widget):
        # pylint: disable=too-many-arguments
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        terms = [SimpleTerm(*args)
                 for args in [(True, 'true', self.true_label),
                              (False, 'false', self.false_label)]]
        self.terms = SimpleVocabulary(terms)


@adapter_config(required=(Interface, IFormLayer, Interface, ICollection, IWidget),
                provides=ITerms)
def CollectionTerms(context, request, form, field, widget):  # pylint: disable=invalid-name
    """Collection terms adapter"""
    terms = field.value_type.bind(context).vocabulary
    return request.registry.queryMultiAdapter((context, request, form, field, terms, widget),
                                              ITerms)


@adapter_config(required=(Interface, IFormLayer, Interface, ICollection, IBaseVocabulary, IWidget),
                provides=ITerms)
class CollectionTermsVocabulary(Terms):
    """ITerms adapter for zope.schema.ICollection based implementations using
    vocabulary."""

    def __init__(self, context, request, form, field, vocabulary, widget):
        # pylint: disable=too-many-arguments
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget
        self.terms = vocabulary


class MissingCollectionTermsMixin(MissingTermsBase):
    """`MissingTermsMixin` adapted to collections."""

    def getTerm(self, value):  # pylint: disable=invalid-name
        """Get term matching given value"""
        try:
            return super().getTerm(value)
        except LookupError:
            if self._can_query_current_value():
                if value in self._query_current_value():
                    return self._make_missing_term(value)
            raise

    def getTermByToken(self, token):  # pylint: disable=invalid-name
        """Get term matching given token"""
        try:
            return super().getTermByToken(token)
        except LookupError:
            if self._can_query_current_value():
                for value in self._query_current_value():
                    term = self._make_missing_term(value)
                    if term.token == token:
                        # check if the given token matches the value, if not
                        # fall back on LookupError, otherwise we might accept
                        # any crap coming from the request
                        return term
            raise

    def getValue(self, token):  # pylint: disable=invalid-name
        """Get value matching given token"""
        try:
            return super().getValue(token)
        except LookupError:
            if self._can_query_current_value():
                for value in self._query_current_value():
                    term = self._make_missing_term(value)
                    if term.token == token:
                        # check if the given token matches the value, if not
                        # fall back on LookupError, otherwise we might accept
                        # any crap coming from the request
                        return value
            raise


class MissingCollectionTermsVocabulary(MissingCollectionTermsMixin,
                                       CollectionTermsVocabulary):
    """ITerms adapter for zope.schema.ICollection based implementations using
    vocabulary with missing terms support."""


@adapter_config(required=(Interface, IFormLayer, Interface, ICollection, IIterableSource, IWidget),
                provides=ITerms)
class CollectionTermsSource(SourceTerms):
    """ITerms adapter for zope.schema.ICollection based implementations using
    source."""


class MissingCollectionTermsSource(MissingCollectionTermsMixin,
                                   CollectionTermsSource):
    """ITerms adapter for zope.schema.ICollection based implementations using
    source with missing terms support."""
