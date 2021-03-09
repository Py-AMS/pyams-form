#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

"""PyAMS_form.browser.select module

Select widget implementation.
"""

from zope.interface import Interface, implementer_only
from zope.schema.interfaces import IChoice, ITitledTokenizedTerm, IUnorderedCollection

from pyams_form.browser.widget import HTMLSelectWidget, add_field_class
from pyams_form.interfaces.widget import IFieldWidget, ISelectWidget
from pyams_form.widget import FieldWidget, SequenceWidget
from pyams_layer.interfaces import IFormLayer
from pyams_utils.adapter import adapter_config


__docformat__ = "reStructuredText"

from pyams_form import _  # pylint: disable=ungrouped-imports


@implementer_only(ISelectWidget)
class SelectWidget(HTMLSelectWidget, SequenceWidget):
    """Select widget implementation."""

    klass = 'select-widget'
    css = 'select'
    prompt = False

    no_value_message = _('No value')
    prompt_message = _('Select a value...')

    # Internal attributes
    _adapter_value_attributes = SequenceWidget._adapter_value_attributes + \
        ('no_value_message', 'prompt_message', 'prompt')

    def is_selected(self, term):
        """Check for term selection"""
        return term.token in self.value

    def update(self):
        """See pyams_form.interfaces.widget.IWidget."""
        super().update()
        add_field_class(self)

    @property
    def items(self):
        """Items list getter"""
        if self.terms is None:  # update() has not been called yet
            return ()
        items = []
        if (not self.required or self.prompt) and self.multiple is None:
            if self.prompt:
                message = self.prompt_message
            else:
                message = self.no_value_message
            items.append({
                'id': self.id + '-novalue',
                'value': self.no_value_token,
                'content': message,
                'selected': self.value in ((), [])
            })

        ignored = set(self.value)

        def add_item(idx, term, prefix=''):
            selected = self.is_selected(term)
            if selected and term.token in ignored:
                ignored.remove(term.token)
            item_id = '%s-%s%i' % (self.id, prefix, idx)
            content = term.token
            if ITitledTokenizedTerm.providedBy(term):
                content = self.request.localizer.translate(term.title)
            items.append({
                'id': item_id,
                'value': term.token,
                'content': content,
                'selected': selected
            })

        for idx, term in enumerate(self.terms):
            add_item(idx, term)

        if ignored:
            # some values are not displayed, probably they went away from the vocabulary
            for idx, token in enumerate(sorted(ignored)):
                try:
                    term = self.terms.getTermByToken(token)
                except LookupError:
                    # just in case the term really went away
                    continue

                add_item(idx, term, prefix='missing-')
        return items

    def json_data(self):
        data = super().json_data()
        data['type'] = 'select'
        data['options'] = self.items
        return data


@adapter_config(required=(IChoice, IFormLayer), provided=IFieldWidget)
def ChoiceWidgetDispatcher(field, request):  # pylint: disable=invalid-name
    """Dispatch widget for IChoice based also on its source."""
    return request.registry.getMultiAdapter((field, field.vocabulary, request),
                                            IFieldWidget)


@adapter_config(required=(IChoice, Interface, IFormLayer), provided=IFieldWidget)
def SelectFieldWidget(field, source, request=None):  # pylint: disable=invalid-name
    """IFieldWidget factory for SelectWidget."""
    if request is None:
        real_request = source
    else:
        real_request = request
    return FieldWidget(field, SelectWidget(real_request))


@adapter_config(required=(IUnorderedCollection, IFormLayer), provided=IFieldWidget)
def CollectionSelectFieldWidget(field, request):  # pylint: disable=invalid-name
    """IFieldWidget factory for SelectWidget."""
    widget = request.registry.getMultiAdapter((field, field.value_type, request), IFieldWidget)
    widget.size = 5
    widget.multiple = 'multiple'
    return widget


@adapter_config(required=(IUnorderedCollection, IChoice, IFormLayer), provided=IFieldWidget)
def CollectionChoiceSelectFieldWidget(field, value_type, request):
    # pylint: disable=invalid-name,unused-argument
    """IFieldWidget factory for SelectWidget."""
    return SelectFieldWidget(field, None, request)
