# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.AbstractResponse
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

from threading import local
from weakref import ref

from dNG.pas.runtime.io_exception import IOException
from dNG.pas.runtime.not_implemented_exception import NotImplementedException

class AbstractResponse(object):
#
	"""
This abstract class contains common methods for response implementations.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v0.1.01
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	local = local()
	"""
Thread-local static object
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractResponse)

:since: v0.1.01
		"""

		self.log_handler = None
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.store = { }
		"""
Response specific generic cache
		"""

		AbstractResponse.local.weakref_instance = ref(self)
	#

	def get_store(self):
	#
		"""
Return the generic store for the response.

:return: (dict) Response store
:since:  v0.1.01
		"""

		return self.store
	#

	def handle_critical_error(self, message):
	#
		"""
"handle_critical_error()" is called to send a critical error message.

:param message: Message (will be translated if possible)

:since: v0.1.01
		"""

		raise IOException(message)
	#

	def handle_error(self, message):
	#
		"""
"handle_error()" is called to send a error message.

:param message: Message (will be translated if possible)

:since: v0.1.01
		"""

		raise IOException(message)
	#

	def handle_exception(self, message, exception):
	#
		"""
"handle_exception()" is called if an exception occurs and should be
send.

:param message: Message (will be translated if possible)
:param exception: Original exception or formatted string (should be shown in
                  dev mode)

:since: v0.1.01
		"""

		raise IOException(message, exception)
	#

	def send(self):
	#
		"""
Sends the prepared response.

:since: v0.1.01
		"""

		raise NotImplementedException()
	#

	def set_log_handler(self, log_handler):
	#
		"""
Sets the LogHandler.

:param log_handler: LogHandler to use

:since: v0.1.01
		"""

		self.log_handler = log_handler
	#

	def supports_headers(self):
	#
		"""
Returns false if headers are not supported.

:return: (bool) True if the response contain headers.
:since:  v0.1.01
		"""

		return False
	#

	def supports_script_name(self):
	#
		"""
Returns false if the script name is not needed for execution.

:return: (bool) True if the controller should call "set_script_name()".
:since:  v0.1.01
		"""

		return False
	#

	def supports_streaming(self):
	#
		"""
Returns false if responses can not be streamed.

:return: (bool) True if streaming is supported.
:since:  v0.1.01
		"""

		return False
	#

	@staticmethod
	def get_instance():
	#
		"""
Get the AbstractResponse singleton.

:return: (object) Object on success
:since:  v0.1.01
		"""

		return (AbstractResponse.local.weakref_instance() if (hasattr(AbstractResponse.local, "weakref_instance")) else None)
	#

	@staticmethod
	def get_instance_store():
	#
		"""
Get the response store.

:return: (dict) Response store
:since:  v0.1.01
		"""

		instance = AbstractResponse.get_instance()
		return (None if (instance == None) else instance.get_store())
	#
#

##j## EOF