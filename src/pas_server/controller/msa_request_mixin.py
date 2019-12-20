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

import re

from dpt_logging import LogLine
from dpt_module_loader import NamedClassLoader

from ..module import Abstract
from ..msa_request_exception import MsaRequestException

class MsaRequestMixin(object):
    """
Mixin to handle requests for actions of specific services and modules.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas
:subpackage: server
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    RE_SPECIAL_CHARACTERS = re.compile("\\W+")
    """
RegExp to find non-word characters
    """

    _mixin_slots_ = [ "_action", "_module_package", "_service_package_and_module" ]
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
Constructor __init__(MsaRequestMixin)

:since: v1.0.0
        """

        self._action = None
        """
Requested action
        """
        self._module_package = None
        """
Requested module package name
        """
        self._service_package_and_module = None
        """
Requested service package and module name
        """
    #

    @property
    def action(self):
        """
Returns the requested action.

:return: (str) Action requested
:since:  v1.0.0
        """

        return ("index" if (self._action is None) else self._action)
    #

    @action.setter
    def action(self, action):
        """
Sets the requested action.

:param action: Action requested

:since: v1.0.0
        """

        action = action.strip()
        if (action not in ( "", "-" )): self._action = MsaRequestMixin.RE_SPECIAL_CHARACTERS.sub("_", action)
    #

    @property
    def module_package(self):
        """
Returns the requested module package name.

:return: (str) Module package name requested
:since:  v1.0.0
        """

        return ("services" if (self._module_package is None) else self._module_package)
    #

    @module_package.setter
    def module_package(self, name):
        """
Sets the requested module package name.

:param name: Module package name requested

:since: v1.0.0
        """

        name = name.strip()
        if (name not in ( "", "-" )): self._module_package = MsaRequestMixin.RE_SPECIAL_CHARACTERS.sub("_", name)
    #

    @property
    def service_package_and_module(self):
        """
Returns the requested service package and module name.

:return: (str) Service package and module requested
:since:  v1.0.0
        """

        return ("index" if (self._service_package_and_module is None) else self._service_package_and_module)
    #

    @service_package_and_module.setter
    def service_package_and_module(self, name):
        """
Sets the requested service package and module name.

:param name: Service package and module requested

:since: v1.0.0
        """

        name = name.strip()

        if (name != "-"):
            name = re.sub("(\\.){2,}", ".", re.sub("[^\\w.]+", "_", name))
            if (name != ""): self._service_package_and_module = name
        #
    #

    @staticmethod
    def execute_msa_request(request, response):
        """
Executes the given request for an action of a specific service and module
and generate content for the given response.

:param request: Request to be executed
:param response: Response instance to be used

:since: v1.0.0
        """

        module_package = request.module_package

        service_package_and_module_data = request.service_package_and_module.rsplit(".", 1)
        service_class_name = NamedClassLoader.get_camel_case_class_name(service_package_and_module_data.pop())
        service_package_and_module_data.append(service_class_name)

        service_package_and_module = ".".join(service_package_and_module_data)

        LogLine.debug("{0!r} has been called for '*.module.{1}.{2}'", request, module_package, service_package_and_module, context = "pas_server")

        if (not NamedClassLoader.is_defined_in_namespace("module",
                                                         "{0}.{1}".format(module_package, service_package_and_module)
                                                        )
           ): raise MsaRequestException("Request given for '*.module.{0}.{1}' is invalid".format(module_package, service_package_and_module))

        instance = NamedClassLoader.get_instance_in_namespace("module",
                                                              "{0}.{1}".format(module_package, service_package_and_module)
                                                             )

        if (not isinstance(instance, Abstract)): raise MsaRequestException("Module instance '*.module.{0}.{1}' is invalid".format(module_package, service_package_and_module))

        instance.init(request, response)
        instance.execute()

        del(instance)
    #
#
