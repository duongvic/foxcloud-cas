#
# Copyright (c) 2020 FTI-CAS
#

from __future__ import absolute_import

from collections import OrderedDict
import ipaddress

from foxcloud import exceptions as fox_exc
from foxcloud.i18n import _
from foxcloud.v1.services.shade import base
from foxcloud.v1.services.shade.heat import model as md
from foxcloud.v1.services.shade.heat import orchestrator
from foxcloud.v1.services.stack.contexts import Context
from foxcloud.v1.utils import constants as consts, str_util
from foxcloud.v1.utils import nova_util


class Heat(base.BaseShade):
    __engine_type__ = 'heat'

    def __init__(self, session):
        super().__init__(session)

    def create_server(self, info):
        """
        Subclass should be override this method
        :param info:
        :return:
        """
        heat_context = HeatContext(session=self._session)
        heat_context.init(attrs=info)
        return heat_context.create()

    def update_server(self, info):
        """
        Subclass should be override this method
        :param info:
        :return:
        """
        heat_context = HeatContext(session=self._session)
        heat_context.init(attrs=info)
        return heat_context.update()

    def delete_server(self, server_id):
        """
        Subclass should be override this method
        :param server_id:
        :return:
        """
        info = {
            'stack_id': server_id,
        }
        heat_context = HeatContext(session=self._session)
        heat_context.init(attrs=info)
        return heat_context.delete()


