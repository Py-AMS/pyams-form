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

"""PyAMS_form.browser.checkbox module

Checkbox widget implementation.
"""

from zope.interface import implementer_only
from zope.schema.interfaces import IBool, ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from pyams_form.browser.widget import HTMLInputWidget, add_field_class
from pyams_form.interfaces.widget import ICheckBoxWidget, IFieldWidget, ISingleCheckBoxWidget
from pyams_form.term import Terms
from pyams_form.util import to_unicode
from pyams_form.widget import FieldWidget, SequenceWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = 'restructuredtext'


@implementer_only(ICheckBoxWidget)
class CheckBoxWidget(HTMLInputWidget, SequenceWidget):
    """Input type checkbox widget implementation."""

    klass = 'checkbox-widget'
    css = 'checkbox'

    def is_checked(self, term):
        """Check if given term is selected"""
        return term.token in self.value

    @property
    def items(self):
        """Items list getter"""
        if self.terms is None:
            return ()
        items = []
        for count, term in enumerate(self.terms):
            checked = self.is_checked(term)
            item_id = '%s-%i' % (self.id, count)
            if ITitledTokenizedTerm.providedBy(term):
                label = self.request.localizer.translate(term.title)
            else:
                label = to_unicode(term.value)
            items.append({
                'id': item_id,
                'name': self.name,
                'value': term.token,
                'label': label,
                'checked': checked
            })
        return items

    def update(self):
        """See pyams_form.interfaces.widget.IWidget."""
        super().update()
        add_field_class(self)

    def json_data(self):
        """Get widget data in JSON format"""
        data = super().json_data()
        data['type'] = 'check'
        data['options'] = list(self.items)
        return data


def CheckBoxFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for CheckBoxWidget."""
    return FieldWidget(field, CheckBoxWidget(request))


@implementer_only(ISingleCheckBoxWidget)
class SingleCheckBoxWidget(CheckBoxWidget):
    """Single input type checkbox widget implementation."""

    klass = 'single-checkbox-widget'

    def update_terms(self):
        """Update terms"""
        if self.terms is None:
            self.terms = Terms()
            self.terms.terms = SimpleVocabulary((
                SimpleTerm('selected', 'selected', self.label or self.field.title), ))
        return self.terms


@adapter_config(required=(IBool, IFormLayer), provides=IFieldWidget)
def SingleCheckBoxFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for CheckBoxWidget."""
    widget = FieldWidget(field, SingleCheckBoxWidget(request))
    widget.label = ''  # don't show the label twice
    return widget
