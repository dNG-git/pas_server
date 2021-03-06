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

from dpt_runtime.not_implemented_exception import NotImplementedException

from .abstract_request_mixin import AbstractRequestMixin

class AbstractInnerRequest(AbstractRequestMixin):
    """
This abstract class contains common methods for inner requests usually used
for redirection.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ "__weakref__", "_parameters_chained" ] + AbstractRequestMixin._mixin_slots_
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self):
        """
Constructor __init__(AbstractInnerRequest)

:since: v1.0.0
        """

        AbstractRequestMixin.__init__(self)

        self._parameters_chained = { }
        """
Chained request parameters
        """

        self.supported_features['listener_data'] = self._supports_listener_data
        self.supported_features['parameters_chained'] = True
    #

    @AbstractRequestMixin.client_host.setter
    def client_host(self, host):
        """
Sets the client host for the inner request.

:param host: Client host

:since: v1.0.0
        """

        self._client_host = host
    #

    @AbstractRequestMixin.client_port.setter
    def client_port(self, port):
        """
Sets the client port.

:param port: Client port

:since: v1.0.0
        """

        self._client_port = port
    #

    @AbstractRequestMixin.parameters.setter
    def parameters(self, parameters):
        """
Sets all parameters given and if not already defined.

:param parameters: Request parameters

:since: v1.0.0
        """

        if (len(parameters) > 0):
            for key in parameters:
                if (key not in self._parameters): self._parameters[key] = parameters[key]
            #
        else: self._parameters = { }
    #

    @property
    def parameters_chained(self):
        """
Return all parameters of a chained request.

:return: (dict) Request parameters chained
:since:  v1.0.0
        """

        return self._parameters_chained
    #

    @AbstractRequestMixin.server_host.setter
    def server_host(self, host):
        """
Sets the server host for the inner request.

:param host: Server host

:since: v1.0.0
        """

        self._server_host = host
    #

    @AbstractRequestMixin.server_port.setter
    def server_port(self, port):
        """
Sets the server port.

:param port: Server port

:since: v1.0.0
        """

        self._server_port = port
    #

    @AbstractRequestMixin.server_scheme.setter
    def server_scheme(self, scheme):
        """
Sets the underlying server scheme.

:param scheme: Server scheme / protocol

:since: v1.0.0
        """

        self._server_scheme = scheme
    #

    def get_parameter_chained(self, name, default = None):
        """
Returns the value for the specified parameter in a chained request.

:param name: Parameter name
:param default: Default value if not set

:return: (mixed) Requested value or default one if undefined
:since:  v1.0.0
        """

        return (self._parameters_chained[name] if (name in self._parameters_chained) else default)
    #

    def init(self, connection_or_request):
        """
Initializes default values from the a connection or request instance.

:param connection_or_request: (object) Connection or request instance

:since: v1.0.0
        """

        AbstractRequestMixin.init(self, connection_or_request)

        parameters = connection_or_request.parameters
        if (len(parameters) > 0): self.parameters = parameters
    #

    def set_parameter_chained(self, name, value):
        """
Sets the value for the given parameter in a chained request.

:param name: Parameter name
:param value: Parameter value

:since: v1.0.0
        """

        self._parameters_chained[name] = value
    #

    def _supports_listener_data(self):
        """
Returns false if the server address is unknown.

:return: (bool) True if listener are known.
:since:  v1.0.0
        """

        return (self.server_host is not None)
    #
#
