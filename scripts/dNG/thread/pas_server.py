# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.thread.pas_server

@internal   We are using epydoc (JavaDoc style) to automate the
            documentation process for creating the Developer's Manual.
            Use the following line to ensure 76 character sizes:
----------------------------------------------------------------------------
@author     direct Netware Group
@copyright  (C) direct Netware Group - All rights reserved
@package    pas_complete
@subpackage server
@since      v0.1.00
@license    http://www.direct-netware.de/redirect.php?licenses;mpl2
            Mozilla Public License, v. 2.0
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.php?pas

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.php?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasCompleteServerVersion)#
pas/#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from os import path
from threading import local,RLock,Thread
from time import sleep as time_sleep
import asyncore,os,stat,socket,sys

from dNG.classes.pas_globals import direct_globals
from dNG.classes.pas_logger import direct_logger
from dNG.classes.pas_pluginmanager import direct_plugin_hooks
from dNG.classes.pas_pythonback import direct_str
from dNG.classes.exception.dNGServerDeactivation import dNGServerDeactivation
from .pas_server_thread import direct_server_thread

_direct_complete_server = local ()
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
@license    http://www.direct-netware.de/redirect.php?licenses;mpl2
            Mozilla Public License, v. 2.0
	"""

	active = False
	"""
Listener state
	"""
	actives = 0
	"""
Active counter
	"""
	actives_list = [ None ]
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
	debug = None
	"""
Debug message container
	"""
	local = None
	"""
Local data handle
	"""
	queue_handler = None
	"""
Passive queue handler
	"""
	queue_max = 0
	"""
Passive queue maximum
	"""
	stopping_hook = ""
	synchronized = None
	"""
Thread safety lock
	"""
	waiting = 0
	"""
Thread safety lock
	"""

	def __init__ (self,listener_type,listener_bind_address,listener_bind_port,active_handler,threads_active = 5,queue_handler = None,threads_queued = 10,stream_err = sys.stderr,thread = False,thread_stopping_hook = None):
	#
		"""
Constructor __init__ (direct_server)

