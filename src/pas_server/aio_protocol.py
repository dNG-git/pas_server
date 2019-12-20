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

from asyncio import BaseProtocol
from socket import fromfd

from dpt_logging import LogLine
from dpt_runtime.io_exception import IOException

class AioProtocol(BaseProtocol):
    """
The "asyncio" protocol implementation is used by the "AioDispatcher" to
process incoming connections.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=unused-argument

    __slots__ = [ "_dispatcher" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, dispatcher):
        """
Constructor __init__(AioProtocol)

:param listener_socket: Listener socket
:param active_connection_class: Thread class to be initialized for activated connections
:param threads_active: Allowed simultaneous threads
:param backlog_max: Allowed queued threads
:param thread_stopping_hook: Thread stopping hook definition

:since: v1.0.0
        """

        self._dispatcher = dispatcher
        """
asyncio event loop of this server instance
        """
    #

    def __call__(self):
        """
python.org: Protocol factory callable returning a protocol implementation.

:since: v1.0.0
        """

        return self
    #

    def connection_made(self, transport):
        """
python.org: Called when a connection is made.

:since: v1.0.0
        """

        async_socket = transport.get_extra_info("socket")
        if (async_socket is None or (not hasattr(async_socket, "detach"))): raise IOException("asyncio transport does not provide an detachable underlying socket")

        fd = async_socket.fileno()
        socket = fromfd(fd, async_socket.family, async_socket.type, async_socket.proto)
        async_socket.detach()

        self._dispatcher.handle_connection(socket)
    #

    def connection_lost(self, exc):
        """
python.org: Called when the connection is lost or closed.

:param exc: Exception instance; None if closed as expected

:since: v1.0.0
        """

        if (exc is not None and self._dispatcher.is_active and ((not isinstance(exc, OSError)) or exc.errno != 9)):
            LogLine.error(exc, context = "pas_server")
        #
    #
#
