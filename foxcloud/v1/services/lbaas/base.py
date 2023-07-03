#
# Copyright (c) 2020 FTI-CAS
#

import copy

from octaviaclient.api.v2 import octavia


class BaseLbaas(octavia.OctaviaAPI):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    __engine_type__ = None

    def __init__(self, session, endpoint=None):
        super(BaseLbaas, self).__init__(session=session, endpoint=endpoint)
        self._session = session
        self.endpoint = endpoint

    def refresh(self, session):
        self._session = session

    def create_allinone(self, info):
        """
        Create allinone
        Subclass should be override this method
        :param info:
        :return:
        """
