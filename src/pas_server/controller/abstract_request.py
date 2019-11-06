# -*- coding: utf-8 -*-

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

from dpt_runtime.not_implemented_exception import NotImplementedException

from .abstract_request_mixin import AbstractRequestMixin

class AbstractRequest(AbstractRequestMixin):
    """
This abstract class contains common methods for request implementations.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ "__weakref__" ] + AbstractRequestMixin._mixin_slots_
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """
    _local = local()
    """
Thread-local static object
    """

    def __init__(self):
        """
Constructor __init__(AbstractRequest)

:since: v1.0.0
        """

        AbstractRequestMixin.__init__(self)

        AbstractRequest._local.weakref_instance = ref(self)

        self.supported_features['listener_data'] = self._supports_listener_data
    #

    def execute(self):
        """
Executes the incoming request.

:since: v1.0.0
        """

        raise NotImplementedException()
    #

    def _new_response(self):
        """
Initializes the matching response instance.

:return: (object) Response object
:since:  v1.0.0
        """

        raise NotImplementedException()
    #

    def _respond(self, response):
        """
Responds the request with the given instance.

:param response: Response object

:since: v1.0.0
        """

        response.send_and_finish()
    #

    def _supports_listener_data(self):
        """
Returns false if the server address is unknown.

:return: (bool) True if listener are known.
:since:  v1.0.0
        """

        return (self.server_host is not None)
    #

    @staticmethod
    def get_instance():
        """
Get the AbstractRequest singleton.

:return: (object) Object on success
:since:  v1.0.0
        """

        return (AbstractRequest._local.weakref_instance() if (hasattr(AbstractRequest._local, "weakref_instance")) else None)
    #
#
