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

"""PyAMS_form.browser.radio module

This module provides radio widgets.
"""

from zope.interface import implementer_only
from zope.schema.interfaces import IBool, ITitledTokenizedTerm
from zope.schema.vocabulary import SimpleTerm

from pyams_form.browser.widget import HTMLInputWidget, add_field_class
from pyams_form.interfaces.widget import IFieldWidget, IRadioWidget
from pyams_form.util import to_unicode
from pyams_form.widget import FieldWidget, SequenceWidget
from pyams_layer.interfaces import IFormLayer
from pyams_template.interfaces import IPageTemplate


__docformat__ = 'restructuredtext'

from pyams_utils.adapter import adapter_config


@implementer_only(IRadioWidget)
class RadioWidget(HTMLInputWidget, SequenceWidget):
    """Input type raiod widget implementation"""

    klass = 'radio-widget'
    css = 'radio'

    def is_checked(self, term):
        """Check if given term is checked"""
        return term.token in self.value

    def render_for_value(self, value):
        """Render given value"""
        terms = list(self.terms)
        try:
            term = self.terms.getTermByToken(value)
        except LookupError:
            if value == SequenceWidget.no_value_token:
                term = SimpleTerm(value)
                terms.insert(0, term)
                item_id = '%s-novalue' % self.id
            else:
                raise
        else:
            item_id = '%s-%i' % (self.id, terms.index(term))
        checked = self.is_checked(term)
        item = {
            'id': item_id,
            'name': self.name,
            'value': term.token,
            'checked': checked
        }
        template = self.request.registry.getMultiAdapter(
            (self.context, self.request, self.form, self.field, self),
            IPageTemplate, name=self.mode + '-single')
        return template(**{
            'context': self.context,
            'request': self.request,
            'view': self,
            'item': item
        })

    @property
    def items(self):
        """Items list getter"""
        if self.terms is None:
            return
        for count, term in enumerate(self.terms):
            checked = self.is_checked(term)
            item_id = '%s-%i' % (self.id, count)
            if ITitledTokenizedTerm.providedBy(term):
                translate = self.request.localizer.translate
                label = translate(term.title)
            else:
                label = to_unicode(term.value)
            yield {
                'id': item_id,
                'name': self.name,
                'value': term.token,
                'label': label,
                'checked': checked
            }

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super().update()
        add_field_class(self)

    def json_data(self):
        """Get widget data in JSON format"""
        data = super().json_data()
        data['options'] = list(self.items)
        data['type'] = 'radio'
        return data


@adapter_config(required=(IBool, IFormLayer),
                provides=IFieldWidget)
def RadioFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for RadioWidget."""
    return FieldWidget(field, RadioWidget(request))
