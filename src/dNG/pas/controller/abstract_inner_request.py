# -*- coding: utf-8 -*-
##j## BOF

"""
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
"""

from dNG.pas.data.supports_mixin import SupportsMixin
from .abstract_mixin import AbstractMixin

class AbstractInnerRequest(AbstractMixin, SupportsMixin):
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

		AbstractMixin.__init__(self)
		SupportsMixin.__init__(self)

		self.parameters_chained = { }
		"""
Chained request parameters
		"""

		self.supported_features['listener_data'] = self._supports_listener_data
		self.supported_features['parameters_chained'] = self._supports_listener_data
	#

	def get_parameter_chained(self, name, default = None):
	#
		"""
Returns the value for the specified parameter in a chained request.

:param name: Parameter name
:param default: Default value if not set

:return: (mixed) Requested value or default one if undefined
:since:  v0.1.01
		"""

		return (self.parameters_chained[name] if (name in self.parameters_chained) else default)
	#

	def get_parameters_chained(self):
	#
		"""
Return all parameters of a chained request.

:return: (dict) Request parameters chained
:since: v0.1.01
		"""

		return self.parameters_chained
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

	def set_parameter_chained(self, name, value):
	#
		"""
Sets the value for the given parameter in a chained request.

:param name: Parameter name
:param value: Parameter value

:since: v0.1.01
		"""

		self.parameters_chained[name] = value
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