#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import exceptions as fox_exc
from foxcloud.v1.services.lbaas.base import BaseLbaas
from foxcloud.v1.services.stack.contexts import Context
from foxcloud.v1.services.lbaas.heat import models as md
from foxcloud.v1.services.lbaas.heat import orchestrator
from foxcloud.v1.utils import constants as consts, str_util


class Heat(BaseLbaas):
    """

    """
    __engine_type__ = 'heat'

    def create_allinone(self, info):
        """
        Deploy a new load balancer
        :param info:
        :return:
        """
        heat_context = HeatContext(session=self._session)
        heat_context.init(attrs=info)
        return heat_context.create()

    def create_lb(self, name, description=None, provider='octavia',
                  address=None, subnet_id=None, listeners=None,
                  l7policy_id=None, **kwargs):
        """Create a new load balancer.
        :param name:
        :param description:
        :param provider: ['octavia']
        :param address:
        :param subnet_id:
        :param listeners:
        :param l7policy_id:
        :param kwargs:
        :return:
        """
        raise fox_exc.FoxCloudException("Not support this method")

    def create_listener(self, name, description, protocol, port,  lb_id, connection_limit=-1,
                        pool_id=None, l7policies=None, timeout_client_data=5000, timeout_member_connect=5000,
                        timeout_member_data=5000, timeout_tcp_inspect=5000, **kwargs):
        """Create a new listener.
        :param name:
        :param description:
        :param lb_id: (required)
        :param connection_limit:
        :param pool_id:
        :param l7policies: A list of l7policy IDs
        :param protocol: [HTTP, HTTPS, TCP, TERMINATED_HTTPS, UDP]
        :param port:
        :param timeout_client_data:
        :param timeout_member_connect:
        :param timeout_member_data:
        :param timeout_tcp_inspect:
        :param kwargs:
        :return:
        """
        raise fox_exc.FoxCloudException("Not support this method")

    def create_pool(self, name=None, description=None, listener_id=None, lb_algorithm='ROUND_ROBIN',
                    protocol='HTTP', lb_id=None, session_persistence='APP_COOKIE', **kwargs):
        """Create a pool.
        :param name:
        :param description:
        :param listener_id:
        :param lb_algorithm: [EAST_CONNECTIONS, ROUND_ROBIN, SOURCE_IP, or SOURCE_IP_PORT]
        :param protocol: [HTTP, HTTPS, PROXY, TCP, or UDP]
        :param lb_id:
        :param session_persistence: [APP_COOKIE, HTTP_COOKIE, SOURCE_IP]
        :param kwargs:
        :return:
        """
        raise fox_exc.FoxCloudException("Not support this method")

    def add_member(self, pool_id, address, port, name=None, is_backup=False,
                   subnet_id=None, weight=1, **kwargs):
        """
        Add new member to a specific pool being created
        :param pool_id:
        :param address:
        :param port:
        :param name:
        :param is_backup:
        :param subnet_id:
        :param weight:
        :param kwargs:
        :return:
        """

    def create_monitor(self, pool_id, delay, timeout, monitor_type='HTTP', name=None,
                       http_method='GET', max_retries=10, max_retries_down=10,
                       url_path='/', **kwargs):
        """
        :param pool_id:
        :param delay:
        :param timeout:
        :param monitor_type: [ HTTP, HTTPS, PING, TCP, TLS-HELLO, UDP-CONNECT]
        :param name:
        :param http_method: [CONNECT, DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT, TRACE]
        :param max_retries:
        :param max_retries_down:
        :param url_path:
        :param kwargs:
        :return:
        """
        raise fox_exc.FoxCloudException("Not support this method")

    def create_l7policy(self, action, listener_id, name=None, description=None,
                         position=None, **kwargs):
        """Create a l7policy
        :param action: [REDIRECT_PREFIX, REDIRECT_TO_POOL, REDIRECT_TO_URL, REJECT]
        :param listener_id:
        :param name:
        :param description:
        :param position:
        :param redirect_http_code:
        :param kwargs:
        :return:
        """


