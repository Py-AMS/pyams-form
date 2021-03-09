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

"""PyAMS_form.browser.widget module

Base widget implementations.
"""

from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty

from pyams_form.browser.interfaces import IHTMLFormElement, IHTMLInputWidget, IHTMLSelectWidget, \
    IHTMLTextAreaWidget, IHTMLTextInputWidget
from pyams_form.interfaces import INPUT_MODE
from pyams_form.interfaces.widget import IFieldWidget


__docformat__ = 'restructuredtext'


class WidgetLayoutSupport:
    """Widget layout support mix-in class"""

    @staticmethod
    def wrap_css_class(klass, pattern='%(class)s'):
        """Return a list of css class names wrapped with given pattern"""
        if klass is not None and pattern is not None:
            return [pattern % {'class': k} for k in klass.split()]
        return []

    def get_css_class(self, klass=None, error=None, required=None,
                      class_pattern='%(class)s', error_pattern='%(class)s-error',
                      required_pattern='%(class)s-required'):
        # pylint: disable=too-many-arguments
        """Setup given css class (klass) with error and required postfix

        If no klass name is given the widget.wrapper class name/names get used.
        It is also possible if more then one (empty space separated) names
        are given as klass argument.

        This method can get used from your form or widget template or widget
        layout template without to re-implement the widget itself just because
        you a different CSS class concept.

        The following sample:

        <div tal:attributes="class python:widget.getCSSClass('foo bar')">
          label widget and error
        </div>

        will render a div tag if the widget field defines required=True:

        <div class="foo-error bar-error foo-required bar-required foo bar">
          label widget and error
        </div>

        And the following sample:

        <div tal:attributes="class python:widget.getCSSClass('row')">
          label widget and error
        </div>

        will render a div tag if the widget field defines required=True
        and an error occurs:

        <div class="row-error row-required row">
          label widget and error
        </div>

        Note; you need to define a globale widget property if you use
        python:widget (in your form template). And you need to use the
        view scope in your widget or layout templates.

        Note, you can set the pattern to None for skip error or required
        rendering. Or you can use a pattern like 'error' or 'required' if
        you like to skip postfixing your default css klass name for error or
        required rendering.

        """
        classes = []
        # setup class names
        if klass is not None:
            kls = klass
        else:
            kls = self.css  # pylint: disable=no-member

        # setup error class names
        if error is None:
            error = kls

        # setup required class names
        if required is None:
            required = kls

        # append error class names
        if self.error is not None:  # pylint: disable=no-member
            classes += self.wrap_css_class(error, error_pattern)
        # append required class names
        if self.required:  # pylint: disable=no-member
            classes += self.wrap_css_class(required, required_pattern)
        # append given class names
        classes += self.wrap_css_class(kls, class_pattern)
        # remove duplicated class names but keep order
        unique = []
        # pylint: disable=expression-not-assigned
        [unique.append(kls) for kls in classes if kls not in unique]
        return ' '.join(unique)


@implementer(IHTMLFormElement)
class HTMLFormElement(WidgetLayoutSupport):
    """HTML form element"""

    id = FieldProperty(IHTMLFormElement['id'])  # pylint: disable=invalid-name
    klass = FieldProperty(IHTMLFormElement['klass'])
    style = FieldProperty(IHTMLFormElement['style'])
    title = FieldProperty(IHTMLFormElement['title'])

    lang = FieldProperty(IHTMLFormElement['lang'])

    onclick = FieldProperty(IHTMLFormElement['onclick'])
    ondblclick = FieldProperty(IHTMLFormElement['ondblclick'])
    onmousedown = FieldProperty(IHTMLFormElement['onmousedown'])
    onmouseup = FieldProperty(IHTMLFormElement['onmouseup'])
    onmouseover = FieldProperty(IHTMLFormElement['onmouseover'])
    onmousemove = FieldProperty(IHTMLFormElement['onmousemove'])
    onmouseout = FieldProperty(IHTMLFormElement['onmouseout'])
    onkeypress = FieldProperty(IHTMLFormElement['onkeypress'])
    onkeydown = FieldProperty(IHTMLFormElement['onkeydown'])
    onkeyup = FieldProperty(IHTMLFormElement['onkeyup'])

    disabled = FieldProperty(IHTMLFormElement['disabled'])
    tabindex = FieldProperty(IHTMLFormElement['tabindex'])
    onfocus = FieldProperty(IHTMLFormElement['onfocus'])
    onblur = FieldProperty(IHTMLFormElement['onblur'])
    onchange = FieldProperty(IHTMLFormElement['onchange'])

    # layout support
    css = FieldProperty(IHTMLFormElement['css'])

    def add_class(self, klass):
        """See IHTMLFormElement"""
        if not self.klass:
            self.klass = str(klass)
        else:
            # make sure items are not repeated
            parts = self.klass.split() + [str(klass)]
            seen = {}
            unique = []
            for item in parts:
                if item in seen:
                    continue
                seen[item] = 1
                unique.append(item)
            self.klass = ' '.join(unique)

    def update(self):
        """See z3c.form.IWidget"""
        super().update()  # pylint: disable=no-member
        if self.mode == INPUT_MODE and self.required:  # pylint: disable=no-member
            self.add_class('required')


@implementer(IHTMLInputWidget)
class HTMLInputWidget(HTMLFormElement):
    """Base HTML input widget"""
    readonly = FieldProperty(IHTMLInputWidget['readonly'])
    alt = FieldProperty(IHTMLInputWidget['alt'])
    accesskey = FieldProperty(IHTMLInputWidget['accesskey'])
    onselect = FieldProperty(IHTMLInputWidget['onselect'])


@implementer(IHTMLTextInputWidget)
class HTMLTextInputWidget(HTMLInputWidget):
    """Base HTML text input widget"""
    size = FieldProperty(IHTMLTextInputWidget['size'])
    maxlength = FieldProperty(IHTMLTextInputWidget['maxlength'])
    placeholder = FieldProperty(IHTMLTextInputWidget['placeholder'])
    autocomplete = FieldProperty(IHTMLTextInputWidget['autocomplete'])
    autocapitalize = FieldProperty(IHTMLTextInputWidget['autocapitalize'])


@implementer(IHTMLTextAreaWidget)
class HTMLTextAreaWidget(HTMLFormElement):
    """Base HTML textarea widget"""
    rows = FieldProperty(IHTMLTextAreaWidget['rows'])
    cols = FieldProperty(IHTMLTextAreaWidget['cols'])
    readonly = FieldProperty(IHTMLTextAreaWidget['readonly'])
    accesskey = FieldProperty(IHTMLTextAreaWidget['accesskey'])
    onselect = FieldProperty(IHTMLTextAreaWidget['onselect'])


@implementer(IHTMLSelectWidget)
class HTMLSelectWidget(HTMLFormElement):
    """Base HTML select widget"""
    multiple = FieldProperty(IHTMLSelectWidget['multiple'])
    size = FieldProperty(IHTMLSelectWidget['size'])


def add_field_class(widget):
    """Add a class to the widget that is based on the field type name.

    If the widget does not have field, then nothing is done.
    """
    if IFieldWidget.providedBy(widget):
        klass = str(widget.field.__class__.__name__.lower() + '-field')
        widget.add_class(klass)
