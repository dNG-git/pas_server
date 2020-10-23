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

import asyncio

class AioStreamResponseMixin(object):
    """
"AioStreamResponseMixin" adds support to "asyncio" response instances.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.1.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    _mixin_slots_ = [ "_aio_response_awaitables" ]
    """
Additional __slots__ used for inherited classes.
    """
    __slots__ = [ ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self):
        """
Constructor __init__(AioStreamResponseMixin)

:since: v1.1.0
        """

        self._aio_response_awaitables = [ ]
        """
"asyncio" response awaitables for this response instance
        """

        self.stream_mode = self.__class__.STREAM_DIRECT
        self.stream_mode_supported |= self.__class__.STREAM_DIRECT
    #

    def __del__(self):
        """
Destructor __del__(AioStreamResponseMixin)

:since: v1.1.0
        """

        event_loop = None

        try: event_loop = asyncio.get_event_loop()
        except: pass

        if (event_loop is not None and (not event_loop.is_closed())): asyncio.run_coroutine_threadsafe(self.finish(), event_loop)
    #

    @property
    def is_self_finishing(self):
        """
Returns true if the response stream is finishing itself automatically after
successful transmission.

:return: (bool) True if finishing itself
:since:  v1.1.0
        """

        return True
    #

    async def finish(self):
        """
Finish transmission and cleanup resources.

:since: v1.1.0
        """

        for awaitable in self._aio_response_awaitables:
            try: await awaitable
            except Exception as handled_exception:
                if (self.log_handler != None): self.log_handler.error(handled_exception)
            #
        #

        self._aio_response_awaitables.clear()
    #

    def _wrap_aio_write(self, _callable):
        """
Wrap the "asyncio" stream writing callable.

:param callable: Wrapped code

:return: (object) Proxy method
:since:  v1.1.0
    """

        def proxymethod(*args, **kwargs):
            if (self.is_active):
                awaitable = _callable(*args, **kwargs)
                self._aio_response_awaitables.append(awaitable)
            #
        #

        return proxymethod
    #
#
