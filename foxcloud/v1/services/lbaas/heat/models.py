#
# Copyright (c) 2020 FTI-CAS
#

from __future__ import absolute_import

from foxcloud.v1.services.stack import model as md
from foxcloud.v1.utils import str_util


class Pool(md.Object):
    def __init__(self, context, name, alg, protocol, listener=None, pool_members=None,
                 monitor=None, description=None, **kwargs):
        """
        Initialize pool instance
        :param context:
        :param name:
        :param kwargs:
        """
        super().__init__(name=name, context=context)
        self.stack_name = context.name
        self.name = name
        self.description = description
        self.alg = alg or 'ROUND_ROBIN'
        self.listener = listener
        self.protocol = protocol
        self.pool_members = pool_members or []
        self.monitor = monitor
        self.kwargs = kwargs

    def add_to_template(self, template):
        pool_dn = str_util.h_join(self.stack_name, self.name)
        #  def add_pool(self, name, description, alg, protocol, listener, **kwargs):
        template.add_pool(name=pool_dn,  description=self.description, alg=self.alg,
                          protocol=self.protocol, listener=self.listener, **self.kwargs)
        # def add_pool_member(self, name, address, pool, port, **kwargs):
        for index, member in enumerate(self.pool_members):
            dn = str_util.h_join(pool_dn, "member", str(index))
            template.add_pool_member(name=dn, address=member.pop('address', None),
                                     pool=pool_dn, port=member.pop('port', None),
                                     weight=member.pop('weight', None), **member)

        if self.monitor:
            dn = str_util.h_join(pool_dn, "monitor")
            # default delay = 3 seconds
            # default max_entries = 3 connection failures before changing the member
            # status to INACTIVE.
            # default timeout = 3 seconds for monitor to wait for a connection to be
            # established before it times out
            # default monitor type: "HTTP"
            template.add_monitor(name=dn, pool=pool_dn, delay=self.monitor.pop('delay', 3),
                                 max_entries=self.monitor.pop('max_entries', 3),
                                 timeout=self.monitor.pop('timeout', 3),
                                 type=self.monitor.pop('type', 'HTTP'), **self.monitor)


class Listener(md.Object):
    def __init__(self, context, name, protocol, port, pool=None, lb=None,
                 l7policy=None, ssl=None, description=None, **kwargs):
        """
        Initialize listener instance
        :param context:
        :param name:
        :param protocol:
        :param port:
        :param pool:
        :param lb:
        :param l7policy
        :param ssl
        :param description:
        :param kwargs:
        """
        super().__init__(name=name, context=context)
        self.stack_name = context.name
        self.name = name
        self.description = description
        self.pool = pool
        self.protocol = protocol
        self.port = port
        self.lb = lb
        self.l7policy = l7policy
        self.ssl = ssl
        self.kwargs = kwargs

    def add_to_template(self, template):

        if self.ssl:
            self.ssl.add_to_template(template)

        ssl_dn = None
        if self.ssl:
            ssl_dn = str_util.h_join(self.stack_name, self.ssl.name)
        listener_dn = str_util.h_join(self.stack_name, self.name)
        template.add_listener(name=listener_dn, description=self.description,
                              protocol=self.protocol, port=self.port, lb=self.lb,
                              ssl=ssl_dn, **self.kwargs)
        self.pool.listener = listener_dn
        if self.pool:
            self.pool.add_to_template(template)

        if self.l7policy:
            self.l7policy.listener = listener_dn
            template.add_to_template(template)


class SSL(md.Object):
    def __init__(self, context, name, ssl_crt, ssl_key, payload_content_type, secret_type, **kwargs):
        super().__init__(name=name, context=context)
        self.stack_name = context.name
        self.name = name
        self.crt = ssl_crt
        self.key = ssl_key
        self.payload_content_type = payload_content_type
        self.secret_type = secret_type
        self.kwargs = kwargs

    def add_to_template(self, template):
        dn = str_util.h_join(self.stack_name, self.name)
        template.add_ssl(name=dn, crt=self.crt, key=self.key, payload_content_type=self.payload_content_type,
                         secret_type=self.secret_type)


class L7Policy(md.Object):
    def __init__(self, context, name, action, listener, rules=None, description=None, **kwargs):
        super().__init__(name=name, context=context)
        self.stack_name = context.name
        self.name = name
        self.description = description
        self.action = action
        self.listener = listener
        self.rules = rules
        self.kwargs = kwargs

    def add_to_template(self, template):
        l7_dn = str_util.h_join(self.stack_name, self.name)
        template.add_l7policy(name=l7_dn, description=self.description, action=self.action,
                              listener=self.listener, **self.kwargs)
        if self.rules:
            for index, rule in enumerate(self.rules):
                l7_rule_dn = str_util.h_join(l7_dn, "rule", str(index))
                template.add_l7rule(name=l7_rule_dn, compare_type=rule.pop('compare_type'),
                                    l7policy=l7_dn, type=rule.pop('type'), value=rule.pop('value'),
                                    **rule)


class LoadBalancer(md.Object):
    def __init__(self, context, name, vip_subnet, listener=None, description=None, **kwargs):
        """
        Initialize lb instance
        :param context:
        :param name:
        :param vip_subnet:
        :param listener:
        :param description:
        :param kwargs:
        """
        super().__init__(name=name, context=context)
        self.stack_name = context.name
        self.name = name
        self.description = description
        self.vip_subnet = vip_subnet
        self.kwargs = kwargs
        self.listener = listener

    def add_to_template(self, template):
        lb_dn = str_util.h_join(self.stack_name, self.name)
        template.add_lb(name=lb_dn, description=self.description,
                        vip_subnet=self.vip_subnet, **self.kwargs)

        if self.listener:
            self.listener.lb = lb_dn
            self.listener.add_to_template(template)