@param listener_type Listener type
@param listener_bind_address Listener address
@param listener_bind_port Port if applicable
@param active_handler Thread to be used for activated connections
@param threads_active Allowed simultaneous threads
@param queue_handler Thread to be used for queued connections
@param threads_queued Allowed queued threads
@param stream_err Error stream
@param thread Runs as a new thread
@param thread_stopping_hook Thread stopping hook definition
@since v0.1.00
		"""

		self.local = local ()
		self.thread_local_check ()

		asyncore.dispatcher.__init__ (self,map = self.local.sockets)

		self.debug = direct_globals['debug']
		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.__init__ (direct_server)- (#echo(__LINE__)#)")

		direct_server.stream_err_set (stream_err)

		if (issubclass (active_handler,direct_server_thread)): self.active_handler = active_handler
		self.actives = 0
		self.actives_list = [ None ] * threads_active
		self.actives_max = threads_active
		if ((queue_handler != None) and (isinstance (queue_handler,direct_server_thread))): self.queue_handler = queue_handler
		self.queue_max = threads_queued
		self.synchronized = RLock ()

		try:
		#
			listener_bind_address = direct_str (listener_bind_address)
			socket.setdefaulttimeout (int (direct_globals['settings'].get ("pas_socket_data_timeout",30)))

			if ((listener_type == socket.AF_INET) or (listener_type == socket.AF_INET6)):
			#
				direct_globals['logger'].write (direct_logger.INFO,"pas.server will listen on '{0}:{1:d}' for connections".format (listener_bind_address,listener_bind_port))

				self.local.listener_data = ( listener_bind_address,listener_bind_port )

				self.create_socket (listener_type,socket.SOCK_STREAM)
				self.set_reuse_addr ()
				self.bind (self.local.listener_data)
			#
			elif (listener_type == socket.AF_UNIX):
			#
				self.local.listener_data = path.normpath (listener_bind_address)
				if (os.access (self.local.listener_data,os.F_OK)): os.unlink (self.local.listener_data)

				direct_globals['logger'].write (direct_logger.INFO,"pas.server will listen at '{0}' for connections".format (listener_bind_address))

				self.create_socket (listener_type,socket.SOCK_STREAM)
				self.set_reuse_addr ()
				self.bind (self.local.listener_data)

				try:
				#
					f_chmod = 0
					f_chmod_value= int (direct_globals['settings'].get ("pas_chmod_unix_sockets","600"),8)

					if ((1000 & f_chmod_value) == 1000): f_chmod |= stat.S_ISVTX
					if ((2000 & f_chmod_value) == 2000): f_chmod |= stat.S_ISGID
					if ((4000 & f_chmod_value) == 4000): f_chmod |= stat.S_ISUID
					if ((0o100 & f_chmod_value) == 0o100): f_chmod |= stat.S_IXUSR
					if ((0o200 & f_chmod_value) == 0o200): f_chmod |= stat.S_IWUSR
					if ((0o400 & f_chmod_value) == 0o400): f_chmod |= stat.S_IRUSR
					if ((0o010 & f_chmod_value) == 0o010): f_chmod |= stat.S_IXGRP
					if ((0o020 & f_chmod_value) == 0o020): f_chmod |= stat.S_IWGRP
					if ((0o040 & f_chmod_value) == 0o040): f_chmod |= stat.S_IRGRP
					if ((0o001 & f_chmod_value) == 0o001): f_chmod |= stat.S_IXOTH
					if ((0o002 & f_chmod_value) == 0o002): f_chmod |= stat.S_IWOTH
					if ((0o004 & f_chmod_value) == 0o004): f_chmod |= stat.S_IROTH

					os.chmod (self.local.listener_data,f_chmod)
				#
				except Exception as f_handled_exception: direct_globals['logger'].write (direct_logger.CRITICAL,f_handled_exception)
			#
		#
		except dNGServerDeactivation as f_handled_exception:
		#
			f_exception = f_handled_exception.get_cause ()

			if (f_exception == None): direct_globals['logger'].write (direct_logger.CRITICAL,f_handled_exception)
			else: f_handled_exception.print_stack_trace (direct_server.stream_err_get ())
		#
		except Exception as f_handled_exception:
		#
			direct_globals['logger'].write (direct_logger.CRITICAL,f_handled_exception)
			dNGServerDeactivation.print_current_stack_trace (direct_server.stream_err_get ())
		#

		if ((thread) and (thread_stopping_hook != None)):
		#
			direct_plugin_hooks.register (thread_stopping_hook,self.thread_stop_listener)
			self.stopping_hook = thread_stopping_hook

			self.start_listener ()
			self.run ()
		#
	#

	def handle_accept (self):
	#
		"""
