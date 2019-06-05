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
from dpt_threading.thread import Thread

from .abstract_dispatched_connection import AbstractDispatchedConnection
from ..shutdown_exception import ShutdownException

class AbstractThreadDispatchedConnection(Thread, AbstractDispatchedConnection):
    """
This abstract class contains methods to implement a dispatched connection
handler that is executed in a separate thread.

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


        Thread.__init__(self)
        AbstractDispatchedConnection.__init__(self)
    #

    def __enter__(self):
        """
python.org: Enter the runtime context related to this object.

:since: v1.0.0
        """

        Hook.register("pas.Application.onShutdown", self.stop)
    #

    def __exit__(self, exc_type, exc_value, traceback):
        """
python.org: Exit the runtime context related to this object.

:return: (bool) True to suppress exceptions
:since:  v1.0.0
        """

        Hook.unregister("pas.Application.onShutdown", self.stop)
        return False
    #

    def handle(self):
        """
Handles this connection.

:since: v1.0.0
        """

        if (isinstance(self, Thread)): self.start()
        else: AbstractConnection.handle(self)
    #

    def start(self):
        """
python.org: Start the thread's activity.

:since: v1.0.0
        """

        if (not isinstance(self, Thread)): raise IOException("{0!r} does not support execution in an separate thread")

        if (self._server is not None):
            if (self.daemon or Thread._active): Thread.start(self)
            else: LogLine.debug("{0!r} prevented new non-daemon thread", self, context = "pas_server")
        #
    #

    def run(self):
        """
Thread "run()" method calling "_thread_run()". Do not override.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        try:
            with self: self._thread_run()
        except ShutdownException:
            if (self._server is not None): self._server.stop()
        except Exception as handled_exception:
            if (self._log_handler is not None): self._log_handler.error(handled_exception, context = "pas_server")
        finally: self.finish()
    #

    def stop(self, params = None, last_return = None):
        """
Stop the thread by actually closing the underlying socket.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v1.0.0
        """

        # pylint: disable=broad-except

        try: self.finish()
        except Exception: pass

        return last_return
    #

    def _thread_run(self):
        """
Handles the active, threaded connection.

:since: v1.0.0
        """

        AbstractDispatchedConnection.handle(self)
    #
#
