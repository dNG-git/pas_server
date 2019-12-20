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

from os import path
from threading import local
from weakref import proxy, ProxyTypes
import os
import stat
import socket
import time

from dpt_module_loader import NamedClassLoader
from dpt_plugins import Hook
from dpt_runtime.binary import Binary
from dpt_runtime.io_exception import IOException
from dpt_runtime.not_implemented_exception import NotImplementedException
from dpt_settings import Settings
from dpt_threading.instance_lock import InstanceLock
from dpt_threading.thread import Thread

from .controller import AbstractDispatchedConnection

class AbstractDispatcher(object):
    """
The server dispatcher allows an application to provide threaded connections
and communication.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=unused-argument

    __slots__ = [ "__weakref__",
                  "_active",
                  "_active_connection_class",
                  "_actives_list",
                  "_backlog_max",
                  "_listener_handle_connections",
                  "_listener_socket",
                  "_listener_startup_timeout",
                  "local",
                  "_lock",
                  "_log_handler",
                  "stopping_hook",
                  "thread"
                ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, listener_socket, active_connection_class, threads_active, backlog_max, thread_stopping_hook):
        """
Constructor __init__(AbstractDispatcher)

:param listener_socket: Listener socket
:param active_connection_class: Thread class to be initialized for activated connections
:param threads_active: Allowed simultaneous threads
:param backlog_max: Allowed queued threads
:param thread_stopping_hook: Thread stopping hook definition

:since: v1.0.0
        """

        self._active = False
        """
Listener state
        """
        self._active_connection_class = (active_connection_class if (issubclass(active_connection_class, AbstractDispatchedConnection)) else None)
        """
Active queue connection class
        """
        self._actives_list = [ ]
        """
Active queue
        """
        self._backlog_max = backlog_max
        """
Maximum sockets in backlog
        """
        self._listener_handle_connections = (listener_socket.type & socket.SOCK_STREAM)
        """
Listener socket
        """
        self._listener_socket = listener_socket
        """
Listener socket
        """
        self._listener_startup_timeout = 45
        """
Listener startup timeout
        """
        self.local = None
        """
Local data handle
        """
        self._lock = InstanceLock()
        """
Thread safety lock
        """
        self._log_handler = None
        """
The log handler is called whenever debug messages should be logged or errors
happened.
        """
        self.stopping_hook = ("" if (thread_stopping_hook is None) else thread_stopping_hook)
        """
Stopping hook definition
        """
        self.thread = None
        """
Thread if started and active
        """

        self.log_handler = NamedClassLoader.get_singleton("dpt_logging.LogHandler", False)
    #

    @property
    def is_active(self):
        """
Returns the listener status.

:return: (bool) True if active and listening
:since:  v1.0.0
        """

        return self._active
    #

    @property
    def log_handler(self):
        """
Returns the log handler.

:return: (object) Log handler in use
:since:  v1.0.0
        """

        return self._log_handler
    #

    @log_handler.setter
    def log_handler(self, log_handler):
        """
Sets the log handler.

:param log_handler: Log handler to use

:since: v1.0.0
        """

        self._log_handler = (log_handler if (isinstance(log_handler, ProxyTypes)) else proxy(log_handler))
    #

    def _activate_connection(self, _socket):
        """
Initializes the active connection class with the given socket.

:param _socket: Active socket resource

:since: v1.0.0
        """

        connection = self._active_connection_class()
        connection.init_from_dispatcher(self, _socket)

        if (isinstance(connection, Thread)):
            connection.start()
            if (_socket.type == socket.SOCK_DGRAM): connection.join()
        else: connection.handle()

        if (self._log_handler is not None): self._log_handler.debug("{0!r} started '{1!r}'", self, connection, context = "pas_server")
    #

    def _add_active_socket(self, _socket):
        """
Put's an socket on the list of active connections.

:param _socket: Active socket resource

:return: (bool) True on success
:since:  v1.0.0
        """

        _return = False

        if (self.is_active):
            with self._lock:
                # Thread safety lock
                if (self.is_active):
                    self._actives_list.append(_socket)
                    _return = True
                #
            #
        #

        return _return
    #

    def _ensure_thread_local(self):
        """
For thread safety some variables are defined per thread. This method makes
sure that these variables are defined.

:since: v1.0.0
        """

        if (self.local is None): self.local = local()
    #

    def _init(self):
        """
Initializes the dispatcher and stopping hook.

:since: v1.0.0
        """

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}._init()- (#echo(__LINE__)#)", self, context = "pas_server")

        if (self.stopping_hook is not None):
            stopping_hook = ("pas.Application.onShutdown" if (self.stopping_hook == "") else self.stopping_hook)
            Hook.register_weakref(stopping_hook, self.thread_stop)
        #
    #

    def _remove_active_socket(self, _socket):
        """
Removes the given socket from the list of active connections.

:param _socket: Active socket resource

