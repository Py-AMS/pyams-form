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

"""PyAMS_form.ajex module

This module is declaring forms which can be used in an AJAX context, where
forms are submitted using an XMLHTTPRequest and where response is made of
JSON messages.
"""

import logging

import venusian
from pyramid.config import ConfigurationError
from pyramid.events import subscriber
from pyramid.interfaces import IRequest
from zope.component import queryMultiAdapter
from zope.interface import Interface, alsoProvides, implementer

from pyams_form.events import FormCreatedEvent
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.error import IAJAXErrorsRenderer, IErrorViewSnippet, IMultipleErrors
from pyams_form.interfaces.form import IAJAXForm, IAJAXFormRenderer, IAddForm, IForm, \
    IFormCreatedEvent
from pyams_layer.interfaces import IFormLayer
from pyams_pagelet.interfaces import IPagelet
from pyams_pagelet.pagelet import Pagelet
from pyams_utils.adapter import adapter_config
from pyams_utils.dict import merge_dict
from pyams_utils.list import boolean_iter


__docformat__ = 'restructuredtext'

from pyams_form import _  # pylint: disable=ungrouped-imports

LOGGER = logging.getLogger('PyAMS (form)')


@implementer(IAJAXForm)
class AJAXForm:
    """A form mix-in class used to support form's submit through AJAX

    You don't have to inherit from AJAXForm or one of it's subclasses; they are used
    automatically when using the "ajax_form_config" class decorator.
    """

    def __call__(self):
        registry = self.request.registry  # pylint: disable=no-member
        registry.notify(FormCreatedEvent(self))
        self.update()  # pylint: disable=no-member
        has_errors, errors = boolean_iter(self.get_errors())  # pylint: disable=no-member
        if has_errors:
            return self.get_ajax_errors(errors)
        return self.get_ajax_output(self.finished_state.get('changes'))  # pylint: disable=no-member

    def get_ajax_errors(self, errors):
        """Get AJAX errors"""
        request = self.request  # pylint: disable=no-member
        registry = request.registry
        # pylint: disable=no-member
        renderer = registry.getMultiAdapter((self.context, request, self),
                                            IAJAXErrorsRenderer)
        return renderer.render(errors)

    def get_ajax_output(self, changes):
        """Get AJAX status and changes output in JSON"""
        raise NotImplementedError


@subscriber(IFormCreatedEvent, context_selector=IAJAXForm)
def handle_new_ajax_form(event):
    """Handle new AJAX form"""
    form = event.object
    impl = getattr(form, '__ajax_interfaces__', None)
    if impl is not None:
        alsoProvides(form, *impl)


class AJAXAddForm(AJAXForm):
    """AJAX add form mix-in class"""

    no_changes_message = _("No data was created.")

    def get_ajax_output(self, changes):
        request = self.request  # pylint: disable=no-member
        # pylint: disable=no-member
        renderer = None
        if 'action' in self.finished_state:
            name = self.finished_state['action'].field.getName()
            renderer = queryMultiAdapter((self.context, request, self),
                                         IAJAXFormRenderer, name=name)
        if renderer is None:
            renderer = queryMultiAdapter((self.context, request, self),
                                         IAJAXFormRenderer)
        if renderer is not None:
            result = renderer.render(changes)
            if result:
                return result
        if not changes:
            return {
                'status': 'info',
                'message': request.localizer.translate(self.no_changes_message)
            }
        return {
            'status': 'reload'
        }


class AJAXEditForm(AJAXForm):
    """AJAX edit form mix-in class"""

    def get_ajax_output(self, changes):
        request = self.request  # pylint: disable=no-member
        translate = request.localizer.translate
        # pylint: disable=no-member
        result = {}
        renderer = None
        if 'action' in self.finished_state:
            name = self.finished_state['action'].field.getName()
            renderer = queryMultiAdapter((self.context, request, self),
                                         IAJAXFormRenderer, name=name)
        if renderer is None:
            renderer = queryMultiAdapter((self.context, request, self),
                                         IAJAXFormRenderer)
        if renderer is not None:
            result = renderer.render(changes) or {}
        status = ''
        message = ''
        if result:
            status = result.get('status')
            message = result.get('message')
        if not changes:
            if not status:
                result['status'] = 'info'
            if not message:
                result['message'] = translate(self.no_changes_message)
        else:
            if not status:
                result['status'] = status = 'success'
            if not message:
                if status == 'success':
                    result['message'] = translate(self.success_message)
        return result


