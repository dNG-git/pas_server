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

try: from collections.abc import Iterator
except ImportError: from collections import Iterator

from dpt_runtime.binary import Binary
from dpt_runtime.not_implemented_exception import NotImplementedException
from dpt_runtime.supports_mixin import SupportsMixin
from dpt_runtime.value_exception import ValueException

from .abstract_request_mixin import AbstractRequestMixin

class AbstractStreamResponse(SupportsMixin):
    """
A stream response reads data from a streamer and writes it to a response object.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=unused-argument

    STREAM_DIRECT = 1 << 1
    """
Do not set Transfer-Encoding but output content directly as soon as it is
available.
    """
    STREAM_ITERATOR = 1
    """
Output content directly as soon as it is available and requested by a iterator.
    """
    STREAM_NONE = 0
    """
Do not stream content
    """

    __slots__ = [ "_active",
                  "_data",
                  "_log_handler",
                  "stream_mode",
                  "stream_mode_supported",
                  "_streamer"
                ] + SupportsMixin._mixin_slots_
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self):
        """
Constructor __init__(AbstractStreamResponse)

:since: v1.0.0
        """

        SupportsMixin.__init__(self)

        self._active = True
        """
True if ready for output.
        """
        self._data = None
        """
Data buffer
        """
        self._log_handler = None
        """
The LogHandler is called whenever debug messages should be logged or errors
happened.
        """
        self.stream_mode = AbstractStreamResponse.STREAM_NONE
        """
Stream response instead of holding it in a buffer
        """
        self.stream_mode_supported = AbstractStreamResponse.STREAM_NONE
        """
Supported streaming mode
        """
        self._streamer = None
        """
Streamer implementation
        """

        if (isinstance(self, Iterator)): self.stream_mode_supported |= AbstractStreamResponse.STREAM_ITERATOR
    #

    def __del__(self):
        """
Destructor __del__(AbstractStreamResponse)

:since: v1.0.0
        """

        self.finish()
    #

    @property
    def is_active(self):
        """
Returns if the response stream is active.

:return: (bool) True if active
:since:  v1.0.0
        """

        return self._active
    #

    @property
    def is_self_finishing(self):
        """
Returns true if the response stream is finishing itself automatically after
successful transmission.

:return: (bool) True if finishing itself
:since:  v1.0.0
        """

        return (self.stream_mode & AbstractStreamResponse.STREAM_ITERATOR)
    #

    @property
    def is_streamer_set(self):
        """
Returns true if a streamer has been set.

:return: (bool) True if set
:since:  v1.0.0
        """

        return (self.streamer is not None)
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
    def streamer(self):
        """
Returns the streamer to create response data when requested.

:return: (object) Streamer object if any
:since:  v1.0.0
        """

        return (self._streamer if (self._active) else None)
    #

    @streamer.setter
    def streamer(self, streamer):
        """
Sets the streamer to create response data when requested.

:since: v1.0.0
        """

        if (streamer is None): self.stream_mode = 0
        else:
            if (streamer is not None and not hasattr(streamer, "read")): raise ValueException("Given streaming object is not supported.")
            if (self.stream_mode_supported & AbstractStreamResponse.STREAM_ITERATOR): self.stream_mode |= AbstractStreamResponse.STREAM_ITERATOR
        #

        self._streamer = streamer
    #

    def finish(self):
        """
Finish transmission and cleanup resources.

:since: v1.0.0
        """

        if (self._active):
            try:
                self.send()
                if (self.streamer is not None and hasattr(self.streamer, "close")): self.streamer.close()
            finally:
                self._active = False
                self._data = None
                self._streamer = None
            #
        #
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
Send data in cache.

:since: v1.0.0
        """

        if (self._active):
            if (self.streamer is not None and (not self.stream_mode & AbstractStreamResponse.STREAM_ITERATOR)):
                while (not self.streamer.is_eof):
                    data = self.streamer.read()

                    if (data is None): break
                    else: self.send_data(data)
                #
            elif (self._data is not None):
                self._write(self._data)
                self._data = None
            #
        #
    #

    def send_data(self, data):
        """
Sends the given data as part of the response.

:param data: Data to send

:since: v1.0.0
        """

        if (self._active):
            if (self.stream_mode == AbstractStreamResponse.STREAM_NONE):
                data = Binary.bytes(data)

                if (self._data is None): self._data = Binary.BYTES_TYPE()
                self._data += data
            else: self._write(data)
        #
    #

    def _write(self, data):
        """
Writes the given data.

:param data: Data to be send

:since: v1.0.0
        """

        raise NotImplementedException()
    #
#
