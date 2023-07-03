#
# Copyright (c) 2020 FTI-CAS
#
from __future__ import absolute_import

from foxcloud.v1.services.stack.contexts import Context


class DummyContext(Context):

    #__context_type__ = contexts.CONTEXT_DUMMY

    def deploy(self):
        """Don't need to deploy"""
        pass

    def undeploy(self):
        """Don't need to undeploy"""
        pass

    def _get_server(self, attr_name):
        return None

    def _get_network(self, attr_name):
        return None

    def _get_physical_nodes(self):
        return None

    def _get_physical_node_for_server(self, server_name):
        return None
