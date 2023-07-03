from magnumclient import exceptions as coe_exc

from foxcloud import (base as fox_base, exceptions as fox_exc, api_versions)
from foxcloud.i18n import _
from foxcloud.v1.services import base as service_base
from foxcloud.v1.utils.data_util import valid_kwargs


class COEResource(fox_base.Resource):
    """
    COE Resource
    """


class COEManager(service_base.BaseChildManager):
    """Basic manager for the shade services. Providing common
    operations such as creating, deleting, updating openstack servers.
    https://docs.openstack.org/magnum/latest/user/
    """
    resource_class = COEResource

    def __init__(self, name_or_id, version, session, engine, endpoint=None, **kwargs):
        super(COEManager, self).__init__(name_or_id, version, session, engine, endpoint, **kwargs)
        if not self._is_supported():
            msg = _("Not supported engine '%s'. "
                    "Expected %s") % {self.engine, ' or '.join(e.upper() for e in fox_base.SUPPORTED_ENGINES)}
            raise fox_exc.FoxCloudUnSupportedEngine(msg)

        # TODO check to find subclasses
        # self._api = sys_util.find_subclasses(self.engine, base_class=BaseInstance)
        if self.engine == 'heat':
            from foxcloud.v1.services.coe.heat import base
            self._api = base.Heat(session=session)
        if self.engine == 'console':
            from foxcloud.v1.services.coe import console
            self._api = console.Console(session=session)
        if not self._api:
            raise fox_exc.FoxCloudCreateException(resource=self.resource_class, resource_id=engine)

    def _is_supported(self):
        return self.supported_heat if self.engine == 'heat' else self.supported_console

    @property
    def supported(self):
        """Is supported services
        Subclass should be override this method

        :return:
        """
        return True

    @property
    def supported_heat(self):
        """Allow to do action by deploying heat stack
        Subclass should be override this method

        :return:
        """
        return True

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
    def get_cluster(self, cluster_id):
        """
        Get a specific cluster
        :param cluster_id:
        :return:
        """
        try:
            data = self._api.clusters.get(id=cluster_id)
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def get_cluster_template(self, template_id):
        """
        Get a specific cluster
        :param template_id:
        :return:
        """
        try:
            data = self._api.cluster_templates.get(id=template_id)
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def get_clusters(self):
        """
        List all clusters
        :return:
        """
        try:
            data = self._api.clusters.list()
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def get_cluster_templates(self):
        """
        List all cluster templates
        :return:
        """
        try:
            data = self._api.cluster_templates.list()
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    # **********************************************
    #   Create a new openstack resource
    # **********************************************
    def create_cluster(self, name, template_id, keypair_id, node_flavor_id, master_flavor_id,
                       node_count=1, master_count=1, network_id=None, subnet_id=None, timeout=3600,
                       floating_ip_enabled=True, labels={}, wait=False):
        data = self._api.create_cluster(name=name, template_id=template_id, keypair_id=keypair_id,
                                        node_flavor_id=node_flavor_id, master_flavor_id=master_flavor_id,
                                        node_count=node_count, master_count=master_count, network_id=network_id,
                                        subnet_id=subnet_id, timeout=timeout,
                                        floating_ip_enabled=floating_ip_enabled, labels=labels, wait=wait)
        return self.resource_class(self, info=data)

    @valid_kwargs('http_proxy', 'https_proxy', 'no_proxy', 'registry_enabled', 'insecure_registry')
    def create_cluster_template(self, name, keypair_id, docker_volume_size, external_network_id, image_id,
                                coe='kubernetes', network_driver='flannel', dns='8.8.8.8',
                                master_lb_enabled=False, floating_ip_enabled=True, volume_driver='cinder',
                                server_type='vm', docker_storage_driver='overlay', tls_disabled=True,
                                is_public=False, hidden=False, labels={}, wait=False, **kwargs):
        def _create_cluster_template():
            try:
                return self._api.create_cluster_template(name=name, keypair_id=keypair_id,
                                                         docker_volume_size=docker_volume_size,
                                                         external_network_id=external_network_id,
                                                         image_id=image_id, coe=coe,
                                                         network_driver=network_driver, dns=dns,
                                                         master_lb_enabled=master_lb_enabled,
                                                         floating_ip_enabled=floating_ip_enabled,
                                                         volume_driver=volume_driver, server_type=server_type,
                                                         docker_storage_driver=docker_storage_driver,
                                                         tls_disabled=tls_disabled, is_public=is_public,
                                                         hidden=hidden, labels=labels, wait=wait, **kwargs)
            except coe_exc.ClientException as e:
                raise fox_exc.FoxCloudBadRequest(e)

        return self.resource_class(self, info=_create_cluster_template())

    # **********************************************
    #   Update an openstack resource being created
    # **********************************************
    def update_cluster(self, cluster_id, patch):
        """
        Update a specific cluster
        Usage:
            patch = {'op': 'replace',
                     'value': NEW_NAME,
                     'path': '/name'}
            cluster = update_cluster(id='123', patch=patch)
        :param cluster_id:
        :param patch: Resource attribute’s name.
        :return:
        """
        try:
            data = self._api.update_cluster(cluster_id, patch)
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def resize_cluster(self, cluster_id, node_count, nodes_to_remove, nodegroup=None):
        """
        Resize a specific cluster
        :param cluster_id:
        :param node_count:
        :param nodes_to_remove:
        :param nodegroup:
        :return:
        """
        try:
            data = self._api.resize_cluster(cluster_id, node_count, nodes_to_remove, nodegroup)
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def upgrade_cluster(self, cluster_id, template_id, max_batch_size=1, nodegroup=None):
        """
        Upgrade a specific cluster
        :param cluster_id:
        :param template_id:
        :param max_batch_size:
        :param nodegroup:
        :return:
        """
        try:
            data = self._api.upgrade_cluster(cluster_id, template_id,
                                             max_batch_size, nodegroup)
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def update_cluster_template(self, template_id, patch):
        """
        Update a specific cluster
        Usage:
            patch = {
                "path":"/master_lb_enabled",
                "value":"True",
                "op":"replace"
            }
            cluster = update_cluster_template(id='123', patch=patch)
        :param template_id:
        :param patch: Resource attribute’s name.
        :return:
        """
        try:
            data = self._api.update_cluster_template(template_id, patch)
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    # **********************************************
    #   Delete an openstack resource being created
    # **********************************************
    def delete_cluster(self, cluster_id):
        """
        Delete a specific cluster.
        :param cluster_id: The UUID or name of clusters in Magnum.
        :return:
        """
        try:
            data = self._api.delete_cluster(cluster_id)
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def delete_cluster_template(self, template_id):
        """
        Delete a specific cluster.
        :param template_id: The UUID or name of cluster templates in Magnum.
        :return:
        """
        try:
            data = self._api.delete_cluster_template(template_id)
            return self.resource_class(self, info=data)
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)
