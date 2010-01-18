# -*- coding: utf-8 -*-
##j## BOF

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

from exceptions import EOFError
from twisted.internet import threads,protocol,reactor
from threading import Event,RLock

class direct_server_thread (protocol.Protocol):
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
	address = None
	"""
Client address
	"""
	data = ""
	"""
Client address
	"""
	data_event = None
	"""
Server instance
	"""
	server = None
	"""
Server instance
	"""
	synchronized = None
	"""
Server instance
	"""

	def __init__ (self):
	#
		"""
Constructor __init__ (direct_server_thread)

@since v0.1.00
		"""

		self.active_id = -1
		self.address = None
		self.data = ""
		self.data_event = Event ()
		self.server = None
		self.synchronized = RLock ()
	#

	def dataReceived (self,data):
	#
		"""
twistedmatrix.com: Called whenever data is received.

@since v0.1.00
		"""

		self.synchronized.acquire ()
		self.data += data
		self.data_event.set ()
		self.synchronized.release ()
	#

	def loseConnection (self):
	#
		"""
twistedmatrix.com: Close my connection, after writing all pending data.

@since v0.1.00
		"""

		self.transport.loseConnection ()
	#

	def get_address (self):
	#
		"""
Returns the address connected to this thread.

@since v0.1.00
		"""

		return self.address
	#

	def get_data (self,f_size = 0):
	#
		"""
Returns the address connected to this thread.

@since v0.1.00
		"""

		f_return = None

		while (f_return == None):
		#
			self.synchronized.acquire ()
			f_data_size = len (self.data)

			if (f_data_size > 0):
			#
				if (f_size > 0):
				#
					f_return = self.data[:f_size]
					self.data = self.data[f_size:]
				#
				else:
				#
					f_return = self.data
					self.data = ""
					self.data_event.clear ()
				#

				self.synchronized.release ()
			#
			else:
			#
				self.data_event.clear ()
				self.synchronized.release ()

				self.data_event.wait (1)
				if (not self.data_event.is_set ()): raise EOFError ("get_data (%i)" % f_size)
			#
		#

		return f_return
	#

	def run (self):
	#
		"""
Placeholder "run ()" method that only unqueues the current thread again.

@since v0.1.00
		"""

		self.server.active_unqueue (self.active_id)
	#

	def set_data (self,f_data):
	#
		"""
twistedmatrix.com: Called whenever data is received.

@since v0.1.00
		"""

		self.synchronized.acquire ()
		self.data = f_data + self.data
		self.synchronized.release ()
	#

	def set_instance_data (self,f_server,f_address,f_id = -1):
	#
		"""
Sets relevant instance data for this thread and address connection.

@param  f_server Server instance
@param  f_address Active address resource
@param  f_id Assigned ID
@return (mixed) Thread assigned ID if any; False on error
@since  v0.1.00
		"""

		self.active_id = f_id
		self.address = f_address
		self.server = f_server

		threads.deferToThread (self.run)

		if (f_id < 0): return -1
		else: return True
	#

	def write_data (self,f_data):
	#
		"""
Write a message to the socket.

@param  f_msg Message
@return (bool) True on success
@since  v1.0.0
		"""

		f_return = True

		if (len (f_data) > 0):
		#
			try: reactor.callFromThread (self.transport.write,f_data)
			except Exception,f_handled_exception: f_return = False
		#

		return f_return
	#
#

##j## EOF