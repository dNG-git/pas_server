# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.net.server.Handler
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

from select import select
from threading import Thread
import time

from dNG.pas.data.binary import Binary
from dNG.pas.data.settings import Settings
from dNG.pas.module.named_loader import NamedLoader
from .shutdown_exception import ShutdownException

class Handler(Thread):
#
	"""
Active thread for the dNG server infrastructure.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self):
	#
		"""
Constructor __init__(Handler)

:since: v0.1.00
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
		self.data = ""
		"""
Data buffer
		"""
		self.log_handler = NamedLoader.get_singleton("dNG.pas.data.logging.LogHandler", False)
		"""
The log_handler is called whenever debug messages should be logged or errors
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
		self.timeout = int(Settings.get("pas_server_socket_data_timeout", 0))
		"""
Request timeout value
		"""

		if (self.timeout < 1): self.timeout = int(Settings.get("pas_global_socket_data_timeout", 30))
	#

	def get_address(self, flush = False):
	#
		"""
Returns the address for the data received.

:param flush: True to delete the cached address after returning it.

:return: (mixed) Address data based on socket family
:since:  v0.1.00
		"""

		var_return = self.address

		if (flush):
		#
			self.address = None
			self.address_family = None
		#

		return var_return
	#

	def get_address_family(self):
	#
		"""
Returns the socket family for the address returned by "get_address()".

:return: (int) Socket family
:since:  v0.1.00
		"""

		return self.address_family
	#

	def get_data(self, size, force_size = False):
	#
		"""
Returns data read from the socket.

:since: v0.1.00
		"""

		var_return = None

		data = None
		data_size = 0
		timeout_time = (time.time() + self.timeout)

		try:
		#
			while ((data == None or (force_size and data_size < size)) and time.time() < timeout_time):
			#
				select([ self.socket.fileno() ], [ ], [ ], self.timeout)

				if (self.address == None):
				#
					( data, self.address ) = self.socket.recvfrom(size)
					self.address_family = self.socket.family
				#
				else: data = self.socket.recv(size)

				if (len(data) > 0):
				#
					self.data += Binary.raw_str(data)
					data_size = len(Binary.bytes(data))
				#
				else: data = None
			#
		#
		except: pass

		if (self.data != None and len(self.data) > 0):
		#
			var_return = self.data
			self.data = ""
		#

		if (force_size and data_size < size): raise OSError("get_data({0:d})".format(size), 5)
		else: return var_return
	#

	def set_data (self, data):
	#
		"""
Sets data returned next time "get_data()" is called. It is placed in front of
the data buffer.

:access: protected
:since:  v0.1.00
		"""

		self.data = (Binary.str(data) + self.data)
	#

	def run(self):
	#
		"""
Placeholder "run()" method calling "thread_run()". Do not override.

:access: protected
:since:  v0.1.00
		"""

		try: self.thread_run()
		except ShutdownException: self.server.stop()
		except Exception as handled_exception:
		#
			if (self.log_handler != None): self.log_handler.error(handled_exception)
		#

		self.server.active_unqueue(self.socket)
	#

	def set_instance_data(self, server, socket):
	#
		"""
Sets relevant instance data for this thread and address connection.

:param server: Server instance
:param socket: Active socket resource
:param id: Assigned ID

:return: (mixed) Thread assigned ID if any; False on error
:since:  v0.1.00
		"""

		self.server = server

		self.socket = socket
		self.socket.settimeout(self.timeout)
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

	def thread_run (self):
	#
		"""
Placeholder "thread_run()" method doing nothing.

:access: protected
:since:  v0.1.00
		"""

		if (self.log_handler != None): self.log_handler.debug("#echo(__FILEPATH__)# -handler->thread_run()- (#echo(__LINE__)#)")
	#

	def write_data(self, data):
	#
		"""
Write data to the socket.

:param data: Data to be written

:return: (bool) True on success
:since:  v1.0.0
		"""

		var_return = True

		data = Binary.bytes(data)

		if (len(data) > 0):
		#
			try: self.socket.sendall(data)
			except Exception as handled_exception:
			#
				if (self.log_handler != None): self.log_handler.error(handled_exception)
				var_return = False
			#
		#

		return var_return
	#
#

##j## EOF