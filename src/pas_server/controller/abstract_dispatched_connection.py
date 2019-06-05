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

from socket import SHUT_RDWR
from time import time
from weakref import proxy, ProxyTypes

from dpt_module_loader import NamedClassLoader
from dpt_plugins import Hook
from dpt_runtime.binary import Binary
from dpt_runtime.descriptor_selector import DescriptorSelector
from dpt_runtime.io_exception import IOException
from dpt_settings import Settings

from .abstract_connection import AbstractConnection

class AbstractDispatchedConnection(AbstractConnection):
    """
This abstract class contains methods to implement a dispatched connection
handler.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=unused-argument

    def __init__(self):
        """
Constructor __init__(AbstractDispatchedConnection)

:since: v1.0.0
        """

        AbstractConnection.__init__(self)

        self._client_socket_address = None
        """
Raw client socket address
        """
        self._read_buffer = Binary.BYTES_TYPE()
        """
Data buffer
        """
        self._read_timeout = int(Settings.get("global_server_socket_data_timeout", -1))
        """
Socket timeout value
        """
        self._server = None
        """
Server instance
        """
        self._socket = None
        """
Socket instance
        """
        self._socket_family = None
        """
Socket connection family
        """

        if (self._read_timeout < 1): self._read_timeout = int(Settings.get("global_socket_data_timeout", 30))
    #

    @property
    def socket(self):
        """
Returns the underlying connection socket.

:return: (object) Connection socket
:since:  v1.0.0
        """

        return self._socket
    #

    def finish(self):
        """
Finish transmission and cleanup resources.

:since: v1.0.0
        """

        if (self._server is not None):
            self._server.active_unqueue(self._socket)

            if (SHUT_RDWR is not None):
                try: self._socket.shutdown(SHUT_RDWR)
                except Exception: pass
            #

            try: self._socket.close()
            except Exception: pass

            self._server = None
            self._socket = None
        #
    #

    def get_data(self, size, force_size = False):
        """
Returns data read from the socket.

:param size: Bytes to read
:param force_size: True to wait for data until the given size has been
                   received.

:return: (bytes) Data received
:since:  v1.0.0
        """

        # pylint: disable=broad-except

        _return = Binary.BYTES_TYPE()

        data = None
        data_size = len(self._read_buffer)
        selector = DescriptorSelector([ self._socket.fileno() ])
        _time = time()
        timeout_time = (_time + self._read_timeout)

        while (self._socket is not None
               and self._socket.fileno() > -1
               and (data is None or (force_size and data_size < size))
               and _time < timeout_time
              ):
            try:
                selector.select(timeout_time - _time, False)

                if (self._socket_family is None):
                    ( data, address ) = self._socket.recvfrom(size)
                    address_family = self._socket.family

                    self._set_socket_address(address_family, address)
                else: data = self._socket.recv(size)

                _time = time()
            except Exception: break

            if (len(data) > 0):
                self._set_data(data)
                data_size = len(self._read_buffer)
            else: data = None
        #

        if (len(self._read_buffer) > 0):
            _return = self._read_buffer
            self._read_buffer = Binary.BYTES_TYPE()
        #

        if (force_size and data_size < size): raise IOException("Received data size is smaller than the expected size of {0:d} bytes".format(size))
        return _return
    #

    def init_from_dispatcher(self, server, socket):
        """
Initializes the connection based on relevant instance data from the underlying
server and socket.

:param server: Server instance
:param socket: Active socket resource

:since: v1.0.0
        """

        self._server = server

        self._socket = socket
        if (self._read_timeout is not None): self._socket.settimeout(self._read_timeout)
    #

    def _set_data(self, data):
        """
Sets data returned next time "get_data()" is called.

:param data: Data to be buffered

:since: v1.0.0
        """

        self._read_buffer += Binary.bytes(data)
    #

    def _set_socket_address(self, family, address):
        """
Sets the socket family and address for this connection.

:param family: Socket family
:param address: Raw client socket address

:since: v1.0.0
        """

        self._client_socket_address = address
        self._socket_family = family
    #

    def write_data(self, data):
        """
Write data to the socket.

:param data: Data to be written

:return: (bool) True on success
:since:  v1.0.0
        """

        # pylint: disable=broad-except

        _return = True

        data = Binary.bytes(data)

        if (self._socket is not None and len(data) > 0):
            try: self._socket.sendall(data)
            except Exception as handled_exception:
                if (self._log_handler is not None): self._log_handler.error(handled_exception, context = "pas_server")
                _return = False
            #
        #

        return _return
    #
#
