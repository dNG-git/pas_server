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

from dpt_runtime.operation_not_supported_exception import OperationNotSupportedException
from dpt_runtime.supports_mixin import SupportsMixin
from dpt_runtime.type_exception import TypeException

class AbstractRequestMixin(SupportsMixin):
    """
Mixin for abstract classes to implement methods only once.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    _mixin_slots_ = [ "_client_host",
                      "_client_port",
                      "_log_handler",
                      "_parameters",
                      "_server_host",
                      "_server_port",
                      "_server_scheme",
                      "_stream_response"
                    ] + SupportsMixin._mixin_slots_
    """
Additional __slots__ used for inherited classes.
    """
    __slots__ = [ ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self):
        """
Constructor __init__(AbstractRequest)

:since: v1.0.0
        """

        SupportsMixin.__init__(self)

        self._client_host = None
        """
Client host
        """
        self._client_port = None
        """
Client port
        """
        self._log_handler = None
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self._parameters = { }
        """
Request parameters
        """
        self._server_host = None
        """
Server host
        """
        self._server_port = None
        """
Server port
        """
        self._server_scheme = None
        """
Server scheme / protocol
        """
        self._stream_response = None
        """
Stream response instance
        """

        self.supported_features['stream_response'] = self._supports_stream_response
    #

    @property
    def client_host(self):
        """
Returns the client host if any.

:return: (str) Client host; None if unknown or not applicable
:since:  v1.0.0
        """

        return self._client_host
    #

    @property
    def client_port(self):
        """
Returns the client port if any.

:return: (int) Client port; None if unknown or not applicable
:since:  v1.0.0
        """

        return self._client_port
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

    @property
    def parameters(self):
        """
Return all parameters received.

:return: (dict) Request parameters
:since:  v1.0.0
        """

        return self._parameters.copy()
    #

    @property
    def server_host(self):
        """
Returns the server host if any.

:return: (str) Server host; None if unknown or not applicable
:since:  v1.0.0
        """

        return self._server_host
    #

    @property
    def server_port(self):
        """
Returns the server port if any.

:return: (int) Server port; None if unknown or not applicable
:since:  v1.0.0
        """

        return self._server_port
    #

    @property
    def server_scheme(self):
        """
Returns the server scheme.

:return: (str) Server scheme / protocol; None if unknown
:since:  v1.0.0
        """

        return self._server_scheme
    #

    @property
    def stream_response(self):
        """
Returns the stream response instance in use.

:return: (object) Stream response instance
:since:  v1.0.0
        """

        if (self._stream_response is None): raise OperationNotSupportedException("'{0!r}' has no stream response instance".format(self))
        return self._stream_response
    #

    def get_parameter(self, name, default = None):
        """
Returns the value for the specified parameter.

:param name: Parameter name
:param default: Default value if not set

:return: (mixed) Requested value or default one if undefined
:since:  v1.0.0
        """

        return self._parameters.get(name, default)
    #

    def init(self, connection_or_request):
        """
Initializes default values from the a connection or request instance.

:param connection_or_request: Connection or request instance

:since: v1.0.0
        """

        if (not isinstance(connection_or_request, AbstractRequestMixin)): raise TypeException("Request instance given is invalid")

        self._client_host = connection_or_request.client_host
        self._client_port = connection_or_request.client_port
        self._server_scheme = connection_or_request.server_scheme
        self._server_host = connection_or_request.server_host
        self._server_port = connection_or_request.server_port

        self._log_handler = connection_or_request.log_handler

        if (connection_or_request.is_supported("stream_response")):
            self._stream_response = connection_or_request.stream_response
        elif (connection_or_request.is_supported("stream_response_creation")):
            self._stream_response = connection_or_request.new_stream_response()
        #
    #

    def set_parameter(self, name, value):
        """
Sets the value for the specified parameter.

:param name: Parameter name
:param value: Parameter value

:since: v1.0.0
        """

        self._parameters[name] = value
    #

    def _supports_stream_response(self):
        """
Returns false if no separate stream response instance is connected to the
connection.

:return: (bool) True if a stream response instance is available
:since:  v1.0.0
        """

        try: return (self.stream_response is not None)
        except OperationNotSupportedException: return False
    #
#
