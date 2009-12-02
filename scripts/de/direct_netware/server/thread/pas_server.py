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
de.direct_netware.server.thread.pas_server

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

from de.direct_netware.server.classes.exception.dNGServerDeactivation import dNGServerDeactivation
from pas_server_thread import direct_server_thread
from threading import Thread
from socket import AF_INET,AF_INET6,AF_UNIX,SOCK_STREAM
import asyncore,sys,thread,time

_direct_complete_server_stream_err = None

class direct_server (asyncore.dispatcher):
#
	"""
The "direct_server" infrastructure allows an application to provide active
listeners, threaded connection establishment and to queue a defined amount
of requests transparently.

@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_complete
@subpackage server
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;gpl
            GNU General Public License 2
	"""

	active = False
	"""
Listener state
	"""
	actives = 0
	"""
Active counter
	"""
	actives_array = [ None ]
	"""
Active queue
	"""
	actives_max = 0
	"""
Active queue maximum
	"""
	active_handler = None
	"""
Active queue handler
	"""
	listener_data = None
	"""
Listener bind data
	"""
	queue_handler = None
	"""
Passive queue handler
	"""
	queue_max = 0
	"""
Passive queue maximum
	"""
	synchronized = None
	"""
Thread safety lock
	"""

	def __init__ (self,f_listener_type,f_listener_bind_address,f_listener_bind_port,f_active_handler,f_threads_active = 5,f_queue_handler = None,f_threads_queued = 10,f_stream_err = sys.stderr):
	#
		"""
Constructor __init__ (direct_server)

@param f_listener_type Listener type
@param f_listener_bind_address Listener address
@param f_listener_bind_port Port if applicable
@param f_active_handler Thread to be used for activated connections
@param f_threads_active Allowed simultaneous threads
@param f_queue_handler Thread to be used for queued connections
@param f_threads_queued Allowed queued threads
@param f_stream_err Error stream
@since v0.1.00
		"""

		asyncore.dispatcher.__init__ (self)

		direct_server.set_stream_err (f_stream_err)

		self.active = False
		if (issubclass (f_active_handler,direct_server_thread)): self.active_handler = f_active_handler
		self.actives = 0
		self.actives_array = [ None ] * f_threads_active
		self.actives_max = f_threads_active
		if ((f_queue_handler != None) and (isinstance (f_queue_handler,direct_server_thread))): self.queue_handler = f_queue_handler
		self.queue_max = f_threads_queued
		self.synchronized = thread.allocate_lock ()

		try:
		#
			if ((f_listener_type == AF_INET) or (f_listener_type == AF_INET6)):
			#
				self.listener_data = (f_listener_bind_address,f_listener_bind_port)
				f_socket_type = SOCK_STREAM

				self.create_socket (f_listener_type,f_socket_type)
				self.set_reuse_addr ()
				self.bind (self.listener_data)
			#
			elif (f_listener_type == AF_UNIX):
			#
				self.listener_data = f_listener_bind_address
				f_socket_type = SOCK_STREAM

				self.create_socket (f_listener_type,f_socket_type)
				self.set_reuse_addr ()
				self.bind (self.listener_data)
			#
		#
		except dNGServerDeactivation,f_handled_exception:
		#
			f_exception = f_handled_exception.get_cause ()
			if (f_exception != None): f_handled_exception.print_stack_trace (direct_server.get_stream_err ())
		#
		except Exception,f_handled_exception: dNGServerDeactivation.print_current_stack_trace (direct_server.get_stream_err ())
	#

	def handle_accept (self):
	#
		"""
python.org: Called on listening channels (passive openers) when a connection
can be established with a new remote endpoint that has issued a connect()
call for the local endpoint.

@since v0.1.00
		"""

		if (self.active):
		#
			try:
			#
				(f_request,f_remote_address) = self.accept ()

				f_id = self.active_queue (f_request)

				if (f_id >= 0):
				#
					f_handler = self.active_handler.__new__ (self.active_handler)
					f_handler.__init__ ()
					f_handler.set_instance_data (self,f_request,f_id)
				#
				elif (f_id == -1):
				#
					if (not self.active):
					#
						try: f_request.close ()
						except error,f_unhandled_exception: pass
					#
				#
			#
			except dNGServerDeactivation,f_handled_exception:
			#
				f_exception = f_handled_exception.get_cause ()
				if (f_exception != None): f_handled_exception.print_stack_trace (direct_server.get_stream_err ())
			#
			except Exception,f_handled_exception: dNGServerDeactivation.print_current_stack_trace (direct_server.get_stream_err ())
		#
	#

	def handle_close (self):
	#
		"""
python.org: Called when the socket is closed.

@since v0.1.00
		"""

		if (self.active): self.stop ()
	#

	def handle_connect (self):
	#
		"""
python.org: Called when the active opener's socket actually makes a
connection. Might send a "welcome" banner, or initiate a protocol
negotiation with the remote endpoint, for example.

@since v0.1.00
		"""

		if (self.active):
		#
			try: self.listen (self.queue_max)
			except Exception,f_handled_exception: dNGServerDeactivation.print_current_stack_trace (direct_server.get_stream_err ())
		#
	#

	def handle_read (self):
	#
		"""
python.org: Called when the asynchronous loop detects that a "read ()" call
on the channel's socket will succeed.

@since v0.1.00
		"""

		pass
	#

	def handle_expt (self):
	#
		"""
python.org: Called when there is out of band (OOB) data for a socket
connection. This will almost never happen, as OOB is tenuously supported and
rarely used.

@since v0.1.00
		"""

		if (self.active):
		#
			self.synchronized.acquire ()
			self.active_unqueue_all ()
			self.synchronized.release ()
		#
	#

	def writable (self):
	#
		"""
python.org: Called each time around the asynchronous loop to determine
whether a channel's socket should be added to the list on which write events
can occur. The default method simply returns True, indicating that by
default, all channels will be interested in write events.

@return (bool) Always False
@since  v0.1.00
		"""

		return False
	#

	def active_queue (self,f_socket):
	#
		"""
Put's an socket on the active queue or tries to temporarily save it on the
passive queue.

@param  f_socket Active socket resource
@return (mixed) Selected queue ID (> -1) on success; True if passively queued.
@since  v0.1.00
		"""

		f_return = -1

		if (self.active):
		#
			while (f_return < 0):
			#
				f_return = self.queue (self.actives_array,self.actives_max,f_socket)

				if (f_return < 0):
				#
					if ((self.queue_handler == None) or (self.queue_running >= self.queue_max)): time.sleep (0.5)
					else:
					#
						try:
						#
							f_handler = self.queue_handler.__new__ (self.queue_handler)
							f_handler.__init__ ()
							f_return = f_handler.set_instance_data (self,f_socket)
						#
						except Exception,f_unhandled_exception: f_return = -1
					#
				#
				else: self.actives += 1
			#
		#

		return f_return;
	#

	def active_unqueue (self,f_id):
	#
		"""
Unqueue the given ID from the active queue.

@param f_id Queue ID
@since v0.1.00
		"""

		self.synchronized.acquire ()
		if (self.unqueue (self.actives_array,f_id)): self.actives -= 1
		self.synchronized.release ()
	#

	def active_unqueue_all (self):
	#
		"""
Unqueue all entries from the active queue (canceling running processes).

@param f_id Queue ID
@since v0.1.00
		"""

		self.unqueue_all (self.actives_array,self.actives_max)
		self.actives = 0
	#

	def get_listener (self):
	#
		"""
Return the socket listener.

@return (object) Listener
@since  v0.1.00
		"""

		return self
	#

	def get_status (self):
	#
		"""
Return the socket status.

@return (bool) True if active and listening
@since  v0.1.00
		"""

		return self.active
	#

	def queue (self,f_queue,f_queue_max,f_socket):
	#
		"""
Tries to find a unused queue position to accept the current socket request.

@return (int) Queue ID (> -1) on success
@since  v0.1.00
		"""

		f_return = -1

		for f_i in range (f_queue_max):
		#
			if ((f_return < 0) and (f_queue[f_i] == None)):
			#
				f_queue[f_i] = f_socket
				f_return = f_i
			#
		#

		return f_return
	#

	def run (self):
	#
		"""
Activates the current listener.

@since v0.1.00
		"""

		self.synchronized.acquire ()

		if (not self.active):
		#
			self.active = True
			self.synchronized.release ()

			asyncore.loop ()
		#
		else: self.synchronized.release ()
	#

	def set_active (self,f_status):
	#
		"""
Sets the status for the listener.

@param f_status New status
@since v0.1.00
		"""

		self.synchronized.acquire ()
		self.active = f_status
		self.synchronized.release ()
	#

	def set_queue (self):
	#
		"""
Adds a passive queue to the counter.

@since v0.1.00
		"""

		self.synchronized.acquire ()
		self.queue_running += 1
		self.synchronized.release ()
	#

	def set_unqueue (self):
	#
		"""
Removes a passive queue from the counter.

@since v0.1.00
		"""

		self.synchronized.acquire ()
		if (queue_running > 0): self.queue_running -= 1
		self.synchronized.release ()
	#

	def stop (self):
	#
		"""
Stops the listener and unqueues all running sockets.

@since v0.1.00
		"""

		self.synchronized.acquire ()

		if (self.active):
		#
			self.active = False

			try: self.close ()
			except error,f_unhandled_exception: pass
		#

		self.active_unqueue_all ()
		self.synchronized.release ()
	#

	def unqueue (self,f_queue,f_id):
	#
		"""
Unqueues a previously active socket connection.

@param  f_queue Queue object
@param  f_id Queue ID
@return (bool) True on success
@since  v0.1.00
		"""

		f_return = False

		if (f_queue[f_id] != None):
		#
			f_return = True
			f_socket = f_queue[f_id]
			f_queue[f_id] = None

			try: f_socket.close ()
			except error,f_unhandled_exception: pass
		#

		return f_return
	#

	def unqueue_all (self,f_queue,f_queue_max):
	#
		"""
Unqueues all entries from the given queue.

@param f_queue Queue object
@param f_queue_max Highest queue ID
@since v0.1.00
		"""

		for f_i in range (f_queue_max):
		#
			if (f_queue[f_i] != None): self.unqueue (f_queue,f_i)
		#
	#

	@staticmethod
	def get_stream_err ():
	#
		"""
Return the thread save error stream object.

@return (object) Currently set error stream object
@since  v0.1.00
		"""

		global _direct_complete_server_stream_err
		return _direct_complete_server_stream_err
	#

	@staticmethod
	def set_stream_err (f_stream_err):
	#
		"""
Sets a error stream object and makes it thread save if needed.

@param f_stream_err Error stream object
@since v0.1.00
		"""

		global _direct_complete_server_stream_err
		# TODO: Pack the IO object into a thread safe one
		_direct_complete_server_stream_err = f_stream_err
	#
#

##j## EOF