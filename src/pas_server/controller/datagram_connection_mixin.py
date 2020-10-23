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

class DatagramConnectionMixin(object):
    """
"DatagramConnectionMixin" provides methods to handle datagram data of the
connection instance.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.1.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    _mixin_slots_ = [ "_datagram_data" ]
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
Constructor __init__(DatagramConnectionMixin)

:since: v1.1.0
        """

        self._datagram_data = None
        """
Datagram data received
        """

        self.supported_features['datagram_data'] = True
    #

    @property
    def datagram_data(self):
        """
Returns the datagram data of this connection.

:return: (bytes) Datagram data received
:since:  v1.1.0
        """

        if (self._datagram_data is None): self._datagram_data = self.get_data(65535)
        return self._datagram_data
    #
#
