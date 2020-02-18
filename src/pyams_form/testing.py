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

lxml.doctestcompare.NOPARSE_MARKUP = register_optionflag('NOPARSE_MARKUP')

outputChecker = outputchecker.OutputChecker(
    patterns=(
        (re.compile("u('.*?')"), r"\1"),
        (re.compile("b('.*?')"), r"\1"),
        (re.compile("__builtin__"), r"builtins"),
        (re.compile("<type"), r"<class"),
        (re.compile("set\(\[(.*?)\]\)"), r"{\1}"),
    )
)


def TestRequest(**kwargs):
    """Test request helper"""
    params = kwargs.get('params')
    if params:
        copy = {}
        for k, v in params.items():
            if k.endswith(':list'):
                k = k.split(':', 1)[0]
            copy[k] = v
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

        return super(TestingFileUploadDataConverter, self).to_field_value(value)


@implementer(IInteraction)
@provider(ISecurityPolicy)
class SimpleSecurityPolicy(object):
    """Allow all access."""

    loggedIn = False
    allowedPermissions = ()

    def __init__(self, loggedIn=False, allowedPermissions=()):
        self.loggedIn = loggedIn
        self.allowedPermissions = allowedPermissions + (checker.CheckerPublic,)

    def __call__(self, *participations):
        self.participations = []
        return self

    def checkPermission(self, permission, object):
        if self.loggedIn:
            if permission in self.allowedPermissions:
                return True
        return False


def get_path(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)


def text_of_with_optional_title(node, addTitle=False, showTooltips=False):
    if isinstance(node, (list, tuple)):
        return '\n'.join(text_of_with_optional_title(child, addTitle, showTooltips)
                         for child in node)
    text = []
    if node is None:
        return None

    if node.tag == 'br':
        return '\n'
    if node.tag == 'input':
        if addTitle:
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
        else:
            return '%s[%s]' % (title, node.get('value') or '')
    if node.tag == 'textarea':
        if addTitle:
            title = node.get('name') or ''
            title += ' '
            text.append(title)
    if node.tag == 'select':
        if addTitle:
            title = node.get('name') or ''
            title += ' '
        else:
            title = ''
        option = node.find('option[@selected]')
        return '%s[%s]' % (title, option.text if option is not None
                                  else '[    ]')
    if node.tag == 'li':
        text.append('*')
    if node.tag == 'script':
        return

    if node.text and node.text.strip():
        text.append(node.text.strip())

    for n, child in enumerate(node):
        s = text_of_with_optional_title(child, addTitle, showTooltips)
        if s:
            text.append(s)
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
    listOfObject = List(title="My list field",
                        value_type=Object(
                            title='my object widget',
                            schema=IMySubObjectMulti),
                        )
    name = TextLine(title='name')


@implementer(IMyMultiObject)
class MyMultiObject:
    """Multi-object class"""
    listOfObject = FieldProperty(IMyMultiObject['listOfObject'])
    name = FieldProperty(IMyMultiObject['name'])

    def __init__(self, name='', listOfObject=None):
        self.listOfObject = listOfObject
        self.name = name


class IntegrationBase:
    """Integration base"""
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self):
        items = list(self.__dict__.items())
        items.sort()
        return ("<" + self.__class__.__name__+"\n  "
            + "\n  ".join(["%s: %s" % (key, pprint.pformat(value))
            for key, value in items]) + ">")


class IObjectWidgetSingleSubIntegration(Interface):
    singleInt = Int(
        title='Int label')
    singleBool = Bool(
        title='Bool label')
    singleChoice = Choice(
        title='Choice label',
        values=('one', 'two', 'three'))
    singleChoiceOpt = Choice(
        title='ChoiceOpt label',
        values=('four', 'five', 'six'),
        required=False)
    singleTextLine = TextLine(
        title='TextLine label')
    singleDate = Date(
        title='Date label')
    singleReadOnly = TextLine(
        title='ReadOnly label',
        readonly=True)


@implementer(IObjectWidgetSingleSubIntegration)
class ObjectWidgetSingleSubIntegration(IntegrationBase):

    singleInt = FieldProperty(IObjectWidgetSingleSubIntegration['singleInt'])
    singleBool = FieldProperty(IObjectWidgetSingleSubIntegration['singleBool'])
    singleChoice = FieldProperty(IObjectWidgetSingleSubIntegration['singleChoice'])
    singleChoiceOpt = FieldProperty(
        IObjectWidgetSingleSubIntegration['singleChoiceOpt'])
    singleTextLine = FieldProperty(
        IObjectWidgetSingleSubIntegration['singleTextLine'])
    singleDate = FieldProperty(IObjectWidgetSingleSubIntegration['singleDate'])
    singleReadOnly = FieldProperty(
        IObjectWidgetSingleSubIntegration['singleReadOnly'])


class IObjectWidgetSingleIntegration(Interface):
    subobj = Object(
        title='Object label',
        schema=IObjectWidgetSingleSubIntegration
    )


@implementer(IObjectWidgetSingleIntegration)
class ObjectWidgetSingleIntegration:

    subobj = FieldProperty(IObjectWidgetSingleIntegration['subobj'])


class IObjectWidgetMultiSubIntegration(Interface):
    multiInt = Int(title='Int label')
    multiBool = Bool(title='Bool label')
    multiChoice = Choice(title='Choice label',
                         values=('one', 'two', 'three'))
    multiChoiceOpt = Choice(title='ChoiceOpt label',
                            values=('four', 'five', 'six'),
                            required=False)
    multiTextLine = TextLine(title='TextLine label')
    multiDate = Date(title='Date label')


