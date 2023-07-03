#
# Copyright (c) 2020 FTI-CAS
#

from __future__ import absolute_import

from foxcloud.v1.services.stack import model as md

DEFAULT_TIMEOUT = 100


class Cluster(md.Object):
    def __init__(self, context, name, template, master_count, node_count, keypair=None, timeout=None, **kwargs):
        super().__init__(name=name, context=context)
        self.stack_name = context.name
        self.name = name or 'cluster'
        self.template = template
        self.node_count = node_count or 1
        self.master_count = master_count or 1
        self.keypair = keypair
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.kwargs = kwargs

    def add_to_template(self, template):
        """
        Add to heat template
        :param template:
        :return:
        """
        template.add_to_template(self.stack_name, self.name, self.template, self.master_count,
                                 self.node_count, self.keypair, self.timeout, **self.kwargs)


class ClusterTemplate(md.Object):
    def __init__(self, context, name, coe, external_network, image,
                 worker_flavor=None, master_flavor=None, volume_driver=None,
                 network_driver='cinder', volume_size=30, fixed_network=None,
                 fixed_subnet=None, keypair=None, labels=None,
                 **kwargs):
        super().__init__(name=name, context=context)
        self.stack_name = context.name
        self.name = name or 'cluster'
        self.coe = coe
        self.external_network = external_network
        self.image = image
        self.worker_flavor = worker_flavor
        self.master_flavor = master_flavor
        self.volume_driver = volume_driver
        self.network_driver = network_driver
        self.volume_size = volume_size
        self.fixed_network = fixed_network
        self.fixed_subnet = fixed_subnet
        self.keypair = keypair
        self.labels = labels
        self.kwargs = kwargs

    def add_to_template(self, template):
        """
        Add to heat template
        :param template:
        :return:
        """
        template.add_to_template(self.stack_name, self.name, self.coe, self.external_network, self.image,
                                 self.worker_flavor, self.master_flavor, self.volume_driver,
                                 self.network_driver, self.volume_size, self.fixed_network,
                                 self.fixed_subnet, self.keypair, self.labels,
                                 **self.kwargs)
