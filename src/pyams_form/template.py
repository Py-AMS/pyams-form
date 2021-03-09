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

"""PyAMS_form.template module

Widgets templates management module.
"""

import inspect
import os

import venusian
from pyramid.config import ConfigurationError
from pyramid_chameleon.interfaces import IChameleonTranslate
from zope.interface import Interface, directlyProvides

from pyams_form.interfaces import INPUT_MODE, IWidgetLayoutTemplate
from pyams_layer.interfaces import IFormLayer
from pyams_template.interfaces import IPageTemplate
from pyams_template.template import TemplateFactory, ViewTemplate
from pyams_utils.registry import get_pyramid_registry, query_utility


__docformat__ = 'restructuredtext'


class WidgetTemplateFactory(TemplateFactory):
    """Widget template factory"""

    def __call__(self, context, request, form, field, widget):
        # pylint: disable=too-many-arguments
        return self.template


class WidgetTemplate(ViewTemplate):
    """Widget template class"""

    def __init__(self, provides):
        super().__init__(provides)

    def __call__(self, instance, *args, **keywords):
        request = instance.request
        registry = request.registry
        template = registry.getMultiAdapter(
            (request.context, request, instance.form, instance.field, instance),
            self.provides, name=instance.mode)

        keywords.update({
            'context': instance.context,
            'request': instance.request,
            'view': instance,
            'translate': query_utility(IChameleonTranslate)
        })
        return template(*args, **keywords)


class GetWidgetTemplate(WidgetTemplate):
    """Get widget template"""

    def __init__(self):
        super().__init__(IPageTemplate)


get_widget_template = GetWidgetTemplate  # pylint: disable=invalid-name


class GetWidgetLayout(WidgetTemplate):
    """Layout template getter class"""

    def __init__(self):
        super().__init__(IWidgetLayoutTemplate)


get_widget_layout = GetWidgetLayout  # pylint: disable=invalid-name


def register_widget_template(template, widget, settings, provides, registry=None):
    """Register new widget template"""
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    content_type = settings.get('content_type', 'text/html')
    macro = settings.get('macro')
    factory = WidgetTemplateFactory(template, content_type, macro)
    provides = settings.get('provides', provides)
    directlyProvides(factory, provides)

    # check context
    required = (
        settings.get('context', Interface),
        settings.get('layer', IFormLayer),
        settings.get('form', None),
        settings.get('field', None),
        widget
    )
    # update registry
    if registry is None:
        registry = settings.get('registry')
        if registry is None:
            registry = get_pyramid_registry()
    registry.registerAdapter(factory, required, provides, settings.get('mode', INPUT_MODE))


class base_widget_template_config:  # pylint: disable=invalid-name
    """Class decorator used to declare a widget template"""

    venusian = venusian  # for testing injection
    interface = IPageTemplate  # template interface

    def __init__(self, **settings):
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings['for_']
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        settings = self.__dict__.copy()

        def callback(context, name, widget):  # pylint: disable=unused-argument
            template = os.path.join(os.path.dirname(inspect.getfile(inspect.getmodule(widget))),
                                    settings.get('template'))
            if not os.path.isfile(template):
                raise ConfigurationError("No such file", template)
            # check registry
            registry = settings.get('registry')
            if registry is None:
                config = context.config.with_package(info.module)  # pylint: disable=no-member
                registry = config.registry
            register_widget_template(template, widget, settings, self.interface, registry)

        info = self.venusian.attach(wrapped, callback, category='pyams_form')
        if info.scope == 'class':  # pylint: disable=no-member
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo  # pylint: disable=no-member
        return wrapped


class widget_template_config(base_widget_template_config):  # pylint: disable=invalid-name
    """Class decorator used to declare a widget template"""


def override_widget_template(widget, **settings):
    """Override template for a given widget

    This function can be used to override a widget template without using ZCML.
    Settings are the same as for @widget_template_config decorator.
    """
    template = settings.get('template', '')
    if not template:
        raise ConfigurationError("No template specified")
    if not template.startswith('/'):
        stack = inspect.stack()[1]
        template = os.path.join(os.path.dirname(inspect.getfile(inspect.getmodule(stack[0]))),
                                template)
    register_widget_template(template, widget, settings, IPageTemplate)


class widget_layout_config(base_widget_template_config):  # pylint: disable=invalid-name
    """Class decorator used to declare a layout template"""

    interface = IWidgetLayoutTemplate  # template interface


def override_widget_layout(widget, **settings):
    """Override layout template for a given class

    This function can be used to override a class layout template without using ZCML.
    Settings are the same as for @layout_config decorator.
    """
    template = settings.get('template', '')
    if not template:
        raise ConfigurationError("No template specified")
    if not template.startswith('/'):
        stack = inspect.stack()[1]
        template = os.path.join(os.path.dirname(inspect.getfile(inspect.getmodule(stack[0]))),
                                template)
    register_widget_template(template, widget, settings, IWidgetLayoutTemplate)
