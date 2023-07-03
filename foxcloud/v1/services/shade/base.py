#
# Copyright (c) 2020 FTI-CAS
#
from novaclient.v2.client import Client as NovaClient
from novaclient import api_versions
from keystoneclient.v3 import client as ks_client
from neutronclient.neutron import client as neu_client
from cinderclient import client as cinder_client

from foxcloud.v1.utils import constants as consts
from foxcloud.v1.services.shade import neutron as neu_client


class BaseShade(NovaClient):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    __engine_type__ = None

    def __init__(self, session):
        nova_version = api_versions.APIVersion(version_str=consts.VERSIONS['nova'])
        super(BaseShade, self).__init__(api_version=nova_version, session=session,
                                        direct_use=False)
        self.ks_api = ks_client.Client(session=session)
        self.neu_api = neu_client.Network(session=session)
        self.cinder_api = cinder_client.Client(consts.VERSIONS['cinder'], session=session)
        self._session = session

    def create_server(self, info):
        """
        Subclass should be override this method
        :param info:
        :return:
        """

    def update_server(self, info):
        """
        Subclass should be override this method
        :param info:
        :return:
        """

    def delete_server(self, server_id):
        """
        Subclass should be override this method
        :param server_id:
        :return:
        """