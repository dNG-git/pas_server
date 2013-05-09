# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.server.dispatcher
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;server

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasServerVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from os import path
from threading import local, BoundedSemaphore, RLock, Thread
import asyncore, os, stat, socket

from dNG.pas.data.settings import direct_settings
from dNG.pas.module.named_loader import direct_named_loader
from dNG.pas.plugins.hooks import direct_hooks
from dNG.pas.pythonback import direct_str
from .handler import direct_handler
from .shutdown_exception import direct_shutdown_exception

class direct_dispatcher(asyncore.dispatcher):
#
	"""
The dNG server infrastructure allows an application to provide active
listeners, threaded connection establishment and to queue a defined amount
of requests transparently.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self, listener_socket, active_handler, threads_active = 5, queue_handler = None, threads_queued = 10, thread_stopping_hook = None):
	#
		"""
Constructor __init__(direct_dispatcher)

:param listener_socket: Listener socket
:param active_handler: Thread to be used for activated connections
:param threads_active: Allowed simultaneous threads
:param queue_handler: Thread to be used for queued connections
:param threads_queued: Allowed queued threads
:param thread_stopping_hook: Thread stopping hook definition

:since: v0.1.00
		"""

		asyncore.dispatcher.__init__(self, sock = listener_socket)

		self.active = False
		"""
Listener state
		"""
		self.active_handler = (active_handler if (issubclass(active_handler, direct_handler)) else None)
		"""
Active queue handler
		"""
		self.actives = BoundedSemaphore(threads_active)
		"""
Active counter
		"""
		self.actives_list = [ ]
		"""
Active queue
		"""
		self.listener_handle_connections = (listener_socket.family == socket.SOCK_STREAM)
		"""
Listener socket
		"""
		self.listener_socket = listener_socket
		"""
Listener socket
		"""
		self.local = None
		"""
Local data handle
		"""
		self.log_handler = direct_named_loader.get_singleton("dNG.pas.data.logging.log_handler", False)
		"""
The log_handler is called whenever debug messages should be logged or errors
happened.
		"""
		self.queue_handler = (queue_handler if (isinstance(queue_handler, direct_handler)) else None)
		"""
Passive queue handler
		"""
		self.queue_max = threads_queued
		"""
Passive queue maximum
		"""
		self.stopping_hook = ("" if (thread_stopping_hook == None) else thread_stopping_hook)
		"""
Stopping hook definition
		"""
		self.synchronized = RLock()
		"""
Thread safety lock
		"""
		self.thread = None
		"""
Thread if started and active
		"""
		self.waiting = 0
		"""
Thread safety lock
		"""
	#

	def __del__(self):
	#
		"""
