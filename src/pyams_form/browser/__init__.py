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

"""PyAMS_form.browser main module

Fanstatic resources definition.
"""

from fanstatic import Library, Resource


__docformat__ = 'restructuredtext'


# pylint: disable=invalid-name
library = Library('pyams_form', 'resources')

# pylint: disable=invalid-name
ordered_select_input = Resource(library, 'js/orderedselect-input.js',
                                minified='js/orderedselect-input.min.js')
