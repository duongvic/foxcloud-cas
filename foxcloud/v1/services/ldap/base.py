#
# Copyright (c) 2020 FTI-CAS
#

import ldap
from ldap.ldapobject import LDAPObject


class BaseLdap(LDAPObject):
    """Basic manager for the shade service.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    __engine_type = None

    def __init__(self, uri, trace_level=0, trace_file=None, trace_stack_limit=5,
                 bytes_mode=None, bytes_strictness=None, fileno=None):
        super(BaseLdap, self).__init__(uri, trace_level, trace_file, trace_stack_limit,
                                       bytes_mode, bytes_strictness, fileno)
        self.protocol_version = ldap.VERSION3

    def refresh(self, session):
        """

        :param session:
        :return:
        """