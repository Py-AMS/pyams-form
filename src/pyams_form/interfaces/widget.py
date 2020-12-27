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

"""PyAMS_form.interfaces.widget module

This module include all widget-related interfaces (except IWidgetLayoutTemplate interface
which is defined into main interfaces module to avoid cyclic dependencies.
"""

from zope.interface import Attribute, Interface
from zope.location import ILocation
from zope.schema import ASCIILine, Bool, Field, Object, Text, TextLine, Tuple

from pyams_form.interfaces import DISPLAY_MODE, HIDDEN_MODE, IManager, INPUT_MODE, ITerms
from pyams_form.template import widget_layout_config, widget_template_config
from pyams_layer.interfaces import IFormLayer
from pyams_utils.interfaces.form import NO_VALUE


__docformat__ = 'restructuredtext'

from pyams_form import _  # pylint: disable=ungrouped-imports


class IFieldWidget(Interface):
    """Offers a field attribute.

    For advanced uses the widget will make decisions based on the field
    it is rendered for.
    """

    field = Field(title=_('Field'),
                  description=_('The schema field which the widget is representing'),
                  required=True)


@widget_layout_config(mode=INPUT_MODE,
                      layer=IFormLayer,
                      template='templates/widget-layout.pt')
@widget_layout_config(mode=DISPLAY_MODE,
                      layer=IFormLayer,
                      template='templates/widget-layout-display.pt')
@widget_layout_config(mode=HIDDEN_MODE,
                      layer=IFormLayer,
                      template='templates/widget-layout-hidden.pt')
class IWidget(ILocation):
    """A widget within a form"""

    name = ASCIILine(title=_('Name'),
                     description=_('The name the widget is known under'),
                     required=True)

    label = TextLine(title=_('Label'),
                     description=_('''The widget label.

        Label may be translated for the request.

        The attribute may be implemented as either a read-write or read-only
        property, depending on the requirements for a specific implementation.
        '''),
                     required=True)

    mode = ASCIILine(title=_('Mode'),
                     description=_('A widget mode'),
                     default=INPUT_MODE,
                     required=True)

    required = Bool(title=_('Required'),
                    description=_('If true the widget should be displayed as required '
                                  'input'),
                    default=False,
                    required=True)

    error = Field(title=_('Error'),
                  description=_('If an error occurred during any step, the error view '
                                'stored here'),
                  required=False)

    value = Field(title=_('Value'),
                  description=_('The value that the widget represents'),
                  required=False)

    template = Attribute('''The widget template''')
    layout = Attribute('''The widget layout template''')

    ignore_request = Bool(title=_('Ignore Request'),
                          description=_('A flag, when set, forces the widget not to look at '
                                        'the request for a value'),
                          default=False,
                          required=False)

    # ugly thing to remove set_errors parameter from extract
    set_errors = Bool(title=_('Set errors'),
                      description=_('A flag, when set, the widget sets error messages '
                                    'on calling extract()'),
                      default=True,
                      required=False)

    # a bit different from ignore_required_on_extract, because we record
    # here the fact, but for IValidator, because the check happens there
    ignore_required_on_validation = Bool(title=_('Ignore Required validation'),
                                         description=_(
                                             "If set then required fields will pass validation "
                                             "regardless whether they're filled in or not"),
                                         default=False,
                                         required=True)

    show_default = Bool(title=_('Show default value'),
                        description=_('A flag, when set, makes the widget to display '
                                      'field|adapter provided default values'),
                        default=True,
                        required=False)

    def extract(self, default=NO_VALUE):
        """Extract the string value(s) of the widget from the form.

        The return value may be any Python construct, but is typically a
        simple string, sequence of strings or a dictionary.

        The value *must not* be converted into a native format.

        If an error occurs during the extraction, the default value should be
        returned. Since this should never happen, if the widget is properly
        designed and used, it is okay to NOT raise an error here, since we do
        not want to crash the system during an inproper request.

        If there is no value to extract, the default is to be returned.
        """

    def update(self):
        """Setup all of the widget information used for displaying."""

    def render(self):
        """Render the plain widget without additional layout"""

    def json_data(self):
        """Returns a dictionary for the widget"""

    def __call__(self):  # pylint: disable=signature-differs
        """Render a layout template which is calling widget/render"""


