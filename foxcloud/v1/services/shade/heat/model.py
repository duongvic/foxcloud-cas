#
# Copyright (c) 2020 FTI-CAS
#

from __future__ import absolute_import

import six
import logging

from foxcloud.v1.utils import errors, constants as consts
from foxcloud.v1.utils import str_util


class Object(object):
    """
    Base class for classes in the logical model
    Contains common attributes and methods
    """

    def __init__(self, name, context):
        self.name = name
        self._context = context
        self.flags = None
        # stack identities
        self.stack_name = None
        self.stack_id = None

    @property
    def dn(self):
        """
        Returns distinguished name for object
        """
        return self.name + "." + self._context.name


class PlacementGroup(Object):
    map = {}

    def __init__(self, name, context, policy):
        super().__init__(name=name, context=context)
        if policy not in ["affinity", "availability"]:
            raise ValueError("placement group '%s', policy '%s' is not valid" %
                             (name, policy))
        self.members = set()
        self.stack_name = context.name + "-" + name
        self.policy = policy
        PlacementGroup.map[name] = self

    def add_member(self, name):
        self.members.add(name)

    @staticmethod
    def get(name):
        return PlacementGroup.map.get(name)


class ServerGroup(Object):
    """
    Class that represents a server group in the logical model
    Policy should be one of "anti-affinity" or "affinity" or
    "soft-anti-affinity" and "soft-affinity"
    """
    map = {}

    def __init__(self, name, context, policy):
        super().__init__(name=name, context=context)
        if policy not in {"affinity", "anti-affinity", "soft-anti-affinity", "soft-affinity"}:
            raise ValueError("server group '%s', policy '%s' is not valid" % (name, policy))
        self.members = set()
        self.stack_name = context.name + "-" + name
        self.policy = policy
        ServerGroup.map[name] = self

    def add_member(self, name):
        self.members.add(name)

    @staticmethod
    def get(name):
        return ServerGroup.map.get(name)


class Router(Object):
    """
    Class that represents a router in the logical model
    """

    def __init__(self, name, network_name, context, attrs):
        super().__init__(name=name, context=context)
        self.stack_name = '{}-{}-{}'.format(context.name, network_name, self.name)
        self.stack_if_name = self.stack_name + "-if0"
        self.external_gateway_info = attrs.get('external_gateway_info')
        self.admin_state_up = attrs.get('admin_state_up') or True
        self.ha = attrs.get('ha') or True
        self.l3_agent_ids = attrs.get('l3_agent_ids')
        self.tags = attrs.get('tags')
        self.value_specs = attrs.get('value_specs')


class Subnet(Object):
    """
    Class that represents a subnet in the logical model
    """

    def __init__(self, name, network_name, context):
        super().__init__(name=name, context=context)
        self.stack_name = '{}-{}-{}'.format(context.name, network_name, self.name)
        self.cidr = None
        self.allocation_pools = None
        self.dns_nameservers = None
        self.enable_dhcp = True
        self.gateway_ip = 'null'  # [ null | ~ | “” ]
        self.host_routes = None
        self.ip_version = 4  # Default IPv4
        self.ipv6_address_mode = 'dhcpv6-stateful'  # ["dhcpv6-stateful", "dhcpv6-stateless", "slaac"]
        self.ipv6_ra_mode = 'dhcpv6-stateful'  # ["dhcpv6-stateful", "dhcpv6-stateless", "slaac"]
        self.prefix_len = None
        self.segment = None
        self.subnet_pool = None
        self.tags = []
        self.project_id = None
        self.value_specs = []

    def parse_attr(self, attrs):
        self.cidr = attrs.get('cidr') or "10.0.0.0/24"
        self.allocation_pools = attrs.get('allocation_pools')
        self.dns_nameservers = attrs.get('dns_nameservers')
        self.enable_dhcp = attrs.get('enable_dhcp') or True
        self.gateway_ip = attrs.get('gateway_ip', 'null')  # [ null | ~ | “” ]
        self.host_routes = attrs.get('host_routes')
        self.ip_version = attrs.get('ip_version') or 4
        self.ipv6_address_mode = attrs.get('ipv6_address_mode')  # ["dhcpv6-stateful", "dhcpv6-stateless", "slaac"]
        self.ipv6_ra_mode = attrs.get('ipv6_ra_mode')  # ["dhcpv6-stateful", "dhcpv6-stateless", "slaac"]
        self.prefix_len = attrs.get('prefix_len')
        self.segment = attrs.get('segment')
        self.subnet_pool = attrs.get('subnet_pool')
        self.tags = attrs.get('tags')
        self.project_id = attrs.get('project_id')
        self.value_specs = attrs.get('value_specs')

    def set_stack_name(self, stack_name):
        self.stack_name = stack_name


