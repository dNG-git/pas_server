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

from socket import AF_UNIX
import asyncore
import time
import traceback

from dpt_plugins import Hook
from dpt_runtime.traced_exception import TracedException
from dpt_threading.thread import Thread

from .abstract_dispatcher import AbstractDispatcher
from .shutdown_exception import ShutdownException

class AsyncoreDispatcher(asyncore.dispatcher, AbstractDispatcher):
    """
The server dispatcher allows an application to provide threaded connections
and communication. This implementation is based on "asyncore".

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=unused-argument

    __slots__ = [ ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, listener_socket, active_connection_class, threads_active = 5, backlog_max = 10, thread_stopping_hook = None):
        """
Constructor __init__(AsyncoreDispatcher)

:param listener_socket: Listener socket
:param active_connection_class: Thread class to be initialized for activated connections
:param threads_active: Allowed simultaneous threads
:param backlog: Allowed queued threads
:param thread_stopping_hook: Thread stopping hook definition

:since: v1.0.0
        """

        asyncore.dispatcher.__init__(self, sock = listener_socket)
        AbstractDispatcher.__init__(self, listener_socket, active_connection_class, threads_active, backlog_max, thread_stopping_hook)
    #

    def _ensure_thread_local(self):
        """
For thread safety some variables are defined per thread. This method makes
sure that these variables are defined.

:since: v1.0.0
        """

        AbstractDispatcher._ensure_thread_local(self)
        if (not hasattr(self.local, "sockets")): self.local.sockets = { }
    #

    def handle_accept(self):
        """
python.org: Called on listening channels (passive openers) when a connection
can be established with a new remote endpoint that has issued a connect()
call for the local endpoint.

Deprecated since version 3.2.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        if (self.is_active and self._listener_handle_connections):
            socket_data = None

            try: socket_data = self.accept()
            except Exception as handled_exception:
                if (self._log_handler is None): TracedException.print_current_stack_trace()
                else: self._log_handler.error(handled_exception, context = "pas_server")
            #

            if (socket_data is not None): self.handle_accepted(socket_data[0], socket_data[1])
        #
    #

    def handle_accepted(self, sock, addr):
        """
python.org: Called on listening channels (passive openers) when a connection
has been established with a new remote endpoint that has issued a connect()
call for the local endpoint.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        if (self.is_active and self._listener_handle_connections):
            try:
                if (self._add_active_socket(sock)): self._activate_connection(sock)
            except ShutdownException as handled_exception:
                exception = handled_exception.cause

                if (exception is None and self._log_handler is not None): self._log_handler.error(handled_exception, context = "pas_server")
                else: handled_exception.print_stack_trace()
            except Exception as handled_exception:
                if (self._log_handler is None): TracedException.print_current_stack_trace()
                else: self._log_handler.error(handled_exception, context = "pas_server")
            #
        #
    #

    def handle_close(self):
        """
python.org: Called when the socket is closed.

:since: v1.0.0
        """

        if (self.is_active): self.stop()
    #

    def handle_connect(self):
        """
python.org: Called when the active opener's socket actually makes a
connection. Might send a "welcome" banner, or initiate a protocol
negotiation with the remote endpoint, for example.

:since: v1.0.0
        """

        if (self.is_active): self._start_listening()
    #

    def handle_error(self):
        """
python.org: Called when an exception is raised and not otherwise handled.

:since: v1.0.0
        """

        if (self._log_handler is None): TracedException.print_current_stack_trace()
        else: self._log_handler.error(traceback.format_exc(), context = "pas_server")
    #

    def handle_read(self):
        """
python.org: Called when the asynchronous loop detects that a "read()" call
on the channel's socket will succeed.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        if ((not self._listener_handle_connections) and self.is_active):
            try:
                if (self._add_active_socket(self._listener_socket)): self._activate_connection(self._listener_socket)
            except ShutdownException as handled_exception:
                exception = handled_exception.cause

                if (exception is None and self._log_handler is not None): self._log_handler.error(handled_exception, context = "pas_server")
                else: handled_exception.print_stack_trace()
            except Exception as handled_exception:
                if (self._log_handler is None): TracedException.print_current_stack_trace()
                else: self._log_handler.error(handled_exception, context = "pas_server")
            #
        #
    #

    def handle_expt(self):
        """
python.org: Called when there is out of band (OOB) data for a socket
connection. This will almost never happen, as OOB is tenuously supported and
rarely used.

:since: v1.0.0
        """

        if (self.is_active): self._remove_all_sockets()
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

        try:
            self._init()
            if (self._listener_handle_connections): self._start_listening()

            self.add_channel(self.local.sockets)
            asyncore.loop(5, map = self.local.sockets)
        except ShutdownException as handled_exception:
            if (self.is_active):
                exception = handled_exception.cause
                if (exception is not None and self._log_handler is not None): self._log_handler.error(exception, context = "pas_server")
            #
        except Exception as handled_exception:
            if (isinstance(handled_exception, OSError) and handled_exception.errno == 9): pass
            elif (self.is_active):
                if (self._log_handler is None): TracedException.print_current_stack_trace()
                else: self._log_handler.error(handled_exception, context = "pas_server")
            #
        finally: self.stop()
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

    def _start_listening(self):
        """
Try to start listening on the prepared socket. Uses the defined startup
timeout to wait for the socket to become available before throwing an
exception.

:since: v1.0.0
        """

        # pylint: disable=broad-except,raising-bad-type

        _exception = None
        timeout_time = (time.time() + self._listener_startup_timeout)

        while (time.time() < timeout_time):
            try:
                if (_exception is not None): time.sleep(0.2)
                _exception = None

                self.listen(self._backlog_max)

                break
            except Exception as handled_exception: _exception = handled_exception
        #

        if (_exception is not None): raise _exception
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

            self._lock.release()

            self._remove_all_sockets()

            unix_socket_path_name = (self._listener_socket.getsockname()
                                     if (self._listener_socket.family == AF_UNIX) else
                                     None
                                    )

            try: self.close()
            finally:
                if (unix_socket_path_name is not None):
                    try: AsyncoreDispatcher._remove_unixsocket(unix_socket_path_name)
                    except Exception: pass
                #
            #
        else: self._lock.release()
    #

    def writable(self):
        """
python.org: Called each time around the asynchronous loop to determine
whether a channel's socket should be added to the list on which write events
can occur.

:return: (bool) Always False
:since:  v1.0.0
        """

        return False
    #
#
