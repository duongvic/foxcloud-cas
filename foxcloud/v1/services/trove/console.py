#
# Copyright (c) 2020 FTI-CAS
#

import time

from troveclient import exceptions as trove_exc

from foxcloud.v1.services.trove.base import BaseTrove
from foxcloud import exceptions as fox_exc


class Console(BaseTrove):
    __engine_type__ = 'console'
    ACTION_TIMEOUT = 3600

    # **********************************************
    #   Create a new openstack resource
    # **********************************************
    def create_cluster(self, name, datastore_id, datastore_version_id, instances=None,
                       locality=None, extended_properties=None, configuration=None, wait=False):
        """
        Create a new cluster
        :param name:
        :param datastore_id:
        :param datastore_version_id:
        :param instances:
        :param locality: [affinity, anti-affinity]
        :param extended_properties:
        :param configuration:
        :param wait
        :return:
        """
        try:
            cluster = self.clusters.create(name, datastore_id, datastore_version_id, instances,
                                           locality, extended_properties, configuration)
            if wait:
                status, error = self._wait_create_cluster(resource_id=cluster.id)
                if not status:
                    try:
                        self.clusters.delete(cluster.id)
                    except trove_exc.ClientException as e:
                        pass
                    raise fox_exc.FoxCloudException(error)
            return cluster
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def _wait_create_cluster(self, resource_id, timeout=ACTION_TIMEOUT, interval=10):
        """
        Check done task
        :param resource_id:
        :param type:
        :param timeout:
        :param interval:
        :return:
        """
        while timeout >= 0:
            data = self.clusters.get(resource_id)
            task = data.task
            if isinstance(task, dict):
                name = task.get('name')
                if name == 'ACTIVE':
                    return True, None
                if name == 'FAILED':
                    return False, task.get('description')
            timeout -= interval
            time.sleep(interval)
        return False, "Action timeout"

    def create_instance(self, name, flavor_id=None, volume=None, databases=None,
                        users=None, restore_point=None, availability_zone=None,
                        datastore_id=None, datastore_version_id=None, nics=None,
                        configuration=None, replica_of=None, replica_count=None,
                        modules=None, locality=None, region_name=None, access=None,
                        wait=False, **kwargs):
        """Create a new database shade.
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
        try:
            if replica_of:
                databases = None
                users = None

            instance = self.instances.create(name, flavor_id, volume, databases,
                                             users, restore_point, availability_zone,
                                             datastore_id, datastore_version_id, nics,
                                             configuration, replica_of, replica_count,
                                             modules, locality, region_name, access,
                                             **kwargs)
            if wait:
                status, error = self._wait_create_instance(resource_id=instance.id)
                if not status:
                    try:
                        self.instances.force_delete(instance.id)
                    except trove_exc.ClientException as e:
                        pass
                    raise fox_exc.FoxCloudException(error)
            return instance
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def _wait_create_instance(self, resource_id, timeout=ACTION_TIMEOUT, interval=10):
        """
        Check done task
        :param resource_id:
        :param type:
        :param timeout:
        :param interval:
        :return:
        """
        while timeout >= 0:
            data = self.instances.get(resource_id)
            if data.status == 'ACTIVE':
                return True, None
            if data.status == 'FAILED':
                return False, 'System error'
            timeout -= interval
            time.sleep(interval)
        return False, 'Action timeout'


    # **********************************************
    #   Update an openstack resource being created
    # **********************************************

    # **********************************************
    #   Delete an openstack resource being created
    # **********************************************

    # **********************************************
    #   Rollback an openstack resource being created
    # **********************************************