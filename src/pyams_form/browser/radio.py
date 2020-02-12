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
from zope.schema.interfaces import ITitledTokenizedTerm, IBool, IVocabularyTokenized
from zope.schema.vocabulary import SimpleTerm

from pyams_form.browser.widget import HTMLInputWidget, add_field_class
from pyams_form.interfaces.widget import IRadioWidget, IFieldWidget
from pyams_form.util import to_unicode
from pyams_form.widget import SequenceWidget, FieldWidget
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
        return term.token in self.value

    def render_for_value(self, value):
        terms = list(self.terms)
        try:
            term = self.terms.getTermByToken(value)
        except LookupError:
            if value == SequenceWidget.no_value_token:
                term = SimpleTerm(value)
                terms.insert(0, term)
                id = '%s-novalue' % self.id
            else:
                raise
        else:
            id = '%s-%i' % (self.id, terms.index(term))
        checked = self.is_checked(term)
        item = {
            'id': id,
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
        if self.terms is None:
            return
        for count, term in enumerate(self.terms):
            checked = self.is_checked(term)
            id = '%s-%i' % (self.id, count)
            if ITitledTokenizedTerm.providedBy(term):
                translate = self.request.localizer.translate
                label = translate(term.title)
            else:
                label = to_unicode(term.value)
            yield {
                'id': id,
                'name': self.name,
                'value': term.token,
                'label': label,
                'checked': checked
            }

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(RadioWidget, self).update()
        add_field_class(self)

    def json_data(self):
        data = super(RadioWidget, self).json_data()
        data['options'] = list(self.items)
        data['type'] = 'radio'
        return data


@adapter_config(required=(IBool, IFormLayer),
                provides=IFieldWidget)
def RadioFieldWidget(field, request):
    """IFieldWidget factory for RadioWidget."""
    return FieldWidget(field, RadioWidget(request))