class HeatContext(Context):
    def __init__(self, session=None):
        self.stack = None
        self._session = session
        self.heat_timeout = None
        self.heat_block = True
        self.template_file = None
        self.heat_parameters = None

        self.servers = []
        self.placement_groups = []
        self.server_groups = []
        self.qos_policies = []
        self.security_group = None
        self.sec_group_name = None
        self.keypair = None
        self.networks = OrderedDict()
        self._server_map = {}
        self._image = None
        self._flavor = None
        self.flavors = None
        self.instances = 1

        self.attrs = {}
        self._user = None
        self.gen_key_file = False
        self.error = None
        super(HeatContext, self).__init__(session=session)

    @staticmethod
    def sorted_network(networks):
        """
        :param networks:
        :return:
        """
        sorted_networks = sorted(networks.items())
        return sorted_networks

    def init(self, attrs):
        """
        Initializes itself from the supplied arguments
        :param attrs:
        :return:
        """
        stack_attrs = attrs['stack']
        super(HeatContext, self).init(stack_attrs)
        self.heat_timeout = stack_attrs.get("timeout", consts.DEFAULT_HEAT_TIMEOUT)
        self.heat_block = stack_attrs.get("block", True)
        resource_attrs = attrs.get('resources')
        if not resource_attrs:
            # don't initialize resources in case: un deployment
            return

        keypair_attrs = resource_attrs.get('keypair')
        if isinstance(keypair_attrs, dict):
            self.keypair = md.KeyPair(name=keypair_attrs['name'], context=self, attrs=keypair_attrs)

        self.security_group = resource_attrs.get("security_group")

        self._image = resource_attrs.get("image")

        self._flavor = resource_attrs.get("flavor")

        self._user = resource_attrs.get("user")

        self.placement_groups = [md.PlacementGroup(name, self, pg_attrs["policy"])
                                 for name, pg_attrs in resource_attrs.get("placement_groups",
                                                                          {}).items()]

        self.server_groups = [md.ServerGroup(name, self, sg_attrs["policy"])
                              for name, sg_attrs in resource_attrs.get("server_groups",
                                                                       {}).items()]

        self.networks = OrderedDict((net_attrs['name'], md.Network(net_attrs['name'], self, net_attrs))
                                    for net_attrs in resource_attrs["networks"])

        for server_attrs in resource_attrs["servers"]:
            name = server_attrs.pop('name')
            server = md.Server(name, self, server_attrs)
            self.servers.append(server)
            self._server_map[server.dn] = server

        self.attrs = attrs

    def check_environment(self):
        """

        :return:
        """

    @property
    def image(self):
        """
        Get default image name
        :return:
        """
        return self._image

    @property
    def flavor(self):
        """
        Get default flavor name
        :return:
        """
        return self._flavor

    @property
    def user(self):
        """
        Get default user name
        :return:
        """
        return self._user

    def _add_resources_to_template(self, template):
        # if self.flavor:
        #     if isinstance(self.flavor, dict):
        #         flavor = self.flavor.setdefault('name', self.name + "-flavor")
        #         template.add_flavor(**self.flavor)
        #         self.flavors.add(flavor)

        # Add a new keypair if not exists
        if self.keypair:
            if not self.keypair.is_existing:
                template.add_keypair(keypair=self.keypair)

        # Add security group
        if self.security_group:
            self.sec_group_name = self.security_group.get('name', 'security-group') or 'security-group'
            description = self.security_group.get('description')
            rules = self.parse_sc_rules(self.security_group.get('rules') or [])
            template.add_security_group(name=self.sec_group_name, stack_name=self.name,
                                        description=description, rules=rules)

        # Add networks
        for network in self.networks.values():
            if network.is_existing:
                continue

            template.add_network(network=network)
            subnet = network.subnet
            template.add_subnet(network=network.stack_name, subnet=subnet)
            if network.router:
                template.add_router(subnet=subnet.stack_name, router=network.router)

                kwargs = {
                    'subnet': subnet.stack_name,
                }
                template.add_router_interface(network.router.stack_if_name, network.router.stack_name,
                                              **kwargs)

        list_of_servers = sorted(self.servers,
                                 key=lambda s: len(s.placement_groups))
        availability_servers = []
        for server in list_of_servers:
            for pg in server.placement_groups:
                if pg.policy == "availability":
                    availability_servers.append(server)
                    break

        for server in availability_servers:
            if isinstance(server.flavor, dict):
                try:
                    self.flavors.add(server.flavor["name"])
                except KeyError:
                    self.flavors.add(str_util.h_join(server.stack_name, "flavor"))
        # add servers with availability policy

        added_servers = []
        for server in availability_servers:
            scheduler_hints = {}
            for pg in server.placement_groups:
                md.update_scheduler_hints(scheduler_hints, added_servers, pg)
            # for details
            if len(availability_servers) == 2:
                if not scheduler_hints["different_host"]:
                    scheduler_hints.pop("different_host", None)
                    server.add_to_template(template,
                                           list(self.networks.values()),
                                           scheduler_hints)
                else:
                    scheduler_hints["different_host"] = \
                        scheduler_hints["different_host"][0]
                    server.add_to_template(template,
                                           list(self.networks.values()),
                                           scheduler_hints)
            else:
                server.add_to_template(template,
                                       list(self.networks.values()),
                                       scheduler_hints)
            added_servers.append(server.stack_name)

        # create list of servers with affinity policy
        affinity_servers = []
        for server in list_of_servers:
            for pg in server.placement_groups:
                if pg.policy == "affinity":
                    affinity_servers.append(server)
                    break

        # add servers with affinity policy
        for server in affinity_servers:
            if server.stack_name in added_servers:
                continue
            scheduler_hints = {}
            for pg in server.placement_groups:
                md.update_scheduler_hints(scheduler_hints, added_servers, pg)
            server.add_to_template(template, list(self.networks.values()),
                                   scheduler_hints)
            added_servers.append(server.stack_name)

        # add server group
        for sg in self.server_groups:
            template.add_server_group(sg.name, sg.policy)

        # add remaining servers with no placement group configured
        for server in list_of_servers:
            # TODO placement_group and server_group should combine
            if not server.placement_groups:
                scheduler_hints = {}
                # affinity/anti-aff server group
                sg = server.server_group
                if isinstance(sg, md.ServerGroup):
                    scheduler_hints["group"] = {'get_resource': sg.name}
                else:
                    # scheduler_hints["group"] = sg
                    pass

                server.add_to_template(template,
                                       list(self.networks.values()),
                                       scheduler_hints)

    @staticmethod
    def parse_sc_rules(rules):
        results = []
        for rule in rules:
            rule_ = {
                'direction': rule.get('direction') or 'ingress',
                'ethertype': rule.get('ether_type') or 'IPv4',
                'protocol': rule.get('protocol') or 'tcp',
                'remote_ip_prefix': rule.get('remote_ip_prefix') or '0.0.0.0/0',
            }
            port_range = rule.get('port_range')
            if port_range:
                try:
                    port_range_arr = port_range.split(":")
                    if port_range_arr[0] <= port_range_arr[1]:
                        if int(port_range_arr[0]) > 0 or int(port_range_arr[1]) <= 65535:
                            rule_['port_range_max'] = port_range_arr[1]
                            rule_['port_range_min'] = port_range_arr[0]
                        else:
                            msg = _("Ports out of ranger '%s'") % port_range
                            raise fox_exc.FoxCloudException(msg)
                except Exception as e:
                    raise fox_exc.FoxCloudException(e)
            results.append(rule_)
        return results

    def get(self):
        """
        Subclass should override this method.
        :return:
        """

    def create(self):
        """
        Subclass should override this method.
        :return:
        """
        heat_template = orchestrator.NovaHeatTemplate(name=self.name,
                                                      template_file=self.template_file,
                                                      heat_parameters=self.heat_parameters,
                                                      session=self._session)

        if self.template_file is None:
            self._add_resources_to_template(heat_template)

        try:
            if self._flags.no_setup:
                self.stack = self._retrieve_existing_stack(stack_name=self.name)
                if not self.stack:
                    self.stack = self._create_new_stack(heat_template=heat_template,
                                                        block=self.heat_block,
                                                        timeout=self.heat_timeout)
            else:
                self.stack = self._create_new_stack(heat_template=heat_template,
                                                    block=self.heat_block,
                                                    timeout=self.heat_timeout)
        except fox_exc.FoxCloudException as e:
            self.error = e

        if not self.error:
            self.get_neutron_info()

            for server in self.servers:
                if server.ports:
                    self.add_server_port(server)

                if server.floating_ip:
                    server.public_ip = self.stack.outputs[server.floating_ip["stack_name"]]

        return self.build_output()

    def build_output(self):
        """
        Build output
        :return:
        """
        if self.stack:
            if self.stack.status == 'COMPLETE':
                instances = []
                output = self.stack.outputs
                nova_client = nova_util.get_nova_client(version=consts.VERSIONS['nova'],
                                                        session=self._session)
                for server in self.servers:
                    if server.instances == 1:
                        instance_id = output.get(server.stack_name)
                        instance_info = nova_util
                        if instance_info is None:
                            instances.append({
                                'id': instance_id
                            })
                        else:
                            instances.append(instance_info.to_dict())
                    else:
                        for i in range(0, server.instances):
                            stack_name = "%s-%d" % (server.stack_name, i)
                            instance_id = output.get(stack_name)
                            instance_info = nova_util
                            if instance_info is None:
                                instances.append({
                                    'id': instance_id
                                })
                            else:
                                instances.append(instance_info.to_dict())
                data = {
                    'stack_status': self.stack.status,
                    'stack_id': self.stack.uuid,
                    'name': self.stack.name_or_id,
                    'task_id': self._task_id,
                    'raw': output,
                    'instances': instances
                }
                return {
                    'data': data,
                    'stack_status': self.stack.status,
                }
            else:
                return {
                    'data': None,
                    'status': self.stack.status,
                }
        else:
            return {
                'data': None,
                'status': None,
            }

    @staticmethod
    def _port_net_is_existing(port_info):
        net_flags = port_info.get('net_flags', {})
        return net_flags.get(consts.IS_EXISTING)

    @staticmethod
    def _port_net_is_public(port_info):
        net_flags = port_info.get('net_flags', {})
        return net_flags.get(consts.IS_PUBLIC)

    def get_neutron_info(self):
        """
        Get services network info

        :return:
        """
        # if not self.shade_client:
        #     self.shade_client = ops_util.get_shade_client()
        # flavor = self.shade_client.get_flavor_by_ram(2048)
        # networks = self.shade_client.list_networks()
        # for network in self.networks.values():
        #     for neutron_net in (net for net in networks if net.name == network.stack_name):
        #         network.segmentation_id = neutron_net.get('provider:segmentation_id')
        #         # we already have physical_network
        #         network.network_type = neutron_net.get('provider:network_type')
        #         network.neutron_info = neutron_net

    def add_server_port(self, server):
        server_ports = server.ports.values()
        for server_port in server_ports:
            port_info = server_port[0]
            port_ip = self.stack.outputs[port_info["stack_name"]]
            port_net_is_existing = self._port_net_is_existing(port_info)
            port_net_is_public = self._port_net_is_public(port_info)
            if port_net_is_existing and (port_net_is_public or
                                         len(server_ports) == 1):
                server.public_ip = port_ip
            if not server.private_ip or len(server_ports) == 1:
                server.private_ip = port_ip
        server.interfaces = {}
        for network_name, ports in server.ports.items():
            for port in ports:
                # port['port'] is either port name from mapping or default network_name
                if self._port_net_is_existing(port):
                    continue
                server.interfaces[port['port']] = self._make_interface_dict(network_name,
                                                                            port['port'],
                                                                            port['stack_name'],
                                                                            self.stack.outputs)
                server.override_ip(network_name, port)

    def _make_interface_dict(self, network_name, port, stack_name, outputs):
        private_ip = outputs[stack_name]
        mac_address = outputs[str_util.h_join(stack_name, "mac_address")]
        # these are attributes of the network, not the port
        output_subnet_cidr = outputs[str_util.h_join(self.name, network_name,
                                                     'subnet', 'cidr')]

        # these are attributes of the network, not the port
        output_subnet_gateway = outputs[str_util.h_join(self.name, network_name,
                                                        'subnet', 'gateway_ip')]

        return {
            # add default port name
            "name": port,
            "private_ip": private_ip,
            "subnet_id": outputs[str_util.h_join(stack_name, "subnet_id")],
            "subnet_cidr": output_subnet_cidr,
            "network": str(ipaddress.ip_network(output_subnet_cidr).network_address),
            "netmask": str(ipaddress.ip_network(output_subnet_cidr).netmask),
            "gateway_ip": output_subnet_gateway,
            "mac_address": mac_address,
            "device_id": outputs[str_util.h_join(stack_name, "device_id")],
            "network_id": outputs[str_util.h_join(stack_name, "network_id")],
            # this should be == vld_id for NSB tests
            "network_name": network_name,
            # to match vnf_generic
            "local_mac": mac_address,
            "local_ip": private_ip,
        }

    def update(self):
        """
        Subclass should override this method.
        :return:
        """
        heat_template = orchestrator.NovaHeatTemplate(name=self.name,
                                                      template_file=self.template_file,
                                                      heat_parameters=self.heat_parameters,
                                                      session=self._flags.session)

        if self.template_file is None:
            self._add_resources_to_template(heat_template)
        try:
            if self._flags.no_setup:
                self.stack = self._retrieve_existing_stack(stack_name=self.name)
                if not self.stack:
                    self.stack = self._update_new_stack(heat_template=heat_template)
            else:
                self.stack = self._create_new_stack(heat_template=heat_template,
                                                    block=self.heat_block,
                                                    timeout=self.heat_timeout)
        except fox_exc.FoxCloudException as e:
            self.error = e

        if not self.error:
            self.get_neutron_info()

            for server in self.servers:
                if server.ports:
                    self.add_server_port(server)

                if server.floating_ip:
                    server.public_ip = self.stack.outputs[server.floating_ip["stack_name"]]

        return self.build_output()

    def delete(self):
        """
        Subclass should override this method.
        :return:
        """
        if self._flags.no_teardown:
            return

        error = None
        if self._flags.no_setup:
            self.stack = self._retrieve_existing_stack(stack_name=self.name)
        else:
            msg = "Cannot initialize stack '{}' resource".format(self.name)
            raise fox_exc.FoxCloudException(msg)
        try:
            if self.stack:
                self.stack.delete(wait=self.heat_block)
                super(HeatContext, self).delete()
                return {}
        except fox_exc.FoxCloudException as e:
            error = e
        return {
            'error': error
        }

    def abandon(self):
        """
        Subclass should override this method.
        :return:
        """
        if self._flags.no_teardown:
            return

        error = None
        if self._flags.no_setup:
            self.stack = self._retrieve_existing_stack(stack_name=self.name)
        else:
            msg = "Cannot initialize stack '{}' resource".format(self.name)
            raise fox_exc.FoxCloudException(msg)
        try:
            if self.stack:
                self.stack.abandon(wait=self.heat_block)
                super(HeatContext, self).delete()
                return {}
        except fox_exc.FoxCloudException as e:
            error = e
        return {
            'error': error
        }
