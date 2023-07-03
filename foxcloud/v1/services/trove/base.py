#
# Copyright (c) 2020 FTI-CAS
#

from troveclient.v1 import client
from troveclient import exceptions as trove_exc


class BaseTrove(client.Client):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    __engine_type = None

    __engine_type__ = None

    def __init__(self, session, endpoint=None):
        super(BaseTrove, self).__init__(session=session)
        self._session = session
        self.endpoint = endpoint
        self.api = client.Client(version='1.0', session=session)

    def refresh(self, session):
        self._session = session

    # **********************************************
    #   Create a new openstack resource
    # **********************************************
    def create_cluster(self, name, datastore_id, datastore_version_id, instances=None,
                       locality=None, extended_properties=None, configuration=None, wait=False):
        """
        Subclass should be override this method
        :param name:
        :param datastore_id:
        :param datastore_version_id:
        :param instances:
        :param locality:
        :param extended_properties:
        :param configuration:
        :param wait:
        :return:
        """
    def create_instance(self, name, flavor_id=None, volume=None, databases=None,
                        users=None, restore_point=None, availability_zone=None,
                        datastore_id=None, datastore_version_id=None, nics=None,
                        configuration=None, replica_of=None, replica_count=None,
                        modules=None, locality=None, region_name=None, access=None,
                        wait=False, **kwargs):
        """
        Subclass should be override this method
        :param name:
        :param flavor_id:
        :param volume:
        :param databases:
        :param users:
        :param restore_point:
        :param availability_zone:
        :param datastore_id:
        :param datastore_version_id:
        :param nics:
        :param configuration:
        :param replica_of:
        :param replica_count:
        :param modules:
        :param locality:
        :param region_name:
        :param access:
        :param wait:
        :param kwargs:
        :return:
        """
    # **********************************************
    #   Update an openstack resource being created
    # **********************************************

    # **********************************************
    #   Delete an openstack resource being created
    # **********************************************

    # **********************************************
    #   Rollback an openstack resource being created
    # **********************************************
