import time

from magnumclient import exceptions as coe_exc

from foxcloud import exceptions as fox_exc
from foxcloud.v1.services.coe.base import BaseCOE
from foxcloud.v1.utils.data_util import valid_kwargs


class Console(BaseCOE):
    __engine_type__ = 'console'
    LABELS = (
        'kube_dashboard_enabled', 'kube_dashboard_version',
        'availability_zone', 'ingress_controller',
        'ingress_controller_role', 'nginx_ingress_controller_tag',
        'octavia_ingress_controller_tag', 'auto_healing_enabled',
        'auto_scaling_enabled', 'min_node_count', 'max_node_count',
        'use_podman', 'container_infra_prefix'
    )

    # **********************************************
    #   Create a new openstack resource
    # **********************************************
    def create_cluster(self, name, template_id, keypair_id, node_flavor_id, master_flavor_id,
                       node_count=1, master_count=1, network_id=None, subnet_id=None, timeout=3600,
                       floating_ip_enabled=True, labels={}, wait=False):
        """
        :param name:
        :param template_id:
        :param keypair_id:
        :param node_flavor_id:
        :param master_flavor_id:
        :param node_count:
        :param master_count:
        :param network_id:
        :param subnet_id:
        :param timeout:
        :param floating_ip_enabled:
        :param labels:
        :param wait
        :return:
        """
        try:
            create_timeout = 60
            if timeout:
                create_timeout = timeout // 60

            cluster = self.clusters.create(name=name, cluster_template_id=template_id, node_count=node_count,
                                           master_count=master_count, create_timeout=create_timeout,
                                           keypair=keypair_id, flavor_id=node_flavor_id,
                                           master_flavor_id=master_flavor_id, fixed_network=network_id,
                                           fixed_subnet=subnet_id, floating_ip_enabled=floating_ip_enabled,
                                           labels=labels)
            if wait:
                status = self.wait_create_cluster(cluster_id=cluster.uuid, timeout=timeout, check_interval=30)
                # if not status:
                #     # Delete cluster
                #     self.clusters.delete(cluster.uuid)
                #     raise fox_exc.FoxCloudException("Action timeout")

            return cluster
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def wait_create_cluster(self, cluster_id, timeout, check_interval=60):
        while timeout >= 0:
            time.sleep(check_interval)
            cluster = self.clusters.get(id=cluster_id)
            if cluster:
                if cluster.status == 'CREATE_COMPLETE':
                    return True
                if cluster.status == 'CREATE_FAILED':
                    return False
            timeout -= check_interval
        return False

    @valid_kwargs('http_proxy', 'https_proxy', 'no_proxy', 'registry_enabled', 'insecure_registry')
    def create_cluster_template(self, name, keypair_id, docker_volume_size, external_network_id, image_id,
                                coe='kubernetes', network_driver='flannel', dns='8.8.8.8', master_lb_enabled=False,
                                floating_ip_enabled=True, volume_driver='cinder', server_type='vm',
                                docker_storage_driver='overlay', tls_disabled=True, is_public=False, hidden=False,
                                labels={}, wait=False, **kwargs):

        try:
            cluster = self.cluster_templates.create(name=name, keypair_id=keypair_id,
                                                    docker_volume_size=docker_volume_size,
                                                    external_network_id=external_network_id,
                                                    image_id=image_id, coe=coe,
                                                    network_driver=network_driver, dns_nameserver=dns,
                                                    master_lb_enabled=master_lb_enabled,
                                                    floating_ip_enabled=floating_ip_enabled,
                                                    volume_driver=volume_driver, server_type=server_type,
                                                    docker_storage_driver=docker_storage_driver,
                                                    tls_disabled=tls_disabled, public=is_public,
                                                    hidden=hidden, labels=labels, **kwargs)
            # if wait:
            #     status = self.wait_create_cluster_template(cluster_template_id=cluster.uuid,
            #                                                timeout=3600, check_interval=30)
            #     # if not status:
            #     #     # Delete cluster
            #     #     self.cluster_templates.delete(cluster.uuid)
            #     #     raise fox_exc.FoxCloudException("Action timeout")
            return cluster
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def wait_create_cluster_template(self, cluster_template_id, timeout=3600, check_interval=60):
        while timeout >= 0:
            time.sleep(check_interval)
            cluster = self.cluster_templates.get(id=cluster_template_id)
            if cluster:
                if cluster.status == 'CREATE_COMPLETE':
                    return True
                if cluster.status == 'CREATE_FAILED':
                    return False
            timeout -= check_interval
        return False

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
            data = self.clusters.update(id=cluster_id, patch=patch)
            return data
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def resize_cluster(self, cluster_id, node_count, nodes_to_remove, nodegroup=None):
        """

        :param cluster_id:
        :param node_count:
        :param nodes_to_remove:
        :param nodegroup:
        :return:
        """
        try:
            data = self.clusters.resize(cluster_id, node_count, nodes_to_remove, nodegroup)
            return data
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def upgrade_cluster(self, cluster_id, template_id, max_batch_size=1, nodegroup=None):
        """

        :param cluster_id:
        :param template_id:
        :param max_batch_size:
        :param nodegroup:
        :return:
        """
        try:
            data = self.clusters.upgrade(cluster_id, template_id, max_batch_size, nodegroup)
            return data
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
            data = self.cluster_templates.update(id=template_id, patch=patch)
            return data
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
            data = self.clusters.delete(id=cluster_id)
            return data
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)

    def delete_cluster_template(self, template_id):
        """
        Delete a specific cluster.
        :param template_id: The UUID or name of cluster templates in Magnum.
        :return:
        """
        try:
            data = self.cluster_templates.delete(id=template_id)
            return data
        except coe_exc.ClientException as e:
            raise fox_exc.FoxCloudBadRequest(e)