python.org: Called on listening channels (passive openers) when a connection
can be established with a new remote endpoint that has issued a connect()
call for the local endpoint.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.handle_accept ()- (#echo(__LINE__)#)")

		self.synchronized.acquire ()

		if (self.active):
		#
			self.synchronized.release ()

			try:
			#
				f_remote_socket = self.accept ()

				if (f_remote_socket != None): f_id = self.active_queue (f_remote_socket[0])
				if (f_remote_socket != None): self.active_activate (f_id,f_remote_socket[0])
			#
			except dNGServerDeactivation as f_handled_exception:
			#
				f_exception = f_handled_exception.get_cause ()

				if (f_exception == None): direct_globals['logger'].write (direct_logger.CRITICAL,f_handled_exception)
				else: f_handled_exception.print_stack_trace (direct_server.stream_err_get ())
			#
			except Exception as f_handled_exception:
			#
				direct_globals['logger'].write (direct_logger.CRITICAL,f_handled_exception)
				dNGServerDeactivation.print_current_stack_trace (direct_server.stream_err_get ())
			#
		#
		else: self.synchronized.release ()
	#

	def handle_close (self):
	#
		"""
python.org: Called when the socket is closed.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.handle_close ()- (#echo(__LINE__)#)")

		self.synchronized.acquire ()

		if (self.active):
		#
			self.synchronized.release ()
			self.stop_listener ()
		#
		else: self.synchronized.release ()
	#

	def handle_connect (self):
	#
		"""
python.org: Called when the active opener's socket actually makes a
connection. Might send a "welcome" banner, or initiate a protocol
negotiation with the remote endpoint, for example.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.handle_connect ()- (#echo(__LINE__)#)")

		self.synchronized.acquire ()

		if (self.active):
		#
			try: self.listen (self.queue_max)
			except: dNGServerDeactivation.print_current_stack_trace (direct_server.stream_err_get ())

			self.synchronized.release ()
		#
		else: self.synchronized.release ()
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

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.handle_expt ()- (#echo(__LINE__)#)")

		self.synchronized.acquire ()

		if (self.active):
		#
			self.active_unqueue_all ()
			self.synchronized.release ()
		#
		else: self.synchronized.release ()
	#

	def run (self):
	#
		"""
Run the main loop for this server instance.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.run ()- (#echo(__LINE__)#)")

		self.thread_local_check ()
		asyncore.loop (5,map = self.local.sockets)
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

	def active_activate (self,id,py_socket):
	#
		"""
Unqueue the given ID from the active queue.

@param id Queue ID
@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.active_activate ({0:d},py_socket)- (#echo(__LINE__)#)".format (id))

		if (id >= 0):
		#
			f_handler = self.active_handler.__new__ (self.active_handler)
			f_handler.__init__ ()
			f_handler.set_instance_data (self,py_socket,id)
			f_handler.start ()

			if (self.debug != None): direct_globals['logger'].write (direct_logger.DEBUG,"pas.server started a new thread: {0:d} for {1!r}".format (id,f_handler))
		#
		elif ((id == -1) and (not self.active)):
		#
			try: py_socket.close ()
			except socket.error: pass
		#
	#

	def active_queue (self,py_socket):
	#
		"""
Put's an transport on the active queue or tries to temporarily save it on
the passive queue.

@param  py_socket Active socket resource
@return (mixed) Selected queue ID (> -1) on success; True if passively queued.
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.active_queue (py_socket)- (#echo(__LINE__)#)")
		f_return = -1

		self.synchronized.acquire ()

		if (self.active):
		#
			self.synchronized.release ()

			while (f_return == -1):
			#
				f_return = -1

				self.synchronized.acquire ()

				for f_i in range (self.actives_max):
				#
					if ((f_return < 0) and (self.actives_list[f_i] == None)):
					#
						f_return = f_i
						self.actives_list[f_i] = py_socket
						break
					#
				#

				self.synchronized.release ()

				if (f_return < 0):
				#
					self.synchronized.acquire ()

					if ((self.queue_handler != None) and (self.waiting < self.queue_max)):
					#
						try:
						#
							f_handler = self.queue_handler.__new__ (self.queue_handler)
							f_handler.__init__ ()
							f_handler.set_instance_data (self,py_socket)
							f_handler.start ()

							self.waiting += 1
							f_return = -2
						#
						except Exception as f_handled_exception:
						#
							direct_globals['logger'].write (direct_logger.CRITICAL,f_handled_exception)
							f_return = -1
						#
					#

					self.synchronized.release ()
				#
				else: self.actives += 1

				if (f_return == -1): time_sleep (0.1)
			#
		#
		else: self.synchronized.release ()

		return f_return
	#

	def active_unqueue (self,id):
	#
		"""
Unqueue the given ID from the active queue.

@param id Queue ID
@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.active_unqueue ({0:d})- (#echo(__LINE__)#)".format (id))

		self.synchronized.acquire ()
		if (self.unqueue (self.actives_list,id)): self.actives -= 1
		self.synchronized.release ()
	#

	def active_unqueue_all (self):
	#
		"""
Unqueue all entries from the active queue (canceling running processes).

@param f_id Queue ID
@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.active_unqueue_all ()- (#echo(__LINE__)#)")

		self.synchronized.acquire ()
		self.actives = 0

		if (self.actives_list != None):
		#
			for f_i in range (self.actives_max):
			#
				if (self.actives_list[f_i] != None): self.unqueue (self.actives_list,f_i)
			#

			self.actives_list = None
		#

		self.synchronized.release ()
	#

	def get_status (self):
	#
		"""
Return the socket status.

@return (bool) True if active and listening
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.get_status ()- (#echo(__LINE__)#)")

		self.synchronized.acquire ()
		f_return = self.active
		self.synchronized.release ()

		return f_return
	#

	def queue_unqueue (self,py_socket):
	#
		"""
Unqueue the given ID from the active queue.

@param id Queue ID
@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.active_unqueue (py_socket)- (#echo(__LINE__)#)")

		self.synchronized.acquire ()

		f_return = self.active_queue (py_socket)
		if (f_return >= 0): self.waiting -= 1

		self.synchronized.release ()

		if (f_return >= 0): self.active_activate (f_return,py_socket)

		return f_return
	#

	def set_active (self,status):
	#
		"""
Sets the status for the listener.

@param status New status
@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.set_active (status)- (#echo(__LINE__)#)")

		self.synchronized.acquire ()
		if (self.active != status): self.active = status
		self.synchronized.release ()
	#

	def start_listener (self):
	#
		"""
Starts the listener and readies this server instance.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.start_listener ()- (#echo(__LINE__)#)")

		self.synchronized.acquire ()

		if (not self.active):
		#
			self.listen (self.queue_max)
			self.active = True
		#

		self.synchronized.release ()
	#

	def stop_listener (self):
	#
		"""
Stops the listener and unqueues all running sockets.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.stop_listener ()- (#echo(__LINE__)#)")

		self.synchronized.acquire ()

		if (self.active):
		#
			self.active = False
			if ((self.stopping_hook != None) and (len (self.stopping_hook) > 0)): direct_plugin_hooks.unregister (self.stopping_hook,self.thread_stop_listener)
			self.stopping_hook = ""

			self.synchronized.release ()

			try: self.close ()
			except socket.error: pass

			self.active_unqueue_all ()
		#
		else: self.synchronized.release ()
	#

	def thread_local_check (self):
	#
		"""
For thread safety some variables are defined per thread. This method makes
sure that these variables are defined.

@since v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.thread_local_check ()- (#echo(__LINE__)#)")

		if (not hasattr (self.local,"sockets")):
		#
			self.local.listener_data = None
			self.local.sockets = { }
		#
	#

	def thread_stop_listener (self,params = None,last_return = None):
	#
		"""
Stops the running server instance by an plugin call.

@param  params Parameter specified calling "direct_pluginmanager".
@param  last_return The return value from the last hook called.
@return (None) None to stop communication after this call
@since  v1.0.0
		"""

		self.stop_listener ()
	#

	def unqueue (self,queue,id):
	#
		"""
Unqueues a previously active socket connection.

@param  queue Queue object
@param  id Queue ID
@return (bool) True on success
@since  v0.1.00
		"""

		if (self.debug != None): self.debug.append ("#echo(__FILEPATH__)# -server.unqueue (queue,{0:d})- (#echo(__LINE__)#)".format (id))
		f_return = False

		if ((queue != None) and (queue[id] != None)):
		#
			f_return = True
			f_socket = queue[id]
			queue[id] = None

			try: f_socket.close ()
			except socket.error: pass
		#

		return f_return
	#

	def thread (listener_type,listener_bind_address,listener_bind_port,active_handler,threads_active = 5,queue_handler = None,threads_queued = 10,stream_err = sys.stderr,thread_stopping_hook = "de.direct_netware.psd.status.exit"):
	#
		"""
Return a thread instance to be used as a server.

@return (object) Currently set error stream object
@since  v0.1.00
		"""

		return Thread (target = direct_server,args = ( listener_type,listener_bind_address,listener_bind_port,active_handler,threads_active,queue_handler,threads_queued,stream_err,True,thread_stopping_hook ))
	#
	thread = staticmethod (thread)

	def stream_err_get ():
	#
		"""
Return the thread save error stream object.

@return (object) Currently set error stream object
@since  v0.1.00
		"""

		global _direct_complete_server_stream_err
		return _direct_complete_server_stream_err
	#
	stream_err_get = staticmethod (stream_err_get)

	def stream_err_set (stream_err):
	#
		"""
Sets a error stream object and makes it thread save if needed.

@param stream_err Error stream object
@since v0.1.00
		"""

		global _direct_complete_server_stream_err
		# TODO: Pack the IO object into a thread safe one
		_direct_complete_server_stream_err = stream_err
	#
	stream_err_set = staticmethod (stream_err_set)
#

##j## EOF