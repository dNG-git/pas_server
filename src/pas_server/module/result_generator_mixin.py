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

from dpt_runtime.io_exception import IOException
from dpt_runtime.iterator import Iterator

class ResultGeneratorMixin(Iterator):
    """
"ResultGeneratorMixin" provides methods to execute an given action. The
result is returned to the executor.

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
Constructor __init__(ResultGeneratorMixin)

:since: v1.0.0
        """

        self._context = None
        """
Executable method context
        """
        self._result = None
        """
Executable method result
        """

        self.supported_features['context'] = True
        self.supported_features['result_generator'] = True
    #

    @property
    def context(self):
        """
Returns the executable method context.

:return: (dict) Executable method context
:since:  v1.0.0
        """

        if (not self.is_result_expected): raise IOException("Executable method context is not supported in the caller's one")
        return self._context
    #

    @property
    def result(self):
        """
Returns the executable method result set.

:return: (mixed) Executable method result
:since:  v1.0.0
        """

        return self._result
    #

    @result.setter
    def result(self, result):
        """
Sets an executable method result.

:param result: Result to be set

:since: v1.0.0
        """

        if (not self.is_result_expected): raise IOException("Executable method result is not supported in the caller's context")
        self._result = result
    #

    def __iter__(self):
        """
python.org: Return an iterator object.

:return: (object) Iterator object
:since:  v1.0.0
        """

        return self
    #

    def __next__(self):
        """
python.org: Return the next item from the container.

:return: (mixed) Executable method result
:since:  v1.0.0
        """

        if (not self.is_result_expected): raise StopIteration()

        self.execute()

        _return = self.result

        self._is_result_expected = False
        self._result = None

        return _return
    #

    def init_generator_executable(self, action, context = None):
        """
Sets an block action for execution.

:param action: Action requested
:param context: Action context

:return: (object) Initialized generator (self)
:since:  v1.0.0
        """

        self.init()
        self.executable_method_name = action

        self._context = context
        self._is_result_expected = True
        self._result = None

        return self
    #
#
