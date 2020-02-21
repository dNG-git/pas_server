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

try: from collections.abc import Mapping
except ImportError: from collections import Mapping

from .abstract_connection import AbstractConnection

class DummyConnection(AbstractConnection):
    """
This class implements a dummy connection instance providing data given to
the "init()" method.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def init(self, **kwargs):
        """
Initializes default values from the connection or request data given.

:param connection_or_request: Connection or request instance

:since: v1.0.0
        """

        if ("client_host" in kwargs): self._client_host = kwargs['client_host']
        if ("client_port" in kwargs): self._client_port = kwargs['client_port']
        if ("server_scheme" in kwargs): self._server_scheme = kwargs['server_scheme']
        if ("server_host" in kwargs): self._server_host = kwargs['server_host']
        if ("server_port" in kwargs): self._server_port = kwargs['server_port']

        if (isinstance(kwargs.get("connection_parameters"), Mapping)):
            self._parameters.update(kwargs['connection_parameters'])
        #

        if ("log_handler" in kwargs): self._log_handler = kwargs['log_handler']

        if ("stream_response" in kwargs): self._stream_response = kwargs['stream_response']
        elif (callable(kwargs.get("new_stream_response"))): self._stream_response = kwargs['new_stream_response']()
    #
#