Destructor __del__(direct_dispatcher)

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.return_instance()
	#

	def active_activate(self, py_socket):
	#
		"""
Unqueue the given ID from the active queue.

:param id: Queue ID
:param py_socket: Active socket resource

:access: protected
:since:  v0.1.00
		"""

		handler = self.active_handler()
		handler.set_instance_data(self, py_socket)
		handler.start()

		if (self.log_handler != None): self.log_handler.debug("pas.server started a new thread '{0!r}'".format(handler))
	#

	def active_queue(self, py_socket):
	#
		"""
Put's an transport on the active queue or tries to temporarily save it on
the passive queue.

:param py_socket: Active socket resource

:return: (int) Selected queue ID (> -1); True if passively queued.
:since:  v0.1.00
		"""

		var_return = False

		if (self.active):
		#
			if (self.actives.acquire(self.queue_handler == None)):
			#
				self.synchronized.acquire()

				if (self.active):
				#
					self.actives_list.append(py_socket)
					var_return = True
				#
				else: self.actives.release()

				self.synchronized.release()
			#
			else:
			#
				handler = self.queue_handler()
				handler.set_instance_data(self, py_socket)
				handler.start()

				self.waiting += 1
			#
		#

		return var_return
	#

	def active_unqueue(self, py_socket):
	#
		"""
Unqueue the given ID from the active queue.

:param id: Queue ID

:since: v0.1.00
		"""

		if (self.unqueue(self.actives_list, py_socket)): self.actives.release()
	#

	def active_unqueue_all(self):
	#
		"""
Unqueue all entries from the active queue (canceling running processes).

:since: v0.1.00
		"""

		self.synchronized.acquire()

		if (self.actives_list != None):
		#
			for py_socket in self.actives_list:
			#
				if (self.unqueue(self.actives_list, py_socket)): self.actives.release()
			#
		#

		self.synchronized.release()
	#

	def get_status(self):
	#
		"""
Return the socket status.

:return: (bool) True if active and listening
:since:  v0.1.00
		"""

		return self.active
	#

	def handle_accept(self):
	#
		"""
python.org: Called on listening channels (passive openers) when a connection
can be established with a new remote endpoint that has issued a connect()
call for the local endpoint.

:since: v0.1.00
		"""

		if (self.active and self.listener_handle_connections):
		#
			try:
			#
				var_socket = self.accept()
				if (self.active_queue(var_socket[0])): self.active_activate(var_socket[0])
			#
			except direct_shutdown_exception as handled_exception:
			#
				exception = handled_exception.get_cause()

				if (exception == None and self.log_handler != None): self.log_handler.error(handled_exception)
				else: handled_exception.print_stack_trace()
			#
			except Exception as handled_exception:
			#
				if (self.log_handler == None): direct_shutdown_exception.print_current_stack_trace()
				else: self.log_handler.error(handled_exception)
			#
		#
	#

	def handle_close(self):
	#
		"""
python.org: Called when the socket is closed.

:since: v0.1.00
		"""

		if (self.active): self.stop()
	#

	def handle_connect(self):
	#
		"""
python.org: Called when the active opener's socket actually makes a
connection. Might send a "welcome" banner, or initiate a protocol
negotiation with the remote endpoint, for example.

:since: v0.1.00
		"""

		self.synchronized.acquire()

		if (self.active):
		#
			try: self.listen(self.queue_max)
			except: direct_shutdown_exception.print_current_stack_trace()

			self.synchronized.release()
		#
		else: self.synchronized.release()
	#

	def handle_read(self):
	#
		"""
python.org: Called when the asynchronous loop detects that a "read()" call
on the channel's socket will succeed.

:since: v0.1.00
		"""

		if ((not self.listener_handle_connections) and self.active):
		#
			try:
			#
				if (self.active_queue(self.listener_socket)): self.active_activate(self.listener_socket)
			#
			except Exception as handled_exception:
			#
				if (id == None): self.synchronized.release()

				if (isinstance(handled_exception, direct_shutdown_exception)):
				#
					exception = handled_exception.get_cause()

					if (exception == None and self.log_handler != None): self.log_handler.error(handled_exception)
					else: handled_exception.print_stack_trace()
				#
				elif (self.log_handler == None): direct_shutdown_exception.print_current_stack_trace()
				else: self.log_handler.error(handled_exception)
			#
		#
		else: self.synchronized.release()
	#

	def handle_expt(self):
	#
		"""
python.org: Called when there is out of band (OOB) data for a socket
connection. This will almost never happen, as OOB is tenuously supported and
rarely used.

:since: v0.1.00
		"""

		if (self.active): self.active_unqueue_all()
	#

	def start(self):
	#
		"""
Starts the prepared dispatcher in a new thread.

:since: v0.1.00
		"""

		Thread(target = self.run).start()
	#

	def run(self):
	#
		"""
Run the main loop for this server instance.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -dispatcher.run()- (#echo(__LINE__)#)")

		self.thread_local_check()

		if (self.stopping_hook != None):
		#
			stopping_hook = ("dNG.pas.status.shutdown" if (self.stopping_hook == "") else self.stopping_hook)
			direct_hooks.register(stopping_hook, self.thread_stop)
		#

		try:
		#
			self.synchronized.acquire()

			if (not self.active):
			#
				if (self.listener_handle_connections): self.listen(self.queue_max)
				self.active = True
			#

			self.synchronized.release()

			self.add_channel(self.local.sockets)
			asyncore.loop(5, map = self.local.sockets)
		#
		except direct_shutdown_exception as handled_exception:
		#
			if (self.active):
			#
				exception = handled_exception.get_cause()
				if (exception != None and self.log_handler != None): self.log_handler.error(exception)
			#

			self.stop()
		#
		except Exception as handled_exception:
		#
			if (self.active):
			#
				if (self.log_handler == None): direct_shutdown_exception.print_current_stack_trace()
				else: self.log_handler.error(handled_exception)
			#

			self.stop()
		#
	#

	def set_active(self, status):
	#
		"""
Sets the status for the listener.

