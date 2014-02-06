# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.AbstractRequest
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

from dNG.pas.runtime.not_implemented_exception import NotImplementedException

class AbstractRequest(object):
#
	"""
This abstract class contains common methods for request implementations.

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
Constructor __init__(AbstractRequest)

:since: v0.1.01
		"""

		self.client_host = None
		"""
Client host
		"""
		self.client_port = None
		"""
Client port
		"""
		self.log_handler = None
		"""
The LogHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.parameters = { }
		"""
Request parameters
		"""
		self.server_host = None
		"""
Server host
		"""
		self.server_port = None
		"""
Server port
		"""
		self.server_scheme = None
		"""
Server scheme / protocol
		"""

		AbstractRequest.local.weakref_instance = ref(self)
	#

	def execute(self):
	#
		"""
Executes the incoming request.

:since: v0.1.01
		"""

		raise NotImplementedException()
	#

	def get_client_host(self):
	#
		"""
Returns the client host if any.

:return: (str) Client host; None if unknown or not applicable
:since:  v0.1.01
		"""

		return self.client_host
	#

	def get_client_port(self):
	#
		"""
Returns the client port if any.

:return: (int) Client port; None if unknown or not applicable
:since:  v0.1.01
		"""

		return self.client_port
	#

	def get_parameter(self, name, default = None):
	#
		"""
Returns the value for the specified parameter.

:param key: Parameter name
:param default: Default value if not set

:return: (mixed) Requested value or default one if undefined
:since:  v0.1.00
		"""

		return (self.parameters[name] if (name in self.parameters) else default)
	#

	def get_parameters(self):
	#
		"""
Return all parameters received.

:return: (mixed) Request parameters
:since:  v0.1.00
		"""

		return self.parameters
	#

	def get_server_host(self):
	#
		"""
Returns the server host if any.

:return: (str) Server host; None if unknown or not applicable
:since:  v0.1.01
		"""

		return self.server_host
	#

	def get_server_port(self):
	#
		"""
Returns the server port if any.

:return: (int) Server port; None if unknown or not applicable
:since:  v0.1.01
		"""

		return self.server_port
	#

	def get_server_scheme(self):
	#
		"""
Returns the server scheme.

:return: (str) Server scheme / protocol; None if unknown
:since:  v0.1.01
		"""

		return self.server_scheme
	#

	def init(self):
	#
		"""
Do preparations for request handling.

:since: v0.1.01
		"""

		"""
Set source variables. The server timezone will be changed if a user is
logged in and/or its timezone is identified.
		"""

		raise NotImplementedException()
	#

	def _init_response(self):
	#
		"""
Initializes the matching response instance.

:return: (object) Response object
:since:  v0.1.01
		"""

		raise NotImplementedException()
	#

	def _respond(self, response):
	#
		"""
Reply the request with the given response.

:since: v0.1.01
		"""

		response.send()
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

	def supports_accepted_formats(self):
	#
		"""
Returns false if accepted formats can not be identified.

:return: (bool) True if accepted formats are identified.
:since:  v0.1.01
		"""

		return False
	#

	def supports_compression(self):
	#
		"""
Returns false if supported compression formats can not be identified.

:return: (bool) True if compression formats are identified.
:since:  v0.1.01
		"""

		return False
	#

	def supports_headers(self):
	#
		"""
Returns false if the script name is not needed for execution.

:return: (bool) True if the request contains headers.
:since:  v0.1.01
		"""

		return False
	#

	def supports_listener_data(self):
	#
		"""
Returns false if the server address is unknown.

:return: (bool) True if listener are known.
:since:  v0.1.01
		"""

		return False
	#

	@staticmethod
	def get_instance():
	#
		"""
Get the AbstractRequest singleton.

:return: (object) Object on success
:since:  v0.1.01
		"""

		return (AbstractRequest.local.weakref_instance() if (hasattr(AbstractRequest.local, "weakref_instance")) else None)
	#
#

##j## EOF