class ISequenceWidget(IWidget):
    """Term based sequence widget base.

    The sequence widget is used for select items from a sequence. Don't get
    confused, this widget does support to choose one or more values from a
    sequence. The word sequence is not used for the schema field, it's used
    for the values where this widget can choose from.

    This widget base class is used for build single or sequence values based
    on a sequence which is in most use case a collection. e.g.
    IList of IChoice for sequence values or IChoice for single values.

    See also the MultiWidget for build sequence values based on none collection
    based values. e.g. IList of ITextLine
    """

    no_value_token = ASCIILine(title=_('NO_VALUE Token'),
                               description=_(
                                   'The token to be used, if no value has been selected.'))

    terms = Object(title=_('Terms'),
                   description=_('A component that provides the options for selection'),
                   schema=ITerms)

    def update_terms(self):
        """Update the widget's ``terms`` attribute and return the terms.

        This method can be used by external components to get the terms
        without having to worry whether they are already created or not.
        """


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/multi-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/multi-display.pt')
@widget_template_config(mode=HIDDEN_MODE,
                        layer=IFormLayer,
                        template='templates/multi-hidden.pt')
class IMultiWidget(IWidget):
    """None Term based sequence widget base.

    The multi widget is used for ITuple, IList or IDict if no other widget is defined.

    Some IList or ITuple are using another specialized widget if they can
    choose from a collection. e.g. a IList of IChoice. The base class of such
    widget is the ISequenceWidget.

    This widget can handle none collection based sequences and offers add or
    remove values to or from the sequence. Each sequence value get rendered by
    it's own relevant widget. e.g. IList of ITextLine or ITuple of IInt
    """


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/select-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/select-display.pt')
@widget_template_config(mode=HIDDEN_MODE,
                        layer=IFormLayer,
                        template='templates/select-hidden.pt')
class ISelectWidget(ISequenceWidget):
    """Select widget with ITerms option."""

    prompt = Bool(title=_('Prompt'),
                  description=_('A flag, when set, enables a choice explicitely '
                                'requesting the user to choose a value'),
                  default=False)

    items = Tuple(title=_('Items'),
                  description=_('A collection of dictionaries containing all pieces of '
                                'information for rendering. The following keys must '
                                'be in each dictionary: id, value, content, selected'))

    no_value_message = Text(title=_('No-Value Message'),
                            description=_('A human-readable text that is displayed to refer the '
                                          'missing value.'))

    prompt_message = Text(title=_('Prompt Message'),
                          description=_('A human-readable text that is displayed to refer the '
                                        'missing value.'))


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/orderedselect-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/orderedselect-display.pt')
class IOrderedSelectWidget(ISequenceWidget):
    """Ordered Select widget with ITerms option."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/checkbox-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/checkbox-display.pt')
@widget_template_config(mode=HIDDEN_MODE,
                        layer=IFormLayer,
                        template='templates/checkbox-hidden.pt')
class ICheckBoxWidget(ISequenceWidget):
    """Checbox widget."""


class ISingleCheckBoxWidget(ICheckBoxWidget):
    """Single Checbox widget."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/radio-input.pt')
@widget_template_config(mode='{}-single'.format(INPUT_MODE),
                        layer=IFormLayer,
                        template='templates/radio-input-single.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/radio-display.pt')
@widget_template_config(mode='{}-single'.format(DISPLAY_MODE),
                        layer=IFormLayer,
                        template='templates/radio-display-single.pt')
@widget_template_config(mode=HIDDEN_MODE,
                        layer=IFormLayer,
                        template='templates/radio-hidden.pt')
@widget_template_config(mode='{}-single'.format(HIDDEN_MODE),
                        layer=IFormLayer,
                        template='templates/radio-hidden-single.pt')
