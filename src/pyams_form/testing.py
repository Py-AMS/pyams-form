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

"""PyAMS_form.testing module

This module provides several testing helpers.
"""

import base64
import os
import pprint
import re
import sys
from doctest import register_optionflag

import lxml
from pyramid.testing import DummyRequest
from zope.component import adapts
from zope.i18n.locales import locales
from zope.interface import Interface, implementer, provider
from zope.schema import Bool, Choice, Date, Dict, Int, List, Object, TextLine
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import IBytes
from zope.security import checker
from zope.security.interfaces import IInteraction, ISecurityPolicy

from pyams_form import browser, field, outputchecker
from pyams_form.ajax import ajax_form_config
from pyams_form.converter import FileUploadDataConverter
from pyams_form.form import AddForm, EditForm
from pyams_form.interfaces.form import IAJAXForm
from pyams_form.interfaces.widget import IFileWidget
from pyams_layer.interfaces import ISkin, PYAMS_BASE_SKIN_NAME
from pyams_layer.skin import PyAMSSkin, apply_skin


__docformat__ = 'restructuredtext'


if sys.argv[-1].endswith('/bin/test'):

    lxml.doctestcompare.NOPARSE_MARKUP = register_optionflag('NOPARSE_MARKUP')

    OUTPUT_CHECKER = outputchecker.OutputChecker(
        patterns=(
            (re.compile(r"u('.*?')"), r"\1"),
            (re.compile(r"b('.*?')"), r"\1"),
            (re.compile(r"__builtin__"), r"builtins"),
            (re.compile(r"<type"), r"<class"),
            (re.compile(r"set\(\[(.*?)\]\)"), r"{\1}"),
        )
    )

    INT_LABEL = 'Int label'
    BOOL_LABEL = 'Bool label'
    CHOICE_LABEL = 'Choice label'
    CHOICE_OPT_LABEL = 'ChoiceOpt label'
    TEXTLINE_LABEL = 'TextLine label'
    DATE_LABEL = 'Date label'
    READONLY_LABEL = 'ReadOnly label'
    OBJECT_LABEL = 'Object label'


    def TestRequest(**kwargs):  # pylint: disable=invalid-name
        """Test request helper"""
        params = kwargs.get('params')
        if params:
            copy = params.__class__()
            for key, value in params.items():
                if key.endswith(':list'):
                    key = key.split(':', 1)[0]
                copy[key] = value
            kwargs['params'] = copy
        request = DummyRequest(**kwargs)
        request.locale = locales.getLocale('en')
        apply_skin(request, PYAMS_BASE_SKIN_NAME)
        return request


    class TestingFileUploadDataConverter(FileUploadDataConverter):
        """A special file upload data converter that works with testing."""

        adapts(IBytes, IFileWidget)

        def to_field_value(self, value):
            if value is None or value == '':
                value = self.widget.request.params.get(self.widget.name + '.testing', '')
                encoding = self.widget.request.params.get(
                    self.widget.name + '.encoding', 'plain')

                # allow for the case where the file contents are base64 encoded.
                if encoding == 'base64':
                    value = base64.b64decode(value)
                self.widget.request.POST[self.widget.name] = value

            return super().to_field_value(value)


    @implementer(IInteraction)
    @provider(ISecurityPolicy)
    class SimpleSecurityPolicy:
        """Allow all access."""

        logged_in = False
        allowed_permissions = ()
        participations = None

        def __init__(self, logged_in=False, allowed_permissions=()):
            self.logged_in = logged_in
            self.allowed_permissions = allowed_permissions + (checker.CheckerPublic,)

        def __call__(self, *participations):
            self.participations = []
            return self

        def checkPermission(self, permission, object):
            # pylint: disable=invalid-name,unused-argument,redefined-builtin
            """Check given permission"""
            if self.logged_in:
                if permission in self.allowed_permissions:
                    return True
            return False


    def get_path(filename):
        """Get full path of given filename"""
        return os.path.join(os.path.dirname(browser.__file__), filename)


    def text_of_with_optional_title(node, add_title=False, show_tooltips=False):
        # pylint: disable=too-many-branches,too-many-return-statements
        """Get node text with title"""
        if isinstance(node, (list, tuple)):
            return '\n'.join(text_of_with_optional_title(child, add_title, show_tooltips)
                             for child in node)
        text = []
        if node is None:
            return None

        if node.tag == 'br':
            return '\n'
        if node.tag == 'input':
            if add_title:
                title = node.get('name') or ''
                title += ' '
            else:
                title = ''
            if node.get('type') == 'radio':
                return title + ('(O)' if node.get('checked') else '( )')
            if node.get('type') == 'checkbox':
                return title + ('[x]' if node.get('checked') else '[ ]')
            if node.get('type') == 'hidden':
                return ''
            return '%s[%s]' % (title, node.get('value') or '')
        if node.tag == 'textarea':
            if add_title:
                title = node.get('name') or ''
                title += ' '
                text.append(title)
        if node.tag == 'select':
            if add_title:
                title = node.get('name') or ''
                title += ' '
            else:
                title = ''
            option = node.find('option[@selected]')
            return '%s[%s]' % (title, option.text if option is not None else '[    ]')
        if node.tag == 'li':
            text.append('*')
        if node.tag == 'script':
            return None

        if node.text and node.text.strip():
            text.append(node.text.strip())

        for _index, child in enumerate(node):
            txt = text_of_with_optional_title(child, add_title, show_tooltips)
            if txt:
                text.append(txt)
            if child.tail and child.tail.strip():
                text.append(child.tail)
        text = ' '.join(text).strip()
        # 'foo<br>bar' ends up as 'foo \nbar' due to the algorithm used above
        text = text.replace(' \n', '\n').replace('\n ', '\n').replace('\n\n', '\n')
        if u'\xA0' in text:
            # don't just .replace, that'll sprinkle my tests with u''
            text = text.replace(u'\xA0', ' ')  # nbsp -> space
        if node.tag == 'li':
            text += '\n'
        if node.tag == 'div':
            text += '\n'
        return text


    def text_of(node):
        """Return the contents of an HTML node as text.

        Useful for functional tests, e.g. ::

            print map(textOf, browser.etree.xpath('.//td'))

        """
        return text_of_with_optional_title(node, False)


    def plain_text(content, xpath=None):
        """Get text of given node"""
        root = lxml.html.fromstring(content)
        if xpath is not None:
            nodes = root.xpath(xpath)
            joinon = '\n'
        else:
            nodes = root
            joinon = ''
        text = joinon.join(map(text_of, nodes))
        lines = [l.strip() for l in text.splitlines()]
        text = '\n'.join(lines)
        return text


    def get_submit_values(content):
        """Get submit values from content"""
        root = lxml.html.fromstring(content)
        form = root.forms[0]
        values = dict(form.form_values())
        return values


    #
    # classes required by ObjectWidget tests
    #

    class IMySubObject(Interface):
        """Sub-object interface"""
        foofield = Int(title="My foo field",
                       default=1111,
                       max=9999,
                       required=True)
        barfield = Int(title="My dear bar",
                       default=2222,
                       required=False)


    @implementer(IMySubObject)
    class MySubObject:
        """Sub-object class"""
        foofield = FieldProperty(IMySubObject['foofield'])
        barfield = FieldProperty(IMySubObject['barfield'])


    class IMySecond(Interface):
        """Second interface"""
        subfield = Object(title="Second-subobject",
                          schema=IMySubObject)
        moofield = TextLine(title="Something")


    @implementer(IMySecond)
    class MySecond:
        """Second object class"""
        subfield = FieldProperty(IMySecond['subfield'])
        moofield = FieldProperty(IMySecond['moofield'])


    class IMyObject(Interface):
        """Object interface"""
        subobject = Object(title='my object', schema=IMySubObject)
        name = TextLine(title='name')


    @implementer(IMyObject)
    class MyObject:
        """Object class"""

        def __init__(self, name='', subobject=None):
            self.subobject = subobject
            self.name = name


    class IMyComplexObject(Interface):
        """Complex object interface"""
        subobject = Object(title='my object', schema=IMySecond)
        name = TextLine(title='name')


    class IMySubObjectMulti(Interface):
        """Multi sub-object interface"""
        foofield = Int(title="My foo field",
                       default=None,  # default is None here!
                       max=9999,
                       required=True)
        barfield = Int(title="My dear bar",
                       default=2222,
                       required=False)


    @implementer(IMySubObjectMulti)
    class MySubObjectMulti:
        """Multi sub-object class"""
        foofield = FieldProperty(IMySubObjectMulti['foofield'])
        barfield = FieldProperty(IMySubObjectMulti['barfield'])


    class IMyMultiObject(Interface):
        """Multi-object interface"""
        list_of_objects = List(title="My list field",
                               value_type=Object(
                                   title='my object widget',
                                   schema=IMySubObjectMulti))
        name = TextLine(title='name')


    @implementer(IMyMultiObject)
    class MyMultiObject:
        """Multi-object class"""
        list_of_objects = FieldProperty(IMyMultiObject['list_of_objects'])
        name = FieldProperty(IMyMultiObject['name'])

        def __init__(self, name='', list_of_objects=None):
            self.list_of_objects = list_of_objects
            self.name = name


    class IntegrationBase:
        """Integration base"""
        def __init__(self, **kw):
            for key, value in kw.items():
                setattr(self, key, value)

        def __repr__(self):
            items = list(self.__dict__.items())
            items.sort()
            return ("<" + self.__class__.__name__+"\n  " + "\n  ".join(
                ["%s: %s" % (key, pprint.pformat(value)) for key, value in items]) + ">")


    class IObjectWidgetSingleSubIntegration(Interface):
        """Sub-integration interface"""
        single_int = Int(title=INT_LABEL)
        single_bool = Bool(title=BOOL_LABEL)
        single_choice = Choice(title=CHOICE_LABEL,
                               values=('one', 'two', 'three'))
        single_choice_opt = Choice(title=CHOICE_OPT_LABEL,
                                   values=('four', 'five', 'six'),
                                   required=False)
        single_textline = TextLine(title=TEXTLINE_LABEL)
        single_date = Date(title=DATE_LABEL)
        single_readonly = TextLine(title=READONLY_LABEL,
                                   readonly=True)


    @implementer(IObjectWidgetSingleSubIntegration)
    class ObjectWidgetSingleSubIntegration(IntegrationBase):
        """Sub-integration class"""
        single_int = FieldProperty(IObjectWidgetSingleSubIntegration['single_int'])
        single_bool = FieldProperty(IObjectWidgetSingleSubIntegration['single_bool'])
        single_choice = FieldProperty(IObjectWidgetSingleSubIntegration['single_choice'])
        single_choice_opt = FieldProperty(
            IObjectWidgetSingleSubIntegration['single_choice_opt'])
        single_textline = FieldProperty(
            IObjectWidgetSingleSubIntegration['single_textline'])
        single_date = FieldProperty(IObjectWidgetSingleSubIntegration['single_date'])
        single_readonly = FieldProperty(
            IObjectWidgetSingleSubIntegration['single_readonly'])


    class IObjectWidgetSingleIntegration(Interface):
        """Single integration interface"""
        subobj = Object(title=OBJECT_LABEL,
                        schema=IObjectWidgetSingleSubIntegration)


    @implementer(IObjectWidgetSingleIntegration)
    class ObjectWidgetSingleIntegration:
        """Single integration class"""
        subobj = FieldProperty(IObjectWidgetSingleIntegration['subobj'])


    class IObjectWidgetMultiSubIntegration(Interface):
        """Multi sub-integration interface"""
        multi_int = Int(title=INT_LABEL)
        multi_bool = Bool(title=BOOL_LABEL)
        multi_choice = Choice(title=CHOICE_LABEL,
                              values=('one', 'two', 'three'))
        multi_choice_opt = Choice(title=CHOICE_OPT_LABEL,
                                  values=('four', 'five', 'six'),
                                  required=False)
        multi_textline = TextLine(title=TEXTLINE_LABEL)
        multi_date = Date(title=DATE_LABEL)


    @implementer(IObjectWidgetMultiSubIntegration)
    class ObjectWidgetMultiSubIntegration(IntegrationBase):
        """Multi sub-integration class"""
        multi_int = FieldProperty(IObjectWidgetMultiSubIntegration['multi_int'])
        multi_bool = FieldProperty(IObjectWidgetMultiSubIntegration['multi_bool'])
        multi_choice = FieldProperty(IObjectWidgetMultiSubIntegration['multi_choice'])
        multi_choice_opt = FieldProperty(
            IObjectWidgetMultiSubIntegration['multi_choice_opt'])
        multi_textline = FieldProperty(
            IObjectWidgetMultiSubIntegration['multi_textline'])
        multi_date = FieldProperty(IObjectWidgetMultiSubIntegration['multi_date'])


    class IObjectWidgetMultiIntegration(Interface):
        """Multi-integration interface"""
        subobj = Object(title=OBJECT_LABEL,
                        schema=IObjectWidgetMultiSubIntegration)


    @implementer(IObjectWidgetMultiIntegration)
    class ObjectWidgetMultiIntegration:
        """Multi-integration class"""
        subobj = FieldProperty(IObjectWidgetMultiIntegration['subobj'])


    class IMultiWidgetListIntegration(Interface):
        """Multi-list interface"""
        list_of_int = List(title="ListOfInt label",
                           value_type=Int(title=INT_LABEL))
        list_of_bool = List(title="ListOfBool label",
                            value_type=Bool(title=BOOL_LABEL))
        list_of_choice = List(title="ListOfChoice label",
                              value_type=Choice(title=CHOICE_LABEL,
                                                values=('one', 'two', 'three')))
        list_of_textline = List(title="ListOfTextLine label",
                                value_type=TextLine(title=TEXTLINE_LABEL), )
        list_of_date = List(title="ListOfDate label",
                            value_type=Date(title=DATE_LABEL))
        list_of_objects = List(title="ListOfObject label",
                               value_type=Object(title=OBJECT_LABEL,
                                                 schema=IObjectWidgetMultiSubIntegration))


    @implementer(IMultiWidgetListIntegration)
    class MultiWidgetListIntegration(IntegrationBase):
        """Mulit-list class"""
        list_of_int = FieldProperty(IMultiWidgetListIntegration['list_of_int'])
        list_of_bool = FieldProperty(IMultiWidgetListIntegration['list_of_bool'])
        list_of_choice = FieldProperty(IMultiWidgetListIntegration['list_of_choice'])
        list_of_textline = FieldProperty(IMultiWidgetListIntegration['list_of_textline'])
        list_of_date = FieldProperty(IMultiWidgetListIntegration['list_of_date'])
        list_of_objects = FieldProperty(IMultiWidgetListIntegration['list_of_objects'])


    class IMultiWidgetDictIntegration(Interface):
        """Multi-dict interface"""
        dict_of_int = Dict(title="DictOfInt label",
                           key_type=Int(title='Int key'),
                           value_type=Int(title=INT_LABEL))
        dict_of_bool = Dict(title="DictOfBool label",
                            key_type=Bool(title='Bool key'),
                            value_type=Bool(title=BOOL_LABEL))
        dict_of_choice = Dict(title="DictOfChoice label",
                              key_type=Choice(title='Choice key',
                                              values=('key1', 'key2', 'key3')),
                              value_type=Choice(title=CHOICE_LABEL,
                                                values=('one', 'two', 'three')))
        dict_of_textline = Dict(title="DictOfTextLine label",
                                key_type=TextLine(title='TextLine key'),
                                value_type=TextLine(title=TEXTLINE_LABEL))
        dict_of_date = Dict(title="DictOfDate label",
                            key_type=Date(title='Date key'),
                            value_type=Date(title=DATE_LABEL))
        dict_of_objects = Dict(title="DictOfObject label",
                               key_type=TextLine(title='Object key'),
                               value_type=Object(title=OBJECT_LABEL,
                                                 schema=IObjectWidgetMultiSubIntegration))


    @implementer(IMultiWidgetDictIntegration)
    class MultiWidgetDictIntegration(IntegrationBase):
        """Multi-dict class"""
        dict_of_int = FieldProperty(IMultiWidgetDictIntegration['dict_of_int'])
        dict_of_bool = FieldProperty(IMultiWidgetDictIntegration['dict_of_bool'])
        dict_of_choice = FieldProperty(IMultiWidgetDictIntegration['dict_of_choice'])
        dict_of_textline = FieldProperty(IMultiWidgetDictIntegration['dict_of_textline'])
        dict_of_date = FieldProperty(IMultiWidgetDictIntegration['dict_of_date'])
        dict_of_objects = FieldProperty(IMultiWidgetDictIntegration['dict_of_objects'])


    def setup_form_defaults(registry):
        """Setup form default settings"""
        # Generic utilities
        registry.registerUtility(PyAMSSkin, provided=ISkin, name=PYAMS_BASE_SKIN_NAME)


    class IAJAXTestContent(Interface):
        """AJAX test content interface"""
        name = TextLine(title="Name")
        value = Int(title="Value")


    @implementer(IAJAXTestContent)
    class AJAXTestContent:
        """AJAX test content"""
        name = FieldProperty(IAJAXTestContent['name'])
        value = FieldProperty(IAJAXTestContent['value'])

        def __init__(self, **data):
            self.name = data.get('name')
            self.value = data.get('value')


    class ITestAddForm(IAJAXForm):
        """Test add form marker interface"""


    @ajax_form_config(name='test-add-form.html',
                      ajax_implements=ITestAddForm, ajax_method=None, ajax_xhr=None)
    class TestAddForm(AddForm):
        """Test add form"""
        fields = field.Fields(IAJAXTestContent)

        def create(self, data):
            return AJAXTestContent(**data)

        def add(self, obj):  # pylint: disable=redefined-builtin
            self.context[obj.name.lower()] = obj


    class ITestEditForm(IAJAXForm):
        """Test edit form marker interface"""


    @ajax_form_config(name='test-edit-form.html', context=IAJAXTestContent,
                      ajax_implements=ITestEditForm, ajax_method=None, ajax_xhr=None)
    class TestEditForm(EditForm):
        """Test edit form"""
        fields = field.Fields(IAJAXTestContent)