:return: (bool) True on success
:since:  v1.0.0
        """

        _return = False

        self._lock.acquire()

        if (self._actives_list is not None and _socket in self._actives_list):
            self._actives_list.remove(_socket)
            self._lock.release()

            _return = True

            if (self._listener_handle_connections):
                try: _socket.close()
                except socket.error: pass
            #
        else: self._lock.release()

        return _return
    #

    def remove_activated_socket(self, _socket):
        """
Unqueue the given ID from the active queue.

:param _socket: Active socket resource

:return: (bool) True on success
:since:  v1.0.0
        """

        return self._remove_active_socket(_socket)
    #

    def _remove_all_sockets(self):
        """
Unqueue all entries from the active queue (canceling running processes).

:since: v1.0.0
        """

        with self._lock:
            if (self._actives_list is not None):
                for _socket in self._actives_list: self._remove_active_socket(_socket)
            #
        #
    #

    def start(self):
        """
Starts the prepared dispatcher in a new thread.

:since: v1.0.0
        """

        raise NotImplementedException()
    #

    def run(self):
        """
Run the main loop for this server instance.

:since: v1.0.0
        """

        raise NotImplementedException()
    #

    def stop(self):
        """
Stops the listener and unqueues all running sockets.

:since: v1.0.0
        """

        raise NotImplementedException()
    #

    def thread_start(self, params = None, last_return = None):
        """
Starts the prepared dispatcher instance.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v1.0.0
        """

        self.start()
        return (True if (last_return is None) else last_return)
    #

    def thread_stop(self, params = None, last_return = None):
        """
Stops the running dispatcher instance by a stopping hook call.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v1.0.0
        """

        self.stop()
        return last_return
    #

    @staticmethod
    def prepare_socket(listener_type, *listener_data):
        """
Prepare socket returns a bound socket for the given listener data.

:param listener_type: Listener type
:param listener_data: Listener data

:since: v1.0.0
        """

        _return = None

        if (listener_type == socket.AF_INET or listener_type == socket.AF_INET6):
            listener_data = ( Binary.str(listener_data[0]), listener_data[1] )

            _return = socket.socket(listener_type, socket.SOCK_STREAM)
            _return.setblocking(0)
            if (hasattr(socket, "SO_REUSEADDR")): _return.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            _return.bind(listener_data)
        elif (listener_type == socket.AF_UNIX):
            unixsocket_path_name = path.normpath(Binary.str(listener_data[0]))

            if (os.access(unixsocket_path_name, os.F_OK)):
                if (os.environ.get("PAS_SERVER_REMOVE_UNIX_SOCKETS_ON_START") in ( "1", "t", "true", "yes" )):
                    AbstractDispatcher._remove_unixsocket(unixsocket_path_name)
                else: raise IOException("UNIX socket file '{0}' already exists".format(unixsocket_path_name))
            #

            _return = socket.socket(listener_type, socket.SOCK_STREAM)
            _return.bind(unixsocket_path_name)

            socket_chmod = 0
            socket_chmod_value = int(Settings.get("pas_global_server_chmod_unix_sockets", "600"), 8)

            if (1000 & socket_chmod_value): socket_chmod |= stat.S_ISVTX
            if (2000 & socket_chmod_value): socket_chmod |= stat.S_ISGID
            if (4000 & socket_chmod_value): socket_chmod |= stat.S_ISUID
            if (0o100 & socket_chmod_value): socket_chmod |= stat.S_IXUSR
            if (0o200 & socket_chmod_value): socket_chmod |= stat.S_IWUSR
            if (0o400 & socket_chmod_value): socket_chmod |= stat.S_IRUSR
            if (0o010 & socket_chmod_value): socket_chmod |= stat.S_IXGRP
            if (0o020 & socket_chmod_value): socket_chmod |= stat.S_IWGRP
            if (0o040 & socket_chmod_value): socket_chmod |= stat.S_IRGRP
            if (0o001 & socket_chmod_value): socket_chmod |= stat.S_IXOTH
            if (0o002 & socket_chmod_value): socket_chmod |= stat.S_IWOTH
            if (0o004 & socket_chmod_value): socket_chmod |= stat.S_IROTH

            os.chmod(unixsocket_path_name, socket_chmod)
        #

        return _return
    #

    @staticmethod
    def _remove_unixsocket(unixsocket_path_name):
        """
Removes the UNIX socket file given.

:param unixsocket_path_name: UNIX socket file path and name

:since: v1.0.0
        """

        if (path.exists(unixsocket_path_name)):
            if (hasattr(stat, "S_ISSOCK")):
                if (not stat.S_ISSOCK(os.stat(unixsocket_path_name).st_mode)):
                    raise IOException("File '{0}' exists but is not a UNIX socket".format(unixsocket_path_name))
                #
            #

            if (not os.access(unixsocket_path_name, os.W_OK)):
                raise IOException("UNIX socket file '{0}' is not writable".format(unixsocket_path_name))
            #

            os.unlink(unixsocket_path_name)
        #
    #
#