@adapter_config(required=(None, IFormLayer, IAJAXForm), provides=IAJAXFormRenderer)
class AJAXFormRenderer:
    """Render an AJAX form's response into JSON format"""

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def render(self, changes):
        """Render form status and changes in JSON format"""
        registry = self.request.registry
        result = {}
        for form in self.form.get_forms(include_self=False):
            if form.mode == DISPLAY_MODE:
                continue
            renderer = registry.queryMultiAdapter((form.context, form.request, form),
                                                  IAJAXFormRenderer)
            if renderer is not None:
                form_output = renderer.render(changes)
                if form_output:
                    merge_dict(form_output, result)
        return result


@adapter_config(required=(Interface, IFormLayer, IForm), provides=IAJAXErrorsRenderer)
class AJAXErrorRenderer:
    """Default AJAX error renderer

    This renderer is based on status messages as handled by MyAMS framework.
    """

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    @classmethod
    def get_widget_error(cls, error, status, translate):
        """Get widget for a given error"""
        message = translate(error.message)
        if hasattr(error, 'widget'):
            widget = error.widget
            if widget is not None:
                status.setdefault('widgets', []).append({
                    'id': widget.id,
                    'name': widget.name,
                    'label': translate(widget.label),
                    'message': message
                })
            else:
                error_message = {'message': message}
                if error_message not in status.get('messages', ()):
                    status.setdefault('messages', []).append(error_message)
        else:
            if message not in status.get('messages', ()):
                status.setdefault('messages', []).append(message)

    def render(self, errors):
        """Return status as JSON message"""
        registry = self.request.registry
        translate = self.request.localizer.translate
        result = {
            'status': 'error',
            'error_message': translate(self.form.status)
        }
        for error in errors:
            if isinstance(error, Exception):
                error = registry.getMultiAdapter(
                    (error, self.request, None, None, self, self.request),
                    IErrorViewSnippet)
            error.update()
            if IMultipleErrors.providedBy(error.error):
                for inner_error in error.error.errors:
                    self.get_widget_error(inner_error, result, translate)
            else:
                self.get_widget_error(error, result, translate)
        return result


