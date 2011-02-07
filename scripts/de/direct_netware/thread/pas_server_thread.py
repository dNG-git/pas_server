# -*- coding: utf-8 -*-
##j## BOF

"""
de.direct_netware.thread.pas_server_thread

@internal   We are using epydoc (JavaDoc style) to automate the
            documentation process for creating the Developer's Manual.
            Use the following line to ensure 76 character sizes:
----------------------------------------------------------------------------
@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_complete
@subpackage server
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;gpl
            GNU General Public License 2
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.php?pas

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.php?licenses;gpl
----------------------------------------------------------------------------
#echo(pasCompleteServerVersion)#
pas/#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from socket import error as socket_error
from threading import Thread
import time

from de.direct_netware.classes.pas_globals import direct_globals
from de.direct_netware.classes.pas_logger import direct_logger
from de.direct_netware.classes.pas_pythonback import *

class direct_server_thread (Thread):
#
	"""
Active thread for the "direct_server" infrastructure.

@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_complete
@subpackage server
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;gpl
            GNU General Public License 2
	"""

	active_id = -1
	"""
Queue ID
	"""
	data = ""
	"""
Daat buffer
	"""
	debug = None
	"""
Debug message container
	"""
	server = None
	"""
Server instance
	"""
	timeout = 5
	"""
Request timeout value
	"""

	def __init__ (self):
	#
		"""
Constructor __init__ (direct_server_thread)

@since v0.1.00
		"""

		Thread.__init__ (self)

		self.active_id = -1
		self.data = ""
		self.daemon = True
		self.debug = direct_globals['debug']
		self.server = None
		self.socket = None

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server_thread.__init__ (direct_server_thread)- (#echo(__LINE__)#)")

		if ("pas_socket_data_timeout" in direct_globals['settings']): self.timeout = direct_globals['settings']['pas_socket_data_timeout']
		else: self.timeout = 5
	#

	def get_data (self,size = 0,force_size = False):
	#
		"""
Returns data read from the socket.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server_thread.get_data ({0:d},force_size)- (#echo(__LINE__)#)".format (size))
		f_return = None

		f_data = None
		f_data_size = 0
		f_timeout_time = (time.time () + self.timeout)

		while (((f_data == None) or ((force_size) and (f_data_size < size))) and (f_timeout_time > (time.time ()))):
		#
			try:
			#
				f_data = self.socket.recv (size)

				if (len (f_data) > 0):
				#
					self.data += direct_str (f_data)
					f_data_size = len (direct_bytes (self.data))
				#
				else: f_data = None
			#
			except socket_error: f_data = None
		#

		if (len (self.data) > 0):
		#
			f_return = self.data
			self.data = ""
		#

		if ((f_return != None) and ((not force_size) or (size <= f_data_size))): return f_return
		else: raise socket_error ("get_data ({0:d})".format (size))
	#

	def set_data (self,data):
	#
		"""
Sets data returned next time "get_data ()" is called. It is placed in front of
the data buffer.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server_thread.set_data (data)- (#echo(__LINE__)#)")
		self.data = ((direct_str (data)) + self.data)
	#

	def run (self):
	#
		"""
Placeholder "run ()" method that only unqueues the current thread again.

@since v0.1.00
		"""

		try: self.thread_run ()
		except Exception as f_handled_exception: direct_logger.critical (f_handled_exception)

		self.server.active_unqueue (self.active_id)
	#

	def set_instance_data (self,server,socket,id = -1):
	#
		"""
Sets relevant instance data for this thread and address connection.

@param  server Server instance
@param  socket Active socket resource
@param  id Assigned ID
@return (mixed) Thread assigned ID if any; False on error
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server_thread.set_instance_data (server,socket,{0:d})- (#echo(__LINE__)#)".format (id))

		self.active_id = id
		self.server = server

		self.socket = socket
		self.socket.setblocking (0)

		if (id < 0): return -1
		else: return True
	#

	def thread_run (self):
	#
		"""
Placeholder "run ()" method that only unqueues the current thread again.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server_thread->thread_run ()- (#echo(__LINE__)#)")
	#

	def write_data (self,data):
	#
		"""
Write data to the socket.

@param  data Data to be written
@return (bool) True on success
@since  v1.0.0
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server_thread.write_data (data)- (#echo(__LINE__)#)")
		f_return = True

		f_data = direct_bytes (data)

		if (len (f_data) > 0):
		#
			try: self.socket.sendall (f_data)
			except socket_error as f_handled_exception:
			#
				direct_logger.critical (f_handled_exception)
				f_return = False
			#
		#

		return f_return
	#
#

##j## EOF