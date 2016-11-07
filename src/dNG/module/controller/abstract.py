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

from dNG.module.named_loader import NamedLoader

class Abstract(object):
    """
"Abstract" provides methods for a controller based module and service
implementation.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self):
        """
Constructor __init__(Abstract)

:since: v0.2.00
        """

        self.log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
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

    def init(self, request, response):
        """
Initializes the controller from the given request and response.

:param request: Request object
:param response: Response object

:since: v0.2.00
        """

        self.request = request
        self.response = response
    #

    def set_log_handler(self, log_handler):
        """
Sets the LogHandler.

:param log_handler: LogHandler to use

:since: v0.2.00
        """

        self.log_handler = log_handler
    #
#
