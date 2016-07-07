# -*- coding: utf-8 -*-
##j## BOF

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

from select import select
from socket import SHUT_RDWR
from time import time

from dNG.data.binary import Binary
from dNG.data.settings import Settings
from dNG.module.named_loader import NamedLoader
from dNG.plugins.hook import Hook
from dNG.runtime.io_exception import IOException
from dNG.runtime.thread import Thread

from .shutdown_exception import ShutdownException

class Handler(Thread):
#
	"""
Active thread for the dNG server infrastructure.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	# pylint: disable=unused-argument

	def __init__(self):
	#
		"""
Constructor __init__(Handler)

:since: v0.2.00
		"""

		Thread.__init__(self)

		self.active_id = -1
		"""
Queue ID
		"""
		self.address = None
		"""
Address of the received data
		"""
		self.address_family = None
		"""
Address family of the received data
		"""
		self.data = Binary.BYTES_TYPE()
		"""
Data buffer
		"""
		self.log_handler = NamedLoader.get_singleton("dNG.data.logging.LogHandler", False)
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.server = None
		"""
Server instance
		"""
		self.socket = None
		"""
Socket instance
		"""
		self.timeout = int(Settings.get("pas_global_server_socket_data_timeout", 0))
		"""
Request timeout value
		"""

		if (self.timeout < 1): self.timeout = int(Settings.get("pas_global_socket_data_timeout", 30))
	#

	def __enter__(self):
	#
		"""
python.org: Enter the runtime context related to this object.

:since: v0.2.00
		"""

		Hook.register("dNG.pas.Status.onShutdown", self.stop)
	#

	def __exit__(self, exc_type, exc_value, traceback):
	#
		"""
python.org: Exit the runtime context related to this object.

:return: (bool) True to suppress exceptions
:since:  v0.2.00
		"""

		Hook.unregister("dNG.pas.Status.onShutdown", self.stop)
		return False
	#

	def get_address(self, flush = False):
	#
		"""
Returns the address for the data received.

:param flush: True to delete the cached address after returning it.

:return: (mixed) Address data based on socket family
:since:  v0.2.00
		"""

		_return = self.address

		if (flush):
		#
			self.address = None
			self.address_family = None
		#

		return _return
	#

	def get_address_family(self):
	#
		"""
Returns the socket family for the address.

:return: (int) Socket family
:since:  v0.2.00
		"""

		return self.address_family
	#

	def get_data(self, size, force_size = False):
	#
		"""
Returns data read from the socket.

:param size: Bytes to read
:param force_size: True to wait for data until the given size has been
                   received.

:return: (bytes) Data received
:since:  v0.2.00
		"""

		# pylint: disable=broad-except

		_return = Binary.BYTES_TYPE()

		data = None
		data_size = 0
		timeout_time = (time() + self.timeout)

		while (self.socket is not None
		       and (data is None or (force_size and data_size < size))
		       and time() < timeout_time
		      ):
		#
			try:
			#
				select([ self.socket.fileno() ], [ ], [ ], self.timeout)

				if (self.address is None):
				#
					( data, self.address ) = self.socket.recvfrom(size)
					self.address_family = self.socket.family
				#
				else: data = self.socket.recv(size)
			#
			except Exception: break

			if (len(data) > 0):
			#
				self.data += data
				data_size = len(self.data)
			#
			else: data = None
		#

		if (self.data is not None and len(self.data) > 0):
		#
			_return = self.data
			self.data = Binary.BYTES_TYPE()
		#

		if (force_size and data_size < size): raise IOException("Received data size is smaller than the expected size of {0:d} bytes".format(size))
		return _return
	#

	def _set_data(self, data):
	#
		"""
Sets data returned next time "get_data()" is called. It is placed in front of
the data buffer.

:param data: Data to be buffered

:since: v0.2.00
		"""

		self.data = (Binary.bytes(data) + self.data)
	#

	def run(self):
	#
		"""
Placeholder "run()" method calling "_thread_run()". Do not override.

:since: v0.2.00
		"""

		try:
		#
			with self: self._thread_run()
		#
		except ShutdownException: self.server.stop()
		except Exception as handled_exception:
		#
			if (self.log_handler is not None): self.log_handler.error(handled_exception, context = "pas_server")
		#

		self.server.active_unqueue(self.socket)
	#

	def set_instance_data(self, server, socket):
	#
		"""
Sets relevant instance data for this thread and address connection.

:param server: Server instance
:param socket: Active socket resource

:return: (mixed) Thread assigned ID if any; False on error
:since:  v0.2.00
		"""

		self.server = server

		self.socket = socket
		self.socket.settimeout(self.timeout)
	#

	def set_log_handler(self, log_handler):
	#
		"""
Sets the LogHandler.

:param log_handler: LogHandler to use

:since: v0.2.00
		"""

		self.log_handler = log_handler
	#

	def stop(self, params = None, last_return = None):
	#
		"""
Stop the thread by actually closing the underlying socket.

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since: v0.2.00
		"""

		# pylint: disable=broad-except

		try: self.socket.shutdown(SHUT_RDWR)
		except Exception: pass

		try: self.socket.close()
		except Exception: pass

		self.socket = None

		return last_return
	#

	def _thread_run(self):
	#
		"""
Placeholder "_thread_run()" method doing nothing.

:since: v0.2.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._thread_run()- (#echo(__LINE__)#)", self, context = "pas_server")
	#

	def write_data(self, data):
	#
		"""
Write data to the socket.

:param data: Data to be written

:return: (bool) True on success
:since:  v0.2.00
		"""

		# pylint: disable=broad-except

		_return = True

		data = Binary.bytes(data)

		if (self.socket is not None and len(data) > 0):
		#
			try: self.socket.sendall(data)
			except Exception as handled_exception:
			#
				if (self.log_handler is not None): self.log_handler.error(handled_exception, context = "pas_server")
				_return = False
			#
		#

		return _return
	#
#

##j## EOF