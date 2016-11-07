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

class AbstractMixin(object):
    """
Mixin for abstract classes to implement methods only once.

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
Constructor __init__(AbstractRequest)

:since: v0.2.00
        """

        self.client_host = None
        """
Client host
        """
        self.client_port = None
        """
Client port
        """
        self.log_handler = None
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self.parameters = { }
        """
Request parameters
        """
        self.server_host = None
        """
Server host
        """
        self.server_port = None
        """
Server port
        """
        self.server_scheme = None
        """
Server scheme / protocol
        """
    #

    def get_client_host(self):
        """
Returns the client host if any.

:return: (str) Client host; None if unknown or not applicable
:since:  v0.2.00
        """

        return self.client_host
    #

    def get_client_port(self):
        """
Returns the client port if any.

:return: (int) Client port; None if unknown or not applicable
:since:  v0.2.00
        """

        return self.client_port
    #

    def get_parameter(self, name, default = None):
        """
Returns the value for the specified parameter.

:param key: Parameter name
:param default: Default value if not set

:return: (mixed) Requested value or default one if undefined
:since:  v0.2.00
        """

        return self.parameters.get(name, default)
    #

    def get_parameters(self):
        """
Return all parameters received.

:return: (dict) Request parameters
:since:  v0.2.00
        """

        return self.parameters
    #

    def get_server_host(self):
        """
Returns the server host if any.

:return: (str) Server host; None if unknown or not applicable
:since:  v0.2.00
        """

        return self.server_host
    #

    def get_server_port(self):
        """
Returns the server port if any.

:return: (int) Server port; None if unknown or not applicable
:since:  v0.2.00
        """

        return self.server_port
    #

    def get_server_scheme(self):
        """
Returns the server scheme.

:return: (str) Server scheme / protocol; None if unknown
:since:  v0.2.00
        """

        return self.server_scheme
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
