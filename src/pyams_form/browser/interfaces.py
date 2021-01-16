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

"""PyAMS_form.browser.interfaces module

Common browser-related interfaces definition.
"""

from zope.interface import Interface
from zope.schema import ASCIILine, Choice, Int, TextLine


__docformat__ = 'restructuredtext'


class IWidgetLayoutSupport(Interface):
    """Widget with layout support interface"""

    css = TextLine(title='Widget layout CSS class name(s)',
                   description='This attribute defines one or more layout class names.',
                   default='row',
                   required=False)

    # pylint: disable=too-many-arguments
    def get_css_class(self, klass=None, error=None, required=None,
                      class_pattern='%(class)s', error_pattern='%(class)s-error',
                      required_pattern='%(class)s-required'):
        """Setup given css class (klass) with error and required postfix

        If no klass name is given the widget.wrapper class name/names get used.
        It is also possible if more then one (empty space separated) names
        are given as klass argument.

        This method can get used from your form or widget template or widget
        layout template without to re-implement the widget itself just because
        you a different CSS class concept.

        """


class IHTMLCoreAttributes(Interface):
    """The HTML element 'core' attributes."""

    # pylint: disable=invalid-name
    id = ASCIILine(title='Id',
                   description=('This attribute assigns a name to an element. This '
                                'name must be unique in a document.'),
                   required=False)

    # HTML "class" attribute; "class" is a keyword in Python.
    klass = TextLine(title='Class',
                     description=('This attribute assigns a class name or set of '
                                  'class names to an element. Any number of elements '
                                  'may be assigned the same class name or names.'),
                     required=False)

    style = TextLine(title='Style',
                     description=('This attribute offers advisory information about '
                                  'the element for which it is set.'),
                     required=False)

    title = TextLine(title='Title',
                     description=('This attribute offers advisory information about '
                                  'the element for which it is set.'),
                     required=False)


class IHTMLI18nAttributes(Interface):
    """The HTML element 'i18n' attributes."""

    lang = TextLine(title='Language',
                    description=("This attribute specifies the base language of an "
                                 "element's attribute values and text content."),
                    required=False)


class IHTMLEventsAttributes(Interface):
    """The HTML element 'events' attributes."""

    onclick = TextLine(title='On Click',
                       description=('The ``onclick`` event occurs when the pointing device '
                                    'button is clicked over an element.'),
                       required=False)

    ondblclick = TextLine(title='On Double-Click',
                          description=('The ``ondblclick`` event occurs when the pointing '
                                       'device button is double clicked over an element.'),
                          required=False)

    onmousedown = TextLine(title='On Mouse Down',
                           description=('The onmousedown event occurs when the pointing '
                                        'device button is pressed over an element.'),
                           required=False)

    onmouseup = TextLine(title='On Mouse Up',
                         description=('The ``onmouseup`` event occurs when the pointing '
                                      'device button is released over an element.'),
                         required=False)

    onmouseover = TextLine(title='On Mouse Over',
                           description=('The ``onmouseover`` event occurs when the pointing '
                                        'device is moved onto an element.'),
                           required=False)

    onmousemove = TextLine(title='On Mouse Move',
                           description=('The ``onmousemove`` event occurs when the pointing '
                                        'device is moved while it is over an element.'),
                           required=False)

    onmouseout = TextLine(title='On Mouse Out',
                          description=('The ``onmouseout`` event occurs when the pointing '
                                       'device is moved away from an element.'),
                          required=False)

    onkeypress = TextLine(title='On Key Press',
                          description=('The ``onkeypress`` event occurs when a key is '
                                       'pressed and released over an element.'),
                          required=False)

    onkeydown = TextLine(title='On Key Down',
                         description=('The ``onkeydown`` event occurs when a key is pressed '
                                      'down over an element.'),
                         required=False)

    onkeyup = TextLine(title='On Key Up',
                       description=('The ``onkeyup`` event occurs when a key is released '
                                    'over an element.'),
                       required=False)


