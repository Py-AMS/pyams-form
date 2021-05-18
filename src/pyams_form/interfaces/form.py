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

"""PyAMS_form.interfaces.form module

Form related interfaces module.
"""

from zope.interface import Attribute, Interface
from zope.lifecycleevent import IObjectCreatedEvent
from zope.schema import ASCIILine, Bool, Choice, Dict, Field, Object, Text, TextLine, Tuple, URI

from pyams_form.interfaces import DISPLAY_MODE, IContentProviders, IFields, INPUT_MODE
from pyams_form.interfaces.button import IActions, IButtonHandlers, IButtons
from pyams_form.interfaces.widget import IWidgets


__docformat__ = 'restructuredtext'

from pyams_form import _


class IHandlerForm(Interface):
    """A form that stores the handlers locally."""

    handlers = Object(title=_('Handlers'),
                      description=_('A list of action handlers defined on the form.'),
                      schema=IButtonHandlers,
                      required=True)


class IActionForm(Interface):
    """A form that stores executable actions"""

    actions = Object(title=_('Actions'),
                     description=_('A list of actions defined on the form'),
                     schema=IActions,
                     required=True)

    refresh_actions = Bool(title=_('Refresh actions'),
                           description=_('A flag, when set, causes form actions to be '
                                         'updated again after their execution.'),
                           default=False,
                           required=True)


class IContextAware(Interface):
    """Offers a context attribute.

    For advanced uses, the widget will make decisions based on the context
    it is rendered in.
    """

    context = Field(title=_('Context'),
                    description=_('The context in which the widget is displayed.'),
                    required=True)

    ignore_context = Bool(title=_('Ignore Context'),
                          description=_('A flag, when set, forces the widget not to look at '
                                        'the context for a value.'),
                          default=False,
                          required=False)


class IFormAware(Interface):
    """Offers a form attribute.

    For advanced uses the widget will make decisions based on the form
    it is rendered in.
    """

    form = Field()


class IForm(Interface):
    """Form interface"""

    mode = Choice(title=_('Mode'),
                  description=_('The mode in which to render the widgets.'),
                  values=(INPUT_MODE, DISPLAY_MODE),
                  required=True)

    ignore_context = Bool(title=_('Ignore Context'),
                          description=_('If set the context is ignored to retrieve a value.'),
                          default=False,
                          required=True)

    ignore_request = Bool(title=_('Ignore Request'),
                          description=_('If set the request is ignored to retrieve a value.'),
                          default=False,
                          required=True)

    ignore_readonly = Bool(title=_('Ignore Readonly'),
                           description=_('If set then readonly fields will also be shown.'),
                           default=False,
                           required=True)

    ignore_required_on_extract = Bool(
        title=_('Ignore Required validation on extract'),
        description=_("If set then required fields will pass validation "
                      "on extract regardless whether they're filled in or not"),
        default=False,
        required=True)

    widgets = Object(title=_('Widgets'),
                     description=_('A widget manager containing the widgets to be used in '
                                   'the form.'),
                     schema=IWidgets)

    title = TextLine(title=_('Title'),
                     description=_('Main form title'),
                     required=False)

    legend = TextLine(title=_('Legend'),
                      description=_('A human readable text describing the form that can be '
                                    'used in the UI.'),
                      required=False)

    required_label = TextLine(title=_('Required label'),
                              description=_('A human readable text describing the form that can '
                                            'be used in the UI for rendering a required info '
                                            'legend.'),
                              required=False)

    prefix = ASCIILine(title=_('Prefix'),
                       description=_('The prefix of the form used to uniquely identify it.'),
                       default='form.')

    status = Text(title=_('Status'),
                  description=_('The status message of the form.'),
                  default=None,
                  required=False)

    def get_content(self):
        """Return the content to be displayed and/or edited."""

    def update_widgets(self, prefix=None):
        """Update the widgets for the form.

        This method is commonly called from the ``update()`` method and is
        mainly meant to be a hook for subclasses.

        Note that you can pass an argument for ``prefix`` to override
        the default value of ``"widgets."``.
        """

    def extract_data(self, set_errors=True):
        """Extract the data of the form.

        set_errors: needs to be passed to extract() and to sub-widgets"""

    def update(self):
        """Update the form."""

    def render(self):
        """Render the form."""

    def json(self):
        """Returns the form in json format"""


class IAJAXForm(IForm):
    """A form interface for handling AJAX calls"""

    def get_ajax_handler(self):
        """Get absolute URL of AJAX handler"""

    def get_form_options(self):
        """Get form options in JSON format"""

    def get_ajax_errors(self):
        """Get AJAX status"""

    def get_ajax_output(self, changes):
        """Get AJAX POST output in JSON"""


class IAJAXFormRenderer(Interface):
    """AJAX form JSON renderer"""

    def render(self, changes):
        """Render changes in JSON"""


