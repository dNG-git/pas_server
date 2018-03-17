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

from weakref import proxy, ProxyTypes

from dNG.runtime.named_loader import NamedLoader

class Abstract(object):
    """
"Abstract" provides methods for a controller based module and service
implementation.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self):
        """
Constructor __init__(Abstract)

:since: v1.0.0
        """

        self._log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self.request = None
        """
Request instance
        """
        self.response = None
        """
Response instance
        """
    #

    @property
    def log_handler(self):
        """
Returns the LogHandler.

:return: (object) LogHandler in use
:since:  v1.0.0
        """

        return self._log_handler
    #

    @log_handler.setter
    def log_handler(self, log_handler):
        """
Sets the LogHandler.

:param log_handler: LogHandler to use

:since: v1.0.0
        """

        self._log_handler = (log_handler if (isinstance(log_handler, ProxyTypes)) else proxy(log_handler))
    #

    def init(self, request, response):
        """
Initializes the controller from the given request and response.

:param request: Request object
:param response: Response object

:since: v1.0.0
        """

        self.request = request
        self.response = response
    #
#
