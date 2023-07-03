import collections
import time

from foxcloud import exceptions as fox_exc
from foxcloud.v1.services.stack.orchestrator import heat
from foxcloud.v1.services.shade.heat import model as md
from foxcloud.v1.utils.data_util import valid_kwargs
from foxcloud.v1.utils import constants as consts, str_util


class LbaasHeatTemplate(heat.HeatTemplate):
    def __init__(self, name, template_file=None, heat_parameters=None, session=None):
        super(LbaasHeatTemplate, self).__init__(name, template_file, heat_parameters, session)

    @valid_kwargs('admin_state_up', 'expected_codes', 'http_method', 'url_path')
    def add_monitor(self, name, pool, delay, max_entries, timeout, type, **kwargs):
        """
        Add new monitor
        :param name:
        :param pool:
        :param delay:
        :param max_entries:
        :param timeout:
        :param type:  “PING”, “TCP”, “HTTP”, “HTTPS”, “UDP-CONNECT”
        :param kwargs:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Octavia::HealthMonitor',
            'depends_on': [pool],
            'properties': {
                'delay': delay,
                'max_retries': max_entries,
                'pool': {'get_resource': pool},
                'timeout': timeout,
                'type': type
            }
        }

        optional_properties = {}
        admin_state_up = kwargs.get('admin_state_up')
        if admin_state_up:
            assert isinstance(admin_state_up, bool)
            optional_properties['admin_state_up'] = admin_state_up

        expected_codes = kwargs.get('expected_codes')
        if expected_codes:
            optional_properties['expected_codes'] = expected_codes

        http_method = kwargs.get('http_method')
        if http_method:
            optional_properties['http_method'] = http_method

        url_path = kwargs.get('url_path')
        if url_path:
            optional_properties['url_path'] = url_path

        self._template['outputs'][name] = {
            'description': 'Monitor %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [name, 'show']}
        }
        self.resources[name]['properties'].update(optional_properties)

    @valid_kwargs('admin_state_up', 'monitor_address', 'monitor_port', 'subnet',
                  'tags', 'weight')
    def add_pool_member(self, name, address, pool, port, weight=1, **kwargs):
        """
        Add a new pool member
        :param name:
        :param address:
        :param pool:
        :param port:
        :param weight:
        :param kwargs:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Octavia::PoolMember',
            'properties': {
                'address': address,  # a descriptive name
                'pool': {'get_resource': pool},
                'protocol_port': port,
            }
        }
        optional_properties = {}
        admin_state_up = kwargs.get('admin_state_up')
        if admin_state_up:
            assert isinstance(admin_state_up, bool)
            optional_properties['admin_state_up'] = admin_state_up

        monitor_address = kwargs.get('monitor_address')
        if monitor_address:
            optional_properties['monitor_address'] = monitor_address

        monitor_port = kwargs.get('monitor_port')
        if monitor_port:
            optional_properties['monitor_port'] = monitor_port

        subnet = kwargs.get('subnet')
        if subnet:
            optional_properties['subnet'] = subnet

        tags = kwargs.get('tags')
        if tags:
            optional_properties['tags'] = tags

        if weight:
            optional_properties['weight'] = weight

        self._template['outputs'][name] = {
            'description': 'Monitor %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [name, 'show']}
        }

        self.resources[name]['properties'].update(optional_properties)

    @valid_kwargs('lb', 'tls_enabled')
    def add_pool(self, name, description, alg, protocol, listener=None, **kwargs):
        """

        :param name:
        :param alg:
        :param protocol:
        :param description
        :param listener
        :param kwargs:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Octavia::Pool',
            'depends_on': [],
            'properties': {
                'name': name,  # a descriptive name
                'protocol': protocol,
                'lb_algorithm': alg,
                'description': description,
            }
        }
        optional_properties = {}
        if listener:
            optional_properties['listener'] = {
                'get_resource': listener,
            }
            self.resources[name]['depends_on'].append(listener)

        admin_state_up = kwargs.get('admin_state_up')
        if admin_state_up:
            assert isinstance(admin_state_up, bool)
            optional_properties['admin_state_up'] = admin_state_up

        session_persistence = kwargs.get('session_persistence')
        if session_persistence:
            optional_properties['session_persistence'] = session_persistence

        lb = kwargs.get('lb')
        if lb:
            optional_properties['loadbalancer'] = {
                'get_resource': lb
            }
            self.resources[name]['depends_on'].append(lb)

        tls_enabled = kwargs.get('tls_enabled')
        if tls_enabled:
            optional_properties['tls_enabled'] = tls_enabled

        self._template['outputs'][name] = {
            'description': 'Pool %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [name, 'show']}
        }

        self.resources[name]['properties'].update(optional_properties)

    @valid_kwargs('admin_state_up', 'cidrs', 'connection_limit', 'default_pool',
                  'default_tls_container_ref')
    def add_listener(self, name, description, protocol, port, lb=None, ssl=None, **kwargs):
        """
        A resource for managing octavia Listeners.
        :param name:
        :param protocol:  “TCP”, “HTTP”, “HTTPS”, “TERMINATED_HTTPS”, “PROXY”, “UDP”
        :param port: The value must be in the range 1 to 65535.
        :param description
        :param lb
        :param ssl
        :param kwargs:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Octavia::Listener',
            'depends_on': [],
            'properties': {
                'name': name,  # a descriptive name
                'protocol': protocol,
                'protocol_port': port,
                'description': description,
            }
        }
        optional_properties = {}
        if lb:
            optional_properties['loadbalancer'] = {
                'get_resource': lb,
            }
            self.resources[name]['depends_on'].append(lb)

        if ssl:
            optional_properties['default_tls_container_ref'] = {
                'get_resource': ssl,
            }
            self.resources[name]['depends_on'].append(ssl)

        admin_state_up = kwargs.get('admin_state_up')
        if admin_state_up:
            assert isinstance(admin_state_up, bool)
            optional_properties['admin_state_up'] = admin_state_up

        allowed_cidrs = kwargs.get('cidrs')
        if allowed_cidrs:
            optional_properties['expected_codes'] = allowed_cidrs

        default_pool = kwargs.get('default_pool')
        if default_pool:
            optional_properties['default_pool'] = default_pool

        allowed_cidrs = kwargs.get('allowed_cidrs')
        if allowed_cidrs:
            optional_properties['expected_codes'] = allowed_cidrs

        default_tls_container_ref = kwargs.get('default_tls_container_ref')
        if default_tls_container_ref:
            optional_properties['default_tls_container_ref'] = default_tls_container_ref

        connection_limit = kwargs.get('connection_limit')
        if connection_limit:
            optional_properties['connection_limit'] = connection_limit

        self._template['outputs'][name] = {
            'description': 'Listener %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [name, 'show']}
        }

        self.resources[name]['properties'].update(optional_properties)

    def add_ssl(self, name, crt, key, payload_content_type, secret_type):
        """
        Add SSL
        :param name:
        :param crt:
        :param key:
        :param payload_content_type:
        :param secret_type:
        :return:
        """
        cert_name = str_util.h_join(name, "certificate")
        self.resources[cert_name] = {
            'type': 'OS::Barbican::Secret',
            'properties': {
                'name': cert_name,  # a descriptive name
                'payload': crt,
                'payload_content_type': payload_content_type,
                'secret_type': secret_type,
            }
        }

        int_name = str_util.h_join(name, "intermediates")
        self.resources[int_name] = {
            'type': 'OS::Barbican::Secret',
            'properties': {
                'name': int_name,  # a descriptive name
                'payload': crt,
                'payload_content_type': payload_content_type,
                'secret_type': secret_type,
            }
        }

        priv_name = str_util.h_join(name, "private_key")
        self.resources[int_name] = {
            'type': 'OS::Barbican::Secret',
            'properties': {
                'name': priv_name,  # a descriptive name
                'payload': key,
                'payload_content_type': payload_content_type,
                'secret_type': secret_type,
            }
        }

        container_name = name
        self.resources[container_name] = {
            'type': 'OS::Barbican::CertificateContainer',
            'depends_on': [cert_name, int_name, priv_name],
            'properties': {
                'certificate_ref': {'get_resource': cert_name},  # a descriptive name
                'intermediates_ref': {'get_resource': int_name},
                'private_key_ref': {'get_resource': priv_name},
            }
        }
        self._template['outputs'][container_name] = {
            'description': 'Cert Container %s ID' % container_name,
            'value': {'get_resource': container_name}
        }
        self._template['outputs'][container_name + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [container_name, 'show']}
        }

    @valid_kwargs('admin_state_up', 'flavor', 'vip_address', 'provider')
    def add_lb(self, name, description, vip_subnet, **kwargs):
        """
        A resource for creating octavia Load Balancers.
        :param name:
        :param description:
        :param vip_subnet:
        :param kwargs:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Octavia::LoadBalancer',
            'properties': {
                'name': name,  # a descriptive name
                'vip_subnet': vip_subnet,
                'description': description,
            }
        }
        optional_properties = {}
        admin_state_up = kwargs.get('admin_state_up')
        if admin_state_up:
            assert isinstance(admin_state_up, bool)
            optional_properties['admin_state_up'] = admin_state_up

        flavor = kwargs.get('flavor')
        if flavor:
            optional_properties['flavor'] = flavor

        provider = kwargs.get('provider')
        if provider:
            optional_properties['provider'] = provider

        vip_address = kwargs.get('vip_address')
        if vip_address:
            optional_properties['vip_address'] = vip_address

        self._template['outputs'][name] = {
            'description': 'LB %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + '-vip_address'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [name, 'vip_address']}
        }
        self._template['outputs'][name + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [name, 'show']}
        }

        self.resources[name]['properties'].update(optional_properties)

    @valid_kwargs('admin_state_up', 'position', 'redirect_pool', 'redirect_url')
    def add_l7policy(self, name, description, action, listener, **kwargs):
        """
        Add new L7 policy
        :param name:
        :param description:
        :param action:
        :param listener:
        :param kwargs:
        :return:
        """
        self.resources[name] = {
            'type': 'OS::Octavia::L7Policy',
            'properties': {
                'name': name,  # a descriptive name
                'depends_on': [listener],
                'action': action,
                'description': description,
                'listener': {'get_resource': listener},
            }
        }
        optional_properties = {}
        admin_state_up = kwargs.get('admin_state_up')
        if admin_state_up:
            assert isinstance(admin_state_up, bool)
            optional_properties['admin_state_up'] = admin_state_up

        position = kwargs.get('position')
        if position:
            optional_properties['position'] = position

        redirect_pool = kwargs.get('redirect_pool')
        if redirect_pool:
            optional_properties['redirect_pool'] = redirect_pool

        redirect_url = kwargs.get('redirect_url')
        if redirect_url:
            optional_properties['redirect_url'] = redirect_url

        self._template['outputs'][name] = {
            'description': 'L7Policy %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [name, 'show']}
        }

    @valid_kwargs('admin_state_up', 'invert', 'key')
    def add_l7rule(self, name, compare_type, l7policy, type, value, **kwargs):
        self.resources[name] = {
            'type': 'OS::Octavia::L7Rule',
            'depends_on': [l7policy],
            'properties': {
                'compare_type': compare_type,  # a descriptive name
                'l7policy': {'get_resource': l7policy},
                'type': type,
                'value': value,
            }
        }
        optional_properties = {}
        admin_state_up = kwargs.get('admin_state_up')
        if admin_state_up:
            assert isinstance(admin_state_up, bool)
            optional_properties['admin_state_up'] = admin_state_up

        invert = kwargs.get('invert')
        if invert:
            optional_properties['invert'] = invert

        key = kwargs.get('key')
        if key:
            optional_properties['key'] = key

        self._template['outputs'][name] = {
            'description': 'L7Rule %s ID' % name,
            'value': {'get_resource': name}
        }
        self._template['outputs'][name + '-show'] = {
            'description': 'Detailed information about resource.',
            'value': {'get_attr': [name, 'show']}
        }
