import os
import time

from novaclient import exceptions as nova_exc
from keystoneauth1 import exceptions as ks_exc
from cinderclient import exceptions as cinder_exc

from foxcloud import (base as fox_base, exceptions as fox_exc, api_versions)
from foxcloud.i18n import _
from foxcloud.v1.services import base as service_base
from foxcloud.v1.utils.data_util import valid_kwargs


class ShadeResource(fox_base.Resource):
    """

    """
    pass


class ShadeManager(service_base.BaseChildManager):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    resource_class = ShadeResource

    ACTIONS = ['start', 'stop', 'pause', 'unpause', 'suspend', 'resume', 'reboot']

    def __init__(self, name_or_id, version, session, engine, endpoint=None, **kwargs):
        super(ShadeManager, self).__init__(name_or_id, version, session, engine, endpoint, **kwargs)
        if not self._is_supported():
            msg = _("Not supported engine '%s'. "
                    "Expected %s") % {self.engine, ' or '.join(e.upper() for e in fox_base.SUPPORTED_ENGINES)}
            raise fox_exc.FoxCloudUnSupportedEngine(msg)

        # TODO check to find subclasses
        # self.api = sys_util.find_subclasses(self.engine, base_class=BaseInstance)
        if self.engine == 'heat':
            from foxcloud.v1.services.shade.heat import base as heat_base
            self._api = heat_base.Heat(session=session)
        if self.engine == 'console':
            from foxcloud.v1.services.shade import console
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
    # KEYSTONE

    def get_user(self, user_id):
        """
        Get user
        :param user_id:
        :return:
        """
        try:
            user_info = self._api.ks_api.users.get(user=user_id)
            return self.resource_class(self, info=user_info)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_users(self, project_id=None, domain_id=None, group_id=None,
                  default_project_id=None, **kwargs):
        """
        Get Users
        :param project_id:
        :param domain_id:
        :param group_id:
        :param default_project_id:
        :param kwargs:
        :return:
        """
        try:
            users = self._api.ks_api.users.list(project=project_id, domain_id=domain_id, group_id=group_id,
                                                default_project_id=default_project_id, **kwargs)
            return self.resource_class(self, info=[user for user in users])
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_user(self, name, domain_id=None, project_id=None, password=None,
                    email=None, description=None, enabled=True,
                    default_project_id=None, **kwargs):
        """Create a user.

        :param str name: the name of the user.
        :param domain: the domain of the user.
        :type domain_id: str or :class:`keystoneclient.v3.domains.Domain`
        :param project: the default project of the user.
                        (deprecated, see warning below)
        :type project_id: str or :class:`keystoneclient.v3.projects.Project`
        :param str password: the password for the user.
        :param str email: the email address of the user.
        :param str description: a description of the user.
        :param bool enabled: whether the user is enabled.
        :param default_project: the default project of the user.
        :type default_project_id: str or
                               :class:`keystoneclient.v3.projects.Project`
        :param kwargs: any other attribute provided will be passed to the
                       server.
        """
        try:
            user = self._api.ks_api.users.create(name, domain_id, project_id, password,
                                                 email, description, enabled,
                                                 default_project_id, **kwargs)

            return self.resource_class(self, info=user)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_user(self, user_id, name=None, domain_id=None, project_id=None, password=None,
                    email=None, description=None, enabled=None,
                    default_project_id=None, **kwargs):
        """
        Update user
        :param user_id:
        :param name:
        :param domain_id:
        :param project_id:
        :param password:
        :param email:
        :param description:
        :param enabled:
        :param default_project_id:
        :param kwargs:
        :return:
        """
        try:
            user = self._api.ks_api.users.update(user_id, name, domain_id, project_id, password,
                                                 email, description, enabled,
                                                 default_project_id, **kwargs)
            return self.resource_class(self, info=user)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def add_user_to_group(self, user_id, group_id):
        """
        Add user to group
        :param user_id:
        :param group_id:
        :return:
        """
        try:
            user = self._api.ks_api.users.add_to_group(user_id, group_id)
            return self.resource_class(self, info=user)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_user(self, user_id):
        """
        Delete a specific user
        :param user_id:
        :return:
        """
        try:
            res = self._api.ks_api.users.delete(user_id)
            data = {
                'status': True if res.status_code == '204' else False,
                'message': res.text,
            }
            return self.resource_class(self, info=data)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_project(self, project_id):
        """
        Get project
        :param project_id:
        :return:
        """
        try:
            user_info = self._api.ks_api.projects.get(project=project_id)
            return self.resource_class(self, info=user_info)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_projects(self, domain=None, user_id=None, parent=None, **kwargs):
        """
        Get projects
        :param domain:
        :param user_id:
        :param parent:
        :param kwargs:
        :return:
        """
        try:
            projects = self._api.ks_api.projects.list(domain, user_id, parent, **kwargs)
            return self.resource_class(self, info=[project for project in projects])
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_project(self, name, domain_id, description=None, enabled=True, parent=None, **kwargs):
        """
        Create project
        :param name:
        :param domain:
        :param description:
        :param enabled:
        :param parent:
        :param kwargs:
        :return:
        """
        try:
            project = self._api.ks_api.projects.create(name, domain_id, description, enabled, parent, **kwargs)
            return self.resource_class(self, info=project)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_project(self, project_id, name=None, domain_id=None, description=None,
                       enabled=None, **kwargs):
        """
        Update project
        :param project_id:
        :param name:
        :param domain_id:
        :param description:
        :param enabled:
        :param kwargs:
        :return:
        """
        try:
            project = self._api.ks_api.projects.update(project_id, name, domain_id,
                                                       description, enabled, **kwargs)
            return self.resource_class(self, info=project)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_project(self, project_id):
        """
        Delete a specific project
        :param project_id:
        :return:
        """
        try:
            res = self._api.ks_api.projects.delete(project_id)
            data = {
                'status': True if res.status_code == '204' else False,
                'message': res.text,
            }
            return self.resource_class(self, info=data)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def assign_role(self, role_id, user_id=None, project_id=None, domain_id=None, group_id=None,
                    system=None, os_inherit_extension_inherited=False, **kwargs):
        """
        Grant a role to a user or group on a domain or project.
        :param role_id:
        :param user_id
        :param project_id:
        :param domain_id
        :param group_id:
        :param system
        :param os_inherit_extension_inherited:
        :param kwargs
        :return
        """
        try:
            project = self._api.ks_api.roles.grant(role=role_id, user=user_id, project=project_id,
                                                   domain=domain_id, group=group_id, system=system,
                                                   os_inherit_extension_inherited=os_inherit_extension_inherited,
                                                   **kwargs)
            return self.resource_class(self, info=project)
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_roles(self, user_id=None, group_id=None, system=None, domain_id=None,
                  project_id=None, os_inherit_extension_inherited=False, **kwargs):
        """
        Get all roles
        :param user_id
        :param project_id:
        :param domain_id
        :param group_id:
        :param system
        :param os_inherit_extension_inherited:
        :param kwargs
        """
        try:
            roles = self._api.ks_api.roles.list(user=user_id, project=project_id, domain=domain_id,
                                                group=group_id, system=system,
                                                os_inherit_extension_inherited=os_inherit_extension_inherited,
                                                **kwargs)
            return self.resource_class(self, info=[role for role in roles])
        except ks_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    # NEUTRON
    def get_neutron_network(self, network_id, **filters):
        try:
            data = self._api.neu_api.show_network(network=network_id, **filters)
            return self.resource_class(self, info=data['network'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_neutron_networks(self, **filters):
        """
        Subclass should be override this method
        :param filters:
        :return:
        """
        try:
            if filters is None:
                filters = {}
            data = self._api.neu_api.list_networks(retrieve_all=True, **filters)
            return self.resource_class(self, info=data['networks'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def create_neutron_network(self, name, shared=False, admin_state_up=True,
                               external=False, provider=None, project_id=None,
                               availability_zone_hints=None,
                               port_security_enabled=None,
                               mtu_size=None):
        try:
            data = self._api.neu_api.create_neutron_network(name, shared, admin_state_up,
                                                            external, provider, project_id,
                                                            availability_zone_hints,
                                                            port_security_enabled, mtu_size)
            return self.resource_class(self, info=data['network'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def update_neutron_network(self, network_id, name, revision_number=None, shared=False,
                               admin_state_up=True, external=False, provider=None,
                               project_id=None, availability_zone_hints=None,
                               port_security_enabled=None, mtu_size=None):
        try:
            data = self._api.neu_api.update_neutron_network(network_id, name, revision_number, shared,
                                                            admin_state_up, external, provider,
                                                            project_id, availability_zone_hints,
                                                            port_security_enabled, mtu_size)
            return self.resource_class(self, info=data['network'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def delete_neutron_network(self, network_id):
        try:
            data = self._api.neu_api.delete_network(network=network_id)
            return self.resource_class(self, info=data)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_neutron_subnets(self, **filters):
        try:
            data = self._api.neu_api.list_subnets(**filters)
            return self.resource_class(self, info=data['subnets'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_neutron_subnet(self, subnet_id, **filters):
        try:
            data = self._api.neu_api.show_subnet(subnet=subnet_id, **filters)
            return self.resource_class(self, info=data['subnet'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def create_neutron_subnet(self, network_id, name, cidr=None, ip_version=4,
                              enable_dhcp=False, tenant_id=None, gateway_ip=None,
                              allocation_pools=None, disable_gateway_ip=False,
                              dns=None, host_routes=None, ipv6_ra_mode=None,
                              ipv6_address_mode=None, default_subnet_pool=False):
        try:
            data = self._api.neu_api.create_neutron_subnet(network_id, name, cidr, ip_version,
                                                           enable_dhcp, tenant_id, gateway_ip,
                                                           allocation_pools, disable_gateway_ip,
                                                           dns, host_routes, ipv6_ra_mode,
                                                           ipv6_address_mode, default_subnet_pool)
            return self.resource_class(self, info=data['subnet'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def update_neutron_subnet(self, subnet_id, name=None, enable_dhcp=None,
                              gateway_ip=None, disable_gateway_ip=None,
                              allocation_pools=None, dns=None,
                              host_routes=None, revision_number=None):
        try:
            data = self._api.neu_api.update_neutron_subnet(subnet_id, name, enable_dhcp,
                                                           gateway_ip, disable_gateway_ip,
                                                           allocation_pools, dns,
                                                           host_routes, revision_number)
            return self.resource_class(self, info=data['subnet'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def delete_neutron_subnet(self, subnet_id):
        try:
            data = self._api.neu_api.delete_subnet(subnet=subnet_id)
            return self.resource_class(self, info=data)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_sec_group(self, sg_id, **filters):
        """
        Get secgroup
        :param sg_id:
        :param filters:
        :return:
        """
        try:
            data = self._api.neu_api.show_security_group(security_group=sg_id, **filters)
            return self.resource_class(self, info=data['security_group'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_sec_groups(self, **filters):
        """
        Get secgroup
        :param filters:
        :return:
        """
        try:
            data = self._api.neu_api.list_security_groups(**filters)
            return self.resource_class(self, info=data['security_groups'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def create_sec_group(self, name, description, project_id=None):
        try:
            data = self._api.neu_api.create_sec_group(name, description, project_id)
            return self.resource_class(self, info=data['security_group'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('name', 'description')
    def update_sec_group(self, sg_id, revision_number=None, **kwargs):
        try:
            data = self._api.neu_api.update_sec_group(sg_id, revision_number, **kwargs)
            return self.resource_class(self, info=data['security_group'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def delete_sec_group(self, sg_id):
        try:
            data = self._api.neu_api.delete_security_group(sg_id)
            return self.resource_class(self, info=data)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_sg_rule(self, sg_rule_id, **filters):
        """
        :param sg_rule_id:
        :param filters:
        :return:
        """
        try:
            data = self._api.neu_api.show_security_group_rule(security_group_rule=sg_rule_id, **filters)
            return self.resource_class(self, info=data['security_group_rule'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_sg_rules(self, **filters):
        """
        :param filters:
        :return:
        """
        try:
            data = self._api.neu_api.list_security_group_rules(**filters)
            return self.resource_class(self, info=data['security_group_rules'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def create_sec_group_rule(self, sg_id, port_range_min=None,
                              port_range_max=None, protocol=None,
                              remote_ip_prefix=None, remote_group_id=None,
                              direction='ingress', ethertype='IPv4',
                              project_id=None):
        try:
            data = self._api.neu_api.create_sec_group_rule(sg_id, port_range_min,
                                                           port_range_max, protocol,
                                                           remote_ip_prefix, remote_group_id,
                                                           direction, ethertype,
                                                           project_id)
            return self.resource_class(self, info=data['security_group_rule'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def delete_sg_rule(self, rule_id):
        """
        Delete security group rule
        :param rule_id:
        :return:
        """
        try:
            data = self._api.neu_api.delete_security_group_rule(rule_id)
            return self.resource_class(self, info=data)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_neutron_router(self, router_id, **filters):
        try:
            data = self._api.neu_api.show_router(router_id, **filters)
            return self.resource_class(self, info=data['router'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_neutron_routers(self, **filters):
        try:
            data = self._api.neu_api.list_routers(**filters)
            return self.resource_class(self, info=data['routers'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def create_neutron_router(self, name=None, admin_state_up=True,
                              ext_gateway_net_id=None, enable_snat=None,
                              ext_fixed_ips=None, project_id=None,
                              availability_zone_hints=None):
        try:
            data = self._api.neu_api.create_neutron_router(name, admin_state_up,
                                                           ext_gateway_net_id, enable_snat,
                                                           ext_fixed_ips, project_id,
                                                           availability_zone_hints)
            return self.resource_class(self, info=data['router'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def update_neutron_router(self, router_id, name=None, admin_state_up=True,
                              ext_gateway_net_id=None, enable_snat=None,
                              ext_fixed_ips=None, routes=None, revision_number=None):
        try:
            data = self._api.neu_api.update_neutron_router(router_id, name, admin_state_up,
                                                           ext_gateway_net_id, enable_snat,
                                                           ext_fixed_ips, routes, revision_number)
            return self.resource_class(self, info=data['router'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def delete_neutron_router(self, router_id):
        try:
            data = self._api.neu_api.delete_router(router_id)
            return self.resource_class(self, info=data)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def add_router_interface(self, router_id, subnet_id=None, port_id=None):
        json_body = {}
        if subnet_id:
            json_body['subnet_id'] = subnet_id
        if port_id:
            json_body['port_id'] = port_id

        try:
            data = self._api.neu_api.add_interface_router(router=router_id, body=json_body)
            return self.resource_class(self, info=data)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def remove_router_interface(self, router_id, subnet_id=None, port_id=None):
        try:
            json_body = {}
            if subnet_id:
                json_body['subnet_id'] = subnet_id
            if port_id:
                json_body['port_id'] = port_id
            data = self._api.neu_api.remove_interface_router(router=router_id, body=json_body)
            return self.resource_class(self, info=data)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def remove_gateway_router(self, router_id):
        try:
            data = self._api.neu_api.remove_gateway_router(router=router_id)
            return self.resource_class(self, info=data)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_neutron_port(self, port_id, **filters):
        try:
            data = self._api.neu_api.show_port(port_id=port_id, **filters)
            return self.resource_class(self, info=data['port'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def get_neutron_ports(self, **filters):
        try:
            data = self._api.neu_api.list_ports(**filters)
            return self.resource_class(self, info=data['ports'])
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('name', 'admin_state_up', 'mac_address', 'fixed_ips',
                  'subnet_id', 'ip_address', 'security_groups',
                  'allowed_address_pairs', 'extra_dhcp_opts',
                  'device_owner', 'device_id')
    def create_neutron_port(self, network_id, **kwargs):
        try:
            data = self._api.neu_api.self.create_neutron_port(network_id, **kwargs)
            return self.resource_class(self, info=data['port'])
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('name', 'admin_state_up', 'fixed_ips',
                  'security_groups', 'allowed_address_pairs',
                  'extra_dhcp_opts', 'device_owner', 'device_id')
    def update_neutron_port(self, port_id, revision_number=None, **kwargs):
        try:
            data = self._api.neu_api.self.update_neutron_port(port_id,
                                                              revision_number=revision_number,
                                                              **kwargs)
            return self.resource_class(self, info=data['port'])
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_neutron_port(self, port_id):
        try:
            data = self._api.neu_api.delete_port(port_id)
            return self.resource_class(self, info=data)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_port_binding(self, port_id, host_id, **filters):
        try:
            data = self._api.neu_api.show_port_binding(port_id, host_id, **filters)
            return self.resource_class(self, info=data['binding'])
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_neutron_port_bindings(self, port_id, **filters):
        try:
            data = self._api.neu_api.list_port_bindings(port_id=port_id, **filters)
            return self.resource_class(self, info=data['bindings'])
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_neutron_port_binding(self, port_id, **kwargs):
        try:
            data = self._api.neu_api.create_neutron_port_binding(port_id, **kwargs)
            return self.resource_class(self, info=data['binding'])
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_neutron_port_binding(self, port_id, host_id):
        """Deletes the specified port binding."""
        try:
            data = self._api.neu_api.delete_neutron_port_binding(port_id, host_id)
            return self.resource_class(self, info=data)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    # NOVA
    def get_server(self, server_id):
        try:
            data = self._api.servers.get(server=server_id)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_servers(self, detailed=True, search_opts=None, marker=None,
                    limit=None, sort_keys=None, sort_dirs=None):
        try:
            data = self._api.servers.list(detailed, search_opts, marker,
                                          limit, sort_keys, sort_dirs)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_server_sec_groups(self, server_id):
        """
        List all security groups of server
        :param server_id:
        :return:
        """
        try:
            data = self._api.servers.list_security_group(server=server_id)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_server(self, info):
        """
        Create a new server
        :param info:
        :return:
        """
        data = self._api.create_server(info=info)
        return self.resource_class(self, info=data)

    def perform_server_action(self, server_id, action='start', **kwargs):
        """
        Perform a action
        :param server_id:
        :param action: [start, stop, pause, unpause, suspend, resume]
        :return:
        """
        try:
            if action not in self.ACTIONS:
                msg = _("Not supported action '%s'") % action
                raise fox_exc.FoxCloudException(msg)
            func_call = getattr(self._api.servers, action)
            if action == 'reboot':
                reboot_type = kwargs.get('reboot_type') or 'SOFT'
                data = func_call(server=server_id, reboot_type=reboot_type)
            else:
                data = func_call(server=server_id)
            if not isinstance(data.request_ids, list):
                return self.resource_class(self, info=True)

            for req_id in data.request_ids:
                error, data = self._wait_do_action(server_id=server_id, request_id=req_id,
                                                   action=action, timeout=60, check_interval=3)
                if error:
                    raise fox_exc.FoxCloudException(message=error)

            return self.resource_class(self, info=True)
        except Exception as e:
            raise fox_exc.FoxCloudException(e)

    def _wait_do_action(self, server_id, request_id, action, timeout=60, check_interval=3):
        """
        Wait a task to be done or failed.
        :param server_id:
        :param request_id:
        :param action:
        :param timeout:
        :param check_interval:
        :return: a dict of
            {
                'error': <if omit, no error>,
            }
        """
        if request_id is None or server_id is None:
            return None, None

        total_wait = 0
        while True:
            time.sleep(check_interval)
            task_info = self._api.instance_action.get(server=server_id,
                                                      request_id=request_id)
            if not task_info:
                return "Not found action", False

            if task_info.action == action:
                is_completed = False
                for event in task_info.events or []:
                    is_completed = event.get('result') == "Success"

                if is_completed:
                    return None, True
                else:
                    total_wait += check_interval
                    if not timeout and total_wait >= timeout:
                        break
            else:
                return None, True

        return "Action time out", False

    def lock_server(self, server_id, reason=None):
        try:
            data = self._api.servers.lock(server=server_id, reason=reason)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def unlock_server(self, server_id):
        try:
            data = self._api.servers.unlock(server=server_id)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_server_action(self, server_id, request_id):
        try:
            data = self._api.instance_action.get(server=server_id,
                                                 request_id=request_id)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def attach_server_sec_groups(self, server_id, sg_ids=[]):
        sg_ids = sg_ids or []
        sec_groups = []
        for sg_id in sg_ids:
            try:
                sg = self._api.servers.add_security_group(server=server_id,
                                                          security_group=sg_id)
                if sg:
                    sec_groups.append(sg)
            except nova_exc.ClientException as e:
                raise fox_exc.FoxCloudException(e)
        return self.resource_class(self, info=sg_ids)

    def remove_server_sec_group(self, server_id, sg_id):
        try:
            sg = self._api.servers.remove_security_group(server=server_id,
                                                         security_group=sg_id)
            return self.resource_class(self, info=sg)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_volume(self, server_id, volume_id):
        """
        Get a specific volume of server
        :param server_id:
        :param volume_id:
        :return:
        """
        try:
            volume = self._api.volumes.get_server_volume(server_id=server_id, volume_id=volume_id)
            return self.resource_class(self, info=volume)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_volumes(self, server_id):
        """
        List all volumes of server
        :param server_id:
        :return:
        """
        try:
            volumes = self._api.volumes.get_server_volumes(server_id=server_id)
            return self.resource_class(self, info=volumes)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def reset_volume_state(self, volume_id, state):
        try:
            # TODO
            return self.resource_class(self, info=True)

        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_volume(self, name_or_id=None, wait=True, timeout=None):
        """
        Delete volume
        :param name_or_id:
        :param wait:
        :param timeout:
        :return:
        """

    def attach_volume(self, server_id, volume_id, wait=True, timeout=None):
        """
        Detach volume
        :param server_id:
        :param volume_id:
        :param wait:
        :param timeout:
        :return:
        """
        try:
            volumes = self._api.servers.get_server_volumes(server=server_id)
            return self.resource_class(self, info=volumes)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def detach_volume(self, server_id, volume_id, wait=True, timeout=None):
        """
        Detach volume
        :param server_id:
        :param volume_id:
        :param wait:
        :param timeout:
        :return:
        """

    def get_volume_backup(self, backup_id):
        """
        Get a backup by ID.
        :param backup_id:
        :return:
        """
        try:
            backup = self._api.cinder_api.backups.get(backup_id=backup_id)
            return self.resource_class(self, info=backup)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_volume_backups(self, detailed=True, search_opts=None, marker=None, limit=None, sort=None):
        """
        Get all snapshots of volumes
        :param detailed:
        :param search_opts:
        :param marker:
        :param limit:
        :param sort:
        :return:
        """
        try:
            backups = self._api.cinder_api.backups.list(detailed, search_opts, marker, limit, sort)
            return self.resource_class(self, info=backups)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_volume_backup(self, volume_id, container=None, name=None, description=None,
                             incremental=False, force=False, snapshot_id=None, metadata=None,
                             availability_zone=None):
        """
        Create a backup
        :param volume_id:
        :param container:
        :param name:
        :param description:
        :param incremental:
        :param force:
        :param snapshot_id:
        :param metadata:
        :param availability_zone:
        :return:
        """
        try:
            backup = self._api.cinder_api.backups.create(volume_id=volume_id, container=container,
                                                         name=name, description=description,
                                                         incremental=incremental, force=force,
                                                         snapshot_id=snapshot_id, metadata=metadata,
                                                         availability_zone=availability_zone)
            return self.resource_class(self, info=backup)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_volume_backup(self, backup_id, force=False):
        """
        Delete a volume backup.
        :param backup_id:
        :param force: Allow delete in state other than error or available.
        """
        try:
            backup = self._api.cinder_api.backups.delete(backup_id, force)
            return self.resource_class(self, info=backup)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def reset_backup_state(self, backup_id, state):
        """
        Reset state of backup
        :param backup_id:
        :param state:
        :return:
        """
        try:
            backup = self._api.cinder_api.backups.reset_state(backup_id, state)
            return self.resource_class(self, info=backup)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def restore_volume_backup(self, backup_id, volume_id=None, name=None):
        """
        Restore a backup to a volume.

        :param backup_id: The ID of the backup to restore.
        :param volume_id: The ID of the volume to restore the backup to.
        :param name: The name for new volume creation to restore.
        :return:
        """
        try:
            backup = self._api.cinder_api.restores.restore(backup_id=backup_id,
                                                           volume_id=volume_id,
                                                           name=name)
            return self.resource_class(self, info=backup)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_volume_snapshot(self, snapshot_id):
        """
        Get a snapshot by ID.
        :param snapshot_id:
        :return:
        """
        try:
            snapshot = self._api.cinder_api.volume_snapshots.get(snapshot_id=snapshot_id)
            return self.resource_class(self, info=snapshot)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_volume_snapshots(self, detailed=True, search_opts=None, marker=None, limit=None, sort=None):
        """
        Get all snapshots of volumes
        :param detailed:
        :param search_opts:
        :param marker:
        :param limit:
        :param sort:
        :return:
        """
        try:
            snapshots = self._api.cinder_api.volume_snapshots.list(detailed, search_opts,
                                                                   marker, limit, sort)
            return self.resource_class(self, info=snapshots)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_volume_snapshot(self, volume_id, force=False, name=None, description=None, metadata=None):
        """
        Create a new snapshot
        :param volume_id:
        :param force:
        :param name:
        :param description:
        :param metadata:
        :return:
        """
        try:
            data = self._api.cinder_api.volume_snapshots.create(volume_id, force, name,
                                                                description, metadata)
            return self.resource_class(self, info=data)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_volume_snapshot(self, snapshot_id, **kwargs):
        """
        Update a specific snapshot
        :param snapshot_id:
        :param kwargs:
        :return:
        """
        try:
            data = self._api.cinder_api.volume_snapshots.update(snapshot_id, **kwargs)
            return self.resource_class(self, info=data)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_volume_snapshot(self, snapshot_id, force=False):
        """
        Delete a specific snapshot
        :param snapshot_id:
        :param force:
        :return:
        """
        try:
            data = self._api.cinder_api.volume_snapshots.delete(snapshot_id, force)
            return self.resource_class(self, info=data)
        except cinder_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_keypair(self, keypair_id, user_id=None):
        try:
            data = self._api.keypairs.get(keypair=keypair_id, user_id=user_id)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_keypairs(self, user_id=None):
        try:
            data = self._api.keypairs.list(user_id=user_id)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def create_keypair(self, name, public_key, key_type="ssh", user_id=None):
        try:
            data = self._api.keypairs.create(name=name, public_key=public_key,
                                             key_type=key_type, user_id=user_id)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_keypair(self, keypair_id, user_id=None):
        try:
            data = self._api.keypairs.delete(key=keypair_id, user_id=user_id)
            return self.resource_class(self, info=data)
        except nova_exc.ClientException as e:
            raise fox_exc.FoxCloudException(e)
