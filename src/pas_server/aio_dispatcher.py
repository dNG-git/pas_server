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

from socket import AF_UNIX, SOCK_DGRAM
import asyncio
import time

from dpt_plugins import Hook
from dpt_runtime.io_exception import IOException
from dpt_runtime.traced_exception import TracedException
from dpt_threading.thread import Thread

from .abstract_dispatcher import AbstractDispatcher
from .aio_datagram_listener import AioDatagramListener
from .aio_protocol import AioProtocol
from .shutdown_exception import ShutdownException

class AioDispatcher(AbstractDispatcher):
    """
The server dispatcher allows an application to provide threaded connections
and communication. This implementation is based on "asyncio".

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=unused-argument

    __slots__ = [ "_datagram_listener", "_event_loop" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, listener_socket, active_connection_class, threads_active = 5, backlog_max = 50, thread_stopping_hook = None):
        """
Constructor __init__(AioDispatcher)

:param listener_socket: Listener socket
:param active_connection_class: Thread class to be initialized for activated connections
:param threads_active: Allowed simultaneous threads
:param backlog_max: Allowed queued threads
:param thread_stopping_hook: Thread stopping hook definition

:since: v1.0.0
        """

        AbstractDispatcher.__init__(self, listener_socket, active_connection_class, threads_active, backlog_max, thread_stopping_hook)

        self._datagram_listener = None
        """
asyncio datagram listener initialized for receiving data
        """
        self._event_loop = None
        """
asyncio event loop of this server instance
        """
    #

    @property
    def event_loop(self):
        """
"asyncio" event loop used for this dispatcher

:since: v1.0.0
        """

        return self._event_loop
    #

    def handle_connection(self, _socket):
        """
Handles incoming connections

:param _socket: Active socket resource

:since: v1.0.0
        """

        # pylint: disable=broad-except

        try:
            if (self._add_active_socket(_socket)): self._activate_connection(_socket)
        except ShutdownException as handled_exception:
            exception = handled_exception.cause

            if (exception is None and self._log_handler is not None): self._log_handler.error(handled_exception, context = "pas_server")
            else: handled_exception.print_stack_trace()
        except Exception as handled_exception:
            if (self._log_handler is None): TracedException.print_current_stack_trace()
            else: self._log_handler.error(handled_exception, context = "pas_server")
        #
    #

    def run(self):
        """
Run the main loop for this server instance.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.run()- (#echo(__LINE__)#)", self, context = "pas_server")

        if (not self.is_active):
            with self._lock:
                # Thread safety
                if (self.is_active): raise IOException("pas.server.Dispatcher has been executed multiple times")
                self._active = True
            #
        #

        self._ensure_thread_local()

        try: self.local.event_loop = asyncio.get_event_loop()
        except:
            self.local.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.local.event_loop)
        finally: self._event_loop = self.local.event_loop

        try:
            self._init()
            self.local.event_loop.run_until_complete(self._start_processing())

            self.local.event_loop.run_forever()
        except ShutdownException as handled_exception:
            if (self.is_active):
                exception = handled_exception.cause
                if (exception is not None and self._log_handler is not None): self._log_handler.error(exception, context = "pas_server")
            #
        except Exception as handled_exception:
            if (self.is_active):
                if (self._log_handler is None): TracedException.print_current_stack_trace()
                else: self._log_handler.error(handled_exception, context = "pas_server")
            #
        finally:
            self.stop()

            self.local.event_loop.run_until_complete(self.local.event_loop.shutdown_asyncgens())
            self.local.event_loop.close()
        #
    #

    def start(self):
        """
Starts the prepared dispatcher in a new thread.

:since: v1.0.0
        """

        if (not self.is_active):
            is_already_active = False

            with self._lock:
                # Thread safety
                is_already_active = self.is_active
                if (not is_already_active): self._active = True
            #

            if (not is_already_active):
                Thread(target = self.run).start()
            #
        #
    #

    async def _start_processing(self):
        """
Try to start processing data for the prepared socket.

:since: v1.0.0
        """

        if (self._listener_socket.type == SOCK_DGRAM): self._datagram_listener = AioDatagramListener(self, self._listener_socket)
        else:
            awaitable_callable = (self._event_loop.create_unix_server
                                  if (self._listener_socket.family == AF_UNIX) else
                                  self._event_loop.create_server
                                 )

            await awaitable_callable(AioProtocol(self), sock = self._listener_socket, backlog =self._backlog_max)
        #
    #

    def stop(self):
        """
Stops the listener and unqueues all running sockets.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        self._lock.acquire()

        if (self.is_active):
            if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.stop()- (#echo(__LINE__)#)", self, context = "pas_server")

            self._active = False

            if (self.stopping_hook is not None and len(self.stopping_hook) > 0): Hook.unregister(self.stopping_hook, self.thread_stop)
            self.stopping_hook = ""

            if (self._event_loop is not None):
                if (self._event_loop.is_running()): self._event_loop.call_soon_threadsafe(self._event_loop.stop)
                self._event_loop = None
            #

            self._lock.release()

            self._remove_all_sockets()

            try:
                if (self._listener_socket.family == AF_UNIX):
                    AioDispatcher._remove_unixsocket(self._listener_socket.getsockname())
                #
            except Exception: pass
        else: self._lock.release()
    #
#
