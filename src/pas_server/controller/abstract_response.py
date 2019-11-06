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

try: from collections.abc import Mapping
except ImportError: from collections import Mapping

from dpt_runtime.io_exception import IOException
from dpt_runtime.not_implemented_exception import NotImplementedException
from dpt_runtime.supports_mixin import SupportsMixin
from dpt_settings import Settings

from .abstract_request_mixin import AbstractRequestMixin

class AbstractResponse(SupportsMixin):
    """
This abstract class contains common methods for response implementations.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ "__weakref__", "_store", "_log_handler" ] + SupportsMixin._mixin_slots_
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
Constructor __init__(AbstractResponse)

:since: v1.0.0
        """

        SupportsMixin.__init__(self)

        self._log_handler = None
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self._store = { }
        """
Response specific data store
        """

        AbstractResponse._local.weakref_instance = ref(self)
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

    @property
    def runtime_settings(self):
        """
Return the runtime settings dict for the response.

:return: (dict) Response runtime settings dict
:since:  v1.0.0
        """

        return self.store['_dpt_settings']
    #

    @property
    def store(self):
        """
Return the data store for the response.

:return: (dict) Response store
:since:  v1.0.0
        """

        if ("_dpt_settings" not in self._store):
            self._store['_dpt_settings'] = StackedDict()
            self._store['_dpt_settings'].add_dict(Settings.get_dict())
        #

        return self._store
    #

    def handle_critical_error(self, message):
        """
"handle_critical_error()" is called to send a critical error message.

:param message: Message (will be translated if possible)

:since: v1.0.0
        """

        raise IOException(message)
    #

    def handle_error(self, message):
        """
"handle_error()" is called to send a error message.

:param message: Message (will be translated if possible)

:since: v1.0.0
        """

        raise IOException(message)
    #

    def handle_exception(self, message, exception):
        """
"handle_exception()" is called if an exception occurs and should be
send.

:param message: Message (will be translated if possible)
:param exception: Original exception or formatted string (should be shown in
                  dev mode)

:since: v1.0.0
        """

        raise IOException(message, exception)
    #

    def init(self, connection_or_request):
        """
Initializes default values from the a connection or request instance.

:param connection_or_request: Connection or request instance

:since: v1.0.0
        """

        if (not isinstance(connection_or_request, AbstractRequestMixin)): raise TypeException("Request instance given is invalid")

        self._log_handler = connection_or_request.log_handler
    #

    def send(self):
        """
Sends the prepared response.

:since: v1.0.0
        """

        raise NotImplementedException()
    #

    def send_and_finish(self):
        """
Sends the prepared response and finishes all related tasks.

:since: v1.0.0
        """

        self.send()
    #

    @staticmethod
    def get_instance():
        """
Get the AbstractResponse singleton.

:return: (object) Object on success
:since:  v1.0.0
        """

        return (AbstractResponse._local.weakref_instance() if (hasattr(AbstractResponse._local, "weakref_instance")) else None)
    #

    @staticmethod
    def get_instance_store():
        """
Get the response store of the response singleton.

:return: (dict) Response store
:since:  v1.0.0
        """

        instance = AbstractResponse.get_instance()
        return (None if (instance is None) else instance.store)
    #
#
