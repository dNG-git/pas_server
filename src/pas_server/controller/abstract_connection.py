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

from dpt_logging import LogLine
from dpt_module_loader import NamedClassLoader

from .abstract_request_mixin import AbstractRequestMixin

class AbstractConnection(AbstractRequestMixin):
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

    __slots__ = [ "_stream_response" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, *args, **kwargs):
        """
Constructor __init__(AbstractConnection)

:since: v1.0.0
        """

        AbstractRequestMixin.__init__(self)

        self._stream_response = None
        """
Stream response instance
        """

        self._log_handler = NamedClassLoader.get_singleton("dpt_logging.LogHandler", False)

        self.supported_features['stream_response_creation'] = False
    #

    def __del__(self):
        """
Destructor __del__(AbstractConnection)

:since: v1.0.0
        """

        self.finish()
    #

    def finish(self):
        """
Finish transmission and cleanup resources.

:since: v1.0.0
        """

        pass
    #

    def handle(self):
        """
Handles this connection.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        try:
            request = self._new_request()

            request.init(self)
            request.execute()
        except Exception as handled_exception: self.handle_execution_exception(handled_exception)
    #

    def handle_execution_exception(self, exception):
        """
Handles the uncatched exception thrown while connection handling.

:since: v1.0.0
        """

        LogLine.error(exception, context = "pas_server")
    #

    def _new_request(self):
        """
Initializes a new request instance for this connection.

:return: (object) Request object
:since:  v1.0.0
        """

        raise NotImplementedException()
    #

    def new_stream_response(self):
        """
Initializes a new stream response instance for this connection. Supported
feature "stream_response_creation" should only be set to true if no
additional arguments are required.

:return: (object) Stream response object
:since:  v1.0.0
        """

        raise NotImplementedException()
    #
#