class Network(Object):
    """
    Class that represents a network in the logical model
    """
    list = []

    def __init__(self, name, context, attrs):
        super().__init__(name=name, context=context)
        self.stack_name = '{}={}'.format(context.name, self.name)
        self.admin_state_up = attrs.get('admin_state_up', True)
        self.dhcp_agent_ids = attrs.get('dhcp_agent_ids')
        self.dns_domain = attrs.get('dns_domain')
        self.port_security_enabled = attrs.get('port_security_enabled')
        self.allowed_address_pairs = attrs.get('allowed_address_pairs')
        self.qos_policy = attrs.get('qos_policy')
        self.shared = attrs.get('shared', False)
        self.tags = attrs.get('tags')
        self.tenant_id = attrs.get('tenant_id') or 'null'
        self.value_specs = attrs.get('value_specs')
        self.net_flags = attrs.get('net_flags', {})

        self.router = None
        self.subnet = None

        self.physical_network = attrs.get('physical_network', 'default_physic_net')
        self.provider = attrs.get('provider')
        self.segmentation_id = attrs.get('segmentation_id')
        self.network_type = attrs.get('network_type')

        if self.is_existing:
            # Override network stack name if the network was created
            self.stack_name = self.name
            subnet_info = attrs.get('subnet')
            if not subnet_info or not isinstance(subnet_info, str):
                raise Warning(errors.NO_EXISTING_SUBNET)
            try:
                # Load subnet if subnet was created
                self.subnet = Subnet(name=subnet_info, network_name=self.name, context=self)
                self.subnet.set_stack_name(stack_name=subnet_info)
            except Exception as e:
                raise Warning(errors.NO_EXISTING_SUBNET)
        else:
            if "external_network" in attrs:
                router_attrs = {
                    'admin_state_up': self.admin_state_up,
                    'external_gateway_info': {
                        'network': attrs["external_network"],
                    }
                }
                self.router = Router(name='router', network_name=self.name, context=self, attrs=router_attrs)
            self.subnet = Subnet(name='subnet', network_name=self.name, context=self)
            self.subnet.parse_attr(attrs=attrs)
            Network.list.append(self)

    @property
    def is_public(self):
        """
        Check public network
        :return:
        """
        net_is_public = self.net_flags.get(consts.IS_PUBLIC)
        if net_is_public and not isinstance(net_is_public, bool):
            raise SyntaxError('Network flags should be bool type!')
        return net_is_public

    @property
    def is_existing(self):
        """
        Check resource exists
        :return:
        """
        if not self.net_flags:
            return True
        net_is_existing = self.net_flags.get(consts.IS_EXISTING)
        if net_is_existing and not isinstance(net_is_existing, bool):
            raise SyntaxError('Network flag should be bool type!')
        return net_is_existing

    def has_route_to(self, network_name):
        """determines if this network has a route to the named network"""
        if self.router and self.router.external_gateway_info == network_name:
            return True
        return False

    @staticmethod
    def find_by_route_to(external_network):
        """
        Finds a network that has a route to the specified network
        :param external_network:
        :return:
        """
        for network in Network.list:
            if network.has_route_to(external_network):
                return network

    @staticmethod
    def find_external_network():
        """
        Return the name of an external network some network in this
        context has a route to
        """
        for network in Network.list:
            if network.router:
                return network.router.external_gateway_info['network']
        return None


