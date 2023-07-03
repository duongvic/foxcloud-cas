#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud.v1.services.stack.orchestrator import heat
from foxcloud.v1.utils.data_util import valid_kwargs
from foxcloud.v1.utils import str_util


class CoeHeatTemplate(heat.HeatTemplate):
    def __init__(self, name, template_file=None, heat_parameters=None, session=None):
        super(CoeHeatTemplate, self).__init__(name, template_file, heat_parameters, session)

    @valid_kwargs('discovery_url')
    def add_cluster(self, stack_name, name, template, master_count, node_count, keypair, timeout, **kwagrs):
        """
        Create a new magnum cluster.
        :param name:
        :param template:
        :param master_count:
        :param node_count:
        :param keypair:
        :param timeout:
        :param kwagrs:
        :return:
        """
        dn = str_util.h_join(stack_name, name)
        self.resources[dn] = {
            'type': 'OS::Magnum::Cluster',
            'depends_on': [template],
            'properties': {
                'name': name,
                'cluster_template': {'get_resource': template},
                'create_timeout': timeout,
                'keypair': keypair,
                'master_count': master_count,
                'node_count': node_count,
                **kwagrs
            }
        }

        self._template['outputs'][dn] = {
            'description': 'Cluster %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][dn + '-api_address'] = {
            'description': 'The endpoint URL of COE API exposed to end-users.',
            'value': {'get_attr': [name, 'api_address']}
        }
        self._template['outputs'][dn + '-status'] = {
            'description': 'The status for this COE cluster.',
            'value': {'get_attr': [dn, 'status']}
        }
        self._template['outputs'][dn + '-status_reason'] = {
            'description': 'The reason of cluster current status.',
            'value': {'get_attr': [dn, 'status_reason']}
        }

    @valid_kwargs('server_type', 'no_proxy', 'public', 'master_lb_enabled', 'floating_ip_enabled',
                  'docker_storage_driver', 'https_proxy', 'http_proxy', 'registry_enabled',
                  'tls_disabled', 'dns_nameserver')
    def add_cluster_template(self, stack_name, name, coe, external_network, image,
                             worker_flavor=None, master_flavor=None, volume_driver=None,
                             network_driver='cinder', volume_size=30, fixed_network=None,
                             fixed_subnet=None, keypair=None, labels=None,
                             **kwargs):
        """
        Create a new magnum cluster template
        :param stack_name:
        :param name:
        :param coe:
        :param external_network:
        :param image:
        :param worker_flavor:
        :param master_flavor:
        :param volume_driver:
        :param network_driver:
        :param volume_size:
        :param fixed_network:
        :param fixed_subnet:
        :param keypair:
        :param labels:
        :param kwargs:
        :return:
        """
        dn = str_util.h_join(stack_name, name)
        self.resources[dn] = {
            'type': 'OS::Magnum::ClusterTemplate',
            'properties': {
                'name': name,
                'coe': coe,
                'external_network': external_network,
                'image': image,
                'flavor': worker_flavor,
                'master_flavor': master_flavor,
                'docker_storage_driver': volume_driver,
                'network_driver': network_driver,
                'docker_volume_size': volume_size,
                'fixed_network': fixed_network,
                'fixed_subnet': fixed_subnet,
                'keypair': keypair,
                'labels': labels or [],
                **kwargs
            }
        }
        self._template['outputs'][dn] = {
            'description': 'Cluster %s ID' % dn,
            'value': {'get_resource': dn}
        }
        self._template['outputs'][dn + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [dn, 'show']}
        }
