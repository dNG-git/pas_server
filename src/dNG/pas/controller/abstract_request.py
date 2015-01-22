# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;server

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasServerVersion)#
#echo(__FILEPATH__)#
"""

from threading import local
from weakref import ref

from dNG.pas.data.supports_mixin import SupportsMixin
from dNG.pas.runtime.not_implemented_exception import NotImplementedException
from .abstract_mixin import AbstractMixin

class AbstractRequest(SupportsMixin, AbstractMixin):
#
	"""
This abstract class contains common methods for request implementations.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v0.1.01
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	_local = local()
	"""
Thread-local static object
	"""

	def __init__(self):
	#
		"""
Constructor __init__(AbstractRequest)

:since: v0.1.01
		"""

		AbstractMixin.__init__(self)
		SupportsMixin.__init__(self)

		AbstractRequest._local.weakref_instance = ref(self)

		self.supported_features['listener_data'] = self._supports_listener_data
	#

	def execute(self):
	#
		"""
Executes the incoming request.

:since: v0.1.01
		"""

		raise NotImplementedException()
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

	def _supports_listener_data(self):
	#
		"""
Returns false if the server address is unknown.

:return: (bool) True if listener are known.
:since:  v0.1.01
		"""

		return (self.server_host is not None)
	#

	@staticmethod
	def get_instance():
	#
		"""
Get the AbstractRequest singleton.

:return: (object) Object on success
:since:  v0.1.01
		"""

		return (AbstractRequest._local.weakref_instance() if (hasattr(AbstractRequest._local, "weakref_instance")) else None)
	#
#

##j## EOF