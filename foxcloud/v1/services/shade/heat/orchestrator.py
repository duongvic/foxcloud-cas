import collections
import time

from foxcloud import exceptions as fox_exc
from foxcloud.v1.services.stack.orchestrator import heat
from foxcloud.v1.services.shade.heat import model as md
from foxcloud.v1.utils.data_util import valid_kwargs
from foxcloud.v1.utils import constants as consts, str_util


class NovaHeatTemplate(heat.HeatTemplate):

    def __init__(self, name, template_file=None, heat_parameters=None, session=None):
        super(NovaHeatTemplate, self).__init__(name, template_file, heat_parameters, session)

    @valid_kwargs('disk', 'ephemeral', 'extra_specs', 'flavor_id', 'is_public',
                  'rxtx_factor', 'swap', 'tenants')
    def add_flavor(self, name, vcpus=1, ram=1024, **kwargs):
        """
        Add a flavor to the template file
        Refer: https://docs.openstack.org/heat/pike/template_guide/openstack.html#OS::Nova::Flavor
        :param name: (required)
        :param vcpus: (required)
        :param ram: (required)
        :param kwargs: (optional)
        :return:
        """
        if name is None:
            name = 'auto'

        self.resources[name] = {
            'type': 'OS::Nova::Flavor',
            'properties': {
                'name': name,  # a descriptive name
                'vcpus': vcpus,
                'ram': ram,
                'is_public': kwargs.get('is_public') or False,
            }
        }

        optional_properties = {}
        disk = kwargs.get('disk')
        if disk:
            assert isinstance(disk, int)
            optional_properties['disk'] = disk

        swap = kwargs.get('swap')
        if swap:
            assert isinstance(swap, int)
            optional_properties['swap'] = swap

        flavor_id = kwargs.get('flavor_id')
        if swap:
            assert isinstance(flavor_id, str)
            optional_properties['flavorid'] = flavor_id

        rxtx_factor = kwargs.get('rxtx_factor')
        if rxtx_factor:
            assert isinstance(rxtx_factor, str)
            optional_properties['rxtx_factor'] = rxtx_factor

        ephemeral = kwargs.get('ephemeral')
        if ephemeral:
            assert isinstance(ephemeral, str)
            optional_properties['ephemeral'] = ephemeral

        extra_specs = kwargs.get('extra_specs')
        if extra_specs:
            assert isinstance(extra_specs, collections.Mapping)
            optional_properties['extra_specs'] = extra_specs

        tenants = kwargs.get('tenants')
        if tenants:
            assert isinstance(tenants, list)
            optional_properties['tenants'] = tenants

        self._template['outputs'][name] = {
            'description': 'Flavor %s ID' % name,
            'value': {'get_resource': name}
        }
        self.resources[name]['properties'].update(optional_properties)

    @valid_kwargs('gigabytes', 'snapshots', 'volumes')
    def add_volume_quota(self, name, project, **kwargs):
        """
        Add volume quota
        :param name: (required)
        :param project: (required)
        :param kwargs: (optional)
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Cinder::Quota',
            'properties': {
                'project': project,
            }
        }

        optional_properties = {}
        gigabytes = kwargs.get('gigabytes')
        if gigabytes:
            assert isinstance(gigabytes, int)
            optional_properties['gigabytes'] = gigabytes

        snapshots = kwargs.get('snapshots')
        if snapshots:
            assert isinstance(snapshots, int)
            optional_properties['snapshots'] = snapshots

        volumes = kwargs.get('volumes')
        if volumes:
            assert isinstance(volumes, int)
            optional_properties['volumes'] = volumes

        self.resources[name]['properties'].update(optional_properties)

    @valid_kwargs('availability_zone', 'backup_id', 'image', 'metadata',
                  'read_only', 'scheduler_hints', 'snapshot_id', 'source_vol_id',
                  'volume_type', 'multi_attach')
    def add_volume(self, name, stack_name, size=10, description=None, **kwargs):
        """
        Add a new volume
        :param name: (required)
        :param stack_name: (required)
        :param size: (required)
        :param description:
        :param kwargs:
        :return:
        """
        stack_name = str_util.h_join(stack_name, name)
        self.resources[stack_name] = {
            'type': 'OS::Cinder::Volume',
            'properties': {
                'name': name,
                'size': size,
                'read_only': kwargs.get('read_only') or False,
                'description': description,
                'multiattach': kwargs.get('multi_attach') or False,
            }
        }
        optional_properties = {}

        availability_zone = kwargs.get('availability_zone')
        if availability_zone:
            assert isinstance(availability_zone, str)
            optional_properties['availability_zone'] = availability_zone

        backup_id = kwargs.get('backup_id')
        if backup_id:
            assert isinstance(backup_id, str)
            optional_properties['backup_id'] = backup_id

        image = kwargs.get('image')
        if image:
            assert isinstance(image, str)
            optional_properties['image'] = image

        metadata = kwargs.get('metadata')
        if metadata:
            assert isinstance(metadata, collections.Mapping)
            optional_properties['metadata'] = metadata

        scheduler_hints = kwargs.get('scheduler_hints')
        if scheduler_hints:
            assert isinstance(scheduler_hints, collections.Mapping)
            optional_properties['scheduler_hints'] = scheduler_hints

        snapshot_id = kwargs.get('snapshot_id')
        if snapshot_id:
            assert isinstance(snapshot_id, str)
            optional_properties['snapshot_id'] = snapshot_id

        volume_type = kwargs.get('volume_type')
        if volume_type:
            assert isinstance(volume_type, str)
            optional_properties['volume_type'] = {
                'get_resource': volume_type,
            }

        self.resources[stack_name]['properties'].update(optional_properties)

        self._template['outputs'][stack_name] = {
            'description': 'Volume %s ID' % stack_name,
            'value': {'get_resource': stack_name}
        }

    def add_volume_attachment(self, name, server_name, volume, mount_point=None):
        """
        Add to the template an association of volume to instance
        Refer: https://docs.openstack.org/heat/latest/template_guide/openstack.html
        :param name:
        :param server_name:
        :param volume:
        :param mount_point:
        :return:
        """
        properties = {
            'instance_uuid': {'get_resource': server_name},
        }
        volume_id = volume.get('uuid')
        if volume_id:
            properties['volume_id'] = volume_id
        else:
            volume_name = str_util.h_join(server_name, volume.get('name'))
            properties['volume_id'] = {'get_resource': volume_name}

        name = str_util.h_join(server_name, name)

        self.resources[name] = {
            'type': 'OS::Cinder::VolumeAttachment',
            'properties': properties,
        }

        if mount_point:
            assert isinstance(mount_point, str)
            self.resources[name]['properties']['mountpoint'] = mount_point

    def add_network_info(self, network):
        """
        Add to the template a Neutron Net
        Refer: https://docs.openstack.org/heat/pike/template_guide/openstack.html#OS::Neutron::Net
        Usage:
        from cas.contexts.model import Network
        net = Network()
        add_network_info(net)

        :param network: (required)
        :return:
        """
        name = network.name
        if network.provider is None:
            self.resources[name] = {
                'type': 'OS::Neutron::Net',
                'properties': {
                    'name': name,
                    'admin_state_up':  True,
                }
            }
        else:
            network_type = network.network_type
            self.resources[name] = {
                'type': 'OS::Neutron::ProviderNet',
                'properties': {
                    'name': name,
                    'network_type': 'flat' if network_type is None else network_type,
                    'physical_network': network.physical_network,
                },
            }
            segmentation_id = network.segmentation_id
            if segmentation_id:
                self.resources[name]['properties']['segmentation_id'] = segmentation_id
                if network_type is None:
                    self.resources[name]['properties']['network_type'] = 'vlan'

            # if port security is not defined then don't add to template:
            # some deployments don't have port security plugin installed
            if network.port_security_enabled:
                self.resources[name]['properties']['port_security_enabled'] = network.port_security_enabled

            tags = network.tags
            if tags:
                assert isinstance(tags, list)
                self.resources[name]['properties']['tags'] = tags

            # The ID of the tenant which will own the network.
            tenant_id = network.tenant_id
            if tenant_id:
                self.resources[name]['properties']['tenant_id'] = tenant_id

            value_specs = network.value_specs
            if value_specs:
                assert isinstance(value_specs, dict)
                self.resources[name]['properties']['value_specs'] = value_specs

    @valid_kwargs('admin_state_up', 'dhcp_agent_ids', 'dns_domain', 'qos_policy', 'tags',
                  'value_specs')
    def add_network(self, name, physical_network='physnet', provider=None, segmentation_id=None,
                    network_type=None, admin_state_up=True, shared=False, port_security_enabled=True,
                    tenant_id=None, **kwargs):
        """
        Add to the template a Neutron Net
        Refer: https://docs.openstack.org/heat/latest/template_guide/openstack.html#OS::Neutron::Net
        Usage:
        def my_func()
            add_network('some-network', 'physnet2', 'sriov', shared=True)

        :param name: (required)
        :param physical_network: (required)
        :param provider: (required)
        :param segmentation_id: (required)
        :param network_type: (required)
        :param admin_state_up: (required)
        :param shared: (required)
        :param port_security_enabled: (required)
        :param tenant_id: (required)
        :param kwargs: (optional)
        :return:
        """
        optional_properties = {}
        if provider is None:
            self.resources[name] = {
                'type': 'OS::Neutron::Net',
                'properties': {
                    'name': name,
                }
            }

            qos_policy = kwargs.get('qos_policy')
            if qos_policy:
                assert isinstance(qos_policy, str)
                optional_properties['qos_policy'] = {
                    'get_resource': qos_policy,
                }

            tags = kwargs.get('tags')
            if tags:
                assert isinstance(tags, list)
                optional_properties['tags'] = tags

            # The ID of the tenant which will own the network.
            if tenant_id:
                assert isinstance(tenant_id, str)
                optional_properties['tenant_id'] = tenant_id

            value_specs = kwargs.get('value_specs')
            if value_specs:
                assert isinstance(value_specs, collections.Mapping)
                optional_properties['value_specs'] = value_specs

        else:
            self.resources[name] = {
                'type': 'OS::Neutron::ProviderNet',
                'properties': {
                    'name': name,
                    'network_type': 'flat' if network_type is None else network_type,
                    'physical_network': physical_network,
                    'router_external': kwargs.get('router_external') or False,
                },
            }
            if segmentation_id:
                self.resources[name]['properties']['segmentation_id'] = segmentation_id
                if network_type is None:
                    self.resources[name]['properties']['network_type'] = 'vlan'

        optional_properties['admin_state_up'] = admin_state_up or True
        optional_properties['port_security_enabled'] = port_security_enabled or True
        optional_properties['shares'] = shared or False

        self.resources[name]['properties'].update(optional_properties)

    def add_network(self, network):
        """
        Add to the template a Neutron Net
        Refer: https://docs.openstack.org/heat/latest/template_guide/openstack.html#OS::Neutron::Net
        :param network: model.Network object
        :return:
        """
        name = network.stack_name
        optional_properties = {}
        if network.provider is None:
            self.resources[name] = {
                'type': 'OS::Neutron::Net',
                'properties': {
                    'name': name,
                }
            }

            qos_policy = network.qos_policy
            if qos_policy:
                optional_properties['qos_policy'] = {
                    'get_resource': qos_policy,
                }

            tags = network.tags
            if tags:
                optional_properties['tags'] = tags

            # The ID of the tenant which will own the network.
            tenant_id = network.tenant_id
            if tenant_id:
                optional_properties['tenant_id'] = tenant_id

            value_specs = network.value_specs
            if value_specs:
                assert isinstance(value_specs, collections.Mapping)
                optional_properties['value_specs'] = value_specs

        else:
            self.resources[name] = {
                'type': 'OS::Neutron::ProviderNet',
                'properties': {
                    'name': name,
                    'network_type': network.network_type or 'flat',
                    'physical_network': network.physical_network,
                    'router_external': network.router_external or False,
                },
            }
            segmentation_id = network.segmentation_id
            if segmentation_id:
                self.resources[name]['properties']['segmentation_id'] = segmentation_id
                if network.network_type is None:
                    self.resources[name]['properties']['network_type'] = 'vlan'

        optional_properties['admin_state_up'] = network.admin_state_up or True
        optional_properties['port_security_enabled'] = network.port_security_enabled or True
        optional_properties['shares'] = network.shared or False

        self.resources[name]['properties'].update(optional_properties)

    @valid_kwargs()
    def add_qos_policy(self, name, policy_type, **kwargs):
        if policy_type == md.QoSPolicyType.QoSBandwidthLimitRule:
            pass

    def add_server_group(self, name, policies):
        """
        Add to the template a ServerGroup
        :param name: (required)
        :param policies: (required)
        :return:
        """
        policies = policies if isinstance(policies, list) else [policies]
        self.resources[name] = {
            'type': 'OS::Nova::ServerGroup',
            'properties': {'name': name, 'policies': policies}
        }

    @valid_kwargs('allocation_pools', 'dns_nameservers', 'host_routes', 'ip_version',
                  'ipv6_address_mode', 'ipv6_ra_mode', 'prefixlen', 'segment',
                  'subnetpool', 'tags', 'value_specs')
    def add_subnet(self, name, network, cidr, gateway_ip=None, enable_dhcp=True, **kwargs):
        """
        Add to the template a Neutron Subnet
        :param name:
        :param network:
        :param cidr:
        :param gateway_ip:
        :param enable_dhcp:
        :param kwargs:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Neutron::Subnet',
            'depends_on': network,
            'properties': {
                'name': name,
                'cidr': cidr,
                'network_id': {'get_resource': network},
                'enable_dhcp': enable_dhcp,
                'gateway_ip': gateway_ip,
                'ip_version': kwargs.get('ip_version') or 4,
            }
        }
        optional_properties = {}

        allocation_pools = kwargs.get('allocation_pools')
        if allocation_pools:
            assert isinstance(allocation_pools, dict)
            optional_properties['allocation_pools'] = allocation_pools

        dns_nameservers = kwargs.get('dns_nameservers')
        if dns_nameservers:
            assert isinstance(dns_nameservers, list)
            optional_properties['dns_nameservers'] = dns_nameservers

        host_routes = kwargs.get('host_routes')
        if host_routes:
            assert isinstance(dns_nameservers, list)
            optional_properties['host_routes'] = host_routes

        if kwargs.get('ip_version') == 6:
            ipv6_address_mode = kwargs.get('ipv6_address_mode')
            if ipv6_address_mode:
                assert isinstance(dns_nameservers, str)
                optional_properties['ipv6_address_mode'] = ipv6_address_mode

            ipv6_ra_mode = kwargs.get('ipv6_ra_mode')
            if ipv6_ra_mode:
                assert isinstance(dns_nameservers, str)
                optional_properties['ipv6_ra_mode'] = ipv6_ra_mode

        prefix_len = kwargs.get('prefix_len')
        if prefix_len:
            assert isinstance(dns_nameservers, str)
            optional_properties['prefixlen'] = prefix_len

        segment = kwargs.get('segment')
        if segment:
            assert isinstance(dns_nameservers, str)
            optional_properties['segment'] = segment

        tags = kwargs.get('tags')
        if tags:
            assert isinstance(tags, list)
            optional_properties['tags'] = tags

        tenant_id = kwargs.get('tenant_id')
        if tenant_id:
            optional_properties['tenant_id'] = tenant_id

        value_specs = kwargs.get('value_specs')
        if value_specs:
            assert isinstance(value_specs, collections.Mapping)
            optional_properties['value_specs'] = value_specs

        self.resources[name]['properties'].update(optional_properties)

        self._template['outputs'][name] = {
            'description': 'subnet %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + "-cidr"] = {
            'description': 'subnet %s cidr' % name,
            'value': {'get_attr': [name, 'cidr']}
        }
        self._template['outputs'][name + "-gateway_ip"] = {
            'description': 'subnet %s gateway_ip' % name,
            'value': {'get_attr': [name, 'gateway_ip']}
        }
        self._template['outputs'][name + "-ip_version"] = {
            'description': 'subnet %s ip_version' % name,
            'value': {'get_attr': [name, 'ip_version']}
        }
        self._template['outputs'][name + "-network_id"] = {
            'description': 'subnet %s network_id' % name,
            'value': {'get_attr': [name, 'network_id']}
        }

    def add_subnet(self, network, subnet):
        """
        Add to the template a Neutron Subnet
        :param network:
        :param subnet: model.Subnet object
        :return:
        """
        name = subnet.name
        cidr = subnet.cidr

        self.resources[name] = {
            'type': 'OS::Neutron::Subnet',
            'depends_on': network,
            'properties': {
                'name': name,
                'cidr': cidr,
                'network_id': {'get_resource': network},
                'enable_dhcp': subnet.enable_dhcp,
                'gateway_ip': subnet.gateway_ip,
                'ip_version': subnet.ip_version,
            }
        }
        optional_properties = {}

        allocation_pools = subnet.allocation_pools
        if allocation_pools:
            assert isinstance(allocation_pools, dict)
            optional_properties['allocation_pools'] = allocation_pools

        dns_nameservers = subnet.dns_nameservers
        if dns_nameservers:
            assert isinstance(dns_nameservers, list)
            optional_properties['dns_nameservers'] = dns_nameservers

        host_routes = subnet.host_routes
        if host_routes:
            assert isinstance(dns_nameservers, list)
            optional_properties['host_routes'] = host_routes

        if subnet.ip_version == 6:
            ipv6_address_mode = subnet.ipv6_address_mode
            if ipv6_address_mode:
                optional_properties['ipv6_address_mode'] = ipv6_address_mode

            ipv6_ra_mode = subnet.ipv6_ra_mode
            if ipv6_ra_mode:
                assert isinstance(dns_nameservers, str)
                optional_properties['ipv6_ra_mode'] = ipv6_ra_mode

        prefix_len = subnet.prefix_len
        if prefix_len:
            assert isinstance(dns_nameservers, str)
            optional_properties['prefixlen'] = prefix_len

        segment = subnet.segment
        if segment:
            assert isinstance(dns_nameservers, str)
            optional_properties['segment'] = segment

        tags = subnet.tags
        if tags:
            assert isinstance(tags, list)
            optional_properties['tags'] = tags

        tenant_id = subnet.tenand_id
        if tenant_id:
            optional_properties['tenant_id'] = tenant_id

        value_specs = subnet.value_specs
        if value_specs:
            assert isinstance(value_specs, collections.Mapping)
            optional_properties['value_specs'] = value_specs

        self.resources[name]['properties'].update(optional_properties)

        self._template['outputs'][name] = {
            'description': 'subnet %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + "-cidr"] = {
            'description': 'subnet %s cidr' % name,
            'value': {'get_attr': [name, 'cidr']}
        }
        self._template['outputs'][name + "-gateway_ip"] = {
            'description': 'subnet %s gateway_ip' % name,
            'value': {'get_attr': [name, 'gateway_ip']}
        }
        self._template['outputs'][name + "-ip_version"] = {
            'description': 'subnet %s ip_version' % name,
            'value': {'get_attr': [name, 'ip_version']}
        }
        self._template['outputs'][name + "-network_id"] = {
            'description': 'subnet %s network_id' % name,
            'value': {'get_attr': [name, 'network_id']}
        }

    @valid_kwargs('admin_state_up', 'distributed', 'ha', 'l3_agent_ids',
                  'tags', 'value_specs')
    def add_router(self, name, external_gateway_info, subnet_name, **kwargs):
        """
        Add to the template a Neutron Router and interface
        Usage:

        :param name:
        :param external_gateway_info: {'net'}
        :param subnet_name:
        :param kwargs:
        :return:
        """
        if name:
            name = 'auto_router'

        assert isinstance(external_gateway_info, list)
        if 'network' not in external_gateway_info:
            raise TypeError('external_gateway_info must contain network')

        self.resources[name] = {
            'type': 'OS::Neutron::Router',
            'depends_on': [subnet_name],
            'properties': {
                'name': name,
                'admin_state_up': kwargs.get('admin_state_up') or True,
                'external_gateway_info': external_gateway_info,
                'ha': kwargs.get('ha') or False,
            }
        }

        optional_properties = {}
        external_fixed_ips = kwargs.get('external_fixed_ips')
        if external_fixed_ips:
            assert isinstance(external_fixed_ips, collections.Mapping)
            optional_properties['external_fixed_ips'] = external_fixed_ips

        l3_agent_ids = kwargs.get('l3_agent_ids')
        if l3_agent_ids:
            assert isinstance(l3_agent_ids, collections.Mapping)
            optional_properties['tags'] = l3_agent_ids

        tags = kwargs.get('tags')
        if tags:
            assert isinstance(tags, list)
            optional_properties['value_specs'] = tags

        value_specs = kwargs.get('value_specs')
        if value_specs:
            assert isinstance(value_specs, collections.Mapping)
            optional_properties['value_specs'] = value_specs

        self.resources[name]['properties'].update(optional_properties)

        self._template['outputs'][name] = {
            'description': 'router %s ID' % name,
            'value': {'get_resource': name}
        }

    def add_router(self, subnet_name, router):
        """
        Add to the template a Neutron Router and interface
        Usage:

        :param subnet_name:
        :param router: model.Router object
        :return:
        """
        name = router.stack_name
        external_gateway_info = router.external_gateway_info

        self.resources[name] = {
            'type': 'OS::Neutron::Router',
            'depends_on': [subnet_name],
            'properties': {
                'name': name,
                'admin_state_up': router.admin_state_up or True,
                'external_gateway_info': external_gateway_info,
                'ha': router.ha or False,
            }
        }

        optional_properties = {}
        external_fixed_ips = router.external_fixed_ips
        if external_fixed_ips:
            assert isinstance(external_fixed_ips, collections.Mapping)
            optional_properties['external_fixed_ips'] = external_fixed_ips

        l3_agent_ids = router.l3_agent_ids
        if l3_agent_ids:
            assert isinstance(l3_agent_ids, collections.Mapping)
            optional_properties['tags'] = l3_agent_ids

        tags = router.tags
        if tags:
            assert isinstance(tags, list)
            optional_properties['value_specs'] = tags

        value_specs =router.value_specs
        if value_specs:
            assert isinstance(value_specs, collections.Mapping)
            optional_properties['value_specs'] = value_specs

        self.resources[name]['properties'].update(optional_properties)

        self._template['outputs'][name] = {
            'description': 'router %s ID' % name,
            'value': {'get_resource': name}
        }

    @valid_kwargs('port', 'subnet')
    def add_router_interface(self, name, router, **kwargs):
        """
        Add to the template a Neutron RouterInterface and interface
        :param name: (required)
        :param router: (required)
        :param kwargs: (optional)
        :return:
        """

        self.resources[name] = {
            'type': 'OS::Neutron::RouterInterface',
            'depends_on': [router],
            'properties': {
                'router': {'get_resource': router},
                'subnet': {'get_resource': kwargs.get('subnet')}
            }
        }

    @valid_kwargs('sec_group_id', 'mac_address', 'propagate_uplink_status',
                  'vnic_type', 'tags', 'value_specs', 'port_security_enabled')
    def add_port(self, name, network, **kwargs):
        """
        Add to the template a named Neutron Port
        Usage:
        add_port(name='port;, network=network, )

        :param name: String (required)
        :param network: model.Network object
        :param kwargs: dict object (optional)
        :return:
        """
        net_is_existing = network.net_flags.get(consts.IS_EXISTING)
        depends_on = [] if net_is_existing else [network.subnet_stack_name]
        fixed_ips = [{'subnet': network.subnet.stack_name}] if net_is_existing else [
            {'subnet': {'get_resource': network.subnet_stack_name}}]
        network_ = network.name if net_is_existing \
            else {'get_resource': network.stack_name}

        self.resources[name] = {
            'type': 'OS::Neutron::Port',
            'depends_on': depends_on,
            'properties': {
                'name': name,
                'admin_state_up': network.admin_state_up,
                'fixed_ips': fixed_ips,
                'network': network_,
                'port_security_enabled': kwargs.get('port_security_enabled') or False,
            }
        }

        optional_properties = {}

        if network.allowed_address_pairs:
            optional_properties['optional_properties'] = network.allowed_address_pairs

        sec_group_id = kwargs.get('sec_group_id')
        if sec_group_id:
            self.resources[name]['depends_on'].append(sec_group_id)
            optional_properties['security_groups'] = [sec_group_id]

        allowed_address_pairs = kwargs.get('allowed_address_pairs')
        if allowed_address_pairs:
            assert isinstance(allowed_address_pairs, list)
            optional_properties['allowed_address_pairs'] = allowed_address_pairs

        vnic_type = kwargs.get('allowed_address_pairs', 'normal')
        optional_properties['binding:vnic_type'] = vnic_type

        qos_policy = network.qos_policy
        if qos_policy:
            depends_on.append(qos_policy('stack_name'))
            optional_properties['qos_policy'] = {
                'get_resource': qos_policy('stack_name'),
            }

        mac_address = kwargs.get('mac_address')
        if mac_address:
            assert isinstance(mac_address, str)
            allowed_address_pairs['mac_address'] = mac_address

        tags = kwargs.get('tags')
        if tags:
            assert isinstance(tags, collections.Mapping)
            optional_properties['tags'] = tags

        value_specs = kwargs.get('value_specs')
        if value_specs:
            assert isinstance(value_specs, list)
            optional_properties['value_specs'] = value_specs

        self.resources[name]['properties'].update(optional_properties)

        self._template['outputs'][name] = {
            'description': 'Port UUID',
            'value': {'get_resource': name}
        }

        self._template['outputs'][str_util.h_join(name, 'ip_address')] = {
            'description': 'Address for interface %s' % name,
            'value': {'get_attr': [name, 'fixed_ips', 0, 'ip_address']}
        }

        self._template['outputs'][str_util.h_join(name, 'subnet_id')] = {
            'description': 'Address for interface %s' % name,
            'value': {'get_attr': [name, 'fixed_ips', 0, 'subnet_id']}
        }

        self._template['outputs'][str_util.h_join(name, 'mac_address')] = {
            'description': 'MAC Address for interface %s' % name,
            'value': {'get_attr': [name, 'mac_address']}
        }
        str_util.h_join(name, 'device_id')
        self._template['outputs'][str_util.h_join(name, 'device_id')] = {
            'description': 'Device ID for interface %s' % name,
            'value': {'get_attr': [name, 'device_id']}
        }
        self._template['outputs'][str_util.h_join(name, 'network_id')] = {
            'description': 'Network ID for interface %s' % name,
            'value': {'get_attr': [name, 'network_id']}
        }
        self._template['outputs'][str_util.h_join(name, 'qos_policy_id')] = {
            'description': 'Policy ID for interface %s' % name,
            'value': {'get_attr': [name, 'qos_policy_id']}
        }

    @valid_kwargs('')
    def add_neutron_floating_ip(self, name, floating_network, port_name, secgroup_name):
        """
        Add to the template a Nova FloatingIP resource
        :param name:
        :param floating_network:
        :param port_name:
        :param secgroup_name:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Neutron::FloatingIP',
            'depends_on': [port_name],
            'properties': {
                'floating_network': floating_network,
            }
        }

        if secgroup_name:
            self.resources[name]["depends_on"].append(secgroup_name)

        self._template['outputs'][name] = {
            'description': 'floating ip %s' % name,
            'value': {'get_attr': [name, 'ip']}
        }

    def add_nova_floating_ip(self, name, floating_network, port_name,
                             router_if_name, secgroup_name=None):
        """
        Add to the template a Nova FloatingIP resource
        Refer: https://docs.openstack.org/heat/latest/template_guide/basic_resources.html
        :param name:
        :param floating_network:
        :param port_name:
        :param router_if_name:
        :param secgroup_name:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Nova::FloatingIP',
            'depends_on': [port_name, router_if_name],
            'properties': {
                'pool': floating_network,
            }
        }

        if secgroup_name:
            self.resources[name]["depends_on"].append(secgroup_name)

        self._template['outputs'][name] = {
            'description': 'floating ip %s' % name,
            'value': {'get_attr': [name, 'ip']}
        }

    def add_floating_ip_association(self, name, floating_ip_name, port_name):
        """
        Add to the template a Nova FloatingIP Association resource
        :param name:
        :param floating_ip_name:
        :param port_name:
        :return:
        """

        self.resources[name] = {
            'type': 'OS::Neutron::FloatingIPAssociation',
            'depends_on': [port_name],
            'properties': {
                'floatingip_id': {'get_resource': floating_ip_name},
                'port_id': {'get_resource': port_name}
            }
        }

    def add_keypair(self, keypair):
        """
        Add to the template a Nova KeyPair
        Refer: https://docs.openstack.org/heat/latest/template_guide/openstack.html#OS::Nova::KeyPair
        :param keypair:
        :return:
        """
        properties = {
            'name': keypair.name,
            'public_key': keypair.public_key.encode(),
            'save_private_key': keypair.save_private_key,
            # 'type': keypair.key_type,
        }
        if keypair.user:
            properties.update({'user': keypair.user})

        self.resources[keypair.stack_name] = {
            'type': 'OS::Nova::KeyPair',
            'properties': properties,
        }

    def add_servergroup(self, name, policies):
        """
        Add to the template a Nova ServerGroup
        :param name:
        :param policies:
        :return:
        """
        if policies:
            assert isinstance(policies, list)

        self.resources[name] = {
            'type': 'OS::Nova::ServerGroup',
            'properties': {
                'name': name,
                'policies': policies or ['anti-affinity'],
            }
        }

        self._template['outputs'][name] = {
            'description': 'ID Server Group %s' % name,
            'value': {'get_resource': name}
        }

    def add_security_group(self, name, stack_name, description=None, rules=None):
        """
        Add to the template a Neutron SecurityGroup
        :param name:
        :param stack_name
        :param description
        :param rules
        :return:
        """
        if rules:
            assert isinstance(rules, list)

        stack_name = str_util.h_join(stack_name, name)
        self.resources[stack_name] = {
            'type': 'OS::Neutron::SecurityGroup',
            'properties': {
                'name': name,
                'description': description,
                'rules': rules,
            }
        }

        self._template['outputs'][stack_name] = {
            'description': 'ID of Security Group',
            'value': {'get_resource': stack_name}
        }

    def add_security_group_rules(self, name, rules):
        """
        Add to the template a Neutron SecurityGroup

        :param name
        :param rules:
        :return:
        """
        properties = self.resources[name]['properties']
        properties['rules'].append(rules)
        self.resources[name]['properties'] = properties

    def remove_security_group_rule(self, name, rule):
        """
        Add to the template a Neutron SecurityGroup

        :param name
        :param rule:
        :return:
        """
        properties = self.resources[name]['properties']
        properties['rules'].remove(rule)
        self.resources[name]['properties'] = properties

    def add_ssh_key(self, name, ssh_key):
        """

        :return:
        """
        self.resources[name] = {
            'type': 'OS::Heat::CloudConfig',
            'depends_on': [],
        }
        properties = {
            'cloud_config': {
                'manage_etc_hosts': True,
                'users': {
                    'name': 'syseleven',
                    'gecos': 'syseleven Stack user',
                    'sudo': 'ALL=(ALL) NOPASSWD:ALL',
                    'shell': '/bin/bash',
                    'lock-passwd': False,
                    'ssh-authorized-keys': ssh_key,
                }
            }
        }
        self.resources[name]['properties'] = properties

    def add_user_password(self, name, username, password):
        """
        Add username and password
        :param name:
        :param username:
        :param password:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Heat::CloudConfig',
            'depends_on': [],
        }
        pass_info = 'root:{}\n{}:{}\n'.format(password, username, password)
        properties = {
            'cloud_config': {
                'users': [
                    "default",
                    {
                        'name': username,
                        'gecos': username,
                        'sudo': ["ALL=(ALL) NOPASSWD:ALL"],
                        "groups": "wheel,adm,systemd-journal",
                        'lock_passwd': False,
                    }
                ],
                "disable_root": False,
                "ssh_pwauth": True,
                "ssh_deletekeys": False,
                "chpasswd": {
                    "list": pass_info,
                    "expire": False
                }
            }
        }
        self.resources[name]['properties'] = properties

    @valid_kwargs('block_device_mapping_v2', 'config_drive',
                  'deployment_swift_data', 'diskConfig', 'flavor_update_policy',
                  'image_update_policy', 'reservation_id','software_config_transport')
    def add_server(self, stack_name, name, image, flavor, flavors, ports=None, networks=None,
                   username=None, password=None, scheduler_hints=None, admin_user=None, keypair=None,
                   user_data=None, metadata=None, additional_properties=None,
                   availability_zone=None, block_device_mapping=None, tags=None, **kwargs):
        """
        Add to the template a Nova Server
        :param stack_name:
        :param name:
        :param image:
        :param flavor:
        :param flavors:
        :param ports:
        :param networks:
        :param username:
        :param password:
        :param scheduler_hints:
        :param admin_user:
        :param keypair:
        :param user_data:
        :param metadata:
        :param additional_properties:
        :param block_device_mapping:
        :param availability_zone:
        :param tags:
        :param kwargs:
        :return:
        """
        self.resources[stack_name] = {
            'type': 'OS::Nova::Server',
            'depends_on': []
        }
        server_properties = {
            'name': name,
            'user_data_format': 'RAW',
            'user_data': None,
            'image': image,
            'flavor': flavor,
            'networks': [],
            'block_device_mapping': {}
        }

        if availability_zone:
            assert isinstance(availability_zone, str)
            server_properties["availability_zone"] = availability_zone

        # if flavor in flavors:
        #     self.resources[stack_name]['depends_on'].append(flavor)
        #     server_properties["flavor"] = {'get_resource': flavor}
        # else:
        #     server_properties["flavor"] = flavor

        if networks:
            for i, _ in enumerate(networks):
                server_properties['networks'].append({'network': networks[i]})

        if admin_user:
            server_properties['admin_user'] = admin_user

        # Add username password
        ssh_name = '{}-cloud-config'.format(stack_name)
        if username and password:
            self.add_user_password(name=ssh_name, username=username, password=password)
            server_properties['user_data'] = {'get_resource': ssh_name}
            self.resources[stack_name]['depends_on'].append(ssh_name)

        if keypair:
            if keypair.is_existing:
                server_properties['key_name'] = keypair.name
            else:
                self.resources[stack_name]['depends_on'].append(keypair.stack_name)
                server_properties['key_name'] = {'get_resource': keypair.stack_name}

        if ports:
            self.resources[stack_name]['depends_on'].extend(ports)
            for port in ports:
                server_properties['networks'].append(
                    {'port': {'get_resource': port}}
                )

        if scheduler_hints:
            server_properties['scheduler_hints'] = scheduler_hints

        if user_data:
            server_properties['user_data'] = user_data

        if metadata:
            assert isinstance(metadata, dict)
            server_properties['metadata'] = metadata

        if additional_properties:
            assert isinstance(additional_properties, dict)
            for prop in additional_properties:
                server_properties[prop] = additional_properties[prop]

        server_properties['config_drive'] = kwargs.get('config_drive') or True

        if block_device_mapping:
            assert isinstance(block_device_mapping, list)
            server_properties['block_device_mapping'] = block_device_mapping

        self.resources[stack_name]['properties'] = server_properties

        self._template['outputs'][stack_name] = {
            'description': 'VM UUID',
            'value': {'get_resource': stack_name},
        }
        name_ = str_util.h_join(stack_name, 'console')
        self._template['outputs'][name_] = {
            'description': 'Server console',
            'value': {'get_attr': [stack_name, 'console_urls', 'novnc']},
        }
