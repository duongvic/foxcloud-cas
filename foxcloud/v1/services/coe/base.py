#
# Copyright (c) 2020 FTI-CAS
#

from magnumclient.client import client


class BaseCOE(client.Client):
    """Basic manager for the shade services.
    Providing common operations such as creating, deleting, updating
    openstack servers.
    """
    __engine_type = None

    def __init__(self, session, endpoint=None):
        super(BaseCOE, self).__init__(session=session, magnum_url=endpoint)
        self._session = session
        self.endpoint = endpoint

    def refresh(self, session):
        self._session = session

    def create_allinone(self, info):
        """
        Create all in one
        :param info:
        :return:
        """

    # **********************************************
    #   Update an openstack resource being created
    # **********************************************
    def update_cluster(self, cluster_id, patch):
        """
        Subclass should be override this method
        Usage:
            patch = {'op': 'replace',
                     'value': NEW_NAME,
                     'path': '/name'}
            cluster = update_cluster(id='123', patch=patch)
        :param cluster_id:
        :param patch: Resource attribute’s name.
        :return:
        """

    def resize_cluster(self, cluster_id, node_count, nodes_to_remove, nodegroup=None):
        """
        Subclass should be override this method
        :param cluster_id:
        :param node_count:
        :param nodes_to_remove:
        :param nodegroup:
        :return:
        """

    def upgrade_cluster(self, cluster_id, template_id, max_batch_size=1, nodegroup=None):
        """
        Subclass should be override this method
        :param cluster_id:
        :param template_id:
        :param max_batch_size:
        :param nodegroup:
        :return:
        """

    def update_cluster_template(self, template_id, patch):
        """
        Update a specific cluster
        Usage:
            patch = {
                "path":"/master_lb_enabled",
                "value":"True",
                "op":"replace"
            }
            cluster = update_cluster_template(id='123', patch=patch)
        :param template_id:
        :param patch: Resource attribute’s name.
        :return:
        """

    # **********************************************
    #   Delete an openstack resource being created
    # **********************************************
    def delete_cluster(self, cluster_id):
        """
        Subclass should be override this method
        :param cluster_id: The UUID or name of clusters in Magnum.
        :return:
        """

    def delete_cluster_template(self, template_id):
        """
        Subclass should be override this method
        :param template_id: The UUID or name of cluster templates in Magnum.
        :return:
        """
