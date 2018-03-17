# -*- coding: utf-8 -*-

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;server

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasServerVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=import-error, no-name-in-module

from dNG.data.supports_mixin import SupportsMixin
from dNG.runtime.named_loader import NamedLoader

from .abstract_mixin import AbstractMixin

class AbstractConnection(SupportsMixin, AbstractMixin):
    """
This abstract class contains common methods to implement a connection.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self, *args, **kwargs):
        """
Constructor __init__(AbstractConnection)

:since: v1.0.0
        """

        AbstractMixin.__init__(self)
        SupportsMixin.__init__(self)

        self._log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
    #

    def close(self):
        """
Cleans up and closes this connection.

:since: v1.0.0
        """

        pass
    #
#
