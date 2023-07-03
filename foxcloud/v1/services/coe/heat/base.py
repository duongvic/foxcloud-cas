#
# Copyright (c) 2020 FTI-CAS
#

from foxcloud import exceptions as fox_exc
from foxcloud.v1.services.coe.base import BaseCOE
from foxcloud.v1.services.coe.heat import models as md
from foxcloud.v1.services.coe.heat import orchestrator
from foxcloud.v1.services.stack.contexts import Context
from foxcloud.v1.utils import constants as consts, str_util


class Heat(BaseCOE):
    """

    """
    __engine_type__ = 'heat'

    class Console(BaseCOE):
        __engine_type__ = 'heat'

    # **********************************************
    #   Create an openstack resource
    # **********************************************
    def create_allinone(self, info):
        """
        Deploy a new coe
        :param info:
        :return:
        """
        heat_context = HeatContext(session=self._session)
        heat_context.init(attrs=info)
        return heat_context.create()


class HeatContext(Context):
    def __init__(self, session=None):
        self.stack = None
        self._session = session
        self.heat_timeout = None
        self.heat_block = True
        self.template_file = None
        self.heat_parameters = None
        self.key_filename = None

        self.cluster_template = None
        self.cluster = None

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

        ct = resource_attrs.get('cluster_template')
        if ct:
            self.cluster_template = md.ClusterTemplate(self, name=ct.pop('name'),
                                                       coe=ct.pop('coe'),
                                                       external_network=ct.pop('external_network'),
                                                       image=ct.pop('name'),
                                                       worker_flavor=ct.pop('worker_flavor'),
                                                       master_flavor=ct.pop('master_flavor'),
                                                       volume_driver=ct.pop('volume_driver'),
                                                       network_driver=ct.pop('network_driver'),
                                                       volume_size=ct.pop('volume_size'),
                                                       fixed_network=ct.pop('fixed_network'),
                                                       fixed_subnet=ct.pop('fixed_subnet'),
                                                       keypair=ct.pop('keypair', None),
                                                       labels=ct.pop('labels', None),
                                                       **ct)

        cluster = resource_attrs.get('cluster')
        if cluster:
            self.cluster = md.Cluster(self, name=cluster.pop('name'),
                                      template=cluster.pop('template'),
                                      master_count=cluster.pop('master_count'),
                                      node_count=cluster.pop('node_count'),
                                      keypair=cluster.pop('keypair', None),
                                      timeout=cluster.pop('timeout', None))

    def _add_resources_to_template(self, template):
        if self.cluster_template:
            self.cluster_template.add_to_template(template)

        if self.cluster:
            ct_dn = str_util.h_join(self.cluster_template.stack_name, self.cluster_template.name)
            self.cluster.template = ct_dn
            self.cluster.add_to_template(template)

    def create(self):
        """
        Subclass should override this method.
        :return:
        """
        if self.key_filename is None:
            pass
        heat_template = orchestrator.CoeHeatTemplate(name=self.name,
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
