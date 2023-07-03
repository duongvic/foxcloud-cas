from neutronclient.v2_0 import client
from foxcloud import exceptions as fox_exc

from foxcloud.v1.utils import net_util


class Network(client.Client):
    __engine_type__ = 'console'

    def __init__(self, session):
        super(Network, self).__init__(session=session)

    def create_neutron_network(self, name, shared=False, admin_state_up=True,
                               external=False, provider=None, project_id=None,
                               availability_zone_hints=None,
                               port_security_enabled=None,
                               mtu_size=None):
        network = {
            'name': name,
            'admin_state_up': admin_state_up,
        }

        if shared:
            network['shared'] = shared

        if project_id is not None:
            network['tenant_id'] = project_id

        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise fox_exc.FoxCloudException(
                    "Parameter 'availability_zone_hints' must be a list")
            if not self._has_neutron_extension('network_availability_zone'):
                raise fox_exc.FoxCloudException(
                    'network_availability_zone extension is not available on '
                    'target cloud')
            network['availability_zone_hints'] = availability_zone_hints

        if provider:
            if not isinstance(provider, dict):
                raise fox_exc.FoxCloudException(
                    "Parameter 'provider' must be a dict")
            # Only pass what we know
            for attr in ('physical_network', 'network_type',
                         'segmentation_id'):
                if attr in provider:
                    arg = "provider:" + attr
                    network[arg] = provider[attr]

        # Do not send 'router:external' unless it is explicitly
        # set since sending it *might* cause "Forbidden" errors in
        # some situations. It defaults to False in the client, anyway.
        if external:
            network['router:external'] = True

        if port_security_enabled is not None:
            if not isinstance(port_security_enabled, bool):
                raise fox_exc.FoxCloudException(
                    "Parameter 'port_security_enabled' must be a bool")
            network['port_security_enabled'] = port_security_enabled

        if mtu_size:
            if not isinstance(mtu_size, int):
                raise fox_exc.FoxCloudException(
                    "Parameter 'mtu_size' must be an integer.")
            if not mtu_size >= 68:
                raise fox_exc.FoxCloudException(
                    "Parameter 'mtu_size' must be greater than 67.")

            network['mtu'] = mtu_size
        return self.create_network(body={'network': network})

    def _has_neutron_extension(self, extension_alias):
        # return extension_alias in self._neutron_extensions()
        return False

    def update_neutron_network(self, network_id, name, revision_number, shared=False,
                               admin_state_up=True, external=False, provider=None,
                               project_id=None, availability_zone_hints=None,
                               port_security_enabled=None, mtu_size=None):
        network = {
            'name': name,
            'admin_state_up': admin_state_up,
        }

        if shared:
            network['shared'] = shared

        if project_id is not None:
            network['tenant_id'] = project_id

        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise fox_exc.FoxCloudException(
                    "Parameter 'availability_zone_hints' must be a list")
            if not self._has_neutron_extension('network_availability_zone'):
                raise fox_exc.FoxCloudException(
                    'network_availability_zone extension is not available on '
                    'target cloud')
            network['availability_zone_hints'] = availability_zone_hints

        if provider:
            if not isinstance(provider, dict):
                raise fox_exc.FoxCloudException(
                    "Parameter 'provider' must be a dict")
            # Only pass what we know
            for attr in ('physical_network', 'network_type',
                         'segmentation_id'):
                if attr in provider:
                    arg = "provider:" + attr
                    network[arg] = provider[attr]

        # Do not send 'router:external' unless it is explicitly
        # set since sending it *might* cause "Forbidden" errors in
        # some situations. It defaults to False in the client, anyway.
        if external:
            network['router:external'] = True

        if port_security_enabled is not None:
            if not isinstance(port_security_enabled, bool):
                raise fox_exc.FoxCloudException(
                    "Parameter 'port_security_enabled' must be a bool")
            network['port_security_enabled'] = port_security_enabled

        if mtu_size:
            if not isinstance(mtu_size, int):
                raise fox_exc.FoxCloudException(
                    "Parameter 'mtu_size' must be an integer.")
            if not mtu_size >= 68:
                raise fox_exc.FoxCloudException(
                    "Parameter 'mtu_size' must be greater than 67.")

            network['mtu'] = mtu_size
        return self.update_network(network=network_id, body={'network': network},
                                   revision_number=revision_number)

    def create_neutron_subnet(self, network_id, name, cidr=None, ip_version=4,
                              enable_dhcp=False, tenant_id=None, gateway_ip=None,
                              allocation_pools=None, disable_gateway_ip=False,
                              dns=None, host_routes=None, ipv6_ra_mode=None,
                              ipv6_address_mode=None, default_subnet_pool=False):
        filters = {}
        if tenant_id is not None:
            filters = {'tenant_id': tenant_id}

        network = self.show_network(network_id, **filters)
        if not network:
            raise fox_exc.FoxCloudException(
                "Network %s not found." % network_id)
        network = network['network']

        if disable_gateway_ip and gateway_ip:
            raise fox_exc.FoxCloudException(
                'arg:disable_gateway_ip is not allowed with arg:gateway_ip')

        if not cidr and not default_subnet_pool:
            raise fox_exc.FoxCloudException(
                'arg:cidr is required when a subnetpool is not used')

        if cidr and default_subnet_pool:
            raise fox_exc.FoxCloudException(
                'arg:cidr must be set to None when use_default_subnetpool == '
                'True')

        # Be friendly on ip_version and allow strings

        try:
            ip_version = int(ip_version)
            if ip_version not in [4, 6]:
                msg = 'Not support ip version'
                raise fox_exc.FoxCloudException(msg)
        except ValueError:
            raise fox_exc.FoxCloudException(
                'ip_version must be an integer')

        # The body of the neutron message for the subnet we wish to create.
        # This includes attributes that are required or have defaults.
        subnet = {
            'network_id': network['id'],
            'ip_version': ip_version,
            'enable_dhcp': enable_dhcp
        }

        # Add optional attributes to the message.
        if net_util.validate_network(cidr=cidr):
            subnet['cidr'] = cidr
        else:
            msg = "CIDR is required"
            raise fox_exc.FoxCloudException(msg)
        if name:
            subnet['name'] = name
        if tenant_id:
            subnet['tenant_id'] = tenant_id
        if allocation_pools:
            if isinstance(allocation_pools, list):
                for pool in allocation_pools:
                    if not net_util.validate_ip_address(pool['start']) \
                            or not net_util.validate_ip_address(pool['end']):
                        msg = 'Invalid pool ip'
                        raise fox_exc.FoxCloudException(msg)
                subnet['allocation_pools'] = allocation_pools
        if gateway_ip:
            subnet['gateway_ip'] = gateway_ip
        if disable_gateway_ip:
            subnet['gateway_ip'] = None
        if dns:
            subnet['dns_nameservers'] = dns
        if host_routes:
            subnet['host_routes'] = host_routes
        if ipv6_ra_mode:
            subnet['ipv6_ra_mode'] = ipv6_ra_mode
        if ipv6_address_mode:
            subnet['ipv6_address_mode'] = ipv6_address_mode
        if default_subnet_pool:
            subnet['use_default_subnetpool'] = True
        return self.create_subnet(body={"subnet": subnet})

    def update_neutron_subnet(self, subnet_id, name=None, enable_dhcp=None,
                              gateway_ip=None, disable_gateway_ip=None,
                              allocation_pools=None, dns=None,
                              host_routes=None, revision_number=None):
        """Update an existing subnet.
        :param string subnet_id:
           Name or ID of the subnet to update.
        :param string name:
           The new name of the subnet.
        :param bool enable_dhcp:
           Set to ``True`` if DHCP is enabled and ``False`` if disabled.
        :param string gateway_ip:
           The gateway IP address. When you specify both allocation_pools and
           gateway_ip, you must ensure that the gateway IP does not overlap
           with the specified allocation pools.
        :param bool disable_gateway_ip:
           Set to ``True`` if gateway IP address is disabled and ``False`` if
           enabled. It is not allowed with gateway_ip.
           Default is ``False``.
        :param list allocation_pools:
           A list of dictionaries of the start and end addresses for the
           allocation pools. For example::

             [
               {
                 "start": "192.168.199.2",
                 "end": "192.168.199.254"
               }
             ]

        :param list dns_nameservers:
           A list of DNS name servers for the subnet. For example::

             [ "8.8.8.7", "8.8.8.8" ]

        :param list host_routes:
           A list of host route dictionaries for the subnet. For example::

             [
               {
                 "destination": "0.0.0.0/0",
                 "nexthop": "123.456.78.9"
               },
               {
                 "destination": "192.168.0.0/24",
                 "nexthop": "192.168.0.1"
               }
             ]
        :param revision_number
        :returns: The updated subnet object.
        :raises: FoxCloudException on operation error.
        """
        subnet = {}
        if name:
            subnet['name'] = name
        if enable_dhcp is not None:
            subnet['enable_dhcp'] = enable_dhcp
        if gateway_ip:
            subnet['gateway_ip'] = gateway_ip
        if disable_gateway_ip:
            subnet['gateway_ip'] = None
        if allocation_pools:
            subnet['allocation_pools'] = allocation_pools
        if dns:
            subnet['dns_nameservers'] = dns
        if host_routes:
            subnet['host_routes'] = host_routes

        if not subnet:
            return

        if disable_gateway_ip and gateway_ip:
            raise fox_exc.FoxCloudException(
                'arg:disable_gateway_ip is not allowed with arg:gateway_ip')

        curr_subnet = self.show_subnet(subnet_id)
        if not curr_subnet:
            raise fox_exc.FoxCloudException(
                "Subnet %s not found." % subnet_id)
        return self.update_subnet(subnet=subnet_id, body={'subnet': subnet},
                                  revision_number=revision_number)

    def create_sec_group(self, name, description, project_id=None):
        security_group_json = {
            'security_group': {
                'name': name, 'description': description
            }}
        if project_id is not None:
            security_group_json['security_group']['tenant_id'] = project_id
        return self.create_security_group(body=security_group_json)

    def update_sec_group(self, sg_id, revision_number=None, **kwargs):
        group = self.show_security_group(sg_id)
        if group is None:
            raise fox_exc.FoxCloudException(
                "Security group %s not found." % sg_id)
        return self.update_security_group(security_group=sg_id,
                                          revision_number=revision_number,
                                          body={'security_group': kwargs})

    def create_sec_group_rule(self, sg_id, port_range_min=None,
                              port_range_max=None, protocol=None,
                              remote_ip_prefix=None, remote_group_id=None,
                              direction='ingress', ethertype='IPv4',
                              project_id=None):
        """
        Create a new security group rule
        :param sg_id:
        :param port_range_min:
        :param port_range_max:
        :param protocol:
        :param remote_ip_prefix:
        :param remote_group_id:
        :param direction:
        :param ethertype:
        :param project_id:
        :return:
        :raises: OpenStackCloudException on operation error.
        """

        # Security groups not supported

        secgroup = self.show_security_group(sg_id)
        if not secgroup:
            raise fox_exc.FoxCloudException(
                "Security group %s not found." % sg_id)
        secgroup = secgroup['security_group']

        if protocol is None:
            raise fox_exc.FoxCloudException('Protocol must be specified')

        if direction not in ['ingress', 'egress']:
            raise fox_exc.FoxCloudException(
                'No support for type of rules')

        if protocol == 'icmp':
            if port_range_min is None:
                port_range_min = -1
            if port_range_max is None:
                port_range_max = -1
        elif protocol in ['tcp', 'udp']:
            if port_range_min is None and port_range_max is None:
                port_range_min = 1
                port_range_max = 65535

        rule_def = {
            'security_group_id': secgroup['id'],
            'port_range_min':
                None if port_range_min == -1 else port_range_min,
            'port_range_max':
                None if port_range_max == -1 else port_range_max,
            'protocol': protocol,
            'remote_ip_prefix': remote_ip_prefix,
            'remote_group_id': remote_group_id,
            'direction': direction,
            'ethertype': ethertype
        }
        if project_id is not None:
            rule_def['tenant_id'] = project_id

        return self.create_security_group_rule(body={'security_group_rule': rule_def})

    def create_neutron_router(self, name=None, admin_state_up=True,
                              ext_gateway_net_id=None, enable_snat=None,
                              ext_fixed_ips=None, project_id=None,
                              availability_zone_hints=None):
        router = {
            'admin_state_up': admin_state_up
        }
        if project_id is not None:
            router['tenant_id'] = project_id
        if name:
            router['name'] = name
        ext_gw_info = self._build_external_gateway_info(
            ext_gateway_net_id, enable_snat, ext_fixed_ips
        )
        if ext_gw_info:
            router['external_gateway_info'] = ext_gw_info
        if availability_zone_hints is not None:
            if not isinstance(availability_zone_hints, list):
                raise fox_exc.FoxCloudException(
                    "Parameter 'availability_zone_hints' must be a list")
            if not self._has_neutron_extension('router_availability_zone'):
                raise fox_exc.FoxCloudException(
                    'router_availability_zone extension is not available on '
                    'target cloud')
            router['availability_zone_hints'] = availability_zone_hints

        return self.create_router(body={'router': router})

    def _build_external_gateway_info(self, ext_gateway_net_id, enable_snat,
                                     ext_fixed_ips):
        info = {}
        if ext_gateway_net_id:
            info['network_id'] = ext_gateway_net_id
        # Only send enable_snat if it is explicitly set.
        if enable_snat is not None:
            info['enable_snat'] = enable_snat
        if ext_fixed_ips:
            info['external_fixed_ips'] = ext_fixed_ips
        if info:
            return info
        return None

    def update_neutron_router(self, router_id, name=None, admin_state_up=None,
                              ext_gateway_net_id=None, enable_snat=None,
                              ext_fixed_ips=None, routes=None, revision_number=None):
        router = {}
        if name:
            router['name'] = name
        if admin_state_up is not None:
            router['admin_state_up'] = admin_state_up
        ext_gw_info = self._build_external_gateway_info(
            ext_gateway_net_id, enable_snat, ext_fixed_ips
        )
        if ext_gw_info:
            router['external_gateway_info'] = ext_gw_info

        if routes:
            if self._has_neutron_extension('extraroute'):
                router['routes'] = routes

        if not router:
            return

        curr_router = self.show_router(router_id)
        if not curr_router:
            raise fox_exc.FoxCloudException(
                "Router %s not found." % router_id)

        return self.update_router(router=router_id, body={'router': router},
                                  revision_number=revision_number)

    def create_neutron_port(self, network_id, **kwargs):
        kwargs['network_id'] = network_id
        return self.create_port(body=kwargs)

    def update_neutron_port(self, port_id, revision_number=None, **kwargs):
        port = self.show_port(port=port_id)
        if port is None:
            raise fox_exc.FoxCloudException(
                "failed to find port '{port}'".format(port=port_id))

        return self.update_port(port=port_id, body=kwargs, revision_number=revision_number)

    def create_neutron_port_binding(self, port_id, **kwargs):
        """Creates a new port binding."""
        return self.create_port_binding(port_id, body=kwargs)
