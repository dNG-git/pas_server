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

from socket import SOCK_DGRAM

from dpt_runtime.descriptor_selector import DescriptorSelector
from dpt_runtime.exception_log_trap import ExceptionLogTrap
from dpt_runtime.io_exception import IOException

class AioDatagramListener(object):
    """
The "asyncio" datagram listener is used by the "AioDispatcher" to process
incoming datagrams.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=unused-argument

    __slots__ = [ "_dispatcher", "_socket" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, dispatcher, listener_socket):
        """
Constructor __init__(AioDatagramProtocol)

:param dispatcher: Dispatcher instance
:param listener_socket: Listener socket

:since: v1.0.0
        """

        if (listener_socket.type != SOCK_DGRAM): raise IOException("Socket given is not configured for datagrams")

        self._dispatcher = dispatcher
        """
"asyncio" based dispatcher instance
        """
        self._socket = listener_socket
        """
Underlying socket instance
        """

        self._dispatcher.event_loop.call_soon_threadsafe(self._configure)
    #

    def __del__(self):
        """
Destructor __del__(AioDatagramListener)

:since: v1.0.0
        """

        if (self._dispatcher.is_active):
            with ExceptionLogTrap("pas_server"):
                try: self._dispatcher.event_loop.remove_reader(self._socket.fileno())
                except OSError as handled_exception:
                    if (handled_exception is not None
                        and ((not isinstance(handled_exception, OSError)) or handled_exception.errno != 9)
                       ): raise
                    #
                #
            #
        #
    #

    def _configure(self):
        """
Called to configure the socket for the event loop reader.

:since: v1.0.0
        """

        with ExceptionLogTrap("pas_server"): self._dispatcher.event_loop.add_reader(self._socket.fileno(), self.handle_read)
    #

    def handle_read(self):
        """
Callback for the read availability watched file descriptor.

:since: v1.0.0
        """

        if (len(DescriptorSelector([ self._socket.fileno() ]).select(0)[0]) > 0):
            self._dispatcher.handle_connection(self._socket)
        #
    #
#
