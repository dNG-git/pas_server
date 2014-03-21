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

from os import path

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

		self.accepted_formats = None
		"""
Formats the client accepts
		"""
		self.action = "index"
		"""
Requested action
		"""
		self.client_host = None
		"""
Client host
		"""
		self.client_port = None
		"""
Client port
		"""
		self.dsd = { }
		"""
Data transmitted with the request
		"""
		self.module = "services"
		"""
Requested module block
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
		self.server_scheme = "http"
		"""
Server scheme / protocol
		"""
		self.service = "index"
		"""
Requested service
		"""
		self.session = None
		"""
Associated session to request
		"""
		self.output_handler = None
		"""
Requested response format name
		"""

		self.supported_features['accepted_formats'] = self._supports_accepted_formats
		self.supported_features['listener_data'] = self._supports_listener_data
	#

	def get_accepted_formats(self):
	#
		"""
Returns the formats the client accepts.

:return: (list) Accepted formats
:since:  v0.1.01
		"""

		return self.accepted_formats
	#

	def get_action(self):
	#
		"""
Returns the requested action.

:return: (str) Requested action
:since:  v0.1.01
		"""

		return self.action
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

	def get_dsd(self, key, default = None):
	#
		"""
Returns the DSD value for the specified parameter.

:param key: DSD key
:param default: Default value if not set

:return: (mixed) Requested DSD value or default one if undefined
:since:  v0.1.01
		"""

		return (self.dsd[key] if (self.is_dsd_set(key)) else default)
	#

	def get_dsd_dict(self):
	#
		"""
Return all DSD parameters received.

:return: (mixed) Request DSD values
:since:  v0.1.01
		"""

		return self.dsd
	#

	def get_inner_request(self):
	#
		"""
Returns the inner request instance.

:return: (object) Request instance; None if not available
:since:  v0.1.01
		"""

		return None
	#

	def get_module(self):
	#
		"""
Returns the requested module.

:return: (str) Requested module
:since:  v0.1.01
		"""

		return self.module
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

	def get_output_handler(self):
	#
		"""
Returns the requested output format.

:return: (str) Requested output format; None if not defined
:since:  v0.1.01
		"""

		return self.output_handler
	#

	def get_script_name(self):
	#
		"""
Returns the script name.

:return: (str) Script name
:since:  v0.1.01
		"""

		return self.script_name
	#

	def get_script_pathname(self):
	#
		"""
Returns the script path and name of the request.

:return: (str) Script path and name
:since:  v0.1.01
		"""

		return self.script_pathname
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

	def get_service(self):
	#
		"""
Returns the requested service.

:return: (str) Requested service
:since:  v0.1.01
		"""

		return self.service
	#

	def get_session(self):
	#
		"""
Returns the associated session.

:return: (object) Session instance
:since:  v0.1.01
		"""

		return self.session
	#

	def init(self, request):
	#
		"""
Initializes default values from the original request.

:param request: (object) Request instance

:since: v0.1.01
		"""

		self.accepted_formats = request.get_accepted_formats()
		self.client_host = request.get_client_host()
		self.client_port = request.get_client_port()
		self.server_scheme = request.get_server_scheme()
		self.server_host = request.get_server_host()
		self.server_port = request.get_server_port()
		self.session = request.get_session()
		self.set_script_pathname(request.get_script_pathname())
	#

	def is_dsd_set(self, key):
	#
		"""
Returns true if the DSD for the specified parameter exists.

:param key: DSD key

:return: (bool) True if set
:since:  v0.1.01
		"""

		return (key in self.dsd)
	#

	def set_accepted_formats(self, accepted_formats):
	#
		"""
Sets the formats the client accepts.

:param accepted_formats: List of accepted formats

:since: v0.1.01
		"""

		if (isinstance(accepted_formats, list)): self.accepted_formats = accepted_formats
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

	def set_dsd(self, key, value):
	#
		"""
Sets the DSD value for the specified parameter.

:param key: DSD key
:param default: DSD value

:since: v0.1.01
		"""

		self.dsd[key] = value
	#

	def set_script_pathname(self, script_pathname):
	#
		"""
Sets the script path and name of the request.

:param script_pathname: Script path and name

:since: v0.1.01
		"""

		if (script_pathname != None):
		#
			self.script_name = path.basename(script_pathname)
			self.script_pathname = script_pathname
		#
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

	def _supports_accepted_formats(self):
	#
		"""
Returns false if accepted formats can not be identified.

:return: (bool) True if accepted formats are identified.
:since:  v0.1.01
		"""

		return (False if (self.accepted_formats == None) else True)
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