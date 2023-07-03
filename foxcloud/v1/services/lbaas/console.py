#
# Copyright (c) 2020 FTI-CAS
#

import time
import uuid

from octaviaclient.api import exceptions as oct_exc

from foxcloud import exceptions as fox_exc
from foxcloud.i18n import _
from foxcloud.v1.services.lbaas.base import BaseLbaas
from foxcloud.v1.utils.data_util import valid_kwargs


class Console(BaseLbaas):
    __engine_type__ = 'console'
    PROVISION_STATUS = {
        'ACTIVE': 'ACTIVE',
        'PENDING_CREATE': 'PENDING_CREATE',
        'ERROR': 'ERROR'
    }

    # **********************************************
    #   Create an openstack resource
    # **********************************************
    def create_allinone(self, info):
        """
        Deploy a new load balancer
        :param info:
        :return:
        """
        result = {}
        lb_info = info.get('lb')
        lb = {}
        if lb_info:
            data = self.create_lb(name=lb_info.pop('name', None),
                                  description=lb_info.pop('description', None),
                                  subnet_id=lb_info.pop('vip_subnet'), **lb_info)
            lb = data['loadbalancer']
        error = lb.get('error')
        if error:
            raise fox_exc.FoxCloudException(error)

        if not self._wait_task(lb['id']):
            raise fox_exc.FoxCloudException('Timeout while doing task')

        result.update({'lb': lb})
        listener_info = info.get('listener')
        listener = {}
        if listener_info:
            data = self.create_listener(name=listener_info.pop('name', None),
                                        description=listener_info.pop('description', None),
                                        protocol=listener_info.pop('protocol'),
                                        port=listener_info.pop('port'),
                                        lb_id=lb['id'])
            listener = data['listener']
        error = listener.get('error')
        if error:
            self.delete_lb(lb_id=lb['id'])
            raise fox_exc.FoxCloudException(error)

        if not self._wait_task(listener['id'], type='listener'):
            self.delete_lb(lb_id=listener['id'])
            raise fox_exc.FoxCloudException('Timeout while doing task')

        result.update({'listener': listener})
        pool_info = info.get('pool')
        pool = {}
        if pool_info:
            data = self.create_pool(name=listener_info.pop('name', None),
                                    description=pool_info.pop('description', None),
                                    listener_id=listener['id'], lb_id=lb['id'],
                                    alg=pool_info.pop('alg'), protocol=pool_info.pop('protocol'),
                                    **pool_info)
            pool = data['pool']
        error = pool.get('error')
        if error:
            self.delete_lb(lb_id=lb['id'])
            self.delete_listener(listener['id'])
            raise fox_exc.FoxCloudException(error)

        if not self._wait_task(pool['id'], type='pool'):
            self.delete_lb(lb_id=lb['id'])
            self.delete_listener(listener['id'])
            raise fox_exc.FoxCloudException('Timeout while doing task')

        result.update({'pool': pool})
        pool_members = info.get('members')
        if pool_members:
            for member in pool_members:
                poll_member = self.add_member(name=member.pop('name', None), pool_id=pool['id'],
                                              address=member.pop('address'), port=member.pop('port'),
                                              weight=member.pop('weight', 1), **member)
                error = poll_member.get('error')
                if error:
                    self.delete_lb(lb_id=lb['id'])
                    self.delete_listener(listener['id'])
                    self.delete_pool(pool['id'])
                    raise fox_exc.FoxCloudException(error)

        monitor_info = info.get('pool_monitor')
        monitor = {}
        if monitor_info and pool:
            monitor = self.create_monitor(name=monitor_info.pop('name', None), pool_id=pool['id'],
                                          delay=monitor_info.pop('name', 2),
                                          timeout=monitor_info.pop('name', 10),
                                          type=monitor_info.pop('name', 'HTTP'),
                                          http_method=monitor_info.pop('http_method', 'GET'),
                                          max_retries=monitor_info.pop('max_retries', 10),
                                          max_retries_down=monitor_info.pop('max_retries_down', 10),
                                          url_path=monitor_info.pop('url_path', '/'))

        error = monitor.get('error')
        if error:
            self.delete_lb(lb_id=lb['id'])
            self.delete_listener(listener['id'])
            self.delete_pool(pool['id'])
            raise fox_exc.FoxCloudException(error)
        result.update({'pool_monitor': monitor})

        l7policy_info = info.get('l7policy')
        l7policy = {}
        if l7policy_info and listener:
            l7policy = self.create_l7policy(name=l7policy_info.pop('name', None),
                                            description=l7policy_info.pop('description', None),
                                            action=l7policy_info.pop('action'),
                                            listener_id=listener['id'], **l7policy_info)
        error = l7policy.get('error')
        if error:
            self.delete_lb(lb_id=lb['id'])
            self.delete_listener(listener['id'])
            self.delete_pool(pool['id'])
            self.delete_health_monitor(monitor['id'])
            raise fox_exc.FoxCloudException(error)
        result.update({'l7policy': l7policy})

        l7rules = info.get('l7rules') or []
        if l7rules and l7policy:
            for rule in l7rules:
                l7_rule = self.create_l7rule(l7policy_id=l7policy['id'],
                                             compare_type=rule.pop('compare_type'),
                                             type=rule.pop('type'),
                                             value=rule.pop('value'), **rule)
                error = l7_rule.get('error')
                if error:
                    self.delete_lb(lb_id=lb['id'])
                    self.delete_listener(listener['id'])
                    self.delete_pool(pool['id'])
                    self.delete_health_monitor(monitor['id'])
                    self.delete_l7policy(l7policy['id'])
                    raise fox_exc.FoxCloudException(error)
        return result

    def _wait_task(self, resource_id, type='load_balancer', timeout=3600, interval=5, **kw):
        """
        Check done task
        :param resource_id:
        :param type:
        :param timeout:
        :param interval:
        :return:
        """
        func_call = getattr(self, '{}_show'.format(type))
        while timeout >= 0:
            data = func_call(resource_id, **kw)
            if data.get('provisioning_status') == self.PROVISION_STATUS['ACTIVE']:
                return True
            if data.get('provisioning_status') == self.PROVISION_STATUS['ERROR']:
                return False
            timeout -= interval
            time.sleep(interval)
        return False

    @valid_kwargs('availability_zone', 'flavor_id', 'provider', 'tags',
                  'vip_network_id', 'vip_address')
    def create_lb(self, name, description,  subnet_id=None, wait=False, **kwargs):
        """
        Create a new load balancer.
        :param name:
        :param description:
        :param subnet_id:
        :param wait:
        :param kwargs:
        :return:
        """
        params = {
            'name': name,
            'description': description,
            'vip_subnet_id': subnet_id,
        }
        params.update(**kwargs)

        try:
            data = self.load_balancer_create(json={'loadbalancer': params})
            lb = data['loadbalancer']
            if wait:
                self._wait_task(resource_id=lb['id'], type='load_balancer')
            return lb
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('connection_limit', 'l7policies', 'timeout_client_data',
                  'timeout_member_connect', 'timeout_member_data', 'timeout_tcp_inspect',
                  'tags', 'default_tls_container_ref', 'tls_ciphers', 'tls_versions')
    def create_listener(self, name, description, protocol, port,  lb_id, wait=False, **kwargs):
        """
        Create a new listener.
        :param name:
        :param description:
        :param protocol:
        :param port:
        :param lb_id:
        :param wait
        :param kwargs:
        :return:
        """
        params = {
            'name': name,
            'description': description,
            'protocol': protocol,
            'protocol_port': port,
            'loadbalancer_id': lb_id,
        }
        params.update(**kwargs)

        try:
            data = self.listener_create(json={'listener': params})
            listener = data['listener']
            if wait:
                self._wait_task(resource_id=listener['id'], type='listener')
            return listener
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('session_persistence', 'tags', 'tls_enabled', 'tls_ciphers',
                  'tls_container_ref', 'tls_versions')
    def create_pool(self, name, description, listener_id, lb_id, alg='ROUND_ROBIN',
                    protocol='HTTP', wait=False, **kwargs):
        """
        Create a pool.
        :param name:
        :param description:
        :param listener_id:
        :param alg: [EAST_CONNECTIONS, ROUND_ROBIN, SOURCE_IP, or SOURCE_IP_PORT]
        :param protocol: [HTTP, HTTPS, PROXY, TCP, or UDP]
        :param lb_id:
        :param wait:
        :param kwargs:
        session_persistence: [APP_COOKIE, HTTP_COOKIE, SOURCE_IP]
        :return:
        """
        params = {
            'name': name,
            'description': description,
            'protocol': protocol,
            'listener_id': listener_id,
            'loadbalancer_id': lb_id,
            'lb_algorithm': alg,
        }
        session_persistence = kwargs.pop('session_persistence', None)
        if session_persistence:
            params['session_persistence'] = {
                "type": session_persistence
            }
            if session_persistence == 'APP_COOKIE':
                params['cookie_name'] = uuid.uuid4().hex
        params.update(**kwargs)

        try:
            data = self.pool_create(json={'pool': params})
            pool = data['pool']
            if wait:
                self._wait_task(resource_id=pool['id'], type='pool')
            return pool
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('tags', 'backup', 'subnet_id', 'monitor_address', 'monitor_port',
                  'admin_state_up')
    def add_member(self, name, pool_id, address, port, weight=1, wait=False, **kwargs):
        """
        Add new member to a specific pool being created
        :param name:
        :param pool_id:
        :param address:
        :param port:
        :param weight:
        :param wait:
        :param kwargs:
        :return:
        """
        params = {
            'name': name,
            'address': address,
            'protocol_port': port,
            'weight': weight,
        }
        params.update(**kwargs)

        try:
            data = self.member_create(json={'member': params}, pool_id=pool_id)
            member = data['member']
            if wait:
                self._wait_task(resource_id=pool_id, type='member', member_id=member['id'])
            return member
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('tags', 'expected_codes', 'admin_state_up')
    def create_monitor(self, name, pool_id, delay, timeout, type='HTTP',
                       http_method='GET', max_retries=10, max_retries_down=10,
                       url_path='/', wait=False, **kwargs):
        """
        Create a new monitor
        :param pool_id:
        :param delay:
        :param timeout:
        :param type: [ HTTP, HTTPS, PING, TCP, TLS-HELLO, UDP-CONNECT]
        :param name:
        :param http_method: [CONNECT, DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT, TRACE]
        :param max_retries:
        :param max_retries_down:
        :param url_path:
        :param wait:
        :param kwargs:
        :return:
        """
        params = {
            'name': name,
            'pool_id': pool_id,
            'delay': delay,
            'max_retries': max_retries or 10,
            'max_retries_down': max_retries_down or 10,
            'timeout': timeout,
            'url_path': url_path,
            'http_method': http_method,
            'type': type,
        }
        params.update(**kwargs)

        try:
            data = self.health_monitor_create(json={'healthmonitor': params})
            monitor = data['healthmonitor']
            if wait:
                self._wait_task(resource_id=monitor['id'], type='health_monitor')
            return monitor
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('position', 'redirect_http_code', 'redirect_pool_id',
                  'redirect_prefix', 'redirect_url', 'tags', 'admin_state_up')
    def create_l7policy(self, name, description, action, listener_id, wait=False, **kwargs):
        """Create a l7policy
        :param action: [REDIRECT_PREFIX, REDIRECT_TO_POOL, REDIRECT_TO_URL, REJECT]
        :param listener_id:
        :param name:
        :param description:
        :param kwargs:
        :return:
        """

        params = {
            'name': name,
            'description': description,
            'action': action,
            'listener_id': listener_id,
        }
        params.update(**kwargs)

        try:
            data = self.l7policy_create(json={'l7policy': params})
            l7policy = data['l7policy']
            if wait:
                self._wait_task(resource_id=l7policy['id'], type='l7policy')
            return l7policy
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    @valid_kwargs('key', 'tags', 'admin_state_up')
    def create_l7rule(self, l7policy_id, compare_type, type,
                      value, invert=False, wait=False, **kwargs):
        """
        Creates a L7 rule.
        :param l7policy_id: The ID of the L7 policy to query.
        :param compare_type: The comparison type for the L7 rule. One of CONTAINS,
        ENDS_WITH, EQUAL_TO, REGEX, or STARTS_WITH.
        :param type: The L7 rule type. One of COOKIE, FILE_TYPE, HEADER, HOST_NAME, PATH,
        SSL_CONN_HAS_CERT, SSL_VERIFY_RESULT, or SSL_DN_FIELD.
        :param value: The value to use for the comparison. For example, the file type to
        compare.
        :param invert:
        :param wait:
        :param kwargs:
        :return:
        """
        params = {
            'compare_type': compare_type,
            'type': type,
            'value': value,
            'invert': invert,
        }
        params.update(**kwargs)

        try:
            data = self.l7rule_create(l7policy_id=l7policy_id, json={'rule': params})
            l7rule = data['rule']
            if wait:
                self._wait_task(resource_id=l7rule['id'], type='l7rule', l7policy_id=l7policy_id)
            return l7rule
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    # **********************************************
    #   Update an openstack resource being created
    # **********************************************

    def update_lb(self, lb_id, **kwargs):
        """
        Delete a load balancer being created.
        :param lb_id:
        :param kwargs:
        :return:
        """
        try:
            return self.load_balancer_set(lb_id=lb_id, json={'loadbalancer': kwargs})
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def trigger_failover_lb(self, lb_id):
        """
        Trigger load balancer failover
        :param lb_id:
        :return:
        """
        try:
            return self.load_balancer_failover(lb_id=lb_id)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_listener(self, listener_id, **kwargs):
        """
        Update a listener being created.
        :param listener_id:
        :param kwargs:
        :return:
        """
        try:
            return self.listener_set(listener_id=listener_id, json={'listener': kwargs})
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_pool(self, pool_id, **kwargs):
        """
        Update a pool being created.
        :param pool_id:
        :param kwargs:
        :return:
        """
        try:
            return self.pool_set(pool_id=pool_id, json={'pool': kwargs})
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_member(self, pool_id, member_id, **kwargs):
        """
        Update a member being created.
        :param pool_id:
        :param member_id:
        :param kwargs:
        :return:
        """
        try:
            return self.member_set(pool_id=pool_id, member_id=member_id,
                                   json={'member': kwargs})
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_health_monitor(self, health_monitor_id, **kwargs):
        """
        Update a member being created.
        :param health_monitor_id:
        :param kwargs:
        :return:
        """
        try:
            return self.health_monitor_set(health_monitor_id=health_monitor_id,
                                           json={'member': kwargs})
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_l7policy(self, l7policy_id, **kwargs):
        """
        Update a l7policy being created.
        :param l7policy_id:
        :param kwargs:
        :return:
        """
        try:
            return self.l7policy_set(l7policy_id=l7policy_id, json={'l7policy': kwargs})
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def update_l7rule(self, l7policy_id, l7rule_id, **kwargs):
        """
        Update a l7rule being created.
        :param l7policy_id:
        :param l7rule_id:
        :param kwargs:
        :return:
        """
        try:
            return self.l7rule_set(l7policy_id=l7policy_id, l7rule_id=l7rule_id, json={'rule': kwargs})
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    # **********************************************
    #   Delete an openstack resource being created
    # **********************************************
    def delete_lb(self, lb_id):
        """
        Delete a load balancer being created.
        :param lb_id:
        :return:
        """
        try:
            return self.load_balancer_delete(lb_id=lb_id)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_listener(self, listener_id):
        """
        Delete a listener being created.
        :param listener_id:
        :return:
        """
        try:
            return self.listener_delete(listener_id=listener_id)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_pool(self, pool_id):
        """
        Delete a pool being created.
        :param pool_id:
        :return:
        """
        try:
            return self.pool_delete(pool_id=pool_id)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def remove_member(self, pool_id, member_id):
        """
        Removes a member and its associated configuration from the pool.
        :param pool_id:
        :param member_id:
        :return:
        """
        try:
            return self.member_delete(pool_id, member_id)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_health_monitor(self, health_monitor_id):
        """
        Removes a health monitor and its associated configuration from the project.
        :param health_monitor_id:
        :return:
        """
        try:
            return self.health_monitor_delete(health_monitor_id)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_l7policy(self, l7policy_id):
        """
        Removes a L7 policy and its associated configuration from the project.
        :param l7policy_id:
        :return:
        """
        try:
            return self.l7policy_delete(l7policy_id)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)

    def delete_l7rule(self, l7rule_id, l7policy_id):
        """
        Removes a L7 rule and its associated configuration from the project.
        :param l7rule_id:
        :param l7policy_id:
        :return:
        """
        try:
            return self.l7rule_delete(l7rule_id, l7policy_id)
        except oct_exc.OctaviaClientException as e:
            raise fox_exc.FoxCloudException(e)
