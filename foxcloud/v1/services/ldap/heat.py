#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud.v1.services.ldap.base import BaseLdap


class Heat(BaseLdap):
    """

    """
    __engine_type = 'heat'

    def __init__(self, session):
        super().__init__(session)

    def create_server(self):
        pass

    def update_server(self):
        pass