class SecurityGroup(Object):
    """
    Class that represents a security group in the logical model
    """

    list = []

    def __init__(self, name, context, attrs):
        super().__init__(name=name, context=context)
        self.stack_name = context.name + "-" + self.name
        self.rules = attrs.get('rules', list())
        self.description = attrs.get('description')
        self.flags = attrs.get('flags')

        if not self.is_existing():
            SecurityGroup.list.append(self)

    def is_existing(self):
        """

        :return:
        """


class KeyPair(Object):
    list = []

    def __init__(self, name, context, attrs):
        super().__init__(name=name, context=context)
        self.name = name
        self.public_key = attrs.get('public_key')
        self.save_private_key = attrs.get('save_private_key', False)
        self.key_type = attrs.get('key_type') or 'ssh'
        self.user = attrs.get('user', None)
        self.key_flags = attrs.get('key_flags', {}) or {}
        if self.is_existing:
            self.stack_name = attrs.get('name')
        else:
            self.stack_name = '{}-keypair-{}'.format(context.name, self.name)

    def add_public_key(self, public_key):
        self.public_key = public_key

    @property
    def is_existing(self):
        """
        Check resource exists
        :return:
        """
        key_is_existing = self.key_flags.get(consts.IS_EXISTING)
        if key_is_existing and not isinstance(key_is_existing, bool):
            raise SyntaxError('Keypair flag should be bool type!')
        return key_is_existing


class QoSPolicyType(object):
    QoSBandwidthLimitRule = 'QoSBandwidthLimitRule'
    QoSDscpMarkingRule = 'QoSDscpMarkingRule'
    QoSMinimumBandwidthRule = 'QoSMinimumBandwidthRule'
    QoSPolicy = 'QoSPolicy'


