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

    _mixin_slots_ = [ ]
    """
Additional __slots__ used for inherited classes.
    """
    __slots__ = [ ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

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
