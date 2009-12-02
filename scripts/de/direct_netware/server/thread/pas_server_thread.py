# -*- coding: utf-8 -*-
##j## BOF

"""/*n// NOTE
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
NOTE_END //n*/"""
"""
de.direct_netware.server.thread.pas_server_thread

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

from threading import Thread

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
	oob_data = None
	"""
Out of band data cache
	"""
	server = None
	"""
Server instance
	"""
	socket = None
	"""
Socket resource
	"""

	def __init__ (self):
	#
		"""
Constructor __init__ (direct_server_thread)

@since v0.1.00
		"""

		super(direct_server_thread,self).__init__ ()
		self.active_id = -1
		self.server = None
		self.socket = None
	#

	def run (self):
	#
		"""
Placeholder "run ()" method that only unqueues the current thread again.

@since v0.1.00
		"""

		self.server.active_unqueue (self.active_id)
	#

	def get_socket (self):
	#
		"""
Returns the socket connected to this thread.

@since v0.1.00
		"""

		return self.socket
	#

	def set_instance_data (self,f_server,f_socket,f_id = -1):
	#
		"""
Sets relevant instance data for this thread and socket connection.

@param  f_server Server instance
@param  f_socket Active socket resource
@param  f_id Assigned ID
@return (mixed) Thread assigned ID if any; False on error
@since  v0.1.00
		"""

		self.active_id = f_id
		self.server = f_server
		self.socket = f_socket

		self.start ()

		if (f_id < 0): return -1
		else: return False
	#

	def set_oob_data (self,f_oob_data):
	#
		"""
This method is used to set data received out of band.

@param f_oob_data Received out of band data
@since v0.1.00
		"""

		self.oob_data = f_oob_data
	#
#

##j## EOF