class IRadioWidget(ISequenceWidget):
    """Radio widget."""

    def render_for_value(self, value):
        """Render a single radio button element for a given value.

        Here the word ``value`` is used in the HTML sense, in other
        words it is a term token.
        """


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/submit-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/submit-display.pt')
class ISubmitWidget(IWidget):
    """Submit widget."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/image-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/image-display.pt')
class IImageWidget(IWidget):
    """Submit widget."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/button-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/button-display.pt')
class IButtonWidget(IWidget):
    """Button widget."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/textarea-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/textarea-display.pt')
@widget_template_config(mode=HIDDEN_MODE,
                        layer=IFormLayer,
                        template='templates/textarea-hidden.pt')
class ITextAreaWidget(IWidget):
    """Text widget."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/textlines-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/textlines-display.pt')
@widget_template_config(mode=HIDDEN_MODE,
                        layer=IFormLayer,
                        template='templates/textlines-hidden.pt')
class ITextLinesWidget(IWidget):
    """Text lines widget."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/text-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/text-display.pt')
@widget_template_config(mode=HIDDEN_MODE,
                        layer=IFormLayer,
                        template='templates/text-hidden.pt')
class ITextWidget(IWidget):
    """Text widget."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/file-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/file-display.pt')
class IFileWidget(ITextWidget):
    """File widget."""


class IMediaFileWidget(IFileWidget):
    """Media file widget marker interface"""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/password-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/password-display.pt')
class IPasswordWidget(ITextWidget):
    """Password widget."""


@widget_template_config(mode=INPUT_MODE,
                        layer=IFormLayer,
                        template='templates/object-input.pt')
@widget_template_config(mode=DISPLAY_MODE,
                        layer=IFormLayer,
                        template='templates/object-display.pt')
@widget_template_config(mode=HIDDEN_MODE,
                        layer=IFormLayer,
                        template='templates/object-hidden.pt')
class IObjectWidget(IWidget):
    """Object widget."""

    def setup_fields(self):
        """setup fields on the widget, by default taking the fields of
        self.schema"""


class IWidgets(IManager):
    """A widget manager"""

    prefix = ASCIILine(title=_('Prefix'),
                       description=_('The prefix of the widgets'),
                       default='widgets.',
                       required=True)

    mode = ASCIILine(title=_('Prefix'),
                     description=_('The prefix of the widgets'),
                     default=INPUT_MODE,
                     required=True)

    errors = Field(title=_('Errors'),
                   description=_('The collection of errors that occured during '
                                 'validation'),
                   default=(),
                   required=True)

    ignore_context = Bool(title=_('Ignore Context'),
                          description=_('If set the context is ignored to retrieve a value'),
                          default=False,
                          required=True)

    ignore_request = Bool(title=_('Ignore Request'),
                          description=_('If set the request is ignored to retrieve a value'),
                          default=False,
                          required=True)

    ignore_readonly = Bool(title=_('Ignore Readonly'),
                           description=_('If set then readonly fields will also be shown'),
                           default=False,
                           required=True)

    ignore_required_on_extract = Bool(title=_('Ignore Required validation on extract'),
                                      description=_(
                                          "If set then required fields will pass validation "
                                          "on extract regardless whether they're filled in or not"),
                                      default=False,
                                      required=True)

    has_required_rields = Bool(title=_('Has required fields'),
                               description=_('A flag set when at least one field is marked as '
                                             'required'),
                               default=False,
                               required=False)

    # ugly thing to remove set_errors parameter from extract
    set_errors = Bool(title=_('Set errors'),
                      description=_('A flag, when set, the contained widgets set error '
                                    'messages on calling extract()'),
                      default=True,
                      required=False)

    def update(self):
        """Setup widgets."""

    def extract(self):
        """Extract the values from the widgets and validate them.
        """

    def extract_raw(self):
        """Extract the RAW/string values from the widgets and validate them.
        """


class IWidgetEvent(Interface):
    """A simple widget event."""

    widget = Object(title=_('Widget'),
                    description=_('The widget for which the event was created.'),
                    schema=IWidget)


class IAfterWidgetUpdateEvent(IWidgetEvent):
    """An event sent out after the widget was updated."""