class ajax_form_config:  # pylint: disable=invalid-name
    """Class decorator for form configuration with AJAX support

    When decorating a form class, this decorator create two new classes:
     - a first class, registered as a view and a pagelet, chich will provide classic HTML form
       rendering
     - a second class, inheriting from AJAX forms, which will handle AJAX queries executed when
       submitting the form; this class is registered as a Pyramid's views using a JSON renderer.

    Decorator arguments are all optional:
    :param name: AJAX view name, as used into browser's URL
    :param context (or *for_*): views context type
    :param layer: (or *request_type*): request layer for which the view is registered
    :param permission: permission required to call the base view
    :param ajax_name: name of the AJAX submit view; if undefined, this AJAX name will be the base
        view name, with ".html" replaced by ".json"
    :param ajax_base: base class for newly created AJAX forms; if not set, inherits from
        :py:class:`AJAXEditForm`of :py:classl`AJAXAddForm`, based on interface implemented by
        the view class
    :param ajax_implements: a list of marker interfaces implemented by the new class; these
        interfaces can be used, for example, to declare custom adapters based on these interfaces
    :param ajax_method: HTTP method name; if not defined, new AJAX
        view is restricted to *POST* requests; use "method=None" to be able to use any method
    :param ajax_permission: permission required to call the AJAX view; if not defined, AJAX view
        permission will be based on base view 'edit_permission', if any
    :param ajax_renderer: name of Pyramid renderer used to return AJAX view output; defaults to
        *json*
    :param ajax_xhr: Pyramid's view *xhr* predicate, *True* by default.

    All other view predicates are also available when using this decorator.
    """

    venusian = venusian

    def __init__(self, **settings):  # pylint: disable=too-many-branches
        if 'name' not in settings:
            raise ConfigurationError("Missing 'name' argument for form definition")
        if 'for_' in settings:
            if settings.get('context') is None:
                settings['context'] = settings.pop('for_')
        if 'layer' in settings:
            settings['request_type'] = settings.pop('layer')
        # get AJAX settings
        settings['ajax'] = ajax_settings = {}
        if 'context' in settings:
            ajax_settings['context'] = settings.get('context')
        if 'ajax_name' in settings:
            ajax_settings['name'] = settings.pop('ajax_name')
        else:
            ajax_settings['name'] = settings['name'].replace('.html', '.json')
        if 'ajax_base' in settings:
            ajax_settings['base'] = settings.pop('ajax_base')
        if 'ajax_implements' in settings:
            ajax_settings['implements'] = settings.pop('ajax_implements')
        if 'ajax_method' in settings:
            method = settings.pop('ajax_method')
            if method is not None:
                ajax_settings['request_method'] = method
        else:
            ajax_settings['request_method'] = 'POST'
        if 'ajax_permission' in settings:
            ajax_settings['permission'] = settings.pop('ajax_permission')
        if 'ajax_renderer' in settings:
            renderer = settings.pop('ajax_renderer')
            if renderer is not None:
                ajax_settings['renderer'] = renderer
        else:
            ajax_settings['renderer'] = 'json'
        if 'ajax_xhr' in settings:
            xhr = settings.pop('ajax_xhr')
            if xhr is not None:
                ajax_settings['xhr'] = xhr
        else:
            ajax_settings['xhr'] = True
        self.__dict__.update(settings)

    def __call__(self, wrapped):
        form_settings = self.__dict__.copy()
        depth = form_settings.pop('_depth', 0)
        ajax_settings = form_settings.pop('ajax')

        def callback(context, name, obj):  # pylint: disable=unused-argument
            """Venusian decorator callback"""

            config = context.config.with_package(info.module)  # pylint: disable=no-member

            # Standard pagelet view settings
            form_cdict = {
                '__module__': obj.__module__,
                '__name__': form_settings.get('name'),
                'permission': form_settings.get('permission'),
                'ajax_form_handler': ajax_settings.get('name')
            }

            # AJAX view settings
            ajax_cdict = {
                '__module__': obj.__module__,
                '__name__': ajax_settings.get('name')
            }
            permission = ajax_settings.get('permission') or getattr(obj, '_edit_permission')
            if permission is not None:
                ajax_cdict['permission'] = permission
            base = ajax_settings.get('base')
            if base is None:
                if IAddForm.implementedBy(obj):  # pylint: disable=no-value-for-parameter
                    base = AJAXAddForm
                else:
                    base = AJAXEditForm
            if 'implements' in ajax_settings:
                impl = ajax_settings.pop('implements')
                if not isinstance(impl, (list, tuple, set)):
                    impl = (impl,)
                # classImplements(ajax_class, *impl)
                obj.__ajax_interfaces__ = impl

            form_class = type(obj.__name__, (obj, Pagelet), form_cdict)
            LOGGER.debug('Registering pagelet view "{}" for {} ({})'.format(
                form_settings.get('name'),
                str(form_settings.get('context', Interface)),
                str(form_class)))
            registry = form_settings.get('registry') or config.registry
            registry.registerAdapter(form_class,
                                     (form_settings.get('context', Interface),
                                      form_settings.get('request_type', IRequest)),
                                     IPagelet, form_settings.get('name'))
            config.add_view(view=form_class, **form_settings)

            ajax_class = type('AJAX' + obj.__name__, (base, obj), ajax_cdict)
            LOGGER.debug('Registering AJAX view "{0}" for {1} ({2})'.format(
                ajax_settings.get('name'),
                str(ajax_settings.get('context', Interface)),
                str(ajax_class)))
            config.add_view(view=ajax_class, **ajax_settings)

        info = self.venusian.attach(wrapped, callback, category='pyams_form',
                                    depth=depth + 1)
        if info.scope == 'class':  # pylint: disable=no-member
            # if the decorator was attached to a method in a class, or
            # otherwise executed at class scope, we need to set an
            # 'attr' into the settings if one isn't already in there
            if form_settings.get('attr') is None:
                form_settings['attr'] = wrapped.__name__
            if ajax_settings.get('attr') is None:
                ajax_settings['attr'] = wrapped.__name__
        form_settings['_info'] = info.codeinfo  # pylint: disable=no-member
        ajax_settings['_info'] = info.codeinfo  # pylint: disable=no-member

        return wrapped
