# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.controller.AbstractInnerRequest
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

from dNG.pas.data.supports_mixin import SupportsMixin

class AbstractInnerRequest(SupportsMixin):
#
	"""
This abstract class contains common methods for inner requests usually used
for redirection.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v0.1.01
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractInnerRequest)

:since: v0.1.01
		"""

		SupportsMixin.__init__(self)

		self.client_host = None
		"""
Client host
		"""
		self.client_port = None
		"""
Client port
		"""
		self.parameters = { }
		"""
Request parameters
		"""
		self.script_name = None
		"""
Called script
		"""
		self.script_pathname = None
		"""
Request path to the script
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

		self.supported_features['listener_data'] = self._supports_listener_data
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
:since:  v0.1.01
		"""

		return (self.parameters[name] if (name in self.parameters) else default)
	#

	def get_parameters(self):
	#
		"""
Return all parameters received.

:return: (mixed) Request parameters
:since:  v0.1.01
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

	def init(self, request):
	#
		"""
Initializes default values from the original request.

:param request: (object) Request instance

:since: v0.1.01
		"""

		self.client_host = request.get_client_host()
		self.client_port = request.get_client_port()
		self.server_scheme = request.get_server_scheme()
		self.server_host = request.get_server_host()
		self.server_port = request.get_server_port()
	#

	def set_client_host(self, host):
	#
		"""
Sets the client host for the inner request.

:param host: Client host

:since: v0.1.01
		"""

		self.client_host = host
	#

	def set_client_port(self, port):
	#
		"""
Sets the client port.

:param port: Client port

:since: v0.1.01
		"""

		self.client_port = port
	#

	def set_server_host(self, host):
	#
		"""
Sets the server host for the inner request.

:param host: Server host

:since: v0.1.01
		"""

		self.server_host = host
	#

	def set_server_port(self, port):
	#
		"""
Sets the server port.

:param port: Server port

:since: v0.1.01
		"""

		self.server_port = port
	#

	def set_server_scheme(self, scheme):
	#
		"""
Sets the underlying server scheme.

:param scheme: Server scheme / protocol

:since: v0.1.01
		"""

		self.server_scheme = scheme
	#

	def _supports_listener_data(self):
	#
		"""
Returns false if the server address is unknown.

:return: (bool) True if listener are known.
:since:  v0.1.01
		"""

		return (self.server_host != None)
	#
#

##j## EOF