@implementer(IObjectWidgetMultiSubIntegration)
class ObjectWidgetMultiSubIntegration(IntegrationBase):

    multiInt = FieldProperty(IObjectWidgetMultiSubIntegration['multiInt'])
    multiBool = FieldProperty(IObjectWidgetMultiSubIntegration['multiBool'])
    multiChoice = FieldProperty(IObjectWidgetMultiSubIntegration['multiChoice'])
    multiChoiceOpt = FieldProperty(
        IObjectWidgetMultiSubIntegration['multiChoiceOpt'])
    multiTextLine = FieldProperty(
        IObjectWidgetMultiSubIntegration['multiTextLine'])
    multiDate = FieldProperty(IObjectWidgetMultiSubIntegration['multiDate'])


class IObjectWidgetMultiIntegration(Interface):
    subobj = Object(
        title='Object label',
        schema=IObjectWidgetMultiSubIntegration
    )


@implementer(IObjectWidgetMultiIntegration)
class ObjectWidgetMultiIntegration:

    subobj = FieldProperty(IObjectWidgetMultiIntegration['subobj'])


class IMultiWidgetListIntegration(Interface):
    listOfInt = List(
        title="ListOfInt label",
        value_type=Int(
            title='Int label'),
    )
    listOfBool = List(
        title="ListOfBool label",
        value_type=Bool(
            title='Bool label'),
    )
    listOfChoice = List(
        title="ListOfChoice label",
        value_type=Choice(
            title='Choice label',
            values=('one', 'two', 'three')
            ),
    )
    listOfTextLine = List(
        title="ListOfTextLine label",
        value_type=TextLine(
            title='TextLine label'),
    )
    listOfDate = List(
        title="ListOfDate label",
        value_type=Date(
            title='Date label'),
    )
    listOfObject = List(
        title="ListOfObject label",
        value_type=Object(
            title='Object label',
            schema=IObjectWidgetMultiSubIntegration),
    )


@implementer(IMultiWidgetListIntegration)
class MultiWidgetListIntegration(IntegrationBase):

    listOfInt = FieldProperty(IMultiWidgetListIntegration['listOfInt'])
    listOfBool = FieldProperty(IMultiWidgetListIntegration['listOfBool'])
    listOfChoice = FieldProperty(IMultiWidgetListIntegration['listOfChoice'])
    listOfTextLine = FieldProperty(IMultiWidgetListIntegration['listOfTextLine'])
    listOfDate = FieldProperty(IMultiWidgetListIntegration['listOfDate'])
    listOfObject = FieldProperty(IMultiWidgetListIntegration['listOfObject'])


class IMultiWidgetDictIntegration(Interface):
    dictOfInt = Dict(
        title="DictOfInt label",
        key_type=Int(
            title='Int key'),
        value_type=Int(
            title='Int label'),
    )
    dictOfBool = Dict(
        title="DictOfBool label",
        key_type=Bool(
            title='Bool key'),
        value_type=Bool(
            title='Bool label'),
    )
    dictOfChoice = Dict(
        title="DictOfChoice label",
        key_type=Choice(
            title='Choice key',
            values=('key1', 'key2', 'key3')
            ),
        value_type=Choice(
            title='Choice label',
            values=('one', 'two', 'three')
            ),
    )
    dictOfTextLine = Dict(
        title="DictOfTextLine label",
        key_type=TextLine(
            title='TextLine key'),
        value_type=TextLine(
            title='TextLine label'),
    )
    dictOfDate = Dict(
        title="DictOfDate label",
        key_type=Date(
            title='Date key'),
        value_type=Date(
            title='Date label'),
    )
    dictOfObject = Dict(
        title="DictOfObject label",
        key_type=TextLine(
            title='Object key'),
        value_type=Object(
            title='Object label',
            schema=IObjectWidgetMultiSubIntegration),
    )


@implementer(IMultiWidgetDictIntegration)
class MultiWidgetDictIntegration(IntegrationBase):

    dictOfInt = FieldProperty(IMultiWidgetDictIntegration['dictOfInt'])
    dictOfBool = FieldProperty(IMultiWidgetDictIntegration['dictOfBool'])
    dictOfChoice = FieldProperty(IMultiWidgetDictIntegration['dictOfChoice'])
    dictOfTextLine = FieldProperty(IMultiWidgetDictIntegration['dictOfTextLine'])
    dictOfDate = FieldProperty(IMultiWidgetDictIntegration['dictOfDate'])
    dictOfObject = FieldProperty(IMultiWidgetDictIntegration['dictOfObject'])


def setup_form_defaults(registry):
    # Generic utilities
    registry.registerUtility(PyAMSSkin, provided=ISkin, name=PYAMS_BASE_SKIN_NAME)


import sys
if sys.argv[-1].endswith('/bin/test'):

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

        def add(self, object):
            self.context[object.name.lower()] = object


    class ITestEditForm(IAJAXForm):
        """Test edit form marker interface"""


    @ajax_form_config(name='test-edit-form.html', context=IAJAXTestContent,
                      ajax_implements=ITestEditForm, ajax_method=None, ajax_xhr=None)
    class TestEditForm(EditForm):
        """Test edit form"""
        fields = field.Fields(IAJAXTestContent)
