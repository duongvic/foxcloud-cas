#
# Copyright (c) 2020 FTI-CAS
#
import uuid

from octaviaclient.api import exceptions as oct_exc

from foxcloud import (base as fox_base, exceptions as fox_exc, api_versions)
from foxcloud.i18n import _
from foxcloud.v1.services import base as service_base
from foxcloud.v1.utils.data_util import valid_kwargs


class LbaasResource(fox_base.Resource):
    def add_details(self, info):
        """Normalize data information
        Subclass should be override this method
        :param info:
        :return:
        """
        self.data = info


class LbaasManager(service_base.BaseChildManager):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    resource_class = LbaasResource

    SUPPORTED_PROVIDERS = ['octavia']

    def __init__(self, name_or_id, version, session, engine, endpoint=None, **kwargs):
        super(LbaasManager, self).__init__(name_or_id, version, session, engine, endpoint, **kwargs)
        if not self._is_supported():
            msg = _("Not supported engine '%s'. "
                    "Expected %s") % {self.engine, ' or '.join(e.upper() for e in fox_base.SUPPORTED_ENGINES)}
            raise fox_exc.FoxCloudUnSupportedEngine(msg)

        # TODO check to find subclasses
        # self._api = sys_util.find_subclasses(self.engine, base_class=BaseInstance)
        if self.engine == 'heat':
            from foxcloud.v1.services.lbaas.heat import base
            self._api = base.Heat(session=session, endpoint=endpoint)
        if self.engine == 'console':
            from foxcloud.v1.services.lbaas import console
            self._api = console.Console(session=session, endpoint=endpoint)
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
    #   Fetch openstack resources being created
    # **********************************************
    def get_lb(self, lb_id):
        """Get a load balancer being created
        :param lb_id:

        :return:
        """
        try:
            lb = self._api.load_balancer_show(lb_id=lb_id)
            return self.resource_class(self, info=lb)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_lbs(self, **kwargs):
        """Get all load balancers
        :param kwargs:
        :return:
        """
        try:
            data = self._api.load_balancer_list(**kwargs)
            return self.resource_class(self, info=data['loadbalancers'])
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_listener(self, listener_id):
        """Get listener
        :param listener_id:

        :return:
        """
        try:
            ls = self._api.listener_show(listener_id=listener_id)
            return self.resource_class(self, info=ls)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_listeners(self, **kwargs):
        """Get all listeners
        :param kwargs:

        :return:
        """
        try:
            data = self._api.listener_list(**kwargs)
            return self.resource_class(self, info=data['listeners'])
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_pool(self, pool_id):
        """Get pool
        :param pool_id:
        :return:
        """
        try:
            pool = self._api.pool_show(pool_id=pool_id)
            return self.resource_class(self, info=pool)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_pools(self, **kwargs):
        """Get all pools
        :param kwargs:
        :return:
        """
        try:
            data = self._api.pool_list(**kwargs)
            return self.resource_class(self, info=data['pools'])
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_member(self, pool_id, member_id):
        """Get member
        :param pool_id:
        :param member_id:
        :return:
        """
        try:
            data = self._api.member_show(pool_id=pool_id, member_id=member_id)
            return self.resource_class(self, info=data)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_members(self, pool_id, **kwargs):
        """
        :param pool_id:
        :param kwargs:
        :return:
        """
        try:
            data = self._api.member_list(pool_id=pool_id, **kwargs)
            return self.resource_class(self, info=data['members'])
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_monitor(self, monitor_id):
        try:
            data = self._api.health_monitor_show(health_monitor_id=monitor_id)
            return self.resource_class(self, info=data)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_monitors(self, **kwargs):
        try:
            data = self._api.health_monitor_list(**kwargs)
            return self.resource_class(self, info=data['healthmonitors'])
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_l7policy(self, l7policy_id):
        """Get l7policy
        :param l7policy_id:
        :return:
        """
        try:
            l7policy = self._api.l7policy_show(l7policy_id=l7policy_id)
            return self.resource_class(self, info=l7policy)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_l7policies(self, **kwargs):
        """Get l7policy
        :param kwargs:
        :return:
        """
        try:
            l7policies = self._api.l7policy_list(**kwargs)
            return self.resource_class(self, info=l7policies['l7policies'])
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_l7rule(self, l7rule_id, l7policy_id, **kwargs):
        """
        :param l7rule_id:
        :param l7policy_id
        :param kwargs:
        :return:
        """
        try:
            data = self._api.l7rule_show(l7rule_id=l7rule_id, l7policy_id=l7policy_id, *kwargs)
            return self.resource_class(self, info=data)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_l7rules(self, l7policy_id, **kwargs):
        """
        :param l7policy_id:
        :param kwargs:
        :return:
        """
        try:
            data = self._api.l7rule_list(l7policy_id=l7policy_id, **kwargs)
            return self.resource_class(self, info=data['rules'])
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def list_providers(self):
        """
        Lists all enabled provider drivers.
        :param kwargs:
        :return:
        """
        try:
            data = self._api.provider_list()
            return self.resource_class(self, info=data['providers'])
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def get_flavor(self, flavor_id):
        """Get a flavor being created
        :param flavor_id:
        :return:
        """
        try:
            data = self._api.flavor_show(flavor_id=flavor_id)
        except oct_exc.OctaviaClientException as e:
            data = {}
        return self.resource_class(self, info=data)

    def list_flavors(self, **kwargs):
        """
        List all available flavors.
        :param kwargs:
        :return:
        """
        try:
            data = self._api.flavor_list(**kwargs)
        except oct_exc.OctaviaClientException as e:
            data = []
        return self.resource_class(self, info=data)

    def get_availability_zone(self, availability_zone_name):
        """
        Get an availability zone. being created
        :param availability_zone_name:
        :return:
        """
        try:
            data = self._api.availabilityzone_show(availabilityzone_name=availability_zone_name)
        except oct_exc.OctaviaClientException as e:
            data = {}
        return self.resource_class(self, info=data)

    def list_availability_zones(self, **kwargs):
        """
        List all available availability zones.
        :param kwargs:
        :return:
        """
        try:
            data = self._api.availabilityzone_list(**kwargs)
        except oct_exc.OctaviaClientException as e:
            data = []
        return self.resource_class(self, info=data)

    # **********************************************
    #   Create a new openstack resource
    # **********************************************
    def create_allinone(self, info):
        """
        Create a new lbaas
        :param info:
        :return:
        """
        data = self._api.create_allinone(info=info)
        return self.resource_class(self, info=data)

    def create_lb(self, name, description, subnet_id=None, **kwargs):
        """
        Create a new lb
        :param name:
        :param description:
        :param subnet_id:
        :param kwargs:
        :return:
        """
        data = self._api.create_lb(name=name, description=description,
                                   subnet_id=subnet_id, **kwargs)
        return self.resource_class(self, info=data)

    def create_listener(self, name, description, protocol, port, lb_id, wait=False, **kwargs):
        """

        :param name:
        :param description:
        :param protocol:
        :param port:
        :param lb_id:
        :param wait:
        :param kwargs:
        :return:
        """
        data = self._api.create_listener(name=name, description=description,
                                         protocol=protocol, port=port,
                                         lb_id=lb_id, wait=wait, **kwargs)
        return self.resource_class(self, info=data)

    def create_pool(self, name, description, listener_id, lb_id, alg='ROUND_ROBIN',
                    protocol='HTTP', wait=False, **kwargs):
        """
        Create a new pool
        :param name:
        :param description:
        :param listener_id:
        :param lb_id:
        :param alg:
        :param protocol:
        :param wait:
        :param kwargs:
        :return:
        """
        data = self._api.create_pool(name=name, description=description,
                                     listener_id=listener_id, alg=alg,
                                     protocol=protocol, lb_id=lb_id,
                                     wait=wait, **kwargs)
        return self.resource_class(self, info=data)

    def add_member(self, name, pool_id, address, port, weight=1, **kwargs):
        """
        Add member to pool
        :param name:
        :param pool_id:
        :param address:
        :param port:
        :param weight:
        :param kwargs:
        :return:
        """
        data = self._api.add_member(name=name, pool_id=pool_id,
                                    address=address, port=port,
                                    weight=weight, **kwargs)
        return self.resource_class(self, info=data)

    def create_health_monitor(self, name, pool_id, delay, timeout, type='HTTP',
                              http_method='GET', max_retries=10, max_retries_down=10,
                              url_path='/', wait=False, **kwargs):
        """
        Create a new health monitor
        :param name:
        :param pool_id:
        :param delay:
        :param timeout:
        :param type:
        :param http_method:
        :param max_retries:
        :param max_retries_down:
        :param url_path:
        :param wait:
        :param kwargs:
        :return:
        """
        data = self._api.create_monitor(name=name, pool_id=pool_id, delay=delay, timeout=timeout, type=type,
                                        http_method=http_method, max_retries=max_retries,
                                        max_retries_down=max_retries_down,
                                        url_path=url_path, wait=wait, **kwargs)
        return self.resource_class(self, info=data)

    def create_l7policy(self, name, description, action, listener_id, wait=False, **kwargs):
        """

        :param name:
        :param description:
        :param action:
        :param listener_id:
        :param wait:
        :param kwargs:
        :return:
        """
        data = self._api.create_l7policy(name=name, description=description, action=action,
                                         listener_id=listener_id, wait=wait, **kwargs)
        return self.resource_class(self, info=data)

    def create_l7rule(self, l7policy_id, compare_type, type, value, invert=False, wait=False, **kwargs):
        """

        :param l7policy_id:
        :param compare_type:
        :param type:
        :param value:
        :param invert:
        :param wait:
        :param kwargs:
        :return:
        """
        data = self._api.create_l7rule(l7policy_id=l7policy_id, compare_type=compare_type, type=type,
                                       value=value, wait=wait, invert=invert, **kwargs)
        return self.resource_class(self, info=data)

    # **********************************************
    #   Update an openstack resource being created
    # **********************************************

    @valid_kwargs('name', 'description', 'qos_policy_id', 'tags', 'admin_state_up')
    def update_lb(self, lb_id, **kwargs):
        """
        :param lb_id:
        :param kwargs:
        :return:
        """
        data = self._api.update_lb(lb_id, **kwargs)
        return self.resource_class(self, info=data['loadbalancer'])

    def trigger_failover_lb(self, lb_id):
        """
        Trigger load balancer failover
        :param lb_id:
        :return:
        """
        data = self._api.trigger_failover_lb(lb_id)
        return self.resource_class(self, info=data)

    @valid_kwargs('name', 'description', 'connection_limit', 'tags', 'admin_state_up',
                  'allowed_cidrs')
    def update_listener(self, listener_id, **kwargs):
        """
        Update a listener being created.
        :param listener_id:
        :param kwargs:
        :return:
        """
        data = self._api.update_listener(listener_id=listener_id, **kwargs)
        return self.resource_class(self, info=data['listener'])

    @valid_kwargs('name', 'description', 'lb_algorithm', 'session_persistence', 'tags',
                  'admin_state_up')
    def update_pool(self, pool_id, **kwargs):
        """
        Update a pool being created.
        :param pool_id:
        :param kwargs:
        :return:
        """
        if 'session_persistence' in kwargs:
            session_persistence = kwargs['session_persistence']
            kwargs['session_persistence'] = {
                'type': session_persistence
            }
            if session_persistence == 'APP_COOKIE':
                kwargs['session_persistence']['cookie_name'] = uuid.uuid4().hex
        data = self._api.update_pool(pool_id=pool_id, **kwargs)
        return self.resource_class(self, info=data)

    @valid_kwargs('name', 'backup', 'monitor_address', 'monitor_port', 'weight',
                  'tags', 'admin_state_up')
    def update_member(self, pool_id, member_id, **kwargs):
        """
        Update a member being created.
        :param pool_id:
        :param member_id:
        :param kwargs:fdd
        :return:
        """
        data = self._api.update_member(pool_id=pool_id, member_id=member_id, **kwargs)
        return self.resource_class(self, info=data)

    @valid_kwargs('name', 'delay', 'expected_codes', 'http_method', 'url_path',
                  'tags', 'admin_state_up', 'timeout', 'max_retries_down', 'max_retries')
    def update_health_monitor(self, health_monitor_id, **kwargs):
        """
        Update an existing health monitor.
        :param health_monitor_id:
        :param kwargs:
        :return:
        """
        data = self._api.update_health_monitor(health_monitor_id=health_monitor_id, **kwargs)
        return self.resource_class(self, info=data)

    @valid_kwargs('name', 'description', 'action', 'redirect_http_code', 'redirect_pool_id',
                  'redirect_prefix', 'tags', 'admin_state_up')
    def update_l7policy(self, l7policy_id, **kwargs):
        """
        Update a l7policy being created.
        :param l7policy_id:
        :param kwargs:
        :return:
        """
        data = self._api.update_l7policy(l7policy_id=l7policy_id, **kwargs)
        return self.resource_class(self, info=data)

    @valid_kwargs('compare_type', 'invert', 'key', 'type', 'value', 'tags', 'admin_state_up')
    def update_l7rule(self, l7policy_id, l7rule_id, **kwargs):
        """
        Update a l7rule being created.
        :param l7policy_id:
        :param l7rule_id:
        :param kwargs:
        :return:
        """
        data = self._api.update_l7rule(l7policy_id=l7policy_id, l7rule_id=l7rule_id, **kwargs)
        return self.resource_class(self, info=data)

    # **********************************************
    #   Delete an openstack resource being created
    # **********************************************

    def delete_lb(self, lb_id):
        """
        Delete a load balancer being created.
        :param lb_id:
        :return:
        """
        data = self._api.delete_lb(lb_id)
        if data.status_code in [200, 204]:
            return self.resource_class(self, info=True)
        else:
            message = data.text
            raise fox_exc.FoxCloudBadRequest(message=message)

    def delete_listener(self, listener_id):
        """
        Delete a listener being created.
        :param listener_id:
        :return:
        """
        data = self._api.delete_listener(listener_id)
        if data.status_code in [200, 204]:
            return self.resource_class(self, info=True)
        else:
            message = data.text
            raise fox_exc.FoxCloudBadRequest(message=message)

    def delete_pool(self, pool_id):
        """
        Delete a pool being created.
        :param pool_id:
        :return:
        """
        data = self._api.delete_pool(pool_id)
        if data.status_code in [200, 204]:
            return self.resource_class(self, info=True)
        else:
            message = data.text
            raise fox_exc.FoxCloudBadRequest(message=message)

    def remove_member(self, pool_id, member_id):
        """
        Removes a member and its associated configuration from the pool.
        :param pool_id:
        :param member_id:
        :return:
        """
        data = self._api.remove_member(pool_id, member_id)
        if data.status_code in [200, 204]:
            return self.resource_class(self, info=True)
        else:
            message = data.text
            raise fox_exc.FoxCloudBadRequest(message=message)

    def delete_health_monitor(self, health_monitor_id):
        """
        Removes a health monitor and its associated configuration from the project.
        :param health_monitor_id:
        :return:
        """
        data = self._api.delete_health_monitor(health_monitor_id)
        if data.status_code in [200, 204]:
            return self.resource_class(self, info=True)
        else:
            message = data.text
            raise fox_exc.FoxCloudBadRequest(message=message)

    def delete_l7policy(self, l7policy_id):
        """
        Removes a L7 policy and its associated configuration from the project.
        :param l7policy_id:
        :return:
        """
        data = self._api.delete_l7policy(l7policy_id)
        if data.status_code in [200, 204]:
            return self.resource_class(self, info=True)
        else:
            message = data.text
            raise fox_exc.FoxCloudBadRequest(message=message)

    def delete_l7rule(self, l7rule_id, l7policy_id):
        """
        Removes a L7 rule and its associated configuration from the project.
        :param l7rule_id:
        :param l7policy_id:
        :return:
        """
        data = self._api.delete_l7rule(l7rule_id, l7policy_id)
        if data.status_code in [200, 204]:
            return self.resource_class(self, info=True)
        else:
            message = data.text
            raise fox_exc.FoxCloudBadRequest(message=message)
