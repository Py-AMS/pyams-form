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

"""PyAMS_form.browser.orderedselect module

Ordered-selection widget implementation.
"""

from zope.interface import implementer_only
from zope.schema.interfaces import IChoice, IList, ISequence, ITitledTokenizedTerm, ITuple

from pyams_form.browser.widget import HTMLSelectWidget, add_field_class
from pyams_form.interfaces.widget import IFieldWidget, IOrderedSelectWidget
from pyams_form.widget import FieldWidget, SequenceWidget


__docformat__ = "reStructuredText"

from pyams_layer.interfaces import IFormLayer

from pyams_utils.adapter import adapter_config


@implementer_only(IOrderedSelectWidget)
class OrderedSelectWidget(HTMLSelectWidget, SequenceWidget):
    """Ordered-Select widget implementation."""

    size = 5
    multiple = u'multiple'
    items = ()
    selected_items = ()
    notselected_items = ()

    def get_item(self, term, count=0):
        """Get item matching given term"""
        item_id = '%s-%i' % (self.id, count)
        content = term.value
        if ITitledTokenizedTerm.providedBy(term):
            content = self.request.localizer.translate(term.title)
        return {
            'id': item_id,
            'value': term.token,
            'content': content
        }

    def update(self):
        """See pyams_form.interfaces.widget.IWidget."""
        super().update()
        add_field_class(self)
        self.items = [self.get_item(term, count)
                      for count, term in enumerate(self.terms)]
        self.selected_items = [
            self.get_item(self.terms.getTermByToken(token), count)
            for count, token in enumerate(self.value)
        ]
        self.notselected_items = self.deselect()

    def deselect(self):
        """Get unselected items"""
        selected_items = []
        notselected_items = []
        for selected_item in self.selected_items:
            selected_items.append(selected_item['value'])
        for item in self.items:
            if item['value'] not in selected_items:
                notselected_items.append(item)
        return notselected_items

    def json_data(self):
        """Get widget data in JSON format"""
        data = super().json_data()
        data['type'] = 'multi_select'
        data['options'] = self.items
        data['selected'] = self.selected_items
        data['not_selected'] = self.notselected_items
        return data


def OrderedSelectFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for SelectWidget."""
    return FieldWidget(field, OrderedSelectWidget(request))


@adapter_config(required=(ISequence, IFormLayer), provided=IFieldWidget)
def SequenceSelectFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for SelectWidget."""
    return request.registry.getMultiAdapter((field, field.value_type, request), IFieldWidget)


@adapter_config(required=(IList, IChoice, IFormLayer), provided=IFieldWidget)
@adapter_config(required=(ITuple, IChoice, IFormLayer), provided=IFieldWidget)
def SequenceChoiceSelectFieldWidget(field, value_type, request):
    # pylint: disable=invalid-name,unused-argument
    """IFieldWidget factory for SelectWidget."""
    return OrderedSelectFieldWidget(field, request)