class ISubForm(IForm):
    """A subform."""

    parent_form = Attribute("Parent form")


class IInnerForm(Interface):
    """Inner form marker interface"""


class IInnerSubForm(IInnerForm, ISubForm):
    """Inner sub-form interface

    Inner sub-forms are standard sub-forms, but which may be included dynamically
    into a given form by using named adapters.
    """


class IInnerTabForm(IInnerForm, ISubForm):
    """Inner tab-form interface

    Inner tab-forms are standard sub-forms, but which may be included dynamically
    into a given form by using named adapters.
    """


class IDisplayForm(IForm):
    """Mark a form as display form, used for templates."""


class IInputForm(Interface):
    """A form that is meant to process the input of the form controls."""

    action = URI(title=_('Action'),
                 description=_('The action defines the URI to which the form data are '
                               'sent.'),
                 required=True)

    name = TextLine(title=_('Name'),
                    description=_('The name of the form used to identify it.'),
                    required=False)

    # pylint: disable=invalid-name
    id = TextLine(title=_('Id'),
                  description=_('The id of the form used to identify it.'),
                  required=False)

    method = Choice(title=_('Method'),
                    description=_('The HTTP method used to submit the form.'),
                    values=('get', 'post'),
                    default='post',
                    required=False)

    enctype = ASCIILine(title=_('Encoding Type'),
                        description=_('The data encoding used to submit the data safely.'),
                        default='multipart/form-data',
                        required=False)

    accept_charset = ASCIILine(title=_('Accepted Character Sets'),
                               description=_('This is a list of character sets the server '
                                             'accepts. By default this is unknown.'),
                               required=False)

    accept = ASCIILine(title=_('Accepted Content Types'),
                       description=_('This is a list of content types the server can '
                                     'safely handle.'),
                       required=False)

    autocomplete = Choice(title=_("Form autocomplete"),
                          description=_("Enable or disable global form autocomplete"),
                          values=('on', 'off', 'new-password'),
                          required=False)

    # AJAX related form settings

    ajax_form_handler = TextLine(title="Name of AJAX form handler",
                                 required=False)

    ajax_form_options = Dict(title="AJAX form submit's data options",
                             required=False)

    ajax_form_target = TextLine(title="Form submit target",
                                description="Form content target, used for HTML and text content "
                                            "types",
                                required=False)

    ajax_form_callback = TextLine(title="AJAX submit callback",
                                  description="Name of a custom form submit callback",
                                  required=False)

    def get_ajax_handler(self):
        """Get absolute URL of AJAX handler"""

    def get_form_options(self):
        """Get form options in JSON format"""


class IAddForm(IForm):
    """A form to create and add a new component."""

    def create_and_add(self, data):
        """Call create and add.

        This method can be used for keep all attributes internal during create
        and add calls. On sucess we return the new created and added object.
        If something fails, we return None. The default handleAdd method will
        only set the _finished_add marker on sucess.
        """

    def create(self, data):
        """Create the new object using the given data.

        Returns the newly created object.
        """

    def add(self, obj):
        """Add the object somewhere."""

    def update_content(self, obj, data):
        """Update content after creation

        This is actually used to apply updates in subforms to newly created content.
        """


class IEditForm(IForm):
    """A form to edit data of a component."""

    def apply_changes(self, data):
        """Apply the changes to the content component."""


class IFieldsForm(IForm):
    """A form that is based upon defined fields."""

    fields = Object(title=_('Fields'),
                    description=_('A field manager describing the fields to be used for '
                                  'the form.'),
                    schema=IFields)


class IFieldsAndContentProvidersForm(IForm):
    """A form that is based upon defined fields and content providers"""

    content_providers = Object(title=_('Content providers'),
                               description=_(
                                   'A manager describing the content providers to be used for '
                                   'the form.'),
                               schema=IContentProviders)


class IButtonForm(IForm):
    """A form that is based upon defined buttons."""

    buttons = Object(title=_('Buttons'),
                     description=_('A button manager describing the buttons to be used for '
                                   'the form.'),
                     schema=IButtons)


class IGroupManager(IForm):
    """Groups manager interface"""

    groups = Tuple(title='Groups',
                   description=('Initially a collection of group classes, which are '
                                'converted to group instances when the form is '
                                'updated.'))


class IGroup(IGroupManager):
    """A group of fields/widgets within a form."""

    parent_form = Attribute("Parent form")


class IGroupForm(IGroupManager):
    """A form that supports groups."""


class IFormCreatedEvent(IObjectCreatedEvent):
    """Form created event interface"""

    request = Attribute("Form request")


class IDataExtractedEvent(Interface):
    """Event sent after data and status are extracted from widgets.
    """
    data = Attribute("Extracted form data. Usually, the widgets extract field names from "
                     "the request and return a dictionary of field names and field values.")
    errors = Attribute("Tuple of status providing IErrorViewSnippet.")
    form = Attribute("Form instance.")