class IHTMLFormElement(IHTMLCoreAttributes,
                       IHTMLI18nAttributes,
                       IHTMLEventsAttributes,
                       IWidgetLayoutSupport):
    """A generic form-related element including layout template support."""

    disabled = Choice(title='Disabled',
                      description=('When set for a form control, this boolean attribute '
                                   'disables the control for user input.'),
                      values=(None, 'disabled'),
                      required=False)

    tabindex = Int(title='Tab Index',
                   description=('This attribute specifies the position of the current '
                                'element in the tabbing order for the current '
                                'document. This value must be a number between 0 and '
                                '32767.'),
                   required=False)

    onfocus = TextLine(title='On Focus',
                       description=('The ``onfocus`` event occurs when an element receives '
                                    'focus either by the pointing device or by tabbing '
                                    'navigation.'),
                       required=False)

    onblur = TextLine(title='On blur',
                      description=('The ``onblur`` event occurs when an element loses '
                                   'focus either by the pointing device or by tabbing '
                                   'navigation.'),
                      required=False)

    onchange = TextLine(title='On Change',
                        description=('The onchange event occurs when a control loses the '
                                     'input focus and its value has been modified since '
                                     'gaining focus.'),
                        required=False)

    def add_class(self, klass):
        """Add a class to the HTML element.

        The class must be added to the ``klass`` attribute.
        """


class IHTMLInputWidget(IHTMLFormElement):
    """A widget using the HTML INPUT element."""

    readonly = Choice(title='Read-Only',
                      description=('When set for a form control, this boolean attribute '
                                   'prohibits changes to the control.'),
                      values=(None, 'readonly'),
                      required=False)

    alt = TextLine(title='Alternate Text',
                   description=('For user agents that cannot display images, forms, '
                                'or applets, this attribute specifies alternate text.'),
                   required=False)

    accesskey = TextLine(title='Access Key',
                         description='This attribute assigns an access key to an element.',
                         min_length=1,
                         max_length=1,
                         required=False)

    onselect = TextLine(title='On Select',
                        description=('The ``onselect`` event occurs when a user selects '
                                     'some text in a text field.'),
                        required=False)


class IHTMLImageWidget(IHTMLInputWidget):
    """A widget using the HTML INPUT element with type 'image'."""

    src = TextLine(title='Image Source',
                   description='The source of the image used to display the widget.',
                   required=True)


class IHTMLTextInputWidget(IHTMLFormElement):
    """A widget using the HTML INPUT element (for text types)."""

    size = Int(title='Size',
               description=('This attribute tells the user agent the initial width '
                            'of the control -- in this case in characters.'),
               required=False)

    maxlength = Int(title='Maximum Length',
                    description=('This attribute specifies the maximum number of '
                                 'characters the user may enter.'),
                    required=False)

    placeholder = TextLine(title='Placeholder Text',
                           description=('This attribute represents a short hint '
                                        '(a word or short phrase) intended to aid the user '
                                        'with data entry when the control has no value.'),
                           required=False)

    autocomplete = Choice(title='Auto-Complete Control',
                          description=('This attribute controls whether the browser should '
                                       'automatically complete the input value.'),
                          values=('off', 'on', 'username', 'new-password', 'current-password',
                                  'cc-number'),
                          required=False)

    autocapitalize = Choice(title='Auto-Capitalization Control',
                            description=('This attribute controls whether the browser should '
                                         'automatically capitalize the input value.'),
                            values=('off', 'on'),
                            required=False)


class IHTMLTextAreaWidget(IHTMLFormElement):
    """A widget using the HTML TEXTAREA element."""

    rows = Int(title='Rows',
               description=('This attribute specifies the number of visible text '
                            'lines.'),
               required=False)

    cols = Int(title='columns',
               description=('This attribute specifies the visible width in average '
                            'character widths.'),
               required=False)

    readonly = Choice(title='Read-Only',
                      description=('When set for a form control, this boolean attribute '
                                   'prohibits changes to the control.'),
                      values=(None, 'readonly'),
                      required=False)

    accesskey = TextLine(title='Access Key',
                         description='This attribute assigns an access key to an element.',
                         min_length=1,
                         max_length=1,
                         required=False)

    onselect = TextLine(title='On Select',
                        description=('The ``onselect`` event occurs when a user selects '
                                     'some text in a text field.'),
                        required=False)


class IHTMLSelectWidget(IHTMLFormElement):
    """A widget using the HTML SELECT element."""

    multiple = Choice(title='Multiple',
                      description=('If set, this boolean attribute allows multiple '
                                   'selections.'),
                      values=(None, 'multiple'),
                      required=False)

    size = Int(title='Size',
               description=('If a  SELECT element is presented as a scrolled '
                            'list box, this attribute specifies the number of '
                            'rows in the list that should be visible at the '
                            'same time.'),
               default=1,
               required=False)
