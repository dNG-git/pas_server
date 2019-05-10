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

# pylint: disable=import-error, no-name-in-module

from weakref import proxy, ProxyTypes

from dpt_module_loader import NamedClassLoader
from dpt_runtime.supports_mixin import SupportsMixin
from dpt_runtime.not_implemented_exception import NotImplementedException

from ..controller.abstract_request import AbstractRequest
from ..controller.abstract_response import AbstractResponse

class Abstract(SupportsMixin):
    """
"Abstract" provides methods for module and service based implementations.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    def __init__(self):
        """
Constructor __init__(Abstract)

:since: v1.0.0
        """

        SupportsMixin.__init__(self)

        self._executable_method_name = None
        """
Method name to be called on execution if set
        """
        self._log_handler = None
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self._is_result_expected = False
        """
True if a result of the executable method is expected
        """
        self.request = None
        """
Request instance
        """
        self.response = None
        """
Response instance
        """

        self.log_handler = NamedClassLoader.get_singleton("dpt_logging.LogHandler", False)
    #

    @property
    def executable_method_name(self):
        """
Returns the executable method name used for the given request and response
instances.

:return: (str) Method name to be executed
:since:  v1.0.0
        """

        _return = (self._get_executable_method_name()
                   if (self._executable_method_name is None) else
                   self._executable_method_name
                  )

        return _return
    #

    @executable_method_name.setter
    def executable_method_name(self, method_name):
        """
Sets the executable method name used for the given request and response
instances.

:param method_name: Method name to be executed

:since: v1.0.0
        """

        self._executable_method_name = method_name
    #

    @property
    def is_result_expected(self):
        """
Returns true if a result of the executable method is expected.

:return: (bool) True if a result is expected
:since:  v1.0.0
        """

        return self._is_result_expected
    #

    @property
    def log_handler(self):
        """
Returns the LogHandler.

:return: (object) LogHandler in use
:since:  v1.0.0
        """

        return self._log_handler
    #

    @log_handler.setter
    def log_handler(self, log_handler):
        """
Sets the LogHandler.

:param log_handler: LogHandler to use

:since: v1.0.0
        """

        self._log_handler = (log_handler if (isinstance(log_handler, ProxyTypes)) else proxy(log_handler))
    #

    @property
    def result(self):
        """
Returns the result set.

:return: (mixed) Executable method result
:since:  v1.0.0
        """

        raise NotImplementedException()
    #

    @result.setter
    def result(self, result):
        """
Sets an executable method result.

:param result: Result to be set

:since: v1.0.0
        """

        raise NotImplementedException()
    #

    def execute(self):
        """
Execute the requested action.

:since: v1.0.0
        """

        method = getattr(self, self.executable_method_name)

        if (self.is_result_expected):
            result = method()
            if (result is not None and self.result is None): self.result = result
        else: method()
    #

    def _get_executable_method_name(self):
        """
Returns the executable method name used for the given request and response
instances.

:return: (str) Method name to be executed
:since:  v1.0.0
        """

        raise NotImplementedException()
    #

    def init(self, request = None, response = None):
        """
Initializes the module and service from the given request and response.

:param request: Request object
:param response: Response object

:since: v1.0.0
        """

        self.request = (AbstractRequest.get_instance()
                        if (request is None) else
                        request
                       )

        self.response = (AbstractResponse.get_instance()
                         if (response is None) else
                         response
                        )
    #
#
