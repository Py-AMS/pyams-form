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

"""PyAMS_form.events module

Data extraction event.
"""

from zope.interface import implementer

from pyams_form.interfaces.form import IDataExtractedEvent


__docformat__ = 'restructuredtext'


@implementer(IDataExtractedEvent)
class DataExtractedEvent:
    """Data extracted event"""

    def __init__(self, data, errors, form):
        self.data = data
        self.errors = errors
        self.form = form