class HeatContext(Context):
    def __init__(self, session=None):
        self.stack = None
        self._session = session
        self.heat_timeout = None
        self.heat_block = True
        self.template_file = None
        self.heat_parameters = None
        self.key_filename = None

        self.lb = None
        self.listener = None
        self.pool = None
        self.l7policies = []
        self.ssl = None

        self._user = None
        self.error = None
        super(HeatContext, self).__init__(session=session)

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
            # don't initialize resources in case: undeployment
            return

        self._user = resource_attrs.get("user")
        self.template_file = resource_attrs.get("heat_template")

        if self.template_file is not None:
            self.key_filename = resource_attrs.get("key_filename", None)
            if self.key_filename is not None:
                pass

        if self.template_file:
            self.heat_parameters = resource_attrs.get("heat_parameters")
            return

        pool_members = resource_attrs.get('pool_members')
        pool_monitor = resource_attrs.get('pool_monitor')
        pool_info = resource_attrs.get('pool')
        if pool_info:
            params = {
                'lb':  pool_info.get('lb'),
                'tls_enabled':  pool_info.get('tls_enabled'),
            }
            self.pool = md.Pool(self, name='pool', alg=pool_info['alg'], protocol=pool_info['protocol'],
                                listener=pool_info.get('listener'), pool_members=pool_members,
                                monitor=pool_monitor, description=pool_info.get('description'), **params)

        ssl_info = resource_attrs.get('ssl')
        if ssl_info:
            self.ssl = md.SSL(self, name='ssl', ssl_crt=ssl_info['ssl_crt'],
                              ssl_key=ssl_info['ssl_key'],
                              payload_content_type=ssl_info['payload_content_type'],
                              secret_type=ssl_info['secret_type'])

        listener_info = resource_attrs.get('listener')
        if listener_info:
            params = {
                'admin_state_up': listener_info.get('admin_state_up'),
                'cidrs': listener_info.get('cidrs'),
                'connection_limit': listener_info.get('connection_limit'),
                'default_pool': listener_info.get('default_pool'),
                'default_tls_container_ref': listener_info.get('default_tls_container_ref'),
            }
            self.listener = md.Listener(self, name='listener', protocol=listener_info['protocol'],
                                        port=listener_info['port'], pool=self.pool,
                                        lb=listener_info.get('lb'), ssl=self.ssl,
                                        description=listener_info.get('description'),
                                        **params)

        lb_info = resource_attrs.get('lb')
        if lb_info:
            params = {
                'admin_state_up': lb_info.get('admin_state_up'),
                'flavor': lb_info.get('admin_state_up'),
                'vip_address': lb_info.get('vip_address'),
                'provider': lb_info.get('provider'),
            }
            self.lb = md.LoadBalancer(self, name='lb', vip_subnet=lb_info['vip_subnet'],
                                      listener=self.listener,
                                      description=listener_info.get('description'),
                                      **params)

    def _add_resources_to_template(self, template):
        if self.lb:
            self.lb.add_to_template(template)

    def create(self):
        """
        Subclass should override this method.
        :return:
        """
        if self.key_filename is None:
            pass
        heat_template = orchestrator.LbaasHeatTemplate(name=self.name,
                                                       template_file=self.template_file,
                                                       heat_parameters=self.heat_parameters,
                                                       session=self._session)

        if self.template_file is None:
            self._add_resources_to_template(heat_template)

        if self._flags.no_setup:
            self.stack = self._retrieve_existing_stack(stack_name=self.name)
            if not self.stack:
                self.stack = self._create_new_stack(heat_template=heat_template)
        else:
            self.stack = self._create_new_stack(heat_template=heat_template)

        return self._build_output(stack=self.stack, task_id=self.task_id, error=self.error)
