#
# Copyright (c) 2020 FTI-CAS
#

from troveclient import exceptions as trove_exc
from troveclient import base

from foxcloud import (base as fox_base, exceptions as fox_exc, api_versions)
from foxcloud.i18n import _
from foxcloud.v1.services import base as service_base
from foxcloud.v1.utils.data_util import valid_kwargs
from foxcloud.v1.utils import str_util


class TroveResource(fox_base.Resource):
    """"""
    # def add_details(self, info):
    #     """Normalize data information
    #     Subclass should be override this method
    #     :param info:
    #     :return:
    #     """
    #     data = []
    #     if isinstance(info, list):
    #         for item in info:
    #             data.append(item.to_dict())
    #     elif isinstance(info, dict):
    #         data = info
    #     else:
    #         data = info.to_dict()
    #     self.data = data


class TroveManager(service_base.BaseChildManager):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    resource_class = TroveResource

    def __init__(self, name_or_id, version, session, engine, endpoint=None, **kwargs):
        super(TroveManager, self).__init__(name_or_id, version, session, engine, endpoint, **kwargs)
        if not self._is_supported():
            msg = _("Not supported engine '%s'. "
                    "Expected %s") % {self.engine, ' or '.join(e.upper() for e in fox_base.SUPPORTED_ENGINES)}
            raise fox_exc.FoxCloudUnSupportedEngine(msg)

        # TODO check to find subclasses
        # self._api = sys_util.find_subclasses(self.engine, base_class=BaseInstance)
        if self.engine == 'heat':
            from foxcloud.v1.services.trove.heat import base
            self._api = base.Heat(session=session)
        if self.engine == 'console':
            from foxcloud.v1.services.trove import console
            self._api = console.Console(session=session)
        if not self._api:
            raise fox_exc.FoxCloudCreateException(resource=self.resource_class, resource_id=engine)

    def _is_supported(self):
        return self.supported_heat if self.engine == 'heat' else self.supported_console

    @property
    def supported_heat(self):
        """Allow to do action by deploying heat stack
        Subclass should be override this method

        :return:
        """
        return False

    @property
    def supported_console(self):
        """Allow to do action by making http requests directly to openstack services
        Subclass should be override this method

        :return:
        """
        return True

    # **********************************************
    #   Fetch the information of openstack resources
    # **********************************************

    def get_datastore(self, datastore_id):
        """
        Get a specific datastore being created
        :param datastore_id:
        :return:
        """
        try:
            data = self._api.datastores.get(datastore_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_datastores(self, limit=None, marker=None):
        """List all datastores
        :param limit:
        :param marker:
        :return:
        """
        try:
            data = self._api.datastores.list(limit, marker)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_datastore_versions(self, datastore_id, limit=None, marker=None):
        """List all datastores
        :param datastore_id
        :param limit:
        :param marker:
        :return:
        """
        try:
            data = self._api.datastore_versions.list(datastore_id, limit, marker)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_datastore_version(self, datastore_id, datastore_version_id):
        """
        Get specific datastore version
        :param datastore_id:
        :param datastore_version_id:
        :return:
        """
        try:
            datastore = self._api.datastore_versions.get(datastore_id, datastore_version_id)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=datastore)

    def get_cluster(self, cluster_id):
        """
        :param cluster_id:
        :return:
        """
        try:
            ds = self._api.clusters.get(cluster=cluster_id)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=ds)

    def get_clusters(self, limit=None, marker=None):
        try:
            data = self._api.clusters.list(limit, marker)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_instance(self, instance_id):
        """Get a database shade being created
        :param instance_id:
        :return:
        """
        try:
            data = self._api.instances.get(instance=instance_id)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_instances(self, limit=None, marker=None, include_clustered=False, detailed=False):
        """Get a list of all instances.
        :param limit:
        :param marker:
        :param include_clustered:
        :param detailed:
        :return:
        """
        try:
            data = self._api.instances.list(limit, marker, include_clustered, detailed)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_instance_backups(self, instance_id, limit=None, marker=None):
        """Get the list of backups for a specific shade.
        :param shade: shade for which to list backups
        :param limit: max items to return
        :param marker: marker start point
        :return: list
        """
        try:
            data = self._api.instances.bacups(instance_id, limit, marker)
        except trove_exc.ClientException as e:
            return []
        return self.resource_class(self, info=data)

    def get_instance_config(self, instance_id):
        """Get a configuration on instances.
        :param instance_id:
        :return:
        """
        try:
            data = self._api.instances.configuration(instance_id)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_logs(self, instance_id):
        """
        List all logs of shade
        :param instance_id:
        :return:
        """
        try:
            data = self._api.instances.log_list(instance_id)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_log(self, instance_id, log_name):
        """
        Get shade log by log name
        :param instance_id:
        :param log_name:
        :return:
        """
        try:
            data = self._api.instances.log_show(instance_id, log_name)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_backup(self, backup_id):
        """
        Get a specific backup being created
        :param backup_id:
        :return:
        """
        try:
            data = self._api.backups.get(backup_id)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_backups(self, limit=None, marker=None, datastore_id=None, instance_id=None,
                    all_projects=False):
        """
        Get a list of all backups.
        :param limit:
        :param marker:
        :param datastore_id:
        :param instance_id:
        :param all_projects:
        :return:
        """
        try:
            data = self._api.backups.list(limit, marker, datastore_id, instance_id, all_projects)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_backup_strategies(self, instance_id):
        """
        Get a specific backup being created
        :param instance_id:
        :return:
        """
        try:
            data = self._api.backup_strategies.list(instance_id)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_config(self, config_id):
        """
        Get a specific configuration being created
        :param config_id:
        :return:
        """
        try:
            data = self._api.configurations.get(config_id)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_configs(self, limit=None, marker=None):
        """
        Get a list of instances on a configuration.
        :param limit:
        :param marker:
        :return:
        """
        try:
            data = self._api.configurations.list(limit, marker)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_config_instances(self, config_id, limit=None, marker=None):
        """
        Get a list of instances on a configuration.
        :param config_id:
        :param limit:
        :param marker:
        :return:
        """
        try:
            data = self._api.configurations.instances(config_id, limit, marker)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_database(self, instance_id, limit=None, marker=None):
        """
        Get a list of all Databases from the shade
        :param instance_id:
        :param limit:
        :param marker:
        :return:
        """
        try:
            data = self._api.databases.get(instance_id, limit, marker)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_user(self, instance_id, username, hostname=None):
        """
        Get a single User from the shade's Database.
        :param instance_id:
        :param username:
        :param hostname:
        :return:
        """
        try:
            data = self._api.users.get(instance_id, username, hostname)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_users(self, instance_id, limit=None, marker=None):
        """
        Get a list of all Users from the shade's database.
        :param instance_id:
        :param limit:
        :param marker:
        :return:
        """
        try:
            data = self._api.users.list(instance_id, limit, marker)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def get_user_database_access(self, instance_id, username, hostname=None):
        """
        Show all databases the given user has access to
        :param instance_id:
        :param username:
        :param hostname:
        :return:
        """
        try:
            data = self._api.users.get_access(instance_id, username, hostname)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    # **********************************************
    #   Create a new openstack resource
    # **********************************************
    def create_cluster(self, name, datastore_id, datastore_version_id, flavor_id, volume_size,
                       volume_type=None, number_of_instances=3, network_id=None, locality=None,
                       availability_zone=None, extended_properties=None, configuration=None,
                       wait=False):
        """
        Create a new cluster
        :param name:
        :param datastore_id:
        :param datastore_version_id:
        :param flavor_id:
        :param volume_size:
        :param volume_type:
        :param number_of_instances:
        :param network_id:
        :param locality:
        :param availability_zone:
        :param extended_properties:
        :param configuration:
        :param wait:
        :return:
        """
        instances = []
        for i in range(0, number_of_instances):
            instance = {
                'name': str_util.h_join(name, 'member', str(i+1)),
                'flavorRef': flavor_id,
                'volume': {
                    'size': volume_size,
                },
                'net-id': network_id,
            }
            if volume_type:
                instance['volume']['type'] = volume_type
            if availability_zone:
                instance['availability_zone'] = availability_zone
            instances.append(instance)

        cluster = self._api.create_cluster(name, datastore_id, datastore_version_id, instances,
                                           locality, extended_properties, configuration, wait)
        return self.resource_class(self, info=cluster)

    @valid_kwargs()
    def create_instance(self, name, flavor_id=None, volume=None, databases=None,
                        users=None, restore_point=None, availability_zone=None,
                        datastore_id=None, datastore_version_id=None, nics=None,
                        configuration=None, replica_of=None, replica_count=None,
                        modules=None, locality=None, region_name=None, access=None,
                        wait=False, **kwargs):
        """
        Create a new instance.
        :param name:
        :param flavor_id:
        :param volume:
        :param databases:'ty
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
        data = self._api.create_instance(name, flavor_id, volume, databases,
                                         users, restore_point, availability_zone,
                                         datastore_id, datastore_version_id, nics,
                                         configuration, replica_of, replica_count,
                                         modules, locality, region_name, access,
                                         wait, **kwargs)
        return self.resource_class(self, info=data)

    def do_instance_action(self, instance_id, action):
        """
        Do an shade's action.
        Allow user role to do actions
        :param instance_id:
        :param action: [stop, reboot, restart, reset]
        :return:
        """
        try:
            # Only Admin
            if action in ['stop', 'reboot']:
                class_call = getattr(self._api.instances, 'mgmt_instances')
                func_call = getattr(class_call, action)
                data = func_call(instance_id)
            elif action in ['restart', 'reset']:
                class_call = getattr(self._api, 'instances')
                func_call = getattr(class_call, action)
                data = func_call(instance_id)
            else:
                msg = _("Not support action '%s'" % action)
                raise fox_exc.FoxCloudException(msg)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=data)

    def set_log_action(self, instance_id, log_name, enable=None, disable=None,
                       publish=None, discard=None):
        """
        Perform action on guest log.
        :param instance_id:
        :param log_name: The name of <log> to publish
        :param enable: Turn on <log>
        :param disable: Turn off <log>
        :param publish: Publish log to associated container
        :param discard: Delete the associated container
        """
        try:
            data = self._api.instances.log_action(instance_id, log_name, enable,
                                                  disable, publish, discard)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_backup(self,  name, instance_id, description=None,
                      parent_id=None, incremental=False, swift_container=None):
        """
        Create a backup.
        :param name:
        :param instance_id:
        :param description:
        :param parent_id:
        :param incremental:
        :param swift_container:
        :return:
        """
        try:
            data = self._api.backups.create(name, instance_id, description, parent_id,
                                            incremental, swift_container)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_backup_strategy(self, instance_id=None, swift_container=None):
        """
        Create a backup strategy.
        :param instance_id:
        :param swift_container:
        :return:
        """
        try:
            data = self._api.backup_strategies.create(instance_id, swift_container)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_config(self, name, values, description=None, datastore_id=None,
                      datastore_version_id=None):
        """
        Create a new configuration.
        :param name:
        :param values:
        :param description:
        :param datastore_id:
        :param datastore_version_id:
        :return:
        """
        try:
            data = self._api.configurations.create(name, values, description,
                                                   datastore_id, datastore_version_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_database(self, instance_id, databases):
        """Create a database.
        :param instance_id: ID of database shade
        :param databases:
        :return:
        """
        try:
            data = self._api.databases.create(instance_id, databases)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_user(self, instance_id, users):
        """
        Create a user for a specific shade being created.
        :param instance_id: ID of database shade
        :param users:
        :return:
        """
        try:
            data = self._api.users.create(instance_id, users)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    # **********************************************
    #   Update an openstack resource being created
    # **********************************************
    def attach_or_detach_config(self, instance_id, config_id):
        """
        Attach/Detach configuration group to database shade
        :param instance_id:
        :param config_id:
        :return:
        """
        try:
            data = self._api.instances.modify(instance_id, config_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_instance(self, instance_id, configuration=None, name=None,
                        detach_replica_source=False, remove_configuration=False):
        """
        Update a database shade being created.
        :param instance_id:
        :param config_id:
        :param name:
        :param detach_replica_source:
        :param remove_configuration:
        :return:
        """
        try:
            data = self._api.instances.edit(instance_id, configuration, name,
                                            detach_replica_source, remove_configuration)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def upgrade_instance(self, instance_id, datastore_version_id):
        """
        Upgrades an shade with a new datastore version.
        :param instance_id:
        :param datastore_version_id:
        :return: 
        """
        try:
            data = self._api.instances.upgrade(instance_id, datastore_version_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def promote_replica(self, instance_id):
        """
        Promote a replica to be the new master shade.
        :param instance_id:
        :return:
        """
        try:
            data = self._api.instances.promote_to_replica_source(instance_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def eject_replica(self, instance_id):
        """
        Remove the master shade in a replication set.
        :param instance_id:
        :return:
        """
        try:
            data = self._api.instances.eject_replica_source(instance_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def resize_volume(self, instance_id, volume_size):
        """
        Resize the volume on an existing instances being created.
        :param instance_id:
        :param volume_size:
        :return:
        """
        try:
            data = self._api.instances.resize_volume(instance_id, volume_size)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def resize_instance(self, instance_id, flavor_id):
        """
        Resize the volume on an existing instances being created.
        :param instance_id:
        :param flavor_id:
        :return:
        """
        try:
            data = self._api.instances.resize_instance(instance_id, flavor_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_config(self, config_id, values, name=None, description=None):
        """
        Update an existing configuration
        :param config_id:
        :param values:
        :param name:
        :param description:
        :return:
        """
        try:
            data = self._api.configurations.update_config(config_id, values,
                                                          name, description)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_user(self, instance_id, username, newuserattr=None, hostname=None):
        """
        Update attributes of a single User in an shade being created.
        :param instance_id:
        :param username:
        :param newuserattr:
        :param hostname:
        :return:
        """
        try:
            data = self._api.users.update_attributes(instance_id, username,
                                                     newuserattr, hostname)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def change_passwords(self, instance_id, users):
        """
        Change the password for one or more users being created.
        :param instance_id:
        :param users:
        :return:
        """
        try:
            data = self._api.users.change_passwords(instance_id, users)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def grant_permissions(self, instance_id, username, databases, hostname=None):
        """
        Allow an existing user permissions to access a database
        :param instance_id:
        :param username:
        :param databases:
        :param hostname:
        :return:
        """

        try:
            data = self._api.users.grant(instance_id, username, databases, hostname)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    # **********************************************
    #   Delete an openstack resource being created
    # **********************************************
    def delete_cluster(self, cluster_id):
        """
        Delete a specific cluster
        :param cluster_id:
        :return:
        """
        try:
            data = self._api.clusters.delete(cluster_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_instance(self, instance_id, force=False):
        """
        Force delete the specified shade being created.
        :param instance_id:
        :param force:
        :return:
        """
        try:
            if force:
                data = self._api.instances.force_delete(instance_id)
            else:
                data = self._api.instances.delete(instance_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_backup(self, backup_id):
        """
        Force delete the specified backup.
        :param backup_id:
        :return:
        """
        try:
            data = self._api.backups.delete(backup_id)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_backup_strategy(self, instance_id):
        """
        Force delete the specified backup strategy being created.
        :param instance_id:
        :return:
        """
        try:
            data = self._api.backup_strategies.delete(instance_id, None)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_config(self, config_id):
        """
        Force delete the specified config being created.
        :param config_id:
        :return:
        """
        try:
            data = self._api.configurations.delete(config_id, None)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_database(self, instance_id, dbname):
        """
        Force delete the specified database being created.
        :param instance_id:
        :param dbname:
        :return:
        """
        try:
            data = self._api.databases.delete(instance_id, dbname)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_user(self, instance_id, username, hostname=None):
        """
        Force delete the specified user being created.
        :param instance_id:
        :param username:
        :param hostname:
        :return:
        """
        try:
            data = self._api.users.delete(instance_id, username, hostname)
            return self.resource_class(self, info=data)
        except trove_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