class Server(Object):
    """
    Class that represents a server in the logical model
    """
    list = []

    def __init__(self, name, context, attrs):
        super().__init__(name=name, context=context)
        self.stack_name = context.name
        self.name = name
        self.keypair = context.keypair
        self.sec_group_name = context.sec_group_name
        self.user = context.user
        self.context = context
        self.private_ip = None
        self.user_data = ''
        self.interfaces = {}
        self.username = None
        self.password = None

        if attrs is None:
            attrs = {}

        self.placement_groups = []
        placement = attrs.get("placement", [])
        placement = placement if isinstance(placement, list) else [placement]
        for p in placement:
            pg = PlacementGroup.get(p)
            if not pg:
                raise ValueError("server '%s', placement '%s' is invalid" %
                                 (name, p))
            self.placement_groups.append(pg)
            pg.add_member(self.stack_name)

        self.volumes = attrs.get("volumes") or []

        # support server group attr
        self.server_group = None
        sg = attrs.get("server_group")
        if sg:
            server_group = ServerGroup.get(sg)
            # if not server_group:
            #     raise ValueError("server '%s', server_group '%s' is invalid" %
            #                      (name, sg))
            if server_group:
                self.server_group = server_group
                server_group.add_member(self.stack_name)
            else:
                self.server_group = sg

        self.instances = 1
        if "instances" in attrs:
            self.instances = attrs["instances"]

        # dict with key network name, each item is a dict with port name and ip
        self.network_ports = attrs.get("network_ports", {})
        self.ports = {}

        self.floating_ip = None
        self.floating_ip_assoc = None
        if "floating_ip" in attrs:
            self.floating_ip = {}
            self.floating_ip_assoc = {}

        if self.floating_ip is not None:
            ext_net = Network.find_external_network()
            if ext_net:
                self.floating_ip["external_network"] = ext_net

        self._image = attrs.get("image")
        self._flavor = attrs.get("flavor")

        self.public_key = attrs.get("public_key")

        self.user_data = attrs.get('user_data', '')
        self.username = attrs.get('username', None)
        self.password = attrs.get('password', None)
        self.availability_zone = attrs.get('availability_zone')
        self.tags = attrs.get('tags') or []

        Server.list.append(self)

    def override_ip(self, network_name, port):
        """
        Override IP address
        :param network_name:
        :param port:
        :return:
        """

        def find_port_overrides():
            for p in ports:
                # p can be string or dict
                # we can't just use p[port['port'] in case p is a string
                # and port['port'] is an int?
                if isinstance(p, dict):
                    g = p.get(port['port'])
                    # filter out empty dicts
                    if g:
                        yield g

        ports = self.network_ports.get(network_name, [])
        intf = self.interfaces[port['port']]
        for override in find_port_overrides():
            intf['local_ip'] = override.get('local_ip', intf['local_ip'])
            intf['netmask'] = override.get('netmask', intf['netmask'])
            # only use the first value
            break

    @property
    def image(self):
        """
        Returns a server's image name
        :return:
        """
        if self._image:
            return self._image
        else:
            return self._context.image

    @property
    def flavor(self):
        """
        Returns a server's flavor name
        :return:
        """
        if self._flavor:
            return self._flavor
        else:
            return self._context.flavor

    def _add_instance(self, template, stack_name, server_name, networks, scheduler_hints):
        """
        Adds to the template one server and corresponding resources

        :param template:
        :param stack_name:
        :param server_name:
        :param networks:
        :param scheduler_hints:
        :return:
        """
        port_name_list = []
        for network in networks:
            # if explicit mapping skip unused networks
            if self.network_ports:
                try:
                    ports = self.network_ports[network.name]
                except KeyError:
                    # no port for this network
                    continue
                else:
                    if isinstance(ports, six.string_types):
                        # because strings are iterable we have to check specifically
                        raise SyntaxError("network_port must be a list '{}'".format(ports))
                    # convert port subdicts into their just port name
                    ports = [next(iter(p)) if isinstance(p, dict) else p for p in ports]
            # otherwise add a port for every network with port name as network name
            else:
                ports = [network.name]

            net_flags = network.net_flags
            for port in ports:
                port_name = "{0}-{1}-port".format(stack_name, port)
                port_info = {"stack_name": port_name, "port": port}
                if net_flags:
                    port_info['net_flags'] = net_flags
                self.ports.setdefault(network.name, []).append(port_info)
                # we can't use security groups if port_security_enabled is False
                if network.port_security_enabled is False:
                    sec_group_id = None
                else:
                    # if port_security_enabled is None we still need to add to security group
                    sec_group_id = self.sec_group_name
                # circular ref encode errors

                other_options = {
                    'port_security_enabled': network.port_security_enabled,
                    'sec_group_id': sec_group_id,
                }
                template.add_port(port_name, network, **other_options)
                if network.is_public:
                    port_name_list.insert(0, port_name)
                else:
                    port_name_list.append(port_name)

                if self.floating_ip:
                    # TODO need verify if supporting this case
                    external_network = self.floating_ip["external_network"]
                    if network.has_route_to(external_network):
                        self.floating_ip["stack_name"] = stack_name + "-fip"
                        template.add_nova_floating_ip(self.floating_ip["stack_name"], external_network,
                                                      port_name, network.router.stack_if_name, sec_group_id)
                        self.floating_ip_assoc["stack_name"] = \
                            stack_name + "-fip-assoc"
                        template.add_floating_ip_association(
                            self.floating_ip_assoc["stack_name"],
                            self.floating_ip["stack_name"],
                            port_name)
        if self.flavor:
            if isinstance(self.flavor, dict):
                self.flavor["name"] = \
                    self.flavor.setdefault("name", self.stack_name + "-flavor")
                template.add_flavor(**self.flavor)
                self.flavor_name = self.flavor["name"]
            else:
                self.flavor_name = self.flavor

        # Add volume
        block_device_mapping = []

        def _is_volume_existing(vol):
            vol_flags = vol.get('vol_flags')
            if vol_flags:
                return vol_flags.get(consts.IS_EXISTING, False)
            else:
                return False

        for index, volume in enumerate(self.volumes):
            if _is_volume_existing(volume):
                is_boot = volume.get('is_boot', False)
                mount_point = volume.get('mount_point', None)
                vol = {
                    'uuid': volume['uuid'],
                }
                if is_boot:
                    block_device_mapping.append({
                        'delete_on_termination': False,
                        'device_name': 'vda',
                        'volume_id': volume['uuid']
                    })
                else:
                    name = volume.get('name', 'volume{}-attachment'.
                                      format(index)) or 'volume-{}'.format(index)
                    template.add_volume_attachment(name=name, server_name=stack_name,
                                                   volume=vol, mount_point=mount_point)
            else:
                vol_size = volume.get('size', 0)
                if not vol_size:
                    continue

                is_boot = volume.get('is_boot', False)
                if is_boot:
                    # Checking image mounted
                    volume['image'] = volume.setdefault('image', self._image)

                vol_name = volume.get('name', 'volume-{}'.format(index)) or 'volume-{}'.format(index)

                kwargs = {
                    'availability_zone': volume.get('availability_zone') or self.availability_zone,
                    'snapshot_id': volume.get('snapshot_id'),
                    'backup_id': volume.get('backup_id'),
                    'image': volume.get('image', None),
                    'metadata': volume.get('metadata', {}),
                    'multi_attach': volume.get('multi_attach', False),
                    'read_only': volume.get('read_only', False),
                    'scheduler_hints': volume.get('scheduler_hints'),
                    'source_vol_id': volume.get('source_vol_id'),
                    'volume_type': volume.get('volume_type'),
                }
                template.add_volume(name=vol_name, stack_name=stack_name, size=vol_size,
                                    description=volume.get('description'), **kwargs)
                if is_boot:
                    block_device_mapping.append({
                        'delete_on_termination': False,
                        'device_name': 'vda',
                        'volume_id': {
                            'get_resource': str_util.h_join(stack_name, vol_name)
                        },
                    })
                else:
                    name = volume.get('name', 'volume{}-attachment'.
                                      format(index)) or 'volume-{}'.format(index)
                    mount_point = volume.get('mount_point', None)
                    vol = {
                        'name': vol_name
                    }
                    template.add_volume_attachment(name=name, server_name=stack_name,
                                                   volume=vol, mount_point=mount_point)

        template.add_server(stack_name, server_name, self.image, flavor=self.flavor_name,
                            flavors=self.context.flavors, ports=port_name_list,
                            username=self.username, password=self.password, scheduler_hints=scheduler_hints,
                            admin_user=self.user, keypair=self.keypair, user_data=self.user_data,
                            availability_zone=self.availability_zone, block_device_mapping=block_device_mapping,
                            tags=self.tags)

    def add_to_template(self, template, networks, scheduler_hints=None):
        """
        Adds to the template one or more servers (instances)
        :param template:
        :param networks:
        :param scheduler_hints:
        :return:
        """
        if self.instances == 1:
            self._add_instance(template, self.stack_name, self.name, networks,
                               scheduler_hints=scheduler_hints)
        else:
            for i in range(self.instances):
                stack_name_ = "%s-%d" % (self.stack_name, i)
                server_name = "%s-%d" % (self.name, i)
                self._add_instance(template, stack_name_, server_name,
                                   networks, scheduler_hints=scheduler_hints)


def update_scheduler_hints(scheduler_hints, added_servers, placement_group):
    """
    update scheduler hints from server's placement configuration
    TODO: this code is openstack specific and should move somewhere else
    """
    if placement_group.policy == "affinity":
        if "same_host" in scheduler_hints:
            host_list = scheduler_hints["same_host"]
        else:
            host_list = scheduler_hints["same_host"] = []
    else:
        if "different_host" in scheduler_hints:
            host_list = scheduler_hints["different_host"]
        else:
            host_list = scheduler_hints["different_host"] = []

    for name in added_servers:
        if name in placement_group.members:
            host_list.append({'get_resource': name})