:param status: New status

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -dispatcher.set_active(status)- (#echo(__LINE__)#)")

		self.synchronized.acquire()
		if (self.active != status): self.active = status
		self.synchronized.release()
	#

	def set_log_handler(self, log_handler):
	#
		"""
Sets the log_handler.

:param log_handler: log_handler to use

:since: v0.1.00
		"""

		self.log_handler = log_handler
	#

	def stop(self):
	#
		"""
Stops the listener and unqueues all running sockets.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -dispatcher.stop()- (#echo(__LINE__)#)")

		self.synchronized.acquire()

		if (self.active):
		#
			self.active = False

			if (self.stopping_hook != None and len(self.stopping_hook) > 0): direct_hooks.unregister(self.stopping_hook, self.thread_stop)
			self.stopping_hook = ""

			self.synchronized.release()

			try: self.close()
			except: pass

			self.active_unqueue_all()
		#
		else: self.synchronized.release()
	#

	def thread_local_check(self):
	#
		"""
For thread safety some variables are defined per thread. This method makes
sure that these variables are defined.

:since: v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -dispatcher.thread_local_check()- (#echo(__LINE__)#)")

		if (self.local == None): self.local = local()
		if (not hasattr(self.local, "sockets")): self.local.sockets = { }
	#

	def thread_stop(self, params = None, last_return = None):
	#
		"""
Stops the running server instance by a stopping hook call.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v1.0.0
		"""

		self.stop()
		return last_return
	#

	def unqueue(self, queue, py_socket):
	#
		"""
Unqueues a previously active socket connection.

:param queue: Queue object
:param id: Queue ID

:return: (bool) True on success
:since:  v0.1.00
		"""

		var_return = False

		self.synchronized.acquire()

		if (queue != None and py_socket in queue):
		#
			queue.remove(py_socket)
			self.synchronized.release()

			var_return = True

			if (self.listener_handle_connections):
			#
				try: py_socket.close()
				except: pass
			#
		#
		else: self.synchronized.release()

		return var_return
	#

	def writable(self):
	#
		"""
python.org: Called each time around the asynchronous loop to determine
whether a channel's socket should be added to the list on which write events
can occur. The default method simply returns True, indicating that by
default, all channels will be interested in write events.

:return: (bool) Always False
:since:  v0.1.00
		"""

		return False
	#

	@staticmethod
	def prepare_socket(listener_type, *listener_data):
	#
		"""
Prepare socket returns a bound socket for the given listener data.

:param listener_type: Listener type
:param listener_data: Listener data

:since: v0.1.00
		"""

		var_return = None

		if (listener_type == socket.AF_INET or listener_type == socket.AF_INET6):
		#
			listener_data[0] = direct_str(listener_data[0])
			listener_data = ( listener_data[0], listener_data[1] )

			var_return = socket.socket(listener_type, socket.SOCK_STREAM)
			var_return.setblocking(0)
			if (hasattr(socket, "SO_REUSEADDR")): var_return.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			var_return.bind(listener_data)
		#
		elif (listener_type == socket.AF_UNIX):
		#
			unixsocket_pathname = path.normpath(direct_str(listener_data[0]))
			if (os.access(unixsocket_pathname, os.F_OK)): os.unlink(unixsocket_pathname)

			var_return = socket.socket(listener_type, socket.SOCK_STREAM)
			if (hasattr(socket, "SO_REUSEADDR")): var_return.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			var_return.bind(unixsocket_pathname)

			socket_chmod = 0
			socket_chmod_value = int(direct_settings.get("pas_server_chmod_unix_sockets", "600"), 8)

			if ((1000 & socket_chmod_value) == 1000): socket_chmod |= stat.S_ISVTX
			if ((2000 & socket_chmod_value) == 2000): socket_chmod |= stat.S_ISGID
			if ((4000 & socket_chmod_value) == 4000): socket_chmod |= stat.S_ISUID
			if ((0o100 & socket_chmod_value) == 0o100): socket_chmod |= stat.S_IXUSR
			if ((0o200 & socket_chmod_value) == 0o200): socket_chmod |= stat.S_IWUSR
			if ((0o400 & socket_chmod_value) == 0o400): socket_chmod |= stat.S_IRUSR
			if ((0o010 & socket_chmod_value) == 0o010): socket_chmod |= stat.S_IXGRP
			if ((0o020 & socket_chmod_value) == 0o020): socket_chmod |= stat.S_IWGRP
			if ((0o040 & socket_chmod_value) == 0o040): socket_chmod |= stat.S_IRGRP
			if ((0o001 & socket_chmod_value) == 0o001): socket_chmod |= stat.S_IXOTH
			if ((0o002 & socket_chmod_value) == 0o002): socket_chmod |= stat.S_IWOTH
			if ((0o004 & socket_chmod_value) == 0o004): socket_chmod |= stat.S_IROTH

			os.chmod(unixsocket_pathname, socket_chmod)
		#

		return var_return
	#
#

##j## EOF